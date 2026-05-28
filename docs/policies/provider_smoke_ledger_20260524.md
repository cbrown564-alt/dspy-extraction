# Provider Smoke Ledger

Last updated: 2026-05-24  
Pathway: E3 — Provider smoke discipline  
decision_scope: operational (compatibility gate only; not performance evidence)

## Purpose

Before broad model comparisons or full-validation spend on a new provider/model track, record a **smoke ledger entry** with:

1. **Run ID** — canonical artifact directory under `runs/`
2. **Experiment config** — `configs/experiments/<smoke>.json`
3. **Model config** — `configs/models/<model>.json`
4. **Structured-output strategy** — from experiment config (typically `provider_json_schema_with_pydantic_validation`)
5. **Schema validity** — `diagnostic_metrics.schema_valid_prediction_rate` (Gan) or zero invalid predictions
6. **Evidence support** — `diagnostic_metrics.evidence_quote_support_rate`

Smokes validate **runtime compatibility and artifact contract only**. They are not performance estimates and must not be cited as benchmark results.

Companion policy: [model_config_smoke_tests.md](model_config_smoke_tests.md).  
Model-suite full validations gated by these smokes: [model_suite_frozen_architecture_v1_preregistration_20260522.md](../archive/experiments/synthesis/pre_component_pivot/model_suite_frozen_architecture_v1_preregistration_20260522.md).

## Gate Discipline

| Step | Requirement |
| --- | --- |
| 1 | `uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py tests/test_experiment_configs.py` (offline) |
| 2 | `uv run python scripts/run_experiment.py --experiment <smoke-config> --env-file .env --dry-run` |
| 3 | Execute smoke config (1-record legacy Gan and/or 3-record model-suite surfaces) |
| 4 | Confirm `metrics.json`, `predictions.json`, and `config.json` exist |
| 5 | Record ledger row below before scheduling full validation |

### Pass criteria (compatibility gate)

| Surface | Records | Pass when |
| --- | ---: | --- |
| Legacy Gan S0 | 1 | Run completes; `invalid_predictions == 0`; schema validity recorded |
| Model-suite Gan F0 | 3 | Run completes; schema ≥ 96%; evidence ≥ 96% |
| ExECT S1 / S4 | 3 | Run completes; evidence ≥ 90%; micro F1 recorded for context only |

**Partial pass:** runtime and artifacts OK but sample label/schema failure on 1-record Gan (document; do not treat as benchmark failure). Example: Gemini 3 Flash legacy Gan smoke predicted an unsupported label (`2 per 4 month`) — schema 0/1 but provider path works.

**Fail / incomplete:** no `metrics.json`, timeout, or adapter error — do not proceed to full validation.

## Canonical Ledger — Model-Suite Tracks (2026-05-24)

Structured output for all rows: `provider_json_schema_with_pydantic_validation`.

### GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`)

| Surface | Config | Canonical run ID | Rec | Schema | Evidence | Micro F1 | Gate |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Legacy Gan | `gan_s0_smoke_gpt4_1_mini.json` | `gan_s0_smoke_gpt4_1_mini_token_usage_smoke_20260519T000000Z` | 1 | 100% | 0%* | — | **Partial** |
| ExECT S1 | `exect_s0_s1_smoke_gpt4_1_mini.json` | `exect_s0_s1_smoke_gpt4_1_mini_20260518T160445Z` | 3 | — | 90.0% | 100.0% | Pass |
| ExECT S4 | `exect_s4_smoke_gpt4_1_mini.json` | `exect_s4_smoke_gpt4_1_mini_20260520T070529Z` | 3 | — | 93.5% | 59.3% | Pass |
| Gan F0 | — | — | — | — | — | — | Skipped† |

\* Token/residency plumbing run; evidence 0% on sampled record — runtime compatibility confirmed, not label quality.  
† GPT 4.1-mini anchor predates F0 smoke surface; full validation `gan_s0_expanded_builders_prose_full_validation_gpt4_1_mini_20260521T073432Z` serves as post-hoc gate.

### GPT 5.5 (`configs/models/gan_s0_gpt5_5_openai.json`)

| Surface | Config | Canonical run ID | Rec | Schema | Evidence | Gate |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Gan F0 | `gan_s0_expanded_builders_prose_smoke_gpt5_5_openai.json` | `gan_s0_expanded_builders_prose_smoke_gpt5_5_openai_20260522T113614Z` | 3 | 100% | 100% | Pass |
| ExECT S1 | `exect_s0_s1_smoke_gpt5_5_openai.json` | `exect_s0_s1_smoke_gpt5_5_openai_20260522T113436Z` | 3 | — | 100% | Pass |
| ExECT S4 | `exect_s4_smoke_gpt5_5_openai.json` | `exect_s4_smoke_gpt5_5_openai_20260522T113510Z` | 3 | — | 100% | Pass |

