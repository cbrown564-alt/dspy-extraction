# Model Suite GPT 5.5 Full Validation v1 — Inspection

Date: 2026-05-22  
Comparison group: `model_suite_frozen_architecture_v1`  
Preregistration: `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md`  
decision_scope: **arm** (model-comparison evidence only; not mechanism closure)

## Purpose

Complete the GPT 5.5 column on the three frozen comparison surfaces (ExECT S1, ExECT S4, Gan S0 F0) after smokes passed (`…113436Z` / `…113510Z` / `…113614Z`).

## Run artifacts

| Arm | Run ID suffix | Records | Config |
| --- | --- | ---: | --- |
| S1 smoke | `…113436Z` | 3 | `exect_s0_s1_smoke_gpt5_5_openai.json` |
| S4 smoke | `…113510Z` | 3 | `exect_s4_smoke_gpt5_5_openai.json` |
| Gan F0 smoke | `…113614Z` | 3 | `gan_s0_expanded_builders_prose_smoke_gpt5_5_openai.json` |
| **S1 full** | **`…114349Z`** | 40 | `exect_s0_s1_validation_full_gpt5_5_openai.json` |
| **S4 full** | **`…115403Z`** | 40 | `exect_s4_validation_full_gpt5_5_openai.json` |
| **Gan F0 full** | **`…121010Z`** | 299 | `gan_s0_expanded_builders_prose_full_validation_gpt5_5_openai.json` |

**Model:** `configs/models/gan_s0_gpt5_5_openai.json` (`gpt-5.5`, `temperature: null`)  
**Scorer / split:** unchanged from suite anchors

## S1 full validation (40 records)

| Metric | GPT 5.5 | GPT anchor | Gemini 3 Flash | Gemini 3.1 | Claude | Δ 5.5−GPT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Micro F1 | **85.7%** | 92.3% | 89.9% | 90.3% | 81.8% | **−6.6pp** |
| diagnosis F1 | 93.7% | 93.8% | 95.0% | 92.3% | 92.5% | −0.1pp |
| seizure_type F1 | 73.5% | 90.5% | 80.8% | 85.7% | 66.0% | **−17.0pp** |
| annotated_medication F1 | 91.7% | 92.8% | 94.9% | 93.5% | 90.1% | −1.1pp |
| Evidence quote support | **99.2%** | — | 100.0% | 100.0% | 97.6% | — |
| Runtime | ~605 s (**15.1 s/rec**) | — | 1.9 s/rec | 1.3 s/rec | 13.4 s/rec | — |
| Tokens (total) | 100,143 | — | 83,743 | — | 113,970 | — |

**Read:** GPT 5.5 trails GPT anchor on pooled micro (−6.6pp), driven mainly by **seizure_type** (−17.0pp). Diagnosis and medication are near anchor. Evidence support is strong (99.2%). Latency is much slower than other hosted tracks on this surface.

## S4 full validation (40 records)

| Metric | GPT 5.5 | GPT anchor | Gemini 3 Flash | Gemini 3.1 | Claude | Δ 5.5−GPT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Micro F1 (11 fam) | **68.7%** | 65.5% | 63.2% | 66.8% | 65.1% | **+3.2pp** |
| diagnosis F1 | 93.8% | 91.1% | 92.5% | 90.0% | 78.9% | +2.7pp |
| seizure_type F1 | 76.1% | 84.0% | 73.0% | 82.8% | 75.4% | −7.9pp |
| annotated_medication F1 | 81.7% | 71.3% | 70.7% | 72.3% | 84.4% | +10.4pp |
| investigation F1 | 91.5% | 96.7% | 94.9% | 96.7% | 91.5% | −5.2pp |
| comorbidity F1 | 58.7% | 59.8% | 56.4% | 62.6% | 62.6% | −1.1pp |
| epilepsy_cause F1 | 23.5% | 10.5% | 20.0% | 22.2% | 18.2% | +13.0pp |
| seizure_frequency F1 | 59.8% | 45.7% | 49.4% | 51.2% | 47.3% | +14.1pp |
| medication_temporality F1 | 62.5% | 62.5% | 56.2% | 59.2% | 62.0% | 0.0pp |
| Evidence quote support | **99.3%** | 87.7% | 98.9% | 99.5% | 93.0% | +11.6pp |
| Runtime | ~958 s (**24.0 s/rec**) | — | 3.2 s/rec | 2.0 s/rec | 19.5 s/rec | — |
| Tokens (total) | 160,068 | — | 142,392 | — | 170,018 | — |

