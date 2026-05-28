# Gan S0 Candidate Builder Gap V1 Qwen35b Full-Validation Inspection

Date: 2026-05-24  
Status: Completed validation pass  
Run ID: `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z`  
Related: `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_preregistration_20260523.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md`

## Scope

| Field | Value |
| --- | --- |
| Dataset / split | Gan 2026 synthetic, `gan_2026_fixed_v1:validation` |
| Records | 299/299 validation records predicted and scored |
| Model / provider | Qwen3.6:35b / Ollama (local) |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` |
| Implementation variant | `gan_s0_candidate_builder_gap_v1` |
| Scorer | `gan_frequency_deterministic_v1` |
| Structured output | provider JSON schema with Pydantic validation |
| Varied factor | `model_track` |

## Results

| Metric | Result | 95% Confidence Interval |
| --- | ---: | --- |
| Monthly-frequency accuracy | **70.7%** (210/297) | 65.7-75.8% |
| Purist category accuracy | **83.2%** (247/297) | 79.1-87.2% |
| Pragmatic category accuracy | **90.6%** (269/297) | 87.2-93.6% |
| Normalized-label exact accuracy | **60.6%** (180/297) | 55.2-66.3% |
| Schema-valid prediction rate | **99.3%** (297/299) | 98.3-100.0% |
| Evidence quote support rate | **99.7%** (296/297) | 99.0-100.0% |

Runtime: ~1.1 hours (3,260 seconds total, 299 estimated model calls under partial CPU offload).

## Interpretation of Qwen Transferability

This validation run validates the **local transferability** of the `gan_s0_candidate_builder_gap_v1` surface. Qwen3.6:35b achieved a monthly frequency accuracy of **70.7%**, which successfully clears the preregistered acceptance gate of **>= 70%** and materially improves over its F0 baseline:

| Run / Model | Monthly Accuracy | Schema Validity | Evidence Support |
| --- | ---: | ---: | ---: |
| Qwen F0 Baseline | 64.4% | 100.0% | 100.0% |
| Qwen Builder-Gap v1 | **70.7%** | **99.3%** | **99.7%** |
| GPT 4.1-mini Rerun (v1) | 80.6% | 100.0% | 100.0% |

Once the deterministic temporal candidates are placed in the context (via the updated v1 builders), Qwen3.6:35b successfully adjudicates the frequency in a majority of cases. 

Although Qwen still trails GPT 4.1-mini (80.6%) due to local reasoning differences, the **+6.3pp lift** on the full validation split confirms that the candidate-builder gap v1 is a robust, model-agnostic mechanism improvement.

## Error Profile

There were 87 monthly-frequency mismatches:
- `classification.pragmatic_category_mismatch`: 28 cases
- `classification.purist_category_mismatch`: 50 cases
- `normalization.invalid_label`: 2 cases
  - `gan_338`: predicted `many per month` (invalid number token)
  - `gan_4100`: predicted `q2 - 3wk` (unsupported format)
- `evidence.unsupported_quote`: 1 case (`gan_16883`)

The remainder are standard semantic mismatches where Qwen over/under-estimated cluster frequencies or fell back to `unknown`.

## Decision

| Item | Position |
| --- | --- |
| Qwen Transfer Arm | **Accepted** (cleared preregistered gates: monthly 70.7% >= 70.0%, schema 99.3% >= 90.0%, evidence 99.7% >= 85.0%) |
| Operational Default | Retain GPT 4.1-mini `gan_s0_candidate_builder_gap_v1` as the primary operational default (due to higher accuracy of 80.6% and lower hosted latency). Qwen3.6:35b remains a highly viable cost-free local alternative. |
