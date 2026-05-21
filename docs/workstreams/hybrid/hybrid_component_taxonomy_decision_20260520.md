# Hybrid Component Taxonomy Decision

Date: 2026-05-20  
Status: Proposed research-operations standard  
Related inventory: `docs/taxonomy/experiment_inventory_for_taxonomy_20260520.md`  
Related synthesis: `docs/experiments/synthesis/experiments_methods_results_20260520.md`, `docs/workstreams/optimizer/dspy_optimizer_vs_manual_engineering_audit_20260520.md`, `docs/planning/kanban_plan.md`

## Research Question

How should this project classify experiments so that it can systematically answer two central research questions?

1. What is the best balance between deterministic and LLM components for clinical extraction?
2. What is the best way to interleave deterministic and LLM components across an extraction pipeline?

The taxonomy should support current project operations, but its deeper purpose is research: it should make later analysis possible without relying on memory of ad hoc prompt versions, bridge names, and run histories.

## Motivation

The project has moved quickly from basic DSPy extraction toward increasingly hybrid clinical extraction systems. The current experiment inventory counts 93 experiment configs, 191 local run directories, 162 runs with metrics, 80 distinct metric-bearing experiment IDs, 13 registered program variants, and 50+ experiment-related documents.

That volume is now too large for a narrative kanban and frozen-thread archive to carry alone. More importantly, the current naming structure obscures a major research theme that has emerged during development: performance gains often came from changing where deterministic structure entered the pipeline, not merely from changing the model or prompt.

Examples include:

- Gan temporal candidates: deterministic temporal/frequency candidate generation before LLM verification and repair.
- Gan evidence guarding: deterministic evidence cleanup after model output.
- ExECT label-policy bridges: deterministic benchmark-alignment rules applied around broad LLM extraction.
- ExECT section-aware extraction: deterministic context selection before extraction, rejected on S0/S1 cap-25.
- DSPy optimizer probes: probabilistic prompt/example search, mostly explored on Gan rather than ExECT.

These interventions were often introduced as local fixes. That was productive during rapid exploration, but it now risks hiding the scientific variable being tested. The project needs an ontology that names the allocation of responsibility between deterministic components and LLM components, and the point in the pipeline where that responsibility is exercised.

## Decision

Adopt a factorial experiment taxonomy with first-class dimensions for hybrid component responsibility and pipeline interleaving.

The taxonomy should not treat implementation labels such as `ExECT S2`, `ExECT S4`, `v4.10`, or `temporal_candidates_v1.1` as top-level research categories. These are important artifact identifiers, but the research taxonomy should describe the scientific variables they instantiate.

The core decision is to tag each experiment by:

- dataset
- schema complexity
- clinical task family
- model track
- program architecture
- deterministic roles
- LLM roles
- interleaving positions
- knowledge sources
- control modes
- evidence strategy
- normalization strategy
- verification strategy
- schema-integrity strategy
- example/optimizer strategy
- comparison group
- outcome

This makes the hybrid design question explicit. An experiment is no longer only "Gan temporal candidates" or "ExECT S4 v1.2"; it becomes a particular placement of deterministic, probabilistic, and tool-mediated responsibilities inside a pipeline.

## Rationale

### 1. Dataset and schema complexity should be separate dimensions

ExECT S2, S3, and S4 are not different research programs. They are the same dataset and benchmark family evaluated under increasing schema complexity. Treating them as separate top-level categories makes the project harder to analyze.

The taxonomy should instead use:

| Dimension | Example values |
| --- | --- |
| Dataset | `gan_2026`, `exect_v2` |
| Schema complexity | `gan_s0`, `exect_s1`, `exect_s2`, `exect_s3`, `exect_s4` |
| Clinical task family | frequency, diagnosis, seizure type, medication, investigation, comorbidity |

This supports questions such as:

- Does Qwen degrade as ExECT schema complexity increases?
- Does verification help narrow temporal extraction more than broad schema extraction?
- Are normalization interventions more valuable for medications, seizure frequency, or diagnosis labels?

### 2. Hybrid balance is now a central research variable

