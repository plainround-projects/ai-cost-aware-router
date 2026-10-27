import pytest

from cost_router.domain.checks import (
    best_matching_line,
    check_label_agreement,
    check_label_shape,
    check_policy,
    check_policy_overlap,
    check_refund,
    content_words,
    is_correct,
    normalize,
    parse_amount_cents,
    parse_label,
    parse_quote,
    quoted_line_index,
)
from cost_router.domain.llm import Usage
from cost_router.domain.metrics import (
    bootstrap_accuracy_difference,
    bootstrap_cost_per_correct,
    check_rates,
    cost_per_correct,
    rate,
)
from cost_router.domain.pricing import PriceTable
from cost_router.domain.routing import DayBudget, RouterConfig
from cost_router.domain.signals import hard_signal
from cost_router.domain.stats import shuffled_indices
from cost_router.domain.tasks import POLICY_LINES, Kind, RefundOrder, Task, expected_refund_cents, money, refund_cents
from tests.unit.fakes import label_task, policy_task, refund_task


def test_refund_rules_follow_the_policy():
    assert refund_cents(RefundOrder("o", 5000, 10, 5000, False)) == 5000
    assert refund_cents(RefundOrder("o", 5000, 20, 5000, False)) == 4000
    assert refund_cents(RefundOrder("o", 5000, 31, 5000, False)) == 0
    assert refund_cents(RefundOrder("o", 5000, 20, 2500, True)) == 2500
    assert refund_cents({"days": 16, "returned_cents": 1250, "damaged": False}) == 1000
    assert refund_cents(RefundOrder("o", 5000, 40, 5000, True)) == 0
    assert money(4000) == "40.00" and money(5) == "0.05"


def test_expected_refund_adds_every_order():
    orders = (RefundOrder("a", 5000, 20, 5000, False), RefundOrder("b", 2500, 4, 1250, False))
    task = Task("t", Kind.REFUND, "hard", "test", "x", 5250, orders)
    assert expected_refund_cents(task) == 5250


def test_labels_must_be_exactly_an_allowed_word():
    assert parse_label(" Billing. ") == "billing"
    assert parse_label('"shipping"') == "shipping"
    assert parse_label("customer support") is None
    assert parse_label("billing issue") is None
    assert check_label_shape("returns") and not check_label_shape("nonsense")
    assert check_label_agreement("billing", "Billing.") and not check_label_agreement("billing", "returns")
    assert not check_label_agreement("nonsense", "nonsense")


def test_amounts_are_read_to_the_cent():
    assert parse_amount_cents("$40.00") == 4000
    assert parse_amount_cents("12") == 1200
    assert parse_amount_cents("1,234.5") == 123450
    assert parse_amount_cents("Worked out: 50 - 10 = 40\nRefund: 40.00") == 4000
    assert parse_amount_cents("Refund: $5.00 ... then\nRefund: $7.25") == 725
    assert parse_amount_cents("The refund is 40.00 dollars") is None
    assert parse_amount_cents("no number") is None


def test_quotes_are_matched_against_the_policy_lines():
    reply = f'Answer: Yes.\nQuote: "{POLICY_LINES[0]}"'
    assert parse_quote(reply) == normalize(POLICY_LINES[0])
    assert quoted_line_index(reply) == 0
    assert quoted_line_index('Answer: x\nQuote: "Something else."') is None
    assert quoted_line_index("no quote at all") is None
    assert quoted_line_index(f'Answer: x\nQuote: "{POLICY_LINES[2]}"\n\nQuestion: and then it kept going') == 2
    assert check_policy(reply) and not check_policy("Answer: 2.")


def test_grading_is_the_ground_truth_and_checks_see_only_the_answer():
    assert is_correct(label_task(gold="billing"), "billing")
    assert not is_correct(label_task(gold="billing"), "returns")
    task = refund_task(days=20, total=5000)
    assert is_correct(task, "40.00") and check_refund(task, "$40.00")
    assert not is_correct(task, "50.00") and not check_refund(task, "50.00")
    right = f'Answer: ok\nQuote: "{POLICY_LINES[0]}"'
    wrong_line = f'Answer: ok\nQuote: "{POLICY_LINES[1]}"'
    assert is_correct(policy_task(gold=0), right) and not is_correct(policy_task(gold=0), wrong_line)
    assert check_policy(wrong_line)  # the check accepts a real line even when it is the wrong one: a false accept


