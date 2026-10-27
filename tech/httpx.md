# httpx 0.28.1 (HTTP client)

## What it is

**HTTP** is the language web programs use to talk to each other. A **client** sends a **request**: a method (`GET` to read, `POST` to send data), an address (URL), headers and an optional body. The **server** answers with a **status code** (200 means OK, 404 not found, 429 too many requests, 500 server error), headers and a body. **httpx** is a Python library that sends such requests and gives you the response.

## Why this repository uses it

Talking to a model server (ollama, llama.cpp, a hosted provider) is an HTTP request with a JSON body. The adapters in `infrastructure/llm/` use `httpx` to send it, to set timeouts and to read the answer; tests pass in a fake client so no network is needed.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/cost_router/infrastructure/llm/openai_compat.py` | Chat completions over HTTP. |
| `src/cost_router/infrastructure/llm/anthropic.py` | Anthropic's Messages API over HTTP. |
| `tests/**/*.py (16 files)` | Tests use `httpx.MockTransport` or a local fake server. |
| `requirements.lock` | Pins httpx 0.28.1 and the libraries it needs (httpcore, h11, anyio, certifi, idna). |


## How it works underneath

**What happens on a request.** `client.post(url, json=body)` (1) resolves the host name to an IP address, (2) opens a TCP connection (and for `https` a TLS session that encrypts the traffic), (3) writes the request text: a line like `POST /v1/chat/completions HTTP/1.1`, header lines such as `Content-Type: application/json`, a blank line, and the body, (4) reads the response status line, headers and body, (5) returns a `Response` object. A `Client` keeps connections open and reuses them, which is faster than a new connection for each call.

**Timeouts.** Without a timeout a call can wait forever. `timeout=60.0` limits the connect, write, read and pool waits to 60 seconds each; exceeding it raises `httpx.TimeoutException`. `TransportError` covers dropped connections and DNS problems.

**Status handling.** httpx does not raise for 4xx/5xx by default. The code either calls `response.raise_for_status()` (raising `HTTPStatusError`) or inspects `status_code` itself, as the adapter does, to decide between retry and give-up.

**JSON.** `json=body` serialises the dictionary and sets the content type; `response.json()` parses the reply.

## Walkthrough of this repository's use

### The OpenAI-compatible adapter, whole file

`src/cost_router/infrastructure/llm/openai_compat.py`

<!-- fmt: off -->
```python
"""An adapter for any server that speaks the OpenAI chat-completions protocol (a local ollama or llama.cpp
server, or a hosted provider). The key, when there is one, comes from the environment."""
```
<!-- fmt: on -->

Module docstring: one adapter serves several programs that speak the same HTTP dialect (the "OpenAI chat-completions" protocol, see `chat-model-apis.md`).

<!-- fmt: off -->
```python
from __future__ import annotations

import time
from typing import Any

import httpx
```
<!-- fmt: on -->

Imports. `time` measures duration. `httpx` is the HTTP library. `Any` is the type that turns checking off for JSON-shaped data.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

Names this module needs from the inner layers: the `Clock` protocol, the request/response/error classes (`python.md`), the real clock and the retry helper.

<!-- fmt: off -->
```python
def raise_for_status(response: httpx.Response) -> None:
    """Map an HTTP status to the retryable or permanent error the application understands."""
    status = response.status_code
    if status < 400:
        return
    detail = response.text[:200]
    if status == 429 or status >= 500:
        raise RetryableModelError(f"provider returned {status}: {detail}")
    raise PermanentModelError(f"provider returned {status}: {detail}")
```
<!-- fmt: on -->

Translates an **HTTP status code** into one of the two error classes. Status 200-299 means success, 4xx means the request was wrong, 5xx means the server failed, and 429 means *too many requests, slow down*. Codes below 400 return silently. For the others the first 200 characters of the body are kept as `detail`. 429 and 5xx are worth trying again (`RetryableModelError`); every other 4xx is permanent.

<!-- fmt: off -->
```python
class OpenAICompatibleChatModel:
    """Chat completions over HTTP with a timeout, retries and backoff."""