The project began with DSPy-mediated LLM extraction, but major gains increasingly came from hybrid design:

- deterministic loaders and scorers protect benchmark fidelity
- deterministic candidate generation helps expose temporal structure
- deterministic bridges align raw output with benchmark label policy
- deterministic evidence checks prevent unsupported quotes from inflating evidence metrics
- LLMs remain necessary for semantic interpretation, temporality, context disambiguation, and broad schema extraction

The taxonomy should therefore include a required `hybrid_balance_class` field:

| Balance class | Meaning |
| --- | --- |
| `L0_llm_only` | LLM handles extraction, evidence, normalization, and schema behavior with minimal deterministic structure |
| `L1_llm_constrained` | LLM extraction with JSON schema, allowed fields, or basic output constraints |
| `H1_post_deterministic` | LLM extracts; deterministic code normalizes, repairs, filters, or bridges afterward |
| `H2_pre_deterministic` | deterministic code selects context, candidates, spans, or vocabularies before LLM extraction |
| `H3_interleaved_tool_hybrid` | LLM can use deterministic tools or structured helper functions during the reasoning/extraction process |
| `H4_deterministic_first_llm_adjudicates` | deterministic code proposes candidates; LLM selects, verifies, or adjudicates |
| `D1_deterministic_only` | no LLM; useful for baselines, feasibility bounds, or scorer checks |

This field should be coarse. It is not a substitute for detailed strategy tags, but it gives later analysis a way to ask whether more deterministic scaffolding improved robustness, evidence support, schema validity, or local-model performance.

### 3. Interleaving position matters as much as component type

The same knowledge source can behave differently depending on where it is introduced.

Medication normalization is a useful example:

| Position | Example |
| --- | --- |
| Pre | detect candidate medication names from a controlled list and inject them into the prompt |
| During | give the LLM the controlled list and rules, then ask it to reason and normalize |
| Tool during | let the LLM call a medication normalizer or vocabulary lookup tool |
| Post | let the LLM emit raw names, then map them deterministically afterward |
| Eval-only | canonicalize only inside the scorer for metric calculation |

These are different research interventions. They may have different effects on recall, precision, evidence support, latency, portability, and benchmark overfitting. The taxonomy should make them impossible to collapse into a vague label such as "normalization improved."

Use a required `interleaving_positions` field with values:

- `pre`
- `during`
- `tool_during`
- `post`
- `eval_only`

An experiment can have multiple positions if it includes several interventions.

### 4. Control strength should be explicit

Not all deterministic components control the LLM in the same way. A candidate list can be a hint, a hard constraint, a tool affordance, or a post-hoc correction.

Use a `control_modes` field:

| Control mode | Meaning |
| --- | --- |
| `none` | no explicit control beyond the prompt |
| `soft_hint` | model can use or ignore supplied candidates/rules |
| `hard_constraint` | output is constrained by schema, enum, parser, or validation |
| `tool_affordance` | model can call deterministic or external functions |
| `posthoc_correction` | deterministic code changes or repairs model output |
| `diagnostic_only` | deterministic code evaluates behavior but does not affect prediction |

This dimension is important because a failed soft hint does not mean the underlying deterministic knowledge is useless. It may mean the knowledge needs to be moved to a different position or given stronger control.

### 5. Knowledge sources should be named

The project currently mixes several kinds of knowledge:

- regular expressions and surface rules
- date/frequency temporal rules
- controlled vocabularies
- benchmark label policies
- JSON schema and Pydantic validators
- examples and bootstrapped demonstrations
- clinician-like semantic judgment supplied by the LLM
- CUI/ontology-aware normalization, planned but not fully built

These should be tagged separately from component type. A controlled vocabulary can be used deterministically before extraction, supplied to the LLM during extraction, exposed as a tool, applied after extraction, or used only inside the scorer.

Use a `knowledge_sources` field with values such as:

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

## Proposed Taxonomy Fields

The experiment registry should use one row per experiment family or canonical experiment ID, not one row per run directory. Individual run IDs remain attached as artifacts.

Required fields:

| Field | Purpose |
| --- | --- |
| `experiment_id` | Stable identifier from config/run metadata |
| `dataset` | Gan or ExECT |
| `schema_complexity` | `gan_s0`, `exect_s1`, `exect_s2`, `exect_s3`, `exect_s4` |
| `clinical_task_family` | frequency, diagnosis, medication, seizure type, etc.; use `multi_family` when appropriate |
| `model_track` | GPT, Qwen35b, Qwen9b, Gemini, etc. |
| `program_architecture` | single-pass, verify-repair, temporal-candidates, ReAct/tool-use, section-aware |
| `hybrid_balance_class` | coarse deterministic/LLM balance class |
| `deterministic_roles` | what deterministic components do |
| `llm_roles` | what LLM components do |
| `interleaving_positions` | pre, during, tool_during, post, eval_only |
| `knowledge_sources` | rules, vocabularies, schema, examples, label policy, ontology |
| `control_modes` | soft hint, hard constraint, tool affordance, posthoc correction, diagnostic only |
| `context_strategy` | full note, section-filtered, candidate-injected, retrieved spans |
| `evidence_strategy` | absent, model quote, injected candidates, verified quote, deterministic span check |
| `normalization_strategy` | model-only, list-constrained, tool-mediated, deterministic mapping, benchmark bridge |
| `verification_strategy` | none, LLM verifier, deterministic validator, verify-repair, adjudicator |
| `schema_integrity_strategy` | JSON schema, Pydantic validation, retry/repair, scorer-only |
| `example_strategy` | zero-shot, manual few-shot, labeled few-shot, bootstrapped, GEPA/MIPRO |
| `comparison_group` | identifier for valid comparisons under fixed controls |
| `fixed_controls` | dataset, split, scorer, schema, model, or prompt elements held constant |
| `varied_factor` | primary factor this experiment changes |
| `run_scope` | smoke, cap, slice, full validation, test holdout |
| `canonical_run_id` | run used as canonical evidence for the row |
| `outcome` | promote, freeze, reject, hold, superseded, exploratory, pending |
| `decision_doc` | path to decision or inspection document |
| `metric_caveats` | benchmark, scorer, split, or artifact caveats |

Optional but useful fields:

- `supersedes`
- `superseded_by`
- `artifact_paths`
- `headline_metric`
- `failure_modes_targeted`
- `failure_modes_remaining`
- `notes`

## Intervention Matrix

The registry should also support a matrix view where each clinical operation is classified by responsibility and position.

| Operation | Deterministic pre | LLM during | Tool during | Deterministic post | LLM post |
| --- | --- | --- | --- | --- | --- |
| Context selection | section/date/frequency span finder | model selects relevant context | retrieval or section tool | context trimming/filtering | relevance adjudicator |
| Candidate generation | entity/span/frequency candidates | model reasons over supplied candidates | candidate lookup tool | discard impossible candidates | repair missing candidate |
| Normalization | inject vocabulary or label set | model maps to allowed terms | normalizer tool | deterministic canonicalization | second-pass LLM normalizer |
| Evidence grounding | supply candidate evidence spans | model quotes evidence | span lookup tool | substring/span validation | verifier judges support |
| Schema integrity | schema/enum constraints | structured generation | validation tool | Pydantic repair/reject | repair model fixes invalid |
| Label-policy alignment | benchmark rules supplied upfront | model applies policy | policy helper tool | benchmark bridge maps output | adjudicator applies policy |
| Temporal reasoning | date/frequency candidate table | model selects current window | temporal calculator/tool | consistency checks | verifier repairs temporal error |

This view should be used when planning new experiments. It turns implementation ideas into explicit scientific choices.

## Implications For Current Work

### Gan temporal-candidates

Current local and hosted temporal-candidates systems should be classified as:

