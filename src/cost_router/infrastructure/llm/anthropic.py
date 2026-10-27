"""An adapter for the Anthropic Messages API, over plain HTTP. The key comes from the environment; this adapter
is exercised only by the opt-in live test (`make test-live`)."""

from __future__ import annotations

import time
from typing import Any

import httpx

from cost_router.application.ports import Clock
from cost_router.domain.llm import (
    ChatRequest,
    ChatResponse,
    PermanentModelError,
    RetryableModelError,
    Usage,
)
from cost_router.infrastructure.clock import SystemClock
from cost_router.infrastructure.llm.openai_compat import raise_for_status
from cost_router.infrastructure.llm.retry import retry_call

API_VERSION = "2023-06-01"


class AnthropicChatModel:
    """Messages API calls with a timeout, retries and backoff."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.anthropic.com",
        client: httpx.Client | None = None,
        attempts: int = 3,
        clock: Clock | None = None,
    ) -> None:
        if not api_key:
            raise PermanentModelError("ANTHROPIC_API_KEY is not set")
        self._base_url = base_url.rstrip("/")
        self._headers = {"x-api-key": api_key, "anthropic-version": API_VERSION, "content-type": "application/json"}
        self._client = client or httpx.Client()
        self._attempts = attempts
        self._clock = clock or SystemClock()

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Send the request, retrying timeouts, 429 and 5xx."""
        return retry_call(lambda: self._once(request, timeout_s), attempts=self._attempts, clock=self._clock)

    def _once(self, request: ChatRequest, timeout_s: float) -> ChatResponse:
        body: dict[str, Any] = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages if m.role != "system"],
        }
        system = request.system_text()
        if system:
            body["system"] = system
        started = time.perf_counter()
        try:
            response = self._client.post(
                f"{self._base_url}/v1/messages", json=body, headers=self._headers, timeout=timeout_s
            )
        except (httpx.TimeoutException, httpx.TransportError) as error:
            raise RetryableModelError(f"transport failure: {type(error).__name__}") from error
        raise_for_status(response)
        elapsed = time.perf_counter() - started
        try:
            data = response.json()
            text = "".join(block["text"] for block in data["content"] if block.get("type") == "text")
            usage = data["usage"]
            return ChatResponse(
                text=text,
                usage=Usage(int(usage["input_tokens"]), int(usage["output_tokens"])),
                model=str(data.get("model", request.model)),
                finish_reason=str(data.get("stop_reason") or "stop"),
                latency_s=elapsed,
            )
        except (KeyError, ValueError, TypeError) as error:
            raise PermanentModelError("the provider's reply did not have the expected shape") from error
