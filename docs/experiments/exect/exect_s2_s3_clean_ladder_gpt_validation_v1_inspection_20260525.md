# ExECT S2/S3 Clean Ladder GPT Validation v1 — Inspection

Date: 2026-05-25  
decision_scope: **arm**

## Purpose

Bring S2 and S3 into the same clean-ladder style used by later S4/S5 work by composing already tested low-risk post-prediction guards, without changing scorer semantics.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | `exect_s2_field_family`, `exect_s3_field_family` |
| Comparison group | `exect_s2_s3_clean_ladder_gpt_validation_v1` |
| Program architecture | `single_pass` |
| Hybrid balance | `H1_post_deterministic` |
| Interleaving position | `post` |
| Varied factor | `implementation_variant` |
| decision_scope | arm |

## Variant

S2 clean ladder v1 combines:

- I0 investigation guard: remove out-of-scope ECG labels.
- C0/C1 comorbidity bridges: TBI atomization plus narrow spelling/plural surface repairs.
- Annotated-medication AM guard: non-ASM pruning plus narrow brand/surface repair from the S5 promoted guard.

S3 clean ladder v1 inherits the S2 clean-ladder stack and adds the K0/K1 epilepsy-cause CUIPhrase bridge.

## Run Artifacts

| Rung | Scope | Run ID | Config |
| --- | --- | --- | --- |
| S2 | cap-25 | `exect_s2_clean_ladder_v1_cap25_gpt4_1_mini_20260525T073152Z` | `configs/experiments/exect_s2_clean_ladder_v1_cap25_gpt4_1_mini.json` |
| S2 | full validation | `exect_s2_clean_ladder_v1_full_gpt4_1_mini_20260525T073213Z` | `configs/experiments/exect_s2_clean_ladder_v1_full_gpt4_1_mini.json` |
| S3 | cap-25 | `exect_s3_clean_ladder_v1_cap25_gpt4_1_mini_20260525T073204Z` | `configs/experiments/exect_s3_clean_ladder_v1_cap25_gpt4_1_mini.json` |
| S3 | full validation | `exect_s3_clean_ladder_v1_full_gpt4_1_mini_20260525T073224Z` | `configs/experiments/exect_s3_clean_ladder_v1_full_gpt4_1_mini.json` |

Model/provider: GPT 4.1-mini via `configs/models/gan_s0_gpt4_1_mini.json`  
Split: `exectv2_fixed_v1:validation`  
Scorers: `exect_s2_field_family_deterministic_v1`, `exect_s3_field_family_deterministic_v1`

## Full Validation Results

| Rung | Baseline run | Baseline micro F1 | Clean-ladder run | Clean micro F1 | Delta |
| --- | --- | ---: | --- | ---: | ---: |
| S2 | `exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` | 80.9% | `exect_s2_clean_ladder_v1_full_gpt4_1_mini_20260525T073213Z` | **82.7%** | +1.8pp |
| S3 | `exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` | 72.1% | `exect_s3_clean_ladder_v1_full_gpt4_1_mini_20260525T073224Z` | **74.4%** | +2.3pp |

## Family Read

| Rung | Diagnosis | Seizure type | Medication | Investigation | Comorbidity | S3-only read |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| S2 clean | 88.9% | 71.0% | **92.9%** | **93.1%** | **72.5%** | — |
| S3 clean | 92.5% | 78.1% | **89.5%** | 93.1% | 61.9% | cause 22.2%, birth 25.0%, onset 13.3%, when-diagnosed 28.6% |

S2 gains are concentrated in low-risk post guards: medication, investigation, and comorbidity improve versus the frozen S2 v1.3 profile while diagnosis/seizure behavior remains unchanged. S3 gains come from inherited medication cleanup plus K0/K1 cause normalization; sparse S3-only slots remain noisy and low-support.

## Decision

Promote S2/S3 clean-ladder v1 as the **GPT operational comparison rung** for schema ladder plots, with arm-level scope. Do not claim mechanism closure for comorbidity or S3 sparse-family extraction.

Qwen follow-up configs are ready:

- `configs/experiments/exect_s2_clean_ladder_v1_full_qwen35b_ollama.json`
- `configs/experiments/exect_s3_clean_ladder_v1_full_qwen35b_ollama.json`

Run those via detached/external PowerShell per the Qwen latency policy, then compare against prior Qwen S2/S3 full-validation anchors.

## Validation

- `uv run --extra dev pytest tests/test_exect_s2_program.py tests/test_exect_s3_program.py tests/test_experiment_configs.py -q`
- `uv run python scripts/validate_experiment_taxonomy.py --errors-only`
- `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_clean_ladder_v1_cap25_gpt4_1_mini.json --env-file .env`
- `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s3_clean_ladder_v1_cap25_gpt4_1_mini.json --env-file .env`
- `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_clean_ladder_v1_full_gpt4_1_mini.json --env-file .env`
- `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s3_clean_ladder_v1_full_gpt4_1_mini.json --env-file .env`

Taxonomy validation still reports the pre-existing missing canonical run warning for `gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini`.