- dataset: `gan_2026`
- schema complexity: `gan_s0`
- clinical task family: `frequency`
- program architecture: `temporal_candidates_verify_repair`
- hybrid balance class: `H2_pre_deterministic` and partly `H4_deterministic_first_llm_adjudicates`
- deterministic roles: temporal candidate generation, canonical normalization, evidence span guard
- LLM roles: frequency interpretation, candidate selection, verification, repair
- interleaving positions: `pre`, `during`, `post`
- knowledge sources: temporal rules, benchmark label policy, JSON schema, gold audit policy
- control modes: soft hint, hard constraint, posthoc correction

This classification makes the research question clearer: the promoted system is not simply a better prompt. It tests whether deterministic temporal scaffolding before LLM verification improves seizure-frequency extraction.

### Gan ReAct temporal tools

The pending ReAct probe should be classified separately from temporal-candidates because it changes interleaving:

- hybrid balance class: `H3_interleaved_tool_hybrid`
- interleaving position: `tool_during`
- varied factor: deterministic temporal knowledge available as a tool during model reasoning rather than precomputed context alone

This distinction is important. A ReAct failure would not invalidate deterministic temporal scaffolding; it would test a specific interleaving strategy.

### ExECT label-policy and benchmark bridges

ExECT S1-S4 label-policy versions should not be treated only as prompt versions. Many improvements likely combine:

- LLM broad extraction
- benchmark-aligned prompt policy during extraction
- deterministic bridge or normalization logic after extraction
- scorer-aware field-family views

These should be tagged with:

- deterministic roles: normalization, benchmark alignment, schema repair or validation
- LLM roles: broad entity/family extraction
- interleaving positions: mostly `during` and `post`
- knowledge sources: benchmark label policy, gold audit policy, JSON schema
- control modes: soft hint plus posthoc correction

This will help separate true model reasoning improvements from benchmark-alignment improvements.

### ExECT schema complexity

ExECT S2, S3, and S4 should be treated as values of `schema_complexity`, not separate research branches. Their comparison is about schema breadth and field-family difficulty, with the caveat that micro F1 changes aggregate different family sets.

Useful analysis questions become:

- Does hybrid scaffolding become more valuable as schema complexity increases?
- Which field families need deterministic normalization most?
- Does Qwen need stronger deterministic scaffolding than GPT for broad schemas?

## Implications For Analysis

This taxonomy enables analysis that the current config naming cannot support well.

### Hybrid balance analysis

Compare performance by `hybrid_balance_class` within valid comparison groups:

- LLM-constrained direct extraction vs deterministic postprocessing
- deterministic preconditioning vs post-hoc correction
- tool-mediated during-extraction hybrid vs precomputed candidate injection
- deterministic-first LLM adjudication vs LLM-first deterministic repair

### Interleaving analysis

For a fixed operation, compare where the same knowledge source enters the pipeline:

- medication vocabulary as pre-injected candidate list vs during-extraction rules vs post-hoc normalizer
- temporal rules as precomputed candidate table vs ReAct tool vs post-hoc repair
- evidence spans as generated quotes vs candidate-injected spans vs deterministic support checks

### Model interaction analysis

Test whether local Qwen benefits more from deterministic scaffolding than hosted GPT:

- same dataset
- same schema complexity
- same scorer
- same run scope
- different model track
- tagged hybrid balance class

### Schema complexity analysis

Analyze whether schema breadth changes the value of different intervention types:

- single-family Gan frequency
- ExECT S1 three-family extraction
- ExECT S2-S4 broad schemas

This should prevent misleading statements such as "S4 is worse than S3" without specifying that schema scope and scorer aggregation changed.

## Implementation Steps

### Step 1: Add the registry file

Create a canonical registry file, preferably machine-readable:

- `docs/experiment_registry.csv`, or
- `docs/experiments/synthesis/experiment_registry.json`

Start with one row per distinct metric-bearing `experiment_id` from the inventory, not one row per run directory.

### Step 2: Define controlled vocabularies

Add a short schema reference document:

- `docs/taxonomy/experiment_taxonomy_schema.md`

This should define allowed values for:

- `hybrid_balance_class`
- `deterministic_roles`
- `llm_roles`
- `interleaving_positions`
- `knowledge_sources`
- `control_modes`
- `normalization_strategy`
- `verification_strategy`
- `evidence_strategy`
- `outcome`

