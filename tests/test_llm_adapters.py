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
    config = LLMProviderConfig(provider="ollama", model="qwen3.6:35b")
    lm = build_dspy_lm(config)
    assert isinstance(lm, dspy.LM)
    assert "qwen3.6:35b" in lm.model


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
            model="gemini-3-flash",
            api_key="test-key",
        )
    )

    assert isinstance(mock, MockChatAdapter)
    assert isinstance(ollama, OpenAICompatibleChatAdapter)
    assert ollama.base_url == "http://localhost:11434/v1"
    assert openai.base_url == "https://api.openai.com/v1"
    assert gemini.base_url == "https://generativelanguage.googleapis.com/v1beta/openai"


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
