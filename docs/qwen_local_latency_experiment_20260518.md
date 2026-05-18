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
