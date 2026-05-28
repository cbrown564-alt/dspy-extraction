# Run Metadata Audit for Validation and Repair Outcomes

Date: 2026-05-21  
Status: Gap report complete; narrow implementation follow-ups recommended  
Scope: recent ExECT and Gan run artifacts, experiment runner metadata contract, and research-reporting requirements  

## Research Question

Do current run artifacts record enough metadata to make validation outcomes, repair decisions, model/prompt settings, scorer semantics, and artifact provenance reproducible for research reporting?

## Sources Inspected

- Runner and artifact code: `src/clinical_extraction/experiments/runner.py`, `src/clinical_extraction/runs.py`, `src/clinical_extraction/schemas.py`
- Policy docs: `docs/policies/deterministic_scorer_semantics.md`, `docs/policies/dataset_splits_policy.md`
- Recent run artifacts:
  - `runs/exect_s4_frequency_slots_s2_structured_cap25_gpt4_1_mini_20260521T075559Z`
  - `runs/gan_s0_expanded_builders_vr_full_validation_gpt4_1_mini_20260521T074513Z`
  - `runs/exect_s4_mt_guard_g0_non_asm_full_gpt4_1_mini_20260521T074459Z`
- Current decision docs:
  - `docs/experiments/exect/exect_s4_frequency_structured_slots_gpt_cap25_v1_inspection_20260521.md`
  - `docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_inspection_20260521.md`
  - `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_full_validation_v1_inspection_20260521.md`

## Current Artifact Contract

Each sampled run contains the expected artifact bundle:

- `metadata.json`
- `config.json`
- `prompts.json`
- `predictions.json`
- `metrics.json`
- `errors.json`
- `artifacts/` with optimizer subpaths reserved where applicable

The strongest reproducibility source is `config.json`. It records:

- dataset and split name
- schema level and scorer mode
- model config path
- program variant and prompt version
- structured-output strategy
- controls, including repair, verifier, evidence, context, few-shot, and abstention policy
- taxonomy fields such as comparison group, varied factor, stage graph, implementation variant, and hybrid class
- cap/full scope via `max_records`, `record_ids`, and `report_on_test_split`
- metric caveats

`metadata.json` records run identity, dataset, split, model provider/name, schema level, program variant, scorer mode, artifact paths, metric caveats, and a nested metadata block with prompt/strategy details.

`prompts.json` records the signature/module/predictor, prompt version, structured-output strategy, and task-specific policy payloads such as field families and label-policy examples.

`predictions.json` records document IDs, values, evidence spans, quality flags, per-document metadata, and prediction-set metadata.

`metrics.json` records benchmark and diagnostic metrics, caveats, counts, errors, confidence intervals where implemented, and runtime details such as prediction duration, estimated model calls, token usage when exposed by the provider, and local-model residency for Ollama.

## What Is Working

1. **Run bundles are complete for recent experiments.** The sampled ExECT and Gan runs had all expected core artifact files.

2. **Experiment configs are research-grade anchors.** They preserve model config path, dataset split, scorer mode, structured-output strategy, controls, taxonomy, metric caveats, and test-reporting guardrails.

3. **Repair decisions are well preserved for Gan verify-repair.** Gan predictions include fields such as `initial_label`, `initial_evidence`, `temporal_candidate_labels`, `temporal_candidate_records`, `verifier_decision`, and `verifier_reason`.

4. **ExECT bridge variants are visible in predictions.** The S4 structured-frequency run records `structured_frequency_slots` metadata with primitive IDs such as `exect.frequency.structured_slots.v1` and `multi_label_retention_v1`.

5. **Runtime reporting is already useful.** Metrics include runtime, estimated calls, token usage when available, and Ollama residency when relevant.

6. **Published-benchmark boundaries are represented in caveats.** Current configs and reports continue to distinguish local ExECT diagnostics from ExECTv2 Table 1 / CUI reproduction and Gan synthetic validation from real-set reproduction.

## Gaps and Risks

### 1. Traceability Is Split Across Files

The project can reconstruct run context, but no single artifact currently acts as a complete manifest. For example, `prompt_version` is nested under `metadata.metadata` rather than top-level in `metadata.json`, while `model_config_path`, `controls`, `taxonomy`, and `structured_output_strategy` live in `config.json`.

Risk: future registry or manuscript extraction scripts may accidentally summarize `metadata.json` alone and miss prompt, decoding, or control details.

