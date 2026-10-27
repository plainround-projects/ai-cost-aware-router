# Chat-model APIs (OpenAI-compatible and Anthropic Messages) and record/replay

## What it is

A **chat model** answers a list of messages. Each message has a **role** (`system` for standing instructions, `user` for the question, `assistant` for earlier answers) and **content** (text). A program sends the messages, with settings such as the **model** name, the **temperature** (0 = the most predictable answer) and **max_tokens** (the longest reply), over HTTP and gets back the reply text, the number of **tokens** read and written (a token is a piece of a word; about four characters of English) and a **finish reason** (`stop` = finished, `length` = hit max_tokens).

## Why this repository uses it

The experiments need many model answers. This repository separates *what it asks* (the request type, in the domain) from *who answers* (an adapter in the infrastructure layer). That lets the same experiment run against a recorded file (default, offline, free), a local server (`ollama.md`), a hosted provider, or Anthropic, and lets the tests prove the experiment's logic without a model.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/cost_router/domain/llm.py` | The request and response types. |
| `src/cost_router/application/ports.py` | The `ChatModel` protocol. |
| `src/cost_router/infrastructure/llm/openai_compat.py` | OpenAI-compatible adapter. |
| `src/cost_router/infrastructure/llm/anthropic.py` | Anthropic adapter. |
| `src/cost_router/infrastructure/llm/recorded.py` | Replaying and recording adapters. |
| `src/cost_router/infrastructure/llm/factory.py` | Chooses the adapter from `LLM_PROVIDER`. |
| `java/src/main/java/dev/plainround/router/infrastructure/SpringAiChatModel.java` | The Java adapter built on Spring AI (`spring-ai.md`). |
| `tests/fixtures/recorded.jsonl` | The recordings. |
| `.env.example` | `LLM_PROVIDER` and friends (`dotenv.md`). |


## How it works underneath

**Two wire formats.** The *OpenAI chat-completions* format posts `{"model": ..., "messages": [{"role": "user", "content": "..."}], "temperature": ..., "max_tokens": ...}` to `/chat/completions` and answers with `{"choices": [{"message": {"content": "..."}, "finish_reason": "stop"}], "usage": {"prompt_tokens": n, "completion_tokens": m}}`. Many servers (ollama, llama.cpp, vLLM, hosted providers) copy it, which is why one adapter serves them all. Anthropic's *Messages* format posts to `/v1/messages`, puts the system prompt in a separate `system` field, requires `max_tokens`, and answers with `{"content": [{"type": "text", "text": "..."}], "usage": {"input_tokens": n, "output_tokens": m}, "stop_reason": "..."}`.

**Ports and adapters.** The application depends on a *port*, the `ChatModel` protocol with one method `complete(request) -> response`. An *adapter* implements it. The application never learns which one it holds. Composition happens in one place (`interfaces/wiring.py`).

**Determinism and record/replay.** With temperature 0 and a fixed seed, the same request gives nearly the same answer, but not byte-for-byte across machines. To make results reproducible, real answers are *recorded* once under the SHA-256 of the full request; a rerun *replays* them. A request that was never recorded is an error, so a change in a prompt cannot silently reuse an old answer.

**Retries.** Rate limits (429) and server errors (5xx) are temporary, so the adapters retry with exponential backoff and jitter (`python.md`); a bad key or a malformed request (other 4xx) fails at once.

## Walkthrough of this repository's use

### Choosing the adapter

`src/cost_router/infrastructure/llm/factory.py`

<!-- fmt: off -->
```python
"""Choose a chat-model adapter from the environment: recorded (the default, offline), a local OpenAI-compatible
server, a hosted OpenAI-compatible provider, or Anthropic."""
```
<!-- fmt: on -->

Module docstring.

<!-- fmt: off -->
```python
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from cost_router.application.ports import ChatModel
from cost_router.infrastructure.env import ConfigError, read_int, read_str
from cost_router.infrastructure.llm.anthropic import AnthropicChatModel
from cost_router.infrastructure.llm.openai_compat import OpenAICompatibleChatModel
from cost_router.infrastructure.llm.recorded import RecordedChatModel, RecordingChatModel
```
<!-- fmt: on -->

Imports: the port, the settings readers (`python.md`), and the four adapters.

<!-- fmt: off -->
```python
PROVIDERS = ("recorded", "local", "openai", "anthropic")
LOCAL_BASE_URL = "http://localhost:11434/v1"
```
<!-- fmt: on -->

The allowed provider names and the default address of a local server: **11434 is ollama's port**, `/v1` its OpenAI-compatible path.

