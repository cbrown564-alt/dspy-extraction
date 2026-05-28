# ExECT S3 Label Policy v1.1

Date: 2026-05-20

## Motivation

Full validation error read (`docs/experiments/exect/exect_s3_validation_full_gpt4_1_mini_inspection_20260520.md`) showed **investigation label-format collapse** (10.3% F1 vs 90.0% S2 full on the same 40 records): the nine-family pass caused the model to emit imaging prose instead of benchmark `modality+result` strings. Frozen S2 bridges in `exect_s2.py` were unchanged.

## Changes

**Prompt version:** `exect_s3_field_family_v1_1_label_policy`

1. **S2-first priority block** — prepended to `EXECT_S3_LABEL_POLICY_GUIDANCE` with explicit investigation `modality+result` rules and anti-prose examples.
2. **Expanded `ExectS3FieldFamilySignature` docstring** — S2-before-S3 ordering and investigation boundary examples.
3. **Additional policy examples** — investigation not prose; S2 labels when birth history present.
4. **S3-only recovery bridges** (in `exect_s3.py`, after frozen S2 bridges):
   - `_recover_s3_investigation_raw_values` — map prose/plus/colon surfaces to `eeg|mri|ct` + `normal|abnormal|unknown`; drop planned-only mentions
   - `_recover_s3_when_diagnosed_raw_values` — drop seizure-type mis-assignments in when-diagnosed slot

`exect_s2.py` and `exect_s0_s1.py` are **unchanged**.

## Configs

- `configs/experiments/exect_s3_smoke_gpt4_1_mini.json`
- `configs/experiments/exect_s3_validation_cap25_gpt4_1_mini.json`
- `configs/experiments/exect_s3_validation_full_gpt4_1_mini.json`

## Validation

```powershell
uv run pytest tests/test_exect_s3_program.py tests/test_experiment_configs.py -k exect_s3 -q
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s3_validation_cap25_gpt4_1_mini.json --env-file .env
```

## Baseline to beat (v1.0 full, 40 records)

Run: `runs/exect_s3_validation_full_gpt4_1_mini_20260519T233810Z`

| Family | v1.0 full |
| --- | ---: |
| Investigation F1 | 10.3% |
| Comorbidity F1 | 57.1% |
| Seizure F1 | 61.2% |
| Micro F1 (9 fam) | 56.1% |

## Cap-25 replay (25 records)

Run: `runs/exect_s3_validation_cap25_gpt4_1_mini_20260519T234358Z`

| Metric | v1.1 cap-25 | v1.0 cap-25 (`…233252Z`) | S2 v1.3 cap-25 (`…230945Z`) |
| --- | ---: | ---: | ---: |
| Micro F1 (9 fam) | **67.3%** | 61.7% | 87.5% (5 fam) |
| Investigation F1 | **93.8%** | 9.3% | 88.2% |
| Comorbidity F1 | 69.8% | 71.0% | 85.7% |
| Seizure F1 | 37.7% | 67.6% | 83.1% |
| Medication F1 | 80.6% | 77.1% | 91.8% |
| Diagnosis F1 | 93.0% | 95.2% | 90.5% |
| Evidence support | 86.9% | 87.3% | — |

Investigation collapse **recovered** on cap-25. Seizure regressed vs v1.0 cap and S2 cap — next tuning target if continuing S3.

## Full validation replay (40 records)

Run: `runs/exect_s3_validation_full_gpt4_1_mini_20260519T234907Z`

| Metric | v1.1 full | v1.0 full (`…233810Z`) | S2 v1.3 full (`…231223Z`) |
| --- | ---: | ---: | ---: |
| Micro F1 (9 fam) | **65.1%** | 56.1% | 80.9% (5 fam) |
| Investigation F1 | **94.9%** | 10.3% | 90.0% |
| Comorbidity F1 | 57.7% | 57.1% | 69.3% |
| Seizure F1 | 32.7% | 61.2% | 71.0% |
| Medication F1 | 82.9% | 78.6% | 90.0% |
| Diagnosis F1 | 88.9% | 92.5% | 88.9% |
| Birth history F1 | 42.9% | 26.7% | n/a |
| When diagnosed F1 | 66.7% | 23.5% | n/a |
| Evidence support | 86.1% | 87.8% | — |

**Read:** v1.1 fixes investigation on full (+84.6pp vs v1.0) and matches/beats S2 investigation. Seizure full F1 collapsed further (−28.5pp vs v1.0) — multi-family drift moved to seizure slot; do not promote v1.1 as frozen S3 without seizure policy work or accepting S2-only seizure baseline.
