# ExECT Gemini Ladder Replay v1 — Inspection

Date: 2026-05-21  
Comparison group: `exect_gemini_ladder_replay_v1`  
Preregistration: `docs/experiments/exect/exect_gemini_ladder_replay_v1_preregistration_20260521.md`  
decision_scope: **arm** (model-comparison evidence only; not mechanism closure)

## Purpose

Replay Gemini 3.1 Flash-Lite under **today's** frozen ExECT S1/S4 field-family architecture to test whether prior Round-2 Gemini champion evidence still matters for model comparison.

## Run artifacts

| Arm | Run ID suffix | Records | Config |
| --- | --- | ---: | --- |
| S1 smoke | `…093432Z` | 3 | `exect_s0_s1_smoke_gemini31_flash_lite.json` |
| S4 smoke | `…093445Z` | 3 | `exect_s4_smoke_gemini31_flash_lite.json` |
| **S1 full** | **`…093501Z`** | 40 | `exect_s0_s1_validation_full_gemini31_flash_lite.json` |
| **S4 full** | **`…093556Z`** | 40 | `exect_s4_validation_full_gemini31_flash_lite.json` |

**Model:** `configs/models/gan_s0_gemini31_flash_lite.json` (`gemini-3.1-flash-lite`)  
**Scorer / split:** unchanged from GPT/Qwen anchors (`exectv2_fixed_v1:validation`)

## S1 full validation (40 records)

| Metric | Gemini | GPT anchor | Qwen anchor | Δ Gemini−GPT |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 | **90.3%** | 92.3% | 79.0% | −2.0pp |
| diagnosis F1 | 92.3% | 93.8% | — | −1.5pp |
| seizure_type F1 | 85.7% | 90.5% | — | −4.8pp |
| annotated_medication F1 | **93.5%** | 92.8% | — | +0.7pp |
| Evidence quote support | **100.0%** | — | — | — |
| Runtime | ~52 s (~1.3 s/rec) | — | — | — |

**Read:** Gemini trails GPT by 2.0pp pooled micro but remains **well above Qwen (+11.3pp)**. Seizure-type surface is the main S1 gap (−4.8pp vs GPT); medication slightly ahead. Evidence support is **100%** on this run — unlike Gan direct cap-25 where Gemini trailed on evidence (86.4%).

## S4 full validation (40 records)

| Metric | Gemini | GPT v1.2 | Qwen full* | Δ Gemini−GPT |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 (11 fam) | **66.8%** | 65.5% | 67.5% | **+1.3pp** |
| diagnosis F1 | 90.0% | 91.1% | 88.3% | −1.1pp |
| seizure_type F1 | 82.8% | 84.0% | 76.3% | −1.2pp |
| annotated_medication F1 | 72.3% | 71.3% | 80.4% | +1.0pp |
| investigation F1 | 96.7% | 96.7% | 94.7% | 0 |
| comorbidity F1 | 62.6% | 59.8% | 64.0% | +2.8pp |
| epilepsy_cause F1 | **22.2%** | 10.5% | 19.0% | +11.7pp |
| seizure_frequency F1 | **51.2%** | 45.7% | 50.0% | +5.5pp |
| medication_temporality F1 | 59.2% | 62.5% | 69.3% | −3.3pp |
| Evidence quote support | **99.5%** | 87.7% | 93.4% | +11.8pp |
| Runtime | ~79 s (~2.0 s/rec) | — | — | — |

\*Qwen S4 anchor used pre-bridge `exect_s4_field_family_single_pass`; Gemini uses frozen K0+K1 path for GPT parity.

**Read:** Pooled micro F1 **exceeds GPT by 1.3pp** with a **mixed family profile** — stronger on cause (+11.7pp), frequency (+5.5pp), and comorbidity; weaker on medication temporality (−3.3pp). Do not collapse to a single ranking without per-family caveats (same discipline as Qwen S4 read). Evidence support **beats both GPT and Qwen** on this architecture.

## Contract gates

| Gate | S1 | S4 |
| --- | --- | --- |
| 40/40 predictions + scorer | Pass | Pass |
| Provider smoke before full | Pass | Pass |
| Schema / normalization errors | 0 | 0 |

## Taxonomy

| Field | Value |
| --- | --- |
| varied_factor | `model_track` = gemini |
| comparison_group | `exect_gemini_ladder_replay_v1` |
| outcome | **hold** (model-comparison evidence) |
| mechanism closure | No |

## Decision

**Hold** as model-comparison evidence:

1. **S1:** Gemini is a credible hosted third track — near GPT (−2.0pp), well above Qwen; seizure-type gap is the main residual.
2. **S4:** Gemini matches/exceeds GPT pooled micro (+1.3pp) with better cause and frequency families; MT precision/recall tradeoff differs from GPT.
3. **Evidence:** ExECT Gemini does **not** replay the Gan-direct evidence gap; quote support is 99.5–100% on full validation.
4. **Not promoted** as operational default — GPT remains frozen anchor; this is arm-scoped comparison only.

**Do not:** mechanism-close hybrid placement from Gemini alone; compare to stale Round-2 `full_exect_gemini_combined_examples` without architecture caveat; treat Qwen S4 pooled micro as directly comparable (different program variant).

## Optional follow-up

- ~~Gan F0 expanded builders prose port~~ **Done** — `gan_s0_expanded_builders_prose_model_comparison_v1` (see Gan F0 inspection section).
- Billing/cost not measured in this session.

## Gan F0 expanded builders (optional step 4)

**Done** — `docs/experiments/gan/gan_s0_expanded_builders_prose_gemini_full_validation_v1_inspection_20260521.md`

| Provider | Gan F0 monthly (299) |
| --- | ---: |
| Gemini | **72.6%** (`…094020Z`) |
| GPT | 68.1% (`…073432Z`) |

Gemini **+4.5pp** vs GPT on identical F0 skeleton; 100% schema/evidence. Hold as model-comparison — not operational swap.

## Validation

- `uv run --extra dev pytest tests/test_experiment_configs.py -k gemini31_flash_lite`
- Dry-run + smoke + full validation configs executed 2026-05-21
