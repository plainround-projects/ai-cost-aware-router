"""Writing reports as JSON, JSONL and Markdown with stable key order and rounded floats."""

from __future__ import annotations

import dataclasses
import json
from enum import Enum
from pathlib import Path
from typing import Any


def to_jsonable(value: Any) -> Any:
    """Dataclasses, enums and tuples as plain JSON data; floats rounded to 6 places."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: to_jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [to_jsonable(v) for v in value]
    if isinstance(value, float):
        return round(value, 6) if value != float("inf") else None
    return value


def dump_json(path: Path, value: Any) -> None:
    """Write one JSON document, indented, keys sorted."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(to_jsonable(value), indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def dump_jsonl(path: Path, rows: list[Any]) -> None:
    """Write one JSON object per line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(to_jsonable(row), sort_keys=True, ensure_ascii=False) + "\n")


def load_json(path: Path) -> Any:
    """Read one JSON document."""
    return json.loads(path.read_text(encoding="utf-8"))
