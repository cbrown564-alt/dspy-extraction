# Clinical Extraction Kanban Plan

Source: `docs/outline.md`  
Grounding note: `docs/deterministic_foundation_decisions.md`  
Date: 2026-05-17

## Goal

Build a hybrid deterministic and DSPy-based clinical extraction research system that can specialize across the broad ExECTv2 schema and the focused Gan seizure-frequency task, while preserving dataset fidelity, reproducible splits, auditable scoring, and experiment traceability.

The first execution milestone remains deterministic only: loaders, gold-label representation, normalization, splitting, and scoring must be testable before adding DSPy programs or model calls.

## Definitions Of Done

- ExECTv2 and Gan gold labels load from the agreed primary sources without silently changing scorer semantics.
- Raw values, normalized values, quality flags, and scoring views remain separable.
- Gan has reproducible train/dev/test splits with documented salt and stratification metadata.
- Deterministic scorers expose benchmark-facing metrics and diagnostic metrics separately.
- DSPy programs are introduced only after loader, schema, split, and scorer contracts are covered by regression tests.
- Every experiment records dataset, split, model, schema level, program variant, scorer mode, artifacts, and metric caveats.

## Done

### Scaffold minimal Python package

- Outcome: `clinical_extraction` package, `pyproject.toml`, pytest configuration, and package path setup exist.
- Dependencies: none.
- Parallelizable: no.
- Owner: Codex.
- Validation: `pytest` can discover tests under `tests/`.
- Notes: Project name is `clinical-extraction`; package name is `clinical_extraction`.

### Load ExECTv2 primary gold documents

- Outcome: Loader reads ExECTv2 JSON annotations and paired `.txt` source letters.
- Dependencies: Scaffold minimal Python package.
- Parallelizable: after Scaffold minimal Python package.
- Owner: Codex.
- Validation: `tests/test_exect_loader.py`.
- Notes: ExECTv2 JSON remains the primary structured gold source; ExECT seizure-frequency CSV is deferred.

### Expose canonical ExECT diagnosis scoring view

- Outcome: Raw ExECT diagnoses are preserved while generic parent diagnoses collapse when a more specific diagnosis is present.
- Dependencies: Load ExECTv2 primary gold documents.
- Parallelizable: no.
- Owner: Codex.
- Validation: `tests/test_exect_loader.py`.
- Notes: Quality flags include `missing_gold`, `gold_noise`, and `specificity_collapsed`.

### Load Gan primary gold labels

- Outcome: Gan records load `check__Seizure Frequency Number.seizure_frequency_number[0]` as gold and `reference[0]` as metadata.
- Dependencies: Scaffold minimal Python package.
- Parallelizable: after Scaffold minimal Python package.
- Owner: Codex.
- Validation: `tests/test_gan_loader_and_splits.py`.
- Notes: Reference is a cross-check and difficulty signal, not benchmark gold.

### Normalize Gan labels and convert to seizures per month

- Outcome: Gan label normalization covers plural units, year/month equivalence, clusters, special labels, and category semantics.
- Dependencies: Load Gan primary gold labels.
- Parallelizable: after Load Gan primary gold labels.
- Owner: Codex.
- Validation: `tests/test_gan_frequency.py`.
- Notes: `unknown` and `no seizure frequency reference` remain distinct.

### Score Gan frequency predictions

- Outcome: Scorer separates raw string exact match, normalized-label exact match, monthly-frequency comparison, Purist category, and Pragmatic category.
- Dependencies: Normalize Gan labels and convert to seizures per month.
- Parallelizable: after Normalize Gan labels and convert to seizures per month.
- Owner: Codex.
- Validation: `tests/test_gan_scoring.py`.
- Notes: Raw exact match is diagnostic only.

### Generate deterministic Gan splits

