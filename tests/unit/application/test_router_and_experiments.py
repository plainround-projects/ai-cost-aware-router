import pytest

from cost_router.application.answer_checks import AnswerChecks
from cost_router.application.experiments import (
    cheapest_matching,
    check_results,
    collect_answers,
    compare_to_large,
    false_accepts,
    harden,
    make_checks,
    measure_models,
    route_all,
    run_day,
    single_model_summary,
    summarize,
    tune,
    weakest_kind,
)
from cost_router.application.router import ESCALATE, CostRouter
from cost_router.domain.checks import is_correct
from cost_router.domain.llm import ChatRequest
from cost_router.domain.pricing import TIERS
from cost_router.domain.routing import Bar, DayBudget
from cost_router.domain.tasks import POLICY_LINES, Kind, Task
from tests.unit.fakes import config, label_task, policy_task, refund_task, sequential, tiers_for

BAR = Bar(0.10, 0.5, 0.02, 0.01, 0.8, (0.5,))
RIGHT_QUOTE = f'Answer: yes\nQuote: "{POLICY_LINES[0]}"'


def by_tier(table):
    """An answer function: look up the reply by the model id in the request."""

    def answer(request: ChatRequest) -> str:
        reply = table[request.model]
        return str(reply(request)) if callable(reply) else str(reply)

    return answer


def test_tiers_build_prompts_by_kind_and_cost_calls_from_billed_tokens():
    tiers, model = tiers_for(lambda r: " billing ")
    answered = tiers.call("small", label_task())
    assert answered.text == "billing" and answered.tokens == 110
    assert answered.cost == pytest.approx(110 / 1000 * 0.0002)
    assert "LABEL I was charged twice." in tiers.prompt(label_task())
    assert "REFUND" in tiers.prompt(refund_task()) and "1. Returns are accepted" in tiers.prompt(policy_task())
    tiers.call("small", label_task(), second_sample=True)
    first, second = model.requests
    assert (first.temperature, first.seed) == (0.0, None) and (second.temperature, second.seed) == (0.8, 7)
    assert tiers.estimate("large", label_task(), calls=2) > tiers.estimate("small", label_task())


def test_label_agreement_costs_a_second_sample_and_shape_does_not():
    tiers, model = tiers_for(lambda r: "billing")
    agreement = AnswerChecks(tiers, "agreement").check(label_task(), "small", "billing")
    assert agreement.passed and agreement.extra_cost > 0 and agreement.extra_tokens == 110
    assert len(model.requests) == 1
    shape = AnswerChecks(tiers, "shape").check(label_task(), "small", "billing")
    assert shape.passed and shape.extra_cost == 0 and len(model.requests) == 1
    assert AnswerChecks(tiers, "agreement").estimate_extra(label_task(), "small") > 0
    assert AnswerChecks(tiers, "shape").estimate_extra(label_task(), "small") == 0
    assert AnswerChecks(tiers).estimate_extra(refund_task(), "small") == 0
    assert AnswerChecks(tiers).check(refund_task(days=20, total=5000), "small", "40.00").passed
    assert not AnswerChecks(tiers).check(policy_task(), "small", "Answer: 2.").passed


def make_router(answer, cfg=None, realistic_usage=False):
    tiers, model = tiers_for(answer, realistic_usage)
    cfg = cfg or config()
    return CostRouter(tiers, AnswerChecks(tiers, cfg.label_check), cfg), model


def test_the_router_stops_at_the_first_accepted_answer():
    router, model = make_router(lambda r: "40.00")
    decision = router.route(refund_task(days=20, total=5000))
    assert decision.served_by == "small" and decision.answer == "40.00"
    assert len(decision.attempts) == 1 and len(model.requests) == 1


def test_a_failed_check_escalates_to_the_next_tier():
    router, _ = make_router(by_tier({"m-small": "99.00", "m-medium": "40.00", "m-large": "40.00"}))
    decision = router.route(refund_task(days=20, total=5000))
    assert decision.served_by == "medium"
    assert [(a.tier, a.passed) for a in decision.attempts] == [("small", False), ("medium", True)]
    assert decision.spent == pytest.approx(sum(a.cost for a in decision.attempts))


