# Model Suite Gemini 3 Flash Full Validation v1 — Inspection

Date: 2026-05-22  
Comparison group: `model_suite_frozen_architecture_v1`  
Preregistration: `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md`  
decision_scope: **arm** (model-comparison evidence only; not mechanism closure)

## Purpose

Complete the Gemini 3 Flash column on the three frozen comparison surfaces (ExECT S1, ExECT S4, Gan S0 F0) after provider smokes passed on 2026-05-22.

## Run artifacts

| Arm | Run ID suffix | Records | Config |
| --- | --- | ---: | --- |
| S1 smoke | `…104250Z` | 3 | `exect_s0_s1_smoke_gemini3_flash.json` |
| S4 smoke | `…105207Z` | 3 | `exect_s4_smoke_gemini3_flash.json` |
| Gan F0 smoke | `…111105Z` | 3 | `gan_s0_expanded_builders_prose_smoke_gemini3_flash.json` |
| **S1 full** | **`…111119Z`** | 40 | `exect_s0_s1_validation_full_gemini3_flash.json` |
| **S4 full** | **`…111330Z`** | 40 | `exect_s4_validation_full_gemini3_flash.json` |
| **Gan F0 full** | **`…111541Z`** | 299 | `gan_s0_expanded_builders_prose_full_validation_gemini3_flash.json` |

**Model:** `configs/models/gan_s0_gemini3_flash.json` (`gemini-3-flash-preview`)  
**Scorer / split:** unchanged from GPT/Gemini 3.1/Claude/Qwen anchors

## S1 full validation (40 records)

| Metric | Gemini 3 Flash | GPT anchor | Gemini 3.1 anchor | Claude anchor | Qwen anchor | Δ Flash−GPT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Micro F1 | **89.9%** | 92.3% | 90.3% | 81.8% | 79.0% | **−2.4pp** |
| diagnosis F1 | 95.0% | 93.8% | 92.3% | 92.5% | — | +1.2pp |
| seizure_type F1 | 80.8% | 90.5% | 85.7% | 66.0% | — | **−9.7pp** |
| annotated_medication F1 | 94.9% | 92.8% | 93.5% | 90.1% | — | +2.1pp |
| Evidence quote support | **100.0%** | — | 100.0% | 97.6% | — | — |
| Runtime | ~77 s (**1.9 s/rec**) | — | ~1.3 s/rec | ~13.4 s/rec | — | — |
| Tokens (total) | 83,743 | — | — | 113,970 | — | — |

**Read:** Gemini 3 Flash is **near Gemini 3.1 (−0.4pp)** and **within 2.4pp of GPT** on pooled micro. Seizure_type remains the main gap vs GPT (−9.7pp); medication is slightly ahead. Evidence support is perfect on this run.

## S4 full validation (40 records)

| Metric | Gemini 3 Flash | GPT anchor | Gemini 3.1 anchor | Claude anchor | Qwen anchor* | Δ Flash−GPT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Micro F1 (11 fam) | **63.2%** | 65.5% | 66.8% | 65.1% | 67.5% | **−2.3pp** |
| diagnosis F1 | 92.5% | 91.1% | 90.0% | 78.9% | 88.3% | +1.4pp |
| seizure_type F1 | 73.0% | 84.0% | 82.8% | 75.4% | 76.3% | −11.0pp |
| annotated_medication F1 | 70.7% | 71.3% | 72.3% | 84.4% | 80.4% | −0.6pp |
| investigation F1 | 94.9% | 96.7% | 96.7% | 91.5% | 94.7% | −1.8pp |
| comorbidity F1 | 56.4% | 59.8% | 62.6% | 62.6% | 64.0% | −3.4pp |
| epilepsy_cause F1 | 20.0% | 10.5% | 22.2% | 18.2% | 19.0% | +9.5pp |
| seizure_frequency F1 | 49.4% | 45.7% | 51.2% | 47.3% | 50.0% | +3.7pp |
| medication_temporality F1 | 56.2% | 62.5% | 59.2% | 62.0% | 69.3% | −6.3pp |
| Evidence quote support | **98.9%** | 87.7% | 99.5% | 93.0% | 93.4% | +11.2pp |
| Runtime | ~128 s (**3.2 s/rec**) | — | ~2.0 s/rec | ~19.5 s/rec | — | — |
| Tokens (total) | 142,392 | — | — | 170,018 | — | — |

