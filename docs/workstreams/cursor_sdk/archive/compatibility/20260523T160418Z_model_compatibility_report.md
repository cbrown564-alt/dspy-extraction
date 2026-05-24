# Model Compatibility and Adapter Report

**Review-only draft.** Not evidence for paper claims unless tied to primary run artifacts. No files were edited.

---

## Sources Read

| Path | Role |
|------|------|
| `configs/models/*.json` (15 configs; excludes `.gitkeep`) | Frozen model/provider parameter sets |
| `src/clinical_extraction/llms.py` | `LLMProviderConfig`, `OpenAICompatibleChatAdapter`, `build_chat_adapter`, `build_dspy_lm` |
| `docs/policies/model_config_smoke_tests.md` | Smoke outcomes, known provider failures (GPT-5.5 temperature, Gemini model id, Qwen context/timeouts) |
| `.agents/skills/model-config-compatibility/SKILL.md` | Workflow, known failure modes, completion criteria |
| `docs/policies/constrained_json_decoding_strategy.md` | DSPy JSONAdapter vs ChatAdapter fallback policy |
| `docs/policies/qwen_dspy_latency_policy.md` | Ollama `think=false`, `num_ctx` + `max_tokens` coupling, CoT/Bootstrap guidance |
| `docs/workstreams/optimizer/qwen_local_latency_experiment_20260518.md` | Measured truncation/timeout failures under low budgets |
| `tests/test_llm_adapters.py` | Adapter unit expectations |
| `tests/test_model_comparison_configs.py` | Config load/adapter resolution coverage (partial) |
| `tests/test_experiment_configs.py` | ExECT Qwen budget assertions |
| `src/clinical_extraction/experiments/runner.py` | Production path: `build_dspy_lm` only; GEPA reflection LM override |
| `scripts/smoke_gan_s0_adapter.py` | Opt-in smoke also uses `build_dspy_lm` |

**Missing context (not read):** LiteLLM version-specific parameter names for GPT-5.5 reasoning controls, Anthropic extended-thinking defaults for `claude-sonnet-4-6`, and live Ollama OpenAI-compat schema support per tag. Claims below about those behaviors are flagged as uncertain.

---

## Model Config Gaps & Gaps Matrix

### Facts: two adapter paths diverge

**Fact:** Experiment runs call `build_dspy_lm` (`runner.py` L482–485; `smoke_gan_s0_adapter.py` L48). `build_chat_adapter` is tested but not used on the experiment hot path (`grep` shows no experiment-backend usage).

**Fact:** Provider routing differs between paths (`llms.py`):

| Provider | `build_dspy_lm` | `build_chat_adapter` |
|----------|-----------------|----------------------|
| `ollama` | LiteLLM `ollama_chat/{model}`; forces `extra_body={"think": False, …}` | OpenAI-compat `POST …/chat/completions` at `localhost:11434/v1`; no `think:false` |
| `gemini` | LiteLLM `gemini/{model}`; passes `reasoning_effort` | OpenAI-compat Gemini proxy URL; **no** `reasoning_effort` |
| `anthropic` | LiteLLM `anthropic/{model}`; `extra_body` nested in kwargs | OpenAI-compat Anthropic URL; `extra_body` merged flat into payload |
| `openai` | LiteLLM `openai/{model}` | Same OpenAI-compat adapter |

**Interpretation (decision scope: `mechanism`):** Config fields like `reasoning_effort` and Ollama `options.num_ctx` behave differently depending on which adapter is invoked. Today’s runs are mostly safe because experiments use `build_dspy_lm`, but config validation that only exercises `build_chat_adapter` (`test_model_comparison_configs.py`) can give a false “compatible” signal for Ollama/Gemini.

---

### Local Qwen (Ollama) configs

