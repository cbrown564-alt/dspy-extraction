# Gan S0 G4 Explicit Reason-Code Adjudicator

Generated: `2026-05-28T22:10:03.026419+00:00`

## Scope

- Dataset: `gan_2026`
- Split: `gan_2026_fixed_v1:validation`
- Records: `25` enriched validation records
- G4 arm: `g4_explicit_reason_code_adjudicator`
- Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`
- Scorer views: `gan2026_paper_reproduction` and `gan_frequency_deterministic_v1`.

## Decision

- Recommendation: `do_not_promote_as_tested`
- Scope: `diagnostic_slice_only`
- Rationale: G4 reached 80.0% canonical monthly and 80.0% pragmatic accuracy, below the best same-slice G2 baselines (92.0% monthly, 100.0% pragmatic).

## Arm Summary

| Arm | Run ID | Paper monthly | Canonical monthly | Canonical pragmatic |
| --- | --- | ---: | ---: | ---: |
| `free_adjudication` | `gan_s0_g2_free_adjudication_gpt4_1_mini_slice_20260528T155000Z` | 16.0% | 16.0% | 76.0% |
| `candidate_constrained` | `gan_s0_g2_candidate_constrained_gpt4_1_mini_slice_20260528T155000Z` | 92.0% | 92.0% | 92.0% |
| `reason_code_selector` | `gan_s0_g2_reason_code_selector_gpt4_1_mini_slice_20260528T155000Z` | 92.0% | 92.0% | 100.0% |
| `g4_explicit_reason_code_adjudicator` | `gan_s0_g4_explicit_reason_code_adjudicator_gpt4_1_mini_slice_20260528T220121Z` | 80.0% | 80.0% | 80.0% |

## G4 Traceability Diagnostics

- Selected candidate references present: 25/25
- Label-construction inputs present: 25/25
- Unsupported selected-candidate cases: 0
- Model final-label mismatches after deterministic construction: 0

| Reason code | Count |
| --- | ---: |
| `select_current_quantified_rate` | 19 |
| `select_seizure_free_duration` | 6 |

| Primary failure type | Count |
| --- | ---: |
| `none` | 20 |
| `target_selection` | 5 |

| Failure signal | Count |
| --- | ---: |
| `policy` | 5 |
| `reason_code_label_incoherent` | 1 |
| `target_selection` | 5 |

## G4 Failure Records

| Record | Gold | G4 prediction | Reason code | Selected candidate | Primary failure | Signals |
| --- | --- | --- | --- | --- | --- | --- |
| `gan_14250` | `2 per month` | `seizure free for multiple month` | `select_seizure_free_duration` | `seizure free for multiple month` | `target_selection` | `target_selection`, `policy` |
| `gan_14485` | `2 per 3 month` | `seizure free for 1 month` | `select_seizure_free_duration` | `seizure free for 1 month` | `target_selection` | `target_selection`, `policy` |
| `gan_14792` | `1 per month` | `seizure free for multiple month` | `select_seizure_free_duration` | `seizure free for multiple month` | `target_selection` | `target_selection`, `policy` |
| `gan_14881` | `1 per month` | `seizure free for multiple month` | `select_seizure_free_duration` | `seizure free for multiple month` | `target_selection` | `target_selection`, `policy` |
| `gan_16750` | `6 per 7 month` | `seizure free for multiple month` | `select_current_quantified_rate` | `seizure free for multiple month` | `target_selection` | `target_selection`, `policy`, `reason_code_label_incoherent` |

## Pairwise Deltas

| Baseline | G4 correct / baseline wrong | G4 wrong / baseline correct |
| --- | --- | --- |
| `free_adjudication` | `gan_13058`, `gan_13149`, `gan_13190`, `gan_14214`, `gan_14562`, `gan_14628`, `gan_14689`, `gan_14965`, `gan_14973`, `gan_15127`, `gan_15168`, `gan_15193`, `gan_15302`, `gan_15442`, `gan_16529`, `gan_16645` |  |
| `candidate_constrained` | `gan_15168`, `gan_15193` | `gan_14250`, `gan_14485`, `gan_14792`, `gan_14881`, `gan_16750` |
| `reason_code_selector` | `gan_13058`, `gan_13123` | `gan_14250`, `gan_14485`, `gan_14792`, `gan_14881`, `gan_16750` |

## Interpretation

- G4 preserves the requested trace fields: explicit reason code, selected candidate reference, and label-construction inputs.
- The tested implementation underperforms the G2 candidate-constrained and seeded answer-options baselines on the same slice.
- All G4 misses are primary target-selection failures with a policy-conflict signal: a seizure-free-duration candidate was selected despite a gold-compatible quantified candidate being present.
- No label-construction or evidence-support failure was observed in this slice.
