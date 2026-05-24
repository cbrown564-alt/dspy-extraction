# ExECT S5 Annotated Medication Guard - Inspection

Date: 2026-05-24  
Comparison group: `exect_s5_axis1_axis2_decomposition_gpt_full_validation_v1`  
decision_scope: **arm** (post-prediction medication guard; mechanism remains open for temporal evidence pruning)

## Purpose

Evaluate whether a narrow post-prediction annotated-medication guard can repair the ExECT S5 medication precision deficit without changing scorer semantics or regressing the other S5 core families.

## Run Artifacts

| Arm | Run ID | Records | Config |
| --- | --- | ---: | --- |
| S5 frequency pre-vocab baseline | `exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z` | 40 | `configs/experiments/exect_s5_frequency_pre_vocab_full_gpt4_1_mini.json` |
| S5 pre-vocab + AM guard cap-25 | `exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini_20260524T182134Z` | 25 | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini.json` |
| S5 pre-vocab + AM guard full validation | `exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini_20260524T182142Z` | 40 | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini.json` |

**Dataset / split:** ExECTv2, `exectv2_fixed_v1:validation`  
**Model/provider:** `gpt-4.1-mini` via `configs/models/gan_s0_gpt4_1_mini.json`  
**Schema / scorer:** `exect_s5_core_field_family`, `exect_s5_core_field_family_deterministic_v1`  
**Program variant:** `exect_s5_frequency_pre_vocab_am_guard_non_asm_brand_alias_v1`  
**Primitive:** `exect.medication.am_guard_non_asm_brand_alias.v1` at post-prediction interleaving position  
**Controls:** high-recall seizure-frequency pre-vocab candidates retained; no verifier, repair module, or medication-temporality family in S5.

## Results

| Metric | S5 pre-vocab baseline | AM guard cap-25 | AM guard full validation | Full delta vs baseline |
| --- | ---: | ---: | ---: | ---: |
| **annotated_medication F1** | 73.6% | 87.9% | **88.7%** | +15.1pp |
| annotated_medication precision | 59.0% | 78.4% | **79.7%** | +20.7pp |
| annotated_medication recall | 97.9% | 100.0% | **100.0%** | +2.1pp |
| diagnosis F1 | 90.0% | 93.0% | 90.0% | 0 |
| seizure_type F1 | 84.0% | 92.5% | 84.0% | 0 |
| investigation F1 | 96.7% | 93.8% | 96.7% | 0 |
| seizure_frequency F1 | 60.2% | 60.5% | 60.2% | 0 |
| **Micro F1** | 77.9% | 83.1% | **81.4%** | +3.5pp |

The full-validation guard clears the Kanban gate of `annotated_medication` F1 >80% and leaves the non-medication S5 families unchanged relative to the full pre-vocab baseline.

## Guard Behavior

The promoted narrow guard:

- drops non-ASM medications from `annotated_medication`
- repairs misspelled `eplim` / `eplim chrono` to the benchmark-facing `epilim chrono` surface
- maps standalone `Epilim` to `sodium valproate` for the audited benchmark view
- preserves `Lamictal` when the aligned evidence contains the brand surface
- deduplicates same-canonical medications while preserving explicit generic predictions where they are present

An earlier cap-25 rehearsal (`exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini_20260524T181821Z`) failed the medication gate at 78.8% F1 because it over-preferred brand surfaces. That run is diagnostic only; the corrected guard is represented by the `20260524T182134Z` cap run and `20260524T182142Z` full run.

## Residual Medication Errors

The remaining full-validation `annotated_medication` mismatches are all false positives:

| Pattern | Documents | Interpretation |
| --- | --- | --- |
| planned / suggested ASM | `EA0016`, `EA0053`, part of `EA0052` | Requires temporal evidence pruning, deliberately excluded from this guard. |
| previous / switched-from ASM | `EA0098`, `EA0131`, `EA0143`, `EA0188`, part of `EA0052` | Requires planned/history/future evidence guard. |
| ambiguous ASM/non-benchmark surface | `EA0059` (`gabapentin`) | Clinically plausible ASM but appears under a non-benchmark/current context. |
| missing or limited gold | `EA0078`, `EA0136` | Annotation-policy limitation; should not drive silent scorer changes. |

## Taxonomy Mapping

| Field | Value |
| --- | --- |
| dataset | `exect_v2` |
| clinical_task_family | `frequency`, `medication` |
| schema_complexity | `exect_s5` |
| program_architecture | `single_pass` |
| hybrid_balance_class | `H2_pre_deterministic`, `H1_post_deterministic` |
| interleaving_positions | `pre`, `during`, `post` |
| varied_factor | `interleaving_position` |
| outcome | **promote** as the current S5 medication precision guard arm |

## Decision

Promote `exect.medication.am_guard_non_asm_brand_alias.v1` for the ExECT S5 pre-vocab medication-precision arm. This is an **arm-level** promotion: it demonstrates that low-risk non-ASM filtering plus narrow brand/surface repair resolves the immediate S5 annotated-medication F1 deficit.

Do not treat medication temporal evidence pruning as closed. The next medication-specific variant, if pulled, should be separately preregistered as `am_guard_temporal_evidence_v1` or equivalent, because it would encode planned/history/future annotation-policy decisions rather than only surface/canonical medication repair.

## Validation

- `uv run --extra dev pytest tests/test_exect_medication_primitives.py tests/test_experiment_configs.py -q`
- `uv run python scripts/validate_primitives.py --errors-only`
- `uv run python scripts/validate_experiment_taxonomy.py --errors-only`
- `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini.json --env-file .env`
- `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini.json --env-file .env`

Primitive validation still reports pre-existing registry/catalog and adapter-extension warnings unrelated to this guard.
