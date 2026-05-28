# Gan S0 Multiple-Answer Selector GPT Slice V1 Inspection

Date: 2026-05-22

## Taxonomy

Dataset: Gan 2026 synthetic validation  
Schema complexity: Gan S0 seizure frequency  
Comparison group: `gan_s0_gpt4_1_mini_multiple_answer_selector_v1`  
Research axis: 3  
stage_graph_id: `g2_candidates_adjudicate`  
varied_factor: `implementation_variant`  
decision_scope: arm

## Hypothesis

An LLM proposer that emits explicit canonical answer options, evidence, status, and ambiguity flags might give a deterministic Gan-policy selector better input than the rejected event-table candidate stage, especially on hard cases where evidence rows alone lost count/window fidelity.

## Fixed Controls

| Dimension | Value |
| --- | --- |
| Model | GPT 4.1-mini |
| Dataset split | `gan_2026_fixed_v1:validation` |
| Slice | Same 25-record Qwen 35b pragmatic-error enriched slice used for G1-G5 |
| Program | `gan_frequency_s0_multiple_answer_det_selector` |
| Prompt | `gan_frequency_s0_multiple_answer_det_selector_v1_0` |
| Scorer | `gan_frequency_deterministic_v1` |
| Verifier / repair | None |
| LLM calls | 1 per record: answer-option proposal; deterministic selector chooses final label |

## Arms

| arm_id | run_id | monthly | pragmatic | schema | evidence | gate |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| G6 multiple-answer + deterministic selector | `gan_s0_gpt4_1_mini_multiple_answer_det_selector_slice_20260522T223556Z` | 0.0% | 0.0% | 100.0% | 100.0% on 4 supported-evidence predictions | fail |

Reference controls from the same slice:

| control | monthly | pragmatic | note |
| --- | ---: | ---: | --- |
| v1.1 deterministic candidates baseline | 24.0% | 56.0% | G1 |
| v1.4 policy | 36.0% | 56.0% | G1 / strongest no-example control |
| compact hierarchy | 28.0% | 48.0% | G3 / rejected as tested |
| event-table candidate stage | 8.3% | 37.5% | G5 / rejected as tested |

## Outcome

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| G6 multiple-answer + deterministic selector | reject as tested | arm | The strict answer-option parser/selector collapsed most records to `unknown` after filtering out unsupported or absent option evidence. It underperformed all same-slice controls. |

## Error Read

- 21/25 records fell back to `unknown` because no valid note-supported answer options survived parsing and evidence filtering.
- The four records with retained options were also wrong: `gan_14628`, `gan_14821`, `gan_14965`, and `gan_14973` selected `unknown`; `gan_15302` selected `no seizure frequency reference` but still missed the gold monthly target.
- Schema validity was 100.0%, so the failure was not Pydantic/schema acceptance.
- Evidence support was 100.0% only among the small set of predictions that retained evidence; most predictions had no evidence because the selector fallback has none.
- Compared with G5, this arm reduced LLM calls from two to one but lost too much candidate recall before deterministic selection.

## Interpretation

Reject this implementation arm. Canonical answer options are a better target surface than free-form event rows in principle, but this v1.0 implementation was too brittle: the selector only had useful choices on a small minority of records, and the proposer still favored unknown over benchmark-facing count/window labels.

This does not reject LLM candidate extraction or deterministic selection as mechanisms. It rejects the strict one-pass `answer_options_json` proposer plus exact-evidence filter and simple selector hierarchy on this enriched slice.

The next stronger implementation should either:

- seed the proposer with deterministic temporal candidates so option recall cannot collapse to zero;
- preserve raw rejected options in artifacts and repair near-exact evidence quotes before dropping them; or
- move to G7 candidate-constrained judge/verifier using deterministic candidates as the candidate set.

## Mechanism Review

No mechanism review claimed.

- Arms cited: one multiple-answer selector implementation plus same-slice controls.
- Implementations/positions tested: LLM answer-option proposal followed by deterministic post-selection.
- Conclusion: arm reject only.

## Open Cells

- This study did not test hybrid deterministic+LLM answer options.
- This study did not test candidate-constrained verifier / judge (G7).
- This study did not test a selector over deterministic candidates plus LLM-proposed ambiguity flags.
- This study did not test Qwen transfer; Qwen should not be run for this failed GPT-first arm.

## Artifacts

- Config: `configs/experiments/gan_s0_gpt4_1_mini_multiple_answer_det_selector_slice.json`
- Run: `runs/gan_s0_gpt4_1_mini_multiple_answer_det_selector_slice_20260522T223556Z/`
- Metrics: `runs/gan_s0_gpt4_1_mini_multiple_answer_det_selector_slice_20260522T223556Z/metrics.json`
- Predictions: `runs/gan_s0_gpt4_1_mini_multiple_answer_det_selector_slice_20260522T223556Z/predictions.json`
