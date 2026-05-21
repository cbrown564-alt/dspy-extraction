# Qwen DSPy Latency Policy

Date: 2026-05-18

## Correction From Max-Budget Follow-Up

The original policy over-attributed the failed `ChainOfThought +
BootstrapFewShot` run to Qwen3.6:35b CPU/RAM offload. The corrected diagnosis is
more specific:

- the earlier Qwen configs used completion budgets that were too small for
  visible DSPy reasoning plus demonstration-expanded prompts;
- local Qwen models must use Ollama/LiteLLM with `think=false`;
- setting `max_tokens=81920` is not enough by itself if Ollama keeps the active
  context at its default `4096`; max-budget runs should also request
  `num_ctx=262144`;
- even when truncation is removed, unconstrained `ChainOfThought` can be very
  slow and can still degrade schema validity.

The current max-budget configs are:

- `configs/models/gan_s0_qwen9b_ollama_max81920.json`
- `configs/models/gan_s0_qwen35b_ollama_max81920.json`

Use these only for explicit latency/reasoning stress tests, not as ordinary
interactive defaults.

## Decision

Do not make `ChainOfThought + BootstrapFewShot` the default path for
Qwen3.6:35b experiments.

Qwen3.6:35b currently does not fit fully in the available GPU memory on the
Windows laptop. Only about 8 GB is resident in VRAM, with roughly another
24 GB offloaded to system RAM. That runtime profile makes long prompts,
reasoning-token generation, repeated compile-time calls, and few-shot-expanded
prediction prompts too slow for normal interactive or capped validation loops.

The larger local-model workstream should still prefer direct structured
extraction without model-visible reasoning unless the experiment is explicitly
testing reasoning or optimizer effects. This is now a measured latency and
schema-stability decision, not just a partial-offload assumption.

## Why ChainOfThought Is Expensive Here

`dspy.ChainOfThought` adds a model-visible `reasoning` output before the final
structured fields. For Gan S0 this means the model generates:

- reasoning text
- `seizure_frequency_number`
- `evidence_text`

The deterministic pipeline only needs the label and evidence. On a partially
RAM-offloaded 35B model, every extra generated token has a high latency cost.
Reasoning may still be useful as an experimental factor, but it should not be
assumed necessary for larger models.

## Why BootstrapFewShot Is Expensive Here

`BootstrapFewShot` has two separate costs:

1. Compilation cost: DSPy runs the program over development examples and keeps
   traces that pass the optimizer metric.
2. Prediction cost: the compiled module can insert selected demonstrations into
   every later prediction prompt.

For clinical letters, each demonstration may include a full note, reasoning,
label, and evidence. A run that used to resemble one model call per document
can become dozens of compile-time calls plus larger prompts for every validation
record.

This may be acceptable for small or hosted models. It is not a good default for
Qwen3.6:35b under partial CPU/RAM offload.

## Workstreams

Maintain two independent experiment workstreams.

### Smaller/Faster Model Optimization Workstream

Use this workstream to evaluate whether `ChainOfThought`, `BootstrapFewShot`,
or their combination improves quality enough to justify complexity.

Candidate models:

- GPT 4.1-mini
- Qwen3.5:9b, because it should fit fully in GPU VRAM on the target laptop

This workstream can test:

- direct extraction versus `ChainOfThought`
- zero-shot versus labeled few-shot
- `BootstrapFewShot` versus hand-curated examples
- optimizer metric variants
- prompt-length and latency tradeoffs

Qwen3.5:9b testing is useful, but secondary. Its results should not force the
Qwen3.6:35b path to use the same optimizer or reasoning strategy.

### Larger Model Direct-Extraction Workstream

Use this workstream for Qwen3.6:35b and larger closed models when the goal is
to measure strong-model extraction behavior.

Default assumptions:

- Prefer direct structured prediction over `ChainOfThought`.
- Do not require model-visible reasoning unless it is the experimental factor.
- Avoid `BootstrapFewShot` in normal capped and full-validation runs.
- Use compact label-policy guidance and deterministic postprocessing where
  possible.
- Treat prompt length and generated-token count as first-class constraints.

`BootstrapFewShot` may still be tested with larger closed models, where latency
and cost are acceptable for a bounded comparison. It may also be run overnight
with Qwen3.6:35b, but those runs should be explicitly marked as optimizer
experiments and should not block ordinary pipeline development.

## Practical Gate Before Qwen3.6:35b Runs

Before running Qwen3.6:35b beyond a one-record smoke:

- Confirm the config has no optimizer unless the run is an explicit overnight
  optimizer experiment.
- Confirm the program variant does not use `ChainOfThought` unless reasoning is
  the factor being tested.
- Estimate model-call count before launch.
- Estimate prompt expansion from any demos.
- Prefer a one-record smoke, then a very small capped run, before scaling.
- Record whether the model was fully GPU-resident or partially offloaded.

## Interpretation

If `ChainOfThought + BootstrapFewShot` is too slow on Qwen3.6:35b, that is a
runtime and experiment-design result, not a failure of the local-model research
goal. The research question should shift to whether larger models can achieve
acceptable extraction quality without explicit reasoning or optimizer-expanded
few-shot prompts.
