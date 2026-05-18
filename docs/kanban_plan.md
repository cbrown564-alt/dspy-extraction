# Clinical Extraction Kanban Plan

Source: `docs/outline.md`  
Grounding note: `docs/deterministic_foundation_decisions.md`  
Last refreshed: 2026-05-18

## Goal

Build a hybrid deterministic and DSPy-based clinical extraction research system that can specialize across the broad ExECTv2 schema and the focused Gan seizure-frequency task, while preserving dataset fidelity, reproducible splits, auditable scoring, and experiment traceability.

The project has moved beyond the deterministic foundation milestone. The current execution focus is tightening the first ExECT S0/S1 field-family baseline after capped model-backed smokes exposed label-policy, medication-scope, seizure-type granularity, and evidence-quote errors.

## Definitions Of Done

- ExECTv2 and Gan gold labels load from the agreed primary sources without silently changing scorer semantics.
- Raw values, normalized values, quality flags, evidence diagnostics, and benchmark-facing scoring views remain separable.
- Gan has reproducible train/dev/test splits with documented salt, allocation policy, stratification metadata, and hard-case counts.
- Deterministic scorers expose benchmark-facing metrics and diagnostic metrics separately.
- DSPy programs record dataset, split, model/provider, schema level, program variant, scorer mode, prompts/configs, predictions, metrics, errors, artifacts, and metric caveats.
- Experiment reports do not compare across changed scorer semantics unless the report says so explicitly.

## Background: Completed Foundation

The deterministic foundation is complete enough to support model-backed experiments. The repo now has the `clinical_extraction` package, pytest configuration, ExECTv2 and Gan loaders, Gan normalization, Gan deterministic scoring, reproducible Gan splits, dataset manifest validation, deterministic scorer semantics documentation, shared prediction/evidence schemas, a baseline evaluation CLI, run artifact layout, evidence support scoring, error-analysis reports, bootstrap confidence intervals, and review queue export.

Key validation and documentation artifacts:

- `tests/test_exect_loader.py`
- `tests/test_gan_loader_and_splits.py`
- `tests/test_gan_frequency.py`
- `tests/test_gan_scoring.py`
- `tests/test_dataset_manifest.py`
- `tests/test_prediction_schemas.py`
- `tests/test_evaluation_cli.py`
- `tests/test_run_artifacts.py`
- `tests/test_evidence_scoring.py`
- `tests/test_bootstrap_confidence.py`
- `tests/test_review_export.py`
- `docs/deterministic_scorer_semantics.md`
- `docs/gan_deterministic_normalization_baseline.json`

Important dataset-policy decisions are also recorded. ExECT benchmark-facing S0/S1 scoring is limited to audited diagnosis, seizure type, and annotated medication fields. Planned/current medication status is excluded from benchmark-facing medication metrics for now because the ExECT prescription gold lacks reliable temporality. Gan `seizure_frequency_number[0]` remains the gold label, while `reference[0]` is metadata and a difficulty signal.

## Background: Completed DSPy And Experiment Infrastructure

The first model-backed path is implemented around a narrow Gan S0 seizure-frequency task. The repo has provider/model configuration, constrained JSON strategy documentation, experiment config validation, model comparison configs, a run experiment script, DSPy/LiteLLM integration, and a proper `dspy.Signature` plus `dspy.ChainOfThought` Gan S0 module.

Completed infrastructure and decision artifacts include:

- `clinical_extraction.programs.gan_frequency_s0`
- `clinical_extraction.llms`
- `clinical_extraction.experiments.config`
- `scripts/run_experiment.py`
- `configs/models/`
- `configs/experiments/gan_s0_baseline_gpt4_1_mini.json`
- `docs/first_dspy_schema_sequence.md`
- `docs/constrained_json_decoding_strategy.md`
- `docs/published_benchmark_metrics.md`

The current model-backed Gan S0 sequence has already produced useful lessons:

- Zero-shot GPT 4.1-mini on 25 validation records had low schema validity, showing that the model needed label-vocabulary examples.
- BootstrapFewShot improved valid output coverage but exposed frequency unit/window errors and weak evidence quote support.
- Synthesis-backed BootstrapFewShot, using prior prompt/error-analysis guidance, produced the current strongest full-validation run.

