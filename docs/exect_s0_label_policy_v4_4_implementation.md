# ExECT Label-Policy v4.4 Implementation

Date: 2026-05-19

Prompt version: `exect_s0_s1_field_family_v4_4_label_policy`

## Target (post–v4.3 plateau)

v4.3 improved medication F1 and evidence support but left **diagnosis F1 (74.3%)** and **seizure F1 (74.7%)** unchanged on full validation. The diagnosis-recall add-only probe was **negative**; this release uses **prompt + deterministic co-list bridges** instead.

Scorer unchanged. v4.3 remains comparison anchor (`exect_s0_s1_field_family_v4_3_label_policy`).

## Changes

### Prompt (`EXECT_S0_S1_LABEL_POLICY_GUIDANCE` + policy examples)

- Generic `epilepsy` co-list when the note names epilepsy outside compound diagnosis phrases
- `focal epilepsy` + `focal onset epilepsy` co-list when both surfaces appear
- Two new boundary examples (`generic_epilepsy_co_list_with_focal_onset`, `focal_onset_and_focal_epilepsy_co_list`)

### Deterministic bridges (monolithic variant only)

| Bridge | Behavior |
| --- | --- |
| `diagnosis_co_list_augmented` | Note-gated additions: `epilepsy` with `focal onset epilepsy`; `focal onset epilepsy` with `focal epilepsy`; `parietal lobe epilepsy` with probable/parietal wording |
| `focal_onset_to_bilateral_surface` | `focal onset convulsive seizure(s)` → `focal to bilateral convulsive seizure(s)` (audited annotation surface) |

Verify-repair and diagnosis-recall variants **do not** run co-list augmentation (guards unchanged).

## Validation ladder

1. **Slice gate (23 records):** `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json`
2. **Cap-25:** `configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json`
3. **Full (40):** `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json --env-file .env
```

## Slice gate (23 records)

Run: `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T210540Z`

| Metric | v4.4 slice | v4.3 slice (23 rec) | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **83.3%** | 80.0% | +3.3pp |
| Diagnosis F1 | **80.9%** | — | — |
| Seizure F1 | **84.8%** | — | — |
| Medication F1 | 83.6% | 83.6% | 0 |
| Evidence support | 95.9% | 95.9% | 0 |

**Slice gate: cleared.**

## Cap-25 (25 records)

Run: `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T210552Z`

| Metric | v4.4 cap-25 | v4.3 cap-25 | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **88.0%** | 84.7% | +3.3pp |
| Diagnosis F1 | **92.7%** | — | — |
| Seizure F1 | 84.1% | — | — |
| Medication F1 | 89.3% | 89.3% | 0 |
| Evidence support | 97.3% | 97.3% | 0 |

## Full validation (40 records)

Run: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T210602Z`

| Metric | v4.4 full | v4.3 full | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **82.0%** | 79.8% | +2.2pp |
| Diagnosis F1 | **79.5%** | 74.3% | +5.2pp |
| Seizure F1 | **76.8%** | 74.7% | +2.1pp |
| Medication F1 | 89.4% | 89.4% | 0 |
| Evidence support | 94.1% | 94.1% | 0 |

**v4.4 is the new monolithic anchor** for ExECT S0/S1 (diagnosis + seizure gains; medication/evidence held). Scorer unchanged.

## Closed paths (unchanged)

- Do not promote verify-repair (cap-25 label F1 regression vs v4.2/v4.3)
- Do not reopen add-only diagnosis-recall v1

## Prior analysis traceability

See `docs/exect_label_policy_prior_error_analysis_traceability_20260519.md` for reconciliation of this ladder with `docs/previous_exect_error_analysis.md` (audited-gold pivot, §8 canonical cases, and regression-slice gaps).

## Next

- **v4.5 bounded hypotheses** (see `docs/exect_s0_s1_validation_full_v4_4_inspection.md`): JME/GTCS vs myoclonic surfaces; note-gated generic `epilepsy` co-list; EA0008 medication; EA0188 specificity-collapse co-list
- Slice expanded **23 → 37 records** (`exect_s0_label_policy_regression_v3`); re-run slice config before v4.5 work

## Prior analysis traceability

See `docs/exect_label_policy_prior_error_analysis_traceability_20260519.md` and `docs/exect_s0_s1_validation_full_v4_4_inspection.md`.
