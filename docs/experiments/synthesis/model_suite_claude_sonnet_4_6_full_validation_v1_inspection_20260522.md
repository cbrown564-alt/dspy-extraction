# Model Suite Claude Sonnet 4.6 Full Validation v1 — Inspection

Date: 2026-05-22  
Comparison group: `model_suite_frozen_architecture_v1`  
Preregistration: `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md`  
decision_scope: **arm** (model-comparison evidence only; not mechanism closure)

## Purpose

Complete the Claude Sonnet 4.6 column on the three frozen comparison surfaces (ExECT S1, ExECT S4, Gan S0 F0) after provider smokes passed on 2026-05-22.

## Run artifacts

| Arm | Run ID suffix | Records | Config |
| --- | --- | ---: | --- |
| S1 smoke | `…080538Z` | 3 | `exect_s0_s1_smoke_claude_sonnet_4_6_anthropic.json` |
| S4 smoke | `…080625Z` | 3 | `exect_s4_smoke_claude_sonnet_4_6_anthropic.json` |
| Gan F0 smoke | `…080527Z` | 3 | `gan_s0_expanded_builders_prose_smoke_claude_sonnet_4_6_anthropic.json` |
| **S1 full** | **`…090828Z`** | 40 | `exect_s0_s1_validation_full_claude_sonnet_4_6_anthropic.json` |
| **S4 full** | **`…093634Z`** | 40 | `exect_s4_validation_full_claude_sonnet_4_6_anthropic.json` |
| **Gan F0 full** | **`…095634Z`** | 299 | `gan_s0_expanded_builders_prose_full_validation_claude_sonnet_4_6_anthropic.json` |

**Model:** `configs/models/gan_s0_claude_sonnet_4_6_anthropic.json` (`claude-sonnet-4-6`)  
**Scorer / split:** unchanged from GPT/Gemini/Qwen anchors

## S1 full validation (40 records)

| Metric | Claude | GPT anchor | Gemini anchor | Qwen anchor | Δ Claude−GPT |
| --- | ---: | ---: | ---: | ---: | ---: |
| Micro F1 | **81.8%** | 92.3% | 90.3% | 79.0% | **−10.5pp** |
| diagnosis F1 | 92.5% | 93.8% | 92.3% | — | −1.3pp |
| seizure_type F1 | **66.0%** | 90.5% | 85.7% | — | **−24.5pp** |
| annotated_medication F1 | 90.1% | 92.8% | 93.5% | — | −2.7pp |
| Evidence quote support | 97.6% | — | 100.0% | — | — |
| Runtime | ~536 s (**13.4 s/rec**) | — | ~1.3 s/rec | — | — |
| Tokens (total) | 113,970 | — | — | — | — |

**Read:** Claude **lags GPT by 10.5pp** pooled micro and sits only **+2.8pp above Qwen**. The deficit is concentrated in **seizure_type F1 (−24.5pp vs GPT)**; diagnosis and medication are nearer parity. Evidence support is strong (97.6%) but not perfect.

## S4 full validation (40 records)

| Metric | Claude | GPT anchor | Gemini anchor | Qwen anchor* | Δ Claude−GPT |
| --- | ---: | ---: | ---: | ---: | ---: |
| Micro F1 (11 fam) | **65.1%** | 65.5% | 66.8% | 67.5% | **−0.4pp** |
| diagnosis F1 | 78.9% | 91.1% | 90.0% | 88.3% | −12.2pp |
| seizure_type F1 | 75.4% | 84.0% | 82.8% | 76.3% | −8.6pp |
| annotated_medication F1 | 84.4% | 71.3% | 72.3% | 80.4% | +13.1pp |
| investigation F1 | 91.5% | 96.7% | 96.7% | 94.7% | −5.2pp |
| comorbidity F1 | 62.6% | 59.8% | 62.6% | 64.0% | +2.8pp |
| epilepsy_cause F1 | **18.2%** | 10.5% | 22.2% | 19.0% | +7.7pp |
| seizure_frequency F1 | 47.3% | 45.7% | 51.2% | 50.0% | +1.6pp |
| medication_temporality F1 | 62.0% | 62.5% | 59.2% | 69.3% | −0.5pp |
| Evidence quote support | **93.0%** | 87.7% | 99.5% | 93.4% | +5.3pp |
| Runtime | ~779 s (**19.5 s/rec**) | — | ~2.0 s/rec | — | — |
| Tokens (total) | 170,018 | — | — | — | — |

