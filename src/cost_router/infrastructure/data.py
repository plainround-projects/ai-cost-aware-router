"""Reading the task set, the bars, the price table and the router configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cost_router.domain.pricing import PriceTable
from cost_router.domain.routing import Bar, RouterConfig
from cost_router.domain.tasks import Kind, RefundOrder, Task


def load_tasks(data_dir: Path) -> list[Task]:
    """All 300 tasks in id order."""
    tasks = []
    with (data_dir / "tasks.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            tasks.append(
                Task(
                    row["task_id"],
                    Kind(row["kind"]),
                    row["difficulty"],
                    row["split"],
                    row["text"],
                    row["gold"],
                    tuple(RefundOrder(**o) for o in row.get("orders", [])),
                )
            )
    return tasks


def load_bar(config_dir: Path) -> Bar:
    """The numbers agreed before any result."""
    raw = json.loads((config_dir / "bar.json").read_text(encoding="utf-8"))
    return Bar(
        raw["false_accept_bar"],
        raw["hard_accuracy_bar"],
        raw["accuracy_margin"],
        raw["request_cap"],
        raw["tighten_at"],
        tuple(raw["day_budget_fractions"]),
    )


def load_prices(config_dir: Path) -> PriceTable:
    """The dated price table."""
    raw = json.loads((config_dir / "prices.json").read_text(encoding="utf-8"))
    return PriceTable(raw["as_of"], raw["per_1k_tokens"])


def router_config_to_json(config: RouterConfig) -> dict[str, Any]:
    """The configuration as plain data."""
    return {
        "start": config.start,
        "hard_start": config.hard_start,
        "label_check": config.label_check,
        "policy_check": config.policy_check,
        "request_cap": config.request_cap,
        "tighten_at": config.tighten_at,
    }


def load_router_config(path: Path) -> RouterConfig:
    """What `tune` wrote."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return RouterConfig(
        raw["start"],
        raw["hard_start"],
        raw["label_check"],
        raw["request_cap"],
        raw["tighten_at"],
        raw.get("policy_check", "quote"),
    )