def test_when_every_check_fails_a_person_gets_the_task():
    router, _ = make_router(lambda r: "99.00")
    decision = router.route(refund_task())
    assert decision.served_by == ESCALATE and decision.answer is None and len(decision.attempts) == 3


def test_the_start_tier_and_the_hard_signal_skip_cheap_tiers():
    cfg = config(start={"label": "medium", "refund": "small", "policy": "small"}, hard={"refund": "large"})
    router, model = make_router(lambda r: "40.00", cfg)
    router.route(refund_task(days=20, total=5000))
    assert model.requests[0].model == "m-small"
    hard = refund_task(days=20, total=5000)
    damaged = type(hard)(
        hard.task_id, hard.kind, hard.difficulty, hard.split, hard.text + " It was damaged.", 0, hard.orders
    )
    router.route(damaged)
    assert model.requests[1].model == "m-large"


def test_the_request_cap_is_checked_before_a_call_and_stops_the_cascade():
    router, model = make_router(lambda r: "99.00", config(cap=0.00001), realistic_usage=True)
    decision = router.route(refund_task())
    assert decision.served_by == ESCALATE and "cap" in decision.tags and model.requests == []
    one_call = tiers_for(lambda r: "x")[0].estimate("small", refund_task())
    tight, called = make_router(lambda r: "99.00", config(cap=one_call * 1.5), realistic_usage=True)
    result = tight.route(refund_task())
    assert len(called.requests) == 1 and "cap" in result.tags and result.spent <= one_call * 1.5


def test_late_in_the_day_the_largest_tier_is_not_offered_but_the_router_keeps_answering():
    router, model = make_router(by_tier({"m-small": "99.00", "m-medium": "99.00", "m-large": "40.00"}))
    day = DayBudget(1.0)
    day.add(0.85)
    decision = router.route(refund_task(days=20, total=5000), day)
    assert decision.served_by == ESCALATE and {r.model for r in model.requests} == {"m-small", "m-medium"}
    assert day.used > 0.85 and decision.share_before == pytest.approx(0.85)
    early, _ = make_router(by_tier({"m-small": "99.00", "m-medium": "99.00", "m-large": "40.00"}))
    assert early.route(refund_task(days=20, total=5000), DayBudget(1.0)).served_by == "large"
    assert router.config.tighten_at == 0.8


def test_the_day_budget_limits_what_a_request_may_spend_and_hands_the_rest_to_a_person():
    router, _ = make_router(lambda r: "99.00", config(cap=1.0), realistic_usage=True)
    day = DayBudget(0.00005)
    first = router.route(refund_task(), day)
    assert first.tags == ("budget",) and day.used <= day.budget
    spent_after_first = day.used
    second = router.route(refund_task(), day)
    assert second.served_by == ESCALATE and day.used <= day.budget and day.used >= spent_after_first
    assert "budget" in second.tags


def corpus():
    return [
        label_task("t1", "billing", split="build"),
        refund_task("t2", split="build"),
        policy_task("t3", 0, split="build"),
    ]


def answer_all(request: ChatRequest) -> str:
    text = request.messages[0].content
    if text.startswith("LABEL"):
        return "billing"
    if text.startswith("REFUND"):
        return "40.00"
    return RIGHT_QUOTE


def test_collect_and_measure_models_report_accuracy_and_cost_per_correct():
    tiers, _ = tiers_for(answer_all)
    tasks = corpus()
    answers = collect_answers(tasks, tiers, sequential)
    assert set(answers) == set(TIERS) and set(answers["small"]) == {"t1", "t2", "t3"}
    table = measure_models(tasks, answers)
    assert table["small"]["label"].accuracy.value == 1.0
    assert table["large"]["refund"].cost_per_correct == pytest.approx(answers["large"]["t2"].cost)
    assert cheapest_matching(table, 0.02) == {"label": "small", "refund": "small", "policy": "small"}


