"""Router configuration, the daily budget and the records a routing decision leaves."""

from __future__ import annotations

from dataclasses import dataclass, field

from cost_router.domain.pricing import TIERS


@dataclass(frozen=True)
class Bar:
    """Numbers agreed before any result was seen (config/bar.json)."""

    false_accept_bar: float
    hard_accuracy_bar: float
    accuracy_margin: float
    request_cap: float
    tighten_at: float
    day_budget_fractions: tuple[float, ...]


@dataclass(frozen=True)
class RouterConfig:
    """What the build set decided (config/router.json) plus the limits."""

    start: dict[str, str]
    hard_start: dict[str, str]
    label_check: str
    request_cap: float
    tighten_at: float
    policy_check: str = "quote"

    def start_index(self, kind: str, hard: bool) -> int:
        """The index in TIERS where this kind of task starts."""
        tier = self.hard_start.get(kind) if hard and self.hard_start.get(kind) else self.start[kind]
        return TIERS.index(tier)


class DayBudget:
    """The money spent so far against a daily budget."""

    def __init__(self, budget: float) -> None:
        if budget <= 0:
            raise ValueError("a budget must be positive")
        self.budget = budget
        self.used = 0.0

    def used_share(self) -> float:
        """Spent divided by budget."""
        return self.used / self.budget

    def add(self, amount: float) -> None:
        """Record spending."""
        self.used += amount


@dataclass(frozen=True)
class Attempt:
    """One tier tried for one task."""

    tier: str
    passed: bool
    cost: float
    tokens: int


@dataclass(frozen=True)
class Decision:
    """What the router did with one task. `served_by` is a tier name or `escalate_to_person`."""

    task_id: str
    answer: str | None
    served_by: str
    attempts: tuple[Attempt, ...]
    spent: float
    tokens: int
    share_before: float = 0.0
    tags: tuple[str, ...] = field(default_factory=tuple)
