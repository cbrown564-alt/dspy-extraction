# ExECT Label-Policy v4.9 Implementation

Date: 2026-05-19

Prompt version: `exect_s0_s1_field_family_v4_9_label_policy`

## Target (post–v4.8 anchor)

v4.8 cleared dissociative versus epileptic seizure routing (**EA0135**) but left two bounded residuals from the v4.4 full read:

- **EA0188** — missing specificity-collapse diagnosis tokens `focal`, `drug`, `occipital` alongside `focal epilepsy` and `occipital lobe epilepsy`
- **EA0008** — missing `lamotrigine` when the model omitted medication despite a current prescription line with a taper parenthetical

Scorer unchanged. v4.8 remains comparison anchor until this ladder clears.

## Changes

### Prompt (`EXECT_S0_S1_LABEL_POLICY_GUIDANCE` + policy examples)

- Co-list collapsed diagnosis tokens `focal`, `drug`, `occipital` when drug-refractory focal / occipital-lobe specificity-collapse gold is supported
- Keep current prescription ASM when taper/stop wording appears in parentheses on the same line; exclude separate planned-start lines only
- Add `specificity_collapse_diagnosis_co_list` and `current_prescription_with_taper_parenthetical` policy examples

### Deterministic bridges (monolithic variant only)

| Bridge | Behavior |
| --- | --- |
| `specificity_collapse_diagnosis_co_listed` | When note supports drug-refractory focal / occipital collapse and at least one trigger diagnosis is present, add `focal`, `drug`, `occipital` |
| `current_prescription_medication_augmented` | Recover ASM from `Current anti-epileptic medication:` / `Medication:` header lines when the model omits them |
| `_medication_evidence_excluded` refinement | On current-prescription evidence lines, exclude only planned/historical phrases (not taper parentheticals with `as detailed below`) |

Verify-repair and diagnosis-recall variants unchanged.

## Validation ladder

1. **Slice gate (37 records):** `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json`
2. **Cap-25:** `configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json`
3. **Full (40):** `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json --env-file .env
```

## Slice gate (37 records)

Run: `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T220225Z`

| Metric | v4.9 slice | v4.8 slice (`…215450Z`) | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **90.9%** | 88.4% | +2.5pp |
| Diagnosis F1 | 93.7% | 89.5% | +4.2pp |
| Seizure F1 | 87.0% | 87.0% | 0 |
| Medication F1 | 92.5% | 88.9% | +3.6pp |

**EA0188:** diagnosis FN `focal`/`drug`/`occipital` **cleared**; seizure FN `secondary` remains (out of v4.9 diagnosis-only scope).  
**EA0008:** `lamotrigine` **cleared**.

## Cap-25 (25 records)

Run: `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T220238Z`

| Metric | v4.9 cap-25 | v4.8 cap-25 | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **96.3%** | 94.4% | +1.9pp |
| Medication F1 | 94.9% | 89.4% | +5.5pp |

## Full validation (40 records)

Run: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T220247Z`

| Metric | v4.9 full | v4.8 full | v4.7 full | Delta vs v4.8 |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 | **91.2%** | 88.7% | 88.0% | +2.5pp |
| Diagnosis F1 | 93.8% | 89.7% | 89.7% | +4.1pp |
| Seizure F1 | 87.2% | 87.2% | 85.1% | 0 |
| Medication F1 | 92.8% | 89.4% | 89.4% | +3.4pp |
| Evidence support | 95.9% | 95.8% | 95.0% | +0.1pp |

**v4.9 was the monolithic anchor until v4.10 (2026-05-19).** **EA0008** cleared on full validation. **EA0188** diagnosis tokens cleared on slice; seizure surface (`secondary` only) cleared in v4.10 — see `docs/experiments/exect/exect_s0_label_policy_v4_10_implementation.md`.

## Prior analysis

`docs/experiments/exect/exect_s0_label_policy_v4_8_implementation.md`, `docs/experiments/exect/exect_label_policy_prior_error_analysis_traceability_20260519.md`, `docs/experiments/exect/exect_s0_s1_validation_full_v4_4_inspection.md`
