# ExECT Ladder Investigation Guard GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Pre-registration: `docs/experiments/exect/exect_ladder_investigation_guard_gpt_cap25_v1_preregistration_20260521.md`  
decision_scope: **arm**

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | `exect_s2_field_family` |
| Comparison group | `exect_ladder_investigation_guard_gpt_cap25_v1` |
| Research axis | 3 |
| stage_graph_id | `g1_l1_policy_bridges` |
| varied_factor | `implementation_variant` |
| decision_scope | arm |

## Arms

| arm_id | run_id | investigation F1 | micro F1 | gate |
| --- | --- | ---: | ---: | --- |
| L1 | `exect_ladder_inv_l1_baseline_cap25_gpt4_1_mini_20260521T082640Z` | **88.2%** | 87.5% | control |
| I0 | `exect_ladder_inv_i0_cap25_gpt4_1_mini_20260521T082644Z` | **93.8%** | 88.2% | pass primary |

Configs: `exect_ladder_inv_l1_baseline_cap25_gpt4_1_mini.json`, `exect_ladder_inv_i0_cap25_gpt4_1_mini.json`

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| L1 | hold (control) | arm | Frozen v1.3 |
| I0 | **hold (cap-25 proceed)** | arm | +5.6pp investigation F1; ECG dropped on EA0016, EA0100 |

## Primary metric read

| Metric | L1 | I0 | Δ (I0 − L1) |
| --- | ---: | ---: | ---: |
| investigation F1 | **88.2%** | **93.8%** | **+5.6pp** |
| investigation precision | 83.3% | 93.8% | +10.5pp |
| investigation recall | 93.8% | 93.8% | 0 |

Label deltas (2/25 docs):

| Doc | L1 investigation | I0 investigation |
| --- | --- | --- |
| EA0016 | `ct abnormal`, `ecg normal` | `ct abnormal` |
| EA0100 | `ct normal`, `ecg normal` | `ct normal` |

Matches preregistered I0 fixture expectation (out-of-scope ECG FPs removed).

## Regression guard

| Family | L1 F1 | I0 F1 | Δ |
| --- | ---: | ---: | ---: |
| diagnosis | 90.5% | 90.5% | 0 |
| seizure_type | 83.1% | 83.1% | 0 |
| comorbidity | 85.7% | 85.7% | 0 |
| annotated_medication | 91.8% | 91.8% | 0 |

No frozen family regressed ≥2pp. Pooled micro F1 +0.7pp (87.5% → 88.2%).

## Mechanism review

Not claimed. I0 is one implementation of post-hoc ECG removal on S2; S3/S4 ports and I1 planned-scan guard are untested.

## Open cells

- I1 `inv_guard_planned_scan_unknown_v1` on S2 cap-25
- Import I0 into S3/S4 `_recover_*_investigation_raw_values` shared path
- Full-validation confirm before operational freeze
- EA0100 missing-gold caveat — ECG removal is still correct policy

## Next steps

1. ~~Port I0 to S3/S4 investigation recovery~~ **Done** — `ladder_investigation_guard_bridge_tiers()` on S3 `_s2_field_values_from_prediction` and S4 `_replace_s4_investigation_values`.
2. Prereg I1 arm when planned-scan fixtures are green.
3. Do **not** claim investigation mechanism closed from I0 alone.

## References

- Design: `docs/experiments/exect/exect_ladder_investigation_regression_guard_design_20260521.md`
- Full anchor: `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` (90.0% investigation F1)
