"""Accuracy, cost per correct answer, and false-accept and false-reject rates."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from cost_router.domain.stats import SplitMix64, wilson_interval


@dataclass(frozen=True)
class Rate:
    """A proportion with its Wilson interval."""

    successes: int
    trials: int
    value: float
    low: float
    high: float


def rate(successes: int, trials: int) -> Rate:
    """A rate and its 95% Wilson interval; zero trials gives value 0 and the whole range."""
    low, high = wilson_interval(successes, trials)
    return Rate(successes, trials, successes / trials if trials else 0.0, low, high)


def cost_per_correct(total_cost: float, correct: int) -> float | None:
    """Money spent divided by right answers; None when nothing was right."""
    return total_cost / correct if correct else None


def bootstrap_cost_per_correct(
    costs: Sequence[float], corrects: Sequence[bool], resamples: int = 2000, seed: int = 7
) -> tuple[float, float]:
    """A 95% bootstrap interval for total cost over right answers, resampling whole tasks."""
    n = len(costs)
    if n == 0:
        return 0.0, 0.0
    rng = SplitMix64(seed)
    values: list[float] = []
    for _ in range(resamples):
        total = 0.0
        right = 0
        for _ in range(n):
            i = rng.below(n)
            total += costs[i]
            right += corrects[i]
        values.append(total / right if right else float("inf"))
    values.sort()
    return values[int(0.025 * resamples)], values[min(resamples - 1, int(0.975 * resamples))]


def bootstrap_accuracy_difference(
    a: Sequence[bool], b: Sequence[bool], resamples: int = 2000, seed: int = 7
) -> tuple[float, float, float]:
    """Mean of (a - b) over paired tasks and its 95% bootstrap interval."""
    if len(a) != len(b):
        raise ValueError("paired comparison needs equal lengths")
    n = len(a)
    if n == 0:
        return 0.0, 0.0, 0.0
    diffs = [float(x) - float(y) for x, y in zip(a, b, strict=True)]
    rng = SplitMix64(seed)
    means = sorted(sum(diffs[rng.below(n)] for _ in range(n)) / n for _ in range(resamples))
    return sum(diffs) / n, means[int(0.025 * resamples)], means[min(resamples - 1, int(0.975 * resamples))]


@dataclass(frozen=True)
class CheckRates:
    """How a check behaves against the ground truth."""

    accepted: int
    wrong: int
    right: int
    false_accepts: int
    false_rejects: int
    false_accept_rate: float
    false_reject_rate: float
    wrong_among_accepted: float


def check_rates(passed: Sequence[bool], correct: Sequence[bool]) -> CheckRates:
    """False-accept rate = wrong answers accepted / wrong answers; false-reject rate = right answers rejected / right
    answers; wrong-among-accepted = accepted answers that are wrong / accepted answers."""
    accepted = sum(passed)
    wrong = sum(1 for c in correct if not c)
    right = len(correct) - wrong
    false_accepts = sum(1 for p, c in zip(passed, correct, strict=True) if p and not c)
    false_rejects = sum(1 for p, c in zip(passed, correct, strict=True) if not p and c)
    return CheckRates(
        accepted,
        wrong,
        right,
        false_accepts,
        false_rejects,
        false_accepts / wrong if wrong else 0.0,
        false_rejects / right if right else 0.0,
        false_accepts / accepted if accepted else 0.0,
    )