**Read:** Pooled micro F1 **beats GPT anchor (+3.2pp)** and leads Gemini 3 Flash on this run. Gains concentrate in sparse/hard families (seizure_frequency, epilepsy_cause, annotated_medication). Seizure_type still lags GPT. Report per-family breakdown in synthesis; do not operational-promote from suite position alone.

## Gan F0 full validation (299 records)

| Provider | Run | Monthly | Purist | Pragmatic | Norm exact | Schema | Evidence | s/rec |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **GPT 5.5** | `…121010Z` | **74.9%** | **80.3%** | **83.9%** | **67.9%** | **100%** | **100%** | **2.03** |
| Gemini 3 Flash | `…111541Z` | 75.3% | 81.3% | 86.3% | 66.2% | 100% | 100% | 1.18 |
| Claude | `…095634Z` | 73.0% | 79.5% | 85.7% | 61.8% | 98.0% | 99.3% | 5.04 |
| Gemini 3.1 | `…094020Z` | 72.6% | 78.3% | 84.6% | 61.2% | 100% | 100% | 0.66 |
| GPT 4.1-mini | `…073432Z` | 68.1% | 75.5% | 81.5% | 56.0% | 99.7% | 100% | 0.91 |

**Monthly delta (GPT 5.5 F0 − GPT 4.1-mini F0):** **+6.8pp** (224/299 vs 203/298).  
**Monthly delta (5.5 − Gemini 3 Flash):** **−0.4pp**.  
95% CI on 5.5 monthly: 69.9–80.0% (bootstrap in metrics JSON).

**Read:** GPT 5.5 is a **strong Gan F0 hosted track** — above GPT 4.1-mini, Gemini 3.1, and Claude on monthly; essentially tied with Gemini 3 Flash (−0.4pp). Perfect schema and evidence. Latency ~2.0 s/rec (slower than Gemini 3.1 / GPT 4.1-mini, faster than Claude).

## Contract gates

| Gate | S1 | S4 | Gan F0 |
| --- | --- | --- | --- |
| Artifacts complete | Pass | Pass | Pass |
| Schema validity | N/A | N/A | **100%** |
| Evidence support | **99.2%** | **99.3%** | **100%** |
| Performance claim | Model-comparison only | Model-comparison only | Model-comparison only |

## Billing (list-price estimate)

OpenAI GPT-5.5 standard rates: $5/M input, $30/M output ([pricing](https://openai.com/api/pricing/)).

| Arm | Prompt | Completion | Total tokens | Est. cost |
| --- | ---: | ---: | ---: | ---: |
| Smokes (9 calls) | 21,377 | 5,562 | 26,939 | ~$0.27 |
| S1 full | 69,995 | 30,148 | 100,143 | ~$1.25 |
| S4 full | 103,924 | 56,144 | 160,068 | ~$2.21 |
| Gan F0 full | 675,513 | 13,279 | 688,792 | ~$3.78 |
| **Full suite** | **849,432** | **99,571** | **949,003** | **~$7.23** |

Actual dashboard totals may differ slightly (rounding, retries, billing lag).

## Decision

| Surface | Position vs GPT 4.1-mini anchor | Operational promotion |
| --- | --- | --- |
| S1 | Below anchor (−6.6pp micro) | **No** |
| S4 | Above anchor (+3.2pp micro) | **No** — arm evidence only |
| Gan F0 | Above anchor (+6.8pp monthly) | **No** — model-comparison only (same rule as Gemini F0 lead) |

**Suite summary:** GPT 5.5 is **mixed on ExECT** (S1 under anchor, S4 over) and **competitive on Gan F0** (near top of hosted ladder). Does not displace GPT 4.1-mini as search/repro anchor or operational default.

## Next

- Fold row into phase-5 model-profile synthesis and registry backfill when curated.
- Kanban: mark GPT 5.5 full replay **done**.
