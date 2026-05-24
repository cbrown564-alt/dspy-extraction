# Model Config Compatibility Backlog

Date: 2026-05-24  
Status: Source-backed backlog note  
Decision scope: operational / test-only  
Source draft: `docs/workstreams/cursor_sdk/archive/compatibility/20260523T164950Z_model_compatibility_report.md`

## Purpose

This note promotes verified, still-current findings from the archived Cursor SDK model compatibility report into a source-backed backlog. It does not change provider configs, adapter behavior, experiment configs, scorer semantics, or registry rows.

The draft was useful as a review lead, but SDK prose is not authority. Findings below were checked against:

- `src/clinical_extraction/llms.py`
- `src/clinical_extraction/experiments/runner.py`
- `scripts/smoke_gan_s0_adapter.py`
- `tests/test_llm_adapters.py`
- `tests/test_model_comparison_configs.py`
- `configs/models/*.json`
- `docs/policies/model_config_smoke_tests.md`
- `docs/policies/qwen_dspy_latency_policy.md`
- `.agents/skills/model-config-compatibility/SKILL.md`

Focused validation run:

```powershell
uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py
```

Result on 2026-05-24: **43 passed**.

## Confirmed Current Facts

### Production Adapter Path

Experiment execution and the legacy smoke script use `build_dspy_lm`, not `build_chat_adapter`:

- `src/clinical_extraction/experiments/runner.py`
- `scripts/smoke_gan_s0_adapter.py`

`build_chat_adapter` remains tested as an OpenAI-compatible chat path, but it is not the current experiment hot path.

### Provider-Specific DSPy Routing

Current `build_dspy_lm` behavior in `src/clinical_extraction/llms.py`:

| Provider | Current DSPy route | Confirmed behavior |
| --- | --- | --- |
| `ollama` | `ollama_chat/{model}` | Injects `extra_body={"think": False, ...}` and strips `/v1` from `api_base`. |
| `gemini` | `gemini/{model}` | Defaults `reasoning_effort="minimal"` when model contains `gemini-3` and config omits it. |
| `anthropic` | `anthropic/{model}` | Passes configured `extra_body` as nested `extra_body` when present. |
| `openai` | `openai/{model}` | Omits `temperature` when config has `temperature: null`. |

### Current Config Coverage

The archived SDK report said two model configs were not covered by parametric tests. That is now stale. `tests/test_model_comparison_configs.py` covers all 15 JSON files under `configs/models/`, including:

- `gan_s0_qwen35b_ollama_verify_repair.json`
- `exect_qwen35b_ollama.json`

The test `test_all_model_configs_are_parametrized` guards this.

## Promoted Backlog Items

### B1 - Keep Adapter-Path Divergence Visible

Status: `open`  
Scope: `mechanism`

`build_dspy_lm` and `build_chat_adapter` intentionally differ today. This is acceptable because experiments use `build_dspy_lm`, but it can mislead compatibility review if only the chat adapter path is inspected.

Current divergence to preserve in reviews:

- Ollama DSPy path injects `think: False`; chat adapter path only sends configured `extra_body`.
- Gemini DSPy path applies `reasoning_effort`; chat adapter path does not.
- Anthropic DSPy path nests `extra_body`; chat adapter merges `extra_body` into the OpenAI-compatible payload.

Suggested future work: if `build_chat_adapter` becomes a production path, add provider-specific parity tests or a shared provider-kwargs builder.

### B2 - Add Runtime Environment Checks Before Live Provider Runs

Status: `open`  
Scope: `operational`

Current config validation checks model shape and some provider-specific parameters, but it does not fail early when required API key environment variables are absent. Hosted provider failures can therefore happen late at call time.

Candidate check:

- For non-`ollama` / non-`mock` configs, dry-run or startup validation should report whether `api_key_env` is set in the current process or `.env`.

Do not make this a normal import-time validation rule, because tests and dry config loading should remain offline-friendly.

### B3 - Keep Qwen Context And Timeout Pairing Explicit

Status: `open`  
Scope: `operational`

Current validation rejects Ollama configs with `max_tokens > 4096` unless `extra_body.options.num_ctx` is set. This is already covered by tests.

Remaining review caveat:

- High-context configs such as `num_ctx=262144` are for explicit stress or long-context runs. `docs/policies/model_config_smoke_tests.md` records that `num_ctx=262144` caused an ExECT 27b attempt to time out before artifacts, while `num_ctx=65536` completed capped smokes.
- `exect_qwen35b_ollama.json` still uses `max_tokens=81920` and `num_ctx=262144`; treat this as high-risk for runtime until a smoke or dry-run policy says otherwise.
- `gan_s0_qwen9b_ollama_max81920.json` uses `timeout_seconds=600` with `num_ctx=262144`; this should stay a stress-test config, not an ordinary smoke default.

Candidate check: add an experiment-startup warning for Ollama configs with `num_ctx >= 131072` and `timeout_seconds < 1800`, or require the experiment config to declare the run as a stress/latency test.

### B4 - Keep GPT-5-Family Temperature Guard

Status: `confirmed`  
Scope: `operational`

`LLMProviderConfig` rejects OpenAI `gpt-5*` configs with `temperature=0.0`, and `gan_s0_gpt5_5_openai.json` uses `"temperature": null`. Tests confirm the adapter omits temperature when null.

GEPA reflection config already preserves null temperature:

- `gepa_reflection_config()` returns the base config unchanged if `base.temperature is None`.
- Otherwise it sets reflection temperature to `1.0`.

Residual risk: future GPT-5-family optimizer runs should keep using a null-temperature base or a separately verified reflection model config.

### B5 - Treat Hosted Timeout And Token Defaults As Unknown Until Run Artifacts Exist

Status: `open`  
Scope: `stale_check`

Hosted configs currently rely on provider defaults for some output budgets:

- Gemini configs omit `max_tokens`.
- GPT 4.1-mini and GPT-5.5 configs omit `max_tokens`.
- Claude Sonnet 4.6 sets `max_tokens=8192`.

This is acceptable for recorded smokes, but not proof that long ExECT S4/S5 full-validation outputs will fit. Any broad hosted-provider comparison should record token budgets, timeout behavior, schema validity, and evidence support in run artifacts.

## Findings Not Promoted

| Draft finding | Review outcome |
| --- | --- |
| "Two model configs are not in parametric config tests." | Stale. Current tests cover all 15 model configs. |
| "Anthropic extended thinking should be disabled." | Not promoted. The need depends on live LiteLLM/provider behavior not verified here. |
| "Gemini reasoning-effort allowlist should reject unknown values." | Not promoted. Needs provider/LiteLLM documentation and should not be inferred from SDK draft. |
| "Structured-output capability probe should be implemented." | Keep as an idea only. It needs design work against DSPy adapter behavior. |
| "OpenAICompatibleChatAdapter should avoid strict JSON schema for Ollama." | Not promoted as current work because experiments use `build_dspy_lm`; revisit only if chat adapter becomes production path. |

## Next Review Gate

Before changing model/provider configs, run:

```powershell
uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py
```

Before any live hosted or Ollama smoke, also follow `docs/policies/model_config_smoke_tests.md` and record the resulting run ID, config path, model/provider, structured-output strategy, schema validity, evidence support, and any timeout or provider-specific caveat.
