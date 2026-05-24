# Model Compatibility and Adapter Report

**Review-only draft.** Not evidence for paper claims unless tied to primary run artifacts under `runs/` or experiment configs under `configs/experiments/`. No files were edited.

---

## Sources Read

| Path | Role |
|------|------|
| `configs/models/*.json` (15 configs; excludes `.gitkeep`) | Frozen provider/model parameter sets |
| `src/clinical_extraction/llms.py` | `LLMProviderConfig`, `OpenAICompatibleChatAdapter`, `build_chat_adapter`, `build_dspy_lm` |
| `docs/policies/model_config_smoke_tests.md` | Recorded smoke outcomes, known provider failures, Qwen context/timeout history |
| `.agents/skills/model-config-compatibility/SKILL.md` | Review workflow and known failure modes |
| `tests/test_llm_adapters.py` | Unit expectations for adapter routing and validation guards |
| `tests/test_model_comparison_configs.py` | Parametric load/adapter resolution for all 15 model configs |
| `src/clinical_extraction/experiments/runner.py` | Production path uses `build_dspy_lm`; GEPA reflection LM override |
| `scripts/smoke_gan_s0_adapter.py` | Opt-in smoke also uses `build_dspy_lm` |
| `docs/policies/qwen_dspy_latency_policy.md` | Ollama `think=false`, `num_ctx` + `max_tokens` coupling (referenced by smoke policy) |
| `docs/policies/model_config_compatibility_backlog_20260524.md` | Prior source-backed backlog (cross-check only; not a primary source for this scan) |

**Missing context (not read):** LiteLLM version pinned in project dependencies, live LiteLLM parameter mapping for GPT-5.5 reasoning controls, Anthropic extended-thinking defaults for `claude-sonnet-4-6`, and per-tag Ollama OpenAI-compat JSON-schema support. Claims about those behaviors are flagged as uncertain below.

---

## Model Config Gaps & Gaps Matrix

### Fact: production vs. review paths diverge

**Fact:** Experiment execution and the legacy smoke script call `build_dspy_lm`, not `build_chat_adapter` (`src/clinical_extraction/experiments/runner.py` ~L474–527; `scripts/smoke_gan_s0_adapter.py` L45–48).

**Fact:** `tests/test_model_comparison_configs.py` validates every model JSON via `build_chat_adapter` only. That path does not exercise Gemini `reasoning_effort`, Ollama `think: False`, or Anthropic nested `extra_body` behavior from `build_dspy_lm`.

**Interpretation (scope: `mechanism`):** Config reviews that inspect only the chat-adapter resolution can miss production-path incompatibilities. This is acceptable today because experiments use `build_dspy_lm`, but it is a latent false-confidence risk.

| Provider | `build_dspy_lm` (`llms.py`) | `build_chat_adapter` (`llms.py`) |
|----------|----------------------------|----------------------------------|
| `ollama` | `ollama_chat/{model}`; injects `extra_body={"think": False, …}`; `api_base` strips `/v1` (L272–285) | OpenAI-compat `POST …/v1/chat/completions`; no `think: False` (L192–201) |
| `gemini` | `gemini/{model}`; passes `reasoning_effort` (L236–254) | OpenAI-compat Gemini proxy URL; no `reasoning_effort` (L192–201) |
| `anthropic` | `anthropic/{model}`; nests `extra_body` in kwargs (L256–268) | Merges `extra_body` flat into chat payload (L155) |
| `openai` | `openai/{model}`; omits `temperature` when null (L287–299) | Same OpenAI-compat adapter; omits null temperature (L151–152) |

---

### Local Qwen (Ollama) configs

| Config file | Model | `max_tokens` | `num_ctx` | `timeout_s` | `num_retries` |
|-------------|-------|--------------|-----------|-------------|---------------|
| `gan_s0_qwen9b_ollama.json` | `qwen3.5:9b` | 1536 | *(none)* | 600 | 0 |
| `gan_s0_qwen9b_ollama_max81920.json` | `qwen3.5:9b` | 81920 | 262144 | 600 | 0 |
| `exect_qwen9b_ollama.json` | `qwen3.5:9b` | 16384 | 65536 | 1800 | 0 |
| `gan_s0_qwen27b_ollama.json` | `qwen3.6:27b` | 256 | *(none)* | 600 | 0 |
| `exect_qwen27b_ollama.json` | `qwen3.6:27b` | 16384 | 65536 | 1800 | 0 |
| `gan_s0_qwen35b_ollama.json` | `qwen3.6:35b` | 256 | *(none)* | 600 | 0 |
| `gan_s0_qwen35b_ollama_verify_repair.json` | `qwen3.6:35b` | 4096 | *(none)* | 600 | 0 |
| `gan_s0_qwen35b_ollama_gepa_max10000.json` | `qwen3.6:35b` | 10000 | 65536 | 600 | 0 |
| `gan_s0_qwen35b_ollama_max81920.json` | `qwen3.6:35b` | 81920 | 262144 | 1800 | 0 |
| `exect_qwen35b_ollama.json` | `qwen3.6:35b` | 81920 | 262144 | 1800 | 0 |