| Config file | Model tag | `max_tokens` | `num_ctx` (`extra_body.options`) | `timeout_seconds` | `num_retries` | Primary use (inferred from paths/caveats) |
|-------------|-----------|--------------|-------------------------------------|-------------------|---------------|-------------------------------------------|
| `gan_s0_qwen9b_ollama.json` | `qwen3.5:9b` | 1536 | *(none — Ollama default 4096)* | 600 | 0 | Gan F0 smoke/direct (`docs/policies/model_config_smoke_tests.md` L59) |
| `gan_s0_qwen9b_ollama_max81920.json` | `qwen3.5:9b` | 81920 | 262144 | 600 | 0 | Max-budget stress (`qwen_dspy_latency_policy.md` L20–23) |
| `exect_qwen9b_ollama.json` | `qwen3.5:9b` | 16384 | 65536 | 1800 | 0 | ExECT long-note smoke |
| `gan_s0_qwen27b_ollama.json` | `qwen3.6:27b` | 256 | *(none)* | 600 | 0 | Gan F0 smoke |
| `exect_qwen27b_ollama.json` | `qwen3.6:27b` | 16384 | 65536 | 1800 | 0 | ExECT S1/S4 smokes (bounded after 262144 timeout — `model_config_smoke_tests.md` L58) |
| `gan_s0_qwen35b_ollama.json` | `qwen3.6:35b` | 256 | *(none)* | 600 | 0 | Gan direct full-validation default |
| `gan_s0_qwen35b_ollama_verify_repair.json` | `qwen3.6:35b` | 4096 | *(none)* | 600 | 0 | Verify-repair slice (`gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json`) |
| `gan_s0_qwen35b_ollama_gepa_max10000.json` | `qwen3.6:35b` | 10000 | *(none)* | 600 | 0 | GEPA optimizer experiments |
| `gan_s0_qwen35b_ollama_max81920.json` | `qwen3.6:35b` | 81920 | 262144 | 1800 | 0 | Max-budget CoT stress |
| `exect_qwen35b_ollama.json` | `qwen3.6:35b` | 81920 | 262144 | 1800 | 0 | ExECT regression (`test_experiment_configs.py` L1844–1849) |

**Facts — Ollama-specific:**

- `build_dspy_lm` always injects `think: False` for Ollama (`llms.py` L259–266; `test_llm_adapters.py` L65–78). Documented rationale: OpenAI-compat `/v1` route returned hidden reasoning with empty final content (`qwen_local_latency_experiment_20260518.md` L20; `qwen_dspy_latency_policy.md` L13–16).
- `num_retries=0` on all Qwen configs; hosted configs omit the field and inherit default `3` (`llms.py` L41).
- Smoke evidence: 27b ExECT at `num_ctx=262144` timed out before artifacts; `65536` completed at ~537–552 s/record (`model_config_smoke_tests.md` L58). **Operational** lesson recorded; not a universal hardware bound.

**Gaps / risks (with decision scope):**

| Gap | Scope | Severity | Evidence |
|-----|-------|----------|----------|
| Gan smoke configs (`gan_s0_qwen27b_ollama.json`, `gan_s0_qwen35b_ollama.json`) use `max_tokens=256` with no `num_ctx` | `operational` | Truncation / schema-invalid outputs if program variant adds reasoning or long outputs | `qwen_local_latency_experiment_20260518.md` L30–32, L117–118; configs |
| `gan_s0_qwen35b_ollama_verify_repair.json` raises `max_tokens` to 4096 but still omits `num_ctx` | `arm` | May silently run at Ollama default context (4096) while expecting longer verify-repair payloads | Config vs `qwen_dspy_latency_policy.md` L14–16 |
| `exect_qwen35b_ollama.json` uses `num_ctx=262144` while `exect_qwen27b_ollama.json` uses `65536` for same suite | `operational` | 35b ExECT runs may hit RAM/residency and timeout risks that 27b smokes already mitigated | Configs; 27b timeout history `model_config_smoke_tests.md` L58 |
| `gan_s0_qwen35b_ollama.json` smoke status **deferred** on Mac (tag missing) | `blocked` | Environment gate, not adapter bug | `model_config_smoke_tests.md` L57 |
| Max-budget configs (`*_max81920.json`) not required for ordinary smokes | `mechanism` | Mis-applying them changes latency comparability | `qwen_dspy_latency_policy.md` L25–26 |

**Uncertainty:** Whether `extra_body.options.num_ctx` is honored identically on `ollama_chat/` vs OpenAI-compat chat adapter path — only the DSPy path is production-tested.

---

### Hosted Gemini configs

