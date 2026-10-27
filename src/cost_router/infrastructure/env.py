"""Validated reads from the process environment (twelve-factor configuration)."""

from __future__ import annotations

import os
from collections.abc import Mapping


class ConfigError(ValueError):
    """An environment variable is missing or has an invalid value."""


def read_str(env: Mapping[str, str], name: str, default: str | None = None) -> str:
    """A non-empty string variable, or the default when it is unset."""
    value = env.get(name, "").strip()
    if value:
        return value
    if default is None:
        raise ConfigError(f"{name} is required")
    return default


def read_int(env: Mapping[str, str], name: str, default: int, minimum: int = 0) -> int:
    """An integer variable at or above a minimum."""
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as error:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from error
    if value < minimum:
        raise ConfigError(f"{name} must be at least {minimum}, got {value}")
    return value


def read_float(env: Mapping[str, str], name: str, default: float, minimum: float = 0.0) -> float:
    """A float variable at or above a minimum."""
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError as error:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from error
    if value < minimum:
        raise ConfigError(f"{name} must be at least {minimum}, got {value}")
    return value


def process_env() -> Mapping[str, str]:
    """The real environment (a function so that tests can pass a dict instead)."""
    return os.environ
