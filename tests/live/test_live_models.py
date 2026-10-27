"""Opt-in tests against real models. Skipped unless RUN_LIVE=1 (`make test-live`) and, for a hosted model, its key
is in the environment. They are never part of `make test` or CI."""

import os

import pytest

from cost_router.domain.llm import ChatRequest, Message
from cost_router.infrastructure.llm.anthropic import AnthropicChatModel
from cost_router.infrastructure.llm.openai_compat import OpenAICompatibleChatModel

pytestmark = pytest.mark.live

requires_live = pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="set RUN_LIVE=1 (make test-live)")


@requires_live
def test_a_local_openai_compatible_server_answers():
    base = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
    model = os.environ.get("LIVE_LOCAL_MODEL", "qwen2.5:0.5b")
    reply = OpenAICompatibleChatModel(base).complete(
        ChatRequest(model, (Message("user", "Reply with the single word: ready"),), max_tokens=16), timeout_s=120
    )
    assert reply.text.strip() and reply.usage.output_tokens > 0


@requires_live
@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY is not set")
def test_claude_answers():
    model = os.environ.get("LIVE_CLAUDE_MODEL", "claude-haiku-5-5")
    reply = AnthropicChatModel(os.environ["ANTHROPIC_API_KEY"]).complete(
        ChatRequest(model, (Message("user", "Reply with the single word: ready"),), max_tokens=16)
    )
    assert reply.text.strip() and reply.usage.input_tokens > 0
