import json

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.llms import (
    ChatMessage,
    LLMProviderConfig,
    MockChatAdapter,
    OpenAICompatibleChatAdapter,
    build_chat_adapter,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    GanFrequencyS0Program,
    build_gan_frequency_s0_extractor,
)


def test_mock_adapter_drives_gan_s0_program_without_changing_program_contract():
    record = next(
        record
        for record in load_gan_records()
        if record.gold_evidence and record.gold_evidence in record.note_text
    )
    adapter = MockChatAdapter(
        provider="mock",
        model="fixture-json",
        responses=[
            {
                "seizure_frequency_number": record.gold_label,
                "evidence_text": record.gold_evidence,
                "confidence": 0.82,
            }
        ],
    )
    program = GanFrequencyS0Program(
        extractor=build_gan_frequency_s0_extractor(adapter),
        model_provider=adapter.provider,
        model_name=adapter.model,
    )

    prediction_set = program.predict_records([record])

    assert prediction_set.metadata["model_provider"] == "mock"
    assert prediction_set.metadata["model_name"] == "fixture-json"
    assert adapter.calls[0][0].role == "system"
    assert "Return strict JSON" in adapter.calls[0][0].content
    value = prediction_set.predictions[0].values[0]
    assert value.raw_value == record.gold_label
    assert value.evidence[0].text == record.gold_evidence
    assert value.confidence == 0.82


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
    assert captured["body"]["response_format"]["type"] == "json_schema"
