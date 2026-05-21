# Gan S0 Expanded Builders Prose Gemini Full Validation v1 — Inspection

Date: 2026-05-21  
Comparison group: `gan_s0_expanded_builders_prose_model_comparison_v1`  
Parent: `docs/experiments/exect/exect_gemini_ladder_replay_v1_inspection_20260521.md` (optional Gan F0 step)  
GPT F0 prereg: `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_preregistration_20260521.md`

## Purpose

Port **Gemini 3.1 Flash-Lite** onto the frozen Gan S0 **F0** skeleton (`cand_prose_expanded_builders_v1`, `g2_candidates_adjudicate`) for a **two-provider model-comparison table** against the GPT F0 monthly leader. No Qwen F0 port exists.

## Run artifacts

| Arm | Run ID suffix | Records | Config |
| --- | --- | ---: | --- |
| Smoke | `…094009Z` | 3 | `gan_s0_expanded_builders_prose_smoke_gemini31_flash_lite.json` |
| **F0 full** | **`…094020Z`** | 299 | `gan_s0_expanded_builders_prose_full_validation_gemini31_flash_lite.json` |

**Model:** `configs/models/gan_s0_gemini31_flash_lite.json`  
**Program:** `gan_frequency_s0_temporal_candidates_single_pass` + expanded builders (identical to GPT F0)

## Three-provider table (F0 skeleton, full validation)

| Provider | Run | Monthly | Purist | Pragmatic | Norm exact | Schema | Evidence | s/rec |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Gemini** | `…094020Z` | **72.6%** | **78.3%** | **84.6%** | **61.2%** | **100%** | **100%** | **0.66** |
| GPT 4.1-mini | `…073432Z` | 68.1% | 75.5% | 81.5% | 56.0% | 99.7% | 100% | 0.91 |
| Qwen3.6:35b | — | *no F0 port* | — | — | — | — | — | — |

**External references (different architecture — not F0-comparable):**

| Reference | Monthly | Notes |
| --- | ---: | --- |
| GPT VR engineering baseline | 65.1% | `g3_candidates_extract_repair`; two LLM calls |
| Stale Gemini direct full | 63.9% | Pre-F0 direct path; evidence 84.9% |

**Monthly delta (Gemini F0 − GPT F0):** **+4.5pp** (217/299 vs 203/298 correct).  
95% CI on Gemini monthly: 67.9–77.3% (bootstrap in metrics JSON).

## Contract gates

| Gate | Result |
| --- | --- |
| Smoke (3 records) | Pass — 100% schema, 100% evidence |
| Full 299/299 predictions | Pass |
| Schema validity ≥ 95% | Pass — **100%** (0 invalid; GPT had 1 shared `gan_338` failure) |
| Evidence support ≥ 95% | Pass — **100%** |
| Same F0 skeleton as GPT | Pass — only `model_track` differs |

## Interpretation

1. **Gemini beats GPT on the same F0 program** across all reported label metrics (+4.5pp monthly, +5.2pp normalized exact, +2.8pp Purist, +3.1pp Pragmatic) with perfect schema and evidence on this run.

2. **Evidence gap from stale Gan direct does not transfer.** Prior Gemini direct full validation showed 84.9% evidence; on F0 adjudication with expanded builders, evidence is **100%** — the earlier gap was architecture/path-specific, not a fixed Gemini weakness on Gan.

3. **Latency favorable.** ~0.66 s/rec (~3.3 min total) vs GPT F0 ~0.91 s/rec (~4.5 min).

4. **Not an operational swap by default.** GPT F0 remains the frozen reproducibility anchor for the repo; this is **model-comparison evidence** (`decision_scope: arm`). Promoting Gemini would require explicit operational decision, billing review, and cross-dataset confirmation (ExECT S1 was −2.0pp vs GPT).

5. **Qwen column absent.** A true three-provider table needs a separate Qwen F0 port prereg if required for the paper.

## Taxonomy

| Field | Value |
| --- | --- |
| varied_factor | `model_track` = gemini |
| comparison_group | `gan_s0_expanded_builders_prose_model_comparison_v1` |
| outcome | **hold** (model-comparison; strong Gan F0 signal) |
| mechanism closure | No |

## Decision

**Hold** as model-comparison evidence with **notable Gan F0 win vs GPT**. Record for paper table; do not mechanism-close det-candidate generation or change frozen GPT operational defaults without separate promotion review.

## Validation

- `uv run --extra dev pytest tests/test_experiment_configs.py -k "expanded_builders_prose and gemini"`
- Smoke + full validation executed 2026-05-21