\*Qwen S4 anchor used pre-bridge L1 variant; Gemini 3 Flash uses frozen K0+K1 path for GPT parity.

**Read:** Pooled micro F1 **lags all suite anchors (−1.9pp to −4.3pp)**. The deficit is **precision-driven** (53.0% micro precision vs 78.2% recall): annotated_medication and medication_temporality show high recall with many false positives. Do not rank from pooled micro alone; per-family profile diverges from Gemini 3.1 (which led GPT on S4).

## Gan F0 full validation (299 records)

| Provider | Run | Monthly | Purist | Pragmatic | Norm exact | Schema | Evidence | s/rec |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Gemini 3 Flash** | `…111541Z` | **75.3%** | **81.3%** | **86.3%** | **66.2%** | **100%** | **100%** | **1.18** |
| Claude | `…095634Z` | 73.0% | 79.5% | 85.7% | 61.8% | 98.0% | 99.3% | 5.04 |
| Gemini 3.1 | `…094020Z` | 72.6% | 78.3% | 84.6% | 61.2% | 100% | 100% | 0.66 |
| GPT 4.1-mini | `…073432Z` | 68.1% | 75.5% | 81.5% | 56.0% | 99.7% | 100% | 0.91 |

**Monthly delta (Gemini 3 Flash F0 − GPT F0):** **+7.2pp** (225/299 vs 203/298).  
**Monthly delta (Flash − Gemini 3.1):** **+2.7pp**.  
**Monthly delta (Flash − Claude):** **+2.3pp**.  
95% CI on Flash monthly: 70.6–79.9% (bootstrap in metrics JSON).

**Read:** Gemini 3 Flash is **strongest hosted track on Gan F0 monthly** in this suite — ahead of Gemini 3.1, Claude, and GPT — with perfect schema and evidence. Latency (~1.2 s/rec) is between Gemini 3.1 (~0.66 s/rec) and GPT (~0.91 s/rec).

## Contract gates

| Gate | S1 | S4 | Gan F0 |
| --- | --- | --- | --- |
| Smoke before full | Pass | Pass | Pass |
| Full predictions + scorer | 40/40 | 40/40 | 299/299 |
| Invalid runtime failures | 0 | 0 | 0 |
| Schema validity | N/A | N/A | **100%** |
| Evidence support | 100.0% | 98.9% | 100.0% |

## Taxonomy

| Field | Value |
| --- | --- |
| varied_factor | `model_track` = gemini3flash |
| comparison_group | `model_suite_frozen_architecture_v1` |
| outcome | **hold** (model-comparison evidence) |
| mechanism closure | No |
| operational promotion | No |

## Decision

**Hold** as model-comparison evidence:

1. **S1:** Gemini 3 Flash is a **credible hosted track** — near Gemini 3.1 (−0.4pp) and within 2.4pp of GPT; seizure_type is the main residual vs GPT.
2. **S4:** Gemini 3 Flash **underperforms suite anchors on pooled micro** (−2.3pp vs GPT) with a **precision-heavy FP profile** on medication families. Unlike Gemini 3.1 on the same architecture, Flash does not exceed GPT here. Report per-family; do not collapse to pooled ranking.
3. **Gan F0:** Gemini 3 Flash **leads the suite on monthly** (+7.2pp vs GPT, +2.7pp vs Gemini 3.1) with **100% schema and evidence**. Model-comparison hold only — no operational promotion from suite results alone.
4. **Cross-surface read:** Flash is **not uniformly interchangeable with Gemini 3.1** — S4 divergence suggests model-id/provider behavior differs even on frozen programs.

## Next steps

- Update `docs/planning/kanban_plan.md` coverage matrix (Gemini 3 Flash column complete).
- Proceed with **GPT 5.5** frozen full replay (remaining hosted lane).
- Phase-5 synthesis: provider tables + ExECT model-profile memo with Flash vs 3.1 Flash-Lite split noted on S4.