```
<!-- fmt: on -->

The adapter class.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

Stores the settings. `base_url.rstrip("/")` removes a trailing slash so URLs are joined cleanly. If there is an API key the **Authorization header** `Bearer <key>` is prepared (an HTTP header is a name and a value sent with the request; `Bearer` means the holder of this token is allowed). `httpx.Client()` is a reusable connection object; tests pass a fake one through `client=`. The `*` makes the rest keyword-only.

<!-- fmt: off -->
```python
    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Send the request, retrying timeouts, 429 and 5xx."""
        return retry_call(lambda: self._once(request, timeout_s), attempts=self._attempts, clock=self._clock)
```
<!-- fmt: on -->

The public method: run `_once` through `retry_call`, which retries on `RetryableModelError` with backoff (`python.md`). `lambda: self._once(...)` is a tiny anonymous function that takes no arguments.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

Builds the JSON **body** of the request: the model, the messages as `{role, content}` dictionaries, the decoding settings, and `"stream": False` (ask for the whole reply at once). A seed is added only if given.

<!-- fmt: off -->
```python
        started = time.perf_counter()
        try:
            response = self._client.post(
                f"{self._base_url}/chat/completions", json=body, headers=self._headers, timeout=timeout_s
            )
        except (httpx.TimeoutException, httpx.TransportError) as error:
            raise RetryableModelError(f"transport failure: {type(error).__name__}") from error
```
<!-- fmt: on -->

Takes the start time, then sends a **POST** request (a request that carries a body) to `<base>/chat/completions` with the JSON body, the headers and a **timeout**, the longest time to wait. If the network fails or times out, `httpx` raises `TimeoutException` or `TransportError`; both become a retryable error with `from error` keeping the cause.

<!-- fmt: off -->
```python
        raise_for_status(response)
        elapsed = time.perf_counter() - started
```
<!-- fmt: on -->

Maps the status code; then the elapsed time is measured.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

Unpacks the reply. `response.json()` parses the body. OpenAI-style replies contain a list `choices`; the first one has `message.content` (the text) and `finish_reason`. `usage` holds `prompt_tokens` and `completion_tokens`, the counts the server reports. `or ""` and `or {}` guard against `null`. Any missing key or wrong type raises one of the listed errors, which become a **permanent** error saying the reply had an unexpected shape.

## Try it yourself

1. `.venv/bin/python -c "import httpx; print(httpx.__version__)"` prints `0.28.1`.
2. `.venv/bin/python -c "import httpx; r = httpx.Response(429, text='slow down'); print(r.status_code, r.text)"` prints `429 slow down` without any network.
3. `.venv/bin/python -c "import httpx, json; t = httpx.MockTransport(lambda req: httpx.Response(200, json={'ok': True})); c = httpx.Client(transport=t); print(c.post('http://x/y', json={'a':1}).json())"` prints `{'ok': True}`: a fake server inside the process, the same trick the tests use.
4. `curl -s -o /dev/null -w '%{http_code}\n' http://localhost:11434/` prints `200` when ollama is running (and `000` when nothing listens).

## Mistakes people make

- **No timeout.** One hung server would hang the whole run.
- **Treating 4xx and 5xx alike.** A 400 will fail again; a 503 may succeed in a second.
- **Retrying everything**, including requests that already had an effect.
- **Putting the API key in the URL or in logs.** It goes in a header; the logger never prints headers.
- **Creating a new `Client` per request**, which opens a new connection each time.

## Check yourself

1. **What does a 429 status mean?**  
   Too many requests: the client should slow down and try again later.
2. **Why are tests given a fake `httpx.Client`?**  
   So the adapter's logic runs without a network or a model.
3. **What is a timeout for?**  
   To stop waiting for a server that does not answer.
4. **What does `response.json()` do?**  
   Parses the response body as JSON and returns Python objects.
5. **Where does the API key go?**  
   In an HTTP header (`Authorization: Bearer ...`), never in the URL.

## Further reading

httpx: https://www.python-httpx.org/ (quickstart, timeouts, MockTransport). HTTP semantics: https://httpwg.org/specs/rfc9110.html . Pinned version: 0.28.1.