- Outcome: `data/splits/gan_2026_splits.json` exists with deterministic assignments and counts.
- Dependencies: Load Gan primary gold labels.
- Parallelizable: after Load Gan primary gold labels.
- Owner: Codex.
- Validation: `tests/test_gan_loader_and_splits.py`.
- Notes: Confirm salt and stratification metadata are explicit before treating this as final benchmark infrastructure.

### Verify deterministic foundation as a milestone

- Outcome: All current deterministic foundation tests pass from a clean checkout-compatible environment.
- Dependencies: Done cards above.
- Parallelizable: no.
- Owner: Codex.
- Validation: `uv run --extra dev pytest` passes with 10 tests.
- Notes: Current foundation files are visible in `git status --short --untracked-files=all`; they should be intentionally added together before committing.

### Review Gan split metadata against audit guidance

- Outcome: Split file documents salt, counts, and any stratification or hard-case balancing metadata needed for reproducibility.
- Dependencies: Generate deterministic Gan splits.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_gan_loader_and_splits.py`.
- Notes: Split metadata now records salt, split ratios, allocation policy, stratification fields, stratum counts, label counts, and hard-case counts.

### Add dataset manifest validation

- Outcome: Manifest validation confirms expected raw files, derived splits, and core counts for ExECTv2 and Gan.
- Dependencies: Load ExECTv2 primary gold documents; Load Gan primary gold labels; Generate deterministic Gan splits.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_dataset_manifest.py`.
- Notes: `clinical_extraction.datasets.manifest` validates raw paths, derived split files, core counts, split coverage, duplicate assignments, and split count metadata.

### Add ExECT medication and seizure-type regression cases

- Outcome: Regression tests cover certainty thresholding, seizure-type extraction from `Diagnosis` rows, medication synonym normalization, and known noisy gold terms.
- Dependencies: Load ExECTv2 primary gold documents; Expose canonical ExECT diagnosis scoring view.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_exect_loader.py`.
- Notes: Planned/current medication scoring remains out of scope; tests lock the current JSON-source loader semantics.

### Document deterministic scorer semantics

- Outcome: A concise methods note states ExECT and Gan gold sources, normalization rules, flags, and which metrics are benchmark-facing versus diagnostic.
- Dependencies: Score Gan frequency predictions; Expose canonical ExECT diagnosis scoring view.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `docs/deterministic_scorer_semantics.md` reviewed against audit and foundation notes.
- Notes: This prevents future experiment reports from mixing incompatible scorer meanings.

### Define shared prediction and evidence schemas

- Outcome: Pydantic models represent extracted values, normalized values, evidence spans, temporality, negation, confidence, and quality flags.
- Dependencies: Document deterministic scorer semantics.
- Parallelizable: after Document deterministic scorer semantics.
- Owner: Codex.
- Validation: `tests/test_prediction_schemas.py`.
- Notes: `EvidenceSpan`, `ExtractedValue`, `DocumentPrediction`, and `PredictionSet` now cover normalized values, evidence, temporality, negation, confidence, metadata, and quality flags. Schema level remains free run metadata so S0-S4 and task-specific variants are experiment parameters.

### Create baseline deterministic evaluation CLI

- Outcome: A script evaluates stored predictions against deterministic scorers and writes metrics plus error samples.
- Dependencies: Document deterministic scorer semantics; Define shared prediction and evidence schemas.
- Parallelizable: after Define shared prediction and evidence schemas.
- Owner: Codex.
- Validation: `tests/test_evaluation_cli.py`.
- Notes: `scripts/evaluate_predictions.py` delegates to `clinical_extraction.evaluation.cli`; current deterministic support covers Gan seizure-frequency predictions and separates benchmark-facing metrics from diagnostic metrics.

### Create run artifact layout and metadata contract

- Outcome: Runs record dataset, split, model/provider, schema level, program variant, scorer mode, prompts/configs, predictions, metrics, and errors.
- Dependencies: Create baseline deterministic evaluation CLI.
- Parallelizable: after Create baseline deterministic evaluation CLI.
- Owner: Codex.
- Validation: `tests/test_run_artifacts.py`.
- Notes: `clinical_extraction.runs` defines required run metadata and creates the standard run directory with metadata, config, prompts, predictions, metrics, errors, and artifact paths. Model/provider fields remain plain metadata until adapters are introduced.

### Add evidence support scoring

- Outcome: Evidence span overlap/support metrics are available for Gan and reusable for ExECT predictions.
- Dependencies: Shared prediction and evidence schemas; baseline evaluation CLI.
- Parallelizable: after Create baseline deterministic evaluation CLI.
- Owner: Codex.
- Validation: `tests/test_evidence_scoring.py`; `tests/test_evaluation_cli.py`.
- Notes: `clinical_extraction.evaluation.evidence` scores quote support, offset validity, gold evidence locatability, overlap ratio, and IoU. Gan evaluation reports evidence diagnostics separately from benchmark-facing frequency metrics.

### Add error analysis reports

- Outcome: Evaluation writes failure taxonomies for negation, temporality, normalization, evidence, schema validity, abstention, and repair.
- Dependencies: Baseline evaluation CLI; evidence scoring.
- Parallelizable: after Add evidence support scoring.
- Owner: Codex.
- Validation: `tests/test_evaluation_cli.py`.
- Notes: Gan evaluation now emits `error_analysis` with bounded examples and category counts for schema coverage, normalization, category mismatches, evidence support, negation, temporality, abstention, and repair metadata.

### Gan deterministic-normalization baseline

- Outcome: Baseline report showing how deterministic normalization and category scoring behave on Gan gold labels and simple prediction fixtures.
- Dependencies: Score Gan frequency predictions; baseline evaluation CLI.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_gan_baseline_report.py`; `docs/gan_deterministic_normalization_baseline.json`.
- Notes: Report fixtures compare gold-copy, pluralized surface variants, and Pragmatic bucket proxy predictions. The report preserves the distinction between raw exact diagnostics, normalized labels, monthly-frequency benchmark semantics, and Pragmatic/Purist category scoring.

