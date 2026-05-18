# Clinical Extraction Kanban Plan

Source: `docs/outline.md`  
Grounding note: `docs/deterministic_foundation_decisions.md`  
Local-model policy: `docs/qwen_dspy_latency_policy.md`  
Last refreshed: 2026-05-18

## Goal

Build a hybrid deterministic and DSPy-based clinical extraction research system that can specialize across the broad ExECTv2 schema and the focused Gan seizure-frequency task, while preserving dataset fidelity, reproducible splits, auditable scoring, and experiment traceability.

The project has moved beyond the deterministic foundation milestone. The current execution focus is split between using the ExECT S0/S1 validation-cap read to guide architecture work and adding a small local-Qwen latency workstream that tests DSPy component costs on the Windows laptop before making Qwen3.6:35b part of routine capped validation.

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

The first ExECT S0/S1 baseline contract is drafted in `docs/exect_s0_s1_baseline_design.md`, and capped GPT 4.1-mini smokes are inspected in `docs/exect_s0_s1_smoke_inspection.md`. The model-backed path is scoped to audited diagnosis, seizure type, and annotated medication field families under `exect_field_family_deterministic_v1`; broader clinical fields and medication temporality remain deferred. The first capped smoke validated the artifact path but showed the zero-shot prompt was too permissive about clinically plausible labels, planned/previous medication mentions, and richer seizure-type surfaces. The v2 label-policy smoke improved the same capped slice to micro F1 84.2%, diagnosis F1 100.0%, and annotated-medication F1 100.0%. The v3 seizure/evidence smoke added a narrow benchmark bridge for fused `temporal lobe onset focal seizures` surfaces and ExECT evidence diagnostics; the same capped slice reached 100.0% micro F1 with 90.0% evidence quote support, but this remains a three-record smoke, not a performance estimate.

A narrow ExECT evidence bridge now repairs literal ellipsis-style model evidence quotes when all fragments can be deterministically located in order inside one short source span. This is tagged as diagnostic bridge behavior (`evidence_repair:ellipsis_contiguous_span`) and does not change benchmark-facing field-family scorer semantics.

## Ready

### Decide bounded Qwen reasoning strategy

- Outcome: Either keep local Qwen on direct extraction only, or define a bounded reasoning variant that emits label/evidence before any rationale and can be measured separately from DSPy's unconstrained `ChainOfThought`.
- Dependencies: `docs/qwen_local_latency_experiment_20260518.md`.
- Parallelizable: yes, if scoped to prompt/program design and not scorer semantics.
- Owner: unassigned.
- Validation: Design note or config diff states whether the next Qwen experiment uses direct extraction, bounded rationale, or no reasoning at all.
- Notes: Unconstrained DSPy `ChainOfThought` was too verbose for Qwen3.5:9b on the tiny Gan S0 latency matrix, and `ChainOfThought + BootstrapFewShot` did not complete under `max_tokens=1536`.

### Add token and residency capture for local model runs

- Outcome: Local-model run artifacts record token usage when available and Qwen residency/offload notes close to run time instead of only relying on manual `ollama ps` checks.
- Dependencies: Current runtime metadata fields.
- Parallelizable: yes.
- Owner: unassigned.
- Validation: Metrics or metadata artifacts include token counts where LiteLLM exposes them and a `model_residency` value that is not `not_recorded` for local Ollama runs.
- Notes: Manual `ollama ps` after the Qwen3.6:35b run reported 74% CPU / 26% GPU residency.

## In Progress

No active implementation card is claimed in this plan.

## Review

No active review card is claimed in this plan.

## Done

Completed work is summarized in the background sections above rather than repeated as foreground cards.

### Add direct Gan S0 DSPy module variant and Qwen latency configs

