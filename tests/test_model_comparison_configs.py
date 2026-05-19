"""Validate all five model comparison config files load and resolve to adapters."""
from pathlib import Path

import pytest

from clinical_extraction.llms import (
    LLMProviderConfig,
    MockChatAdapter,
    OpenAICompatibleChatAdapter,
    build_chat_adapter,
)

MODEL_CONFIGS_DIR = Path("configs/models")

MODEL_CONFIG_FILES = [
    ("gan_s0_gpt4_1_mini.json", "openai", "gpt-4.1-mini", "https://api.openai.com/v1"),
    ("gan_s0_gpt5_5_openai.json", "openai", "gpt-5.5", "https://api.openai.com/v1"),
    ("gan_s0_gemini3_flash.json", "gemini", "gemini-3-flash-preview", "https://generativelanguage.googleapis.com/v1beta/openai"),
    ("gan_s0_qwen35b_ollama.json", "ollama", "qwen3.6:35b", "http://localhost:11434/v1"),
    ("gan_s0_qwen35b_ollama_gepa_max10000.json", "ollama", "qwen3.6:35b", "http://localhost:11434/v1"),
    ("gan_s0_qwen9b_ollama.json", "ollama", "qwen3.5:9b", "http://localhost:11434/v1"),
    ("gan_s0_qwen35b_ollama_max81920.json", "ollama", "qwen3.6:35b", "http://localhost:11434/v1"),
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


def test_all_five_model_configs_are_present():
    filenames = {f for f, *_ in MODEL_CONFIG_FILES}
    for filename in filenames:
        assert (MODEL_CONFIGS_DIR / filename).exists(), f"Missing model config: {filename}"
