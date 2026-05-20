# Clinical Extraction Kanban Plan

**Core direction:** `docs/outline.md`  
**Current synthesis:** `docs/experiment_taxonomy_research_synthesis_20260520.md`  
**Taxonomy decision:** `docs/hybrid_component_taxonomy_decision_20260520.md`  
**Registry:** `docs/experiment_registry.json`  
**Scorer and dataset guardrails:** `docs/deterministic_scorer_semantics.md`, `docs/exect_gold_label_audit.md`, `docs/gan_2026_label_audit.md`  
**Frozen run archive:** `docs/kanban_frozen_threads_history.md`  
**Last refreshed:** 2026-05-20, after ExECT Qwen S4 inspection/registry, S1 interleaving pre-registration, and Gan ReAct H3 rejection

---

## Current Research Focus

The project has crossed from rapid prompt/program iteration into taxonomy-governed research. The immediate goal is no longer "find the next better prompt." It is to make the central scientific question measurable:

**Where should deterministic clinical knowledge enter a DSPy extraction pipeline, and how does that differ by dataset, schema breadth, model track, and clinical task family?**

The experiment taxonomy is now the planning spine. New work should hold dataset, split, schema, scorer, and model fixed unless the varied factor explicitly says otherwise. Comparison groups matter more than local version names.

## Experimentation Model

Most experiment design should happen on **GPT 4.1-mini** because it gives the fastest loop for prompt, architecture, taxonomy, and scorer-facing iteration. Use it to discover whether an idea is coherent, whether the comparison group is clean, whether the metrics move in a meaningful direction, and whether failure modes are worth deeper study.

Run **Qwen35b** on longer, more expensive studies only after the GPT loop or prior evidence shows the experiment is valuable. Qwen runs should answer focused questions about local-model feasibility, transfer of a proven architecture, or whether deterministic scaffolding changes the local/hosted model tradeoff. Do not spend Qwen time on broad speculative sweeps when the same design question can be sharpened faster on GPT 4.1-mini.

Practical rule: GPT 4.1-mini is the default exploration model; Qwen35b is the confirmatory and local-deployment model for selected high-value experiments.

## What We Know Now

### Gan S0 seizure frequency

Default architecture: **temporal-candidates verify-repair**.

Taxonomy interpretation: `H2_pre_deterministic` plus `H4_deterministic_first_llm_adjudicates`.

Key evidence:

- Qwen35b promoted full-validation temporal-candidates run: `...230324Z`, 65.8% monthly accuracy, 100% evidence support.
- GPT 4.1-mini promoted full-validation temporal-candidates run: `...130933Z`, 65.1% monthly, 76.5% Purist, 84.2% Pragmatic, 99.7% schema validity, 100% evidence support.
- ReAct temporal-tools H3 slice rejected: `...173943Z`, 50% schema validity and 42.9% monthly accuracy on valid predictions.

Research interpretation: deterministic temporal knowledge works best when precomputed and injected before LLM adjudication. Tool-during ReAct did not replace preconditioning under strict Gan label constraints.

### ExECT S1-S4 schema ladder

Hosted GPT is frozen across S1-S4. Local Qwen replication has now completed through S4 full validation.

Current anchors:

| Schema | GPT 4.1-mini | Qwen35b | Interpretation |
| --- | ---: | ---: | --- |
| S1 | 92.3% micro | 79.0% micro | Qwen lags on the narrow audited S1 policy surface. |
| S2 | 80.9% micro | 82.6% micro | Qwen matches or slightly exceeds GPT under broader scope. |
| S3 | 72.1% micro | 72.2% micro | Qwen essentially matches GPT. |
| S4 | 65.5% micro | 67.5% micro (`...160914Z`) | Qwen slightly exceeds GPT on the 11-family S4 diagnostic view. |

Research interpretation: schema breadth changes the field-family surface, so the ladder is not a simple learning curve. The next useful ExECT question is not broader schema expansion; it is a fixed-schema interleaving experiment.

### Experiment taxonomy

Completed:

- `docs/experiment_registry.json`
- `docs/experiment_taxonomy_schema.md`
- typed taxonomy metadata in experiment configs
- registry validation in `src/clinical_extraction/experiments/registry_validation.py`
- `scripts/validate_experiment_taxonomy.py`
- focused tests for registry/config coverage
- taxonomy synthesis answering near-term research questions

Research interpretation: taxonomy is now part of experiment design. Avoid more broad exploratory runs that cannot isolate the varied factor.

## Active Work

### 1. Implement and run ExECT S1 interleaving (GPT phase 1)

Pre-registration complete: `docs/exect_s1_interleaving_experiment_preregistration_20260520.md`

Stub configs (implementation pending):

- `configs/experiments/exect_s1_interleaving_h1_post_bridge_gpt4_1_mini.json`
- `configs/experiments/exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini.json`
- H3 config deferred until `exect_s0_s1_field_family_react_normalize_tools` is registered in `ExperimentConfig`

