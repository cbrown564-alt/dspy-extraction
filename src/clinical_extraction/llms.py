from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from typing import Any, Literal, Protocol

import dspy
from pydantic import Field, model_validator

from clinical_extraction.schemas import FrozenModel

ProviderName = Literal["mock", "ollama", "openai", "gemini", "openai_compatible"]


class ChatMessage(FrozenModel):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMProviderConfig(FrozenModel):
    provider: ProviderName
    model: str
    base_url: str | None = None
    api_key: str | None = None
    api_key_env: str | None = None
    timeout_seconds: float = Field(default=60.0, gt=0)
    temperature: float | None = Field(default=0.0, ge=0.0)
    mock_responses: list[dict[str, Any] | str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_provider_config(self) -> LLMProviderConfig:
        if not self.model.strip():
            raise ValueError("model must be a non-empty string.")
        if self.provider == "mock" and not self.mock_responses:
            raise ValueError("mock provider requires at least one mock response.")
        return self


class ChatAdapter(Protocol):
    provider: str
    model: str

    def complete_json(
        self,
        messages: Iterable[ChatMessage],
        *,
        response_schema: dict[str, Any] | None = None,
    ) -> str:
        """Return model content expected to contain a single JSON object."""


class MockChatAdapter:
    def __init__(
        self,
        *,
        provider: str = "mock",
        model: str = "fixture",
        responses: Iterable[dict[str, Any] | str],
    ) -> None:
        self.provider = provider
        self.model = model
        self._responses = list(responses)
        self.calls: list[list[ChatMessage]] = []

    def complete_json(
        self,
        messages: Iterable[ChatMessage],
        *,
        response_schema: dict[str, Any] | None = None,
    ) -> str:
        self.calls.append(list(messages))
        if not self._responses:
            raise RuntimeError("MockChatAdapter has no remaining responses.")
        response = self._responses.pop(0)
        if isinstance(response, str):
            return response
        return json.dumps(response)


Transport = Callable[[str, dict[str, str], str, float], dict[str, Any]]


class OpenAICompatibleChatAdapter:
    """Minimal chat-completions adapter for OpenAI-compatible endpoints.

    Ollama's OpenAI-compatible `/v1/chat/completions` endpoint and several
    closed providers can share this path. Provider-specific structured-output
    details stay outside scorers and extraction contracts.
    """

    def __init__(
        self,
        *,
        provider: str,
        model: str,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: float = 60.0,
        temperature: float | None = 0.0,
        transport: Transport | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.temperature = temperature
        self._transport = transport or _urlopen_json

    def complete_json(
        self,
        messages: Iterable[ChatMessage],
        *,
        response_schema: dict[str, Any] | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [message.model_dump() for message in messages],
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if response_schema is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "clinical_extraction_response",
                    "schema": response_schema,
                    "strict": True,
                },
            }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = self._transport(
            f"{self.base_url}/chat/completions",
            headers,
            json.dumps(payload),
            self.timeout_seconds,
        )
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Chat completion response did not include message content.") from exc


def build_chat_adapter(config: LLMProviderConfig) -> ChatAdapter:
    if config.provider == "mock":
        return MockChatAdapter(
            provider=config.provider,
            model=config.model,
            responses=config.mock_responses,
        )

    base_url = config.base_url or _default_base_url(config.provider)
    api_key = config.api_key or _api_key_from_env(config.api_key_env)
    return OpenAICompatibleChatAdapter(
        provider=config.provider,
        model=config.model,
        base_url=base_url,
        api_key=api_key,
        timeout_seconds=config.timeout_seconds,
        temperature=config.temperature,
    )


def _default_base_url(provider: ProviderName) -> str:
    if provider == "ollama":
        return "http://localhost:11434/v1"
    if provider == "openai":
        return "https://api.openai.com/v1"
    if provider == "gemini":
        return "https://generativelanguage.googleapis.com/v1beta/openai"
    if provider == "openai_compatible":
        raise ValueError("openai_compatible provider requires base_url.")
    raise ValueError(f"Unsupported provider: {provider}")


def _api_key_from_env(env_var: str | None) -> str | None:
    if not env_var:
        return None
    return os.environ.get(env_var)


def build_dspy_lm(config: LLMProviderConfig) -> dspy.LM:
    """Build a ``dspy.LM`` from an ``LLMProviderConfig``.

    Gemini routes through LiteLLM's native Gemini support (``gemini/`` prefix).
    All other providers use the OpenAI-compatible path (``openai/`` prefix),
    with ``api_base`` set for non-default endpoints (Ollama, custom).
    """
    api_key = config.api_key or _api_key_from_env(config.api_key_env) or "dummy"

    if config.provider == "gemini":
        kwargs: dict[str, Any] = {
            "model": f"gemini/{config.model}",
            "api_key": api_key,
            "timeout": config.timeout_seconds,
        }
        if config.temperature is not None:
            kwargs["temperature"] = config.temperature
        return dspy.LM(**kwargs)

    base_url = config.base_url or _default_base_url(config.provider)
    kwargs: dict[str, Any] = {
        "model": f"openai/{config.model}",
        "api_key": api_key,
        "timeout": config.timeout_seconds,
    }
    if config.temperature is not None:
        kwargs["temperature"] = config.temperature
    if config.provider != "openai" or config.base_url:
        kwargs["api_base"] = base_url
    return dspy.LM(**kwargs)


def _urlopen_json(
    url: str,
    headers: dict[str, str],
    body: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=body.encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            error_body = exc.read().decode("utf-8")
        except Exception:
            error_body = "(could not read response body)"
        raise RuntimeError(
            f"LLM provider request failed: {exc} — {error_body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"LLM provider request failed: {exc}") from exc
