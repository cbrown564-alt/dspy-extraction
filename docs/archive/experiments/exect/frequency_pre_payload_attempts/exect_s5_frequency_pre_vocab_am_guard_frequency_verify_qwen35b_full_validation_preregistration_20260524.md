# ExECT S5 Frequency Verifier v1 Qwen35b Full Validation — Pre-Registration

Date: 2026-05-24  
Status: **Pre-registration before L1.1 Qwen run**  
Comparison group: `exect_s5_frequency_verify_v1_model_comparison`  
GPT anchor: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini_20260524T195813Z`  
Kanban: L1.1 in [kanban_plan.md](../../planning/kanban_plan.md)  
Parent review: [24h_progress_and_local_model_gap_review_20260524.md](../synthesis/24h_progress_and_local_model_gap_review_20260524.md)

## Research Question

Does the **paper-frozen ExECT S5 stack** (high-recall pre-vocab candidates → extraction → reject-only frequency verifier v1 + A3 prompt policy → AM guard) transfer to **Qwen3.6:35b** on the full 40-record ExECTv2 validation split with acceptable per-family performance vs the GPT 4.1-mini anchor?

This is the first local-model run on any promoted S5 hybrid stack.

## Decision Relevance

| Outcome | Action |
| --- | --- |
| **Accept local S5 arm** | Pooled micro ≥ GPT −5pp **and** seizure_frequency F1 ≥ GPT −8pp; each guard family within −3pp |
| **Hold local S5** | Mixed profile — document best local sub-variant; do not claim local deployment parity |
| **Reject local S5 arm** | Schema validity < 90% after smoke, or pooled micro < GPT −10pp without compensating freq gain |

GPT anchor (full validation):

| Family / metric | GPT 4.1-mini |
| --- | ---: |
| Pooled micro F1 | 85.5% |
| seizure_frequency F1 | 72.3% |
| diagnosis F1 | 90.0% |
| seizure_type F1 | 84.0% |
| annotated_medication F1 | 88.7% |
| investigation F1 | 96.7% |

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Comparison group | `exect_s5_frequency_verify_v1_model_comparison` |
| Primary varied factor | `model_track` = `qwen35b` |
| Program variant | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1` (fixed) |
| decision_scope | `arm` (model comparison only) |
| Mechanism closure allowed? | No |

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` (40 records) |
| Model | Qwen3.6:35b via Ollama (`configs/models/exect_qwen35b_ollama.json`) |
| Scorer | `exect_s5_core_field_family_deterministic_v1` |
| Program | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1` |
| Prompt | `exect_s4_field_family_v1_2_label_policy` |
| Verifier | `frequency_evidence_verify_reject_only_v1` |
| AM guard | `am_guard_non_asm_brand_alias.v1` |
| Candidate policy | High-recall pre-vocab (unchanged vs GPT) |
| ChainOfThought / optimizers | **None** (per Qwen latency policy) |

## Varied Factor

| Component | Treatment |
| --- | --- |
| Model track | Qwen3.6:35b / Ollama replaces GPT 4.1-mini / OpenAI |

All other stack components match the GPT paper-frozen run.

## Configs

| Arm | Config |
| --- | --- |
| Smoke (3 records) | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_smoke_qwen35b_ollama.json` |
| Full validation | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_qwen35b_ollama.json` |

## Acceptance Gates (Full Validation)

| Gate | Criterion |
| --- | --- |
| Primary — pooled micro | ≥ **80.5%** (GPT 85.5% − 5pp) |
| Primary — seizure_frequency F1 | ≥ **64.3%** (GPT 72.3% − 8pp) |
| Guard families | diagnosis, seizure_type, annotated_medication, investigation each ≥ GPT −3pp |
| Schema validity | ≥ 95% on full split |
| Evidence support | ≥ 90% on full split |

## Stopping Rules

Abort or hold if:

1. Ollama connection errors persist for > 3 consecutive records.
2. Smoke (3 records) schema validity < 100%.
3. First 10 full-validation records show schema validity < 90%.

## Latency Guard

- Model adapter timeout: 1800s per call (`exect_qwen35b_ollama.json`).
- S5 verify stack uses **two LLM calls per record** (extract + verifier); expect multi-hour runtime on partial CPU offload.
- Run smoke before full validation.
- Record GPU residency / RAM offload in inspection doc.

## Forbidden Changes

- Scorer, loader, split, candidate-builder output, gold labels
- Verifier policy version (v1 only — v2 is GPT-gated separately)
- High-precision candidate pruning (rejected arm)
- Medication temporal guard (rejected A4 arm)

## Verification Plan

1. Config contract: `uv run pytest tests/test_experiment_configs.py -k "exect_s5_frequency_verify.*qwen35b"`
2. Smoke: `uv run python -m clinical_extraction.experiments.run configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_smoke_qwen35b_ollama.json`
3. Full validation only after smoke passes
4. Inspection doc: `docs/experiments/exect/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_qwen35b_full_validation_inspection_YYYYMMDD.md`
5. Side-by-side comparison (L1.2): per-family GPT vs Qwen table

## Skills

`dspy-experiment-design`, `model-config-compatibility`, `experiment-run-lifecycle`, `exect-label-policy-alignment`, `windows-portability`
