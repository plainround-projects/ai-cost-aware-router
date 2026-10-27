"""Choose a chat-model adapter from the environment: recorded (the default, offline), a local OpenAI-compatible
server, a hosted OpenAI-compatible provider, or Anthropic."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from cost_router.application.ports import ChatModel
from cost_router.infrastructure.env import ConfigError, read_int, read_str
from cost_router.infrastructure.llm.anthropic import AnthropicChatModel
from cost_router.infrastructure.llm.openai_compat import OpenAICompatibleChatModel
from cost_router.infrastructure.llm.recorded import RecordedChatModel, RecordingChatModel

PROVIDERS = ("recorded", "local", "openai", "anthropic")
LOCAL_BASE_URL = "http://localhost:11434/v1"


def build_chat_model(env: Mapping[str, str], fixtures: Path) -> ChatModel:
    """Build the adapter named by LLM_PROVIDER.

    - recorded (default): replay `fixtures`; needs no network and no key.
    - local: an OpenAI-compatible server on this machine (ollama, llama.cpp); LLM_BASE_URL overrides the address.
    - openai: a hosted OpenAI-compatible provider; LLM_BASE_URL and OPENAI_API_KEY come from the environment.
    - anthropic: the Messages API; ANTHROPIC_API_KEY comes from the environment.

    When LLM_RECORD_TO is set, every real exchange is also appended to that fixture file.
    """
    provider = read_str(env, "LLM_PROVIDER", "recorded")
    if provider not in PROVIDERS:
        raise ConfigError(f"LLM_PROVIDER must be one of {', '.join(PROVIDERS)}, got {provider!r}")
    attempts = read_int(env, "LLM_ATTEMPTS", 3, minimum=1)
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
    record_to = env.get("LLM_RECORD_TO", "").strip()
    return RecordingChatModel(model, Path(record_to)) if record_to else model