| Config | Model id | `temperature` | `reasoning_effort` | `max_tokens` | `timeout_seconds` |
|--------|----------|---------------|--------------------|--------------|-------------------|
| `gan_s0_gemini3_flash.json` | `gemini-3-flash-preview` | 0.0 | `"minimal"` (also code-default if omitted for `gemini-3*`) | *(unset)* | 60 |
| `gan_s0_gemini31_flash_lite.json` | `gemini-3.1-flash-lite` | 0.0 | *(unset)* | *(unset)* | 60 |

**Facts:**

- Invalid model id `gemini-3-flash` caused 404; fixed to `gemini-3-flash-preview` (`model_config_smoke_tests.md` L55, L61–65).
- Code auto-defaults `reasoning_effort="minimal"` when model string contains `gemini-3` and field is null (`llms.py` L234–238; `test_llm_adapters.py` L52–62).
- Gemini 3 Flash one-record smoke: runtime OK, schema 0/1 on sampled record (invalid label `'2 per 4 month'`) — **compatibility only**, not quality (`model_config_smoke_tests.md` L55, L64–65).
- Gemini 3.1 Flash-Lite smoke completed (`model_config_smoke_tests.md` L56).

**Gaps / risks:**

| Gap | Scope | Notes |
|-----|-------|-------|
| No explicit `max_tokens` on either Gemini config | `operational` | Long ExECT multi-family JSON + evidence may hit provider output limits; smoke tests used capped record counts |
| `reasoning_effort` only on 3 Flash, not 3.1 Flash-Lite | `open` | Comparability across Gemini variants uncertain without primary artifacts |
| 60 s timeout vs Ollama 600–1800 s | `operational` | Hosted smokes are fast on 1–3 records; full-validation timeout risk **uncertain** without run logs |
| `build_chat_adapter` ignores `reasoning_effort` | `mechanism` | Latent if chat adapter becomes production path |

---

### Hosted OpenAI configs

| Config | Model | `temperature` | `max_tokens` | `timeout_seconds` |
|--------|-------|---------------|--------------|-------------------|
| `gan_s0_gpt4_1_mini.json` | `gpt-4.1-mini` | 0.0 | *(unset)* | 60 |
| `gan_s0_gpt5_5_openai.json` | `gpt-5.5` | **`null`** | *(unset)* | 90 |

**Facts:**

- GPT-5.5 rejected `temperature=0`; config sets `"temperature": null`; adapter omits key when null (`model_config_smoke_tests.md` L67–69; `llms.py` L138–139, L280–281; `test_llm_adapters.py` L195–213).
- Both smokes completed on Windows (`model_config_smoke_tests.md` L53–54).

**Gaps / risks:**

| Gap | Scope | Notes |
|-----|-------|-------|
| `build_dspy_lm` OpenAI path does not map `reasoning_effort` or `extra_body` | `open` | If GPT-5.5 gains reasoning-only parameters, configs cannot express them today (`llms.py` L274–286) |
| GEPA runs set `reflection_config.temperature = 1.0` (`runner.py` L488–490) | `blocked` / `arm` | **Uncertain** whether GPT-5.5 rejects `temperature=1.0`; would surface only on GEPA experiments |
| No `max_tokens` cap | `operational` | Relies on provider defaults; usually fine for Gan S0, uncertain for ExECT S4 breadth |

---

### Hosted Anthropic config

| Config | Model | `temperature` | `max_tokens` | `timeout_seconds` | `extra_body` |
|--------|-------|---------------|--------------|-------------------|--------------|
| `gan_s0_claude_sonnet_4_6_anthropic.json` | `claude-sonnet-4-6` | 0.0 | 8192 | 90 | *(none)* |

**Facts:**

- Smokes completed (Gan 1-record + model-suite 3-record) (`model_config_smoke_tests.md` L52).
- `build_dspy_lm` passes `extra_body` as nested `kwargs["extra_body"]` (`llms.py` L254–255). Unit test shows chat adapter can send `thinking: {"type": "disabled"}` (`test_llm_adapters.py` L216–234), but **config does not set this**.

**Gaps / risks:**

