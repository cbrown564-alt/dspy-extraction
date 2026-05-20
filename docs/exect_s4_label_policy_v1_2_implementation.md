# ExECT S4 Label Policy v1.2

Date: 2026-05-20

## Motivation

S4 v1.1 full validation (`runs/exect_s4_validation_full_gpt4_1_mini_20260520T064751Z`) established the frequency lift anchor at **45.2%** F1 (+19.6pp vs v1.0) but introduced investigation regression (−7.1pp vs v1.0 full) from `eeg unknown` / `mri unknown` over-extraction on planned scans. Residual frequency gaps: qualitative co-label omission (EA0008, EA0050) and non-audited period FPs (`1 per 30 day`, `1 per previous appointment`).

Error read: `docs/exect_s4_validation_full_v1_1_gpt4_1_mini_inspection_20260520.md`.

## Changes

**Prompt version:** `exect_s4_field_family_v1_2_label_policy`

1. **Frequency co-label guidance** — when note states quantified rate + frequency change, emit both; block non-audited period templates (`30 day`, `previous appointment`, `several per day`).
2. **Investigation unknown guard guidance** — do not emit `modality unknown` for planned/requested scans; allow when results explicitly unavailable.
3. **Policy examples** — planned-scan abstention; unavailable-results `eeg unknown`; retained v1.1 frequency examples.
4. **S4-only bridges** (in `exect_s4.py`; S3 code unchanged):
   - `_augment_s4_seizure_frequency_co_labels` — note-anchored `frequency increased/decreased/infrequent` when quantified rate present
   - `_is_non_audited_frequency_surface` — drop invented period templates
   - `_recover_s4_investigation_raw_values` — stricter unknown guard (planned scan + unavailable-results cues)
   - `_replace_s4_investigation_values` — recompute investigation after S3 recovery with S4 guard

`exect_s3.py`, `exect_s2.py`, and `exect_s0_s1.py` are **unchanged**.

## Configs

- `configs/experiments/exect_s4_smoke_gpt4_1_mini.json`
- `configs/experiments/exect_s4_validation_cap25_gpt4_1_mini.json`
- `configs/experiments/exect_s4_validation_full_gpt4_1_mini.json`
- Qwen ladder replicas: `exect_s4_*_qwen35b_ollama.json`

## Validation

```powershell
uv run --extra dev pytest tests/test_exect_s4_program.py tests/test_exect_s4_scoring.py tests/test_exect_s4_gold_loader.py tests/test_experiment_configs.py -k exect_s4 -q
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s4_smoke_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s4_validation_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s4_validation_full_gpt4_1_mini.json --env-file .env
```

## Baseline to beat (v1.1 full, 40 records)

| Metric | v1.1 full (`…064751Z`) |
| --- | ---: |
| Micro F1 (11 fam) | 65.6% |
| Seizure frequency F1 | **45.2%** |
| Investigation F1 | 86.2% |
| Seizure type F1 | 82.0% |
| Medication temporality F1 | 67.2% |

## Smoke replay (3 records)

Run: `runs/exect_s4_smoke_gpt4_1_mini_20260520T070529Z`

Contract cleared (3/3 evaluated). Frequency F1 40.0% on 2-support subset — smoke is contract-only, not a performance gate.

## Cap-25 replay (25 records)

Run: `runs/exect_s4_validation_cap25_gpt4_1_mini_20260520T070616Z`

| Metric | v1.2 cap-25 | v1.1 cap-25 (`…064206Z`) |
| --- | ---: | ---: |
| Micro F1 (11 fam) | **69.2%** | 68.3% |
| Seizure frequency F1 | **49.1%** | 47.3% |
| Investigation F1 | **93.8%** | 83.3% |
| Seizure type F1 | 90.9% | 86.6% |
| Medication temporality F1 | 63.7% | 66.7% |
| Evidence support | 88.0% | 88.9% |

## Full validation replay (40 records)

Run: `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`

| Metric | v1.2 full | v1.1 full (`…064751Z`) | v1.0 full (`…001602Z`) |
| --- | ---: | ---: | ---: |
| Micro F1 (11 fam) | **65.5%** | 65.6% | 63.4% |
| Seizure frequency F1 | **45.7%** | 45.2% | 25.6% |
| Investigation F1 | **96.7%** | 86.2% | 93.3% |
| Seizure type F1 | 84.0% | 82.0% | 78.8% |
| Medication temporality F1 | 62.5% | 67.2% | 65.2% |
| Evidence support | 87.7% | 87.9% | 86.6% |

**Read:** v1.2 investigation guard delivers **+10.5pp** full investigation F1 without frequency regression (+0.5pp). **Freeze at v1.2** — error read: `docs/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md`.

**Do not:** reopen S3 v1.2, S2 v1.3, or S1 v4.10 on validation; compare eleven-family micro F1 to nine-family S3 headlines.