<!-- fmt: off -->
```python
def build_chat_model(env: Mapping[str, str], fixtures: Path) -> ChatModel:
    """Build the adapter named by LLM_PROVIDER.

    - recorded (default): replay `fixtures`; needs no network and no key.
    - local: an OpenAI-compatible server on this machine (ollama, llama.cpp); LLM_BASE_URL overrides the address.
    - openai: a hosted OpenAI-compatible provider; LLM_BASE_URL and OPENAI_API_KEY come from the environment.
    - anthropic: the Messages API; ANTHROPIC_API_KEY comes from the environment.

    When LLM_RECORD_TO is set, every real exchange is also appended to that fixture file.
    """
```
<!-- fmt: on -->

The docstring lists the four choices. `recorded` (the default) needs no network and no key. `local` is a server on this computer. `openai` is a hosted provider that speaks the same protocol, with `LLM_BASE_URL` and `OPENAI_API_KEY` from the environment. `anthropic` is the Messages API. If `LLM_RECORD_TO` is set, every real exchange is also appended to that file.

<!-- fmt: off -->
```python
    provider = read_str(env, "LLM_PROVIDER", "recorded")
    if provider not in PROVIDERS:
        raise ConfigError(f"LLM_PROVIDER must be one of {', '.join(PROVIDERS)}, got {provider!r}")
    attempts = read_int(env, "LLM_ATTEMPTS", 3, minimum=1)
```
<!-- fmt: on -->

Reads the provider (default `recorded`) and rejects an unknown name with a `ConfigError` that lists the valid ones. `LLM_ATTEMPTS` must be at least 1.

<!-- fmt: off -->
```python
    model: ChatModel
    if provider == "recorded":
        return RecordedChatModel(fixtures)
    if provider == "local":
        model = OpenAICompatibleChatModel(read_str(env, "LLM_BASE_URL", LOCAL_BASE_URL), attempts=attempts)
    elif provider == "openai":
        model = OpenAICompatibleChatModel(
            read_str(env, "LLM_BASE_URL"), read_str(env, "OPENAI_API_KEY"), attempts=attempts
        )
    else:
        model = AnthropicChatModel(read_str(env, "ANTHROPIC_API_KEY"), attempts=attempts)
```
<!-- fmt: on -->

Declares the variable's type. Recorded: build and return the replaying adapter at once. Local: an OpenAI-compatible adapter with the default or given address. `openai`: base address and key are required (`read_str` without a default raises if missing). Anything else is Anthropic.

<!-- fmt: off -->
```python
    record_to = env.get("LLM_RECORD_TO", "").strip()
    return RecordingChatModel(model, Path(record_to)) if record_to else model
```
<!-- fmt: on -->

When a recording file is configured the chosen adapter is wrapped in the recording adapter; otherwise it is used as it is.

### Replaying and recording

`src/cost_router/infrastructure/llm/recorded.py`

<!-- fmt: off -->
```python
"""The recorded adapter replays real responses from JSONL fixtures; the recording adapter writes them.

A fixture line holds the request's hash, the request itself (so a human can read it) and the response. The
Java port reads the same files with the same hash.
"""
```
<!-- fmt: on -->

Module docstring: **record and replay**. A real run appends every exchange to a file; later runs read that file instead of calling a model. A fixture line holds the request's hash, the request (for humans) and the response.

<!-- fmt: off -->
```python
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from cost_router.application.ports import ChatModel
from cost_router.domain.llm import ChatRequest, ChatResponse, FixtureMissError, Message, Usage
```
<!-- fmt: on -->

Imports: `json`, `threading` (for the lock), `Path`, and the project's types.

<!-- fmt: off -->
```python
def request_to_json(request: ChatRequest) -> dict[str, Any]:
    """The request as plain JSON data."""
    return {
        "model": request.model,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "seed": request.seed,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
    }
```
<!-- fmt: on -->

Turns a request into plain JSON-able data.

<!-- fmt: off -->
```python
def summarize_request(request: ChatRequest, limit: int = 160) -> dict[str, Any]:
    """The request for a fixture line: the decoding settings and each message cut to `limit` characters.

    The fixture key already identifies the full request; the summary only lets a human see what was asked.
    """
    data = request_to_json(request)
    data["messages"] = [
        {
            "role": m.role,
            "content": m.content if len(m.content) <= limit else f"{m.content[:limit]}...[{len(m.content)} chars]",
        }
        for m in request.messages
    ]
    return data
```
<!-- fmt: on -->

A shortened copy for the fixture file: each message is cut to `limit` characters with the full length noted. The key already identifies the full request; the summary only lets a person see what was asked.

