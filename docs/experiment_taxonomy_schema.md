# Experiment Taxonomy Schema

Date: 2026-05-20  
Status: Initial controlled-vocabulary reference  
Related decision: `docs/hybrid_component_taxonomy_decision_20260520.md`  
Related registry: `docs/experiment_registry.json`

## Purpose

This document defines the controlled values for the experiment registry taxonomy.
The registry is research-facing metadata, not just bookkeeping: its job is to make
hybrid deterministic and LLM design choices analyzable across Gan and ExECT
experiments.

Rows in `docs/experiment_registry.json` use one row per canonical experiment ID.
Individual run directories remain attached as artifacts.

## Experiment Config Taxonomy Block

New configs under `configs/experiments/` must include a `taxonomy` object with at
least these fields (see `ExperimentTaxonomy` in
`src/clinical_extraction/experiments/taxonomy.py`):

- `dataset`
- `schema_complexity`
- `program_architecture`
- `hybrid_balance_class` (array)
- `interleaving_positions` (array)
- `varied_factor`
- `comparison_group`
- `intended_decision`

Optional on configs: `clinical_task_family`, `stage_graph_id`, `stage_executor`,
`implementation_variant` (Axis 3 presentation / tooling IDs).

Legacy configs may omit inline taxonomy when they already have a row in
`docs/experiment_registry.json`. Early stubs may set `taxonomy_exemption` to
`exploratory_stub`. `pytest tests/test_experiment_configs.py` enforces coverage.

Promotion, freeze, hold, and reject decision documents should include a
**Taxonomy** section with dataset, schema complexity, clinical task family,
hybrid balance class, interleaving positions, varied factor, comparison group,
outcome, and **`decision_scope`** (`operational` | `arm` | `mechanism`).

Registry rows may store `decision_scope` in `notes` until a dedicated field is added.
See `docs/hybrid_pipeline_research_pivot_20260521.md`.

## General Rules

- Use JSON arrays for fields that can contain multiple values, such as
  `hybrid_balance_class`, `deterministic_roles`, `llm_roles`,
  `interleaving_positions`, `knowledge_sources`, `control_modes`, and
  `schema_integrity_strategy`.
- Use `pending_backfill` only when a retrospective row cannot be classified from
  existing artifacts without code or document review.
- Do not use `pending_backfill` for new experiment configs unless the row is an
  explicitly marked exploratory stub.
- Prefer benchmark-facing labels when the row exists to compare against Gan or
  ExECT deterministic scorers.
- Preserve clinical nuance in notes or caveats when benchmark-facing labels hide
  clinically richer distinctions.
- Do not compare rows across different scorers, splits, schema scopes, or
  prompt families unless `comparison_group` and `metric_caveats` explicitly say
  why the comparison is valid.

## Required Core Fields

### `dataset`

Allowed values:

- `gan_2026`
- `exect_v2`

### `schema_complexity`

Allowed values:

- `gan_s0`
- `exect_s1`
- `exect_s2`
- `exect_s3`
- `exect_s4`
- `pending_backfill`

Notes:

- ExECT S0/S1 field-family runs are represented as `exect_s1` because the
  benchmark-facing row covers diagnosis, seizure type, and medication.
- Schema complexity is not the same as program architecture. For example,
  ExECT S4 can still use a single-pass architecture.

### `clinical_task_family`

Allowed values:

- `frequency`
- `diagnosis`
- `seizure_type`
- `medication`
- `investigation`
- `comorbidity`
- `birth_development`
- `family_history`
- `social_history`
- `driving`
- `pregnancy`
- `multi_family`
- `pending_backfill`

Use `multi_family` when the schema breadth is too wide for one family to be the
primary research target.

### `model_track`

Allowed values:

- `gpt4_1_mini`
- `gpt5_5`
- `gemini`
- `qwen35b`
- `qwen9b`
- `unknown`
- `pending_backfill`