**Facts — Ollama-specific:**

- `build_dspy_lm` always injects `think: False` for Ollama (`llms.py` L272–279; `tests/test_llm_adapters.py` L67–81). `docs/policies/qwen_dspy_latency_policy.md` L13–16 documents why thinking must stay disabled for local Qwen.
- Startup validation rejects `max_tokens > 4096` without `extra_body.options.num_ctx` (`llms.py` L56–62; `tests/test_llm_adapters.py` L89–96).
- All Qwen configs set `num_retries=0`. Hosted configs omit the field and inherit default `3` (`llms.py` L41).
- Smoke evidence: 27b ExECT at `num_ctx=262144` timed out before artifacts; `num_ctx=65536` completed at ~537–552 s/record (`docs/policies/model_config_smoke_tests.md` L58). Gan 9b/27b smokes completed at default/low context (`model_config_smoke_tests.md` L58–59). 35b Gan smoke deferred on Mac due to missing Ollama tag (`model_config_smoke_tests.md` L57).

**Gaps / risks (Ollama):**

| Gap | Scope | Notes |
|-----|-------|-------|
| Gan smoke configs use `max_tokens=256` with no `num_ctx` | `operational` | May truncate if program variant emits reasoning or long structured output. Configs: `gan_s0_qwen27b_ollama.json`, `gan_s0_qwen35b_ollama.json`. |
| `gan_s0_qwen35b_ollama_verify_repair.json` has `max_tokens=4096` but no `num_ctx` | `arm` | Passes validation (threshold is `> 4096`), but may run at Ollama default context (~4096) while verify-repair expects larger payloads. Policy says max-budget runs need explicit `num_ctx` (`qwen_dspy_latency_policy.md` L14–16). |
| `exect_qwen35b_ollama.json` uses `num_ctx=262144`; `exect_qwen27b_ollama.json` uses `65536` | `operational` | 35b ExECT may hit residency/timeout risks that 27b smokes already mitigated (`model_config_smoke_tests.md` L58). |
| `gan_s0_qwen9b_ollama_max81920.json`: `num_ctx=262144`, `timeout_seconds=600` | `operational` | Same 9b model in `exect_qwen9b_ollama.json` uses 1800 s timeout. Stress config may timeout on long notes. |
| Max-budget configs (`*_max81920.json`, `exect_qwen35b_ollama.json`) | `mechanism` | Explicit stress/latency configs per `qwen_dspy_latency_policy.md` L25–26; not ordinary smoke defaults. |
| `gan_s0_qwen35b_ollama.json` smoke status deferred (Mac) | `blocked` | Environment gate (`model_config_smoke_tests.md` L57), not necessarily an adapter bug. |
| `extra_body.options.num_ctx` on chat-adapter path | `stale_check` | **Uncertain** whether OpenAI-compat `/v1/chat/completions` honors `options.num_ctx` identically to `ollama_chat/`. Only DSPy path is production-tested. |

---

### Hosted Gemini configs

| Config | Model id | `temperature` | `reasoning_effort` (config) | `max_tokens` | `timeout_s` | `num_retries` |
|--------|----------|---------------|----------------------------|--------------|-------------|---------------|
| `gan_s0_gemini3_flash.json` | `gemini-3-flash-preview` | 0.0 | `"minimal"` | *(unset)* | 60 | 3 (default) |
| `gan_s0_gemini31_flash_lite.json` | `gemini-3.1-flash-lite` | 0.0 | *(unset)* | *(unset)* | 60 | 3 (default) |

**Facts — Gemini-specific:**

