# Clinical Extraction Kanban Plan

Source: `docs/outline.md`  
Grounding note: `docs/deterministic_foundation_decisions.md`  
Last refreshed: 2026-05-18

## Goal

Build a hybrid deterministic and DSPy-based clinical extraction research system that can specialize across the broad ExECTv2 schema and the focused Gan seizure-frequency task, while preserving dataset fidelity, reproducible splits, auditable scoring, and experiment traceability.

The project has moved beyond the deterministic foundation milestone. The current execution focus is deciding how to use the Gan S0 full-validation results: narrow deterministic surface repair, model-backed verification/repair, or a pivot into the first ExECT S0/S1 baseline.

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

## Ready

### Inspect post-repair Gan S0 validation behavior

- Outcome: A short report identifies which Gan S0 errors remain after the current surface repairs and quantifies whether the repairs improved validation metrics without changing scorer semantics.
- Dependencies: `docs/gan_s0_full_validation_error_read.md`; repaired Gan S0 artifact bridge.
- Parallelizable: yes.
- Owner: unassigned.
- Validation: New or refreshed run artifact plus a note comparing pre-repair and post-repair schema validity, normalized-label accuracy, monthly/Purist/Pragmatic accuracy, and evidence support.
- Notes: Keep label scoring separate from evidence diagnostics. Do not treat semantic repair as a deterministic normalization issue unless the evidence rule is explicit and tested.

### Decide next Gan repair boundary

- Outcome: Decision recorded for whether the next Gan change is deterministic postprocessing, a DSPy verifier/repair module, abstention calibration, or no further Gan repair before ExECT.
- Dependencies: Inspect post-repair Gan S0 validation behavior.
- Parallelizable: no, because it changes the next implementation path.
- Owner: User; Codex.
- Validation: Decision captured in this plan and, if needed, a short design note linked from the relevant implementation card.
- Notes: The decision should explicitly separate repairable output-surface errors from semantic errors such as cluster-to-unknown, no-reference/unknown confusion, and temporal-window denominator mistakes.

### Add targeted Gan failure regression fixtures

- Outcome: Regression fixtures cover the recurring Gan full-validation failure classes before any new repair/verifier implementation changes behavior.
- Dependencies: Inspect post-repair Gan S0 validation behavior.
- Parallelizable: yes.
- Owner: unassigned.
- Validation: Focused tests assert current or intended behavior for incomplete cluster labels, `unknown per cluster`, frequent-to-unknown mismatches, no-reference/unknown confusion, denominator-window errors, abstentions, missing evidence, and unsupported evidence quotes.
- Notes: Use Gan audit guidance. Preserve the distinction between `unknown` and `no seizure frequency reference`.

### Draft ExECT S0/S1 baseline design

- Outcome: A short design note defines the first ExECT S0/S1 field-family DSPy baseline, including schema fields, label-policy constraints, context strategy, evidence expectations, scorer mode, and report format.
- Dependencies: ExECT field-family scorers; shared prediction/evidence schemas; prior ExECT error-analysis synthesis.
- Parallelizable: yes.
- Owner: unassigned.
- Validation: Design note reviewed against `docs/exect_gold_label_audit.md`, `docs/deterministic_scorer_semantics.md`, and `docs/prior_prompt_error_analysis_synthesis.md`.
- Notes: Benchmark-facing fields remain diagnosis, seizure type, and annotated medications only. Investigation, history, birth history, aetiology, onset, and diagnosis-date scoring require separate audit-and-loader work before becoming benchmark-facing metrics.

### Smoke-test model configs on Gan S0

- Outcome: Provider/model configs that are expected to work in the current environment have at least one small Gan S0 smoke run or a documented runtime blocker.
- Dependencies: Model credentials in `.env`; model comparison configs; run experiment script.
- Parallelizable: yes, except shared API rate limits.
- Owner: unassigned.
- Validation: Run artifacts or documented blockers for GPT 4.1-mini, GPT 5.5, Gemini 3 Flash, Qwen3.6:35b, and Qwen3.5:9b.
- Notes: Closed-provider credentials are available in `.env`. Local Ollama availability remains a separate machine/runtime check for Qwen runs.

## In Progress

No active implementation card is claimed in this plan.

## Review

No active review card is claimed in this plan.

## Done

Completed work is summarized in the background sections above rather than repeated as foreground cards.

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

### Build ExECT S0/S1 DSPy field-family baseline

- Outcome: A model-backed baseline extracts audited ExECT S0/S1 field families and writes field-level and document-level metrics.
- Dependencies: Draft ExECT S0/S1 baseline design; ExECT field-family scorers; run artifact layout; provider adapters.
- Parallelizable: after design.
- Owner: unassigned.
- Validation: Mocked-LM tests plus a capped real-model run; report includes schema validity, diagnosis metrics, seizure-type metrics, annotated-medication metrics, evidence diagnostics, and error samples.
- Notes: Start with benchmark-facing label constraints rather than broad clinical label freedom.

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
- Validation: Field-level and document-level report with schema validity, evidence diagnostics, and failure taxonomy.
- Notes: This tests audited S0/S1 schema breadth before full ExECT-like S4 extraction.

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
- Carry forward prior ExECT label-policy guidance: benchmark-facing label constraints, symptomatic-to-focal normalization, single-event diagnosis null policy, and no seizure-type inference from diagnosis alone.
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
- ExECT implementation should wait for the ExECT baseline design decision so field scope and label policy do not drift.
- Model smoke tests are unblocked for closed providers with credentials in `.env`; Qwen runs remain blocked on local Ollama availability.
- Benchmark reproduction remains a long-term dependency chain, not a near-term claim.

## Parallelization Opportunities

- Safe immediately in parallel: post-repair Gan validation inspection, ExECT S0/S1 baseline design, and closed-provider Gan S0 smoke tests.
- Safe after the next Gan decision: targeted Gan fixtures and verifier/repair design.
- Blocked on module interfaces: ablation config files and broad program-architecture comparisons.
- Blocked on local runtime: Qwen-backed model comparisons.
- Keep single-threaded: scorer semantics, schema contracts, run metadata changes, split policy, and benchmark-reproduction claims.

## Recommended Next Pull

1. Inspect post-repair Gan S0 validation behavior and produce a short before/after metrics note.
2. Draft the ExECT S0/S1 baseline design for a combined diagnosis, seizure-type, and annotated-medication task.
3. Add targeted Gan regression fixtures around the agreed repair boundary before any later verifier/repair implementation.
4. Keep Gan verifier/repair and abstention calibration as explicit follow-up ablations after the ExECT baseline path is opened.

The plan is now organized so completed work serves as background and the foreground path is: verify the Gan S0 surface-repair impact, open the combined ExECT S0/S1 baseline, then use Gan and ExECT as complementary testbeds for architecture and model comparisons.
