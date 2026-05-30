# Gan S0 G30 GEPA Teacher-Runner Smoke Results

Status: current synthesis / mechanism open
Date: 2026-05-30
Preregistration: `gan_s0_g30_gepa_teacher_runner_preregistration_20260530.md`

## Research Question

Can the Gan S0 evidence-first target selector run through a hosted GEPA
teacher-runner path where GPT-4.1-mini remains the prediction model and a
separate hosted GPT-5-family model supplies reflection feedback?

## Method

- Dataset and split: Gan 2026 synthetic, `gan_2026_fixed_v1:validation`.
- Gold label: `seizure_frequency_number[0]`; `reference` remains a secondary
  difficulty signal only.
- Program variant: `gan_frequency_s0_evidence_first_target_selector`.
- Prediction model config: `configs/models/gan_s0_gpt4_1_mini.json`.
- Reflection model config: `configs/models/gan_s0_gpt5_5_openai.json`.
- Scorer: primary `gan2026_paper_reproduction`; canonical Gan metrics remain
  diagnostic only.
- Fixed controls: loader, split, benchmark bridge, candidate-builder,
  G21 constructed answer options, closed-option copy repair policy, and
  prediction-repair semantics.

## Runs

| Arm | Config | Run ID | Result |
| --- | --- | --- | --- |
| Matched control smoke | `configs/experiments/gan_s0_g30_evidence_first_control_gpt4_1_mini_smoke6.json` | `gan_s0_g30_evidence_first_control_gpt4_1_mini_smoke6_20260530T200132Z` | Completed six-record live smoke. |
| GEPA smoke, initial live attempt | `configs/experiments/gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_smoke6.json` | `gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_smoke6_20260530T200159Z` | Compiled, then failed while serializing `reflection_model_config_path` as a Windows `Path`. |
| GEPA smoke, low-budget serialization check | same config, before budget correction | `gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_smoke6_20260530T200431Z` | Completed, but `max_metric_calls=4` was below the eight-record trainset base evaluation and did not exercise reflective proposal. |
| GEPA smoke, corrected teacher-runner gate | same config, now `max_metric_calls=12` | `gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_smoke6_20260530T200635Z` | Completed and exercised the GPT-5.5 reflection path. |

## Implementation Fix

The first GEPA live attempt exposed a runner artifact bug: optimizer payloads
were written with `OptimizerConfig.model_dump()`, which preserved
`reflection_model_config_path` as a `WindowsPath` and broke JSON serialization.
The runner now writes optimizer payloads with `model_dump(mode="json")` for
`prompts.json`, `artifacts/optimizer/summary.json`, and runtime metrics.

Regression coverage:

- `tests/test_experiment_runner.py::test_mock_runner_writes_gepa_optimizer_artifacts_with_reflection_path`

## Results

The matched control and corrected GEPA smoke both produced the same final labels
on the six smoke records:

| Record | Matched control | GEPA smoke |
| --- | --- | --- |
| `gan_10751` | `seizure free for 17 month` | `seizure free for 17 month` |
| `gan_11380` | `2 per 3 month` | `2 per 3 month` |
| `gan_12679` | `1 to 2 per month` | `1 to 2 per month` |
| `gan_13019` | `unknown` | `unknown` |
| `gan_14485` | `seizure free for 1 month` | `seizure free for 1 month` |
| `gan_10618` | `4 to 6 per day` | `4 to 6 per day` |

Metrics on the smoke slice were identical:

| Metric | Matched control | GEPA smoke |
| --- | ---: | ---: |
| Paper monthly accuracy | 0/6 | 0/6 |
| Paper purist category accuracy | 0/6 | 0/6 |
| Paper pragmatic category accuracy | 1/6 | 1/6 |
| Schema validity | 6/6 | 6/6 |
| Evidence quote support among present quotes | 5/5 | 5/5 |
| Missing prediction evidence | 1/6 | 1/6 |

The corrected GEPA run used 12 metric-call budget, recorded
`compile_duration_seconds=96.57`, and reported token usage across three
history entries: 10,010 prompt tokens, 5,561 completion tokens, and 15,571 total
tokens. Its `gepa_state.bin` records `total_num_evals=14`, one full dataset
evaluation, and one retained program candidate. GEPA did invoke the reflection
model and proposed a longer replacement instruction for `adjudicate`, but the
proposal was not retained because the two-example subsample score did not
improve over the seed instruction.

## Interpretation

G30 completes the hosted teacher-runner smoke gate:

- GPT-4.1-mini can remain the prediction runner while a distinct GPT-5.5 config
  is resolved and used for GEPA reflection.
- Runtime artifacts now preserve the prediction/reflection model distinction.
- The smoke preserved fixed scorer, loader, split, benchmark bridge,
  candidate-builder, constructor, and repair semantics.
- This smoke is not a benchmark-facing performance result and does not promote
  GEPA, the proposed reflected instruction, or the evidence-first selector.

The smoke result is mildly cautionary for GEPA: the first reflected proposal was
a long policy-wall style instruction and did not improve the sampled score. That
matches the R14 concern about instruction bloat, but it is only one tiny hosted
smoke and does not close GEPA as a mechanism.

## Caveats

- The six-record smoke slice is a runtime and validity gate, not a performance
  estimate.
- The GEPA config uses trainset as valset during compilation; this is acceptable
  for smoke plumbing but not a generalization design.
- Token usage is captured at run level, not split by prediction versus
  reflection model.
- The rejected reflected instruction was visible in runtime logs but is not
  retained as a promoted artifact because GEPA did not accept it.
- Frozen-test rows were not used for prompt wording, candidate surfaces,
  scorer changes, bridge changes, repair changes, or policy tuning.

## Decision

Decision scope: arm/runtime gate.

P2 completed the hosted teacher-runner smoke gate. The subsequent standard50
result is recorded in
`gan_s0_g30_gepa_teacher_runner_standard50_results_20260530.md`; that follow-up
exercised the 80-call optimizer budget but rejected the tested G30 GEPA arm at
41/50 paper monthly.

## Next Steps

1. Do not full-validate, run Qwen GEPA, or inspect frozen test for the tested
   evidence-first G30 GEPA arm.
2. Any future GEPA work should be a new compact or stripped-prompt mechanism
   card with its own standard50 gate and row ledger, because the standard50
   follow-up confirmed policy-wall expansion without benchmark-facing lift.
3. Keep `gan2026_paper_reproduction` as the primary benchmark-facing scorer and
   canonical Gan metrics diagnostic.