- `build_dspy_lm` auto-defaults `reasoning_effort="minimal"` when model string contains `"gemini-3"` and field is null (`llms.py` L247–251; `tests/test_llm_adapters.py` L54–64).
- Because `"gemini-3"` is a substring of `"gemini-3.1-flash-lite"`, **3.1 Flash-Lite receives `reasoning_effort="minimal"` at runtime even though its config omits the field.** This is code behavior, not config intent.
- 3 Flash smoke completed but produced an invalid Gan label on the one record (`model_config_smoke_tests.md` L55, L61–65) — compatibility only, not label quality.
- 3.1 Flash-Lite smoke completed (`model_config_smoke_tests.md` L56). Prior invalid model id `gemini-3-flash` caused 404; fixed to preview/GA ids (`model_config_smoke_tests.md` L55–56).

**Gaps / risks (Gemini):**

| Gap | Scope | Notes |
|-----|-------|-------|
| Substring `"gemini-3"` auto-injects `reasoning_effort` onto 3.1 Flash-Lite | `mechanism` | Config file omits `reasoning_effort`; adapter applies it anyway. **Uncertain** whether 3.1 Lite supports or ignores this parameter. Smoke passed, so not proven incompatible. |
| Explicit `reasoning_effort` only on 3 Flash config | `open` | Cross-variant comparability unclear without run artifacts recording effective kwargs. |
| No `max_tokens` on either Gemini config | `stale_check` | Relies on provider defaults. Acceptable for recorded 1-record smokes; **uncertain** for long ExECT multistage outputs. |
| `timeout_seconds=60` | `operational` | May be tight for ChainOfThought or multistage programs on long clinical notes. Skill flags timeout risk (`SKILL.md` L29). |
| `build_chat_adapter` ignores `reasoning_effort` | `mechanism` | Latent if chat adapter becomes production path. |

---

### Hosted OpenAI configs

| Config | Model | `temperature` | `max_tokens` | `timeout_s` |
|--------|-------|---------------|--------------|-------------|
| `gan_s0_gpt4_1_mini.json` | `gpt-4.1-mini` | 0.0 | *(unset)* | 60 |
| `gan_s0_gpt5_5_openai.json` | `gpt-5.5` | `null` | *(unset)* | 90 |

**Facts — OpenAI-specific:**

- GPT-5.5 rejected `temperature=0`; config now uses `"temperature": null` (`model_config_smoke_tests.md` L67–69).
- `LLMProviderConfig` rejects OpenAI `gpt-5*` with `temperature=0.0` (`llms.py` L50–55; `tests/test_llm_adapters.py` L84–86).
- Adapter omits `temperature` from payload when null (`llms.py` L151–152, L293–294; `tests/test_llm_adapters.py` L212–230).
- Both smokes completed (`model_config_smoke_tests.md` L53–54).
- `build_dspy_lm` OpenAI path does not map `reasoning_effort` or `extra_body` (`llms.py` L287–299).
- GEPA reflection preserves null temperature: `gepa_reflection_config()` returns base unchanged when `temperature is None` (`runner.py` L305–309).

**Gaps / risks (OpenAI):**

| Gap | Scope | Notes |
|-----|-------|-------|
| No `max_tokens` on either config | `stale_check` | Output budget unknown until run artifacts record truncation/schema failures. |
| `reasoning_effort` / `extra_body` silently ignored on OpenAI DSPy path | `open` | Cannot express future GPT-5-family reasoning parameters via model config today. |
| GPT-4.1-mini `timeout_seconds=60` | `operational` | May be low for optimizer or multistage runs. |

---

### Hosted Anthropic config

| Config | Model | `temperature` | `max_tokens` | `timeout_s` | `extra_body` |
|--------|-------|---------------|--------------|-------------|--------------|
| `gan_s0_claude_sonnet_4_6_anthropic.json` | `claude-sonnet-4-6` | 0.0 | 8192 | 90 | *(none)* |

**Facts:**

- Smoke completed on Windows 2026-05-22 with standard artifacts (`model_config_smoke_tests.md` L52).
- `build_dspy_lm` passes `extra_body` nested; config does not set extended-thinking controls (`llms.py` L256–268).
- Unit test shows chat adapter *can* send `thinking: {"type": "disabled"}` via `extra_body` (`tests/test_llm_adapters.py` L233–251), but production config does not.

**Gaps / risks (Anthropic):**