- Outcome: Complete. Gan S0 now supports `gan_frequency_s0_direct_single_pass` alongside the existing `gan_frequency_s0_single_pass` ChainOfThought variant, and local-Qwen latency configs exist for Qwen3.5:9b and Qwen3.6:35b.
- Validation: `uv run --extra dev pytest tests/test_llm_adapters.py tests/test_gan_s0_program.py tests/test_experiment_configs.py`; dry runs passed for the new Qwen3.5:9b latency matrix and Qwen3.6:35b direct gate configs.
- Notes: DSPy Ollama construction now uses LiteLLM `ollama_chat/` with `think=false` because Ollama's OpenAI-compatible `/v1` route returned hidden reasoning with empty final content for Qwen tags.

### Add latency and call-count capture to run artifacts

- Outcome: Complete. Experiment `metrics.json` files now include runtime metadata: compile duration, prediction duration, prediction seconds per record, evaluation duration, total duration, estimated model-call count, optimizer settings, and model residency placeholder.
- Validation: Runtime fields are present in completed Qwen runs such as `runs/gan_s0_latency_qwen9b_direct_cap3_20260518T201228Z/metrics.json` and `runs/gan_s0_latency_qwen35b_direct_cap3_20260518T201925Z/metrics.json`.
- Notes: Token counts and automatic residency capture remain future work.

### Run Qwen local Gan S0 latency and pace experiments

- Outcome: Complete. `docs/qwen_local_latency_experiment_20260518.md` records the Qwen3.5:9b DSPy component latency matrix and the Qwen3.6:35b direct-extraction pace gate.
- Validation: Completed artifacts: `runs/gan_s0_latency_qwen9b_direct_cap3_20260518T201228Z`, `runs/gan_s0_latency_qwen9b_cot_cap3_20260518T201247Z`, `runs/gan_s0_latency_qwen9b_direct_bootstrap_cap3_20260518T201540Z`, `runs/gan_s0_smoke_qwen35b_direct_ollama_20260518T201840Z`, and `runs/gan_s0_latency_qwen35b_direct_cap3_20260518T201925Z`. The combined Qwen3.5:9b `ChainOfThought + BootstrapFewShot` attempt `runs/gan_s0_latency_qwen9b_cot_bootstrap_cap3_20260518T201609Z` failed during prediction before metrics were written.
- Notes: On Qwen3.5:9b, direct extraction completed at 3.91 prediction seconds/record, ChainOfThought completed at 53.74 seconds/record with truncation warnings, and direct plus tiny BootstrapFewShot completed with 3.92s compile time and 4.62 prediction seconds/record. ChainOfThought plus BootstrapFewShot did not function under `max_tokens=1536`. Qwen3.6:35b direct extraction completed a one-record smoke and a warm three-record cap; manual `ollama ps` showed 74% CPU / 26% GPU residency after the run.

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

### Tighten ExECT seizure-type granularity and evidence policy

- Outcome: Complete. The ExECT S0/S1 single-pass field-family baseline now handles fused seizure-type surfaces such as `temporal lobe onset focal seizures` against the current audited scorer view and reports explicit evidence quote/offset diagnostics before scaling.
- Validation: `uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py`; dry-run `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --dry-run`; capped run `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T160445Z`.
- Notes: Scorer semantics are unchanged. The fused seizure-type handling is explicitly tagged benchmark bridge behavior (`benchmark_bridge:fused_seizure_type_split`), not a scorer-policy change. On the same capped three-record slice, v3 produced micro F1 100.0%, diagnosis F1 100.0%, seizure-type F1 100.0%, annotated-medication F1 100.0%, evidence quote support 90.0%, evidence offsets present 90.0%, and evidence offsets valid 100.0%. One EA0018 medication evidence quote remained unsupported because it used an ellipsis/non-contiguous quote.

### Add ExECT ellipsis evidence quote bridge

- Outcome: Complete. The ExECT S0/S1 artifact bridge now converts literal `...` evidence quotes into a single exact contiguous source quote when all fragments are found in order within a short same-paragraph span.
- Validation: `uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py`; dry-run `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json --dry-run`.
- Notes: Benchmark-facing scorer semantics are unchanged. Repaired evidence is tagged with `evidence_repair:ellipsis_contiguous_span` so future reports can separate model-supplied exact quotes from deterministic evidence bridge repairs.

