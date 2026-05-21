# Qwen Local DSPy Latency Experiment

Date: 2026-05-18

## Research Question

Can the Windows laptop run local Qwen models inside the current DSPy Gan S0
setup, and how much latency or fragility is added by `ChainOfThought` and
`BootstrapFewShot`?

## Method

- Dataset/split: Gan 2026 synthetic validation split, `gan_2026_fixed_v1:validation`.
- Schema level: `gan_frequency_s0`.
- Scorer mode: `gan_frequency_deterministic_v1`.
- Task: Gan S0 `seizure_frequency_number` plus source evidence.
- Local runtime: Ollama on Windows.
- Qwen3.5:9b config: `configs/models/gan_s0_qwen9b_ollama.json`, `max_tokens=1536`, `num_retries=0`.
- Qwen3.6:35b config: `configs/models/gan_s0_qwen35b_ollama.json`, `max_tokens=256`, `num_retries=0`.
- DSPy/Ollama adapter decision: use LiteLLM `ollama_chat/` with `extra_body={"think": false}`. Ollama's OpenAI-compatible `/v1` route returned hidden reasoning with empty final content for Qwen, which caused DSPy parse failures and incomplete runs.

All reported metrics below are capped exploratory diagnostics, not published
Gan benchmark reproduction and not stable quality estimates.

## Results

| Run | Model | Variant | Optimizer | Records | Status | Prediction seconds / record | Schema validity | Evidence support | Notes |
| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| `runs/gan_s0_latency_qwen9b_direct_cap3_20260518T201228Z` | Qwen3.5:9b | direct | none | 3 | completed | 3.91 | 100.0% | 66.7% | Fastest successful local Qwen path. |
| `runs/gan_s0_latency_qwen9b_cot_cap3_20260518T201247Z` | Qwen3.5:9b | `ChainOfThought` | none | 3 | completed with truncation warnings | 53.74 | 66.7% | 50.0% | Visible reasoning made prediction about 13.7x slower than direct and still exceeded `max_tokens=1536` on some calls. |
| `runs/gan_s0_latency_qwen9b_direct_bootstrap_cap3_20260518T201540Z` | Qwen3.5:9b | direct | tiny `BootstrapFewShot` | 3 | completed | 4.62 | 100.0% | 33.3% | Compile took 3.92s; prediction was about 1.18x slower than direct zero-shot. |
| `runs/gan_s0_latency_qwen9b_cot_bootstrap_cap3_20260518T201609Z` | Qwen3.5:9b | `ChainOfThought` | tiny `BootstrapFewShot` | 3 | failed during prediction | n/a | n/a | n/a | Compilation succeeded, but prediction exhausted `max_tokens=1536` in the reasoning field before label/evidence, producing no metrics artifact. |
| `runs/gan_s0_smoke_qwen35b_direct_ollama_20260518T201840Z` | Qwen3.6:35b | direct | none | 1 | completed | 35.83 | 100.0% | 100.0% | Cold/warm state caveat; validates direct one-record runtime path. |
| `runs/gan_s0_latency_qwen35b_direct_cap3_20260518T201925Z` | Qwen3.6:35b | direct | none | 3 | completed | 8.83 | 100.0% | 100.0% | Warm 3-record run. `ollama ps` showed Qwen3.6:35b at 74% CPU / 26% GPU residency after the run. |

## Interpretation

Qwen3.5:9b can function in this DSPy setup for direct extraction and for a
tiny direct `BootstrapFewShot` compile/run. `ChainOfThought` is technically
runnable on the tiny cap, but it is much slower and less reliable: it generated
long visible reasoning, hit output truncation warnings, and reduced schema
validity on this slice.

Qwen3.5:9b did not successfully complete `ChainOfThought + BootstrapFewShot`
under the tested constraints. The failure is not compilation; the tiny
bootstrap compile found a passing trace. The failure is prediction-time output
budget: demonstrations plus visible reasoning caused the model to spend the
completion on `reasoning` and omit the required label/evidence fields.

Qwen3.6:35b can function with direct extraction and no optimizer on a tiny cap.
The run is not a quality signal, but it answers the hardware gate positively
for direct-only smoke/capped experiments. Because Ollama reported 74% CPU / 26%
GPU residency, larger runs should still be treated as paced jobs rather than
interactive loops.

