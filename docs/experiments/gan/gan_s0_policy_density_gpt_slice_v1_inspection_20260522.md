# Gan S0 Policy-Density GPT Slice v1 Inspection

Date: 2026-05-22  
Status: Done  

## Taxonomy

Dataset: Gan 2026 synthetic validation  
Schema complexity: Gan S0 seizure frequency  
Comparison group: `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1`  
Research axis: 3  
stage_graph_id: `g2_candidates_adjudicate`  
varied_factor: `prompt_policy`  
decision_scope: arm  

## Fixed Controls

- Model/provider: GPT 4.1-mini via `configs/models/gan_s0_gpt4_1_mini.json`
- Split: `gan_2026_fixed_v1:validation`
- Record set: 25-record enriched slice from Qwen 35b pragmatic-category misses
- Program: `gan_frequency_s0_temporal_candidates_single_pass`
- Candidate source: deterministic temporal candidates, full note plus candidate hints
- Scorer: `gan_frequency_deterministic_v1`
- Evidence policy: exact quote support diagnostic only

## Arms

| arm_id | prompt_version | run_id | Monthly | Purist | Pragmatic | Normalized | Schema | Evidence |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v1.1 baseline | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` | `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_1_slice_20260522T215239Z` | 24.0% | 40.0% | 56.0% | 16.0% | 100.0% | 100.0% |
| compact hierarchy | `gan_frequency_s0_temporal_candidates_single_pass_v1_5_compact_hierarchy` | `gan_s0_gpt4_1_mini_policy_density_compact_hierarchy_slice_20260522T221745Z` | 28.0% | 36.0% | 48.0% | 20.0% | 100.0% | 100.0% |
| v1.4 full policy | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` | `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z` | 36.0% | 44.0% | 56.0% | 28.0% | 100.0% | 100.0% |

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| v1.1 baseline | hold baseline | arm | Better pragmatic than compact, but lower monthly/normalized than v1.4. |
| compact hierarchy | reject as tested | arm | Rescued `gan_14214`, but lost v1.4 wins on `gan_13190` and `gan_14881`; added pragmatic regressions on `gan_14689`, `gan_15442`, `gan_16529`, and `gan_16750`. |
| v1.4 full policy | hold for next GPT search cells | arm | Best monthly, Purist, and normalized accuracy on this slice while tying v1.1 pragmatic accuracy. |

## Interpretation

The compact hierarchy did not preserve the useful v1.4 monthly/normalized lift. Its failures suggest that concise policy prose is not enough to stabilize the difficult grouped-event and cluster cases; the model still needs either fuller policy text, targeted examples, or a more structured candidate/proposal stage.

The result does not close policy compression as a mechanism. It rejects only this compact v1.5 implementation on this enriched slice.

## Open Cells

- Targeted examples for grouped recent events, short stability after counted events, cluster ambiguity, and highest-current-frequency selection.
- LLM event-table candidate stage where the model emits events/windows/ambiguities before final adjudication.
- Multiple-answer proposer plus deterministic selector over candidate labels.
- Candidate-constrained judge/verifier that cannot free-form over-repair.
