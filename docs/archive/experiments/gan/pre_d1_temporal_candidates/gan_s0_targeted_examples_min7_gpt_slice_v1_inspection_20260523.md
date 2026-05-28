# Gan S0 Targeted Examples Min7 GPT Slice Inspection

Date: 2026-05-23  
Status: Reject as tested for promotion; examples mechanism remains open  
Comparison group: `gan_s0_gpt4_1_mini_targeted_examples_v1`  

## Taxonomy

Dataset: Gan 2026 synthetic validation  
Schema complexity: Gan S0 seizure frequency  
Comparison group: `gan_s0_gpt4_1_mini_targeted_examples_v1`  
Research axis: 3  
stage_graph_id: `g2_candidates_adjudicate`  
varied_factor: `example_strategy`  
decision_scope: arm  

## Fixed Controls

- Model/provider: GPT 4.1-mini via OpenAI
- Config: `configs/experiments/gan_s0_gpt4_1_mini_targeted_examples_min7_slice.json`
- Run: `runs/gan_s0_gpt4_1_mini_targeted_examples_min7_slice_20260523T072443Z/`
- Split: `gan_2026_fixed_v1:validation`, fixed 25-record enriched slice
- Program: `gan_frequency_s0_temporal_candidates_single_pass`
- Prompt: `gan_frequency_s0_temporal_candidates_single_pass_v1_6_targeted_examples_min7`
- Scorer: `gan_frequency_deterministic_v1`
- Candidate source: deterministic temporal candidates
- Verifier/repair: none; artifact-bridge surface normalization only

## Arms

| arm_id | run_id | monthly | purist | pragmatic | normalized | schema | evidence | gate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v1.4 no-example control | `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z` | 36.0% | 44.0% | 56.0% | 28.0% | 100.0% | 100.0% | control |
| targeted_examples_min7_v1 | `gan_s0_gpt4_1_mini_targeted_examples_min7_slice_20260523T072443Z` | 36.0% | 44.0% | 56.0% | 28.0% | 100.0% | 100.0% | fail: no lift |

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| targeted_examples_min7_v1 | reject as tested for promotion | arm | Tied v1.4 on all aggregate benchmark-facing and diagnostic headline metrics while adding substantial prompt tokens. |

## Error Read

The example pack changed several labels but did not improve aggregate accuracy.

Useful movements:

- `gan_16750`: `unknown` -> `6 per 7 month`, exact/monthly/pragmatic rescue.
- `gan_15442`: `unknown` -> `multiple per day`, pragmatic rescue but still not exact cluster syntax.
- `gan_16645`: `3 cluster per month, 3 per cluster` -> `3 cluster per 6 month, 1 per cluster`, Purist/pragmatic rescue but still monthly mismatch.

Regressions:

- `gan_14881`: `1 per month` -> `unknown`, losing exact/monthly/pragmatic match.
- `gan_15193`: `1 per year` -> `unknown`, losing pragmatic match.
- `gan_16529`: `1 cluster per 5 day, multiple per cluster` -> `unknown`, losing Purist/pragmatic match.

Most remaining errors are still candidate-coverage and denominator/window selection failures. The examples sometimes encouraged a better grouped-event interpretation, but also increased abstention or cluster uncertainty on records where v1.4 already had a usable approximation.

## Mechanism Review

Not applicable. This is a single fixed example-pack implementation on an enriched slice.

- Arms cited: one example-pack arm plus v1.4 no-example control.
- Implementations/positions tested: prompt-embedded examples in the adjudicator only.
- Conclusion: reject this example pack as tested for promotion; do not mechanism-reject targeted examples.

## Open Cells

- Smaller targeted packs may isolate the helpful grouped-event/YTD examples from cluster/abstention regressions.
- Retrieval-selected examples remain untested.
- Seeded hybrid answer options with deterministic candidates remain open.
- No Qwen transfer is justified from this tied GPT slice result.

## Caveats

The 25-record slice is enriched for Qwen 35b pragmatic misses and does not estimate full-validation performance. Evidence support is diagnostic; benchmark-facing conclusions use Gan monthly, Purist, and Pragmatic metrics against `seizure_frequency_number[0]`.
