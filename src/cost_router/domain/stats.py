"""Small, dependency-free statistics: percentiles, Wilson intervals and a seeded paired bootstrap.

The random generator is a SplitMix64 written out here so that the Java port produces the same intervals
from the same seed.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

_MASK = (1 << 64) - 1


class SplitMix64:
    """A tiny deterministic generator (the same arithmetic in the Python and the Java code)."""

    def __init__(self, seed: int) -> None:
        self._state = seed & _MASK

    def next_u64(self) -> int:
        """The next 64-bit value."""
        self._state = (self._state + 0x9E3779B97F4A7C15) & _MASK
        z = self._state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
        return z ^ (z >> 31)

    def below(self, bound: int) -> int:
        """A value in [0, bound). The modulo bias is negligible for the sizes used here."""
        if bound <= 0:
            raise ValueError("bound must be positive")
        return self.next_u64() % bound


def mean(values: Sequence[float]) -> float:
    """The arithmetic mean; zero for an empty sequence."""
    return sum(values) / len(values) if values else 0.0


def percentile(values: Sequence[float], q: float) -> float:
    """The q-th percentile (0 to 100) by linear interpolation between closest ranks; zero when empty."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q / 100.0
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    """The Wilson score interval for a proportion; (0, 1) when there are no trials."""
    if trials <= 0:
        return 0.0, 1.0
    p = successes / trials
    denominator = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denominator
    margin = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator
    return max(0.0, centre - margin), min(1.0, centre + margin)


def bootstrap_mean_interval(
    values: Sequence[float], resamples: int = 2000, seed: int = 7, level: float = 0.95
) -> tuple[float, float]:
    """A percentile bootstrap interval for the mean of per-item values."""
    if not values:
        return 0.0, 0.0
    rng = SplitMix64(seed)
    n = len(values)
    means = sorted(sum(values[rng.below(n)] for _ in range(n)) / n for _ in range(resamples))
    tail = (1 - level) / 2
    return means[int(tail * resamples)], means[min(resamples - 1, int((1 - tail) * resamples))]


def paired_bootstrap_difference(
    treatment: Sequence[float], control: Sequence[float], resamples: int = 2000, seed: int = 7, level: float = 0.95
) -> tuple[float, tuple[float, float]]:
    """The mean of (treatment - control) over paired items and its percentile bootstrap interval."""
    if len(treatment) != len(control):
        raise ValueError("a paired comparison needs the same number of items on both sides")
    differences = [t - c for t, c in zip(treatment, control, strict=True)]
    return mean(differences), bootstrap_mean_interval(differences, resamples, seed, level)


def shuffled_indices(n: int, seed: int) -> list[int]:
    """A seeded Fisher-Yates permutation of range(n), the same in the Python and Java ports."""
    rng = SplitMix64(seed)
    order = list(range(n))
    for i in range(n - 1, 0, -1):
        j = rng.below(i + 1)
        order[i], order[j] = order[j], order[i]
    return order