def test_cheapest_matching_is_none_when_no_tier_reaches_the_large_one():
    tiers, _ = tiers_for(by_tier({"m-small": "x", "m-medium": "x", "m-large": "billing"}))
    tasks = [label_task("t1", "billing")]
    table = measure_models(tasks, collect_answers(tasks, tiers, sequential))
    assert cheapest_matching(table, 0.0)["label"] == "large"
    broken = measure_models(tasks, collect_answers(tasks, tiers_for(lambda r: "x")[0], sequential))
    assert cheapest_matching(broken, 0.0)["label"] == "small"


def test_check_results_measure_false_accepts_and_the_tuner_moves_a_kind_up():
    def answer(request: ChatRequest) -> str:
        text = request.messages[0].content
        if text.startswith("LABEL"):
            return "returns" if request.model == "m-small" else "billing"
        if text.startswith("REFUND"):
            return "40.00"
        return f'Answer: x\nQuote: "{POLICY_LINES[1]}"' if request.model != "m-large" else RIGHT_QUOTE

    tiers, _ = tiers_for(answer)
    tasks = corpus()
    answers = collect_answers(tasks, tiers, sequential)
    rates = check_results(tasks, answers, tiers, sequential)
    assert rates["small"]["label"]["label_shape"].false_accept_rate == 1.0
    assert rates["small"]["label"]["label_agreement"].false_accept_rate == 1.0
    assert rates["small"]["refund"]["refund_recompute"].false_accept_rate == 0.0
    assert rates["medium"]["policy"]["policy_quote"].false_accept_rate == 1.0
    assert rates["large"]["policy"]["policy_quote"].false_accept_rate == 0.0
    cfg = tune(tasks, answers, rates, BAR)
    assert cfg.start == {"label": "medium", "refund": "small", "policy": "large"}
    assert cfg.label_check == "agreement" and cfg.request_cap == BAR.request_cap


def test_hard_tasks_skip_a_tier_that_fails_them_on_the_build_set():
    def answer(request: ChatRequest) -> str:
        return "99.00" if "damaged" in request.messages[0].content else "40.00"

    tiers, _ = tiers_for(answer)
    tasks = [refund_task(f"t{i}", split="build") for i in range(5)]
    hard = [
        type(t)(f"h{i}", t.kind, "hard", "build", t.text + " The item was damaged.", t.gold, t.orders)
        for i, t in enumerate(tasks)
    ]
    everything = tasks + hard
    answers = collect_answers(everything, tiers, sequential)
    rates = check_results(everything, answers, tiers, sequential)
    cfg = tune(everything, answers, rates, BAR, request_cap=0.5)
    assert cfg.start["refund"] == "small" and cfg.hard_start == {"refund": "medium"} and cfg.request_cap == 0.5


def test_routing_the_test_set_summaries_and_the_verdict_against_the_large_model():
    tiers, _ = tiers_for(answer_all)
    tasks = corpus()
    answers = collect_answers(tasks, tiers, sequential)
    router = CostRouter(tiers, make_checks(tiers, config()), config())
    outcomes = route_all(tasks, router)
    summary = summarize(outcomes)
    assert summary.n == 3 and summary.accuracy.value == 1.0 and summary.escalated == 0
    assert summary.served_by == {"small": 3} and summary.max_request_spend > 0
    large = single_model_summary(tasks, answers, "large")
    assert large.total_cost > summary.total_cost
    verdict = compare_to_large(tasks, answers, outcomes, BAR)
    assert verdict["verdict"] == "matched" and verdict["matched_within_margin"] and verdict["cheaper_per_correct"]
    escalating = route_all(tasks, CostRouter(tiers_for(lambda r: "x")[0], make_checks(tiers, config()), config()))
    assert all(o.escalated for o in escalating)
    assert compare_to_large(tasks, answers, escalating, BAR)["verdict"] == "not cheaper"


