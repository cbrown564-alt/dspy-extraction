# Gan S0 Seeded Answer Options GPT Slice V1 Inspection

Date: 2026-05-23  
Status: Reject as tested for promotion; seeded hybrid answer-options mechanism remains open  

## Taxonomy

Dataset: Gan 2026 synthetic validation  
Schema complexity: Gan S0 seizure frequency  
Comparison group: `gan_s0_gpt4_1_mini_seeded_answer_options_v1`  
Research axis: 3  
stage_graph_id: `g2_candidates_adjudicate`  
varied_factor: `implementation_variant`  
decision_scope: arm

## Hypothesis

Seeded hybrid answer options might avoid the G6 candidate-recall collapse by retaining deterministic temporal candidates as selectable options while allowing the LLM to add competing canonical labels and ambiguity flags.

## Fixed Controls

| Dimension | Value |
| --- | --- |
| Model | GPT 4.1-mini |
| Dataset split | `gan_2026_fixed_v1:validation` |
| Slice | Same 25-record enriched validation slice used for G1-G7 and targeted examples min7 |
| Program | `gan_frequency_s0_seeded_multiple_answer_det_selector` |
| Prompt | `gan_frequency_s0_seeded_multiple_answer_det_selector_v1_0` |
| Scorer | `gan_frequency_deterministic_v1` |
| Candidate source | Deterministic temporal candidates plus LLM answer options |
| Verifier / repair | None |
| LLM calls | 1 per record: seeded answer-option proposal; deterministic selector chooses final label |

## Arms

| arm_id | run_id | monthly | purist | pragmatic | normalized | schema | evidence | gate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| G6b seeded hybrid answer options | `gan_s0_gpt4_1_mini_seeded_answer_options_slice_20260523T074823Z` | 16.0% | 16.0% | 20.0% | 16.0% | 100.0% | 100.0% on 8 supported-evidence predictions | fail |

Reference controls from the same slice:

| control | monthly | pragmatic | note |
| --- | ---: | ---: | --- |
| v1.4 no-example control | 36.0% | 56.0% | strongest no-example policy control |
| G6 multiple-answer selector | 0.0% | 0.0% | strict unseeded options collapsed to fallback `unknown` |
| G7 candidate-constrained verifier | 36.0% | 56.0% | tied v1.4 but added a second LLM pass |
| targeted examples min7 | 36.0% | 56.0% | tied v1.4 with mixed rescues/regressions |

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| G6b seeded hybrid answer options | reject as tested for promotion | arm | Seeding prevented complete candidate collapse on records with deterministic candidates, but the selector over-trusted poor LLM options and still fell back to `unknown` on 14/25 records. |

## Error Read

- Selected option sources: deterministic temporal candidate 4/25, LLM answer option 7/25, no selected option 14/25.
- Raw rejected LLM options were preserved: 66 rejected options across 25 records, mostly unsupported or missing evidence.
- Exact monthly matches were limited to deterministic-seed wins: `gan_14250`, `gan_14485`, `gan_14881`, and `gan_15302`.
- One additional pragmatic-only match: `gan_13123`, where the LLM option selected `1 per 6 months` instead of gold `1 per year`.
- Bad LLM options caused severe regressions on several records, including `no seizure frequency reference` for quantified gold labels (`gan_13058`, `gan_14214`, `gan_16750`) and zero-rate labels (`0 per month`, `0 per week`) for infrequent gold labels (`gan_14965`, `gan_14973`).
- The remaining dominant failure is still candidate coverage/policy selection: 14/25 records had no valid option after filtering and therefore fell back to `unknown`.

## Interpretation

Reject this implementation arm for promotion. The seeded design is better than G6 on monthly accuracy, but it remains below v1.4, G7, and targeted examples on the same slice while adding a new candidate-option pass. The run is useful mainly because it separates two failures: deterministic seeds can rescue records when the candidate builders already find the right label, but the LLM option layer needs stricter selection guards before it should influence the final answer.

This does not reject hybrid answer options as a mechanism. It rejects this v1.0 selector policy: deterministic seeds plus all valid LLM options ranked by the current simple hierarchy.

## Mechanism Review

No mechanism review claimed.

- Arms cited: one seeded hybrid answer-options implementation plus same-slice controls.
- Implementations/positions tested: deterministic candidate seeds merged with LLM answer options before deterministic post-selection.
- Conclusion: arm reject only.

## Open Cells

- Selector guard: prefer deterministic temporal seeds over LLM options unless the LLM option is an in-note quantified label that beats an `unknown`/no-option state.
- Raw rejected options can drive a focused repair experiment for near-exact evidence, but this should not change scorer semantics.
- Deterministic candidate builder gaps remain the higher-value route for the 14/25 no-option fallbacks.
- No Qwen transfer is justified from this failed GPT-first arm.

## Artifacts

- Config: `configs/experiments/gan_s0_gpt4_1_mini_seeded_answer_options_slice.json`
- Run: `runs/gan_s0_gpt4_1_mini_seeded_answer_options_slice_20260523T074823Z/`
- Metrics: `runs/gan_s0_gpt4_1_mini_seeded_answer_options_slice_20260523T074823Z/metrics.json`
- Predictions: `runs/gan_s0_gpt4_1_mini_seeded_answer_options_slice_20260523T074823Z/predictions.json`