Most recent full-validation artifact:

- `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z`

Full-validation summary on 299 validation records:

- Schema validity: 97.3%
- Normalized-label accuracy: 51.5%
- Monthly-frequency accuracy: 62.9%
- Purist category accuracy: 70.1%
- Pragmatic category accuracy: 73.9%
- Evidence quote support: 89.9%

The first full-validation error read and surface-repair pass is complete in `docs/gan_s0_full_validation_error_read.md`. The artifact bridge now preserves raw model output while normalizing repairable surface forms such as quoted special labels and matching-count denominator ranges. Incomplete cluster labels, `unknown per cluster`, abstentions, and semantic cluster-to-unknown mistakes remain unresolved because repairing them requires additional evidence-aware rule or model logic.

The post-repair replay is complete in `docs/gan_s0_post_repair_validation_replay.md`. Replaying the current artifact bridge over the stored full-validation raw outputs changed exactly three predictions, reducing invalid predictions from 8 to 5 and improving schema validity from 97.3% to 98.3% without changing scorer semantics. Remaining Gan failures are semantic or evidence-grounding failures and should be handled only by an explicit verifier/repair or abstention-calibration variant.

The first ExECT S0/S1 baseline contract is drafted in `docs/exect_s0_s1_baseline_design.md`, and capped GPT 4.1-mini smokes are inspected in `docs/exect_s0_s1_smoke_inspection.md`. The model-backed path is scoped to audited diagnosis, seizure type, and annotated medication field families under `exect_field_family_deterministic_v1`; broader clinical fields and medication temporality remain deferred. The first capped smoke validated the artifact path but showed the zero-shot prompt was too permissive about clinically plausible labels, planned/previous medication mentions, and richer seizure-type surfaces. The v2 label-policy smoke improved the same capped slice to micro F1 84.2%, diagnosis F1 100.0%, and annotated-medication F1 100.0%, but seizure-type granularity and exact evidence quote support remain unresolved.

## Ready

### Tighten ExECT seizure-type granularity and evidence policy

- Outcome: The ExECT S0/S1 single-pass field-family baseline handles fused seizure-type surfaces such as `temporal lobe onset focal seizures` against the current audited scorer view and has an explicit evidence-support inspection or aggregation path before full validation.
- Dependencies: ExECT S0/S1 label-policy v2 capped smoke.
- Parallelizable: yes, subject to API credentials and rate limits.
- Owner: unassigned.
- Validation: Focused mocked-LM tests for fused seizure-type policy and evidence quote behavior; dry-run and capped GPT 4.1-mini smoke using the same validation cap. Inspect `predictions.json`, `errors.json`, and evidence offsets before scaling.
- Notes: This should not silently change scorer semantics. If normalization or label splitting is added outside the prompt, document whether it is benchmark-facing bridge behavior or a scorer-policy change.

### Run Qwen Gan S0 smoke tests on Windows laptop

- Outcome: Qwen3.6:35b and Qwen3.5:9b each have a one-record Gan S0 smoke run from the Windows laptop, using the same single-pass smoke configs and standard run artifact layout.
- Dependencies: Windows laptop with Ollama running; `qwen3.6:35b` and `qwen3.5:9b` installed; repo dependencies installed with `uv`; `.env` present if needed by shared scripts.
- Parallelizable: no, because both runs depend on the Windows local-model runtime.
- Owner: unassigned.
- Validation: `uv run --extra dev pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py tests/test_experiment_configs.py`; dry runs for `configs/experiments/gan_s0_smoke_qwen35b_ollama.json` and `configs/experiments/gan_s0_smoke_qwen9b_ollama.json`; completed run artifacts for both Qwen smoke configs.
- Notes: Handoff commands and Mac-side smoke results are documented in `docs/model_config_smoke_tests.md`. Treat these one-record runs as runtime compatibility checks only, not performance estimates.

### Resolve Gemini 3 Flash model identifier