## Caveats

- The cap is only three validation records, so quality metrics are not stable.
- The Qwen3.6:35b one-record and three-record timings differ because the model
  was warm for the later cap.
- Runtime metadata records wall-clock timing but not token counts or exact GPU
  residency at run time; residency was checked separately with `ollama ps`.
- Failed Qwen attempts before switching to `ollama_chat/` created incomplete
  run directories without metrics and should not be interpreted as model
  quality failures.

## Next Steps

- Keep direct Gan S0 as the default local-Qwen path.
- Do not use `ChainOfThought + BootstrapFewShot` for Qwen3.6:35b.
- If Qwen3.5:9b reasoning remains interesting, test a bounded custom reasoning
  field or stricter prompt that forces label/evidence before explanation.
- Add token-count capture if LiteLLM/Ollama exposes reliable usage metadata in
  DSPy artifacts.

## Max-Budget Follow-Up

After the first run, the latency policy interpretation was corrected. The
primary issue was not only Qwen3.6:35b CPU/RAM offload. Qwen was also still
able to spend output on thinking/reasoning-like text, and the earlier
`max_tokens` values were too low for `ChainOfThought` plus demonstration-heavy
prediction prompts.

Qwen's current model cards recommend `max_tokens=32768` for most queries and
`max_tokens=81920` for complex benchmark tasks. Local `ollama show` reports a
`262144` context length for both `qwen3.5:9b` and `qwen3.6:35b`. The max-budget
configs therefore set:

- `max_tokens=81920`
- `extra_body={"options": {"num_ctx": 262144}}`
- the existing DSPy Ollama adapter default `extra_body={"think": false}`

The first max-budget 9B run accidentally reused Ollama's default active
`CONTEXT 4096`; those artifacts are superseded by the later runs below, where
`ollama ps` confirmed `CONTEXT 262144`.

| Run | Model | Variant | Optimizer | Records | Prediction seconds / record | Schema validity | Evidence support | Notes |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `runs/gan_s0_maxbudget_qwen9b_direct_cap3_20260518T205611Z` | Qwen3.5:9b | direct | none | 3 | 15.60 | 100.0% | 0.0% | Full-context direct baseline; slower than the earlier default-context direct run. |
| `runs/gan_s0_maxbudget_qwen9b_cot_cap3_20260518T205711Z` | Qwen3.5:9b | `ChainOfThought` | none | 3 | 186.16 | 100.0% | 33.3% | Completed, but visible reasoning remained about 11.9x slower than direct. |
| `runs/gan_s0_maxbudget_qwen9b_direct_bootstrap_cap3_20260518T210732Z` | Qwen3.5:9b | direct | tiny `BootstrapFewShot` | 3 | 27.06 | 100.0% | 66.7% | Compile took 59.18s and found 0 full traces under the strict optimizer metric. |
| `runs/gan_s0_maxbudget_qwen9b_cot_bootstrap_cap3_20260518T210921Z` | Qwen3.5:9b | `ChainOfThought` | tiny `BootstrapFewShot` | 3 | 388.58 | 66.7% | 50.0% | Completed where the earlier low-budget run failed, but remained very slow and schema-fragile. |
| `runs/gan_s0_maxbudget_qwen35b_direct_cap1_20260518T212905Z` | Qwen3.6:35b | direct | none | 1 | 35.30 | 100.0% | 100.0% | Ollama confirmed `CONTEXT 262144`; residency was 79% CPU / 21% GPU. |
| `runs/gan_s0_maxbudget_qwen35b_cot_cap1_20260518T212944Z` | Qwen3.6:35b | `ChainOfThought` | none | 1 | 96.29 | 100.0% | 0.0% | One-record CoT smoke completed, about 2.7x slower than direct on the same first validation record. |

Interpretation: raising the output and context budget changes the failure mode.
`ChainOfThought + BootstrapFewShot` on Qwen3.5:9b is no longer simply blocked by
truncation, but it is still not a good default because it is very slow and still
schema-fragile. Qwen3.6:35b can run a one-record full-context CoT smoke, but the
observed pace does not justify promoting visible reasoning or bootstrap-expanded
prompts to the routine local 35B path.

## 2026-05-19 Follow-Up - Qwen3.6:35b Direct `max_tokens=1024`

