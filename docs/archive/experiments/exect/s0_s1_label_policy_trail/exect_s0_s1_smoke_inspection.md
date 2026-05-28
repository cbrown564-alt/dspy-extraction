# ExECT S0/S1 Smoke Inspection

Date: 2026-05-18

## Context

The ExECT S0/S1 field-family baseline had a completed DSPy contract and dry-run path. The next Kanban pull was to run a capped GPT 4.1-mini validation smoke and inspect the artifacts before deciding whether to scale or add label-policy examples.

This is a capped validation smoke only. It is not a performance estimate and is not published ExECTv2 benchmark reproduction.

## Work Completed

Run artifact:

- `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T154456Z`

Config and controls:

- Experiment config: `configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json`
- Model config: `configs/models/gan_s0_gpt4_1_mini.json`
- Dataset: `exect_v2`
- Split: `exectv2_fixed_v1:validation`
- Cap: 3 records
- Schema level: `exect_s0_s1_field_family`
- Program variant: `exect_s0_s1_field_family_single_pass`
- Scorer mode: `exect_field_family_deterministic_v1`
- Context policy: full note
- Few-shot policy: none
- Verifier, repair, and abstention policy: none
- Structured output strategy: provider JSON schema with Pydantic validation

Validation before the model call:

```text
uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py
```

Result: 20 passed.

Dry-run command:

```text
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --env-file .env --dry-run
```

Run command:

```text
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --env-file .env
```

## Artifact Check

The run produced the expected standard artifacts:

- `metadata.json`
- `config.json`
- `prompts.json`
- `predictions.json`
- `metrics.json`
- `errors.json`

The predictions file uses the shared `PredictionSet` layout with `dataset = "exect_v2"`, `schema_level = "exect_s0_s1_field_family"`, and field values under the benchmark-facing families `diagnosis`, `seizure_type`, and `annotated_medication`.

## Results

On the three capped validation records:

| Metric | Value |
|---|---:|
| Micro precision | 61.5% |
| Micro recall | 80.0% |
| Micro F1 | 69.6% |
| Diagnosis F1 | 50.0% |
| Seizure-type F1 | 80.0% |
| Annotated-medication F1 | 66.7% |
| Documents with gold quality flags | 0.0% |

Field-family support in the capped slice:

- Diagnosis: 2
- Seizure type: 5
- Annotated medication: 3

## Observations

The run validates the model-backed artifact path. The program produced schema-valid artifacts for the capped records, and the evaluator reported per-family metrics and bounded mismatch records.

The main errors are label-policy and annotation-surface issues rather than structural failures:

- `EA0008` diagnosis: predicted `focal epilepsy`; gold expected `symptomatic structural focal epilepsy`.
- `EA0008` medication: predicted `levetiracetam` from "To start levetiracetam", but this is not in the current annotated prescription scoring view.
- `EA0018` seizure type: one output preserved the richer phrase `temporal lobe onset focal seizures`; gold expected the benchmark-facing `temporal lobe seizure`.
- `EA0018` medication: predicted previously tried or planned drugs (`carbamazepine`, `lamotrigine`) as annotated medications.

Evidence behavior is mixed. Most values have source quotes, but at least one emitted seizure type carried `missing_evidence`, and one levetiracetam quote had null offsets because the model returned an ellipsis-containing non-contiguous quote.

## Interpretation

The ExECT baseline is ready for prompt/policy tightening before any larger validation run. The capped smoke confirms the runner, bridge, and scorer path, but the current zero-shot single-pass prompt is too permissive about clinically plausible labels and medication mentions.

The highest-value next improvement is not a scorer change. It is to add benchmark-facing label-policy examples or constraints that teach:

- prescription scoring is tied to the audited annotated medication view, not all clinically mentioned medicines;
- planned and previous medication mentions remain outside the benchmark-facing medication metric for this baseline;
- seizure-type labels should be canonical benchmark-facing surfaces when the scorer has a coarser label;
- diagnosis surfaces should preserve audited canonical labels rather than over-collapse clinically rich diagnosis phrases unless that mapping is explicitly tested.

## Caveats

This run is capped at three validation records and should not be used as a performance estimate.

The metrics are partial ExECT S0/S1 diagnostics over diagnosis, seizure type, and annotated medication only. They exclude investigation, history, birth history, aetiology, onset, diagnosis-date, seizure frequency, and medication temporality.

Medication temporality remains clinically important but intentionally outside benchmark-facing medication metrics for this baseline because the ExECT prescription gold lacks reliable temporality.

## Next Steps

1. Add ExECT benchmark-facing label-policy examples or a constrained prompt policy for the same single-pass field-family module.
2. Add or verify mocked-LM tests for planned/previous medication exclusion, canonical seizure-type granularity, and diagnosis label preservation.
3. Re-run the same capped smoke config or a sibling config that changes only the prompt/example policy.
4. Defer full validation and section-aware ablations until the capped label-policy run shows cleaner benchmark-facing behavior.

## 2026-05-18 Label-Policy V2 Follow-Up

