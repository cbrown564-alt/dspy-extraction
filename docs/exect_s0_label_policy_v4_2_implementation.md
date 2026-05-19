# ExECT Label-Policy v4.2 Implementation

Date: 2026-05-19

Prompt version: `exect_s0_s1_field_family_v4_2_label_policy`

## Target (from v4.1 full-validation read)

1. Granular seizure false positives: `myoclonic jerks`, `absences`, `jerks`, `absence events`
2. Medication false positives: non-ASM drugs, historical/planned mentions, `missing_gold` over-prediction

Scorer unchanged.

## Changes

### Prompt

- Reject jerks/absences when coarse generalized/GTCS label applies
- Empty medication without prescription list
- Non-ASM exclusion in guidance
- Four new boundary examples

### Deterministic bridges

| Bridge | Behavior |
| --- | --- |
| `granular_seizure_rejected` | Drop `jerks`, `absences`, `occasional absences` |
| `granular_seizure_surface_coarsened` | `myoclonic jerks` → `myoclonic seizures`; `absence events` → `generalized tonic clonic seizures` |
| `seizure_temporal_modifier_stripped` | `…from sleep` → `generalized tonic clonic seizures` |
| `non_asm_medication_rejected` | Drop citalopram and other listed non-ASM drugs |
| `medication_surface_repaired` | `eslicarbazine` → `eslicarbazepine` |
| Evidence filter | Drop medication when evidence contains previously/planned/tried phrasing |

### Regression slice

Expanded to 15 records (+EA0029, EA0053, EA0078).

## Slice gate (15 records)

Run: `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T202412Z`

| Metric | v4.1 (12 rec) | v4.2 (15 rec) |
| --- | ---: | ---: |
| Micro F1 | 84.8% | **89.1%** |
| Seizure F1 | 80.0% | **89.4%** |
| Diagnosis F1 | 73.7% | 78.3% |
| Medication F1 | 97.1% | 95.0% |

## Cap-25 (25 records)

Run: `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T202537Z`

| Metric | v4.2 | v4.1 cap-25 | v3 cap-25 |
| --- | ---: | ---: | ---: |
| Micro F1 | **86.4%** | 81.4% | 73.7% |
| Seizure F1 | **81.2%** | 72.0% | 65.8% |
| Medication F1 | **93.5%** | 90.6% | 92.1% |

## Full validation (40 records)

Run: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T202626Z`

| Metric | v4.2 full | v4.1 full | v3 full |
| --- | ---: | ---: | ---: |
| Micro F1 | **78.5%** | 75.3% | 67.8% |
| Diagnosis F1 | 74.3% | 74.3% | 50.6% |
| Seizure F1 | **74.7%** | 68.6% | 61.4% |
| Medication F1 | 85.1% | 82.7% | 87.4% |
| Evidence | 84.0% | 84.7% | 87.6% |

**+3.2pp micro F1** vs v4.1 full; **+10.7pp** vs v3 full. Cap-25 again optimistic (−7.9pp vs full). **v4.2 is the new monolithic anchor.**