\*Qwen S4 anchor used pre-bridge L1 variant; Claude uses frozen K0+K1 path for GPT parity.

**Read:** Pooled micro F1 is **essentially tied with GPT (−0.4pp)** with a **mixed family profile** — stronger medication recall/precision tradeoff (+13.1pp medication F1 vs GPT), weaker diagnosis (−12.2pp) and seizure_type (−8.6pp). Sparse-family cells (onset, when_diagnosed) remain noisy at n≤4. Do not rank from pooled micro alone.

## Gan F0 full validation (299 records)

| Provider | Run | Monthly | Purist | Pragmatic | Norm exact | Schema | Evidence | s/rec |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Claude** | `…095634Z` | **73.0%** | **79.5%** | **85.7%** | **61.8%** | **98.0%** | **99.3%** | **5.04** |
| Gemini | `…094020Z` | 72.6% | 78.3% | 84.6% | 61.2% | 100% | 100% | 0.66 |
| GPT 4.1-mini | `…073432Z` | 68.1% | 75.5% | 81.5% | 56.0% | 99.7% | 100% | 0.91 |

**Monthly delta (Claude F0 − GPT F0):** **+4.9pp** (~218/299 vs 203/298).  
**Monthly delta (Claude − Gemini):** **+0.4pp**.

**Schema note:** 6/299 invalid predictions (98.0% schema-valid rate) vs Gemini 100% and GPT 99.7% (1 shared failure). Inspect `errors.json` before treating schema parity as established.

**Read:** Claude is **competitive on Gan F0 monthly** — between Gemini (+0.4pp) and GPT (+4.9pp) — but **~7.6× slower per record than Gemini** and **~5.5× slower than GPT** on this run, with slightly worse schema validity.

## Contract gates

| Gate | S1 | S4 | Gan F0 |
| --- | --- | --- | --- |
| Smoke before full | Pass | Pass | Pass |
| Full predictions + scorer | 40/40 | 40/40 | 299/299 |
| Invalid runtime failures | 0 | 0 | 0 |
| Schema validity | N/A | N/A | 98.0% (6 invalid) |
| Evidence support | 97.6% | 93.0% | 99.3% |

## Taxonomy

| Field | Value |
| --- | --- |
| varied_factor | `model_track` = claude_sonnet46 |
| comparison_group | `model_suite_frozen_architecture_v1` |
| outcome | **hold** (model-comparison evidence) |
| mechanism closure | No |
| operational promotion | No |

## Decision

**Hold** as model-comparison evidence:

1. **S1:** Claude is **not competitive with GPT/Gemini hosted tracks** on pooled micro (−10.5pp vs GPT); seizure_type is the dominant residual. Do not substitute Claude for ExECT S1 operational defaults.
2. **S4:** Claude **matches GPT pooled micro** with divergent per-family tradeoffs (medication up, diagnosis/seizure down). Same per-family reporting discipline as Gemini/Qwen S4 reads.
3. **Gan F0:** Claude **matches/exceeds GPT and Gemini on monthly** (+4.9pp / +0.4pp) but with **6 schema-invalid records**, **99.3% evidence**, and **high latency (~5 s/rec)**. Model-comparison hold only — no operational promotion from suite results alone.
4. **Billing/latency:** Hosted Claude runs consumed **~114k / ~170k / ~808k tokens** on S1/S4/Gan F0 respectively; latency is materially higher than Gemini on all three surfaces.

## Next steps

- Update `docs/planning/kanban_plan.md` coverage matrix (Claude column complete).
- Proceed with Gemini 3 Flash and GPT 5.5 frozen full replays (hosted lane unblocked).
- Optional: error-read on S1 seizure_type failures and Gan F0 six invalid records before paper-facing model-profile memo (phase 5).