### Run larger capped ExECT S0/S1 field-family validation

- Outcome: Complete. A 25-record GPT 4.1-mini validation-cap run exists for the ExECT S0/S1 field-family baseline using the v3 label policy plus the narrow ellipsis evidence bridge, with standard run artifacts and an inspection note in `docs/exect_s0_s1_validation_cap25_inspection.md`.
- Validation: `uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py`; dry-run `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json --env-file .env --dry-run`; capped run `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260518T172431Z`.
- Notes: Scorer semantics are unchanged. On the capped 25-record validation slice, micro precision/recall/F1 reached 68.8%/79.5%/73.7%; diagnosis F1 60.5%; seizure-type F1 65.8%; annotated-medication F1 92.1%; evidence quote support 92.1% overall, 92.0% on exact model quotes, and 100.0% on ellipsis repairs. The inspection classified remaining issues as mostly label-policy or normalization errors, with a smaller architecture-shaped subset suggesting cross-family leakage.

### Design section-aware versus monolithic ExECT ablation

- Outcome: Complete. `docs/exect_section_aware_ablation_design.md` defines the first ExECT architecture ablation around the audited S0/S1 field-family contract and the existing deterministic sectioning/context-selection utilities.
- Validation: Design reviewed against `docs/exect_gold_label_audit.md`, `docs/exect_s0_s1_baseline_design.md`, `docs/exect_s0_s1_validation_cap25_inspection.md`, `src/clinical_extraction/pipeline/sectioning.py`, and `tests/test_sectioning_context.py`.
- Notes: The design keeps dataset, split, model, schema level, scorer mode, prompt policy, fused seizure-type bridge, and ellipsis evidence repair fixed. The experimental factor is architecture only: current monolithic single-pass extraction versus a section-aware per-family variant that merges outputs through the same artifact bridge.

### Implement section-aware ExECT S0/S1 field-family module variant

- Outcome: Complete. `src/clinical_extraction/programs/exect_s0_s1.py` now includes a section-aware ExECT S0/S1 program variant that uses deterministic per-family context selection for diagnosis, seizure type, and annotated medication while preserving the shared ExECT bridge and scorer contract.
- Validation: `uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py tests/test_sectioning_context.py`; dry-run `uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_section_aware_cap25_gpt4_1_mini.json --env-file .env --dry-run`; capped run `runs/exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z`; inspection note `docs/exect_section_aware_cap25_inspection.md`.
- Notes: Scorer semantics, schema level, prompt version, fused seizure-type bridge, and ellipsis evidence repair were held fixed. The first section-aware cap underperformed the monolithic cap-25 baseline: micro F1 73.7% -> 65.6%, diagnosis F1 60.5% -> 44.9%, seizure-type F1 65.8% -> 59.7%, annotated-medication F1 92.1% -> 88.9%, evidence quote support 92.1% -> 75.5%. Keep the monolithic ExECT S0/S1 baseline as the active comparison anchor.

### Resolve Gemini 3 Flash model identifier