- Outcome: Complete. `configs/models/gan_s0_gemini3_flash.json` uses the API-listed Gemini 3 Flash Preview model identifier, `gemini-3-flash-preview`.
- Dependencies: Confirmed with the configured Google API key that `models/gemini-3-flash-preview` is available and supports `generateContent`.
- Parallelizable: yes.
- Owner: unassigned.
- Validation: `uv run --extra dev pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py tests/test_experiment_configs.py`; dry-run `configs/experiments/gan_s0_smoke_gemini3_flash.json`; completed smoke artifact `runs/gan_s0_smoke_gemini3_flash_20260518T134109Z`.
- Notes: The Mac smoke attempt reached Google but failed with 404 for invalid `models/gemini-3-flash`; see `docs/model_config_smoke_tests.md`. The fixed smoke run completed but produced one invalid Gan label, so it validates provider/runtime compatibility rather than extraction quality.

## In Progress

No active implementation card is claimed in this plan.

## Review

No active review card is claimed in this plan.

## Done

Completed work is summarized in the background sections above rather than repeated as foreground cards.

### Inspect post-repair Gan S0 validation behavior

- Outcome: Complete. `docs/gan_s0_post_repair_validation_replay.md` compares the original full-validation run with a post-repair replay.
- Validation: Derived artifact `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_surface_replay_20260518T000000Z`; invalid predictions 8 -> 5; schema validity 97.3% -> 98.3%; normalized-label accuracy 51.5% -> 52.0%; monthly/Purist/Pragmatic accuracy 62.9%/70.1%/73.9% -> 63.3%/70.4%/74.1%; evidence quote support 89.9% -> 90.0%.
- Notes: Scorer semantics are preserved. Remaining Gan errors are not deterministic surface-repair candidates.

### Decide next Gan repair boundary

- Outcome: Complete. No further deterministic Gan repair should be added before ExECT; semantic Gan work should be an explicit verifier/repair or abstention-calibration variant.
- Validation: Decision recorded in `docs/gan_s0_post_repair_validation_replay.md` and this plan.
- Notes: Incomplete clusters, `unknown per cluster`, abstentions, unknown/no-reference confusion, and temporal-window denominator errors remain outside deterministic postprocessing.

### Add targeted Gan failure regression fixtures

- Outcome: Complete. Regression coverage now asserts the current boundary for incomplete clusters, frequent-to-unknown mismatches, unknown/no-reference confusion, denominator/window mismatch, abstentions, missing evidence, and unsupported evidence quotes.
- Validation: `uv run --extra dev pytest tests/test_evaluation_cli.py tests/test_gan_s0_program.py tests/test_gan_scoring.py`.
- Notes: The evaluator now records `abstention.predicted_abstention` even when the abstention is schema-invalid because the label value is missing.

### Draft ExECT S0/S1 baseline design

- Outcome: Complete. `docs/exect_s0_s1_baseline_design.md` defines the combined audited diagnosis, seizure-type, and annotated-medication baseline.
- Validation: Design reviewed against `docs/exect_gold_label_audit.md`, `docs/deterministic_scorer_semantics.md`, `docs/prior_prompt_error_analysis_synthesis.md`, existing ExECT loader/scorer code, and current shared prediction schema.
- Notes: Benchmark-facing fields remain diagnosis, seizure type, and annotated medications only. Investigation, history, birth history, aetiology, onset, diagnosis-date, seizure frequency, and medication temporality remain deferred.

### Prepare Gan S0 provider smoke configs and Windows Qwen handoff

- Outcome: Complete. One-record Gan S0 smoke experiment configs exist for GPT 4.1-mini, GPT 5.5, Gemini 3 Flash, Qwen3.6:35b, and Qwen3.5:9b, and the Windows Qwen handoff is documented in `docs/model_config_smoke_tests.md`.
- Validation: `uv run --extra dev pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py tests/test_experiment_configs.py`; dry-runs passed for all five smoke configs.
- Notes: GPT 4.1-mini completed `runs/gan_s0_smoke_gpt4_1_mini_20260518T130500Z`; GPT 5.5 completed `runs/gan_s0_smoke_gpt5_5_openai_20260518T130600Z` after changing its config to omit unsupported temperature. Gemini is blocked on model identifier/API-version 404. Qwen smoke runs are deferred to the Windows laptop.

