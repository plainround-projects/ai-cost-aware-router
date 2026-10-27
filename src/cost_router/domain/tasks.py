"""The tasks the router serves, the policy text they refer to, and the arithmetic that fixes the refund answers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

LABELS = ("billing", "shipping", "returns", "account")

REFUND_POLICY = (
    "Refunds are 100% of the returned items' price for returns within 15 days of delivery, 80% from day 16 to "
    "day 30, and nothing after day 30. Damaged items are refunded 100% of their price within 30 days."
)

POLICY_LINES = (
    "Returns are accepted within 30 days of delivery.",
    "The customer pays return shipping unless the item arrived damaged or wrong.",
    "Refunds reach the original payment method within 5 business days after the returned item arrives.",
    "An exchange for another size or color is free within 30 days if the item is unopened.",
    "A damaged item is refunded in full, with a prepaid return label, within 30 days of delivery.",
    "Gift cards pay for items only; they cannot pay for shipping.",
    "Electronics have a warranty of 12 months from delivery.",
    "We match a lower price from another shop within 7 days of purchase.",
    "An order can be cancelled for free until it ships, normally within 2 hours of ordering.",
    "We never sell or share a customer's personal data with other companies.",
)

ORDER_ID = re.compile(r"\bPR-\d{6}\b")
EXCEPTION_WORDS = ("damaged", "broken", "exception", "only part", "partial")


class Kind(StrEnum):
    """The three kinds of task."""

    LABEL = "label"
    REFUND = "refund"
    POLICY = "policy"


@dataclass(frozen=True)
class RefundOrder:
    """One order in a refund task."""

    order_id: str
    total_cents: int
    days: int
    returned_cents: int
    damaged: bool


@dataclass(frozen=True)
class Task:
    """A task whose answer code can check. `gold` is a label, an amount in cents, or a policy line index."""

    task_id: str
    kind: Kind
    difficulty: str
    split: str
    text: str
    gold: str | int
    orders: tuple[RefundOrder, ...] = ()


def refund_cents(order: dict[str, Any] | RefundOrder) -> int:
    """The refund for one order under REFUND_POLICY, in cents (half up)."""
    days, returned, damaged = (
        (order.days, order.returned_cents, order.damaged)
        if isinstance(order, RefundOrder)
        else (order["days"], order["returned_cents"], order["damaged"])
    )
    if days > 30:
        return 0
    if damaged or days <= 15:
        return int(returned)
    return (int(returned) * 80 + 50) // 100


def expected_refund_cents(task: Task) -> int:
    """The refund the policy gives for every order of the task."""
    return sum(refund_cents(o) for o in task.orders)


def money(cents: int) -> str:
    """Cents as dollars with two places."""
    return f"{cents // 100}.{cents % 100:02d}"