L1 baseline anchor (frozen, no new run): `exect_s0_s1_validation_full_gpt4_1_mini` — 92.3% micro.

Run order: cap-25 gates for new arms → full validation (40) → inspection + registry rows under `exect_s1_interleaving_gpt_validation_v1`.

### 2. ExECT field-family deterministic support map

Build the compact table described under **Ready After Active Work** (GPT/Qwen performance, deterministic roles, candidate interleaving positions). Can proceed in parallel with S1 implementation planning.

## Recently Completed (2026-05-20)

- ExECT Qwen S4 full inspection: `docs/exect_s4_validation_full_qwen35b_ollama_inspection_20260520.md` (`…160914Z`, 67.5% micro, +2.0pp vs GPT v1.2)
- Registry row: `exect_s4_validation_full_qwen35b_ollama` (cap-25 row `…133930Z` remains gate-only)
- S1 interleaving pre-registration + stub configs (see Active Work §1)
- Gan Qwen H1 full comparator: **deferred** — slice evidence sufficient; see **Current Decisions**

## Ready After Active Work

### ExECT field-family deterministic support map

Build a compact table of ExECT field families showing:

- current GPT and Qwen performance
- existing deterministic roles
- candidate knowledge source
- candidate interleaving position
- likely clinical/scorer caveat

Likely high-value targets:

- medication: controlled vocabulary or deterministic mapping
- medication temporality: planned/current/previous bridge
- seizure type: benchmark-policy versus clinical-specificity boundary
- diagnosis: certainty/specificity policy
- seizure frequency: whether Gan temporal scaffolding transfers to ExECT S4 frequency fields

### Paper-ready registry matrix export

Create a stable table from `docs/experiment_registry.json` grouped by:

- dataset
- schema complexity
- model track
- program architecture
- hybrid balance class
- interleaving position
- comparison group
- outcome
- headline metric

This is useful for methods/results drafting; S4 Qwen full row is now settled.

### Optional Gan model-interaction robustness slice

Only run this if the Gan narrative needs model-interaction evidence. Keep the same records, scorer, schema, and temporal-candidates architecture across GPT and Qwen.

## Blocked Or Deferred

### Published ExECTv2 benchmark reproduction

Blocked on CUI-aware all-family scoring. Current ExECT numbers are local field-family diagnostics, not published Table 1 reproduction.

Use `dataset-audit-first` and `gold-scorer-integrity` before touching this.

### Published Gan real-set reproduction

Blocked on access to Gan Real(300)/Real(150) style data. Current Gan claims are fixed synthetic validation claims.

### Broad ExECT architecture ablation

Deferred until the S1-only interleaving experiment is designed. A broad monolithic versus field-family versus verify-repair versus section-aware ablation would change too many factors at once right now.

### Optimizer scale-up

Deferred. ExECT compile infrastructure can be reopened later, but optimizers should be explicit ablation factors, not silent prompt tuning.

## Current Decisions

| Decision | Current position |
| --- | --- |
| Experiment loop | Explore primarily on GPT 4.1-mini; reserve Qwen35b for selected high-value focus experiments |
| Gan default architecture | Temporal-candidates verify-repair (`H2` + `H4`) |
| Gan ReAct H3 | Rejected as default path; keep as negative control |
| ExECT next experiment | S1-only interleaving, not S5 or broad architecture expansion |
| Registry policy | Taxonomy fields required for new configs or registry rows |
| Benchmark claims | Keep separate from local validation until scorer/data blockers clear |
| Mass historical backfill | Defer low-value exploratory Gan direct rows |
| Gan Qwen H1 full (verify-repair, no temporal candidates) | **Skip** for now — hard-slice H1 regressed; temporal-candidates promoted; full run unlikely to change default |
| ExECT Qwen S4 full | **Hold** as local ladder anchor (`…160914Z`); +2.0pp pooled micro vs GPT but weaker seizure/diagnosis per-family |

## Recommended Next Pull

1. Implement H1 post-bridge-only program path (smallest diff vs frozen L1).
2. Run GPT cap-25 for H1, then full validation if gates pass.
3. Implement H2 pre-vocabulary arm; repeat cap-25 → full ladder.
4. Defer or implement H3 tools only if H1/H2 show interleaving position matters on GPT.

## Long-Term Research Arc

1. Stabilize taxonomy-governed evidence and keep decision docs linked to registry rows.
2. Use Gan as the completed temporal-frequency case study for deterministic preconditioning versus tool-during reasoning.
3. Use ExECT S1 as the next causal test of benchmark policy, deterministic bridges, controlled vocabularies, and tool-mediated normalization.
4. Port only the strongest GPT-discovered interventions to Qwen and test whether local Qwen benefits more from deterministic scaffolding than hosted GPT under fixed comparison groups.
5. Only then reopen broad architecture ablations, optimizers, and benchmark reproduction infrastructure.
