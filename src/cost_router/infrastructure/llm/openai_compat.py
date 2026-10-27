"""An adapter for any server that speaks the OpenAI chat-completions protocol (a local ollama or llama.cpp
server, or a hosted provider). The key, when there is one, comes from the environment."""

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
from cost_router.infrastructure.llm.retry import retry_call


def raise_for_status(response: httpx.Response) -> None:
    """Map an HTTP status to the retryable or permanent error the application understands."""
    status = response.status_code
    if status < 400:
        return
    detail = response.text[:200]
    if status == 429 or status >= 500:
        raise RetryableModelError(f"provider returned {status}: {detail}")
    raise PermanentModelError(f"provider returned {status}: {detail}")


class OpenAICompatibleChatModel:
    """Chat completions over HTTP with a timeout, retries and backoff."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        client: httpx.Client | None = None,
        attempts: int = 3,
        clock: Clock | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = client or httpx.Client()
        self._attempts = attempts
        self._clock = clock or SystemClock()

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Send the request, retrying timeouts, 429 and 5xx."""
        return retry_call(lambda: self._once(request, timeout_s), attempts=self._attempts, clock=self._clock)

    def _once(self, request: ChatRequest, timeout_s: float) -> ChatResponse:
        body: dict[str, Any] = {
            "model": request.model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": False,
        }
        if request.seed is not None:
            body["seed"] = request.seed
        started = time.perf_counter()
        try:
            response = self._client.post(
                f"{self._base_url}/chat/completions", json=body, headers=self._headers, timeout=timeout_s
            )
        except (httpx.TimeoutException, httpx.TransportError) as error:
            raise RetryableModelError(f"transport failure: {type(error).__name__}") from error
        raise_for_status(response)
        elapsed = time.perf_counter() - started
        try:
            data = response.json()
            choice = data["choices"][0]
            usage = data.get("usage") or {}
            return ChatResponse(
                text=choice["message"]["content"] or "",
                usage=Usage(int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))),
                model=str(data.get("model", request.model)),
                finish_reason=str(choice.get("finish_reason") or "stop"),
                latency_s=elapsed,
            )
        except (KeyError, IndexError, ValueError, TypeError) as error:
            raise PermanentModelError("the provider's reply did not have the expected shape") from error
