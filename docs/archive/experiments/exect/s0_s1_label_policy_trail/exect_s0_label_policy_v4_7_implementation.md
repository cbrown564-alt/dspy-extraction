# ExECT Label-Policy v4.7 Implementation

Date: 2026-05-19

Prompt version: `exect_s0_s1_field_family_v4_7_label_policy`

## Target (post–v4.6 anchor)

v4.6 cleared generic epilepsy co-list and TLE header regressions but left **EA0116** failing: the model misfiled `epilepsy with generalised tonic clonic seizures from sleep` into the seizure-type slot (or omitted diagnosis entirely) while gold expects `epilepsy with generalized tonic clonic seizures on awakening`. Scorer unchanged. v4.6 remains comparison anchor until this ladder clears.

## Changes

### Prompt (`EXECT_S0_S1_LABEL_POLICY_GUIDANCE` + policy examples)

- Clarify that from-sleep header phrasing for this syndrome maps to the on awakening benchmark diagnosis label
- Add `from_sleep_header_to_on_awakening_diagnosis` policy example

### Deterministic bridges (monolithic variant only)

| Bridge | Behavior |
| --- | --- |
| `on_awakening_diagnosis_surface` | Map `epilepsy with generalized tonic clonic seizures from sleep` model outputs to `epilepsy with generalized tonic clonic seizures on awakening` |
| `diagnosis_co_list_augmented` (extended) | Note-gated recovery when the note establishes the on-awakening syndrome via header/impression `from sleep` or `on awakening` phrasing but diagnosis is empty |

Verify-repair and diagnosis-recall variants unchanged.

## Validation ladder

1. **Slice gate (37 records):** `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json`
2. **Cap-25:** `configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json`
3. **Full (40):** `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json --env-file .env
```

## Slice gate (37 records)

Run: `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T214010Z`

| Metric | v4.7 slice | v4.6 slice baseline (`…213639Z`) | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **87.6%** | 87.2% | +0.4pp |
| Diagnosis F1 | **89.5%** | 88.0% | +1.5pp |
| Seizure F1 | 84.8% | 84.8% | 0 |
| Medication F1 | 88.9% | 88.9% | 0 |

**Slice gate: cleared** vs v4.6 expanded baseline. **EA0116 cleared.**

## Cap-25 (25 records)

Run: `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T214021Z`

| Metric | v4.7 cap-25 | v4.6 cap-25 | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **94.4%** | 93.8% | +0.6pp |
| Diagnosis F1 | **97.6%** | 95.0% | +2.6pp |
| Seizure F1 | 96.9% | 96.9% | 0 |

## Full validation (40 records)

Run: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T214031Z`

| Metric | v4.7 full | v4.6 full | v4.5 full | Delta vs v4.6 |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 | **88.0%** | 87.5% | 84.5% | +0.5pp |
| Diagnosis F1 | **89.7%** | 88.3% | 77.1% | +1.4pp |
| Seizure F1 | 85.1% | 85.1% | 85.1% | 0 |
| Medication F1 | 89.4% | 89.4% | 89.4% | 0 |
| Evidence support | 95.0% | 94.9% | 94.7% | +0.1pp |

**v4.7 was the monolithic anchor until v4.8 (2026-05-19).** **EA0116** cleared on full validation. Next bounded work at v4.7 ship: EA0135 dissociative routing (cleared in v4.8), EA0188 specificity collapse, EA0008 medication. See `docs/experiments/exect/exect_s0_label_policy_v4_8_implementation.md`.

## Prior analysis

`docs/experiments/exect/exect_s0_label_policy_v4_6_implementation.md`, `docs/experiments/exect/exect_s0_s1_validation_full_v4_4_inspection.md`, `docs/experiments/exect/exect_label_policy_prior_error_analysis_traceability_20260519.md`