### Choose schema level sequence for first DSPy runs

- Outcome: Decision recorded for whether first experiments run Gan-only, ExECT S0, ExECT S1, or a paired Gan plus ExECT S0 comparison.
- Dependencies: Shared prediction and evidence schemas.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_experiment_design_docs.py`; `docs/first_dspy_schema_sequence.md`.
- Notes: Decision is Gan frequency first, then ExECT S0/S1. The broad DSPy module card has been split by adding a narrow Gan S0 program-contract card before provider adapters or broad module work.

### Implement sectioning and context selection

- Outcome: Deterministic note segmentation and section-aware context selection feed field-specific extractors.
- Dependencies: Shared prediction and evidence schemas.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_sectioning_context.py`.
- Notes: `clinical_extraction.pipeline.sectioning` provides offset-preserving section spans and field-keyword context selection that returns reusable `EvidenceSpan` objects.

### Build bootstrap confidence interval reporting

- Outcome: Evaluation reports include uncertainty intervals for key metrics across splits and program variants.
- Dependencies: Baseline evaluation CLI; experiment run artifacts.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_bootstrap_confidence.py`; `tests/test_evaluation_cli.py`.
- Notes: `clinical_extraction.evaluation.bootstrap` provides seeded percentile bootstrap mean intervals. Gan evaluation now reports confidence intervals for benchmark-facing frequency metrics and diagnostic validity/evidence metrics without changing scorer semantics.

### Create review annotation export

- Outcome: Low-confidence or conflicting extractions can be reviewed through a simple tool-agnostic export.
- Dependencies: Error analysis reports; evidence schemas.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_review_export.py`.
- Notes: `clinical_extraction.review.export` flattens bounded evaluation error-analysis examples into deterministic JSONL review queue items. `scripts/export_review_queue.py` exports any evaluation report into a tool-agnostic review queue. The moved `exect-explorer/` React app is a future UI foundation, not a near-term dependency.

