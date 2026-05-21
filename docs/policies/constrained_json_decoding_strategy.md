# Constrained JSON Decoding Strategy

Date: 2026-05-17 (revised)

## Decision

Use DSPy's adapter layer for structured output. DSPy's ``JSONAdapter`` requests
provider JSON-schema response formatting when the endpoint supports it and falls
back to the chat-marker format (``ChatAdapter``) when it does not.
Pydantic validation of the program's output fields remains the source of truth
for schema acceptance, scorer inputs, and error reporting.

For the first model-backed path, the active signature is ``GanFrequencyS0Signature``
from ``clinical_extraction.programs.gan_frequency_s0``. DSPy handles prompt
construction, schema request, and output parsing; the project does not manually
write system prompts or JSON response schemas.

## Fallback

When a provider or local runtime does not support JSON-schema response formatting,
DSPy's ``ChatAdapter`` uses its chat-marker format with the same output field
validation. The fallback changes the adapter path but must not change the
``PredictionSet``, scorer mode, field names, evidence requirements, or
benchmark-facing metric semantics.

## Provider Notes

- OpenAI-compatible endpoints: DSPy's ``JSONAdapter`` requests
  ``response_format.type=json_schema`` with ``strict=true`` when the endpoint
  supports it; use a strict JSON prompt fallback otherwise.
- Ollama OpenAI-compatible endpoint: attempt the same adapter path; if the
  model/runtime rejects JSON schema, DSPy falls back to ``ChatAdapter`` and
  the text-marker format.
- Gemini via LiteLLM: routes through LiteLLM's native Gemini support using
  the ``gemini/`` model prefix; structured output follows LiteLLM's adapter.
- Mock LM for tests: use ``dspy.utils.DummyLM`` with response dicts; tests
  exercise the program's signature and ``PredictionSet`` output contract
  without real provider calls.

## Reporting Rules

Experiment configs and run metadata record the structured-output strategy.
Reports distinguish schema validity and repair/abstention diagnostics from
Gan benchmark-facing monthly-frequency, Purist category, and Pragmatic
category metrics.
