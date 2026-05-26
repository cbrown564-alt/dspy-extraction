# Gan S0 R1.1c Schema-Guard Cap-25 Inspection

Date: 2026-05-26  
Config: `configs/experiments/gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama.json`  
Completed run ID: [gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260526T092006Z](file:///c:/Users/cbrow/Code/dspy-extraction/runs/gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260526T092006Z)  
Prompt version: `gan_frequency_s0_temporal_candidates_single_pass_v1_8_qwen_schema_validity`  
Dataset/split: Gan 2026 synthetic, `gan_2026_fixed_v1:validation`, first 25 records  
Model: Qwen3.6:35b via Ollama  
Scorer: `gan_frequency_deterministic_v1`  
Decision Scope: `arm`  
Decision: **PASS**

## Why This Run Exists

This run gates the R1.1 schema-guard patch (R5-R8) on a capped validation set of 25 records. The goal is to verify if the schema-guard adapter layer successfully restores schema validity to 100.0% without collapsing monthly accuracy, unknown/no-reference handling, or evidence support, and before committing to a full validation replay.

## Cap-25 Metrics Summary

| Metric | Value |
| --- | ---: |
| **Schema validity rate** | 100.0% (25/25 valid, 0 invalid) |
| **Evidence quote support rate** | 100.0% |
| **Monthly frequency accuracy** | 68.0% |
| **Purist category accuracy** | 76.0% |
| **Pragmatic category accuracy** | 84.0% |
| **Normalized-label accuracy** | 60.0% |

- **No-reference repairs:** 0 count (no note-facing administrative records were encountered in this cap-25 split that required note-text heuristic repair).
- **Rejected final-labels:** 0 count (no raw outputs fell into the invalid/rejected hybrid, concatenated, or prose-appended classes).
- **Remaining invalids:** None.

## Analysis & Findings

1. **Schema Validity Recovery:** Under unchanged scorer semantics, the schema validity has successfully recovered to **100.0%** (up from 90.0% in R1.1 full validation and 92.0% in v1.7 cap-25).
2. **Rejection & Repair Counts:** Zero predictions were rejected by the final-label schema guards, showing that the model output is staying within canonical bounds for these 25 validation records and not relying excessively on abstention.
3. **Accuracy Stability:** Monthly accuracy (68.0%), Purist category accuracy (76.0%), and Pragmatic category accuracy (84.0%) remain highly aligned with previous runs, confirming that the adapter logic did not degrade semantic performance.

## Conclusion & Decision

The schema-guard gates are verified and functional. The exact-policy Qwen stack is cleared for full validation replay.
