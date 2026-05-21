# ExECT S1 Full Reference Ladder — GPT Validation v1 Inspection

Date: 2026-05-21  
Comparison group: `exect_s1_full_ladder_gpt_validation_v1`  
Preregistration: `docs/exect_s1_full_ladder_gpt_validation_v1_preregistration_20260521.md`  
Split policy: `docs/dataset_splits_policy.md`

## Taxonomy (shared fixed controls)

| Control | Value |
| --- | --- |
| Dataset / split | ExECTv2 `exectv2_fixed_v1:validation` |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` |
| Model | GPT 4.1-mini |
| Verification | `none` (L1+policy uses inline bridges) |
| `report_on_test_split` | `false` |

## Run artifacts

| Rung | Config | Run ID | Records |
| ---: | --- | --- | ---: |
| D1 | `exect_s1_full_ladder_d1_cap25_gpt4_1_mini` | `exect_s1_full_ladder_d1_cap25_gpt4_1_mini_20260521T003704Z` | 25 |
| L0 | `exect_s1_full_ladder_l0_cap25_gpt4_1_mini` | `exect_s1_full_ladder_l0_cap25_gpt4_1_mini_20260521T003707Z` | 25 |
| L1 | `exect_s1_full_ladder_l1_cap25_gpt4_1_mini` | `exect_s1_full_ladder_l1_cap25_gpt4_1_mini_20260521T003924Z` | 25 |
| L1+policy | `exect_s1_full_ladder_l1_policy_full_gpt4_1_mini` | `exect_s1_full_ladder_l1_policy_full_gpt4_1_mini_20260521T004209Z` | 40 |

## Headline metrics

| Rung | Micro F1 | Δ vs prior | Diagnosis | Seizure | Medication | Evidence support | Mismatch docs |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D1 | **58.4%** | — | 52.9% | 50.0% | 70.1% | n/a (no spans) | 25 |
| L0 | **60.0%** | +1.6 pp | 41.9% | 59.5% | 75.7% | 78.7% | 24 |
| L1 | **67.7%** | +7.7 pp | 51.0% | 62.0% | 87.5% | 85.6% | 24 |
| L1+policy | **92.3%** | +24.6 pp vs L1 cap-25* | 93.8% | 90.5% | 92.8% | 95.8% | 12 |

\*L1+policy evaluated on full validation (40 records); not directly comparable slice-to-slice with cap-25 L1 without a dedicated cap-25 policy arm.

**Micro precision / recall (pooled):**

| Rung | Precision | Recall |
| ---: | ---: | ---: |
| D1 | 48.4% | 73.5% |
| L0 | 49.6% | 75.9% |
| L1 | 61.2% | 75.9% |
| L1+policy | 92.0% | 92.6% |

## Frozen references

| Role | Run / anchor | Micro F1 | Slice |
| --- | --- | ---: | --- |
| GPT v4_10 cap-25 | `exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z` | 95.8% | cap-25 |
| GPT v4_10 full | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | 92.3% | full 40 |
| Optimizer baseline (in-group) | `exect_s1_optimizer_baseline_cap25_gpt4_1_mini_20260521T000602Z` | 95.8% | cap-25 |
| Optimizer bootstrap (reject) | `exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini_20260521T000608Z` | 90.7% | cap-25 |

L1+policy ladder metrics are **metric-identical** to the frozen full-validation anchor (same micro F1 and per-family F1 to four decimal places).

## Preregistration gates (rungs 0–3)

| Transition | Rule | Result |
| --- | --- | --- |
| D1 → L0 | Always run | **Done** |
| L0 → L1 | Always run | **Done** |
| L1 → L1+policy | Always run | **Done** |
| L1+policy → rung 4+ | Full ≥ 90% micro; no family regression > 3 pp vs L1 cap-25 | **Pass** — 92.3% full; all families ↑ vs L1 |

**Decision:** **Proceed to optimizer compile rungs 4–7** on `exectv2_fixed_v1:train` with validation eval (separate prereg). Do not tune on test.

## Rung-by-rung interpretation

### D1 — deterministic feasibility floor

Substring note-anchoring without LLM or benchmark bridges. High recall (~74%) and low precision (~48%): many token-level false positives (`focal`, `secondary`, `epilepsy` fragments) and specificity collapse on JME cases. Establishes that deterministic matching alone is not a credible S1 ceiling.

### L0 — bare LLM (+1.6 pp vs D1)

Minimal signature with structured JSON but no v4_10 policy or inline bridges. Small pooled gain; diagnosis F1 actually **below** D1 (41.9% vs 52.9%) because the model emits clinically richer but non-benchmark labels (comorbidities, probable JME, psychogenic seizures). Evidence support 78.7% with quote-offset failures on header-style spans.

### L1 — schema-only LLM (+7.7 pp vs L0)

Schema-oriented field descriptions without benchmark policy examples. Medication improves to 87.5%; seizure +2.5 pp vs L0. Still far from production: over-extraction, missing gold on EA0109 seizure family, JME/absence confusion on EA0029/EA0125.

### L1+policy — v4_10 + inline bridges

Matches frozen GPT S1 production anchor on full validation. Mismatch docs drop from 24 (cap-25 L1) to 12 (full 40). Residual errors: EA0072 secondary seizure token, EA0136 medication brand normalization, EA0143/EA0179 specificity, EA0078 missing-gold FPs.

**Runtime caveat:** L1+policy run reported ~0.33 s prediction time and `token_usage: null` while `estimated_model_calls: 40`. Metrics match the frozen anchor; verify live-call logging if cost telemetry matters. Scoring and label path are validated.

## Mechanism attribution (ladder story)

| Increment | Approx. micro lift (cap-25 unless noted) | Primary mechanism |
| --- | ---: | --- |
| D1 → L0 | +1.6 pp | LLM extraction vs substring |
| L0 → L1 | +7.7 pp | Schema field descriptions |
| L1 → L1+policy | +24.6 pp (full 40)* | v4_10 label policy + inline benchmark bridges |

Optimizer compile (bootstrap −5.1 pp vs 95.8% cap-25 baseline) sits **above** L1 schema-only but **below** hand-authored policy — consistent with investigation doc: compile-time search cannot recover missing policy/bridge surface.

## Explicit non-promotions

- **L0/L1** are diagnostic ladder rungs only — not production candidates.
- **D1** is eval-only feasibility — not a model replacement.
- **Test holdout** not run; no promotion claim beyond validation.

## Recommended next pull

1. **Optimizer automation thesis (priority):** Run `exect_s1_ladder_optimizer_automation_v1` — L0+LabeledFewShot, L0+Bootstrap (raw compile metric), L1+LabeledFewShot. Prereg: `docs/exect_s1_ladder_optimizer_automation_thesis_20260521.md`. This tests whether compile can **replace** hand-crafted policy, not stack on it (prior v4_10 bootstrap reject at 90.7%).
2. **Rungs 6–7:** BootstrapRS / GEPA only if rung 4–5 show ≥ 10 pp lift over L1 zero-shot.
3. **Lane A Gan:** continue Gan factor-isolation follow-ups as needed.

Registry rows updated under `exect_s1_full_ladder_gpt_validation_v1`; kanban and open frontiers refreshed 2026-05-21.