| Gap | Scope | Notes |
|-----|-------|-------|
| Extended thinking not explicitly disabled in model config | `open` | **Uncertain** default for Sonnet 4.6 via LiteLLM; may affect latency/cost comparability |
| `max_tokens=8192` may be tight for ExECT S4 multi-field JSON on long notes | `operational` | Smoke used 3 records; full-validation risk **uncertain** |
| Chat vs DSPy path both differ from native Messages API | `mechanism` | DSPy uses LiteLLM native prefix; chat adapter uses OpenAI-compat URL (`llms.py` L196–199) |

---

### Cross-provider parameter matrix (summary)

| Parameter | Local Qwen | Gemini | OpenAI GPT-4.1 | OpenAI GPT-5.5 | Anthropic |
|-----------|------------|--------|----------------|----------------|-----------|
| `temperature=0.0` | All configs | Both | Yes | **Rejected — use `null`** | Yes |
| `reasoning_effort` | N/A (use `think:false` in adapter) | 3 Flash: explicit; 3.1 Lite: absent | Not wired in `build_dspy_lm` | Not wired | N/A |
| `max_tokens` | 256–81920 (task-dependent) | Unset | Unset | Unset | 8192 |
| `num_ctx` / context | Only in `extra_body.options` on ExECT/max-budget | Provider-managed | Provider-managed | Provider-managed | Provider-managed |
| `timeout_seconds` | 600–1800 | 60 | 60 | 90 | 90 |
| `num_retries` | 0 | 3 (default) | 3 (default) | 3 (default) | 3 (default) |
| Structured JSON | DSPy JSONAdapter → ChatAdapter fallback (`constrained_json_decoding_strategy.md`) | Via LiteLLM Gemini | Via LiteLLM OpenAI | Via LiteLLM OpenAI | Via LiteLLM Anthropic |
| Config test coverage | 10/15 files in `test_model_comparison_configs.py` | Included | Included | Included | Included |

**Not in parametric config tests (`stale_check`):**

- `gan_s0_qwen35b_ollama_verify_repair.json`
- `exect_qwen35b_ollama.json`

---

## Draft Adapter Wrapper/Interface Proposals

*Draft only — not implemented.*

### 1. Unified provider kwargs builder (single source for both adapters)

**Problem:** `reasoning_effort`, Ollama `think`, and `extra_body` nesting differ across providers and between `build_dspy_lm` / `build_chat_adapter` (`llms.py`).

```python
# Draft: src/clinical_extraction/llms.py (conceptual)
from typing import Any

def _provider_kwargs(config: LLMProviderConfig, *, for_dspy: bool) -> dict[str, Any]:
    """Map LLMProviderConfig to provider-safe kwargs."""
    kwargs: dict[str, Any] = {
        "timeout": config.timeout_seconds,
        "num_retries": config.num_retries,
    }
    if config.max_tokens is not None:
        kwargs["max_tokens"] = config.max_tokens

    # Temperature: omit when null (GPT-5.5 pattern)
    if config.temperature is not None:
        kwargs["temperature"] = config.temperature

    if config.provider == "ollama":
        extra = {"think": False, **config.extra_body}
        if for_dspy:
            kwargs["model"] = f"ollama_chat/{config.model}"
            kwargs["api_base"] = (config.base_url or "http://localhost:11434/v1").removesuffix("/v1")
            kwargs["extra_body"] = extra
        else:
            # OpenAI-compat path: flatten options if present
            kwargs["extra_body"] = extra
        return kwargs

    if config.provider == "gemini":
        kwargs["model"] = f"gemini/{config.model}"
        reasoning = config.reasoning_effort
        if reasoning is None and "gemini-3" in config.model:
            reasoning = "minimal"
        if reasoning is not None:
            kwargs["reasoning_effort"] = reasoning
        if config.extra_body:
            kwargs.update(config.extra_body)
        return kwargs

    if config.provider == "anthropic":
        kwargs["model"] = f"anthropic/{config.model}"
        extra = dict(config.extra_body)
        # Optional: disable extended thinking unless explicitly enabled
        extra.setdefault("thinking", {"type": "disabled"})
        if for_dspy:
            kwargs["extra_body"] = extra
        else:
            kwargs["extra_body"] = extra  # chat adapter merges flat
        return kwargs

    # openai / openai_compatible
    kwargs["model"] = f"openai/{config.model}"
    if config.extra_body:
        kwargs["extra_body"] = config.extra_body
    return kwargs
```