### Context

The overnight full-validation Gan S0 run for `Qwen3.6:35b` direct extraction used
`configs/models/gan_s0_qwen35b_ollama.json` with `max_tokens=256` and logged a
single DSPy truncation warning. The follow-up question was whether that cap was
artificially depressing full-validation quality and should be raised for the
default 35B direct path.

### Work Completed

- Updated `configs/models/gan_s0_qwen35b_ollama.json` from `max_tokens=256` to
  `max_tokens=1024`.
- Re-ran full Gan S0 validation with
  `configs/experiments/gan_s0_overnight_qwen35b_direct_full_validation.json`.
- New run artifact:
  `runs/gan_s0_overnight_qwen35b_direct_full_validation_20260519T035636Z`
- Baseline comparison artifact:
  `runs/gan_s0_overnight_qwen35b_direct_full_validation_20260518T223713Z`
- Dataset/split: `gan_2026_fixed_v1:validation`
- Schema level: `gan_frequency_s0`
- Program variant: `gan_frequency_s0_direct_single_pass`
- Scorer: `gan_frequency_deterministic_v1`

### Observations

- The benchmark-facing metrics were identical between the two runs:
  - monthly-frequency accuracy: `55.6%`
  - Purist category accuracy: `61.7%`
  - Pragmatic category accuracy: `69.2%`
- The main diagnostic rates were also unchanged except for a small evidence drop:
  - schema-valid prediction rate: `89.0%` in both runs
  - normalized-label exact: `44.7%` in both runs
  - evidence quote support: `94.0%` at `256` versus `93.6%` at `1024`
- The invalid-prediction count stayed exactly the same:
  - `33` invalid predictions
  - `25` `normalization.invalid_label`
  - `8` `schema.missing_value`
- Runtime got materially worse:
  - `256` run: `6.55` prediction seconds/record, `1957.9s` total
  - `1024` run: `9.99` prediction seconds/record, `2988.9s` total
- The invalid examples stayed the same shape: non-canonical surface forms such as
  `quarter`, `fortnight`, `several`, `few`, `1-2`, dropped cluster structure,
  and null/abstained labels where the scorer requires a label.
- A representative long-evidence case changed failure mode. In record `gan_11044`,
  the earlier `256` run returned a long quote truncated mid-word (`Continue levet`).
  The `1024` rerun returned an even longer quote that continued past the note into
  prompt wrapper text beginning `Respond with the corresponding output fields...`.
  That output remained schema-valid for the label, but it worsened evidence
  grounding.

### Interpretation

The full-validation artifact comparison does not support raising the default 35B
direct cap from `256` to `1024` as a quality improvement. The higher cap did not
change label validity, normalized-label accuracy, monthly-frequency accuracy, or
category accuracy on this 299-record validation set.

The dominant failure mode in the 35B direct path remains canonicalization, not
completion budget. The model is mostly producing short labels successfully under
the existing JSON-schema contract, but it still drifts into unsupported Gan
surface forms and occasionally abstains where a label is expected.

Increasing the cap did change output behavior for long evidence spans, but not in
the desired direction. Instead of cleanly fixing the one obvious truncation case,
the model sometimes over-generated and copied prompt footer text into the evidence
field. That makes a larger blanket output budget look less attractive for the
default direct path.

### Caveats

- This comparison changes only one runtime control, but it does so after the
  overnight run rather than in an interleaved A/B schedule.
- The evidence-support change is small and diagnostic-only; it should not be
  over-read as a benchmark-quality regression.
- `metrics.json` stores only sampled invalid examples in `errors.invalid_predictions`;
  the full invalid counts come from `error_analysis.counts`.
- This remains fixed-validation exploratory work, not published Gan benchmark
  reproduction.

### Next Steps

- Revert the default `Qwen3.6:35b` direct config to the smaller cap unless a
  separate evidence-length control is added.
- If long evidence remains a concern, test a targeted intervention instead:
  instruct the model to return the shortest sufficient contiguous quote, or cap
  evidence length post-hoc while preserving raw artifacts.
- Prioritize canonical label control next: cluster structure retention, forbidden
  units (`quarter`, `fortnight`), forbidden lexical alternatives (`few`,
  `several`), and range formatting (`1 to 2`, not `1-2`).