| Gap | Scope | Notes |
|-----|-------|-------|
| Extended thinking not explicitly disabled | `open` | **Uncertain** default for Sonnet 4.6 via LiteLLM; may affect latency/cost comparability. |
| `max_tokens=8192` | `stale_check` | Explicit budget; **uncertain** sufficiency for longest ExECT multistage outputs. |

---

### Cross-provider parameter matrix

| Parameter | Ollama (DSPy path) | Gemini | OpenAI | Anthropic |
|-----------|-------------------|--------|--------|-----------|
| `temperature=0.0` | All Qwen configs | Both Gemini configs | GPT-4.1-mini only | Claude config |
| `temperature=null` | N/A | N/A | GPT-5.5 (required for gpt-5*) | N/A |
| `reasoning_effort` | N/A (uses `think:False`) | 3 Flash: explicit; 3.1 Lite: injected by code | Not wired in `build_dspy_lm` | Not wired |
| `max_tokens` | 256–81920 (varies) | Unset (provider default) | Unset | 8192 |
| `num_ctx` / context | Only when `max_tokens>4096` or in ExECT/max configs | N/A | N/A | N/A |
| `timeout_seconds` | 600–1800 | 60 | 60–90 | 90 |
| `num_retries` | 0 (all Qwen) | 3 (default) | 3 (default) | 3 (default) |
| Structured JSON schema (chat adapter) | Would use strict `json_schema` if invoked (`llms.py` L156–164) | Same | Same | Same |

**Interpretation (scope: `arm`):** Hosted and local configs are not directly comparable on token budget, retry policy, or timeout without experiment metadata recording effective LM kwargs and per-record latency.

---

## Draft Adapter Wrapper/Interface Proposals

These are **draft recommendations only** — not implemented. They aim to centralize provider mapping in `clinical_extraction.llms` without touching scorer semantics or experiment logic.

### 1. Shared provider-kwargs builder (mechanism parity)

**Problem:** `build_dspy_lm` and `build_chat_adapter` apply different semantics for the same `LLMProviderConfig` (`llms.py`).

**Draft interface:**

```python
# Draft — not in repo
from dataclasses import dataclass
from typing import Any, Literal

AdapterKind = Literal["dspy", "chat_openai_compat"]

@dataclass(frozen=True)
class ResolvedProviderKwargs:
    provider: str
    model: str
    base_url: str | None
    api_key: str | None
    timeout_seconds: float
    temperature: float | None
    max_tokens: int | None
    num_retries: int
    # Provider-specific payload fragments
    dspy_model: str
    dspy_kwargs: dict[str, Any]
    chat_payload_extras: dict[str, Any]

def resolve_provider_kwargs(
    config: LLMProviderConfig,
    *,
    kind: AdapterKind,
) -> ResolvedProviderKwargs:
    """Single source of truth for provider-specific parameter mapping."""
    ...
```

**Draft mapping rules:**

```python
# Ollama — DSPy path only
if config.provider == "ollama" and kind == "dspy":
    extra_body = {"think": False, **config.extra_body}
    return {
        "dspy_model": f"ollama_chat/{config.model}",
        "dspy_kwargs": {
            "api_base": (config.base_url or "http://localhost:11434/v1").removesuffix("/v1"),
            "extra_body": extra_body,
            ...
        },
    }

# Gemini — tighten reasoning_effort default
if config.provider == "gemini":
    reasoning = config.reasoning_effort
    if reasoning is None and config.model.startswith("gemini-3-flash"):
        reasoning = "minimal"  # draft: avoid substring match on gemini-3.1-*
    ...

# Anthropic — optional thinking disable via config, not hardcoded
if config.provider == "anthropic" and kind == "dspy":
    extra = dict(config.extra_body)
    # draft: only if experiment policy requires comparability
    # extra.setdefault("thinking", {"type": "disabled"})
    dspy_kwargs["extra_body"] = extra
```

---

### 2. Gemini reasoning-effort guard (config vs. code mismatch)

**Problem:** `"gemini-3" in config.model` matches `gemini-3.1-flash-lite` (`llms.py` L248).

**Draft config recommendation** (choose one policy explicitly):

```json
// Option A: opt-in reasoning on 3 Flash only (config documents intent)
{
  "provider": "gemini",
  "model": "gemini-3-flash-preview",
  "reasoning_effort": "minimal"
}

// Option B: 3.1 Lite explicitly opts out once adapter supports it
{
  "provider": "gemini",
  "model": "gemini-3.1-flash-lite",
  "reasoning_effort": null
}
```

