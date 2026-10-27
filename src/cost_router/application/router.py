"""The cost-aware router: cheapest tier first, a check after every answer, escalation on a failed check."""

from __future__ import annotations

from cost_router.application.answer_checks import AnswerChecks
from cost_router.application.tiers import ModelTiers
from cost_router.domain.pricing import TIERS
from cost_router.domain.routing import Attempt, DayBudget, Decision, RouterConfig
from cost_router.domain.signals import hard_signal
from cost_router.domain.tasks import Task

ESCALATE = "escalate_to_person"


class CostRouter:
    """Tries tiers in order of price and stops at the first answer a check accepts.

    - The start tier comes from the build set (config/router.json) and a hard task may start higher.
    - Before every call the router adds the next call's estimated cost (and its check's) to what the request has
      spent and refuses to go over the per-request cap, or over what is left of the day's budget when there is one.
    - Once the day's budget is 80% used, the largest tier is no longer available; the router keeps answering until
      the money runs out, then hands the task to a person.
    """

    def __init__(self, tiers: ModelTiers, checks: AnswerChecks, config: RouterConfig) -> None:
        self._tiers = tiers
        self._checks = checks
        self._config = config

    @property
    def config(self) -> RouterConfig:
        """The configuration in force."""
        return self._config

    def route(self, task: Task, day: DayBudget | None = None) -> Decision:
        """Serve one task and record every tier tried."""
        config = self._config
        share = day.used_share() if day else 0.0
        allowed = TIERS[:-1] if day and share >= config.tighten_at else TIERS
        start = config.start_index(task.kind.value, hard_signal(task))
        limit = config.request_cap if day is None else min(config.request_cap, day.budget - day.used)
        spent = 0.0
        tokens = 0
        attempts: list[Attempt] = []
        tags: list[str] = []
        for tier in allowed[min(start, len(allowed)) :]:
            projected = spent + self._tiers.estimate(tier, task) + self._checks.estimate_extra(task, tier)
            if projected > limit:
                tags.append("cap" if limit == config.request_cap else "budget")
                break
            answered = self._tiers.call(tier, task)
            result = self._checks.check(task, tier, answered.text)
            call_cost = answered.cost + result.extra_cost
            spent += call_cost
            tokens += answered.tokens + result.extra_tokens
            attempts.append(Attempt(tier, result.passed, call_cost, answered.tokens + result.extra_tokens))
            if result.passed:
                if day:
                    day.add(spent)
                return Decision(task.task_id, answered.text, tier, tuple(attempts), spent, tokens, share, tuple(tags))
        if day:
            day.add(spent)
        return Decision(task.task_id, None, ESCALATE, tuple(attempts), spent, tokens, share, tuple(tags))
