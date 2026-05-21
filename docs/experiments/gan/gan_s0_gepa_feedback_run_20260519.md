# Gan S0 GEPA Feedback Run 2026-05-19

Run artifact: `runs/gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z`

## Scope

This note records the first capped Gan S0 GEPA run after widening the optimizer-facing feedback metric beyond the earlier harness signal. The benchmark-facing scorer remains `gan_frequency_deterministic_v1`; the richer feedback is used only during GEPA instruction search.

## Fixed Controls

- Dataset/split: `gan_2026_fixed_v1:validation`
- Record cap: `5`
- Trainset size for GEPA: `4`
- Model/provider: `GPT 4.1-mini` via OpenAI
- Program variant: `gan_frequency_s0_direct_single_pass`
- Optimizer metric: `synthesis_exact_with_evidence_feedback`
- Scorer: `gan_frequency_deterministic_v1`

## Metrics

Compared with the earlier harness smoke `runs/gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T052124Z`:

| Metric | Earlier harness | Rich-feedback run |
|---|---:|---:|
| schema_valid_prediction_rate | 80.0% | 100.0% |
| normalized_label_accuracy | 50.0% | 40.0% |
| monthly_frequency_accuracy | 50.0% | 60.0% |
| pragmatic_category_accuracy | 75.0% | 60.0% |
| evidence_quote_support_rate | 25.0% | 80.0% |

Runtime from `metrics.json`:

- Compile duration: `20.05s`
- Prediction duration: `8.26s`
- Prediction seconds/record: `1.65`
- Estimated model calls: `9`

## What Changed

The richer feedback appears to have helped the model stay inside the schema and return grounded evidence more reliably. This was the intended near-term benefit of adding explicit failure feedback for invalid format, unsupported quote behavior, temporal-window mistakes, seizure-free threshold issues, cluster-format loss, forbidden units, and abstention.

The run did not improve the tiny-cap label metrics. The selected GEPA instruction in `artifacts/compiled_state.json` became much longer and more prescriptive, so the current tradeoff is:

- better schema validity and evidence support
- worse exact-label and Pragmatic category accuracy on this small slice
- clear prompt-bloat risk

## Remaining Failures On The 5-Record Cap

- `gan_10434`: gold cluster label collapsed to `unknown`
- `gan_14485`: gold `2 per 3 month` became `seizure free for 1 year`
- `gan_6532`: gold `unknown, multiple per cluster` became plain `unknown`
- `gan_14485`: evidence quote was unsupported because the model returned quoted wrapper text rather than the exact source span

These failures still fit the known Gan boundary: cluster structure, temporal-window interpretation, seizure-free threshold application, and quote-boundary control remain the main open problems.

## Next Recommendation

The next useful probe is not a larger GPT 4.1-mini cap with the same settings. The next question is whether the compact direct-extraction policy transfers to `Qwen3.6:35b` well enough for GEPA to be worthwhile despite local latency and partial offload.

Recommended next run:

- keep Gan S0 as the task
- keep the direct single-pass variant
- keep the deterministic scorer unchanged
- use a tiny GEPA cap first
- record compile time, prediction time, seconds/record, and token/residency metadata where available
- inspect whether GEPA produces compact transferable guidance or just prompt expansion that local Qwen cannot use efficiently

This should be treated as a latency-and-transfer probe, not as the new default local-Qwen workflow until the runtime cost is measured.