### Choose ExECT planned/current medication policy

- Outcome: Decision recorded that planned/current medication status is excluded from benchmark-facing ExECT medication metrics for now.
- Dependencies: ExECT audit review.
- Parallelizable: yes.
- Owner: User; Codex.
- Validation: Decision reflected in this plan and should be linked from scorer documentation when ExECT field-family scorers are implemented.
- Notes: The ExECT audit shows the original prescription markup has no temporality column and tags planned/tapering medications alongside current medications. Benchmark-facing medication scoring should treat the loaded medication view as annotated medications, with planned/current status reserved for diagnostic or challenge-set analysis until corrected gold exists.

### Choose first Gan DSPy implementation boundary

- Outcome: Decision recorded to implement a narrow Gan S0 DSPy program contract with mocked execution before real provider adapters.
- Dependencies: Choose schema level sequence for first DSPy runs; run artifact layout and metadata contract.
- Parallelizable: yes.
- Owner: User; Codex.
- Validation: Future `Implement Gan S0 DSPy program contract` card should include mocked-LM tests and run-artifact checks.
- Notes: This breaks the dependency loop between first DSPy modules and LLM provider adapters. Provider adapters should target the narrow contract after it exists.

### Choose initial ExECT S0/S1 scorer scope

- Outcome: Decision recorded that benchmark-facing ExECT S0/S1 scoring is limited to audited diagnosis, seizure type, and annotated medication fields.
- Dependencies: ExECT audit review; shared prediction and evidence schemas.
- Parallelizable: yes.
- Owner: User; Codex.
- Validation: Future ExECT scorer tests should use audited examples only.
- Notes: Investigation, history, birth history, aetiology, onset, and diagnosis-date scoring require separate audit-and-loader cards before they become benchmark-facing metrics. Evidence diagnostics can remain generic and reusable.

### Implement ExECT field-family scorers

- Outcome: Diagnosis, seizure-type, and annotated-medication scorer modules expose field-level and document-level metrics for the audited ExECT S0/S1 core.
- Dependencies: ExECT regression cases; shared prediction and evidence schemas.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_exect_scoring.py`; `tests/test_exect_loader.py`; `tests/test_prediction_schemas.py`.
- Notes: `clinical_extraction.evaluation.exect` implements `exect_field_family_deterministic_v1` with field-level and micro metrics for diagnosis, seizure type, and annotated medication. Benchmark-facing medication scoring excludes planned/current status for now because the ExECT prescription gold lacks reliable temporality. Investigation and history scorers are deferred until their source files are audited and loaded.

### Implement Gan S0 DSPy program contract

- Outcome: A narrow Gan frequency extraction signature/module contract maps mocked LM outputs into `PredictionSet` artifacts with prompt/config metadata.
- Dependencies: Choose first Gan DSPy implementation boundary; shared prediction and evidence schemas; baseline evaluation CLI; run artifact layout and metadata contract.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_gan_s0_program.py`; `tests/test_gan_scoring.py`; `tests/test_evaluation_cli.py`; `tests/test_run_artifacts.py`.
- Notes: `clinical_extraction.programs.gan_frequency_s0` defines the mocked-execution contract for `gan_frequency_s0_single_pass`: one frequency label plus evidence, prompt/config metadata, abstention flags, and run metadata. No real provider adapters or broad DSPy module surface were added.

### Extract published benchmark metrics and definitions

