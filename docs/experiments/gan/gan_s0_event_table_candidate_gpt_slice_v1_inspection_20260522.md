# Gan S0 Event-Table Candidate GPT Slice V1 Inspection

Date: 2026-05-22

## Taxonomy

Dataset: Gan 2026 synthetic validation  
Schema complexity: Gan S0 seizure frequency  
Comparison group: `gan_s0_gpt4_1_mini_event_table_candidates_v1`  
Research axis: 3  
stage_graph_id: `g2_candidates_adjudicate`  
varied_factor: `implementation_variant`  
decision_scope: arm

## Hypothesis

An LLM event-table candidate stage might expose seizure events, observation windows, cluster rows, and seizure-free intervals before final adjudication, improving hard cases where direct final-label extraction collapses to `unknown` or overuses short stability windows.

## Fixed Controls

| Dimension | Value |
| --- | --- |
| Model | GPT 4.1-mini |
| Dataset split | `gan_2026_fixed_v1:validation` |
| Slice | Same 25-record Qwen 35b pragmatic-error enriched slice used for G1-G3 |
| Program | `gan_frequency_s0_temporal_event_table_single_pass` |
| Prompt | `gan_frequency_s0_temporal_event_table_single_pass_v1_0` |
| Scorer | `gan_frequency_deterministic_v1` |
| Verifier / repair | None |
| LLM calls | 2 per record: event-table extraction, then final adjudication |

## Arms

| arm_id | run_id | monthly | pragmatic | schema | evidence | gate |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| G5 event-table candidate stage | `gan_s0_gpt4_1_mini_event_table_candidate_slice_20260522T222602Z` | 8.3% (2/24 valid) | 37.5% (9/24 valid) | 96.0% | 100.0% | fail |

Reference controls from the same slice:

| control | monthly | pragmatic | note |
| --- | ---: | ---: | --- |
| v1.1 deterministic candidates baseline | 24.0% | 56.0% | G1 |
| v1.4 policy | 36.0% | 56.0% | G1 / strongest no-example control |
| compact hierarchy | 28.0% | 48.0% | G3 / rejected as tested |

## Outcome

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| G5 event-table candidate stage | reject as tested | arm | The event-table stage underperformed all same-slice controls, with low monthly accuracy and lower pragmatic accuracy despite high evidence quote support. |

## Error Read

- The model usually extracted note-supported event-table rows, but many rows lacked usable `event_count`, `window_phrase`, or denominator structure.
- The final adjudicator often treated counted-event notes as `unknown` or `no seizure frequency reference`, especially when the table contained seizure-free/no-event language alongside counted events.
- Exact monthly matches were limited to `gan_13123` and `gan_13574`.
- Pragmatic matches were mostly coarse bucket preservation despite denominator errors: `gan_13190`, `gan_14250`, `gan_14485`, `gan_14562`, `gan_14628`, `gan_15127`, and `gan_16750`.
- One schema-invalid label was emitted: `gan_15442` predicted `multiple per cluster per week, 2 per cluster`, which violates Gan cluster syntax.

## Interpretation

Reject this implementation arm. Free-form event-table rows are not enough: the model can find relevant evidence spans, but the table does not reliably preserve the numeric slots needed for Gan canonical label selection. This result does not reject LLM candidate extraction as a mechanism; it rejects this event-table-to-adjudicator implementation on this enriched slice.

The next stronger implementation should either:

- make the candidate stage emit canonical answer options plus ambiguity flags, then let a deterministic selector apply the Gan policy hierarchy; or
- constrain event-table rows with required numeric slots and add deterministic candidate derivation before final adjudication.

## Mechanism Review

No mechanism review claimed.

- Arms cited: one event-table candidate implementation plus same-slice controls.
- Implementations/positions tested: LLM event table as pre-adjudication candidate hints.
- Conclusion: arm reject only.

## Open Cells

- This study did not test multiple-answer proposer plus deterministic selector (G6).
- This study did not test candidate-constrained verifier / judge (G7).
- This study did not test a stricter JSON schema requiring normalized count/window slots for each event row.
- This study did not test Qwen transfer; Qwen should not be run for this failed GPT-first arm.

## Artifacts

- Config: `configs/experiments/gan_s0_gpt4_1_mini_event_table_candidate_slice.json`
- Run: `runs/gan_s0_gpt4_1_mini_event_table_candidate_slice_20260522T222602Z/`
- Metrics: `runs/gan_s0_gpt4_1_mini_event_table_candidate_slice_20260522T222602Z/metrics.json`
- Predictions: `runs/gan_s0_gpt4_1_mini_event_table_candidate_slice_20260522T222602Z/predictions.json`