- Outcome: Complete. `configs/models/gan_s0_gemini3_flash.json` uses the API-listed Gemini 3 Flash Preview model identifier, `gemini-3-flash-preview`.
- Validation: `uv run --extra dev pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py tests/test_experiment_configs.py`; dry-run `configs/experiments/gan_s0_smoke_gemini3_flash.json`; completed smoke artifact `runs/gan_s0_smoke_gemini3_flash_20260518T134109Z`.
- Notes: The Mac smoke attempt reached Google but failed with 404 for invalid `models/gemini-3-flash`; see `docs/model_config_smoke_tests.md`. The fixed smoke run completed but produced one invalid Gan label, so it validates provider/runtime compatibility rather than extraction quality.

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
- Dependencies: Local Ollama availability; validated Qwen model configs; stable task config; Qwen3.5:9b latency ablation results; Qwen3.6:35b direct-extraction pace gate.
- Parallelizable: after local runtime availability and latency gates are confirmed.
- Owner: unassigned.
- Validation: Run artifacts with identical split, scorer, schema level, and program variant to the closed-provider runs.
- Notes: This is partly an environment blocker and partly a policy gate. Do not include Qwen3.6:35b in routine comparison runs with `ChainOfThought` or `BootstrapFewShot` unless the run is explicitly labeled as an overnight optimizer/reasoning experiment.

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
- Dependencies: Design section-aware versus monolithic ExECT ablation; Implement section-aware ExECT S0/S1 field-family module variant.
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
- Validation: Initial capped smoke complete in `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T154456Z`; label-policy v2 capped smoke complete in `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T155638Z`; v3 seizure/evidence capped smoke complete in `runs/exect_s0_s1_smoke_gpt4_1_mini_20260518T160445Z`; ellipsis evidence bridge dry-run complete; validation-cap inspection complete in `docs/exect_s0_s1_validation_cap25_inspection.md`.
- Notes: This tests audited S0/S1 schema breadth before full ExECT-like S4 extraction. The larger validation cap showed that evidence and medication scope are no longer the main blockers; the next cycle should test whether section-aware architecture reduces cross-family leakage without changing scorer semantics.

### Section-aware versus monolithic ExECT ablation

- Outcome: Comparison of monolithic note-to-schema extraction against section-aware field-group extraction.
- Dependencies: ExECT S0/S1 field-family baseline; Design section-aware versus monolithic ExECT ablation; Implement section-aware ExECT S0/S1 field-family module variant.
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

### Qwen3.5:9b DSPy component latency ablation

- Outcome: Complete. `docs/qwen_local_latency_experiment_20260518.md` quantifies whether Qwen3.5:9b can complete direct extraction, `ChainOfThought`, direct `BootstrapFewShot`, and `ChainOfThought + BootstrapFewShot` on a three-record Gan S0 cap.
- Dependencies: Build Qwen3.5:9b Gan S0 latency ablation configs; completed Qwen3.5:9b hardware smoke.
- Parallelizable: no on the Windows laptop, because local GPU/RAM measurements should be isolated from competing model workloads.
- Owner: unassigned.
- Validation: Direct run `runs/gan_s0_latency_qwen9b_direct_cap3_20260518T201228Z`; ChainOfThought run `runs/gan_s0_latency_qwen9b_cot_cap3_20260518T201247Z`; direct BootstrapFewShot run `runs/gan_s0_latency_qwen9b_direct_bootstrap_cap3_20260518T201540Z`; failed ChainOfThought plus BootstrapFewShot attempt `runs/gan_s0_latency_qwen9b_cot_bootstrap_cap3_20260518T201609Z`.
- Notes: Direct extraction worked at 3.91 prediction seconds/record. ChainOfThought worked but was about 13.7x slower and less schema-stable. Direct plus tiny BootstrapFewShot worked with modest overhead. ChainOfThought plus BootstrapFewShot did not complete prediction under `max_tokens=1536`.

### Qwen3.6:35b direct-extraction pace experiment