### Implement ExECT S0/S1 DSPy field-family baseline contract

- Outcome: Complete. `clinical_extraction.programs.exect_s0_s1` defines the benchmark-facing ExECT S0/S1 DSPy signature/module, example helper, artifact bridge, and run metadata for diagnosis, seizure type, and annotated medication field families.
- Validation: `uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py`; `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --dry-run`.
- Notes: The bridge preserves raw model phrases, normalizes benchmark-facing values with audited ExECT normalizers, collapses parent diagnosis labels when a more specific child is emitted, flags unsupported diagnosis labels and missing evidence, and does not infer seizure types from diagnosis. `scripts/run_experiment.py` now dispatches Gan and ExECT configs through the appropriate loader, module, metadata, and evaluator.

### Run capped ExECT S0/S1 field-family smoke

- Outcome: Complete. A capped GPT 4.1-mini validation smoke run exists for the ExECT S0/S1 field-family baseline, with predictions, metrics, errors, prompts/config snapshots, and an artifact inspection note in `docs/exect_s0_s1_smoke_inspection.md`.
- Validation: `uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py`; dry-run `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --env-file .env --dry-run`; capped run `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T154456Z`.
- Notes: The run validated the artifact path and produced partial capped metrics: micro precision 61.5%, micro recall 80.0%, micro F1 69.6%; diagnosis F1 50.0%, seizure-type F1 80.0%, annotated-medication F1 66.7%. This is not a performance estimate. Main failure modes were label-policy granularity, planned/previous medication scope, and evidence quote quality.

### Add ExECT S0/S1 label-policy examples

- Outcome: Complete. The ExECT S0/S1 single-pass field-family baseline now has v2 benchmark-facing prompt policy and examples for audited diagnosis labels, medication-scope exclusion, seizure-type surfaces, and evidence quote expectations.
- Validation: `uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py`; dry-run `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --dry-run`; capped run `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T155638Z`.
- Notes: Scorer semantics are unchanged. Final v2 capped smoke on the same three validation records: micro precision 88.9%, micro recall 80.0%, micro F1 84.2%; diagnosis F1 100.0%, seizure-type F1 66.7%, annotated-medication F1 100.0%. The policy corrected medication scope and current-scorer diagnosis alignment, but EA0018 still needs seizure-type granularity handling and evidence quote support remains diagnostic-only.

## Blocked

### Reproduce published ExECTv2 and Gan benchmark numbers

- Outcome: Repo can run benchmark-aligned reproduction or comparison against the published ExECTv2 and Gan values.
- Dependencies: Benchmark reference constants and caveats; CUI/feature-aware ExECT all-family scorer; access to or reconstruction of Gan Real(300)/Real(150) evaluation sets.
- Parallelizable: after missing scorer/data prerequisites.
- Owner: unassigned.
- Validation: Benchmark-aligned comparison tests and a report that states exact metric alignment.
- Notes: Current repo metrics are partial/diagnostic for published-benchmark purposes. Do not claim reproduction from the current synthetic Gan subset or ExECT S0/S1 field-family scorer.

### Run Qwen-backed local model comparisons

- Outcome: Qwen3.6:35b and Qwen3.5:9b runs are included in the model comparison matrix.
- Dependencies: Local Ollama availability; validated Qwen model configs; stable task config.
- Parallelizable: after local runtime availability is confirmed.
- Owner: unassigned.
- Validation: Run artifacts with identical split, scorer, schema level, and program variant to the closed-provider runs.
- Notes: This is an environment blocker, not a code-design blocker.

## Backlog

### Implement Gan evidence-aware verifier and repair module