**Draft adapter logic** (safer than substring):

```python
_GEMINI_REASONING_DEFAULT_MODELS = frozenset({
    "gemini-3-flash-preview",
    # extend only with provider-documented ids
})

def _resolve_gemini_reasoning_effort(config: LLMProviderConfig) -> str | None:
    if config.reasoning_effort is not None:
        return config.reasoning_effort
    if config.model in _GEMINI_REASONING_DEFAULT_MODELS:
        return "minimal"
    return None
```

**Uncertainty:** Whether 3.1 Lite should receive `reasoning_effort` at all requires provider/LiteLLM documentation not read in this scan.

---

### 3. Ollama chat-adapter safety wrapper (non-production path)

**Problem:** `build_chat_adapter` for Ollama does not inject `think: False` (`llms.py` L192–201), unlike `build_dspy_lm` (L272–279).

**Draft wrapper** if chat adapter is used for probes/smokes:

```python
def build_chat_adapter(config: LLMProviderConfig) -> ChatAdapter:
    extra_body = dict(config.extra_body)
    if config.provider == "ollama":
        # Mirror DSPy path: disable hidden reasoning on OpenAI-compat route
        extra_body = {"think": False, **extra_body}
        # Draft: avoid strict json_schema on Ollama unless probed
        ...
    return OpenAICompatibleChatAdapter(..., extra_body=extra_body)
```

**Scope:** `mechanism` — relevant only if `build_chat_adapter` becomes a production or smoke path.

---

### 4. Structured-output capability probe (startup, optional)

**Problem:** `OpenAICompatibleChatAdapter.complete_json` always sends strict `response_format` JSON schema (`llms.py` L156–164). Ollama OpenAI-compat support for this is **uncertain** and not used on the experiment hot path today.

**Draft opt-in probe** (run at experiment startup, not import time):

```python
def probe_structured_output(adapter: ChatAdapter, schema: dict[str, Any]) -> bool:
    try:
        adapter.complete_json(
            [ChatMessage(role="user", content='Return {"ok": true} as JSON.')],
            response_schema=schema,
        )
        return True
    except RuntimeError:
        return False
```

Record result in run metadata; do not change scorer semantics based on probe alone.

---

### 5. Runtime environment preflight (operational)

**Problem:** Hosted configs declare `api_key_env` but validation does not fail early when the env var is absent (`llms.py` L218–221; configs e.g. `gan_s0_claude_sonnet_4_6_anthropic.json`).

**Draft preflight** (called from `runner.py` before live runs only):

```python
def validate_runtime_environment(config: LLMProviderConfig, *, env: os._Environ) -> list[str]:
    warnings: list[str] = []
    if config.provider in {"openai", "gemini", "anthropic"}:
        if config.api_key_env and not env.get(config.api_key_env):
            warnings.append(f"Missing API key env var: {config.api_key_env}")
    if config.provider == "ollama":
        # draft: optional HTTP GET to base_url/models or `ollama list` subprocess
        ...
    return warnings
```

---

## Recommended Parameter Validations

Rules to check at **config load** (always) vs. **run startup** (live runs only). Draft only — not implemented.

### A. Config-load validations (extend `LLMProviderConfig.validate_provider_config`)

| Rule | Rationale | Source |
|------|-----------|--------|
| Reject non-empty model string | Already enforced | `llms.py` L46–47 |
| Mock provider requires `mock_responses` | Already enforced | `llms.py` L48–49 |
| OpenAI `gpt-5*`: `temperature` must be `null`, not `0.0` | GPT-5.5 rejects zero temperature | `llms.py` L50–55; `model_config_smoke_tests.md` L67–69 |
| Ollama: `max_tokens > 4096` requires `extra_body.options.num_ctx` | Prevents silent default-context truncation | `llms.py` L56–62 |
| **Draft:** Ollama: if `max_tokens >= 4096` and no `num_ctx`, warn or require explicit `num_ctx` | Verify-repair config sits at boundary without `num_ctx` | `gan_s0_qwen35b_ollama_verify_repair.json`; `qwen_dspy_latency_policy.md` L14–16 |
| **Draft:** Ollama: if `extra_body.options.num_ctx >= 131072` and `timeout_seconds < 1800`, warn | 262144 ctx timed out on 27b ExECT smoke | `model_config_smoke_tests.md` L58 |
| **Draft:** `openai_compatible` requires `base_url` | Already enforced in `_default_base_url` | `llms.py` L213–214 |
| **Draft:** Reject unknown `provider` values | Already enforced at runtime | `llms.py` L215 |

