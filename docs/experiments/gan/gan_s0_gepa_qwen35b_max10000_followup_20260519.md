# Gan S0 Qwen3.6:35b GEPA Follow-Up at `max_tokens=10000` (2026-05-19)

Run artifact: `runs/gan_s0_gepa_direct_cap5_qwen35b_ollama_20260519T060700Z`

## Research Question

Did the earlier negative local-Qwen GEPA probe understate the usefulness of
`Qwen3.6:35b` because the reflection/output budget was capped too low at
`max_tokens=1024`?

## Motivation

The earlier probe note in `docs/experiments/gan/gan_s0_gepa_qwen35b_probe_run_20260519.md`
recommended against near-term local-Qwen GEPA follow-up, but that run also
logged a DSPy truncation warning during GEPA reflection at `max_tokens=1024`.
This rerun isolates that concern by raising only the active Qwen GEPA model
budget to `10000` while keeping the capped Gan S0 GEPA setup otherwise fixed.

## Method

- Dataset/split: `gan_2026_fixed_v1:validation`
- Record cap: `5`
- Trainset size for GEPA: `4`
- Model/provider: `Qwen3.6:35b` via Ollama
- Model config: `configs/models/gan_s0_qwen35b_ollama_gepa_max10000.json`
- Experiment config: `configs/experiments/gan_s0_gepa_direct_cap5_qwen35b_ollama.json`
- Program variant: `gan_frequency_s0_direct_single_pass`
- Optimizer: `GEPA`
- Optimizer metric: `synthesis_exact_with_evidence_feedback`
- Scorer: `gan_frequency_deterministic_v1`
- Structured output: `provider_json_schema_with_pydantic_validation`

## Results

Compared with the earlier `max_tokens=1024` Qwen GEPA probe
(`runs/gan_s0_gepa_direct_cap5_qwen35b_ollama_20260519T055049Z`):

| Metric | `1024` run | `10000` run |
|---|---:|---:|
| schema_valid_prediction_rate | 100.0% | 80.0% |
| evidence_quote_support_rate | 100.0% | 100.0% |
| normalized_label_accuracy | 20.0% | 25.0% |
| monthly_frequency_accuracy | 20.0% | 50.0% |
| purist_category_accuracy | 20.0% | 50.0% |
| pragmatic_category_accuracy | 40.0% | 50.0% |

Runtime and prompt shape:

- Compile duration: `267.81s` -> `535.80s`
- Prediction duration: `70.34s` -> `59.90s`
- Prediction seconds/record: `14.07` -> `11.98`
- Total duration: `338.21s` -> `595.97s`
- Token usage in the `10000` run: `40764` prompt, `3445` completion, `44209` total
- Selected GEPA instruction length: `3936` chars / `664` words -> `10562` chars / `1819` words
- Residency snapshot after the `10000` run: `ollama ps` captured `72%/28% CPU/GPU (context=4096)`

Key record-level outcomes from the `10000` run:

- `gan_4956`: remained correct as `seizure free for 7 month`
- `gan_13123`: improved structurally from the earlier `1 per week` error to
  `1 per 1 year`, which still missed exact normalization
- `gan_10434`: regressed into an invalid non-canonical label, `several per week`
- `gan_14485`: still collapsed to `no seizure frequency reference`
- `gan_6532`: still collapsed to `no seizure frequency reference`

## Interpretation

Raising the token budget to `10000` did matter. The rerun improved all
benchmark-facing accuracy metrics on this tiny capped slice and removed the
earlier severe `1 per week` temporal distortion on `gan_13123`. That means the
earlier `1024` result was too pessimistic if interpreted as a pure test of
whether Qwen can use deeper GEPA reflection at all.

At the same time, the higher budget did not make the local-Qwen GEPA path clean
or compact. The selected GEPA instruction expanded to more than `10k`
characters and introduced self-conflicted reflective policy text. That prompt
growth coincided with a new schema-validity failure at the normalization layer:
`gan_10434` emitted `several per week`, which is outside the Gan label
vocabulary. So the extra budget helped transfer somewhat, but it also gave GEPA
room to over-elaborate and drift away from the benchmark contract.

## Limitations

- This is still a tiny capped validation probe on `5` records, not a benchmark
  reproduction.
- GEPA used `4` training examples and no separate validation set, so DSPy
  explicitly overfit to the tiny train slice by design.
- The scorer remains `gan_frequency_deterministic_v1`; benchmark-facing metrics
  and diagnostic metrics should not be conflated.
- Gan label-policy quirks still matter here, especially around cluster labels,
  `unknown`, and `no seizure frequency reference`.

## Next Experiments

- Keep this `10000`-token rerun as evidence that budget mattered, but do not
  treat it as sufficient support for scaling the current prompt-growth pattern.
- Test whether the gain survives if the GEPA output is manually compacted back
  to benchmark-contract rules before Qwen prediction.
- Add a deterministic canonical-label guardrail for Gan S0 so non-vocabulary
  strings like `several per week` cannot pass through as the final answer.
- If local-Qwen GEPA follow-up continues, track prompt length and token usage as
  first-class metrics alongside label quality.
