# ExECT Label-Policy Regression Slice Comparison

Date: 2026-05-19

Slice: 12 validation records from `data/fixtures/exect_s0_label_policy_error_regression_slice.json`

Scorer: `exect_field_family_deterministic_v1` (unchanged)

## Runs

| Version | Run directory | Prompt |
| --- | --- | --- |
| v3 anchor | `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T200017Z` (subset) | `exect_s0_s1_field_family_v3_seizure_evidence_policy` |
| v4 | `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T200559Z` | `exect_s0_s1_field_family_v4_label_policy` |
| v4.1 | `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T200950Z` | `exect_s0_s1_field_family_v4_1_label_policy` |

## Headline metrics (12 records)

| Version | Micro F1 | Diagnosis F1 | Seizure-type F1 | Medication F1 | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: |
| v3 (subset) | ~58% mean record | — | — | — | — |
| v4 | **73.3%** | 41.7% | 71.4% | 97.1% | 86.7% |
| **v4.1** | **84.8%** | **73.7%** | **80.0%** | 97.1% | **95.3%** |

v4.1 adds deterministic bridges: unsupported-diagnosis rejection, symptomatic structural focal restoration, `temporal lobe seizures` → `temporal lobe seizure` + `focal seizures` split.

## v3 → v4 wins (prompt + v4 bridges)

- **EA0047**: diagnosis uncertainty stripped (`probable` removed)
- **EA0061**: convulsive modifier on focal to bilateral seizures
- **EA0090**: secondary-generalisation split (partial; GTCS still missed in v4)
- **EA0116**: dropped erroneous `from sleep` on seizure type

## v4 regressions fixed in v4.1

- **EA0018**: `temporal lobe seizures` alone → split restores `focal seizures`
- **EA0059 / EA0150**: `symptomatic structural epilepsy` → `symptomatic structural focal epilepsy`
- **EA0068 / EA0090 / EA0109**: cross-family diagnosis FPs rejected (not in audited diagnosis vocabulary)

## Remaining slice gaps (v4.1)

- **EA0090**: may still miss `generalized tonic clonic seizure` when model does not emit full fused phrase for bridge split
- **EA0098**: `focal onset convulsive seizure` vs `focal to bilateral convulsive seizure` (annotation-policy surface)
- **EA0047 / EA0124**: granular `jerks` / `absence events` vs coarse gold (`generalized seizures`, `generalized tonic clonic seizures`)
- **EA0137**: seizure phrase in diagnosis slot (model + evidence)
- **EA0061**: may still miss `parietal lobe epilepsy` co-diagnosis

## Gate recommendation

v4.1 clears a meaningful slice gate (+11.5pp micro F1 vs v4 on the same 12 records). **Reasonable next pull:** cap-25 validation on v4.1 before full validation re-run. Keep v3 full-validation run as the published comparison anchor until cap-25 completes.
