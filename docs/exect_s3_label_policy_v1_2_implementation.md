# ExECT S3 Label Policy v1.2

Date: 2026-05-20

## Motivation

v1.1 full validation (`…234907Z`) recovered **investigation** (94.9% F1) but **seizure collapsed** to 32.7% F1 vs 61.2% v1.0 and 71.0% S2 full (`…231223Z`). Error read: multi-family drift shifted to the seizure slot after investigation prose was fixed.

## Changes

**Prompt version:** `exect_s3_field_family_v1_2_label_policy`

1. **S1 seizure-priority block** — `EXECT_S3_S1_SEIZURE_PRIORITY_GUIDANCE` prepended before S2/S3 rules.
2. **Signature + seizure output field** — expanded S1 seizure legacy-surface instructions (mirrors S2 v1.1).
3. **Policy examples** — seizure before S3 fields; onset vs seizure_type slot boundaries.
4. **S3-only bridges** (in `exect_s3.py`; v1.1 investigation bridge retained):
   - `_seizure_phrases_from_misplaced_s3_slots` — reroute seizure-type phrases from onset/when_diagnosed/comorbidity into seizure recovery input
   - `_recover_s3_onset_raw_values` — keep `epilepsy` / `epileptic seizures` in onset; strip named seizure types

`exect_s2.py` and `exect_s0_s1.py` are **unchanged**.

## Configs

- `configs/experiments/exect_s3_smoke_gpt4_1_mini.json`
- `configs/experiments/exect_s3_validation_cap25_gpt4_1_mini.json`
- `configs/experiments/exect_s3_validation_full_gpt4_1_mini.json`

## Validation

```powershell
uv run pytest tests/test_exect_s3_program.py tests/test_experiment_configs.py -k exect_s3 -q
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s3_validation_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s3_validation_full_gpt4_1_mini.json --env-file .env
```

## Baseline to beat

| Run | Seizure F1 | Investigation F1 | Micro F1 (9 fam) |
| --- | ---: | ---: | ---: |
| v1.1 full `…234907Z` | 32.7% | 94.9% | 65.1% |
| v1.0 full `…233810Z` | 61.2% | 10.3% | 56.1% |
| S2 v1.3 full `…231223Z` | 71.0% | 90.0% | 80.9% (5 fam) |

## Cap-25 replay (25 records)

Run: `runs/exect_s3_validation_cap25_gpt4_1_mini_20260519T235349Z`

| Metric | v1.2 cap-25 | v1.1 cap-25 (`…234358Z`) | S2 v1.3 cap-25 (`…230945Z`) |
| --- | ---: | ---: | ---: |
| Micro F1 (9 fam) | **78.1%** | 67.3% | 87.5% (5 fam) |
| Seizure F1 | **88.2%** | 37.7% | 83.1% |
| Investigation F1 | 93.8% | 93.8% | 88.2% |
| Comorbidity F1 | 73.0% | 69.8% | 85.7% |
| Medication F1 | 80.6% | 80.6% | 91.8% |
| Evidence support | 90.8% | 86.9% | — |

Seizure regression **recovered** on cap-25 (+50.5pp vs v1.1). Investigation held.

## Full validation replay (40 records)

Run: `runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z`

| Metric | v1.2 full | v1.1 full (`…234907Z`) | v1.0 full (`…233810Z`) | S2 v1.3 full (`…231223Z`) |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 (9 fam) | **72.1%** | 65.1% | 56.1% | 80.9% (5 fam) |
| Seizure F1 | **78.1%** | 32.7% | 61.2% | 71.0% |
| Investigation F1 | **93.1%** | 94.9% | 10.3% | 90.0% |
| Comorbidity F1 | 59.8% | 57.7% | 57.1% | 69.3% |
| Medication F1 | 81.4% | 82.9% | 78.6% | 90.0% |
| Diagnosis F1 | 92.5% | 88.9% | 92.5% | 88.9% |
| Evidence support | 90.1% | 86.1% | 87.8% | — |

**Read:** v1.2 restores seizure on full (+45.4pp vs v1.1) and **beats S2 seizure** (+7.1pp). Investigation stays strong. **Comorbidity** remains below S2 full (−9.5pp).

**Freeze decision (2026-05-20):** S3 **frozen at v1.2** for ladder planning. Comorbidity gap **accepted**; no v1.3 comorbidity tuning on validation. Ladder continues at **S4** — see `docs/kanban_plan.md` Thread E.