- Outcome: A cited methods note records ExECTv2 and Gan published benchmark values, metric definitions, and whether current repo metrics are aligned, partial, or not comparable.
- Dependencies: Deterministic scorer semantics; access to benchmark definitions in `data/` papers.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_published_benchmark_metrics_doc.py`.
- Notes: `docs/published_benchmark_metrics.md` records ExECTv2 Table 1 values, Gan micro-F1 headline/Table 6-8 values, metric definitions, and explicit alignment caveats. Code-level constants were added later with explicit non-reproduction caveats.

### Add LLM provider adapters

- Outcome: Configurable adapters support local Ollama Qwen models and closed providers without changing extraction code.
- Dependencies: Run artifact layout and metadata contract; Implement Gan S0 DSPy program contract.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_llm_adapters.py`; opt-in `scripts/smoke_gan_s0_adapter.py`.
- Notes: `clinical_extraction.llms` provides a deterministic mock adapter and an OpenAI-compatible chat-completions adapter used by Ollama, OpenAI, Gemini, and custom OpenAI-compatible endpoints. The Gan S0 program now exposes `build_gan_frequency_s0_extractor(adapter)` so provider calls map into the existing `PredictionSet` contract. Model config examples live under `configs/models/`.

### Add benchmark reference constants and comparison caveats

- Outcome: Repo contains benchmark reference values extracted from the papers and a comparison helper or fixture that labels current metrics as aligned, partial, or not comparable.
- Dependencies: Extract published benchmark metrics and definitions.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_benchmark_references.py`; `tests/test_published_benchmark_metrics_doc.py`.
- Notes: `clinical_extraction.evaluation.benchmarks` records selected ExECTv2 Table 1 and Gan Table 6/Table 8 reference values with alignment labels and caveats. `benchmark_alignment()` marks current ExECT field-family scoring as partial and current Gan synthetic-subset comparisons as partial rather than published real-letter reproduction.

### Decide constrained JSON decoding strategy

- Outcome: Decision recorded for provider-specific JSON-schema or structured-output support.
- Dependencies: LLM provider adapters.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_experiment_configs.py`; `docs/constrained_json_decoding_strategy.md`.
- Notes: Use provider JSON-schema response formatting when available, but always treat Pydantic validation against the active program output model as the source of truth. Providers without JSON-schema support use the strict JSON prompt fallback and must record that strategy in run metadata.

### Add narrow Gan S0 experiment config

