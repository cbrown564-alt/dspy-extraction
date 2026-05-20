# ExECT Label-Policy v4.6 Implementation

Date: 2026-05-19

Prompt version: `exect_s0_s1_field_family_v4_6_label_policy`

## Target (post–v4.5 anchor)

v4.5 cleared the JME / myoclonic cluster but left **generic `epilepsy` false negatives** (EA0131, EA0148, EA0170, EA0173) and introduced an **EA0185** regression by over-suppressing diagnosis when the header lists focal seizures with possible TLE. Scorer unchanged. v4.5 remains comparison anchor until this ladder clears.

## Changes

### Prompt (`EXECT_S0_S1_LABEL_POLICY_GUIDANCE` + policy examples)

- Broaden generic-epilepsy co-list guidance beyond focal onset epilepsy to primary generalized and symptomatic structural focal surfaces
- Map `epilepsy unclassified` / `unclassified epilepsy` header wording to `epilepsy`
- Preserve `temporal lobe epilepsy` when the diagnosis header names possible TLE (not seizure-descriptor-only)

### Deterministic bridges (monolithic variant only)

| Bridge | Behavior |
| --- | --- |
| `diagnosis_co_list_augmented` (extended) | Note-gated `epilepsy` when any of focal onset, primary generalized, symptomatic structural focal, focal, generalized, or genetic generalized epilepsy is present and standalone epilepsy appears in prose |
| `diagnosis_co_list_augmented` (header recovery) | When `epilepsy` is still missing but the diagnosis header establishes generic epilepsy (`epilepsy unclassified`, `unclassified epilepsy`, or header-leading `epilepsy`) |
| `unclassified_epilepsy_surface` | Map `epilepsy unclassified` / `unclassified epilepsy` model outputs to `epilepsy` |
| TLE header guard | Do not run `diagnosis_seizure_descriptor_header_suppressed` when the header contains `TLE` or `temporal lobe epilepsy` |

Flexible diagnosis-header parsing now accepts colon, en-dash, and hyphen separators (`Diagnosis – …`).

Verify-repair and diagnosis-recall variants unchanged.

## Validation ladder

1. **Slice gate (37 records):** `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json`
2. **Cap-25:** `configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json`
3. **Full (40):** `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json --env-file .env
```

## Slice gate (37 records)

Run: `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T213639Z`

| Metric | v4.6 slice | v4.5 slice baseline (`…212119Z`) | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **87.2%** | 84.5% | +2.7pp |
| Diagnosis F1 | **88.0%** | 78.3% | +9.7pp |
| Seizure F1 | 84.8% | 84.8% | 0 |
| Medication F1 | 88.9% | 88.9% | 0 |

**Slice gate: cleared** vs v4.5 expanded baseline.

## Cap-25 (25 records)

Run: `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T213452Z`

| Metric | v4.6 cap-25 | v4.5 cap-25 | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | 93.8% | 93.8% | 0 |
| Diagnosis F1 | 95.0% | 95.0% | 0 |
| Seizure F1 | 96.9% | 96.9% | 0 |

## Full validation (40 records)

Run: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T213650Z`

| Metric | v4.6 full | v4.5 full | v4.4 full | Delta vs v4.5 |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 | **87.5%** | 84.5% | 82.0% | +3.0pp |
| Diagnosis F1 | **88.3%** | 77.1% | 79.5% | +11.2pp |
| Seizure F1 | 85.1% | 85.1% | 76.8% | 0 |
| Medication F1 | 89.4% | 89.4% | 89.4% | 0 |
| Evidence support | 94.9% | 94.7% | 94.1% | +0.2pp |

**v4.6 is the new monolithic anchor.** Target records **EA0131, EA0148, EA0170, EA0173** (generic epilepsy co-list) and **EA0185** (TLE header regression) cleared on full validation. Field-family mismatches remain **22** (shifted cluster; next bounded work per v4.4 inspection: EA0116 awakening syndrome, EA0135 dissociative routing, EA0188 specificity collapse, EA0008 medication).

## Prior analysis

`docs/exect_s0_label_policy_v4_5_implementation.md`, `docs/exect_s0_s1_validation_full_v4_4_inspection.md`, `docs/exect_label_policy_prior_error_analysis_traceability_20260519.md`
