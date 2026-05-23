# Gan S0 Candidate Builder Gap V1 GPT Slice Inspection

Date: 2026-05-23  
Status: G15 slice inspection  
Dataset/split: Gan 2026 synthetic validation enriched 25-record slice  
Program: `gan_frequency_s0_temporal_candidates_single_pass`  
Prompt: `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy`  
Model/provider: GPT 4.1-mini / OpenAI  
Scorer: `gan_frequency_deterministic_v1`  
Run: `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T093314Z`  
Control: `runs/gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z`

## Question

Does the preregistered deterministic candidate-builder gap surface translate the no-model coverage lift into GPT adjudication lift on the same enriched 25-record Gan S0 slice?

## Fixed Controls

- Same record IDs as the v1.4 control.
- Same prompt version, model config, structured output strategy, context policy, repair policy, and scorer.
- No examples and no verifier.
- Varied factor: deterministic candidate-builder implementation surface, `gan_s0_candidate_builder_gap_v1`.

## Results

| Metric | v1.4 control | Builder-gap v1 | Delta |
| --- | ---: | ---: | ---: |
| Candidate gold coverage | 5/25 | 23/25 | +18 records |
| Monthly accuracy | 36.0% | **92.0%** | +56.0pp |
| Purist category accuracy | 44.0% | **92.0%** | +48.0pp |
| Pragmatic category accuracy | 56.0% | **96.0%** | +40.0pp |
| Normalized-label accuracy | 28.0% | **84.0%** | +56.0pp |
| Schema validity | 100.0% | 100.0% | 0 |
| Evidence quote support | 100.0% | 100.0% | 0 |

## Rescues

The builder-gap run corrected 14 control predictions exactly or monthly-equivalently, including:

| Record | Gold | v1.4 control | Builder-gap v1 |
| --- | --- | --- | --- |
| `gan_13058` | `2 per 7 month` | `1 per 3 week` | `2 per 7 month` |
| `gan_13149` | `3 per year` | `1 per year` | `3 per year` |
| `gan_14562` | `3 per 6 month` | `3 per 7 month` | `3 per 6 month` |
| `gan_14628` | `2 per 2 month` | `2 per 3 month` | `2 per 2 month` |
| `gan_14689` | `3 per 2 month` | `2 per 2 month` | `3 per 2 month` |
| `gan_14792` | `1 per month` | `unknown` | `1 per month` |
| `gan_14821` | `1 per month` | `unknown` | `1 per month` |
| `gan_14965` | `1 per 3 month` | `unknown` | `1 per 3 month` |
| `gan_14973` | `1 per month` | `unknown` | `1 per month` |
| `gan_15127` | `5 per 13 month` | `4 per month` | `5 per 13 month` |
| `gan_15442` | `1 cluster per 4 day, 2 per cluster` | `unknown` | `1 cluster per 4 day, 2 per cluster` |
| `gan_16529` | `1 per 5 day` | `1 cluster per 5 day, multiple per cluster` | `1 per 5 day` |
| `gan_16645` | `5 per 7 month` | `3 cluster per month, 3 per cluster` | `5 per 7 month` |
| `gan_16750` | `6 per 7 month` | `unknown` | `6 per 7 month` |

## Residual Errors

Two monthly-frequency mismatches remain:

| Record | Gold | Prediction | Interpretation |
| --- | --- | --- | --- |
| `gan_15168` | `multiple per 15 month` | `unknown` | Candidate is now available, but the model abstained on vague myoclonic "jumps from time to time." |
| `gan_15193` | `multiple per 13 month` | `1 per 13 month` | Candidate is now available, but the model undercounted vague "absence from time to time" as a single event. Pragmatic category remains correct. |

Two seizure-free records remain normalized-label mismatches (`gan_13574`, `gan_13598`), but they are monthly/category correct because both gold and prediction map to no seizure information under current Gan scorer semantics.

## Interpretation

This is a strong mechanism signal that candidate recall, not another generic verifier or example layer, was the binding constraint on the enriched slice. Once the deterministic surface included the relevant gold labels, the same GPT prompt and model selected the correct frequency for most quantified and cluster residuals without sacrificing schema validity or evidence support.

## Caveats

This slice is enriched for failures and is not a full-validation estimate. The new builders are deterministic regex-style helpers tied to explicit evidence phrasings; they need broader validation before changing the full-validation operational default. Scorer semantics were not changed, and `seizure_frequency_number[0]` remains the only benchmark gold.

## Decision

Promote `gan_s0_candidate_builder_gap_v1` past the enriched-slice gate. The next useful step is a full-validation GPT 4.1-mini run or a cap-style validation on a broader validation sample, not Qwen transfer yet. Qwen transfer should wait until the broader GPT validation confirms that the builder expansion does not overfit the enriched slice.
