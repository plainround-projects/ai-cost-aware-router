"""The three model tiers: building each task's prompt, calling the tier's model, and costing the call."""

from __future__ import annotations

from dataclasses import dataclass

from cost_router.application.ports import ChatModel, PromptStore
from cost_router.application.templates import render
from cost_router.domain.llm import ChatRequest, Message, Usage
from cost_router.domain.pricing import PriceTable
from cost_router.domain.tasks import POLICY_LINES, REFUND_POLICY, Kind, Task

MAX_TOKENS = {Kind.LABEL: 8, Kind.REFUND: 80, Kind.POLICY: 80}
SECOND_SAMPLE = {"temperature": 0.8, "seed": 7}


@dataclass(frozen=True)
class Answered:
    """One model answer with what it cost."""

    text: str
    cost: float
    usage: Usage
    latency_s: float

    @property
    def tokens(self) -> int:
        """Billed tokens."""
        return self.usage.total


@dataclass(frozen=True)
class ModelTiers:
    """Calls the model behind a tier name; the same code serves recorded, local and hosted models."""

    model: ChatModel
    prompts: PromptStore
    models: dict[str, str]
    prices: PriceTable

    def prompt(self, task: Task) -> str:
        """The rendered prompt of a task."""
        if task.kind is Kind.LABEL:
            return render(self.prompts.get("label.v2"), text=task.text)
        if task.kind is Kind.REFUND:
            return render(self.prompts.get("refund.v2"), policy=REFUND_POLICY, text=task.text)
        lines = "\n".join(f"{i + 1}. {line}" for i, line in enumerate(POLICY_LINES))
        return render(self.prompts.get("policy.v2"), policy_lines=lines, text=task.text)

    def request(self, tier: str, task: Task, second_sample: bool = False) -> ChatRequest:
        """The chat request for a tier; the second sample differs in temperature and seed."""
        extras = SECOND_SAMPLE if second_sample else {"temperature": 0.0, "seed": None}
        return ChatRequest(
            self.models[tier],
            (Message("user", self.prompt(task)),),
            temperature=float(extras["temperature"] or 0.0),
            max_tokens=MAX_TOKENS[task.kind],
            seed=extras["seed"],  # type: ignore[arg-type]
        )

    def call(self, tier: str, task: Task, second_sample: bool = False) -> Answered:
        """Ask a tier; the cost comes from the billed tokens and the price table."""
        response = self.model.complete(self.request(tier, task, second_sample))
        return Answered(
            response.text.strip(), self.prices.cost(tier, response.usage), response.usage, response.latency_s
        )

    def estimate(self, tier: str, task: Task, calls: int = 1) -> float:
        """What `calls` calls of this task would cost, from a rough token count made before calling."""
        # Three characters per token over-counts English (it is nearer four), so the estimate errs high and the
        # per-request cap holds even when a prompt tokenizes worse than usual. The billed usage is checked afterwards.
        tokens = (len(self.prompt(task)) + 2) // 3 + MAX_TOKENS[task.kind]
        return self.prices.estimate(tier, tokens) * calls
