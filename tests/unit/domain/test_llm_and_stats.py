import pytest

from cost_router.domain.llm import ChatRequest, Message, Price, Usage, estimate_tokens
from cost_router.domain.stats import (
    SplitMix64,
    bootstrap_mean_interval,
    mean,
    paired_bootstrap_difference,
    percentile,
    wilson_interval,
)


def request(text="hi", **kw):
    return ChatRequest(model="m", messages=(Message("user", text),), **kw)


def test_fixture_key_is_stable_and_depends_on_every_decoding_setting():
    assert request().fixture_key() == request().fixture_key()
    assert request().fixture_key() != request("other").fixture_key()
    assert request().fixture_key() != request(temperature=0.5).fixture_key()
    assert request().fixture_key() != request(max_tokens=10).fixture_key()
    assert request().fixture_key() != request(seed=1).fixture_key()


def test_a_request_rejects_bad_values():
    with pytest.raises(ValueError):
        ChatRequest(model="", messages=(Message("user", "x"),))
    with pytest.raises(ValueError):
        ChatRequest(model="m", messages=())
    with pytest.raises(ValueError):
        request(temperature=3.0)
    with pytest.raises(ValueError):
        request(max_tokens=0)
    with pytest.raises(ValueError):
        Message("robot", "x")


def test_cost_comes_from_billed_usage_and_the_price_table():
    price = Price(input_per_1k=0.5, output_per_1k=1.5)
    assert price.cost(Usage(2000, 1000)) == pytest.approx(2.5)
    assert Usage(3, 4).total == 7


def test_system_text_joins_system_messages():
    req = ChatRequest("m", (Message("system", "a"), Message("user", "u"), Message("system", "b")))
    assert req.system_text() == "a\nb"


def test_estimate_tokens_is_about_four_characters_each():
    assert estimate_tokens("abcdefgh") == 2
    assert estimate_tokens("") == 1


def test_percentile_interpolates_between_ranks():
    assert percentile([1, 2, 3, 4], 50) == pytest.approx(2.5)
    assert percentile([5], 95) == 5
    assert percentile([], 50) == 0.0
    assert percentile([1, 2, 3, 4, 5], 100) == 5


def test_wilson_interval_brackets_the_rate_and_is_wide_for_few_trials():
    low, high = wilson_interval(2, 2)
    assert 0.3 < low < 0.5 and high == 1.0
    assert wilson_interval(0, 0) == (0.0, 1.0)
    low, high = wilson_interval(50, 100)
    assert low < 0.5 < high


def test_splitmix_is_deterministic_and_bounded():
    a, b = SplitMix64(42), SplitMix64(42)
    assert [a.next_u64() for _ in range(3)] == [b.next_u64() for _ in range(3)]
    assert SplitMix64(42).next_u64() == 13679457532755275413
    with pytest.raises(ValueError):
        SplitMix64(1).below(0)
    assert all(0 <= SplitMix64(i).below(5) < 5 for i in range(20))


def test_paired_bootstrap_excludes_zero_for_a_clear_gain_and_includes_it_for_noise():
    gain, (low, high) = paired_bootstrap_difference([1.0] * 20, [0.0] * 20)
    assert gain == 1.0 and low == 1.0 and high == 1.0
    _, (low, high) = paired_bootstrap_difference([1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1])
    assert low < 0 < high
    with pytest.raises(ValueError):
        paired_bootstrap_difference([1.0], [1.0, 2.0])


def test_bootstrap_of_nothing_and_mean_of_nothing_are_zero():
    assert bootstrap_mean_interval([]) == (0.0, 0.0)
    assert mean([]) == 0.0