Inspection: [model_suite_gpt5_5_full_validation_v1_inspection_20260522.md](../archive/experiments/synthesis/pre_component_pivot/model_suite_gpt5_5_full_validation_v1_inspection_20260522.md).

### Gemini 3 Flash (`configs/models/gan_s0_gemini3_flash.json`, `gemini-3-flash-preview`)

| Surface | Config | Canonical run ID | Rec | Schema | Evidence | Gate |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Legacy Gan | `gan_s0_smoke_gemini3_flash.json` | `gan_s0_smoke_gemini3_flash_20260518T134109Z` | 1 | 0% | — | **Partial** |
| Gan F0 | `gan_s0_expanded_builders_prose_smoke_gemini3_flash.json` | `gan_s0_expanded_builders_prose_smoke_gemini3_flash_20260522T111105Z` | 3 | 100% | 100% | Pass |
| ExECT S1 | `exect_s0_s1_smoke_gemini3_flash.json` | `exect_s0_s1_smoke_gemini3_flash_20260522T104250Z` | 3 | — | 100% | Pass |
| ExECT S4 | `exect_s4_smoke_gemini3_flash.json` | `exect_s4_smoke_gemini3_flash_20260522T105207Z` | 3 | — | 100% | Pass |

Inspection: [model_suite_gemini3_flash_full_validation_v1_inspection_20260522.md](../archive/experiments/synthesis/pre_component_pivot/model_suite_gemini3_flash_full_validation_v1_inspection_20260522.md).

### Gemini 3.1 Flash-Lite (`configs/models/gan_s0_gemini31_flash_lite.json`, GA `gemini-3.1-flash-lite`)

| Surface | Config | Canonical run ID | Rec | Schema | Evidence | Gate |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Legacy Gan | `gan_s0_smoke_gemini31_flash_lite.json` | `gan_s0_smoke_gemini31_flash_lite_20260519T101222Z` | 1 | 100% | 100% | Pass |
| Gan F0 | `gan_s0_expanded_builders_prose_smoke_gemini31_flash_lite.json` | `gan_s0_expanded_builders_prose_smoke_gemini31_flash_lite_20260521T094009Z` | 3 | 100% | 100% | Pass |
| ExECT S1 | `exect_s0_s1_smoke_gemini31_flash_lite.json` | `exect_s0_s1_smoke_gemini31_flash_lite_20260521T093432Z` | 3 | — | 100% | Pass |
| ExECT S4 | `exect_s4_smoke_gemini31_flash_lite.json` | `exect_s4_smoke_gemini31_flash_lite_20260521T093445Z` | 3 | — | 100% | Pass |

### Claude Sonnet 4.6 (`configs/models/gan_s0_claude_sonnet_4_6_anthropic.json`)

| Surface | Config | Canonical run ID | Rec | Schema | Evidence | Gate |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Legacy Gan | `gan_s0_smoke_claude_sonnet_4_6_anthropic.json` | `gan_s0_smoke_claude_sonnet_4_6_anthropic_20260522T080515Z` | 1 | 100% | 100% | Pass |
| Gan F0 | `gan_s0_expanded_builders_prose_smoke_claude_sonnet_4_6_anthropic.json` | `gan_s0_expanded_builders_prose_smoke_claude_sonnet_4_6_anthropic_20260522T080527Z` | 3 | 100% | 100% | Pass |
| ExECT S1 | `exect_s0_s1_smoke_claude_sonnet_4_6_anthropic.json` | `exect_s0_s1_smoke_claude_sonnet_4_6_anthropic_20260522T080538Z` | 3 | — | 100% | Pass |
| ExECT S4 | `exect_s4_smoke_claude_sonnet_4_6_anthropic.json` | `exect_s4_smoke_claude_sonnet_4_6_anthropic_20260522T080625Z` | 3 | — | 96.4% | Pass |

Inspection: [model_suite_claude_sonnet_4_6_full_validation_v1_inspection_20260522.md](../archive/experiments/synthesis/pre_component_pivot/model_suite_claude_sonnet_4_6_full_validation_v1_inspection_20260522.md).

### Qwen3.6:27b (`configs/models/gan_s0_qwen27b_ollama.json`, `configs/models/exect_qwen27b_ollama.json`)