<!-- fmt: off -->
```python
def request_from_json(data: dict[str, Any]) -> ChatRequest:
    """Rebuild a request from `request_to_json` output."""
    return ChatRequest(
        model=data["model"],
        messages=tuple(Message(m["role"], m["content"]) for m in data["messages"]),
        temperature=float(data["temperature"]),
        max_tokens=int(data["max_tokens"]),
        seed=data.get("seed"),
    )
```
<!-- fmt: on -->

Rebuilds a request from the JSON form.

<!-- fmt: off -->
```python
def response_to_json(response: ChatResponse) -> dict[str, Any]:
    """The response as plain JSON data."""
    return {
        "text": response.text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "model": response.model,
        "finish_reason": response.finish_reason,
        "latency_s": round(response.latency_s, 4),
    }
```
<!-- fmt: on -->

The response as JSON data; the latency is rounded to four decimals.

<!-- fmt: off -->
```python
def response_from_json(data: dict[str, Any]) -> ChatResponse:
    """Rebuild a response from `response_to_json` output."""
    return ChatResponse(
        text=data["text"],
        usage=Usage(int(data["input_tokens"]), int(data["output_tokens"])),
        model=data["model"],
        finish_reason=data.get("finish_reason", "stop"),
        latency_s=float(data.get("latency_s", 0.0)),
    )
```
<!-- fmt: on -->

Rebuilds a response.

<!-- fmt: off -->
```python
def load_fixtures(path: Path) -> dict[str, ChatResponse]:
    """Read every `*.jsonl` file under `path` (or the one file) into a key -> response map."""
    files = sorted(path.glob("*.jsonl")) if path.is_dir() else [path]
    found: dict[str, ChatResponse] = {}
    for file in files:
        with file.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    found[row["key"]] = response_from_json(row["response"])
    return found
```
<!-- fmt: on -->

Reads every `*.jsonl` file in a folder (or one file) into a dictionary from key to response. `sorted(path.glob("*.jsonl"))` lists matching files in a fixed order. Blank lines are skipped.

<!-- fmt: off -->
```python
class RecordedChatModel:
    """Answers from fixtures only; an unknown request is a FixtureMissError, never a silent guess."""

    def __init__(self, fixtures: Path) -> None:
        self._responses = load_fixtures(fixtures)

    def __len__(self) -> int:
        return len(self._responses)

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Return the recorded response for this exact request."""
        try:
            return self._responses[request.fixture_key()]
        except KeyError:
            raise FixtureMissError(
                f"no recorded response for model={request.model} key={request.fixture_key()[:12]} "
                f"({len(request.messages)} messages); run `make record` with a local model to add it"
            ) from None
```
<!-- fmt: on -->

The replaying adapter. It loads the file once; `complete` looks up `request.fixture_key()` (`sha-256.md`). An unknown request raises `FixtureMissError` with the first 12 characters of the key and the instruction to run `make record` - **it never invents an answer**. `from None` hides the internal `KeyError`.

<!-- fmt: off -->
```python
class RecordingChatModel:
    """Wraps a real model and appends every new exchange to a fixture file, so a run can be replayed offline.

    A request already in the file is answered from the file, so a recording run can be interrupted and resumed.
    """

    def __init__(self, inner: ChatModel, path: Path) -> None:
        self._inner = inner
        self._path = path
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._seen = load_fixtures(path) if path.exists() else {}
```
<!-- fmt: on -->

The recording adapter wraps a real model (the *inner* one). On creation it makes sure the folder exists and loads what is already recorded, so an interrupted recording can be resumed.

<!-- fmt: off -->
```python
    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Answer from the file when the request is known, else call the inner model and store the exchange."""
        key = request.fixture_key()
        with self._lock:
            known = self._seen.get(key)
        if known is not None:
            return known
        response = self._inner.complete(request, timeout_s)
        with self._lock:
            if key not in self._seen:
                row = {"key": key, "request": summarize_request(request), "response": response_to_json(response)}
                with self._path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                self._seen[key] = response
        return response
```
<!-- fmt: on -->

If the request is already known, return it. Otherwise call the inner model, then take the lock and append one JSON line (`"a"` means append) containing the key, the summarised request and the response, and remember it. The lock is explained in `concurrency.md`.

### Anthropic's Messages API

`src/cost_router/infrastructure/llm/anthropic.py`

<!-- fmt: off -->
```python
"""An adapter for the Anthropic Messages API, over plain HTTP. The key comes from the environment; this adapter
is exercised only by the opt-in live test (`make test-live`)."""
```
<!-- fmt: on -->

