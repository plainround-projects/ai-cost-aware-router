"""The recorded adapter replays real responses from JSONL fixtures; the recording adapter writes them.

A fixture line holds the request's hash, the request itself (so a human can read it) and the response. The
Java port reads the same files with the same hash.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from cost_router.application.ports import ChatModel
from cost_router.domain.llm import ChatRequest, ChatResponse, FixtureMissError, Message, Usage


def request_to_json(request: ChatRequest) -> dict[str, Any]:
    """The request as plain JSON data."""
    return {
        "model": request.model,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "seed": request.seed,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
    }


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


def request_from_json(data: dict[str, Any]) -> ChatRequest:
    """Rebuild a request from `request_to_json` output."""
    return ChatRequest(
        model=data["model"],
        messages=tuple(Message(m["role"], m["content"]) for m in data["messages"]),
        temperature=float(data["temperature"]),
        max_tokens=int(data["max_tokens"]),
        seed=data.get("seed"),
    )


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


def response_from_json(data: dict[str, Any]) -> ChatResponse:
    """Rebuild a response from `response_to_json` output."""
    return ChatResponse(
        text=data["text"],
        usage=Usage(int(data["input_tokens"]), int(data["output_tokens"])),
        model=data["model"],
        finish_reason=data.get("finish_reason", "stop"),
        latency_s=float(data.get("latency_s", 0.0)),
    )


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