- Outcome: A DSPy verifier/repair step can accept Gan S0 predictions, source text, and initial evidence, then either confirm, repair, or abstain with auditable metadata.
- Dependencies: Decide next Gan repair boundary; targeted Gan failure regression fixtures.
- Parallelizable: after decision and fixture cards.
- Owner: unassigned.
- Validation: Mocked-LM tests plus a capped real-model run comparing extraction-only versus extract-verify-repair.
- Notes: The module should target semantic failures that deterministic surface repair should not handle: temporal-window errors, no-reference/unknown confusion, unsupported evidence quotes, and cluster semantics.

### Add Gan abstention calibration

- Outcome: Gan S0 reports distinguish wrong labels, invalid labels, unsupported evidence, and explicit abstentions with a clear threshold or policy.
- Dependencies: Gan verifier/repair design or decision to keep extraction-only.
- Parallelizable: after next Gan repair boundary.
- Owner: unassigned.
- Validation: Evaluation report includes abstention rate, accuracy on non-abstained predictions, evidence support on non-abstained predictions, and examples.
- Notes: This should not inflate headline accuracy without reporting coverage.

### Add field-group and section-aware DSPy modules

- Outcome: Reusable DSPy modules support monolithic extraction, field-group extraction, section-aware context-then-extract, and context selection as explicit program variants.
- Dependencies: ExECT S0/S1 baseline design; existing sectioning/context selection utilities.
- Parallelizable: after ExECT baseline design, but coordinate with ExECT baseline implementation.
- Owner: unassigned.
- Validation: Unit tests with mocked LM outputs plus at least one capped real-model smoke run.
- Notes: Treat program variants as first-class experiment factors, not prompt-only changes.

### Add experiment config files for ablations

- Outcome: Configs define monolithic, field-group, section-aware, context-then-extract, extract-verify-repair, and abstention variants.
- Dependencies: Field-group/section-aware DSPy modules; Gan verifier/repair module where relevant.
- Parallelizable: after module interfaces stabilize.
- Owner: unassigned.
- Validation: Config schema validation.
- Notes: Configs must pin dataset, split, model, schema level, program variant, scorer mode, structured-output strategy, and metric caveats.

### Improve review workflow around exported queues

- Outcome: Low-confidence or conflicting extractions can be reviewed in a lightweight workflow that consumes the existing JSONL review export.
- Dependencies: Review export; current or future UI choice.
- Parallelizable: yes.
- Owner: unassigned.
- Validation: A sample review queue can be opened, reviewed, and linked back to run artifacts.
- Notes: The moved `exect-explorer/` React app is a possible future UI foundation, but should not block the simple export workflow.

## Questions

### Should Gan continue before ExECT?

- Decision: Run the post-repair Gan S0 validation replay/report, then pivot the next main implementation cycle to the ExECT S0/S1 baseline.
- Outcome: Resolved. Gan remains the focused reference task for smoke tests and later verifier/repair ablations, but another Gan semantic repair cycle should not block opening ExECT.
- Dependencies: Inspect post-repair Gan S0 validation behavior; Draft ExECT S0/S1 baseline design.
- Parallelizable: no, because it selects the next implementation path.
- Owner: User; Codex.
- Validation: This plan and the relevant implementation card reflect the decision.
- Notes: If the post-repair replay reveals unexpectedly large unresolved surface-repair issues, revisit the boundary before ExECT implementation. Otherwise, ExECT establishes whether the broader audited field-family path is viable.

### What counts as an acceptable semantic Gan repair?

- Decision: Deterministic Gan repair may only normalize output surfaces that preserve model meaning. Any evidence-dependent or meaning-changing repair must be implemented as a separate verifier/repair program variant and reported with repair rate, abstention rate, extraction-only metrics, and post-repair metrics.
- Outcome: Resolved. Surface normalization and semantic repair remain separate experiment surfaces.
- Dependencies: Decide next Gan repair boundary; Add targeted Gan failure regression fixtures.
- Parallelizable: no, because it affects scorer and repair interpretation.
- Owner: User; Codex.
- Validation: Fixtures and reports separate repair rates from extraction-only metrics.
- Notes: Acceptable deterministic repairs include quote stripping, sentinel normalization, and canonical unit/range formatting. Semantic repairs such as unknown/no-reference conversion, filling missing cluster counts, choosing a temporal window, or turning an abstention into a label require an explicit verifier/repair stage.