Prefer model family tracks over exact provider implementation details. Exact
model config paths should remain in `fixed_controls.model_config_path`.

### `program_architecture`

Allowed values:

- `single_pass`
- `direct_single_pass`
- `verify_repair`
- `temporal_candidates_verify_repair`
- `temporal_event_table_verify_repair`
- `react_temporal_tools`
- `section_aware`
- `diagnosis_recall`
- `optimizer_compiled_single_pass`
- `pending_backfill`

This field names the pipeline shape, not the outcome or model.

## Hybrid Balance

### `hybrid_balance_class`

Allowed values:

- `L0_llm_only`
- `L1_llm_constrained`
- `H1_post_deterministic`
- `H2_pre_deterministic`
- `H3_interleaved_tool_hybrid`
- `H4_deterministic_first_llm_adjudicates`
- `D1_deterministic_only`
- `pending_backfill`

Definitions:

| Value | Meaning |
| --- | --- |
| `L0_llm_only` | LLM handles extraction, evidence, normalization, and schema behavior with minimal deterministic structure. |
| `L1_llm_constrained` | LLM extraction with JSON schema, allowed fields, parser constraints, or basic output validation. |
| `H1_post_deterministic` | LLM emits candidate output; deterministic code normalizes, repairs, filters, bridges, or scores afterward. |
| `H2_pre_deterministic` | Deterministic code selects context, candidates, spans, vocabularies, or hints before LLM extraction. |
| `H3_interleaved_tool_hybrid` | LLM can call deterministic tools or structured helper functions during reasoning or extraction. |
| `H4_deterministic_first_llm_adjudicates` | Deterministic code proposes candidates; LLM selects, verifies, adjudicates, or repairs. |
| `D1_deterministic_only` | No LLM component; useful for baselines, scorer checks, and feasibility bounds. |

Multiple values are allowed when an architecture genuinely combines positions,
such as Gan temporal candidates using both `H2_pre_deterministic` and
`H4_deterministic_first_llm_adjudicates`.

## Component Roles

### `deterministic_roles`

Allowed values:

- `none`
- `json_schema_constraint`
- `pydantic_validation`
- `benchmark_label_policy`
- `gold_audit_policy`
- `field_family_scoring`
- `section_context_selection`
- `temporal_candidate_generation`
- `frequency_normalization`
- `controlled_vocabulary_filter`
- `evidence_span_guard`
- `evidence_quote_repair`
- `benchmark_bridge`
- `schema_repair`
- `add_only_recall_merge`
- `optimizer_metric`
- `diagnostic_scoring`
- `pending_backfill`

Use this field to name what deterministic code does, not where it happens. The
where belongs in `interleaving_positions`.

### `llm_roles`

Allowed values:

- `none`
- `clinical_field_extraction`
- `frequency_interpretation`
- `temporal_reasoning`
- `candidate_selection`
- `benchmark_policy_application`
- `evidence_quote_generation`
- `normalization`
- `verification`
- `repair`
- `adjudication`
- `recall_pass`
- `tool_guided_reasoning`
- `optimizer_candidate_generation`
- `pending_backfill`

Use this field to describe model responsibility. If the LLM only emits JSON
under a schema, that is still usually `clinical_field_extraction` or
`frequency_interpretation`; schema enforcement belongs under deterministic roles
and control modes.

## Interleaving And Control

### `interleaving_positions`

Allowed values:

- `pre`
- `during`
- `tool_during`
- `post`
- `eval_only`
- `pending_backfill`

Definitions:

| Value | Meaning |
| --- | --- |
| `pre` | Deterministic or external information is prepared before the LLM call. |
| `during` | Information is embedded in prompt instructions, examples, schema, or context during generation. |
| `tool_during` | The LLM can call a deterministic helper or external tool during reasoning or extraction. |
| `post` | Deterministic or LLM repair, normalization, filtering, or adjudication happens after initial output. |
| `eval_only` | Knowledge affects scoring or diagnostics only, not the prediction. |

### `control_modes`

