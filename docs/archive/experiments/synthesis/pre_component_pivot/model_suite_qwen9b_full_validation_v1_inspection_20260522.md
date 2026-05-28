# Model Suite Qwen 3.5:9b Full Validation v1 — Inspection

Date: 2026-05-22  
Comparison group: `model_suite_frozen_architecture_v1`  
Preregistration: `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md`  
Ladder log: `runs/overnight_logs/qwen9b_model_suite_ladder_20260522_190404.log`

## Purpose

Confirmatory model-comparison replay of frozen ExECT S1/S4 + Gan S0 F0 on **Qwen3.5:9b** (local latency-floor track). `decision_scope: arm` only.

## Run artifacts

| Surface | Run ID suffix | Records | Outcome |
| --- | --- | ---: | --- |
| ExECT S1 | `…180406Z` | 40 | **Pass** — micro **79.4%**, evidence **89.7%** |
| ExECT S4 | `…190626Z` | 40 | **Pass** — micro **64.0%**, evidence **89.4%** |
| Gan S0 F0 | `…201156Z` | 299 | **Pass** — monthly **65.9%**, schema **92.3%**, evidence **100%** |

Queue: **3/3 succeeded**, 0 failed (`…214839Z` queue complete).

## Results vs anchors

| Surface | GPT 4.1-mini | Qwen 3.6:35b | Qwen 3.5:9b | Read |
| --- | ---: | ---: | ---: | --- |
| ExECT S1 micro | 92.3% | 79.0% | **79.4%** | Matches 35b; ~13pp below GPT |
| ExECT S4 micro | 65.5% | 67.5% | **64.0%** | Slightly below GPT/35b |
| Gan F0 monthly | 68.1% | 64.4% | **65.9%** | Between GPT and 35b; schema **92.3%** (23 invalid / 299) |

## Runtime (local)

| Surface | s/record | Residency notes |
| --- | ---: | --- |
| S1 | ~93.4 | `exect_qwen9b_ollama`, `num_ctx=65536` |
| S4 | ~98.2 | Same; per-family breakdown in `metrics.json` |
| Gan F0 | ~7.4 | `gan_s0_qwen9b_ollama`; faster than 35b (~14.5 s/rec) on F0 |

## Interpretation

1. **9b column complete** for frozen-architecture suite surfaces — model-comparison evidence only; no operational promotion.
2. **Latency floor confirmed** on Gan F0 (~7 s/rec vs 35b ~14.5 s/rec) with modest monthly lift vs 35b (+1.5pp) at lower schema validity (92.3% vs 99.7%).
3. **ExECT evidence** ~90% on S1/S4 — report separately from micro F1; do not mechanism-close from 9b alone.
4. **Next local pull:** Qwen **27b** overnight ladder (`start_qwen27b_model_suite_ladder_detached.ps1`).

## Caveats

- Not published benchmark reproduction; same splits/scorers as prereg.
- Gan schema 92.3% — inspect `invalid_predictions` in `…201156Z/errors.json` before cross-model Gan claims.
- S4 requires per-family F1 for interpretation; pooled micro alone insufficient.
