"""The difficulty signal the router can see before it calls any model: two order ids, or an exception word."""

from __future__ import annotations

from cost_router.domain.tasks import EXCEPTION_WORDS, ORDER_ID, Task


def hard_signal(task: Task) -> bool:
    """True when the text mentions two or more order ids, or a damage or partial-return word."""
    lowered = task.text.lower()
    return len(set(ORDER_ID.findall(task.text))) >= 2 or any(word in lowered for word in EXCEPTION_WORDS)
