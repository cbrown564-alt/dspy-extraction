# ExECT S1 Stage-Executor GPT Cap-25 v1 Inspection

Date: 2026-05-21  
Scope: cap-25 (25 records), GPT 4.1-mini, Axis 2 stage-executor grid  
Preregistration: `docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_preregistration_20260521.md`  
Comparison group: `exect_s1_stage_executor_gpt_cap25_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S1 field-family |
| Comparison group | `exect_s1_stage_executor_gpt_cap25_v1` |
| Research axis | 2 |
| Anchor `stage_graph_id` | `g1_l1_policy_bridges` |
| Primary varied factor | `stage_executor` |
| decision_scope | `arm` |

## Run artifacts

| Arm | `stage_executor` | Run ID | Micro F1 |
| --- | --- | --- | ---: |
| E1 | `llm_extract_inline_bridges` | `exect_s1_stage_executor_e1_inline_bridges_cap25_gpt4_1_mini_20260521T014853Z` | **95.8%** |
| E2 | `llm_extract_post_bridges` | `exect_s1_stage_executor_e2_post_bridges_cap25_gpt4_1_mini_20260521T014856Z` | **95.8%** |
| E5 | `det_medication_hints_llm_extract` | `exect_s1_stage_executor_e5_medication_hints_cap25_gpt4_1_mini_20260521T014958Z` | 93.3% |
| E4 | `det_seizure_hints_llm_extract` | `exect_s1_stage_executor_e4_seizure_hints_cap25_gpt4_1_mini_20260521T014903Z` | 92.8% |
| E3 | `det_all_family_hints_llm_extract` | `exect_s1_stage_executor_e3_all_family_hints_cap25_gpt4_1_mini_20260521T014859Z` | 90.9% |

## Headline metrics

| Arm | Micro F1 | Diagnosis | Seizure | Medication | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: |
| E1 | **95.8%** | 97.6% | **95.4%** | 94.9% | 97.3% |
| E2 | **95.8%** | 97.6% | **95.4%** | 94.9% | 97.3% |
| E5 | 93.3% | 92.3% | 92.3% | 94.9% | 94.5% |
| E4 | 92.8% | 97.6% | 90.9% | 91.5% | 93.2% |
| E3 | 90.9% | 95.2% | 87.9% | 91.2% | 93.2% |

Best micro F1: **95.8%** (E1, E2 tied).

## Bridge placement (E1 vs E2)

| Comparison | Micro F1 Δ | Notes |
| --- | ---: | --- |
| E1 inline vs E2 post | **0.0pp** | Metric-identical on cap-25; confirms Phase 5a S1/S4 null |

Operational implication: inline and post bridge placement are interchangeable on this cap-25 slice under `g1_l1_policy_bridges`. Mechanism class remains **open** (cap-25 only, single model).

## Pre-vocab hint executors (E3–E5 vs E1)

| Arm | Micro Δ vs E1 | Seizure Δ | Prior artifact |
| --- | ---: | ---: | --- |
| E3 all-family hints | **−4.9pp** | −7.5pp | Matches interleaving H2 cap-25 (90.9%) |
| E4 seizure hints | **−3.0pp** | −4.5pp | Full cap-25 better than seizure slice reject (83.3% slice) but still below E1 |
| E5 medication hints | **−2.5pp** | −3.1pp | Full cap-25 better than medication slice (95.1% med F1 on slice) but micro below E1 |

Family-isolated hints (E4/E5) outperform all-family hints (E3) on cap-25 (+1.9pp / +2.4pp micro), but none beat inline-bridge baseline E1.

## Outcomes

| Arm | Outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| E1 | **Hold** | arm | Reproduces Phase 5a S1; production-shaped anchor |
| E2 | **Hold** | arm | Null vs E1; post bridges sufficient on cap-25 |
| E3 | **Reject (arm)** | arm | −4.9pp micro; confirms interleaving H2 cap-25 harm |
| E4 | **Reject (arm)** | arm | −3.0pp micro; family isolation does not rescue all-family H2 |
| E5 | **Reject (arm)** | arm | −2.5pp micro; best hint arm but still below E1 gate |

## Gates applied

| Rule | Result |
| --- | --- |
| Rank by micro F1 | E1/E2 lead (95.8%); E5 third (93.3%) |
| Hold within 2pp of best | E1, E2 only |
| Reject >2pp below best | E3, E4, E5 |

## Mechanism review

Not applicable — `decision_scope: arm` only.

Directional observation (not mechanism closure): deterministic pre-vocab hints hurt micro F1 on full cap-25 under every tested executor tag, consistent with interleaving v1 full-validation H2 reject. Family-isolated hints regress less than all-family hints on cap-25 but do not promote.

## Recommendation

1. **Operational default unchanged:** `llm_extract_inline_bridges` on `g1_l1_policy_bridges` (E1).
2. **Do not** advance E3–E5 to full validation.
3. **Do not** rerun slice-only H2 probes; cap-25 executor grid subsumes family-isolated full-cap evidence.
4. **Next ExECT work:** Axis 3 only if a new `implementation_variant` is preregistered (e.g., hint presentation); otherwise pivot to Gan validation ladder or ExECT optimizer rungs 4–5 thesis.

## Open cells

- Bridge inline vs post on full validation (cap-25 null).
- Diagnosis-only hint executor (no program variant).
- Hint presentation `implementation_variant`.
- Qwen port deferred.

## Cross-reference

| Prior artifact | Relationship |
| --- | --- |
| Phase 5a S1 | E1 metric match (95.8%) |
| Phase 5a S4 | E2 metric match (95.8%) |
| interleaving H2 cap-25 | E3 metric match (90.9%) |
| seizure H2 slice | E4 better on full cap-25 (92.8% vs 83.3% slice seizure F1 context) |
| medication H2 slice | E5 medication F1 94.9% vs slice 95.1% — null on primary family |