| Surface | Config | Canonical run ID | Rec | Schema | Evidence | Gate |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Gan F0 | `gan_s0_expanded_builders_prose_smoke_qwen27b_ollama.json` | `gan_s0_expanded_builders_prose_smoke_qwen27b_ollama_20260522T091754Z` | 3 | 100% | 100% | Pass |
| ExECT S1 | `exect_s0_s1_smoke_qwen27b_ollama.json` | `exect_s0_s1_smoke_qwen27b_ollama_20260522T095301Z` | 3 | — | 100% | Pass |
| ExECT S4 | `exect_s4_smoke_qwen27b_ollama.json` | `exect_s4_smoke_qwen27b_ollama_20260522T102006Z` | 3 | — | 100% | Pass |

Note: first S1 attempt at `num_ctx=262144` timed out; config now uses bounded `num_ctx=65536`.

### Qwen3.6:35b (`configs/models/gan_s0_qwen35b_ollama.json`, `configs/models/exect_qwen35b_ollama.json`)

| Surface | Config | Canonical run ID | Rec | Schema | Evidence | Gate |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Legacy Gan | `gan_s0_smoke_qwen35b_ollama.json` | — | — | — | — | **Incomplete** |
| Legacy Gan (direct) | `gan_s0_smoke_qwen35b_direct_ollama.json` | `gan_s0_smoke_qwen35b_direct_ollama_20260518T201840Z` | 1 | 100% | 100% | Pass |
| Gan F0 | `gan_s0_expanded_builders_prose_smoke_qwen35b_ollama.json` | `gan_s0_expanded_builders_prose_smoke_qwen35b_ollama_20260521T095443Z` | 3 | 100% | 100% | Pass |
| ExECT S1 | `exect_s0_s1_smoke_qwen35b_ollama.json` | `exect_s0_s1_smoke_qwen35b_ollama_20260520T001917Z` | 3 | — | 100% | Pass |
| ExECT S4 | `exect_s4_smoke_qwen35b_ollama.json` | `exect_s4_smoke_qwen35b_ollama_20260520T010617Z` | 3 | — | 96.3% | Pass |
| Builder-gap v1 | `gan_s0_candidate_builder_gap_v1_smoke_qwen35b_ollama.json` | `gan_s0_candidate_builder_gap_v1_smoke_qwen35b_ollama_20260523T215406Z` | 3 | 100% | 100% | Pass |

Legacy `gan_s0_smoke_qwen35b_ollama` runs (`…182354Z`, `…windows_202315Z`) stalled before `metrics.json`; use direct-path and F0 smokes as gate evidence.

### Qwen3.5:9b (`configs/models/gan_s0_qwen9b_ollama.json`)

| Surface | Config | Canonical run ID | Rec | Schema | Evidence | Gate |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Legacy Gan | `gan_s0_smoke_qwen9b_ollama.json` | `gan_s0_smoke_qwen9b_ollama_20260522T092032Z` | 1 | 100% | 100% | Pass |

Model-suite ExECT/Gan F0 smokes not required for 9b secondary track.

## Supplementary Ladder Smokes (GPT 4.1-mini / Qwen3.6:35b)

Recorded for operational ladder work; not model-suite comparison gates.

| Config | Run ID | Evidence | Notes |
| --- | --- | ---: | --- |
| `exect_s2_smoke_gpt4_1_mini.json` | `exect_s2_smoke_gpt4_1_mini_20260519T223951Z` | 87.5% | S2 compatibility |
| `exect_s3_smoke_gpt4_1_mini.json` | `exect_s3_smoke_gpt4_1_mini_20260519T233117Z` | 85.7% | S3 compatibility |
| `exect_s2_smoke_qwen35b_ollama.json` | `exect_s2_smoke_qwen35b_ollama_20260520T003342Z` | 100% | S2 compatibility |
| `exect_s3_smoke_qwen35b_ollama.json` | `exect_s3_smoke_qwen35b_ollama_20260520T005327Z` | 100% | S3 compatibility |

## Adding A New Entry

1. Add or confirm smoke config under `configs/experiments/*_smoke_*.json`.
2. Run dry-run then smoke; capture run ID.
3. Append a row to the provider section above with all six required fields.
4. Set gate status: Pass / Partial / Incomplete.
5. Cross-link any resulting full-validation inspection doc.
6. Do **not** compare smoke metrics across providers for ranking.

## Open Gaps

| Gap | Mitigation |
| --- | --- |
| GPT 4.1-mini Gan F0 3-record smoke never run | Full validation artifact cited; run F0 smoke before next new hosted track |
| Legacy Gan smokes with partial schema (Gemini 3 Flash) | Use 3-record F0 smoke as primary gate |
| Qwen3.6:35b legacy 1-record smoke incomplete on Windows | Direct-path + F0 smokes pass |
| B6 offline `build_dspy_lm` coverage for all model configs | Backlog in [model_config_smoke_tests.md](model_config_smoke_tests.md) |
