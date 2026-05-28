# ExECT S2 Label Policy v1.1

Date: 2026-05-19

## Motivation

Cap-25 error read (`docs/experiments/exect/exect_s2_validation_cap25_gpt4_1_mini_inspection_20260519.md`) showed seizure F1 collapse (40% vs 95.4% S1 cap-25) from model output drift when S2 fields were added, not from changes to frozen S1 bridges.

## Changes

**Prompt version:** `exect_s2_field_family_v1_1_label_policy`

1. **S1 priority guidance block** — prepended to `EXECT_S2_LABEL_POLICY_GUIDANCE` (prompts artifact + policy traceability).
2. **Expanded `ExectS2FieldFamilySignature` docstring** — S1 seizure/medication priority and S2 boundary examples (DSPy instruction surface).
3. **Additional policy examples** — altered awareness, absence guard, stroke atomization, investigation unknown guard.
4. **S2-only recovery bridges** (in `exect_s2.py`, before S1 `_seizure_type_values_for_record`):
   - `_recover_s2_seizure_raw_values` — impaired→altered, GTCS plural, ILAE drop, absence drop, convulsive restore, focal specificity
   - `_recover_s2_comorbidity_raw_values` — stroke atomization, learning-difficulty modifiers, migraine plural, trisomy specificity
   - `_recover_s2_investigation_raw_values` — drop unknown without note support

S1 code in `exect_s0_s1.py` is **unchanged**.

## Configs

- `configs/experiments/exect_s2_smoke_gpt4_1_mini.json`
- `configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json`

## Validation

```powershell
uv run --extra dev pytest tests/test_exect_s2_program.py tests/test_experiment_configs.py -k exect_s2 -q
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json --env-file .env
```

## Cap-25 replay (25 records)

Run: `runs/exect_s2_validation_cap25_gpt4_1_mini_20260519T225159Z`

| Metric | v1.1 cap-25 | v1 cap-25 (`…224038Z`) | S1 v4.10 cap-25 |
| --- | ---: | ---: | ---: |
| Micro F1 (5 fam) | **79.7%** | 66.4% | 95.8% (3 fam) |
| Seizure F1 | **80.6%** | 40.0% | 95.4% |
| Diagnosis F1 | 83.7% | 88.4% | — |
| Medication F1 | 91.8% | 81.7% | — |
| Investigation F1 | 90.9% | 85.7% | n/a |
| Comorbidity F1 | 53.8% | 49.0% | n/a |
| Evidence support | 88.4% | 87.1% | ~96% |

Seizure regression largely recovered; comorbidity remains the main S2 tuning target. Full 40-record validation is the next gate after comorbidity policy iteration.
