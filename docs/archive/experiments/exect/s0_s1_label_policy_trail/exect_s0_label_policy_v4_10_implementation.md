# ExECT Label-Policy v4.10 Implementation

Date: 2026-05-19

Prompt version: `exect_s0_s1_field_family_v4_10_label_policy`

## Target (post–v4.9 anchor)

v4.9 cleared specificity-collapse diagnosis co-list (**EA0188** diagnosis tokens) and prescription lamotrigine recovery (**EA0008**) but left **EA0188** seizure FN `secondary` and **EA0150** seizure FN `secondary`. Gold expects collapsed `secondary` tokens alongside or instead of full secondary generalised seizure surfaces. Scorer unchanged. v4.9 remains comparison anchor until this ladder clears.

## Changes

### Prompt (`EXECT_S0_S1_LABEL_POLICY_GUIDANCE` + policy examples)

- When specificity-collapse diagnosis context applies and the note names secondary generalised seizure(s), emit only `secondary` in `seizure_type`
- When the note names secondary generalised seizures without specificity-collapse context, co-list `secondary` alongside the full audited label
- Add `specificity_collapse_secondary_seizure_surface` and `secondary_token_co_list_with_full_phrase` policy examples

### Deterministic bridges (monolithic variant only)

| Bridge | Behavior |
| --- | --- |
| `specificity_collapse_seizure_surface` | When drug-refractory focal / occipital specificity-collapse note context + secondary generalised seizure phrasing, replace all seizure labels with `secondary` only |
| `secondary_token_co_listed` | When full secondary generalised seizures label is present without collapse context, co-add `secondary` |

Verify-repair and diagnosis-recall variants unchanged.

## Validation ladder

1. **Slice gate (37 records):** `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json`
2. **Cap-25:** `configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json`
3. **Full (40):** `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json --env-file .env
```

## Slice gate (37 records)

Run: `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T221928Z`

| Metric | v4.10 slice | v4.9 slice (`…220225Z`) | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **92.1%** | 90.9% | +1.2pp |
| Diagnosis F1 | 93.7% | 93.7% | 0 |
| Seizure F1 | **90.3%** | 87.0% | +3.3pp |
| Medication F1 | 92.5% | 92.5% | 0 |

**EA0188:** seizure `secondary` **cleared**. **EA0150:** seizure `secondary` **cleared**.

## Cap-25 (25 records)

Run: `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z`

| Metric | v4.10 cap-25 | v4.9 cap-25 | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **95.8%** | 96.3% | −0.5pp |
| Seizure F1 | **95.4%** | 93.8% | +1.6pp |

Cap-25 headline micro F1 dipped slightly; seizure F1 improved. Use full validation for promotion claims.

## Full validation (40 records)

Run: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`

| Metric | v4.10 full | v4.9 full | v4.8 full | Delta vs v4.9 |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 | **92.3%** | 91.2% | 88.7% | +1.1pp |
| Diagnosis F1 | 93.8% | 93.8% | 89.7% | 0 |
| Seizure F1 | **90.5%** | 87.2% | 87.2% | +3.3pp |
| Medication F1 | 92.8% | 92.8% | 89.4% | 0 |
| Evidence support | 95.8% | 95.9% | 95.8% | −0.1pp |

**v4.10 is the frozen monolithic dev anchor.** **EA0188** and **EA0150** seizure surfaces cleared on full validation. Residual **EA0150** diagnosis FN `epilepsy` (generic co-list) unchanged from v4.9.

## One-shot test holdout (40 records)

Config: `configs/experiments/exect_s0_s1_validation_test_gpt4_1_mini.json`  
Run: `runs/exect_s0_s1_validation_test_gpt4_1_mini_20260519T222615Z`

| Metric | Test (holdout) | Dev validation (`…221944Z`) | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **77.8%** | 92.3% | −14.5pp |
| Diagnosis F1 | 71.4% | 93.8% | −22.4pp |
| Seizure F1 | 66.0% | 90.5% | −24.5pp |
| Medication F1 | 92.7% | 92.8% | −0.1pp |
| Evidence support | 88.5% | 95.8% | −7.3pp |

**Interpretation (frozen — do not tune on test):**

- Dev-split gains from v3→v4.10 were concentrated in diagnosis and seizure label-policy bridges tuned against validation failures; medication policy generalized.
- The −14.5pp micro F1 gap supports the Kanban freeze: further record-specific bridges on the 40 dev records risk overfitting; test holdout is required before any promotion claim.
- 77.8% test micro F1 is still above the v3 dev anchor (67.8%) but well below v4.10 dev — treat 92.3% as a **partial S0/S1 dev diagnostic**, not generalization performance.
- Next Thread B step: **breadth pivot** (S2 field expansion, architecture ablation at fixed S1, or benchmark-reproduction infra) — see `docs/planning/kanban_plan.md`.

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_validation_test_gpt4_1_mini.json --env-file .env
```

## Prior analysis

`docs/experiments/exect/exect_s0_label_policy_v4_9_implementation.md`, `docs/experiments/exect/exect_s0_s1_validation_full_v4_4_inspection.md`, `docs/experiments/exect/exect_label_policy_prior_error_analysis_traceability_20260519.md`
