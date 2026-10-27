"""Retry with exponential backoff and jitter, for adapters that call a network."""

from __future__ import annotations

import random
from collections.abc import Callable

from cost_router.application.ports import Clock
from cost_router.domain.llm import RetryableModelError


def retry_call[T](
    operation: Callable[[], T],
    *,
    attempts: int,
    clock: Clock,
    base_delay_s: float = 0.5,
    max_delay_s: float = 8.0,
    rng: random.Random | None = None,
) -> T:
    """Run `operation`, retrying only RetryableModelError with backoff and full-range jitter (50% to 100%)."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    jitter = rng or random.Random()
    for attempt in range(attempts):
        try:
            return operation()
        except RetryableModelError:
            if attempt == attempts - 1:
                raise
            clock.sleep(min(max_delay_s, base_delay_s * 2**attempt) * jitter.uniform(0.5, 1.0))
    raise AssertionError("unreachable")  # pragma: no cover
