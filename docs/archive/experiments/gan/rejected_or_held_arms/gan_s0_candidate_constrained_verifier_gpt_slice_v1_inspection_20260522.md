# Gan S0 Candidate-Constrained Verifier GPT Slice V1 Inspection

Date: 2026-05-22

## Taxonomy

Dataset: Gan 2026 synthetic validation  
Schema complexity: Gan S0 seizure frequency  
Comparison group: `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1`  
Research axis: 3  
stage_graph_id: `g2_candidates_adjudicate`  
varied_factor: `verification_strategy`  
decision_scope: arm

## Hypothesis

A candidate-constrained verifier can reduce historical verify-repair over-repair by allowing the second pass to confirm the adjudicator output or select only from deterministic temporal candidates plus explicit `unknown` / `no seizure frequency reference`, without free-form repair.

## Fixed Controls

| Dimension | Value |
| --- | --- |
| Model | GPT 4.1-mini |
| Dataset split | `gan_2026_fixed_v1:validation` |
| Slice | Same 25-record Qwen 35b pragmatic-error enriched slice used for G1-G6 |
| Program | `gan_frequency_s0_temporal_candidates_adjudicate_constrained_verifier` |
| Prompt | `gan_frequency_s0_temporal_candidates_adjudicate_constrained_verifier_v1_1` |
| Candidate source | Deterministic temporal candidates |
| Scorer | `gan_frequency_deterministic_v1` |
| LLM calls | 2 per record: candidate-aware adjudication, then constrained verification |

## Arms

| arm_id | run_id | monthly | pragmatic | schema | evidence | gate |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| G7 candidate-constrained verifier | `gan_s0_gpt4_1_mini_constrained_verifier_slice_20260522T225947Z` | 36.0% | 56.0% | 100.0% | 100.0% | neutral / no promote |

Reference controls from the same slice:

| control | monthly | pragmatic | note |
| --- | ---: | ---: | --- |
| v1.1 deterministic candidates baseline | 24.0% | 56.0% | G1 |
| v1.4 policy | 36.0% | 56.0% | G1 / strongest no-example control |
| compact hierarchy | 28.0% | 48.0% | G3 / rejected as tested |
| event-table candidate stage | 8.3% | 37.5% | G5 / rejected as tested |
| multiple-answer + deterministic selector | 0.0% | 0.0% | G6 / rejected as tested |

## Outcome

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| G7 candidate-constrained verifier | reject as tested for promotion | arm | The verifier preserved the v1.4 single-pass outputs almost exactly and did not improve monthly or pragmatic accuracy. It avoided free-form over-repair, but the added second LLM call did not buy measurable benefit on this slice. |

## Error Read

- 25/25 predictions were schema-valid and all evidence quotes had deterministic note support.
- Verifier decisions were 22 `confirm` and 3 guard-level `repair` decisions. The repairs were surface-boundary corrections to keep outputs within the allowed initial/candidate/sentinel set, not substantive benchmark fixes.
- Final labels matched the v1.4 no-verifier control on 24/25 records; the only visible difference stripped outer quotes from `gan_14881` (`"1 per month"` to `1 per month`) with no metric change.
- Monthly misses remained concentrated in denominator/window errors and over-unknown cases: `gan_14792`, `gan_14821`, `gan_14965`, `gan_14973`, `gan_15168`, `gan_15442`, and `gan_16750` still predicted `unknown` against quantified gold labels.
- Candidate coverage was the limiting factor on several repair opportunities: when deterministic temporal candidates were empty, the constrained verifier mostly confirmed the initial label or `unknown` rather than inventing a free-form repair.

## Interpretation

Reject this G7 implementation as a promotion candidate. It is safer than historical unconstrained verify-repair because it did not introduce unsupported free-form labels, but it also did not move the hard slice beyond the v1.4 single-pass policy control. For this exact implementation, the second pass mostly acts as a costlier confirmation layer.

This does not reject candidate-constrained verification as a mechanism. A stronger version would need better candidate coverage or a seeded hybrid option set before the verifier, while preserving the no-free-form-repair constraint.

## Mechanism Review

No mechanism review claimed.

- Arms cited: one candidate-constrained verifier implementation plus same-slice controls.
- Implementations/positions tested: deterministic candidates before adjudication, LLM verifier after adjudication, deterministic guard after verifier.
- Conclusion: arm reject only.

## Open Cells

- Hybrid deterministic+LLM answer options seeded by deterministic candidates, with raw rejected options preserved before filtering.
- Targeted examples for grouped recent events, short stability after counted events, highest-current-frequency selection, and cluster ambiguity.
- Candidate-constrained verification with higher candidate recall, if a future candidate-generation arm provides materially better options.
- Qwen transfer is not warranted for this failed GPT-first promotion cell.

## Artifacts

- Config: `configs/experiments/gan_s0_gpt4_1_mini_constrained_verifier_slice.json`
- Run: `runs/gan_s0_gpt4_1_mini_constrained_verifier_slice_20260522T225947Z/`
- Metrics: `runs/gan_s0_gpt4_1_mini_constrained_verifier_slice_20260522T225947Z/metrics.json`
- Predictions: `runs/gan_s0_gpt4_1_mini_constrained_verifier_slice_20260522T225947Z/predictions.json`
