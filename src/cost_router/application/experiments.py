"""The lesson's steps as functions over the tier, check and router objects."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from cost_router.application.answer_checks import AnswerChecks
from cost_router.application.ports import Mapper
from cost_router.application.router import ESCALATE, CostRouter
from cost_router.application.tiers import Answered, ModelTiers
from cost_router.domain.checks import (
    check_label_agreement,
    check_label_shape,
    check_policy,
    check_refund,
    is_correct,
)
from cost_router.domain.metrics import (
    CheckRates,
    Rate,
    bootstrap_accuracy_difference,
    bootstrap_cost_per_correct,
    check_rates,
    cost_per_correct,
    rate,
)
from cost_router.domain.pricing import TIERS
from cost_router.domain.routing import Bar, DayBudget, Decision, RouterConfig
from cost_router.domain.signals import hard_signal
from cost_router.domain.stats import shuffled_indices
from cost_router.domain.tasks import Kind, Task

KINDS = tuple(k.value for k in Kind)
CHECK_NAMES = {
    "label": ("label_shape", "label_agreement"),
    "refund": ("refund_recompute",),
    "policy": ("policy_quote",),
}

Answers = dict[str, dict[str, Answered]]


@dataclass(frozen=True)
class TierKind:
    """A tier's accuracy and cost on one kind of task."""

    accuracy: Rate
    cost_per_call: float
    cost_per_correct: float | None


def collect_answers(tasks: Sequence[Task], tiers: ModelTiers, mapper: Mapper) -> Answers:
    """Every tier's first answer (temperature 0) to every task."""
    jobs = [(tier, task) for tier in TIERS for task in tasks]
    results = mapper(lambda job: tiers.call(job[0], job[1]), jobs)
    answers: Answers = {tier: {} for tier in TIERS}
    for (tier, task), answered in zip(jobs, results, strict=True):
        answers[tier][task.task_id] = answered
    return answers


def measure_models(tasks: Sequence[Task], answers: Answers) -> dict[str, dict[str, TierKind]]:
    """Step 1: accuracy per task kind, cost per call and cost per correct answer for each model alone."""
    table: dict[str, dict[str, TierKind]] = {}
    for tier in TIERS:
        table[tier] = {}
        for kind in KINDS:
            subset = [t for t in tasks if t.kind.value == kind]
            correct = [is_correct(t, answers[tier][t.task_id].text) for t in subset]
            cost = sum(answers[tier][t.task_id].cost for t in subset)
            table[tier][kind] = TierKind(
                rate(sum(correct), len(correct)),
                cost / len(subset) if subset else 0.0,
                cost_per_correct(cost, sum(correct)),
            )
    return table


def cheapest_matching(table: dict[str, dict[str, TierKind]], margin: float) -> dict[str, str | None]:
    """For each kind, the cheapest tier whose accuracy is within `margin` of the large tier's, or None."""
    chosen: dict[str, str | None] = {}
    for kind in KINDS:
        target = table["large"][kind].accuracy.value - margin
        chosen[kind] = next((t for t in TIERS if table[t][kind].accuracy.value >= target), None)
    return chosen


def check_results(
    tasks: Sequence[Task], answers: Answers, tiers: ModelTiers, mapper: Mapper
) -> dict[str, dict[str, dict[str, CheckRates]]]:
    """Step 2: the false-accept and false-reject rate of each check, for each tier, on the given tasks."""
    out: dict[str, dict[str, dict[str, CheckRates]]] = {}
    for tier in TIERS:
        out[tier] = {}
        for kind in KINDS:
            subset = [t for t in tasks if t.kind.value == kind]
            correct = [is_correct(t, answers[tier][t.task_id].text) for t in subset]
            texts = [answers[tier][t.task_id].text for t in subset]
            out[tier][kind] = {}
            if kind == "label":

                def second_text(task: Task, tier: str = tier) -> str:
                    return tiers.call(tier, task, second_sample=True).text

                seconds = mapper(second_text, subset)
                shape = [check_label_shape(x) for x in texts]
                agree = [check_label_agreement(x, y) for x, y in zip(texts, seconds, strict=True)]
                out[tier][kind]["label_shape"] = check_rates(shape, correct)
                out[tier][kind]["label_agreement"] = check_rates(agree, correct)
            elif kind == "refund":
                passed = [check_refund(t, x) for t, x in zip(subset, texts, strict=True)]
                out[tier][kind]["refund_recompute"] = check_rates(passed, correct)
            else:
                passed = [check_policy(x) for x in texts]
                out[tier][kind]["policy_quote"] = check_rates(passed, correct)
    return out