### B. Run-startup validations (live runs / dry-run with `--check-live`)

| Rule | Rationale | Scope |
|------|-----------|-------|
| Hosted providers: `api_key_env` must be set (or inline `api_key` present) | Fail fast before first prediction | `operational` |
| Ollama: optional reachability check to `base_url` | Avoid long hangs on dead daemon | `operational` |
| Ollama: warn if requested model tag not in `ollama list` | 35b smoke blocked on Mac for missing tag | `blocked` / `model_config_smoke_tests.md` L57 |
| Log **effective** `build_dspy_lm` kwargs (model string, temperature, max_tokens, reasoning_effort, num_ctx, think) into run metadata | Cross-provider comparability | `arm` |
| **Draft:** Warn when `num_retries=0` on local configs vs. default `3` on hosted | Asymmetric failure recovery | `operational` |
| **Draft:** Warn when hosted config omits `max_tokens` for multistage/CoT program variants | Truncation risk unknown | `stale_check` |

### C. Provider-specific parameter allowlists (draft)

```python
# Draft validation helpers — not in repo
PROVIDER_FORBIDDEN_FIELDS = {
    "ollama": {"reasoning_effort"},
    "openai": {"reasoning_effort"},  # until wired in build_dspy_lm
}

PROVIDER_WARN_IF_PRESENT = {
    "gemini": {
        # keys merged flat via kwargs.update — typos silently pass through
        "extra_body": "Gemini build_dspy_lm flattens extra_body; prefer top-level LiteLLM kwargs",
    },
}

GEMINI_REASONING_EFFORT_ALLOWLIST = {"minimal", "low", "medium", "high"}  # verify against LiteLLM docs before enforcing

def validate_no_forbidden_fields(config: LLMProviderConfig) -> list[str]:
    warnings = []
    forbidden = PROVIDER_FORBIDDEN_FIELDS.get(config.provider, set())
    for field in forbidden:
        if getattr(config, field, None) is not None:
            warnings.append(f"{config.provider}: field {field!r} is set but not wired in build_dspy_lm")
    return warnings
```

**Uncertainty:** Gemini `reasoning_effort` allowlist should not be enforced without LiteLLM/provider documentation (prior backlog marked this `stale_check`; `docs/policies/model_config_compatibility_backlog_20260524.md` L140–142).

### D. Pre-run smoke gate (operational)

Before changing model configs or running hosted/Ollama smokes, the repo already recommends:

```powershell
uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py
```

(`docs/policies/model_config_smoke_tests.md` L77–78; `docs/policies/model_config_compatibility_backlog_20260524.md` L147–151)

**Draft addition:** add a parametrized test that calls `build_dspy_lm` (not just `build_chat_adapter`) for each `configs/models/*.json` file and asserts expected kwargs fragments (`think: False` for Ollama, `reasoning_effort` presence/absence for Gemini variants). This closes the mechanism gap identified in `tests/test_model_comparison_configs.py` L43–54.

---

## Summary by decision scope

| Scope | Top items |
|-------|-----------|
| `mechanism` | `build_dspy_lm` vs. `build_chat_adapter` divergence; Gemini substring `reasoning_effort` injection on 3.1 Lite; Ollama `think: False` only on DSPy path |
| `operational` | High-ctx Ollama timeout pairing; low `max_tokens` on Gan smokes; missing API-key preflight; hosted 60 s timeouts |
| `arm` | Incomparable token/retry/timeout defaults across providers without run metadata |
| `open` | Anthropic extended-thinking default; Gemini 3.1 `reasoning_effort` support; OpenAI `extra_body`/`reasoning_effort` wiring |
| `blocked` | `gan_s0_qwen35b_ollama.json` smoke deferred where Ollama tag missing |
| `stale_check` | Hosted `max_tokens` defaults for long ExECT/multistage runs; Ollama chat-adapter JSON-schema support |

**Residual risk:** Config JSON validates and resolves to adapters in unit tests, but production compatibility is determined by `build_dspy_lm` + LiteLLM + provider behavior at runtime. Treat smoke run IDs in `docs/policies/model_config_smoke_tests.md` as the primary compatibility evidence; this report is a review lead only.