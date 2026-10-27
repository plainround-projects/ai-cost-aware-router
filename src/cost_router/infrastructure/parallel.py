"""Run independent jobs on a few threads, keeping the input order of the results."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def thread_mapper(workers: int) -> Callable[[Callable[[T], R], Sequence[T]], list[R]]:
    """A mapper that uses `workers` threads (one means no threads at all)."""

    def run(function: Callable[[T], R], items: Sequence[T]) -> list[R]:
        if workers <= 1:
            return [function(item) for item in items]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(function, items))

    return run