### How broad should the first ExECT baseline be?

- Decision: The first ExECT baseline is a combined audited S0/S1 field-family task covering diagnosis, seizure type, and annotated medications only.
- Outcome: Resolved. The baseline should test realistic audited schema breadth while reporting per-family metrics and overall micro-average.
- Dependencies: Draft ExECT S0/S1 baseline design.
- Parallelizable: no, because it defines the ExECT baseline contract.
- Owner: User; Codex.
- Validation: ExECT baseline design and run report state the chosen field scope.
- Notes: Do not include seizure frequency, investigations, history, birth history, aetiology, onset, diagnosis-date, or medication temporality as benchmark-facing metrics in the first baseline. Report diagnosis, seizure-type, annotated-medication, schema-validity, evidence-support, and label-policy failure diagnostics separately.

## Experiments

### Gan post-repair validation

- Outcome: A refreshed Gan S0 run or replay quantifies the impact of current surface repairs against the full validation split.
- Dependencies: Inspect post-repair Gan S0 validation behavior.
- Parallelizable: yes.
- Owner: unassigned.
- Validation: Report includes before/after metrics and bounded examples for changed predictions.
- Notes: This should be the next Gan measurement before adding heavier verifier/repair modules.

### Gan extract-verify-repair ablation

- Outcome: Comparison of extraction-only versus evidence-aware verifier/repair and abstention variants.
- Dependencies: Gan verifier/repair module; evidence support scoring; error analysis reports.
- Parallelizable: after verifier/repair module exists.
- Owner: unassigned.
- Validation: Ablation report with normalized-label accuracy, monthly/Purist/Pragmatic accuracy, evidence support, repair rate, abstention rate, and coverage.
- Notes: Hypothesis: verifier improves evidence support and semantic precision, possibly at the cost of coverage.

### ExECT S0/S1 field-family baseline

- Outcome: Baseline for audited diagnosis, seizure type, and annotated medication extraction.
- Dependencies: Build ExECT S0/S1 DSPy field-family baseline.
- Parallelizable: after implementation.
- Owner: unassigned.
- Validation: Initial capped smoke complete in `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T154456Z`; label-policy v2 capped smoke complete in `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T155638Z`.
- Notes: This tests audited S0/S1 schema breadth before full ExECT-like S4 extraction. The v2 capped smoke improved medication scope and diagnosis alignment, but seizure-type granularity and evidence quote support should be addressed before full validation.

### Section-aware versus monolithic ExECT ablation

- Outcome: Comparison of monolithic note-to-schema extraction against section-aware field-group extraction.
- Dependencies: ExECT S0/S1 baseline; field-group and section-aware DSPy modules.
- Parallelizable: after ExECT baseline.
- Owner: unassigned.
- Validation: Ablation report with temporality, negation, evidence, and field-family breakdown.
- Notes: Most relevant for broad ExECT schema complexity.

### Model comparison matrix

- Outcome: Comparable reports for Qwen3.6:35b, Qwen3.5:9b, Gemini 3 Flash, GPT 5.5, and GPT 4.1-mini on fixed tasks.
- Dependencies: Stable experiment configs; model adapters; selected benchmark task.
- Parallelizable: after config and runtime readiness, subject to rate limits.
- Owner: unassigned.
- Validation: Run table with identical split, scorer, schema level, program variant, and metric caveats.
- Notes: Start with Gan S0 because it is already instrumented, then repeat on ExECT S0/S1 after that baseline stabilizes.

## Long-Term Plan

### Phase 1: Consolidate Gan S0 Into A Reliable Reference Task

- Decide whether to stop at the current extraction-only baseline or add verifier/repair.
- Quantify post-repair validation metrics on the full validation split.
- Add fixtures for the recurring failure modes so future changes do not silently change label semantics.
- If verifier/repair is added, report extraction-only and extract-verify-repair metrics side by side.
- Keep Gan as the fast, focused task for provider smoke tests, optimizer experiments, and evidence-support diagnostics.

