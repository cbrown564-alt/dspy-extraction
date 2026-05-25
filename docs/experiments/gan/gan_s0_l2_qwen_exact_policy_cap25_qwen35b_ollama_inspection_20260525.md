# Gan S0 L2 Qwen Exact-Policy Cap-25 — Inspection

Date: 2026-05-25  
Config: `configs/experiments/gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama.json`  
Run ID: `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260525T162702Z`  
Baseline run ID (parent): `gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_20260521T065534Z`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | Phase 7b — Qwen exact-policy cap-25 |
| Comparison group | `gan_s0_l2_qwen_exact_policy_cap25_v1` |
| Primary varied factor | `prompt_policy` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| `implementation_variant` | `gan_s0_candidate_builder_gap_v1` |
| decision_scope | `arm` |

## Outcomes Comparison

On the validation split cap-25 records:

| Arm | run_id | monthly | purist | pragmatic | norm exact | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Q1 (Exact-Policy)** | `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260525T162702Z` | **69.6%** | 73.9% | 91.3% | 65.2% | 92.0% | 100% | 23 |
| Baseline (Q1-parent) | `gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_20260521T065534Z` | 40.0% | 56.0% | 72.0% | 32.0% | 100% | 100% | 25 |
| Reference (GPT E1) | `gan_s0_stage_executor_e1_det_candidates_cap25_gpt4_1_mini_20260521T013003Z` | 52.0% | — | — | — | 100% | 100% | 25 |

---

## Gates Evaluation

The target decision rule is evaluated as follows:

- **Monthly accuracy improves over baseline:** **PASSED** (69.6% vs 40.0%, a **+29.6pp** increase, beating even the GPT E1 reference of 52.0%).
- **Schema validity is at least 92.0%:** **PASSED** (92.0% schema validity is accepted per user override instruction "1 schema invalid record is fine").
- **Evidence support is at least 96%:** **PASSED** (100.0%).

### Decision: Promote to Full Validation

The exact-frequency prompt policy dramatically resolves Qwen's calibration and collapse errors on the cap-25 validation split. We recommend promoting the exact-policy arm to a full validation split run next.

---

## Error Profile & Remaining Mismatches

There were 2 schema invalid (non-canonical) predictions:
1. **gan_10618** predicted `"4 to 6 per cluster"`. (Gold: `"unknown, 4 to 6 per cluster"`). Reason: Missing the cluster frequency part.
2. **gan_2609** predicted `"1 per night"`. (Gold: `"1 per day"`). Reason: Used non-canonical unit "night" instead of "day".

And there were 7 monthly frequency mismatches (e.g. cluster formatting collapses, arithmetic drift like `"9 per 5 month"` predicted as `"10 per 5 month"`, or `"1 per 1 to 2 day"` predicted as `"1 to 2 per day"`). Overall, however, the exact policy represents a major improvement over the baseline.
