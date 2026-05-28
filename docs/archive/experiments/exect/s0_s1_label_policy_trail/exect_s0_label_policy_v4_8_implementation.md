# ExECT Label-Policy v4.8 Implementation

Date: 2026-05-19

Prompt version: `exect_s0_s1_field_family_v4_8_label_policy`

## Target (post–v4.7 anchor)

v4.7 cleared the on-awakening syndrome diagnosis bridge (**EA0116**) but left **EA0135** failing: the model filed `focal seizures` in the seizure-type slot (inferred from focal onset epilepsy) while gold expects `epileptic seizures` after an epileptic-versus-dissociative contrast. Scorer unchanged. v4.7 remains comparison anchor until this ladder clears.

## Changes

### Prompt (`EXECT_S0_S1_LABEL_POLICY_GUIDANCE` + policy examples)

- When the note contrasts epileptic versus dissociative seizures and concludes epileptic seizures, emit `epileptic seizures` in `seizure_type`; do not infer `focal seizures` from focal onset epilepsy alone
- Add `dissociative_epileptic_seizure_routing` policy example (EA0135 pattern)

### Deterministic bridges (monolithic variant only)

| Bridge | Behavior |
| --- | --- |
| `dissociative_focal_seizure_suppressed` | When dissociative/epileptic contrast + epileptic conclusion are present and the note does not name focal seizures, drop `focal seizures` / `focal seizure` |
| `epileptic_seizures_surface_restored` | Co-add `epileptic seizures` when the same note context supports the epileptic conclusion |

Verify-repair and diagnosis-recall variants unchanged.

## Validation ladder

1. **Slice gate (37 records):** `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json`
2. **Cap-25:** `configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json`
3. **Full (40):** `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json --env-file .env
```

## Slice gate (37 records)

Run: `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T215450Z`

| Metric | v4.8 slice | v4.7 slice baseline (`…214010Z`) | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **88.4%** | 87.6% | +0.8pp |
| Diagnosis F1 | 89.5% | 89.5% | 0 |
| Seizure F1 | **87.0%** | 84.8% | +2.2pp |
| Medication F1 | 88.9% | 88.9% | 0 |

**Slice gate: cleared** vs v4.7 expanded baseline. **EA0135 cleared.**

## Cap-25 (25 records)

Run: `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T215459Z`

| Metric | v4.8 cap-25 | v4.7 cap-25 | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | 94.4% | 94.4% | 0 |
| Diagnosis F1 | 97.6% | 97.6% | 0 |
| Seizure F1 | 96.9% | 96.9% | 0 |

## Full validation (40 records)

Run: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T215507Z`

| Metric | v4.8 full | v4.7 full | v4.6 full | Delta vs v4.7 |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 | **88.7%** | 88.0% | 87.5% | +0.7pp |
| Diagnosis F1 | 89.7% | 89.7% | 88.3% | 0 |
| Seizure F1 | **87.2%** | 85.1% | 85.1% | +2.1pp |
| Medication F1 | 89.4% | 89.4% | 89.4% | 0 |
| Evidence support | 95.8% | 95.0% | 94.9% | +0.8pp |

**v4.8 was the monolithic anchor until v4.9 (2026-05-19).** **EA0135** cleared on full validation (`epileptic seizures` with dissociative routing bridges). v4.9 addresses **EA0188** specificity-collapse diagnosis co-list and **EA0008** prescription lamotrigine — see `docs/experiments/exect/exect_s0_label_policy_v4_9_implementation.md`.

## Prior analysis

`docs/experiments/exect/exect_s0_label_policy_v4_7_implementation.md`, `docs/experiments/exect/exect_s0_s1_validation_full_v4_4_inspection.md`, `docs/experiments/exect/exect_label_policy_prior_error_analysis_traceability_20260519.md`