def test_the_verdict_can_be_cheaper_but_less_accurate():
    tiers, _ = tiers_for(by_tier({"m-small": "40.00", "m-medium": "x", "m-large": "x"}))
    task = refund_task("t2", days=20, total=5000)
    answers = collect_answers([task], tiers, sequential)
    wrong_router = CostRouter(
        tiers, make_checks(tiers, config()), config(start={"label": "small", "refund": "large", "policy": "small"})
    )
    outcomes = route_all([task], wrong_router)
    large = answers["large"]["t2"]
    assert not is_correct(task, large.text)
    assert compare_to_large([task], answers, outcomes, BAR)["verdict"] in {
        "not cheaper",
        "cheaper but less accurate",
        "matched",
    }


def test_a_day_under_a_budget_tightens_and_reports_before_and_after():
    tiers, _ = tiers_for(by_tier({"m-small": "99.00", "m-medium": "99.00", "m-large": "40.00"}))
    tasks = [refund_task(f"t{i}", days=20, total=5000) for i in range(12)]
    answers = collect_answers(tasks, tiers, sequential)
    factory = lambda: CostRouter(tiers, make_checks(tiers, config()), config())  # noqa: E731
    result = run_day(tasks, answers, factory, 0.6)
    assert result.crossed_at is not None and result.accuracy_before.trials + result.accuracy_after.trials == 12
    assert result.large_served_after == 0 and result.accuracy_after.value == 0.0
    assert result.requests_over_cap == 0 and result.budget == pytest.approx(
        0.6 * sum(a.cost for a in answers["large"].values())
    )
    roomy = run_day(tasks, answers, factory, 50.0)
    assert roomy.crossed_at is None and roomy.accuracy_after.trials == 0 and roomy.under_budget


def test_false_accepts_are_grouped_by_tier_and_check_and_the_weakest_kind_changes():
    def answer(request: ChatRequest) -> str:
        text = request.messages[0].content
        return f'Answer: x\nQuote: "{POLICY_LINES[1]}"' if text.startswith("POLICY") else "40.00"

    tiers, _ = tiers_for(answer)
    tasks = [policy_task("t3", 0), refund_task("t2")]
    cfg = config()
    outcomes = route_all(tasks, CostRouter(tiers, make_checks(tiers, cfg), cfg))
    report = false_accepts(outcomes, cfg)
    assert report["false_accepts"] == 1 and report["by_tier"] == {"small": 1}
    assert report["by_tier_and_check"]["small/policy_quote"]["tasks"] == ["t3"]
    assert weakest_kind(outcomes) == "policy"
    only_refund = route_all([refund_task()], CostRouter(tiers, make_checks(tiers, cfg), cfg))
    assert weakest_kind(only_refund) is None


def test_hardening_moves_a_kind_up_a_tier_then_strengthens_the_policy_check_then_gives_up():
    cfg = config(start={"label": "small", "refund": "large", "policy": "medium"}, hard={"policy": "medium"})
    up, text = harden(cfg, "policy")
    assert up.start["policy"] == "large" and up.hard_start == {} and "large instead of medium" in text
    stronger, text = harden(up, "policy")
    assert stronger.policy_check == "overlap" and stronger.start == up.start and "best matches" in text
    same, text = harden(cfg, "refund")
    assert same == cfg and "nothing changed" in text


def test_the_overlap_check_rejects_a_real_but_wrong_line():
    tiers, _ = tiers_for(lambda r: "x")
    question = Task("t3", Kind.POLICY, "easy", "test", "Who pays return shipping?", 1)
    wrong, right = f'Quote: "{POLICY_LINES[6]}"', f'Quote: "{POLICY_LINES[1]}"'
    quote_only = AnswerChecks(tiers, "agreement", "quote")
    overlap = AnswerChecks(tiers, "agreement", "overlap")
    assert quote_only.check(question, "small", wrong).passed
    assert not overlap.check(question, "small", wrong).passed
    assert overlap.check(question, "small", right).passed