def tune(
    build_tasks: Sequence[Task],
    answers: Answers,
    rates: dict[str, dict[str, dict[str, CheckRates]]],
    bar: Bar,
    request_cap: float | None = None,
) -> RouterConfig:
    """Step 3, from the build set only: where each kind starts, and which hard tasks skip the small tier."""
    start: dict[str, str] = {}
    hard_start: dict[str, str] = {}
    for kind in KINDS:
        check_name = CHECK_NAMES[kind][-1]
        start[kind] = next(
            (t for t in TIERS if rates[t][kind][check_name].false_accept_rate <= bar.false_accept_bar), TIERS[-1]
        )
        index = TIERS.index(start[kind])
        signalled = [t for t in build_tasks if t.kind.value == kind and hard_signal(t)]
        if index < len(TIERS) - 1 and len(signalled) >= 5:
            accuracy = sum(is_correct(t, answers[start[kind]][t.task_id].text) for t in signalled) / len(signalled)
            if accuracy < bar.hard_accuracy_bar:
                hard_start[kind] = TIERS[index + 1]
    return RouterConfig(start, hard_start, "agreement", request_cap or bar.request_cap, bar.tighten_at)


@dataclass(frozen=True)
class Outcome:
    """A routing decision with the ground truth next to it."""

    decision: Decision
    kind: str
    difficulty: str
    correct: bool

    @property
    def escalated(self) -> bool:
        """True when no tier's answer was accepted."""
        return self.decision.served_by == ESCALATE


def route_all(tasks: Sequence[Task], router: CostRouter, day: DayBudget | None = None) -> list[Outcome]:
    """Serve tasks in order (the day's budget makes the order matter, so this is sequential)."""
    outcomes = []
    for task in tasks:
        decision = router.route(task, day)
        correct = decision.answer is not None and is_correct(task, decision.answer)
        outcomes.append(Outcome(decision, task.kind.value, task.difficulty, correct))
    return outcomes


@dataclass(frozen=True)
class Summary:
    """Accuracy, money and tier shares of a set of outcomes."""

    n: int
    accuracy: Rate
    total_cost: float
    cost_per_correct: float | None
    cost_per_correct_interval: tuple[float, float]
    served_by: dict[str, int]
    escalated: int
    max_request_spend: float


def summarize(outcomes: Sequence[Outcome]) -> Summary:
    """Aggregate outcomes (a router's) with bootstrap intervals."""
    correct = [o.correct for o in outcomes]
    costs = [o.decision.spent for o in outcomes]
    shares: dict[str, int] = {}
    for o in outcomes:
        shares[o.decision.served_by] = shares.get(o.decision.served_by, 0) + 1
    return Summary(
        len(outcomes),
        rate(sum(correct), len(correct)),
        sum(costs),
        cost_per_correct(sum(costs), sum(correct)),
        bootstrap_cost_per_correct(costs, correct),
        dict(sorted(shares.items())),
        sum(1 for o in outcomes if o.escalated),
        max(costs, default=0.0),
    )


def single_model_summary(tasks: Sequence[Task], answers: Answers, tier: str) -> Summary:
    """The same summary for one model answering every task alone."""
    correct = [is_correct(t, answers[tier][t.task_id].text) for t in tasks]
    costs = [answers[tier][t.task_id].cost for t in tasks]
    return Summary(
        len(tasks),
        rate(sum(correct), len(correct)),
        sum(costs),
        cost_per_correct(sum(costs), sum(correct)),
        bootstrap_cost_per_correct(costs, correct),
        {tier: len(tasks)},
        0,
        max(costs, default=0.0),
    )


def compare_to_large(tasks: Sequence[Task], answers: Answers, outcomes: Sequence[Outcome], bar: Bar) -> dict[str, Any]:
    """Step 5's verdict: matched the large model's accuracy within the margin at a lower cost per correct?"""
    router = summarize(outcomes)
    large = single_model_summary(tasks, answers, "large")
    router_correct = [o.correct for o in outcomes]
    large_correct = [is_correct(t, answers["large"][t.task_id].text) for t in tasks]
    diff, low, high = bootstrap_accuracy_difference(router_correct, large_correct)
    matched = router.accuracy.value >= large.accuracy.value - bar.accuracy_margin
    cheaper = (
        router.cost_per_correct is not None
        and large.cost_per_correct is not None
        and router.cost_per_correct < large.cost_per_correct
    )
    return {
        "accuracy_difference_vs_large": diff,
        "accuracy_difference_interval": [low, high],
        "margin": bar.accuracy_margin,
        "matched_within_margin": matched,
        "cheaper_per_correct": cheaper,
        "verdict": "matched" if matched and cheaper else ("cheaper but less accurate" if cheaper else "not cheaper"),
    }


