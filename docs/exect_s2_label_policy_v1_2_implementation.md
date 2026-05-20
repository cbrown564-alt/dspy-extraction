# ExECT S2 Label Policy v1.2

Date: 2026-05-19

## Motivation

Cap-25 v1.1 (`runs/exect_s2_validation_cap25_gpt4_1_mini_20260519T225159Z`) cleared the seizure gate (80.6% F1) but **comorbidity remained the main gap** (53.8% F1, 50% recall). Error read: `docs/exect_s2_validation_cap25_gpt4_1_mini_inspection_20260519.md`.

## Changes

**Prompt version:** `exect_s2_field_family_v1_2_label_policy`

1. **Comorbidity label-policy guidance** — affirmed history recall, meningioma surgery, stroke retained with atomized components, episodic migraine → migraine, measles surface, trisomy not trisomy 21.
2. **Policy examples** — meningioma surgery, affirmed history recall (meningitis + brain atrophy).
3. **Signature docstring** — comorbidity v1.2 boundaries.
4. **S2-only bridges** (in `exect_s2.py`):
   - `_normalize_s2_comorbidity_candidate` — meningioma surgery, episodic migraine, childhood measles, trisomy 21 → trisomy
   - `_recover_s2_comorbidity_raw_values` — stroke atomization retains `stroke`; drop seizure-history FPs (febrile seizure, etc.)
   - `_augment_s2_comorbidity_from_note` — bounded affirmed recall for meningitis, brain atrophy, arachnoid cyst, cortical dysplasia, measles, migraine(s), stroke when components present, meningioma surgery, jerk from jerks

S1 code in `exect_s0_s1.py` is **unchanged**.

## Configs

- `configs/experiments/exect_s2_smoke_gpt4_1_mini.json`
- `configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json`
- `configs/experiments/exect_s2_validation_full_gpt4_1_mini.json`

## Validation

```powershell
uv run --extra dev pytest tests/test_exect_s2_program.py tests/test_exect_s2_scoring.py tests/test_exect_s2_gold_loader.py tests/test_experiment_configs.py -k exect_s2 -q
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json --env-file .env
```

## Cap-25 replay (25 records)

Run: `runs/exect_s2_validation_cap25_gpt4_1_mini_20260519T225836Z`

| Metric | v1.2 cap-25 | v1.1 cap-25 (`…225159Z`) | v1 cap-25 (`…224038Z`) |
| --- | ---: | ---: | ---: |
| Micro F1 (5 fam) | **84.1%** | 79.7% | 66.4% |
| Seizure F1 | **83.1%** | 80.6% | 40.0% |
| Diagnosis F1 | 83.7% | 83.7% | 88.4% |
| Medication F1 | 93.3% | 91.8% | 81.7% |
| Investigation F1 | 90.9% | 90.9% | 85.7% |
| Comorbidity F1 | **74.3%** | 53.8% | 49.0% |
| Micro recall | **89.8%** | 80.3% | — |
| Evidence support | 89.3% | 88.4% | 87.1% |

Comorbidity recall was the main lever (+20.5pp F1 vs v1.1). Seizure family held above the v1.1 gate.

## Full validation (40 records)

Run: `runs/exect_s2_validation_full_gpt4_1_mini_20260519T230407Z`

| Metric | Full v1.2 (40) | Cap-25 v1.2 (25) |
| --- | ---: | ---: |
| Micro F1 (5 fam) | **80.6%** | 84.1% |
| Seizure F1 | 76.6% | 83.1% |
| Diagnosis F1 | 86.4% | 83.7% |
| Medication F1 | 91.8% | 93.3% |
| Investigation F1 | 91.5% | 90.9% |
| Comorbidity F1 | **63.6%** | 74.3% |
| Evidence support | 89.3% | 89.3% |

Error read: `docs/exect_s2_validation_full_gpt4_1_mini_inspection_20260520.md`

## Next gate

Optional v1.3 comorbidity iteration (jerk FP + full-split recall) or proceed to S2→S4 schema ladder at this baseline.