- Outcome: A validated experiment config captures the first provider-backed Gan S0 baseline controls before opt-in model runs.
- Dependencies: Implement Gan S0 DSPy program contract; Add LLM provider adapters; run metadata contract.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_experiment_configs.py`; `configs/experiments/gan_s0_baseline_gpt4_1_mini.json`.
- Notes: `clinical_extraction.experiments.config` validates dataset, split, model config path, schema level, program variant, scorer mode, prompt controls, structured-output strategy, metric caveats, and an explicit test-set reporting guard. The initial config targets GPT 4.1-mini on the fixed Gan validation split with `max_records=25`.

### Add model comparison configs

- Outcome: Configs cover Qwen3.6:35b, Qwen3.5:9b, Gemini 3 Flash, GPT 5.5, and GPT 4.1-mini.
- Dependencies: LLM provider adapters; run metadata contract.
- Parallelizable: after Add LLM provider adapters.
- Owner: Codex.
- Validation: `tests/test_model_comparison_configs.py`.
- Notes: All five model configs in `configs/models/` validate as `LLMProviderConfig` and resolve to `OpenAICompatibleChatAdapter` with the expected provider, model, and base URL.

### Add run experiment script

- Outcome: `scripts/run_experiment.py` integrates experiment config, split loading, DSPy LM, program execution, run artifact layout, and evaluation into a single command.
- Dependencies: Experiment config; `build_dspy_lm`; run artifact layout; baseline evaluation CLI.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `--dry-run` validates config and record loading without model calls; full run produces run artifact with metadata, config, prompts, predictions, metrics, and errors.
- Notes: Accepts `--env-file .env` for loading API keys. Run ID is auto-generated as `{experiment_id}_{timestamp}`. DSPy adapter handles JSON schema and prompt construction; no manual system prompts or response schemas.

### Build Gan S0 DSPy extraction module

- Outcome: `clinical_extraction.programs.gan_frequency_s0` provides `GanFrequencyS0Signature`, `GanFrequencyS0Module` (ChainOfThought), `gan_frequency_s0_metric`, `make_gan_dspy_examples`, `predict_gan_records`, and `gan_frequency_s0_run_metadata`.
- Dependencies: DSPy library; shared prediction schemas; run artifact layout.
- Parallelizable: yes.
- Owner: Codex.
- Validation: `tests/test_gan_s0_program.py`; dry-run and live baseline runs in `runs/`.
- Notes: Replaced the custom `ChatAdapter`-based contract with proper `dspy.Signature` + `dspy.ChainOfThought`. `build_dspy_lm(config)` in `llms.py` translates `LLMProviderConfig` to `dspy.LM` via LiteLLM. DummyLM tests use response dicts with `reasoning` key (required by ChainOfThought). Abstain sentinel normalization handles `"None"` / `"null"` strings returned by DummyLM for null Optional fields.

### Synthesize prior prompt and error-analysis guidance

- Outcome: Prior hand-crafted prompt lessons and previous ExECT/Gan error analyses are converted into concrete optimization guidance before the full validation run.
- Dependencies: Gan first LLM extraction baseline; first BootstrapFewShot run; `docs/previously_effective_prompts.md`; `docs/previous_exect_error_analysis.md`; `docs/previous_gan_frequency_error_analysis.md`.
- Parallelizable: no, because it changes the next optimization target and validation-readiness decision.
- Owner: Codex.
- Validation: `docs/prior_prompt_error_analysis_synthesis.md` records the synthesis and this board keeps full validation after synthesis-backed optimization.
- Notes: Reuse the old prompt strengths as optimization priors rather than reverting to manual prompting: explicit Gan canonical-frequency rules, 6-month seizure-free threshold examples, year-to-date denominator handling, cluster formatting, and evidence-quote support; for ExECT, carry forward coarse benchmark label mapping, symptomatic-to-focal diagnosis normalization, single-event diagnosis null policy, and "do not infer seizure type from diagnosis" examples. The synthesis implies the next Gan optimization pass should target unit/window errors and evidence support before spending a full validation run, while the later ExECT baseline should start with benchmark-facing label constraints rather than broad clinical label freedom.

### Implement synthesis-backed Gan S0 optimization

- Outcome: Gan S0 optimization uses compact synthesis-backed guidance, exact-label-plus-evidence optimizer scoring, locatable-evidence demos, compiled-state artifacts, and a capped validation check before full validation.
- Dependencies: Synthesize prior prompt and error-analysis guidance; Gan first LLM extraction baseline; run artifact layout and metadata contract.
- Parallelizable: no, because it changes the optimizer target and validation gate for the next Gan run.
- Owner: Codex.
- Validation: `tests/test_gan_s0_program.py`; `tests/test_experiment_configs.py`; `uv run --extra dev pytest`; capped run `runs/gan_s0_synthesis_bootstrap_gpt4_1_mini_20260518T062451Z`.
- Notes: Best capped run preserved 96% schema validity while improving normalized-label accuracy to 37.5%, monthly and Purist accuracy to 54.2%, Pragmatic category accuracy to 79.2%, and evidence quote support to 87.0%. The remaining invalid is an incomplete cluster label missing the per-cluster component. This is now ready for a full validation run with the same config after removing the `max_records` cap.

## Review

No active review card is claimed in this plan.

## Ready

No active ready card is claimed in this plan.

## In Progress

No active implementation card is claimed in this plan.

## Blocked

### Reproduce published ExECTv2 and Gan benchmark numbers

- Outcome: Repo can run benchmark-aligned reproduction or comparison against the published ExECTv2 and Gan values.
- Dependencies: Add benchmark reference constants and comparison caveats; CUI/feature-aware ExECT all-family scorer; access to or reconstruction of Gan Real(300)/Real(150) evaluation sets.
- Parallelizable: after benchmark references and missing scorer/data prerequisites.
- Owner: unassigned.
- Validation: Benchmark-aligned comparison tests and a report that states exact metric alignment.
- Notes: Current repo metrics are partial/diagnostic for published-benchmark purposes. Do not claim reproduction from the current synthetic Gan subset or ExECT S0/S1 field-family scorer.

### Build DSPy extraction modules

- Outcome: DSPy signatures/modules exist for context selection, field-group extraction, evidence verification, repair, and abstention.
- Dependencies: Narrow Gan S0 DSPy module; first LLM baseline lessons; BootstrapFewShot optimization pass.
- Parallelizable: after Gan S0 DSPy module and optimization.
- Owner: unassigned.
- Validation: Unit tests with mocked LM outputs plus one small real-model smoke run.
- Notes: Narrow Gan S0 module is now unblocked and implemented. First DSPy zero-shot baseline (ChainOfThought, no optimization) showed 32% schema validity on 25 validation records; 87.5% pragmatic category accuracy on valid predictions. Lesson: BootstrapFewShot with training split examples is required to teach the model the Gan label vocabulary format before running on larger splits. Broad verifier, repair, abstention, and field-group surfaces remain blocked until optimization is validated.

## Backlog

### Add experiment config files

- Outcome: Configs define monolithic, field-group, section-aware, context-then-extract, extract-verify-repair, and ablation variants.
- Dependencies: DSPy extraction modules; run metadata contract.
- Parallelizable: after Build DSPy extraction modules.
- Owner: unassigned.
- Validation: Config schema validation.
- Notes: Treat program variants as first-class experiments, not prompt-only changes.

## Questions

## Experiments

### Gan first LLM extraction baseline

- Outcome: Single-pass Gan frequency extraction baseline with evidence capture on the fixed Gan split.
- Dependencies: Implement Gan S0 DSPy program contract; LLM provider adapters; run metadata contract.
- Parallelizable: after Implement Gan S0 DSPy program contract and Add LLM provider adapters.
- Owner: Codex (completed).
- Validation: Run artifacts in `runs/`.
- Notes: Two DSPy ChainOfThought zero-shot baseline runs with GPT 4.1-mini on 25 validation records.
  - v1 zero-shot without optimization: 32% schema validity, 87.5% pragmatic category accuracy on valid predictions, 0% evidence quote support. Lesson: BootstrapFewShot optimization with labeled training examples is required to teach the Gan label vocabulary format.
  - v2 manual vocab-guided prompt (pre-DSPy refactor, now superseded): 92% schema validity, 70% pragmatic category accuracy — demonstrates the vocabulary learning gap, but was implemented as manual prompt engineering. This approach was abandoned in favour of DSPy optimization.
  - v3 BootstrapFewShot (4 demos from 50 dev records): 96% schema validity, 58.3% pragmatic category accuracy on valid predictions, 0% evidence quote support. Schema validity target achieved. Categorical accuracy lower than zero-shot per-valid rate (87.5%) but overall pragmatic accuracy more than doubled (~28% → 58.3%) because nearly all records now produce valid labels. Normalized label accuracy 16.7% — frequency unit errors are the likely next bottleneck.
  - v4 synthesis-backed BootstrapFewShot (`runs/gan_s0_synthesis_bootstrap_gpt4_1_mini_20260518T062451Z`): 96% schema validity, 37.5% normalized-label accuracy, 54.2% monthly/Purist accuracy, 79.2% Pragmatic category accuracy, and 87.0% evidence quote support on the capped 25-record validation slice. The strict synthesis metric accepted four full traces after eight dev examples and the run artifact includes compiled state.
  - Next: run the synthesis-backed config on the full validation split for stable confidence intervals; inspect the remaining incomplete-cluster and temporal-window errors in `errors.json`.

### ExECT S0/S1 field-family baseline

- Outcome: Baseline for core diagnosis/seizure/medication fields using field-family extraction.
- Dependencies: ExECT field-family scorers; DSPy extraction modules.
- Parallelizable: after Implement ExECT field-family scorers and Build DSPy extraction modules.
- Owner: unassigned.
- Validation: Field-level and document-level report with schema-validity rate.
- Notes: This tests audited S0/S1 schema breadth before full ExECT-like S4 extraction. Benchmark-facing metrics should cover diagnosis, seizure type, and annotated medication only.

### Extract-verify-repair ablation

- Outcome: Comparison of extraction-only versus evidence verifier and repair/abstention variants.
- Dependencies: First LLM baselines; evidence support scoring; error analysis reports.
- Parallelizable: after baseline runs.
- Owner: unassigned.
- Validation: Ablation report with precision, recall, evidence support, repair rate, and abstention rate.
- Notes: Hypothesis: verifier improves precision and evidence support, possibly reducing recall.

### Section-aware versus monolithic ablation

- Outcome: Comparison of monolithic note-to-schema extraction against section-aware field-group extraction.
- Dependencies: Sectioning and context selection; ExECT S0/S1 baseline.
- Parallelizable: after ExECT S0/S1 field-family baseline.
- Owner: unassigned.
- Validation: Ablation report with temporality, negation, and field-family breakdown.
- Notes: Most relevant for broad ExECT schema complexity.

### Model comparison matrix

- Outcome: Comparable reports for Qwen3.6:35b, Qwen3.5:9b, Gemini 3 Flash, GPT 5.5, and GPT 4.1-mini on fixed tasks.
- Dependencies: Stable experiment configs; model adapters; benchmark baselines.
- Parallelizable: after Add model comparison configs.
- Owner: unassigned.
- Validation: Run table with identical split, scorer, schema level, and program variant.
- Notes: Do not compare across scorer changes unless reports say so explicitly.

## Dependency Notes

- Shared contracts should stay single-threaded: schemas, scorer semantics, run metadata, and split definitions affect every later card.
- ExECT and Gan regression tests can expand in parallel because they touch different dataset-specific behavior.
- Narrow Gan S0 provider-backed smoke runs are unblocked; broader DSPy verifier, repair, abstention, and field-group modules remain blocked until that first path has real-model lessons.
- Full-validation Gan runs should wait until prior prompt and error-analysis guidance has been synthesized into the optimization target; otherwise the run will mostly re-measure known unit/window and evidence-support failures.
- Model adapters now target the Gan S0 program contract; generalize them only when additional program variants require it.
- Benchmark reproduction has reference constants and caveats, but still depends on CUI/feature-aware ExECT scoring and Gan real-letter evaluation access.

## Parallelization Opportunities

- Safe immediately in parallel: constrained JSON decoding decision, narrow Gan S0 experiment config schema, and continued review-export polish.
- The moved `exect-explorer/` app can be inspected or rewired later, but it should not block the simple review export workflow.
- Blocked on the broad DSPy module card: experiment configs and broader verifier/repair/field-group ablations.
- Blocked on opt-in credentials or local Ollama availability: first LLM baseline.
- Blocked on stable experiment configs and first baseline lessons: comparable model matrix runs.
- Keep single-threaded: scorer semantics, schema contracts, run metadata contract, and split generation policy.

## Recommended Next Pull

1. Run `configs/experiments/gan_s0_synthesis_bootstrap_gpt4_1_mini.json` on the full validation split after removing the `max_records` cap, preserving `synthesis_exact_with_evidence` and compiled-state artifact capture.
2. Inspect full-validation `errors.json` for incomplete cluster labels, year/window denominator errors, and residual no-reference over-abstention.
3. Only after the full Gan validation read, decide whether to add a repair/verifier module or move to the ExECT S0/S1 benchmark-facing label-policy ablation.

These cards move from mocked execution into reproducible model runs while keeping scorer semantics, benchmark caveats, and provider-specific structured output behavior explicit.