**Decision scope:** `mechanism` — reduces drift between adapter paths; does not change scorer or experiment semantics.

---

### 2. Ollama context budget validator (config + runtime)

**Problem:** `max_tokens=81920` without `num_ctx` still ran at Ollama default 4096 in at least one 9B run (`qwen_local_latency_experiment_20260518.md` L93–95).

```python
# Draft validation hook on LLMProviderConfig
@model_validator(mode="after")
def validate_ollama_context_budget(self) -> LLMProviderConfig:
    if self.provider != "ollama":
        return self
    num_ctx = (self.extra_body.get("options") or {}).get("num_ctx")
    if self.max_tokens and self.max_tokens > 4096 and num_ctx is None:
        raise ValueError(
            "Ollama config with max_tokens > 4096 should set "
            "extra_body.options.num_ctx (see docs/policies/qwen_dspy_latency_policy.md)."
        )
    if num_ctx and self.timeout_seconds < 600:
        raise ValueError(
            f"num_ctx={num_ctx} with timeout_seconds={self.timeout_seconds} "
            "is likely to timeout on long notes (see model_config_smoke_tests.md ExECT 27b)."
        )
    return self
```

**Decision scope:** `operational` — prevents silent context mismatch.

---

### 3. GEPA reflection LM safe override

**Problem:** `runner.py` L489 forces `temperature=1.0` for GEPA reflection on any model config.

```python
# Draft: runner.py (conceptual)
def _reflection_config(base: LLMProviderConfig) -> LLMProviderConfig:
    if base.temperature is None:
        # GPT-5.5-style: keep provider default
        return base
    return base.model_copy(update={"temperature": 1.0})
```

**Decision scope:** `arm` — affects optimizer experiments only.

---

### 4. Structured-output capability probe (startup smoke)

**Problem:** `provider_json_schema_with_pydantic_validation` assumes JSON schema support; Ollama may fall back to ChatAdapter (`constrained_json_decoding_strategy.md` L31–33). Fallback is acceptable but should be logged.

```python
# Draft: optional startup probe (uses build_dspy_lm path)
def probe_structured_output(lm: dspy.LM, schema: dict) -> str:
    """Returns 'json_schema' | 'chat_marker' | 'failed'."""
    try:
        # Minimal one-turn call with tiny schema; inspect adapter metadata if exposed
        ...
    except Exception:
        return "failed"
```

**Decision scope:** `operational` — records actual strategy in run metadata without changing `structured_output_strategy` enum.

---

### 5. Configuration recommendations (no code)

| Scenario | Recommended config pattern | Source basis |
|----------|---------------------------|--------------|
| Gan F0 direct smoke (Qwen 27b/35b) | Keep `max_tokens=256` only for 1-record compatibility smokes; use ≥4096 for any CoT/verify-repair | Latency experiment + verify_repair config gap |
| ExECT local Qwen | Pair `max_tokens` ≥16384 with bounded `num_ctx` (65536 for 27b smokes; treat 262144 on 35b as high-risk) | `exect_qwen27b_ollama.json`, smoke timeout history |
| Max-budget / CoT stress | `gan_s0_qwen*_ollama_max81920.json` + explicit metric caveats | `qwen_dspy_latency_policy.md` |
| GPT-5.5 | `"temperature": null`; avoid GEPA until reflection override is fixed | `gan_s0_gpt5_5_openai.json`, `runner.py` L489 |
| Gemini 3 Flash | Keep `reasoning_effort: "minimal"`; do not copy OpenAI reasoning params | `gan_s0_gemini3_flash.json`, skill L28 |
| Anthropic Sonnet 4.6 | Consider `"extra_body": {"thinking": {"type": "disabled"}}` if extended thinking is default | `test_llm_adapters.py` L228 — **behavior uncertain on live API** |

---

## Recommended Parameter Validations

Rules to run at config load or experiment startup (`LLMProviderConfig.model_validate_json` / dry-run extension). Each tagged with decision scope.

### Universal

| Rule | Scope | Action |
|------|-------|--------|
| `model` non-empty | `operational` | Already enforced (`llms.py` L46–47) |
| `timeout_seconds > 0` | `operational` | Already enforced (`llms.py` L36) |
| `api_key_env` set for non-`ollama`/`mock` providers → env var must exist | `operational` | **Missing today** — fails late at API call |
| Warn if `structured_output_strategy == "provider_json_schema_with_pydantic_validation"` and provider is `ollama` | `operational` | Log expected ChatAdapter fallback per policy |

