import json

from clinical_extraction.llms import (
    ChatMessage,
    LLMProviderConfig,
    MockChatAdapter,
    OpenAICompatibleChatAdapter,
    build_chat_adapter,
    build_dspy_lm,
)


def test_build_dspy_lm_resolves_openai_provider_config():
    import dspy
    config = LLMProviderConfig(provider="openai", model="gpt-4.1-mini", api_key="test-key")
    lm = build_dspy_lm(config)
    assert isinstance(lm, dspy.LM)
    assert "gpt-4.1-mini" in lm.model


def test_build_dspy_lm_resolves_ollama_provider_config():
    import dspy
    config = LLMProviderConfig(
        provider="ollama",
        model="qwen3.6:35b",
        max_tokens=256,
        num_retries=0,
    )
    lm = build_dspy_lm(config)
    assert isinstance(lm, dspy.LM)
    assert "qwen3.6:35b" in lm.model
    assert lm.model.startswith("ollama_chat/")
    assert lm.kwargs["extra_body"] == {"think": False}


def test_build_dspy_lm_resolves_anthropic_provider_config():
    import dspy
    config = LLMProviderConfig(
        provider="anthropic",
        model="claude-sonnet-4-6",
        api_key="test-key",
        max_tokens=4096,
    )

    lm = build_dspy_lm(config)

    assert isinstance(lm, dspy.LM)
    assert lm.model == "anthropic/claude-sonnet-4-6"
    assert lm.kwargs["max_tokens"] == 4096


def test_build_dspy_lm_passes_ollama_extra_body_with_thinking_disabled():
    config = LLMProviderConfig(
        provider="ollama",
        model="qwen3.5:9b",
        max_tokens=81920,
        extra_body={"options": {"num_ctx": 262144}},
    )

    lm = build_dspy_lm(config)

    assert lm.kwargs["max_tokens"] == 81920
    assert lm.kwargs["extra_body"] == {
        "think": False,
        "options": {"num_ctx": 262144},
    }


def test_build_chat_adapter_resolves_supported_provider_configs():
    mock = build_chat_adapter(
        LLMProviderConfig(
            provider="mock",
            model="fixture",
            mock_responses=[{"seizure_frequency_number": "unknown"}],
        )
    )
    ollama = build_chat_adapter(
        LLMProviderConfig(provider="ollama", model="qwen3.6:35b")
    )
    openai = build_chat_adapter(
        LLMProviderConfig(
            provider="openai",
            model="gpt-4.1-mini",
            api_key="test-key",
        )
    )
    gemini = build_chat_adapter(
        LLMProviderConfig(
            provider="gemini",
            model="gemini-3-flash-preview",
            api_key="test-key",
        )
    )
    anthropic = build_chat_adapter(
        LLMProviderConfig(
            provider="anthropic",
            model="claude-sonnet-4-6",
            api_key="test-key",
        )
    )

    assert isinstance(mock, MockChatAdapter)
    assert isinstance(ollama, OpenAICompatibleChatAdapter)
    assert ollama.base_url == "http://localhost:11434/v1"
    assert openai.base_url == "https://api.openai.com/v1"
    assert gemini.base_url == "https://generativelanguage.googleapis.com/v1beta/openai"
    assert anthropic.base_url == "https://api.anthropic.com/v1"


def test_openai_compatible_adapter_posts_chat_completion_payload_offline():
    captured = {}

    def transport(url, headers, body, timeout_seconds):
        captured["url"] = url
        captured["headers"] = headers
        captured["body"] = json.loads(body)
        captured["timeout_seconds"] = timeout_seconds
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "seizure_frequency_number": "1 per 1 month",
                                "evidence_text": "one seizure per month",
                                "confidence": 0.7,
                            }
                        )
                    }
                }
            ]
        }

    adapter = OpenAICompatibleChatAdapter(
        provider="openai",
        model="gpt-4.1-mini",
        base_url="https://api.openai.com/v1",
        api_key="test-key",
        transport=transport,
    )

    content = adapter.complete_json(
        [
            ChatMessage(role="system", content="Return JSON."),
            ChatMessage(role="user", content="note text"),
        ],
        response_schema={"type": "object"},
    )

    assert json.loads(content)["seizure_frequency_number"] == "1 per 1 month"
    assert captured["url"] == "https://api.openai.com/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["body"]["model"] == "gpt-4.1-mini"
    assert captured["body"]["messages"] == [
        {"role": "system", "content": "Return JSON."},
        {"role": "user", "content": "note text"},
    ]
    assert captured["body"]["temperature"] == 0.0
    assert captured["body"]["response_format"]["type"] == "json_schema"


def test_openai_compatible_adapter_includes_max_tokens_when_configured():
    captured = {}

    def transport(url, headers, body, timeout_seconds):
        captured["body"] = json.loads(body)
        return {"choices": [{"message": {"content": "{}"}}]}

    adapter = OpenAICompatibleChatAdapter(
        provider="ollama",
        model="qwen3.5:9b",
        base_url="http://localhost:11434/v1",
        max_tokens=128,
        transport=transport,
    )

    adapter.complete_json([ChatMessage(role="user", content="note text")])

    assert captured["body"]["max_tokens"] == 128


def test_openai_compatible_adapter_omits_temperature_when_config_uses_default():
    captured = {}

    def transport(url, headers, body, timeout_seconds):
        captured["body"] = json.loads(body)
        return {"choices": [{"message": {"content": "{}"}}]}

    adapter = OpenAICompatibleChatAdapter(
        provider="openai",
        model="gpt-5.5",
        base_url="https://api.openai.com/v1",
        api_key="test-key",
        temperature=None,
        transport=transport,
    )

    adapter.complete_json([ChatMessage(role="user", content="note text")])

    assert "temperature" not in captured["body"]


def test_openai_compatible_adapter_merges_provider_extra_body():
    captured = {}

    def transport(url, headers, body, timeout_seconds):
        captured["body"] = json.loads(body)
        return {"choices": [{"message": {"content": "{}"}}]}

    adapter = OpenAICompatibleChatAdapter(
        provider="anthropic",
        model="claude-sonnet-4-6",
        base_url="https://api.anthropic.com/v1",
        api_key="test-key",
        extra_body={"thinking": {"type": "disabled"}},
        transport=transport,
    )

    adapter.complete_json([ChatMessage(role="user", content="note text")])

    assert captured["body"]["thinking"] == {"type": "disabled"}
