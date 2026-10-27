"""Prompt templates use `{{name}}` placeholders; rendering fails loudly on a missing value or a leftover."""

from __future__ import annotations

import re

PLACEHOLDER = re.compile(r"\{\{([a-z_]+)\}\}")


def render(template: str, **values: str) -> str:
    """Fill the placeholders; an unknown or unfilled one is an error, never a silent blank."""
    unknown = set(values) - set(PLACEHOLDER.findall(template))
    if unknown:
        raise ValueError(f"template has no placeholder for {sorted(unknown)}")

    def fill(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in values:
            raise ValueError(f"no value for placeholder {{{{{name}}}}}")
        return values[name]

    return PLACEHOLDER.sub(fill, template)