### Context

The next Kanban pull was to tighten ExECT S0/S1 benchmark-facing prompt policy without changing scorer semantics. The first implementation attempt exposed a conflict between recovered prior prompt guidance and the current audited scorer: older notes recommended mapping `symptomatic structural focal epilepsy` to `focal epilepsy`, but the current `exect_field_family_deterministic_v1` scorer expects the explicit audited label for EA0008. The final v2 policy therefore preserves current audited diagnosis surfaces rather than forcing a five-label diagnosis set.

### Work Completed

Code and config changes:

- `src/clinical_extraction/programs/exect_s0_s1.py`: bumped prompt version to `exect_s0_s1_field_family_v2_label_policy`, embedded benchmark-facing guidance and boundary examples, expanded diagnostic allowed diagnosis labels to match the current audited scorer vocabulary, and kept bridge/scorer semantics unchanged.
- `scripts/run_experiment.py`: records ExECT label-policy guidance and examples in `prompts.json`.
- `configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json`: now uses the v2 prompt policy while preserving dataset, split, model, scorer, schema level, cap, context policy, verifier policy, repair policy, and abstention policy.
- `tests/test_exect_s0_s1_program.py` and `tests/test_experiment_configs.py`: added focused mocked-LM/config coverage for planned/previous medication exclusion, audited diagnosis preservation, seizure-type granularity, plural seizure-type preservation, and prompt-version traceability.

Validation:

```text
uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py
```

Result: 24 passed.

Dry run:

```text
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --dry-run
```

Result: config resolved the same capped 3-record validation slice.

Final capped model run:

```text
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --env-file .env
```

Run artifact:

- `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T155638Z`

### Results

On the same three capped validation records:

| Metric | V1 smoke | V2 label-policy smoke |
|---|---:|---:|
| Micro precision | 61.5% | 88.9% |
| Micro recall | 80.0% | 80.0% |
| Micro F1 | 69.6% | 84.2% |
| Diagnosis F1 | 50.0% | 100.0% |
| Seizure-type F1 | 80.0% | 66.7% |
| Annotated-medication F1 | 66.7% | 100.0% |

### Observations

The policy change fixed the capped diagnosis and medication failures:

- EA0008 now predicts `symptomatic structural focal epilepsy`, matching the current scorer label.
- EA0018 now predicts `epilepsy`, matching the current scorer label instead of over-specifying `focal epilepsy`.
- Planned/previous medication overreach from the first smoke is no longer present on this slice; annotated-medication F1 is 100%.

The remaining labeled mismatch is seizure-type granularity on EA0018:

- Prediction: `temporal lobe onset focal seizures`
- Gold expects: `temporal lobe seizure` and `focal seizures`
- The model also correctly emitted `occipital lobe seizures`.

Evidence remains a diagnostic concern. EA0016 and one EA0018 medication evidence quote used ellipsis-containing non-contiguous text, producing null offsets. The ExECT field-family scorer does not yet aggregate evidence quote support, so this should be inspected separately before scaling.

### Interpretation

The v2 policy is useful but not sufficient for full validation. It corrected medication scope and current-scorer diagnosis alignment on the capped slice, while showing that seizure-type surface policy still needs a more explicit audited mapping/splitting rule. The main lesson is that recovered prompt guidance must be checked against the current loader/scorer vocabulary before being treated as benchmark policy.

### Caveats

This is still a capped 3-record smoke, not a performance estimate and not published ExECTv2 benchmark reproduction. Metrics are partial S0/S1 diagnostics over diagnosis, seizure type, and annotated medication only. The v1 and v2 runs are comparable only as capped smoke checks because the prompt policy changed while scorer semantics stayed fixed.

### Next Steps

1. Add an explicit seizure-type policy example or normalization decision for fused surfaces such as `temporal lobe onset focal seizures` when the current gold expects separate `temporal lobe seizure` and `focal seizures`.
2. Add ExECT evidence-support aggregation or a focused artifact inspection check before any full validation run.
3. Re-run the same capped smoke after the seizure-type follow-up before moving to full validation or section-aware ablations.

## 2026-05-18 Seizure-Type And Evidence Follow-Up

### Context

The v2 label-policy smoke fixed medication scope and diagnosis alignment on the capped slice, but EA0018 still exposed a fused seizure-type surface: the model emitted `temporal lobe onset focal seizures` while the current audited scorer view expects two benchmark-facing labels, `temporal lobe seizure` and `focal seizures`. The same run also showed that evidence quote quality needed an explicit diagnostic aggregation path before any full validation.

### Work Completed

Code and config changes:

- `src/clinical_extraction/programs/exect_s0_s1.py`: bumped the prompt version to `exect_s0_s1_field_family_v3_seizure_evidence_policy`, added a fused seizure-type policy example, and added a narrow benchmark bridge that splits `temporal lobe onset focal seizures`-style outputs into `temporal lobe seizure` plus `focal seizures`.
- `src/clinical_extraction/evaluation/exect.py`: added ExECT value-level evidence quote diagnostics using the shared deterministic evidence support check. These diagnostics report quote support, offset presence, offset validity, and bounded evidence errors without changing field-family scorer semantics.
- `scripts/run_experiment.py`: prints ExECT evidence diagnostics in the run summary.
- `configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json`: now records the v3 prompt policy.
- `tests/test_exect_s0_s1_program.py` and `tests/test_exect_scoring.py`: added mocked-LM coverage for fused seizure-type bridge behavior and ExECT evidence aggregation.

Validation:

```text
uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py
```

Result: 26 passed.

Dry run:

```text
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --dry-run
```

Result: config resolved the same capped 3-record validation slice.

Final capped model run:

```text
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --env-file .env
```

Run artifact:

- `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T160445Z`

### Results

On the same three capped validation records:

| Metric | V2 label-policy smoke | V3 seizure/evidence smoke |
|---|---:|---:|
| Micro precision | 88.9% | 100.0% |
| Micro recall | 80.0% | 100.0% |
| Micro F1 | 84.2% | 100.0% |
| Diagnosis F1 | 100.0% | 100.0% |
| Seizure-type F1 | 66.7% | 100.0% |
| Annotated-medication F1 | 100.0% | 100.0% |
| Evidence quote support | not aggregated | 90.0% |
| Evidence offsets present | not aggregated | 90.0% |
| Evidence offsets valid | not aggregated | 100.0% |

### Observations

The bridge split EA0018's fused `temporal lobe onset focal seizures` output into the two current benchmark-facing labels and tagged both values with `benchmark_bridge:fused_seizure_type_split`. This is bridge behavior, not a scorer semantic change.

Evidence diagnostics now surface the remaining source-grounding issue: one EA0018 medication evidence quote used an ellipsis (`Currently she is taking ... levetiracetam 1000 mg twice today`) and was counted as unsupported because it is not a contiguous source quote.

### Interpretation

The capped v3 smoke clears the immediate seizure-type granularity blocker and adds the evidence-support aggregation needed before scaling. The capped slice is still too small for performance claims. Before full validation, the remaining open question is whether unsupported ellipsis evidence quotes are common enough to justify a verifier/repair step or stricter prompt/evidence example work.

## 2026-05-18 Ellipsis Evidence Bridge Follow-Up

### Context

The v3 capped smoke left one unsupported medication evidence quote on EA0018 because the model returned a literal ellipsis quote: `Currently she is taking ... levetiracetam 1000 mg twice today`. The source sentence was contiguous, so this was a recoverable artifact-bridge issue rather than a label scorer issue.

### Work Completed

Code changes:

- `src/clinical_extraction/programs/exect_s0_s1.py`: added a narrow evidence bridge that repairs literal `...` quotes only when all non-empty fragments can be located in order inside one short same-paragraph source span.
- `tests/test_exect_s0_s1_program.py`: added regression coverage using EA0018's levetiracetam evidence quote.

Validation:

```text
uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py
```

Result: 27 passed.

Dry run:

```text
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --dry-run
```

Result: config resolved the same capped 3-record validation slice.

### Interpretation

This is diagnostic bridge behavior, not benchmark-facing scorer behavior. Repaired spans are tagged with `evidence_repair:ellipsis_contiguous_span`, allowing later reports to separate model-provided exact quotes from deterministic quote repairs.

The next reasonable ExECT pull is a larger capped validation run with the same label policy and bridge behavior, followed by artifact inspection before any full validation or section-aware ablation.

## 2026-05-19 Label-Policy V4 Follow-Up

### Context

After the v3 monolithic full-validation read (`docs/experiments/exect/exect_s0_s1_validation_full_inspection.md`, micro F1 67.8%), the next Kanban pull targeted benchmark label-policy alignment without scorer changes: seizure-type splitting (secondary generalisation), convulsive modifiers on focal to bilateral seizures, diagnosis uncertainty stripping, cross-family leakage boundaries, and symptomatic structural focal preservation.

### Work Completed

- `src/clinical_extraction/programs/exect_s0_s1.py`: prompt version `exect_s0_s1_field_family_v4_label_policy`; expanded guidance/examples; deterministic bridges for fused secondary-generalisation splits, focal-to-bilateral convulsive modifier, and diagnosis uncertainty prefix stripping. Preserved `EXECT_S0_S1_V3_PROMPT_VERSION` for anchor configs.
- `data/fixtures/exect_s0_label_policy_error_regression_slice.json`: 12-record slice from full-validation failure clusters.
- `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json`: v4 regression-slice gate config.
- `configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json`: smoke now tracks v4; cap-25/full validation configs remain on v3 anchor.
- Tests: 3 new bridge tests + regression-slice config contract.

### Validation

```text
uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py -k exect_s0_s1 -q
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json --dry-run
```

### Next Pull

1. Run the 12-record regression slice with `--env-file .env` and inspect artifacts before cap-25/full re-run.
2. Keep v3 runs as the comparison anchor until v4 clears the slice gate.
