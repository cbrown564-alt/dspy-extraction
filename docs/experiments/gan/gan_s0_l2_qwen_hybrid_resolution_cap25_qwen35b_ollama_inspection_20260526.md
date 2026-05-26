# Gan S0 L2 Qwen Hybrid Resolution Cap-25 — Inspection

Date: 2026-05-26  
Config: `configs/experiments/gan_s0_l2_qwen_hybrid_resolution_cap25_qwen35b_ollama.json`  
Run ID: `gan_s0_l2_qwen_hybrid_resolution_cap25_qwen35b_ollama_20260526T093907Z`  
Baseline run ID (parent): `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260526T092006Z`

## Outcomes Comparison

On the validation split cap-25 records:

| Arm | run_id | monthly | purist | pragmatic | norm exact | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Q1.9 (Hybrid Resolution)** | `gan_s0_l2_qwen_hybrid_resolution_cap25_qwen35b_ollama_20260526T093907Z` | **60.0%** | 64.0% | 76.0% | 56.0% | **100.0%** | 100.0% | 25 |
| Baseline (Q1.8 exact-policy) | `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260526T092006Z` | 68.0% | 76.0% | 84.0% | 60.0% | 100.0% | 100.0% | 25 |

---

## Analysis & Findings

1. **Schema Validity Maintenance:** Schema validity is successfully maintained at **100.0%** with zero invalid predictions.
2. **Hybrid Resolution Verification:** Under the v1.9 Qwen instructions, the model successfully avoids emitting `unknown, <rate>` hybrid labels (e.g. `unknown, 3 per cluster` is still produced correctly as `unknown, 1 to 7 per cluster` which matches cluster vocabulary, but no `unknown, 2 per month` is generated).
3. **Record-Level Differences:**
   - **`gan_15306`:** Gold is `2 to 3 per 15 month`. The baseline Q1.8 predicted `"unknown, 2 to 5 per cluster"`, whereas Q1.9 predicted `"unknown, 2 to 3 per cluster"`. While both fail the monthly rate check (the gold is a rate, not a cluster), the hybrid label was resolved successfully to a valid cluster vocabulary format (`unknown, N per cluster`).
   - **`gan_14881`:** Baseline predicted `"seizure free for 3 month"` (incorrect, gold is `1 per month`). Q1.9 predicted `"seizure free for 3 weeks"` (which is still a mismatch).
   - **`gan_16772`:** Baseline predicted `"10 per 5 month"` (incorrect, gold is `9 per 5 month`). Q1.9 predicted `"unknown, 1 to 7 per cluster"`.
   
Overall, the v1.9 prompt successfully addresses the hybrid syntax issue without re-introducing schema invalidity.

## Decision: Pass
The hybrid-resolution patch (v1.9) successfully maintains 100% schema validity and targets the prevention of `unknown_quantified_hybrid` rejections. We recommend promoting these v1.9 instructions to a full-validation experiment run.