Allowed values:

- `none`
- `soft_hint`
- `hard_constraint`
- `tool_affordance`
- `posthoc_correction`
- `diagnostic_only`
- `pending_backfill`

Definitions:

| Value | Meaning |
| --- | --- |
| `none` | No explicit control beyond the prompt. |
| `soft_hint` | Model can use or ignore supplied candidates, examples, or rules. |
| `hard_constraint` | Output is constrained by schema, enum, parser, validation, or allowed fields. |
| `tool_affordance` | Model can call deterministic or external functions. |
| `posthoc_correction` | Deterministic or repair code changes, filters, maps, or rejects model output. |
| `diagnostic_only` | Deterministic code evaluates behavior but does not affect prediction. |

## Knowledge Sources

### `knowledge_sources`

Allowed values:

- `regex_rules`
- `temporal_rules`
- `controlled_vocabulary`
- `benchmark_label_policy`
- `json_schema`
- `pydantic_validation`
- `manual_examples`
- `bootstrapped_examples`
- `optimizer_feedback`
- `cui_or_ontology`
- `gold_audit_policy`
- `temporal_tooling`
- `diagnostic_metric`
- `pending_backfill`

This field should name the source of knowledge separately from responsibility
and interleaving. For example, `controlled_vocabulary` can be used as a prompt
hint, a hard output constraint, a tool, a deterministic postprocessor, or an
eval-only scorer mapping.

## Strategy Fields

### `context_strategy`

Allowed values:

- `full_note`
- `section_filtered`
- `candidate_injected`
- `retrieved_spans`
- `regression_slice`
- `pending_backfill`

### `evidence_strategy`

Allowed values:

- `absent`
- `model_quote`
- `model_quote_with_diagnostic_span_check`
- `injected_candidates`
- `verified_quote`
- `deterministic_span_check`
- `verified_quote_with_deterministic_span_check`
- `pending_backfill`

Evidence support metrics in this project are diagnostic unless a decision doc
explicitly treats them as benchmark-facing.

### `normalization_strategy`

Allowed values:

- `model_only`
- `list_constrained`
- `tool_mediated`
- `deterministic_mapping`
- `benchmark_bridge`
- `benchmark_policy_prompt`
- `scorer_only`
- `none`
- `pending_backfill`

Use `benchmark_bridge` when deterministic mapping aligns model output with
benchmark label policy after extraction. Use `benchmark_policy_prompt` when the
policy is primarily supplied during extraction.

### `verification_strategy`

Allowed values:

- `none`
- `llm_verifier`
- `deterministic_validator`
- `verify_repair`
- `adjudicator`
- `llm_recall_pass_with_deterministic_merge`
- `pending_backfill`

### `schema_integrity_strategy`

Allowed values:

- `none`
- `json_schema`
- `pydantic_validation`
- `retry_repair`
- `scorer_only`
- `pending_backfill`

## Examples And Optimizers

### `example_strategy`

Allowed values:

- `zero_shot_or_prompt_only`
- `manual_few_shot_or_policy_examples`
- `labeled_few_shot`
- `bootstrapped`
- `optimizer_or_bootstrapped`
- `gepa`
- `mipro`
- `none`
- `pending_backfill`

If a run uses a DSPy optimizer, record the optimizer name or family here and
keep exact optimizer metadata in config or artifact paths.

## Lifecycle And Comparability

### `run_scope`

Allowed values:

- `smoke`
- `cap1`
- `cap3`
- `cap5`
- `cap10`
- `cap25`
- `cap100`
- `slice`
- `full_validation`
- `test_holdout`
- `unclear`
- `pending_backfill`

### `outcome`

Allowed values:

- `promote`
- `freeze`
- `reject`
- `hold`
- `superseded`
- `exploratory`
- `pending`
- `pending_backfill`

Definitions:

