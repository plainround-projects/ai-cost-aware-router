import json
from pathlib import Path

import httpx
import pytest

from cost_router.domain.llm import (
    ChatRequest,
    ChatResponse,
    FixtureMissError,
    Message,
    PermanentModelError,
    RetryableModelError,
    Usage,
)
from cost_router.infrastructure.clock import ManualClock
from cost_router.infrastructure.env import ConfigError
from cost_router.infrastructure.llm.anthropic import AnthropicChatModel
from cost_router.infrastructure.llm.factory import build_chat_model
from cost_router.infrastructure.llm.openai_compat import OpenAICompatibleChatModel
from cost_router.infrastructure.llm.recorded import (
    RecordedChatModel,
    RecordingChatModel,
    request_from_json,
    request_to_json,
)
from cost_router.infrastructure.llm.retry import retry_call

REQUEST = ChatRequest("m", (Message("system", "be brief"), Message("user", "hello")), temperature=0.2, seed=3)


def client_with(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def openai_ok(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    assert body["messages"][0]["role"] == "system" and body["seed"] == 3
    return httpx.Response(
        200,
        json={
            "model": "m-served",
            "choices": [{"message": {"content": "hi there"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 3},
        },
    )


def test_openai_compatible_adapter_maps_request_and_response():
    model = OpenAICompatibleChatModel("http://x/v1/", "k", client=client_with(openai_ok))
    response = model.complete(REQUEST)
    assert response.text == "hi there" and response.usage == Usage(7, 3) and response.model == "m-served"


def test_openai_adapter_sends_the_bearer_key_only_when_given():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        return openai_ok(request)

    OpenAICompatibleChatModel("http://x/v1", "secret", client=client_with(handler)).complete(REQUEST)
    assert seen["auth"] == "Bearer secret"
    OpenAICompatibleChatModel("http://x/v1", client=client_with(handler)).complete(REQUEST)
    assert seen["auth"] is None


def test_openai_adapter_retries_a_503_then_succeeds_with_backoff():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(503, text="busy") if len(calls) < 3 else openai_ok(request)

    clock = ManualClock()
    model = OpenAICompatibleChatModel("http://x/v1", client=client_with(handler), attempts=3, clock=clock)
    assert model.complete(REQUEST).text == "hi there"
    assert len(calls) == 3 and clock.monotonic() > 0


def test_openai_adapter_does_not_retry_a_400():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(400, text="bad")

    model = OpenAICompatibleChatModel("http://x/v1", client=client_with(handler), clock=ManualClock())
    with pytest.raises(PermanentModelError):
        model.complete(REQUEST)
    assert len(calls) == 1


def test_openai_adapter_turns_a_timeout_into_a_retryable_error_after_the_last_attempt():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("slow")

    model = OpenAICompatibleChatModel("http://x/v1", client=client_with(handler), attempts=2, clock=ManualClock())
    with pytest.raises(RetryableModelError):
        model.complete(REQUEST)


def test_openai_adapter_rejects_a_reply_of_the_wrong_shape():
    model = OpenAICompatibleChatModel("http://x/v1", client=client_with(lambda r: httpx.Response(200, json={})))
    with pytest.raises(PermanentModelError):
        model.complete(REQUEST)


def test_anthropic_adapter_lifts_the_system_message_and_reads_usage():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["headers"] = request.headers
        seen["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "model": "claude-x",
                "content": [{"type": "text", "text": "hello"}],
                "usage": {"input_tokens": 11, "output_tokens": 2},
                "stop_reason": "end_turn",
            },
        )

    response = AnthropicChatModel("key", client=client_with(handler)).complete(REQUEST)
    assert seen["body"]["system"] == "be brief"
    assert [m["role"] for m in seen["body"]["messages"]] == ["user"]
    assert seen["headers"]["x-api-key"] == "key" and "anthropic-version" in seen["headers"]
    assert response.text == "hello" and response.usage == Usage(11, 2)


def test_anthropic_adapter_needs_a_key():
    with pytest.raises(PermanentModelError):
        AnthropicChatModel("")


def test_request_survives_a_json_round_trip():
    assert request_from_json(request_to_json(REQUEST)) == REQUEST


def test_recording_then_replaying_returns_the_same_answer(tmp_path: Path):
    class Fixed:
        def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
            return ChatResponse("recorded text", Usage(5, 2), "m", latency_s=0.25)

    path = tmp_path / "one.jsonl"
    recording = RecordingChatModel(Fixed(), path)
    recording.complete(REQUEST)
    recording.complete(REQUEST)
    assert len(path.read_text().splitlines()) == 1
    replay = RecordedChatModel(path)
    assert len(replay) == 1
    assert replay.complete(REQUEST).text == "recorded text" and replay.complete(REQUEST).usage == Usage(5, 2)


def test_replay_of_an_unknown_request_is_a_named_error(tmp_path: Path):
    (tmp_path / "empty.jsonl").write_text("")
    with pytest.raises(FixtureMissError):
        RecordedChatModel(tmp_path).complete(REQUEST)


def test_retry_call_gives_up_after_the_last_attempt_and_waits_between_attempts():
    clock = ManualClock()
    attempts = []

    def always_fails():
        attempts.append(1)
        raise RetryableModelError("nope")

    with pytest.raises(RetryableModelError):
        retry_call(always_fails, attempts=3, clock=clock)
    assert len(attempts) == 3 and clock.monotonic() > 0
    with pytest.raises(ValueError):
        retry_call(always_fails, attempts=0, clock=clock)


def test_factory_defaults_to_the_recorded_adapter_and_rejects_unknown_providers(tmp_path: Path):
    assert isinstance(build_chat_model({}, tmp_path), RecordedChatModel)
    with pytest.raises(ConfigError):
        build_chat_model({"LLM_PROVIDER": "carrier-pigeon"}, tmp_path)
    with pytest.raises(ConfigError):
        build_chat_model({"LLM_PROVIDER": "openai"}, tmp_path)
    assert isinstance(build_chat_model({"LLM_PROVIDER": "local"}, tmp_path), OpenAICompatibleChatModel)
    recording = build_chat_model({"LLM_PROVIDER": "local", "LLM_RECORD_TO": str(tmp_path / "r.jsonl")}, tmp_path)
    assert isinstance(recording, RecordingChatModel)