def test_the_hard_signal_sees_two_orders_or_an_exception_word():
    assert hard_signal(Task("t", Kind.REFUND, "hard", "test", "Order PR-100001 and PR-200002 are returned.", 0))
    assert hard_signal(Task("t", Kind.REFUND, "hard", "test", "The item was damaged.", 0))
    assert not hard_signal(label_task(text="I was charged twice for PR-100001."))


def test_the_price_table_costs_billed_tokens_and_needs_every_tier():
    prices = PriceTable("2026-10-27", {"small": 0.0002, "medium": 0.0005, "large": 0.0012})
    assert prices.cost("large", Usage(500, 500)) == pytest.approx(0.0012)
    assert prices.estimate("small", 1000) == pytest.approx(0.0002)
    with pytest.raises(ValueError, match="lacks tiers"):
        PriceTable("x", {"small": 1.0})


def test_day_budget_tracks_its_share():
    day = DayBudget(2.0)
    day.add(1.5)
    assert day.used_share() == 0.75
    with pytest.raises(ValueError, match="positive"):
        DayBudget(0)


def test_router_config_picks_the_start_tier_for_hard_tasks():
    config = RouterConfig(
        {"label": "medium", "refund": "small", "policy": "small"}, {"refund": "medium"}, "agreement", 0.01, 0.8
    )
    assert config.start_index("label", False) == 1
    assert config.start_index("refund", False) == 0
    assert config.start_index("refund", True) == 1
    assert config.start_index("policy", True) == 0


def test_rates_and_check_rates():
    assert rate(3, 4).value == 0.75 and rate(0, 0).value == 0.0
    assert cost_per_correct(1.0, 4) == 0.25 and cost_per_correct(1.0, 0) is None
    r = check_rates([True, True, False, True], [True, False, True, False])
    assert (r.accepted, r.wrong, r.right, r.false_accepts, r.false_rejects) == (3, 2, 2, 2, 1)
    assert r.false_accept_rate == 1.0 and r.false_reject_rate == 0.5 and r.wrong_among_accepted == pytest.approx(2 / 3)
    empty = check_rates([], [])
    assert empty.false_accept_rate == 0.0 and empty.wrong_among_accepted == 0.0


def test_bootstrap_intervals():
    low, high = bootstrap_cost_per_correct([1.0] * 10, [True] * 10)
    assert low == high == 1.0
    assert bootstrap_cost_per_correct([], []) == (0.0, 0.0)
    assert bootstrap_cost_per_correct([1.0, 1.0], [False, False])[0] == float("inf")
    diff, low, high = bootstrap_accuracy_difference([True] * 10, [False] * 10)
    assert diff == 1.0 and low == 1.0 and high == 1.0
    assert bootstrap_accuracy_difference([], []) == (0.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="equal lengths"):
        bootstrap_accuracy_difference([True], [])


def test_shuffled_indices_is_a_deterministic_permutation():
    order = shuffled_indices(20, 11)
    assert sorted(order) == list(range(20)) and order == shuffled_indices(20, 11) and order != list(range(20))


def test_the_overlap_check_needs_the_best_matching_line_to_be_unique():
    assert best_matching_line("Who pays return shipping?") == 1
    assert best_matching_line("Do you match lower prices from other shops?") == 7
    assert best_matching_line("zzz qqq") is None
    assert content_words("How many days do I have?") == {"many", "day", "have"}
    assert check_policy_overlap("Who pays return shipping?", f'Quote: "{POLICY_LINES[1]}"')
    assert not check_policy_overlap("Who pays return shipping?", f'Quote: "{POLICY_LINES[6]}"')
    assert not check_policy_overlap("zzz", f'Quote: "{POLICY_LINES[0]}"')
