"""Validate model comparison config files load and resolve to adapters."""
from pathlib import Path

import pytest

from clinical_extraction.llms import (
    LLMProviderConfig,
    MockChatAdapter,
    OpenAICompatibleChatAdapter,
    build_chat_adapter,
    build_dspy_lm,
)

MODEL_CONFIGS_DIR = Path("configs/models")

MODEL_CONFIG_FILES = [
    ("exect_qwen27b_ollama.json", "ollama", "qwen3.6:27b", "http://localhost:11434/v1"),
    ("exect_qwen35b_ollama.json", "ollama", "qwen3.6:35b", "http://localhost:11434/v1"),
    ("exect_qwen9b_ollama.json", "ollama", "qwen3.5:9b", "http://localhost:11434/v1"),
    ("gan_s0_claude_sonnet_4_6_anthropic.json", "anthropic", "claude-sonnet-4-6", "https://api.anthropic.com/v1"),
    ("gan_s0_gemini3_flash.json", "gemini", "gemini-3-flash-preview", "https://generativelanguage.googleapis.com/v1beta/openai"),
    ("gan_s0_gemini31_flash_lite.json", "gemini", "gemini-3.1-flash-lite", "https://generativelanguage.googleapis.com/v1beta/openai"),
    ("gan_s0_gpt4_1_mini.json", "openai", "gpt-4.1-mini", "https://api.openai.com/v1"),
    ("gan_s0_gpt4_1_mini_temp0_7.json", "openai", "gpt-4.1-mini", "https://api.openai.com/v1"),
    ("gan_s0_gpt5_5_openai.json", "openai", "gpt-5.5", "https://api.openai.com/v1"),
    ("gan_s0_qwen27b_ollama.json", "ollama", "qwen3.6:27b", "http://localhost:11434/v1"),
    ("gan_s0_qwen35b_ollama.json", "ollama", "qwen3.6:35b", "http://localhost:11434/v1"),
    ("gan_s0_qwen35b_ollama_gepa_max10000.json", "ollama", "qwen3.6:35b", "http://localhost:11434/v1"),
    ("gan_s0_qwen35b_ollama_max81920.json", "ollama", "qwen3.6:35b", "http://localhost:11434/v1"),
    ("gan_s0_qwen35b_ollama_temp0_7.json", "ollama", "qwen3.6:35b", "http://localhost:11434/v1"),
    ("gan_s0_qwen35b_ollama_verify_repair.json", "ollama", "qwen3.6:35b", "http://localhost:11434/v1"),
    ("gan_s0_qwen9b_ollama.json", "ollama", "qwen3.5:9b", "http://localhost:11434/v1"),
    ("gan_s0_qwen9b_ollama_max81920.json", "ollama", "qwen3.5:9b", "http://localhost:11434/v1"),
]


@pytest.mark.parametrize("filename,provider,model,base_url", MODEL_CONFIG_FILES)
def test_model_config_file_validates_as_provider_config(filename, provider, model, base_url):
    path = MODEL_CONFIGS_DIR / filename
    config = LLMProviderConfig.model_validate_json(path.read_text(encoding="utf-8"))

    assert config.provider == provider
    assert config.model == model


@pytest.mark.parametrize("filename,provider,model,base_url", MODEL_CONFIG_FILES)
def test_model_config_file_resolves_to_openai_compatible_adapter(
    filename, provider, model, base_url
):
    path = MODEL_CONFIGS_DIR / filename
    config = LLMProviderConfig.model_validate_json(path.read_text(encoding="utf-8"))
    adapter = build_chat_adapter(config)

    assert isinstance(adapter, OpenAICompatibleChatAdapter)
    assert adapter.provider == provider
    assert adapter.model == model
    assert adapter.base_url == base_url


@pytest.mark.parametrize("filename,provider,model,base_url", MODEL_CONFIG_FILES)
def test_model_config_file_resolves_to_dspy_lm(filename, provider, model, base_url):
    import dspy
    path = MODEL_CONFIGS_DIR / filename
    config = LLMProviderConfig.model_validate_json(path.read_text(encoding="utf-8"))
    lm = build_dspy_lm(config)

    assert isinstance(lm, dspy.LM)
    assert lm.model.endswith(model)

    if provider == "ollama":
        assert lm.model.startswith("ollama_chat/")
        assert lm.kwargs["extra_body"].get("think") is False
    elif provider == "gemini":
        assert lm.model.startswith("gemini/")
        if model == "gemini-3-flash-preview":
            assert lm.kwargs.get("reasoning_effort") == "minimal"
        elif model == "gemini-3.1-flash-lite":
            assert "reasoning_effort" not in lm.kwargs
    elif provider == "anthropic":
        assert lm.model.startswith("anthropic/")
        if config.extra_body:
            assert lm.kwargs.get("extra_body") == config.extra_body
    elif provider == "openai":
        assert lm.model.startswith("openai/")
        if model.startswith("gpt-5"):
            assert lm.kwargs.get("temperature") is None


def test_all_model_configs_are_parametrized():
    filenames = {f for f, *_ in MODEL_CONFIG_FILES}
    actual_filenames = {
        path.name for path in MODEL_CONFIGS_DIR.glob("*.json") if path.is_file()
    }

    assert filenames == actual_filenames