### Step 3: Backfill canonical rows for high-value anchors first

Do not try to classify all 80 experiment IDs perfectly in one pass. Start with canonical anchors:

1. Gan hosted temporal full `...130933Z`
2. Gan local temporal full `...230324Z`
3. Gan verify-repair v2 full `...084732Z`
4. Gan synthesis bootstrap full `...065115Z`
5. ExECT S1 GPT frozen v4.10 `...221944Z`
6. ExECT S1 GPT test holdout `...222615Z`
7. ExECT S2/S3/S4 GPT frozen full runs
8. ExECT Qwen S1/S2/S3 full runs
9. ExECT Qwen S4 full when complete
10. Gan ReAct slice when complete

### Step 4: Create comparison groups

Add `comparison_group` identifiers only where comparisons are legitimate.

Examples:

- `gan_s0_architecture_gpt_validation_v1`
- `gan_s0_architecture_qwen_validation_v1`
- `exect_s1_policy_gpt_validation_v1`
- `exect_schema_complexity_gpt_validation_v1`
- `exect_qwen_replication_validation_v1`

Rows outside a shared comparison group should not be compared without explicit caveats.

### Step 5: Require taxonomy tags for new experiment configs (done 2026-05-20)

Add taxonomy metadata to new experiment configs or to the registry immediately when a config is added. At minimum:

- dataset
- schema complexity
- program architecture
- hybrid balance class
- interleaving positions
- varied factor
- comparison group
- intended decision

This converts the taxonomy from retrospective cleanup into experiment design discipline.

### Step 6: Update decision docs to cite taxonomy fields (done 2026-05-20)

Promotion, freeze, hold, and reject docs should include a short "Taxonomy" block:

```text
Dataset:
Schema complexity:
Clinical task family:
Hybrid balance class:
Interleaving positions:
Varied factor:
Comparison group:
Outcome:
```

This makes decision provenance analyzable later.

### Step 7: Add lightweight validation (done 2026-05-20)

Add tests or a small script that checks:

- every config has either a registry row or an explicit exploratory exemption
- allowed taxonomy values are valid
- canonical run IDs exist
- decision docs exist for promoted/frozen/rejected rows
- comparison groups do not mix incompatible scorers, splits, or schema scopes unless marked as non-clean

## Near-Term Research Use

Once the initial registry exists, the next research synthesis should answer these questions:

1. Which promoted systems are `H1`, `H2`, `H3`, or `H4`?
2. Did deterministic preconditioning outperform deterministic postprocessing on Gan?
3. Did ExECT gains come from model capability, benchmark policy alignment, or deterministic bridge behavior?
4. Which clinical task families still rely mostly on LLM judgment without deterministic support?
5. Which future experiments would most cleanly test interleaving position while holding dataset, schema, model, and scorer fixed?

## Risks And Caveats

- Retrospective tagging will be imperfect. Some historical experiments changed multiple factors at once.
- `hybrid_balance_class` is intentionally coarse and should not replace detailed strategy fields.
- Some deterministic behavior currently lives inside program code or scorer logic rather than config metadata; it may require code inspection to tag correctly.
- Post-hoc benchmark bridges can improve measured performance without improving clinical validity. The registry should distinguish benchmark-facing normalization from clinically meaningful normalization.
- Evidence support in current runs is a diagnostic based on substring/span support, not independent clinical evidence review.
- Published benchmark reproduction remains separate from repo synthetic validation until CUI-aware ExECT scoring and Gan Real-set access are resolved.

## Recommended Next Step

Before starting broad new experiment families, implement a minimal experiment registry using this taxonomy and backfill the canonical anchors. This is a research maturity step, not administrative polish: it makes the core hybrid-system questions measurable.

The immediate next pull should be:

1. Create `docs/taxonomy/experiment_taxonomy_schema.md` with controlled values.
2. Create `docs/experiment_registry.csv` with the first 10-15 canonical rows.
3. Add a taxonomy block to the next Gan ReAct and ExECT Qwen S4 inspection/decision documents.

