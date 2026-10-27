"""Small fakes shared by the unit tests."""

from __future__ import annotations

from collections.abc import Callable

from cost_router.application.tiers import ModelTiers
from cost_router.domain.llm import ChatRequest, ChatResponse, Usage
from cost_router.domain.pricing import PriceTable
from cost_router.domain.routing import RouterConfig
from cost_router.domain.tasks import Kind, RefundOrder, Task

PRICES = PriceTable("2026-10-27", {"small": 0.0002, "medium": 0.0005, "large": 0.0012})
MODELS = {"small": "m-small", "medium": "m-medium", "large": "m-large"}


class ScriptedModel:
    """A chat model whose answer is computed from the request by a function (tokens: 100 in, 10 out)."""

    def __init__(self, answer: Callable[[ChatRequest], str], realistic_usage: bool = False) -> None:
        self.answer = answer
        self.realistic_usage = realistic_usage
        self.requests: list[ChatRequest] = []

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        self.requests.append(request)
        # four characters per token, like English text, when asked to be realistic
        usage = Usage(sum(len(m.content) for m in request.messages) // 4, 8) if self.realistic_usage else Usage(100, 10)
        return ChatResponse(self.answer(request), usage, request.model, latency_s=0.1)


class DictPrompts:
    def __init__(self) -> None:
        self.templates = {
            "label.v2": "LABEL {{text}}",
            "refund.v2": "REFUND {{policy}} {{text}}",
            "policy.v2": "POLICY {{policy_lines}} {{text}}",
        }

    def get(self, name: str) -> str:
        return self.templates[name]


def sequential(function, items):
    return [function(item) for item in items]


def tiers_for(answer: Callable[[ChatRequest], str], realistic_usage: bool = False) -> tuple[ModelTiers, ScriptedModel]:
    model = ScriptedModel(answer, realistic_usage)
    return ModelTiers(model, DictPrompts(), MODELS, PRICES), model


def label_task(task_id="t1", gold="billing", text="I was charged twice.", split="test") -> Task:
    return Task(task_id, Kind.LABEL, "easy", split, text, gold)


def refund_task(task_id="t2", days=20, total=5000, returned=5000, damaged=False, split="test") -> Task:
    order = RefundOrder("PR-100001", total, days, returned, damaged)
    text = f"Order {order.order_id} totaled ${total / 100:.2f} and arrived {days} days ago."
    from cost_router.domain.tasks import refund_cents

    return Task(task_id, Kind.REFUND, "easy", split, text, refund_cents(order), (order,))


def policy_task(task_id="t3", gold=0, split="test") -> Task:
    return Task(task_id, Kind.POLICY, "easy", split, "How many days to return?", gold)


def config(start=None, hard=None, label_check="agreement", cap=0.01, tighten=0.8) -> RouterConfig:
    return RouterConfig(
        start or {"label": "small", "refund": "small", "policy": "small"}, hard or {}, label_check, cap, tighten
    )
