# Gan S0 R1.1 Schema-Guard Full Validation Inspection

Date: 2026-05-26  
Config: `configs/experiments/gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama.json`  
Completed run ID: [gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T092508Z](file:///c:/Users/cbrow/Code/dspy-extraction/runs/gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T092508Z)  
Prompt version: `gan_frequency_s0_temporal_candidates_single_pass_v1_8_qwen_schema_validity`  
Dataset/split: Gan 2026 synthetic, `gan_2026_fixed_v1:validation`, all 299 records  
Model: Qwen3.6:35b via Ollama  
Scorer: `gan_frequency_deterministic_v1`  
Decision Scope: `mechanism`  
Decision: **PASS**

## Why This Run Exists

This run performs full validation on all 299 records in the Gan validation split. It tests the R1.1 exact-policy Qwen stack protected by the R5-R8 schema-guard adapter layer. The goal is to verify if the schema guards stabilize the Qwen stack at scale, improving the previous R1.1 schema validity rate (originally 90.0%) and ensuring that no malformed outputs masquerade as canonical predictions.

## Metrics Summary (Before vs After Schema-Guard Fix)

| Metric | R1.1 Original Full Run | R1.1 Schema-Guard Full Run (Post-Bugfix) |
| --- | ---: | ---: |
| **Schema validity rate** | 90.0% | **93.3%** |
| **Evidence quote support** | 98.9% | **98.9%** |
| **Monthly frequency accuracy** | 70.3% | **71.3%** |
| **Purist category accuracy** | 78.4% | **79.2%** |
| **Pragmatic category accuracy** | 83.3% | **83.9%** |
| **Normalized-label accuracy** | 58.0% | **59.5%** |
| **Total Evaluated** | 299 | **299** |
| **Valid Predictions** | 269 | **279** |
| **Invalid Predictions** | 30 | **20** |

## Rejection & Repair Breakdown

A total of 20 predictions (6.7%) were rejected/abstained from the 299 evaluated records:
- **`unknown_quantified_hybrid` rejections:** 13 records (e.g. malformed `unknown, N per ...` patterns)
- **`multiple_frequency_labels` rejections:** 5 records (multiple rates concatenated)
- **`prose_appended_label` rejections:** 1 record (canonical label followed by prose)
- **`malformed_cluster_unknown_slot` rejections:** 1 record
- **Clean Model Abstentions:** 1 record (`gan_11874` predicted null naturally)

Additionally, **4 leading inequality predictions** (`gan_115`, `gan_17`, `gan_22`, `gan_31`) that previously caused float parsing errors were successfully intercepted, stripped, and repaired to canonical rates (e.g. `≤ 2 per day` -> `2 per day`), boosting both monthly and category accuracies.

## Key Bug Fix Applied

During this workstream, a minor bug was identified and resolved in the adapter pipeline:
- **Issue:** `canonicalize_leading_inequality_label(label)` was receiving the raw `label` containing double quotes (e.g., `'"\u2264 2 per day"'`), which prevented regex matching of the leading inequality operator.
- **Fix:** Updated the pipeline to pass `normalized_label` (which has quotes stripped) into the canonicalization helper, allowing the repairs to execute successfully.

## Conclusion

The R5-R8 schema-guard implementation successfully protects the Qwen stack at scale, elevating the schema validity to **93.3%** (with the remaining 6.7% representing intentional rejections converted to clean abstentions rather than format violations) and providing a minor boost to overall extraction accuracy.
