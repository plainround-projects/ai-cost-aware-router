"""The checks the router runs on an answer (no gold answer is visible to them)."""

from __future__ import annotations

from dataclasses import dataclass

from cost_router.application.tiers import ModelTiers
from cost_router.domain.checks import (
    check_label_agreement,
    check_label_shape,
    check_policy,
    check_policy_overlap,
    check_refund,
)
from cost_router.domain.tasks import Kind, Task


@dataclass(frozen=True)
class CheckResult:
    """Whether the answer may be accepted, and what running the check cost."""

    passed: bool
    extra_cost: float = 0.0
    extra_tokens: int = 0


@dataclass(frozen=True)
class AnswerChecks:
    """Label: allowed value (`shape`) or allowed value that a second sample repeats (`agreement`). Refund: recomputed
    by code. Policy: the quoted line exists
    (`quote`), or exists and is the line that best matches the question (`overlap`)."""

    tiers: ModelTiers
    label_check: str = "agreement"
    policy_check: str = "quote"

    def check(self, task: Task, tier: str, text: str) -> CheckResult:
        """Run the check for the task's kind."""
        if task.kind is Kind.REFUND:
            return CheckResult(check_refund(task, text))
        if task.kind is Kind.POLICY:
            return CheckResult(
                check_policy_overlap(task.text, text) if self.policy_check == "overlap" else check_policy(text)
            )
        if self.label_check == "shape":
            return CheckResult(check_label_shape(text))
        second = self.tiers.call(tier, task, second_sample=True)
        return CheckResult(check_label_agreement(text, second.text), second.cost, second.tokens)

    def estimate_extra(self, task: Task, tier: str) -> float:
        """The money a check will add (only the label agreement check calls a model)."""
        if task.kind is Kind.LABEL and self.label_check == "agreement":
            return self.tiers.estimate(tier, task)
        return 0.0