### Phase 2: Establish The First ExECT S0/S1 Baseline

- Design a narrow, audited ExECT baseline around diagnosis, seizure type, and annotated medications.
- Carry forward current ExECT label-policy guidance: benchmark-facing label constraints grounded in the active scorer vocabulary, single-event diagnosis null policy, medication-scope exclusion, and no seizure-type inference from diagnosis alone.
- Run capped provider-backed experiments before full validation.
- Use error analysis to decide whether ExECT needs separate field-family modules, stronger section selection, or verifier/repair before moving wider.

### Phase 3: Compare Program Architectures

- Implement and compare monolithic extraction, field-group extraction, section-aware context-then-extract, and extract-verify-repair variants.
- Treat each architecture as a first-class program variant with its own config, metadata, prompt/config snapshot, and metric caveats.
- Evaluate not only accuracy, but also schema validity, evidence support, abstention behavior, repair rate, temporality failures, negation failures, and field-family-specific errors.

### Phase 4: Compare Models Under Fixed Conditions

- Run GPT 4.1-mini, GPT 5.5, Gemini 3 Flash, Qwen3.6:35b, and Qwen3.5:9b on the same split, schema level, program variant, scorer mode, and structured-output strategy where possible.
- Report provider-specific caveats such as constrained JSON support, local runtime availability, rate limits, and token/context constraints.
- Avoid cross-model claims when model runs used different scorer semantics or materially different prompts/configs.

### Phase 5: Move Toward Benchmark-Relevant ExECT Breadth

- Audit and load additional ExECT source families before making them benchmark-facing: investigation, history, birth history, aetiology, onset, and diagnosis-date fields.
- Add CUI/feature-aware scoring only after the relevant gold-label source quirks are documented and tested.
- Keep partial S0/S1 metrics clearly labeled as partial until all benchmark-aligned prerequisites exist.

### Phase 6: Revisit Published Benchmark Reproduction

- Use the benchmark reference constants and caveats as guardrails, not as proof of reproduction.
- Reproduction requires CUI/feature-aware ExECT all-family scoring and access to or reconstruction of Gan Real(300)/Real(150) evaluation sets.
- Any benchmark comparison report must state whether each metric is aligned, partial, diagnostic, or not comparable.

## Dependency Notes

- Shared contracts should stay single-threaded: scorer semantics, schema contracts, run metadata, split generation policy, and benchmark-alignment language affect every later card.
- Gan repair work and ExECT baseline design can proceed in parallel because they touch different task surfaces.
- ExECT implementation has opened the S0/S1 field-family path; the next dependency is label-policy prompt/example tightening before full validation or architecture ablations.
- Model smoke tests are unblocked for closed providers with credentials in `.env`; Qwen runs remain blocked on local Ollama availability.
- Benchmark reproduction remains a long-term dependency chain, not a near-term claim.

## Parallelization Opportunities

- Safe immediately in parallel: ExECT S0/S1 label-policy example work and closed-provider Gan S0 smoke tests.
- Safe after the next Gan decision: targeted Gan fixtures and verifier/repair design.
- Blocked on module interfaces: ablation config files and broad program-architecture comparisons; ExECT section-aware work should wait until the label-policy-aligned S0/S1 capped smoke is inspected.
- Blocked on local runtime: Qwen-backed model comparisons.
- Keep single-threaded: scorer semantics, schema contracts, run metadata changes, split policy, and benchmark-reproduction claims.

## Recommended Next Pull

1. Tighten ExECT S0/S1 seizure-type granularity for fused surfaces such as `temporal lobe onset focal seizures`, and add explicit evidence-support inspection before full validation.
2. Re-run the same capped ExECT S0/S1 GPT 4.1-mini smoke after that seizure-type/evidence follow-up.
3. Smoke-test Qwen Gan S0 on the Windows laptop when the local Ollama runtime is available.

The plan is now organized so completed work serves as background and the foreground path is: tighten the combined ExECT S0/S1 baseline after the first capped run, keep Gan as the focused smoke-test and verifier/repair testbed, then use both tasks for architecture and model comparisons.
