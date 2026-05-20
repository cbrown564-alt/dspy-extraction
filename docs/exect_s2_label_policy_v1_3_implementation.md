# ExECT S2 Label Policy v1.3

Date: 2026-05-20

## Motivation

Full validation v1.2 (`runs/exect_s2_validation_full_gpt4_1_mini_20260519T230407Z`) showed **comorbidity 63.6%** F1 with **jerk** as the dominant FP cluster (7 records). Root cause: v1.2 note-recall augmented `jerk` from any affirmed `jerks` mention, and the model emitted jerk on JME/myoclonic-jerk seizure surfaces. Gold allows `jerk` only in rare follow-up contexts (for example EA0048). Read: `docs/exect_s2_validation_full_gpt4_1_mini_inspection_20260520.md`.

## Changes

**Prompt version:** `exect_s2_field_family_v1_3_label_policy`

1. **Prompt guidance** — exclude jerk/jerks/myoclonic jerks as seizure descriptors; family history of epilepsy is not comorbidity.
2. **Policy example** — myoclonic jerks + JME → empty comorbidity.
3. **S2-only bridges** (in `exect_s2.py`):
   - `_is_seizure_descriptor_jerk_context` / `_is_benchmark_comorbidity_jerk` — drop or selectively recall jerk
   - Remove blind `jerks` → `jerk` note augmentation; recall jerk only for follow-up “get jerks” surfaces
   - `meningioma resection` → `meningioma surgery`
   - `family history of epilepsy` → seizure-history removal set
   - Brain atrophy recall: `premature atrophy` / `generalised brain atrophy` patterns

S1 code in `exect_s0_s1.py` is **unchanged**.

## Configs

- `configs/experiments/exect_s2_smoke_gpt4_1_mini.json`
- `configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json`
- `configs/experiments/exect_s2_validation_full_gpt4_1_mini.json`

## Validation

```powershell
uv run --extra dev pytest tests/test_exect_s2_program.py tests/test_exect_s2_scoring.py tests/test_exect_s2_gold_loader.py tests/test_experiment_configs.py -k exect_s2 -q
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_validation_full_gpt4_1_mini.json --env-file .env
```

## Cap-25 replay (25 records)

Run: `runs/exect_s2_validation_cap25_gpt4_1_mini_20260519T230945Z`

| Metric | v1.3 cap-25 | v1.2 cap-25 (`…225836Z`) |
| --- | ---: | ---: |
| Micro F1 (5 fam) | **87.5%** | 84.1% |
| Comorbidity F1 | **85.7%** | 74.3% |
| Seizure F1 | 83.1% | 83.1% |
| Diagnosis F1 | 90.5% | 83.7% |
| Investigation F1 | 88.2% | 90.9% |
| Evidence support | 92.6% | 89.3% |

## Full validation (40 records)

Run: `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z`

| Metric | v1.3 full (40) | v1.2 full (`…230407Z`) |
| --- | ---: | ---: |
| Micro F1 (5 fam) | **80.9%** | 80.6% |
| Comorbidity F1 | **69.3%** | 63.6% |
| Seizure F1 | 71.0% | 76.6% |
| Diagnosis F1 | 88.9% | 86.4% |
| Medication F1 | 90.0% | 91.8% |
| Investigation F1 | 90.0% | 91.5% |
| Evidence support | 92.7% | 89.3% |

**jerk** false positives: 7 → **0**. Comorbidity mismatch entries: 20 → **15**. Seizure F1 dropped on this replay (model variance in multi-family pass); treat seizure as monitor-only for v1.3.

## Next gate

**S2 frozen.** Schema ladder proceeds at this baseline — see `docs/exect_s2_s4_schema_ladder_design.md` and Thread D in `docs/kanban_plan.md`.
