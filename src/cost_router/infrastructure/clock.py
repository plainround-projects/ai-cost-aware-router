"""Clocks: the real one, and a manual one for tests and simulations."""

from __future__ import annotations

import time


class SystemClock:
    """Wall time and real sleeping."""

    def monotonic(self) -> float:
        """Seconds from the monotonic clock."""
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        """Block for the given seconds."""
        if seconds > 0:
            time.sleep(seconds)


class ManualClock:
    """A clock that only moves when told to; `sleep` advances it instead of waiting."""

    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def monotonic(self) -> float:
        """The current manual time."""
        return self._now

    def sleep(self, seconds: float) -> None:
        """Advance the manual time."""
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        """Move time forward."""
        if seconds < 0:
            raise ValueError("time cannot go backward")
        self._now += seconds