Module docstring: the adapter talks to Anthropic's **Messages API** with plain HTTP (`httpx.md`), and is only exercised by the opt-in live test, because it needs a key.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

Imports, the same set as for the other adapter; `raise_for_status` is reused from there.

<!-- fmt: off -->
```python
API_VERSION = "2023-06-01"
```
<!-- fmt: on -->

The API version header value Anthropic asks every client to send.

<!-- fmt: off -->
```python
class AnthropicChatModel:
    """Messages API calls with a timeout, retries and backoff."""
```
<!-- fmt: on -->

The adapter class.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

A missing key is a permanent error at construction time. The headers are `x-api-key` (the secret), `anthropic-version` and the content type. Everything else is as in the OpenAI-compatible adapter: base address, reusable client, attempts, clock.

<!-- fmt: off -->
```python
    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        """Send the request, retrying timeouts, 429 and 5xx."""
        return retry_call(lambda: self._once(request, timeout_s), attempts=self._attempts, clock=self._clock)
```
<!-- fmt: on -->

Retry wrapper, as before.

<!-- fmt: off -->
```python
    def _once(self, request: ChatRequest, timeout_s: float) -> ChatResponse:
        body: dict[str, Any] = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages if m.role != "system"],
        }
        system = request.system_text()
        if system:
            body["system"] = system
```
<!-- fmt: on -->

Builds the body. In the Messages API the **system** prompt is a separate field, not a message, so system messages are filtered out of `messages` and joined into `system` (`request.system_text()`). `max_tokens` is required by this API. The request goes to `<base>/v1/messages`.

<!-- fmt: off -->
```python
        started = time.perf_counter()
        try:
            response = self._client.post(
                f"{self._base_url}/v1/messages", json=body, headers=self._headers, timeout=timeout_s
            )
        except (httpx.TimeoutException, httpx.TransportError) as error:
            raise RetryableModelError(f"transport failure: {type(error).__name__}") from error
```
<!-- fmt: on -->

POST, timeout and error translation exactly as in `httpx.md`.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

Status mapping, timing, then parsing. The reply holds a list of content `blocks`; the text blocks are joined (`block.get("type") == "text"`). `usage` has `input_tokens` and `output_tokens`; `stop_reason` becomes the finish reason.

The OpenAI-compatible adapter is walked through in `httpx.md`.

## Try it yourself

1. `LLM_PROVIDER=recorded make run` (the default) replays the fixtures; no key and no server needed.
2. `LLM_PROVIDER=bogus .venv/bin/python -c "from cost_router.infrastructure.llm.factory import build_chat_model; import os, pathlib; build_chat_model(os.environ, pathlib.Path('tests/fixtures'))"` ends with `ConfigError: LLM_PROVIDER must be one of recorded, local, openai, anthropic, got 'bogus'`.
3. `.venv/bin/python -c "from cost_router.domain.llm import ChatRequest, Message; r = ChatRequest('m', (Message('user','hi'),)); print(r.fixture_key()[:12])"` prints the first 12 characters of the request's key (the same text in the error message of a fixture miss).
4. `curl -s http://localhost:11434/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"qwen2.5:1.5b","messages":[{"role":"user","content":"Say hi"}],"max_tokens":8}'` prints a JSON reply when ollama runs and the model is pulled.

## Mistakes people make

- **Assuming a recorded answer exists for a changed prompt.** Any change to model, text, temperature, max tokens or seed changes the key; re-record with `make record`.
- **Sending the system prompt as a message to Anthropic.** That API wants it in the `system` field.
- **Putting keys in `.env.example` or in logs.**
- **Believing temperature 0 is perfectly repeatable.** Different hardware and library versions can change a token; that is why answers are recorded.
- **Counting characters instead of tokens** when planning cost.

## Check yourself

1. **What are the three message roles?**  
   `system`, `user` and `assistant`.
2. **Why does the application depend on a port and not on an HTTP library?**  
   So that the experiment's logic can be tested and replayed without a network or a vendor.
3. **What happens when the recorded adapter gets a request it never recorded?**  
   It raises `FixtureMissError`; it never guesses.
4. **Which HTTP status codes are retried?**  
   429 and the 5xx codes, plus network timeouts and drops.
5. **Where does Anthropic's API expect the system prompt?**  
   In a separate `system` field of the request body.

## Further reading

OpenAI chat completions reference: https://platform.openai.com/docs/api-reference/chat . Anthropic Messages API: https://docs.anthropic.com/en/api/messages . ollama's OpenAI compatibility: https://github.com/ollama/ollama/blob/main/docs/openai.md