### OpenAI

| Rule | Scope | Action |
|------|-------|--------|
| If `model` matches `gpt-5*` and `temperature == 0.0`, reject with message pointing to `gan_s0_gpt5_5_openai.json` | `operational` | Documented failure (`model_config_smoke_tests.md` L67–69) |
| If `model` matches `gpt-5*` and experiment uses GEPA optimizer, warn or block until reflection temperature override is safe | `blocked` | `runner.py` L488–490 |

### Gemini

| Rule | Scope | Action |
|------|-------|--------|
| If `provider == "gemini"` and `"gemini-3" in model` and `reasoning_effort is None`, info-log auto-default `"minimal"` | `operational` | Matches `llms.py` L234–236 |
| Reject unknown `reasoning_effort` values unless allowlisted (`minimal`, …) | `open` | **Allowlist unknown** — needs LiteLLM/Gemini docs |
| For ExECT experiments, require explicit `max_tokens` or document provider default | `stale_check` | Both Gemini configs omit field |

### Anthropic

| Rule | Scope | Action |
|------|-------|--------|
| Require `max_tokens` when `provider == "anthropic"` | `operational` | Config sets 8192; default is None in schema |
| Warn if `max_tokens < 4096` on ExECT S4 experiment configs | `operational` | Long structured outputs |
| Optional: require `extra_body.thinking.type == "disabled"` unless experiment tests thinking | `open` | **Uncertain** necessity |

### Ollama / Qwen

| Rule | Scope | Action |
|------|-------|--------|
| Require `base_url` reachable (HTTP HEAD/GET) on non-dry-run startup | `operational` | **Missing today** |
| If `max_tokens > 4096`, require `extra_body.options.num_ctx` | `operational` | Policy (`qwen_dspy_latency_policy.md` L14–16) |
| If `num_ctx >= 131072`, require `timeout_seconds >= 1800` for ExECT variants | `operational` | Smoke timeout at 262144 (`model_config_smoke_tests.md` L58) |
| If program variant contains `ChainOfThought` and `max_tokens < 8192`, warn | `mechanism` | Truncation failures (`qwen_local_latency_experiment_20260518.md`) |
| Assert `num_retries == 0` for local Qwen in latency-sensitive arms (optional lint) | `arm` | All Qwen configs use 0 |
| Verify Ollama tag exists (`ollama show {model}`) before run | `blocked` | Mac deferral for 35b (`model_config_smoke_tests.md` L57) |

### Cross-config lint (CI)

| Rule | Scope | Action |
|------|-------|--------|
| Extend `MODEL_CONFIG_FILES` in `test_model_comparison_configs.py` to all 15 JSON configs | `stale_check` | Covers `verify_repair`, `exect_qwen35b` |
| Add `test_build_dspy_lm_*` per provider mirroring chat adapter tests | `mechanism` | Chat tests do not exercise `ollama_chat/` or Gemini native routing |
| Pair experiment `program_variant` with minimum `max_tokens` / `num_ctx` table | `operational` | **Missing** — would need experiment config crosswalk |

---

## Residual Risks Summary

| Risk | Scope | Status |
|------|-------|--------|
| Dual adapter paths with divergent parameter mapping | `mechanism` | Open — mitigated because production uses `build_dspy_lm` only |
| Qwen 35b smoke not re-verified on all target hosts | `blocked` | Mac blocked; Windows status in smoke doc but not in this scan’s runtime |
| Hosted 60–90 s timeouts on full-validation ExECT | `open` | Uncertain without primary full-validation artifacts per provider |
| GPT-5.5 + GEPA reflection temperature | `blocked` | Uncertain failure mode |
| Gemini 3 Flash label quality on smoke record | `arm` | Compatibility proven; quality not (`model_config_smoke_tests.md` L64–65) |
| Config test coverage gaps | `stale_check` | 2 model configs untested in parametric suite |

---

*End of review-only draft. Point to primary run directories under `runs/` and experiment configs under `configs/experiments/` for empirical claims beyond compatibility.*