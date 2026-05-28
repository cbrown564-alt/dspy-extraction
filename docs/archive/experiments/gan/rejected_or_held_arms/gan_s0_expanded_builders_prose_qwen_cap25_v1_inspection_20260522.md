# Gan S0 Expanded Builders Prose Qwen Cap-25 v1 — Inspection

Date: 2026-05-22  
Preregistration: `docs/experiments/gan/gan_s0_expanded_builders_prose_qwen_full_validation_v1_preregistration_20260521.md`  
Comparison group: `gan_s0_expanded_builders_prose_model_comparison_v1`

## Purpose

Cap-25 gate for **Qwen3.6:35b** on the frozen Gan S0 **F0** skeleton (`cand_prose_expanded_builders_v1`, `g2_candidates_adjudicate`) before full-validation model comparison against GPT and Gemini F0 ports.

## Run artifacts

| Run | Run ID suffix | Records | Notes |
| --- | --- | ---: | --- |
| Primary (fresh inference) | **`…091442Z`** | 25 | `qwen3.6:35b` loaded; ~72%/28% CPU/GPU after run |
| Duplicate replay | `…104242Z` | 25 | ~8s total; DSPy cache replay; same metrics as primary |

**Config:** `configs/experiments/gan_s0_expanded_builders_prose_cap25_qwen35b_ollama.json`  
**Model:** `configs/models/gan_s0_qwen35b_ollama.json`

## Cap-25 results (canonical: `…091442Z`)

| Metric | Value |
| --- | ---: |
| Monthly frequency accuracy | **48.0%** |
| Purist category accuracy | 60.0% |
| Pragmatic category accuracy | 72.0% |
| Normalized-label exact | 40.0% |
| Schema validity | **100%** |
| Evidence quote support | **100%** |
| Valid predictions | 25/25 |

## F0 anchors (full validation, same skeleton)

| Provider | Run suffix | Monthly |
| --- | --- | ---: |
| GPT 4.1-mini | `…073432Z` | 68.1% |
| Gemini 3.1 Flash-Lite | `…094020Z` | 72.6% |
| Gemini 3 Flash | `…111541Z` | 75.3% |
| Claude Sonnet 4.6 | `…095634Z` | 73.0% |
| GPT 5.5 | `…121010Z` | 74.9% |

**Not comparable:** Qwen g2 cap-25 pre-expansion builders (`gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_20260521T065534Z`, **40.0%** monthly, reject arm).

## Contract gates (prereg)

| Gate | Threshold | Result |
| --- | --- | --- |
| Schema validity | ≥ 90% | **Pass** — 100% |
| Evidence support | ≥ 85% | **Pass** — 100% |
| Valid predictions | 25/25 | **Pass** |

**Outcome: hold (arm) — cap-25 gates cleared; full validation done (`…131822Z`, 64.4% monthly).**

Monthly accuracy on cap-25 is diagnostic only; do not treat 48.0% as a full-validation claim. Expanded builders lifted cap-25 monthly **+8.0pp** vs pre-expansion g2 cap-25 (40.0%) but remain below hosted F0 full anchors.

## Interpretation

1. **Gates pass.** Schema and evidence meet prereg thresholds; proceed to `gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama.json` via detached launcher.

2. **Model-comparison only** (`decision_scope: arm`). Do not promote Qwen to operational default or mechanism-close hybrid placement from this cap-25 slice.

3. **Cache caveat on duplicate.** The `…104242Z` replay completed in ~8s with identical metrics; use `…091442Z` for residency and latency interpretation unless a fresh no-cache rerun is required.

## Next step

- **Full validation:** **Done** — `runs/gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama_20260522T131822Z` (64.4% monthly, 99.7% schema, 100% evidence)
- Next local scaling: Qwen **9b** model-suite ladder, then Qwen **27b** overnight
