# ExECT Label-Policy v4.5 Implementation

Date: 2026-05-19

Prompt version: `exect_s0_s1_field_family_v4_5_label_policy`

## Target (post–v4.4 anchor)

v4.4 lifted diagnosis/seizure F1 via co-list bridges but left a **JME / myoclonic** cluster: models emit `myoclonic seizures` alongside coarse GTCS/tonic-clonic labels, and sometimes pick `generalized tonic clonic seizures` when gold uses `tonic clonic seizures` or `generalized tonic seizures`. Scorer unchanged. v4.4 remains comparison anchor until this ladder clears.

## Changes

### Prompt (`EXECT_S0_S1_LABEL_POLICY_GUIDANCE` + policy examples)

- JME coarse-surface policy: prefer audited coarse label; suppress myoclonic when coarse label is present
- Tonic clonic vs generalized tonic clonic vs generalized tonic seizures surface selection
- Do not emit epilepsy diagnosis when diagnosis header is seizure-descriptor-only with qualified possible JME

### Deterministic bridges (monolithic variant only)

| Bridge | Behavior |
| --- | --- |
| `jme_myoclonic_suppressed_for_coarse_label` | Drop `myoclonic seizures` when JME context and a coarse tonic/GTCS label coexist |
| `jme_tonic_clonic_surface` | Map GTCS → `tonic clonic seizures` when note uses tonic clonic without generalized prefix |
| `jme_generalized_tonic_surface` | Map GTCS → `generalized tonic seizures` when note uses that surface without clonic |
| `jme_gtcs_singular_co_listed` | Add singular GTCS when note uses singular phrasing |
| `diagnosis_seizure_descriptor_header_suppressed` | Clear diagnosis when header lists seizure types + qualified possible JME only |

Verify-repair and diagnosis-recall variants unchanged.

## Validation ladder

1. **Slice gate (37 records):** `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json`
2. **Cap-25:** `configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json`
3. **Full (40):** `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json --env-file .env
```

## Slice gate (37 records)

Run: `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T212119Z`

| Metric | v4.5 slice | v4.4 slice baseline (`…211558Z`) | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **84.5%** | 81.4% | +3.1pp |
| Seizure F1 | **84.8%** | 76.3% | +8.5pp |
| Diagnosis F1 | 78.3% | 78.9% | −0.6pp |
| Medication F1 | 88.9% | 88.9% | 0 |

**Slice gate: cleared** vs v4.4 expanded baseline.

## Cap-25 (25 records)

Run: `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T212129Z`

| Metric | v4.5 cap-25 | v4.4 cap-25 | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **93.8%** | 88.0% | +5.8pp |
| Seizure F1 | **96.9%** | 84.1% | +12.8pp |
| Diagnosis F1 | 95.0% | 92.7% | +2.3pp |
| Medication F1 | 89.3% | 89.3% | 0 |

## Full validation (40 records)

Run: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T212141Z`

| Metric | v4.5 full | v4.4 full | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **84.5%** | 82.0% | +2.5pp |
| Seizure F1 | **85.1%** | 76.8% | +8.3pp |
| Diagnosis F1 | 77.1% | 79.5% | −2.4pp |
| Medication F1 | 89.4% | 89.4% | 0 |
| Evidence support | 94.7% | 94.1% | +0.6pp |

**v4.5 is the new monolithic anchor** for ExECT S0/S1. JME cluster records **EA0048, EA0050, EA0069, EA0026, EA0029** cleared on full validation; mismatch count 26 → 22. Diagnosis F1 dipped slightly (header-suppression tradeoff); next bounded work: generic `epilepsy` co-list recall (EA0131, EA0148, EA0170, EA0173).

## Prior analysis

`docs/experiments/exect/exect_s0_s1_validation_full_v4_4_inspection.md`, `docs/experiments/exect/exect_s0_label_policy_v4_4_implementation.md`
