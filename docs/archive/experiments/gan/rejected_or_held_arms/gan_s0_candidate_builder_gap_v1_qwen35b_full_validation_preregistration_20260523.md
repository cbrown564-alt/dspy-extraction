# Gan S0 Candidate Builder Gap V1 Qwen35b Full Validation — Pre-Registration

Date: 2026-05-23  
Status: **Pre-registration before Qwen run**  
Comparison group: `gan_s0_candidate_builder_gap_v1_model_comparison`  
GPT anchor rerun: `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md`  
Parent audit: `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`  
Kanban: `docs/planning/kanban_plan.md`  

## Research Question

Does the deterministic candidate-builder gap v1 surface (which improved GPT-4.1-mini's monthly accuracy from 68.1% to 80.6%) transfer its performance lift to the local open-source model **Qwen3.6:35b**? Specifically, does Qwen3.6:35b with the new builder-gap v1 candidate surface beat its F0 baseline of **48.0%** (cap-25)?

## Decision Relevance (Stopping / Action Rule)

This run evaluates the model transferability of the `gan_s0_candidate_builder_gap_v1` surface:
- **Decision to change**: If Qwen3.6:35b achieves a monthly-frequency accuracy of **>= 70%** on the validation split, we will accept the Qwen transfer arm as highly viable and unblock it for potential operational promotion.
- **Arm rejection**: If Qwen3.6:35b fails to exceed 60% monthly-frequency accuracy, or if its schema validity falls below 90% or evidence support falls below 85%, we will reject the Qwen transfer arm for this surface and retain the GPT 4.1-mini/Gemini-based hosted tracks.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Comparison group | `gan_s0_candidate_builder_gap_v1_model_comparison` |
| Primary varied factor | `model_track` = `qwen35b` |
| implementation_variant | `gan_s0_candidate_builder_gap_v1` (fixed) |
| decision_scope | `arm` (model comparison only) |
| Mechanism closure allowed? | No |

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` (299 records) |
| Model | Qwen3.6:35b via Ollama (`configs/models/gan_s0_qwen35b_ollama.json`) |
| Scorer | `gan_frequency_deterministic_v1` |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` |
| Builders | `gan_s0_candidate_builder_gap_v1` (in `src/clinical_extraction/gan/temporal_candidates.py`) |
| ChainOfThought / optimizers | **None** (per Qwen latency policy) |

## Latency Guard

- **Timeout**: The model adapter timeout is set to 600.0 seconds per record.
- **Estimated Run Time**: Total run time is expected to be under 2 hours for the full 299 records, assuming standard GPU acceleration for local Ollama.
- **Resource Monitoring**: Ensure no other large model processes are running concurrently on the host.

## Stopping Rules

The execution will be aborted immediately if:
1. Connection errors to the local Ollama instance (`http://localhost:11434/v1`) persist for more than 3 consecutive records.
2. The schema validity rate drops below **90%** after the first 25 records.
3. The evidence quote support rate drops below **85%** after the first 25 records.

## Verification plan

- Verify configuration validity: `uv run pytest tests/test_experiment_configs.py`
- Run a local smoke check on 3 records before initiating the full validation run.
- Monitor the run output via the generated JSON files in the `runs` directory.

## Skills

`model-config-compatibility`, `experiment-run-lifecycle`, `dspy-experiment-design`, `windows-portability`.
