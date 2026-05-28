# Gan S0 Self-Consistency Variance Probe Decision Report (R13/R37)

Date: 2026-05-28  
Comparison Group: `gan_s0_self_consistency_compute_allocation_gpt_cap25_v1`  
Status: Completed & Evaluated (GPT 4.1-mini and Qwen 3.6:35b)

## Executive Summary

The R13 compute-allocation grid evaluated whether repeated sampling (5x) and majority-vote aggregation (S1-S4) improve Gan S0 monthly frequency extraction accuracy and whether output variance acts as a reliable proxy for prediction instability.

**Decision:** **REJECT/HOLD** self-consistency for Gan S0. On both GPT 4.1-mini and Qwen 3.6:35b, self-consistency yielded **exactly 0.0pp** accuracy improvement (remaining at **96.0%** for GPT and **76.0%** for Qwen across all arms S1-S4). Because the models were completely stable (zero variance/disagreements detected), self-consistency adds 5x latency and API cost without any diagnostic or performance benefits.

---

## Taxonomy Block

```json
{
  "dataset": "gan_2026",
  "schema_complexity": "gan_s0",
  "clinical_task_family": "frequency",
  "comparison_group": "gan_s0_self_consistency_compute_allocation_gpt_cap25_v1",
  "stage_graph_id": "g2_candidates_adjudicate",
  "varied_factor": "compute_allocation_repeated_sampling",
  "decision_scope": "arm",
  "intended_decision": "reject_self_consistency"
}
```

---

## Run Metadata & Configs

| Arm / Model | Model Config | Run Directory |
| --- | --- | --- |
| **S0** Control (GPT-4) | `configs/models/gan_s0_gpt4_1_mini_temp0_7.json` | `runs/gan_s0_self_consistency_s0_single_sample_cap25_gpt4_1_mini_20260528T000218Z` |
| **S0** Control (Qwen) | `configs/models/gan_s0_qwen35b_ollama_temp0_7.json` | `runs/gan_s0_self_consistency_s0_single_sample_cap25_qwen35b_20260528T005912Z` |
| **S1-S4** 5x (GPT-4) | `configs/models/gan_s0_gpt4_1_mini_temp0_7.json` | `runs/gan_s0_self_consistency_sample5_cap25_gpt4_1_mini_20260528T000203Z` |
| **S1-S4** 5x (Qwen) | `configs/models/gan_s0_qwen35b_ollama_temp0_7.json` | `runs/gan_s0_self_consistency_sample5_cap25_qwen35b_20260528T010925Z` |

---

## Metrics & Disagreement Analysis

| Model | Arm | Monthly Acc | Disagreements | True Positives | False Positives | False Negatives | True Negatives |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **GPT 4.1-mini** | **S0 (Control)** | **96.0%** | - | - | - | - | - |
| | **S1-S4 (5x)** | **96.0%** | 0 | 0 | 0 | 1 | 24 |
| **Qwen 3.6:35b** | **S0 (Control)** | **76.0%** | - | - | - | - | - |
| | **S1-S4 (5x)** | **76.0%** | 0 | 0 | 0 | 6 | 19 |

- **True Positives:** Disagreed and S0 was wrong.
- **False Positives:** Disagreed and S0 was right.
- **False Negatives:** Stable and S0 was wrong (the model was confidently and consistently incorrect).
- **True Negatives:** Stable and S0 was right.

### Key Findings
1. **Absolute Stability:** Despite setting the sampling temperature to 0.7, there was **zero variance** (disagreement rate = 0%) across all 5 repeated runs of each record on both models.
2. **Confidently Wrong:** In cases where the baseline model failed (e.g. `gan_15193` on GPT-4, or `gan_13123`, `gan_13149`, `gan_14214` on Qwen), the model repeated the exact same error across all 5 samples.
3. **API Cost/Latency Penalty:** Multi-sampling results in a direct **500% increase** in API cost/local Ollama generation time with zero accuracy utility.

---

## Decision & Gates

- **Action:** **REJECT/HOLD** self-consistency for Gan S0. Do not promote this mechanism.
- **Guidance:** Retain single-sample inference with temperature 0.0 for clinical extraction stability and efficiency.

## Open Cells
- Sweeping self-consistency over harder ExECT S5 diagnosis schemas (which are more prone to variance than S0 frequency values).