@dataclass(frozen=True)
class DayResult:
    """One replay of the test tasks as a single day under a budget."""

    fraction: float
    budget: float
    spent: float
    under_budget: bool
    requests_over_cap: int
    crossed_at: int | None
    accuracy_before: Rate
    accuracy_after: Rate
    large_served_after: int
    outcomes: list[Outcome]


def run_day(tasks: Sequence[Task], answers: Answers, router_factory: Any, fraction: float, seed: int = 11) -> DayResult:
    """Step 4: the tasks, in a fixed shuffled order, under a budget of `fraction` of the always-large cost."""
    order = [tasks[i] for i in shuffled_indices(len(tasks), seed)]
    large_cost = sum(answers["large"][t.task_id].cost for t in tasks)
    day = DayBudget(large_cost * fraction)
    router: CostRouter = router_factory()
    outcomes = route_all(order, router, day)
    crossed = next((i for i, o in enumerate(outcomes) if o.decision.share_before >= router.config.tighten_at), None)
    before = outcomes[:crossed] if crossed is not None else outcomes
    after = outcomes[crossed:] if crossed is not None else []
    cap = router.config.request_cap
    return DayResult(
        fraction,
        day.budget,
        day.used,
        day.used <= day.budget,
        sum(1 for o in outcomes if o.decision.spent > cap),
        crossed,
        rate(sum(o.correct for o in before), len(before)),
        rate(sum(o.correct for o in after), len(after)),
        sum(1 for o in after if o.decision.served_by == "large"),
        outcomes,
    )


def check_name(kind: str, config: RouterConfig) -> str:
    """The name of the check a configuration runs for a kind of task."""
    if kind == "label":
        return f"label_{config.label_check}"
    return "refund_recompute" if kind == "refund" else f"policy_{config.policy_check}"


def false_accepts(outcomes: Sequence[Outcome], config: RouterConfig) -> dict[str, Any]:
    """Step 6: answers the router accepted that were wrong, grouped by the tier that served them and the check."""
    grouped: dict[str, list[str]] = {}
    served_wrong = 0
    for o in outcomes:
        if o.decision.answer is None or o.correct:
            continue
        served_wrong += 1
        grouped.setdefault(f"{o.decision.served_by}/{check_name(o.kind, config)}", []).append(o.decision.task_id)
    by_tier: dict[str, int] = {}
    for key, ids in grouped.items():
        tier = key.split("/")[0]
        by_tier[tier] = by_tier.get(tier, 0) + len(ids)
    return {
        "false_accepts": served_wrong,
        "by_tier_and_check": {k: {"count": len(v), "tasks": v} for k, v in sorted(grouped.items())},
        "by_tier": dict(sorted(by_tier.items())),
    }


def harden(config: RouterConfig, kind: str) -> tuple[RouterConfig, str]:
    """The one change step 6 makes to the weakest check's kind: start one tier higher, or, when it already starts at
    the top tier, run a stronger check (for policy: the quoted line must also be the line that best matches the
    question). Returns the new configuration and a sentence describing the change."""
    index = TIERS.index(config.start[kind])
    if index < len(TIERS) - 1:
        start = {**config.start, kind: TIERS[index + 1]}
        hard = {k: v for k, v in config.hard_start.items() if k != kind or TIERS.index(v) > index + 1}
        changed = RouterConfig(
            start, hard, config.label_check, config.request_cap, config.tighten_at, config.policy_check
        )
        return changed, f"{kind} tasks start at {TIERS[index + 1]} instead of {TIERS[index]}"
    if kind == "policy":
        changed = RouterConfig(
            config.start, config.hard_start, config.label_check, config.request_cap, config.tighten_at, "overlap"
        )
        return changed, "policy answers must quote the line that best matches the question, not just any line"
    return config, f"{kind} already starts at the top tier and has no stronger check; nothing changed"


def weakest_kind(outcomes: Sequence[Outcome]) -> str | None:
    """The kind with the most accepted-but-wrong answers on the test set (None when there are none)."""
    counts: dict[str, int] = {}
    for o in outcomes:
        if o.decision.answer is not None and not o.correct:
            counts[o.kind] = counts.get(o.kind, 0) + 1
    return max(sorted(counts), key=lambda k: counts[k]) if counts else None


def make_checks(tiers: ModelTiers, config: RouterConfig) -> AnswerChecks:
    """The answer checks for a router configuration."""
    return AnswerChecks(tiers, config.label_check, config.policy_check)