- Outcome: Complete. Qwen3.6:35b completed a direct-only one-record smoke and a direct-only three-record Gan S0 cap without `ChainOfThought` or `BootstrapFewShot`.
- Dependencies: Build Qwen3.6:35b direct-extraction pace gate; completed Qwen3.6:35b hardware smoke.
- Parallelizable: no on the Windows laptop, because this specifically measures partially offloaded local-model runtime.
- Owner: unassigned.
- Validation: Smoke `runs/gan_s0_smoke_qwen35b_direct_ollama_20260518T201840Z`; cap `runs/gan_s0_latency_qwen35b_direct_cap3_20260518T201925Z`; synthesis note `docs/qwen_local_latency_experiment_20260518.md`.
- Notes: The one-record smoke took 35.83 prediction seconds/record; the warm three-record cap took 8.83 prediction seconds/record. Manual `ollama ps` after the run reported Qwen3.6:35b at 74% CPU / 26% GPU residency, so direct 35B caps are feasible but should be paced jobs, not default interactive loops.

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
- Before broad local-Qwen comparisons, complete the Qwen3.5:9b DSPy component latency ablation and the Qwen3.6:35b direct-extraction pace experiment.
- Use Qwen3.5:9b to test whether `ChainOfThought`, `BootstrapFewShot`, or their combination is locally feasible; do not transfer that policy to Qwen3.6:35b unless the 35B direct pace gate is already acceptable and the heavier run is explicitly justified.
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
- ExECT implementation has opened the S0/S1 field-family path; the larger capped validation and artifact inspection are now complete, so the next dependency is a section-aware module implementation that keeps the current scorer and bridge behavior fixed.
- Model smoke tests are unblocked for closed providers with credentials in `.env`; local Qwen runs now require Ollama's native LiteLLM `ollama_chat/` route with `think=false`, not the OpenAI-compatible `/v1` route.
- The direct Gan S0 variant and runtime metadata fields are implemented, so Qwen can now join model comparisons only under latency-gated direct-extraction configs.
- Qwen3.5:9b can run direct extraction and tiny direct BootstrapFewShot, but unconstrained ChainOfThought is very slow and `ChainOfThought + BootstrapFewShot` did not complete under `max_tokens=1536`.
- Qwen3.6:35b can run direct extraction on a tiny cap, but because it was observed at 74% CPU / 26% GPU residency, avoid reasoning and optimizer-expanded prompts except for explicitly scheduled overnight experiments.
- Max-budget follow-up corrected the Qwen policy: both local Qwen models report 262144 context, and Qwen recommends max_tokens=81920 for complex benchmarks. New max-budget configs set `max_tokens=81920`, `num_ctx=262144`, and `think=false`. Qwen3.5:9b `ChainOfThought + BootstrapFewShot` then completed but remained very slow at 388.58 prediction seconds/record with 66.7% schema validity on a 3-record cap. Qwen3.6:35b completed direct and ChainOfThought one-record full-context smokes at 35.30s and 96.29s respectively, with Ollama reporting 79% CPU / 21% GPU residency.
- Benchmark reproduction remains a long-term dependency chain, not a near-term claim.

## Parallelization Opportunities

- Safe immediately in parallel: ExECT architecture follow-up work and token/residency capture for local model artifacts, because they touch different task surfaces.
- Safe after explicit design: bounded-Qwen-reasoning prompt/module work, if still desired.
- Safe after explicit design: Gan verifier/repair and abstention-calibration work.
- Blocked on local runtime availability: any larger Qwen-backed model comparison.
- Keep single-threaded: scorer semantics, schema contracts, run metadata changes, split policy, and benchmark-reproduction claims.

## Recommended Next Pull

1. Keep local Qwen model-comparison runs on direct extraction by default.
2. Add token and automatic residency capture to local-model artifacts if Qwen timing remains a near-term research question.
3. Decide whether a bounded reasoning variant is worth designing for Qwen3.5:9b; do not reuse unconstrained DSPy `ChainOfThought` as the default.
4. Keep Qwen3.6:35b out of `ChainOfThought` and `BootstrapFewShot` loops unless the run is explicitly scheduled as an overnight stress test.
5. Keep the monolithic ExECT S0/S1 baseline as the active comparison anchor for future architecture experiments.

The plan is now organized so completed work serves as background and the foreground path is: use the validated ExECT S0/S1 baseline to test architecture under fixed scorer semantics, use Gan S0 as the focused smoke-test and local-Qwen latency testbed, then use only latency-gated local models for broader architecture and model comparisons.
