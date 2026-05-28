# Gan S0 Target Selection And Label Construction Split

Date: 2026-05-28
Status: G2 ablation plan plus no-model split implementation
Dataset/split: Gan 2026 synthetic validation split (`gan_2026_fixed_v1:validation`)
Candidate source: `deterministic_temporal_candidates_current_d1_builder`
Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`
Scorer semantics: unchanged; paper reproduction and canonical views are both reported.

## Summary

Candidate-constrained oracle reaches **93.3%** monthly accuracy under `gan2026_paper_reproduction` and **94.0%** under the canonical diagnostic scorer.
The deterministic label constructor handled **1605/1605** candidate records; invalid candidate labels remain unsupported rather than repaired.

## Ablation Plan

| Arm | Selector | Label constructor | Status |
| --- | --- | --- | --- |
| `free_adjudication` | LLM reads the note and emits the final Gan label directly | LLM final-label text | `planned_model_arm` |
| `candidate_constrained_adjudication` | LLM selects one candidate or explicit fallback policy | deterministic constructor emits selected candidate label | `implemented_no_model_oracle; model arm pending` |
| `reason_code_selector` | LLM selects reason code/family and candidate target | deterministic constructor emits label from selected target | `implemented_family_oracle; slot-level model arm pending` |
| `deterministic_label_constructor` | provided selected candidate | normalization plus audited Gan taxonomy validation only | `implemented_candidate_validation_surface` |

## No-Model Split Report

| Arm | Supported | Canonical monthly | Canonical pragmatic | Paper monthly | Paper pragmatic |
| --- | ---: | ---: | ---: | ---: | ---: |
| `candidate_constrained_oracle` | 299/299 | 94.0% | 98.7% | 93.3% | 98.0% |
| `reason_code_selector_family_oracle` | 296/299 | 83.9% | 94.3% | 83.9% | 94.3% |

## Constructor Diagnostics

| Candidate records | Constructed | Invalid |
| ---: | ---: | ---: |
| 1605 | 1605 | 0 |

## Label-Family View

| Family | Records | Candidate-constrained paper monthly | Reason-code paper monthly |
| --- | ---: | ---: | ---: |
| `cluster` | 29 | 100.0% | 100.0% |
| `no_reference` | 11 | 100.0% | 100.0% |
| `quantified_rate` | 162 | 88.9% | 71.6% |
| `seizure_free` | 45 | 95.6% | 100.0% |
| `unknown` | 35 | 100.0% | 100.0% |
| `unknown_cluster` | 5 | 100.0% | 80.0% |
| `vague_or_multiple_rate` | 12 | 100.0% | 91.7% |

## Interpretation

- This report is a no-model decomposition scaffold, not a completed model comparison.
- `free_adjudication` remains the control model arm; the implemented rows here quantify what the current G1 substrate can support if selection were perfect.
- Invalid candidate surfaces are not repaired here; scorer repair remains explicit and scorer-only.
- `reference[0]` is not used as gold. It is retained only through hard-case flags.

## Companion Artifact

`docs/experiments/gan/gan_s0_target_label_split_g2_report_20260528.json` contains all record-level selected-candidate, construction, scorer, and strata fields.