### 2. `metrics.json` Lacks Stable Top-Level Split and Scorer Fields

Sampled metrics include `dataset`, `schema_level`, and `scorer`, but not stable top-level `split_name` or `scorer_mode`. These values are recoverable from config/metadata but absent from the metrics file itself.

Risk: metrics tables exported directly from run directories may lose split/scorer context, especially when comparing validation, cap-25, train/optimizer, and test-holdout outputs.

### 3. Decoding Settings Are Only Indirectly Recoverable

`config.json` stores `model_config_path`, and `metadata.json` stores provider/model, but the resolved model config contents are not copied into the run bundle.

Risk: if model config files change later, old run artifacts will still point to the path but not preserve exact temperature, max-token, provider, API base, or adapter settings.

### 4. Input Record IDs Are Implicit for Cap Runs

Run predictions contain document IDs, and config records `max_records`; explicit `record_ids` may be null for split-order cap runs.

Risk: capped-run comparison is reproducible only if split ordering remains unchanged and loader ordering is stable. That has worked so far, but paper-grade cap-25 reports should not rely on implicit ordering.

### 5. ExECT Repair and Bridge Flags Are Less Uniform Than Gan Verify-Repair Metadata

Gan verify-repair exposes explicit verifier decisions and reasons. ExECT bridge variants expose primitive IDs and some quality flags, but bridge/recovery outcome counts are mostly inferred through predictions, flags, and diagnostic metrics.

Risk: bridge contribution, repair activation rate, and abstention behavior may require custom parsing per variant instead of a stable cross-run field.

### 6. Validation Failures Are Reflected in Metrics but Not Standardized as a Run-Level Block

The artifacts include schema validity and errors, but there is no standard top-level `validation_outcomes` block summarizing Pydantic acceptance, schema failures, evidence support gate pass/fail, repair counts, and abstention counts.

Risk: inspection docs may manually compute gates consistently today, but automation remains fragile.

## Recommended Implementation Cards

### Card 1 — Add a Run Manifest Artifact

Create `run_manifest.json` during experiment execution. It should denormalize the minimum paper-grade context:

- run ID and created timestamp
- experiment ID
- dataset, split file, split name, selected record IDs
- cap/full/test scope
- model provider, model name, and resolved model config content or hash
- program variant, prompt version, structured-output strategy
- scorer mode and metric caveats
- controls and taxonomy
- artifact paths
- git commit and dirty-worktree flag if easy to capture

Priority: high. This is the lowest-risk way to prevent future reporting drift.

### Card 2 — Copy Resolved Model Config Into Each Run

Write `model_config.json` or embed `resolved_model_config` in `run_manifest.json`.

Priority: high for long-lived research artifacts, especially because model config paths may be edited over time.

### Card 3 — Add Top-Level Run Context to Metrics

Add `split_name`, `scorer_mode`, `experiment_id`, `program_variant`, `prompt_version`, `model_provider`, and `model_name` to `metrics.json`.

Priority: medium. This helps downstream tables and registry backfills avoid joining multiple files.

### Card 4 — Record Selected Record IDs for Every Run

After split loading and cap slicing, write the exact ordered evaluated IDs into `metadata.json` or `run_manifest.json`.

Priority: high for cap-25 grids and residual slices.

### Card 5 — Standardize `validation_outcomes`

Add a run-level block to metrics or manifest:

- schema-valid count / invalid count
- evidence support rate and gate result
- abstention count
- repair activation count by repair type
- verifier decision counts where applicable
- bridge flag counts where applicable

Priority: medium-high. This directly supports validation/repair outcome reporting and reduces inspection-doc manual work.

## Interpretation

The project is not blocked by metadata quality. Existing artifacts are good enough for current internal interpretation because configs, predictions, metrics, and inspection docs together preserve the relevant context.

The main weakness is **denormalization**, not absence. Research-facing reporting would be safer if each run had one manifest that freezes the resolved execution contract and selected record IDs at run time. This is especially important now that the repo is comparing many Axis 1/2/3 arms where small metadata differences determine whether a result is interpretable.

## Next Pull

Implement Card 1 plus Card 4 together: add `run_manifest.json` with exact evaluated record IDs and denormalized config/model/run context. Then add tests against a dry-run or fake backend path so future runs cannot omit the manifest.
