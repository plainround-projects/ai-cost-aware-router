"""Prompt templates read from versioned files under prompts/."""

from __future__ import annotations

from pathlib import Path


class FilePromptStore:
    """Looks up `<name>.md` in a directory; a missing prompt is a clear error."""

    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def get(self, name: str) -> str:
        """The template text with the trailing newline removed (the Java port does the same)."""
        path = self._directory / f"{name}.md"
        if not path.is_file():
            raise FileNotFoundError(f"no prompt named {name!r} in {self._directory}")
        return path.read_text(encoding="utf-8").rstrip("\n")
