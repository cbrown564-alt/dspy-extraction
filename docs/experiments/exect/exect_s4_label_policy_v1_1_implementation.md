# ExECT S4 Label Policy v1.1

Date: 2026-05-20

## Motivation

S4 v1.0 full validation (`runs/exect_s4_validation_full_gpt4_1_mini_20260520T001602Z`) established the eleven-family ladder baseline at **63.4%** micro F1 but **seizure frequency F1 was 25.6%**. Error read: `docs/experiments/exect/exect_s4_validation_full_gpt4_1_mini_inspection_20260520.md`.

Primary failure mode: benchmark surface mismatch — model emits near-miss quantified strings (`1 per month` vs gold `1 per 1 month`), omits qualitative changes, or collapses multi-label frequency blocks. Frozen S3 families (investigation **93.3%**, seizure **78.8%**) held; v1.1 targets **frequency only**.

## Changes

**Prompt version:** `exect_s4_field_family_v1_1_label_policy`

1. **`EXECT_S4_FREQUENCY_LABEL_POLICY_GUIDANCE`** — dual-cardinal `N per N period` template, zero-rate surfaces, multi-label retention, qualitative surfaces, prose prohibition.
2. **Policy examples** — dual-cardinal (`1 per 1 day` + `1 per 1 month`), zero-rate (`0 per 3 year`), multi-label block, seizure-free prose collapse.
3. **Signature + `seizure_frequency` output field** — expanded frequency instructions.
4. **S4-only bridges** (in `exect_s4.py`; S3 code unchanged):
   - `_repair_s4_seizure_frequency_surface` — insert missing time-period cardinal (`1 per month` → `1 per 1 month`); frequency-change synonyms; collapse seizure-free prose to `seizure free`
   - Applied inside `_recover_s4_seizure_frequency_raw_values` after seizure-type stripping

`exect_s3.py`, `exect_s2.py`, and `exect_s0_s1.py` are **unchanged**.

## Configs

- `configs/experiments/exect_s4_smoke_gpt4_1_mini.json`
- `configs/experiments/exect_s4_validation_cap25_gpt4_1_mini.json`
- `configs/experiments/exect_s4_validation_full_gpt4_1_mini.json`
- Qwen ladder replicas: `exect_s4_*_qwen35b_ollama.json`

## Validation

```powershell
uv run --extra dev pytest tests/test_exect_s4_program.py tests/test_exect_s4_scoring.py tests/test_exect_s4_gold_loader.py tests/test_experiment_configs.py -k exect_s4 -q
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s4_validation_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s4_validation_full_gpt4_1_mini.json --env-file .env
```

## Baseline to beat (v1.0 full, 40 records)

| Metric | v1.0 full (`…001602Z`) |
| --- | ---: |
| Micro F1 (11 fam) | 63.4% |
| Seizure frequency F1 | **25.6%** |
| Medication temporality F1 | 65.2% |
| Seizure type F1 | 78.8% |
| Investigation F1 | 93.3% |

## Cap-25 replay (25 records)

Run: `runs/exect_s4_validation_cap25_gpt4_1_mini_20260520T064206Z`

| Metric | v1.1 cap-25 | v1.0 cap-25 (`…001157Z`) |
| --- | ---: | ---: |
| Micro F1 (11 fam) | **68.3%** | 67.8% |
| Seizure frequency F1 | **47.3%** | 32.6% |
| Seizure type F1 | 86.6% | 92.3% |
| Investigation F1 | 83.3% | 90.9% |
| Medication temporality F1 | 66.7% | 65.9% |
| Evidence support | 88.9% | 87.7% |

Frequency **+14.7pp** on cap-25; seizure type −5.7pp (monitor only).

## Full validation replay (40 records)

Run: `runs/exect_s4_validation_full_gpt4_1_mini_20260520T064751Z`

| Metric | v1.1 full | v1.0 full (`…001602Z`) | S3 v1.2 full (`…235439Z`) |
| --- | ---: | ---: | ---: |
| Micro F1 (11 fam) | **65.6%** | 63.4% | 72.1% (9 fam) |
| Seizure frequency F1 | **45.2%** | 25.6% | n/a |
| Seizure type F1 | 82.0% | 78.8% | 78.1% |
| Investigation F1 | 86.2% | 93.3% | 93.1% |
| Medication temporality F1 | 67.2% | 65.2% | n/a |
| Annotated medication F1 | 72.6% | 72.0% | 81.4% |
| Comorbidity F1 | 56.6% | 57.1% | 59.8% |
| Diagnosis F1 | 92.5% | 91.4% | 92.5% |
| Evidence support | 87.9% | 86.6% | 90.1% |

**Read:** v1.1 delivers the intended frequency lift (**+19.6pp** full) without reopening S3 code. Investigation dropped −7.1pp vs v1.0 full (model variance in eleven-family pass); seizure type **+3.2pp** vs v1.0. Frequency remains below S3-era families but is no longer the dominant ladder gap.

**Freeze decision:** Record **S4 v1.1 full anchor** at `…064751Z`. Error read: `docs/experiments/exect/exect_s4_validation_full_v1_1_gpt4_1_mini_inspection_20260520.md`. Optional v1.2: qualitative frequency co-labels + investigation `unknown` guard (S4-only).

**Do not:** reopen S3 v1.2, S2 v1.3, or S1 v4.10 on validation; compare eleven-family micro F1 to nine-family S3 headlines.
