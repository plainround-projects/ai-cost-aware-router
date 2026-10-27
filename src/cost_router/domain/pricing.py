"""The dated price table. Prices are per 1,000 billed tokens, input and output alike."""

from __future__ import annotations

from dataclasses import dataclass

from cost_router.domain.llm import Usage

TIERS = ("small", "medium", "large")


@dataclass(frozen=True)
class PriceTable:
    """Prices as of a date, so a number in a report can be traced to the table that produced it."""

    as_of: str
    per_1k_tokens: dict[str, float]

    def __post_init__(self) -> None:
        missing = [t for t in TIERS if t not in self.per_1k_tokens]
        if missing:
            raise ValueError(f"price table lacks tiers {missing}")

    def cost(self, tier: str, usage: Usage) -> float:
        """The cost of one call from its billed tokens."""
        return usage.total / 1000 * self.per_1k_tokens[tier]

    def estimate(self, tier: str, tokens: int) -> float:
        """The cost of a call of the given token count (used before the call, from an estimate)."""
        return tokens / 1000 * self.per_1k_tokens[tier]
