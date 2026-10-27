"""Value types for talking to a chat model.

Nothing here knows about a vendor, an SDK or HTTP: adapters in the infrastructure layer translate these
types to and from a provider's wire format.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

ROLES = frozenset({"system", "user", "assistant"})


class ModelError(Exception):
    """Base class for every failure of a model call."""


class RetryableModelError(ModelError):
    """A failure that a second attempt may fix: a timeout, a 5xx, a rate limit, a dropped connection."""


class PermanentModelError(ModelError):
    """A failure that a retry cannot fix: a malformed request, a bad key, an unknown model."""


class FixtureMissError(PermanentModelError):
    """The recorded adapter has no response for this exact request (re-record with `make record`)."""


@dataclass(frozen=True)
class Message:
    """One chat message."""

    role: str
    content: str

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ValueError(f"unknown role {self.role!r}; expected one of {sorted(ROLES)}")


@dataclass(frozen=True)
class ChatRequest:
    """Everything that decides a model's answer: the model, the messages and the decoding settings."""

    model: str
    messages: tuple[Message, ...]
    temperature: float = 0.0
    max_tokens: int = 256
    seed: int | None = None

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("model must not be empty")
        if not self.messages:
            raise ValueError("a request needs at least one message")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

    def fixture_key(self) -> str:
        """A stable hash of the request; the Java port computes the same string, so both read one fixture file."""
        parts = [
            self.model,
            f"{self.temperature:.3f}",
            str(self.max_tokens),
            "-" if self.seed is None else str(self.seed),
            *(f"{m.role}\x1f{m.content}" for m in self.messages),
        ]
        return hashlib.sha256("\x1e".join(parts).encode("utf-8")).hexdigest()

    def system_text(self) -> str:
        """The system messages joined, or an empty string."""
        return "\n".join(m.content for m in self.messages if m.role == "system")


@dataclass(frozen=True)
class Usage:
    """Billed token counts as the provider reported them."""

    input_tokens: int
    output_tokens: int

    @property
    def total(self) -> int:
        """Input plus output tokens."""
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class ChatResponse:
    """A completed model call."""

    text: str
    usage: Usage
    model: str
    finish_reason: str = "stop"
    latency_s: float = 0.0


@dataclass(frozen=True)
class Price:
    """Dollars per 1,000 tokens, from a dated price table."""

    input_per_1k: float
    output_per_1k: float

    def cost(self, usage: Usage) -> float:
        """The cost of one call from its billed usage."""
        return usage.input_tokens / 1000 * self.input_per_1k + usage.output_tokens / 1000 * self.output_per_1k


def estimate_tokens(text: str) -> int:
    """A rough token count (about four characters per token) for estimates made before a call."""
    return max(1, (len(text) + 3) // 4)
