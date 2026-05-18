---
name: model-config-compatibility
description: Use when creating, reviewing, debugging, or porting model/provider configs or DSPy adapters for OpenAI GPT-5.5, GPT-4.1-mini, Gemini 3 Flash, Qwen via Ollama, or other LLM providers, especially around unsupported parameters, token limits, timeouts, structured output, and provider-specific reasoning settings.
---

# Model Config Compatibility

Use this skill before model-backed runs and when adapter errors look provider-specific.

## Workflow

1. Identify provider, model name, adapter path, structured-output strategy, and config file.
2. Read the local model config and relevant adapter code before changing parameters.
3. Check provider-specific parameter compatibility:
   - unsupported `temperature`
   - reasoning or extended-thinking parameter names
   - token-output limits
   - request timeout limits
   - JSON schema or structured-output support
   - Ollama/OpenAI-compatible endpoint differences
4. Prefer config or adapter changes over hardcoded provider branches inside experiment logic.
5. Validate with the smallest possible smoke run or dry run before full experiment execution.
6. Record provider caveats in experiment config, prompts, or run metadata when they affect comparability.

## Known Failure Modes

- GPT-5.5 may reject `temperature=0`; do not assume all OpenAI-family models accept the same sampling parameters.
- Gemini 3 Flash uses provider-specific reasoning/extended-thinking controls; do not copy OpenAI reasoning parameters into Gemini configs.
- Qwen via Ollama and GPT-5.5 can fail when token output limits or request timeouts are too low for long clinical notes or ChainOfThought outputs.
- Structured-output support may differ between provider JSON schema, strict JSON prompting, DSPy `JSONAdapter`, and DSPy `ChatAdapter` fallback.
- Manual prompt-era provider settings may not translate directly into DSPy adapter settings.

## Checks

- Does the model config contain only parameters the provider accepts?
- Are max tokens and timeout large enough for the note length, reasoning style, and output schema?
- Is structured output validated by Pydantic after provider parsing?
- Does the experiment config record the structured-output strategy?
- Is any provider-specific behavior isolated in `clinical_extraction.llms` or model config?

## Completion Criteria

Before finishing, summarize:

- provider and model checked
- config fields changed or confirmed
- known incompatible parameters avoided
- smoke/dry-run validation performed
- residual provider-specific risk