| Value | Meaning |
| --- | --- |
| `promote` | Recommended current default for a task or model track. |
| `freeze` | Stable reference result or prompt family; do not keep tuning casually. |
| `reject` | Evidence argues against continuing **this arm** under current controls. Prefer `decision_scope: arm` in inspection docs. Mechanism-class closure requires a mechanism review (see `docs/hybrid_pipeline_research_pivot_20260521.md`). |
| `hold` | Useful result, but blocked by caveats, cost, incomplete validation, or unclear next action. |
| `superseded` | Historically important but replaced by a later promoted or frozen row. |
| `exploratory` | Diagnostic, capped, slice, smoke, or early probe not intended as a final comparison anchor. |
| `pending` | Planned or partly run but not decision-ready. |
| `pending_backfill` | Existing row still needs curation. |

### `comparison_group`

Comparison groups are free-form identifiers, but should follow this pattern:

```text
<dataset>_<schema>_<factor>_<model_or_track>_<split_or_scope>_v<number>
```

Examples:

- `gan_s0_architecture_gpt_validation_v1`
- `gan_s0_architecture_qwen_validation_v1`
- `exect_s1_policy_gpt_validation_v1`
- `exect_schema_complexity_gpt_validation_v1`
- `exect_qwen_replication_validation_v1`

A valid comparison group should hold fixed the dataset, split, scorer,
schema complexity or intentionally varied schema ladder, and model track unless
the `varied_factor` names the exception.

Use `comparison_group` as the primary group for simple consumers. Rows that
legitimately participate in more than one analysis may also include an optional
`comparison_groups` array. For example, an ExECT GPT S2 full-validation row can
belong to both the GPT schema-ladder group and the Qwen replication baseline
group.

### `varied_factor`

Allowed values:

- `program_architecture`
- `hybrid_balance_class`
- `interleaving_position`
- `knowledge_source_position`
- `model_track`
- `schema_complexity`
- `prompt_policy`
- `optimizer_strategy`
- `ladder_rung`
- `validation_ladder_rung` — Gan S0 post-adjudicate validation layer (schema/surface, det plausibility, evidence grounding, LLM VR, guards, span-check); see `docs/gan_s0_validation_ladder_gpt_cap25_v1_preregistration_20260521.md`
- `run_scope`
- `normalization_strategy`
- `verification_strategy`
- `evidence_strategy`
- `control_mode`
- `pipeline_stage_graph`
- `stage_executor`
- `implementation_variant`
- `context_selection_policy`
- `multi_factor`
- `pending_backfill`

Use `multi_factor` when historical rows changed more than one important factor.
Do not force a clean single-factor interpretation onto retrospective experiments.

## Validation

Run the lightweight validator from the repository root:

```powershell
uv run python scripts/validate_experiment_taxonomy.py --errors-only
```

`pytest tests/test_experiment_registry_validation.py` also enforces the same
rules on the live registry and config set.

The validator checks:

- every config has inline `taxonomy`, `taxonomy_exemption`, or a registry row
- every registry row has a valid `experiment_id`
- controlled fields contain only values listed in this document
- array-valued fields are arrays, even when they contain one value
- every `canonical_run_id` points to an existing run directory, or the row
  documents why the artifact is absent
- promoted, frozen, rejected, and superseded rows have a non-placeholder
  `decision_doc` that exists on disk
- comparison groups do not mix incompatible scorers, splits, schema scopes, or
  model tracks unless `varied_factor`, `comparison_caveat`, or documented
  metric caveats explain the exception

## Current Known Caveats

- The initial registry was generated from local run metadata and contains
  conservative retrospective tags.
- Some historical rows changed several factors at once, especially prompt
  policy, guardrails, and architecture.
- ExECT schema-complexity comparisons aggregate different field families at
  each level; micro F1 is not a clean learning curve by itself.
- Gan frequency labels depend on audited benchmark policy, especially the
  distinction between `unknown`, no current reference, historical-only
  statements, and current seizure-free status.
- Post-hoc benchmark bridges may improve measured benchmark performance without
  proving broader clinical validity.
