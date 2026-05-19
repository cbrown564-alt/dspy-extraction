# Gan S0 Qwen3.6:35b GEPA Probe Run 2026-05-19

Run artifact: `runs/gan_s0_gepa_direct_cap5_qwen35b_ollama_20260519T055049Z`

## Scope

This note records the tiny local-Qwen GEPA transfer probe requested by the
current Kanban plan. The goal was not to establish a new default workflow. The
goal was to measure whether `Qwen3.6:35b` could use the existing Gan S0
optimizer setup effectively enough to justify more local GEPA follow-up under
the validated direct-extraction policy.

## Fixed Controls

- Dataset/split: `gan_2026_fixed_v1:validation`
- Record cap: `5`
- Trainset size for GEPA: `4`
- Model/provider: `Qwen3.6:35b` via Ollama
- Program variant: `gan_frequency_s0_direct_single_pass`
- Optimizer metric: `synthesis_exact_with_evidence_feedback`
- Scorer: `gan_frequency_deterministic_v1`
- Structured output: `provider_json_schema_with_pydantic_validation`

## Metrics

From `metrics.json`:

| Metric | Value |
|---|---:|
| schema_valid_prediction_rate | 100.0% |
| evidence_quote_support_rate | 100.0% |
| normalized_label_accuracy | 20.0% |
| monthly_frequency_accuracy | 20.0% |
| purist_category_accuracy | 20.0% |
| pragmatic_category_accuracy | 40.0% |

Runtime:

- Compile duration: `267.81s`
- Prediction duration: `70.34s`
- Prediction seconds/record: `14.07`
- Estimated model calls: `9`
- Total duration: `338.21s`

Prompt-shape comparison from `artifacts/compiled_state.json`:

- Selected Qwen GEPA instruction: `3936` characters / `664` words
- Prior GPT 4.1-mini GEPA instruction from
  `runs/gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z`:
  `3249` characters / `508` words

Residency snapshot after the run:

- `ollama ps`: `72%/28% CPU/GPU`, `CONTEXT 4096`

## What Happened

The run succeeded operationally. GEPA compiled, produced optimizer artifacts,
and the prediction path stayed completely schema-valid with exact contiguous
evidence quotes on all five capped records. That is the positive result.

The transfer result itself was weak. Four of five records still missed the gold
label after normalization:

- `gan_10434`: gold cluster label collapsed to plain rate
- `gan_13123`: gold `1 per year` became `1 per week`
- `gan_14485`: gold `2 per 3 month` became `no seizure frequency reference`
- `gan_6532`: gold `unknown, multiple per cluster` became
  `no seizure frequency reference`

The selected GEPA instruction also became materially longer than the earlier
GPT 4.1-mini GEPA instruction and drifted into over-specific temporal logic.
During GEPA reflection, DSPy logged a truncation warning at `max_tokens=1024`
for the higher-temperature reflection LM, which is another sign that this local
optimizer path is spending a lot of budget on prompt/reflection overhead rather
than producing compact transferable guidance.

## Interpretation

This probe does not support promoting GEPA to the normal `Qwen3.6:35b` Gan S0
workflow.

What the probe did show:

- local Qwen can execute the GEPA harness end to end
- the resulting prompt can strongly constrain schema format and evidence quoting
- the current optimizer setup does not transfer cleanly to label quality on this
  tiny slice
- compile cost is high relative to the quality signal obtained
- prompt bloat is getting worse rather than better

Compared with the earlier warm direct-only three-record Qwen cap in
`runs/gan_s0_latency_qwen35b_direct_cap3_20260518T201925Z`, prediction speed
was slower here (`14.07s`/record versus `8.83s`/record), and that excludes the
additional `267.81s` compile phase.

## Recommendation

Keep `Qwen3.6:35b` on the validated direct-extraction path for Gan S0.

Near-term follow-up should prioritize:

- direct-path canonical label control
- evidence-length guardrails
- token and residency capture for local runs

Do not schedule larger local-Qwen GEPA follow-up until there is either:

- a demonstrably more compact optimizer output, or
- a cheaper transfer strategy that optimizes on a faster model and ports only a
  manually reviewed compact policy to Qwen
