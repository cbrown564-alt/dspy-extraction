# Gan S0 GEPA Harness Run 2026-05-19

Date: 2026-05-19

## Purpose

Close the remaining gap on the shared GEPA workstream by proving that the Gan S0 GEPA harness can do more than validate config shape and dry-run output. The target was a real capped GPT 4.1-mini run that compiles with `dspy.GEPA`, writes optimizer artifacts, and evaluates under unchanged `gan_frequency_deterministic_v1` scorer semantics.

## Scope

- Dataset/split: `gan_2026_fixed_v1:validation`
- Optimization train slice: first 4 Gan development records from `data/splits/gan_2026_splits.json`
- Evaluation cap: first 5 validation records
- Model/provider: `openai` / `gpt-4.1-mini`
- Program variant: `gan_frequency_s0_direct_single_pass`
- Prompt version: `gan_frequency_s0_synthesis_v1_gepa_harness`
- Optimizer: `GEPA`
- Optimizer metric: `synthesis_exact_with_evidence_feedback`
- Scorer mode: `gan_frequency_deterministic_v1`

## Integration Fixes Required

The first real run exposed two harness bugs that dry-run validation did not catch:

1. GEPA budget validation in `src/clinical_extraction/experiments/config.py` was too permissive. DSPy requires exactly one of `auto`, `max_full_evals`, or `max_metric_calls`, but the original config set both `max_full_evals` and `max_metric_calls`.
2. GEPA runtime support was incomplete in the optimizer path:
   - `dspy.GEPA` requires a reflection LM, so `scripts/run_experiment.py` now builds one from the active model config at higher temperature and passes it into `compile_gan_s0_module_gepa`.
   - GEPA state saving failed on DSPy dynamic signatures under default pickle, so the optimizer config now records `use_cloudpickle=true`, which is passed through `gepa_kwargs`.

These fixes were validated by:

```powershell
uv run --extra dev pytest tests/test_experiment_configs.py tests/test_gan_s0_program.py tests/test_run_artifacts.py
```

## Completed Artifact

Successful capped harness run:

- `runs/gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T052124Z`

The run wrote:

- `metrics.json`
- `predictions.json`
- `prompts.json`
- `artifacts/compiled_state.json`
- `artifacts/optimizer/summary.json`
- `artifacts/optimizer/logs/`

This satisfies the shared optimizer-harness milestone that required a model-backed capped run and artifact write, not just config validation and dry-run output.

## Metrics

Five-record capped validation summary:

- Schema validity: `80.0%`
- Normalized-label accuracy: `50.0%`
- Monthly-frequency accuracy: `75.0%`
- Purist category accuracy: `75.0%`
- Pragmatic category accuracy: `75.0%`
- Evidence quote support: `25.0%`
- Compile duration: `21.91s`
- Prediction duration: `8.35s`
- Prediction seconds/record: `1.67s`

Observed capped errors:

- `normalization.invalid_label`: 1
- `normalization.label_mismatch`: 2
- `classification.pragmatic_category_mismatch`: 1
- `evidence.unsupported_quote`: 3

## Selected Instruction Behavior

GEPA completed under the capped budget and proposed longer instruction variants that mostly reiterated:

- canonical Gan vocabulary constraints
- seizure-free threshold guidance
- cluster-format completeness
- evidence-as-exact-quote requirements

On this tiny overfit train-as-val setup, those proposals did not obviously improve held-out capped evidence behavior. The evaluation errors still concentrated in:

- unsupported quoted evidence with surrounding quotation marks or overlong paraphrase-like spans
- non-canonical frequency wording such as `several per week`
- semantic boundary errors around short seizure-free windows and cluster structure

## Interpretation

The important result is infrastructure, not quality. Shared GEPA support is now real:

- config validation matches DSPy runtime constraints
- the optimizer path provides a reflection LM
- the run harness can persist GEPA state for DSPy dynamic signatures
- capped runs write the expected optimizer artifacts

The next Gan GEPA step should not be more harness work. It should be metric work:

1. enrich the feedback metric from the current exact-label-plus-evidence contract into the planned Gan failure taxonomy
2. keep the capped comparison against the current synthesis prompt
3. inspect whether prompt growth is causing worse evidence quoting or label drift

## Remaining Cautions

- GEPA currently uses train-as-val because no explicit valset is passed to DSPy GEPA. That is acceptable for a harness smoke but not for claims about generalization.
- The proposed instruction text became long quickly. Future GEPA comparisons should track prompt length deliberately.
- Evidence support remains the weakest signal in this capped run, so richer feedback should emphasize exact contiguous quotes and quote-boundary control.
