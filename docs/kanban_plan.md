# Clinical Extraction Kanban Plan

**Core direction:** `docs/outline.md`  
**Current synthesis:** `docs/experiment_taxonomy_research_synthesis_20260520.md`  
**Taxonomy decision:** `docs/hybrid_component_taxonomy_decision_20260520.md`  
**Registry:** `docs/experiment_registry.json`  
**Scorer and dataset guardrails:** `docs/deterministic_scorer_semantics.md`, `docs/exect_gold_label_audit.md`, `docs/gan_2026_label_audit.md`  
**Frozen run archive:** `docs/kanban_frozen_threads_history.md`  
**Last refreshed:** 2026-05-20, after S4 frequency pre-candidate cap-25 (reject H2)
**Support map:** `docs/exect_field_family_deterministic_support_map_20260520.md`

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

### 1. S4 medication temporality post classifier (GPT)

Precision-primary probe on planned/taper phrases (`exect_s4_temporality_deterministic_v1`); after or in parallel with frequency probe if configs do not share program paths.

## Recently Completed (2026-05-20)

- **S4 frequency pre-candidate cap-25 GPT complete:** L1 49.1% / H2 47.1% seizure_frequency F1 (`…191914Z` / `…191951Z`); inspection `docs/exect_s4_frequency_deterministic_gpt_inspection_20260520.md` — **reject** H2 (−2.0pp); program `exect_s4_field_family_frequency_pre_vocab_single_pass` + configs + preregistration.
- **Medication pre-vocab slice GPT complete:** L1 98.3% / H2 95.1% medication F1 (`…191336Z` / `…191345Z`); inspection `docs/exect_s1_medication_pre_vocab_slice_gpt_inspection_20260520.md` — **reject** H2 (−3.2pp medication F1); registry rows added.
- **Interleaving v2 registry rows:** four rows under `exect_s1_interleaving_gpt_validation_v2` (`docs/experiment_registry.json`).
- **S1 interleaving v2 GPT complete:** L1 raw 68.6% / H1 post 92.3% full micro (`…190804Z` / `…190807Z`); inspection `docs/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md` — bridges contribute ~24pp micro vs raw.
- **Medication-only H2 slice scaffold:** `exect_s0_s1_field_family_medication_pre_vocab_single_pass`, slice fixture, L1/H2 slice configs, tests (`exect_s1_medication_pre_vocab_slice_gpt_v1`).
- **Bridge-free S1 repair policy:** `REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES` in `exect_s0_s1.py`; interleaving v2 configs `exect_s1_interleaving_l1_raw_no_bridges_{cap25,full}_gpt4_1_mini.json`.
- **ExECT field-family deterministic support map:** `docs/exect_field_family_deterministic_support_map_20260520.md` — S1–S4 per-family GPT/Qwen anchors, deterministic inventory, interleaving lessons, ranked experiment queue (bridge-free baseline → family-isolated probes).
- **S1 interleaving GPT phase 1 complete:** H1 cap-25/full + H2 cap-25/full; inspection `docs/exect_s1_interleaving_gpt_validation_v1_inspection_20260520.md`; registry rows under `exect_s1_interleaving_gpt_validation_v1`. H1 **hold (null)** vs L1; H2 **reject** (−4.8pp full micro); H3 deferred.
- S1 interleaving H1/H2 program paths + cap-25/full configs (`src/clinical_extraction/programs/exect_s0_s1.py`, `scripts/run_experiment.py`)
- ExECT Qwen S4 full inspection: `docs/exect_s4_validation_full_qwen35b_ollama_inspection_20260520.md` (`…160914Z`, 67.5% micro, +2.0pp vs GPT v1.2)
- Registry row: `exect_s4_validation_full_qwen35b_ollama` (cap-25 row `…133930Z` remains gate-only)
- S1 interleaving pre-registration + v2 configs (see v2 inspection doc)
- Gan Qwen H1 full comparator: **deferred** — slice evidence sufficient; see **Current Decisions**

## Ready After Active Work

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
| ExECT next experiment | S4 medication temporality post classifier (`exect_s4_temporality_deterministic_v1`) |
| ExECT S4 frequency H2 pre-vocab | **Reject** — 47.1% vs 49.1% seizure_frequency F1 on cap-25 (−2.0pp) |
| ExECT medication H2 slice | **Reject** — 95.1% vs 98.3% medication F1 on 14-record Rx-heavy slice (−3.2pp) |
| ExECT interleaving v2 registry | **Done** — four rows in `exect_s1_interleaving_gpt_validation_v2` |
| ExECT S1 interleaving H1 (v2) | **Hold (null vs production L1)** — 92.3% full micro; bridges match `repair_policy=none` |
| ExECT S1 interleaving L1 raw (v2) | **Diagnostic** — 68.6% full micro without bridges; ~24pp bridge contribution measured |
| ExECT S1 interleaving H1 (v1) | **Superseded** — v1 null explained by always-on bridges; see v2 inspection |
| ExECT S1 interleaving H2 | **Reject** — pre-vocab regressed full micro to 87.5% (−4.8pp vs L1) |
| ExECT S1 interleaving H3 | **Defer** — no positive signal from H1/H2 |
| Registry policy | Taxonomy fields required for new configs or registry rows |
| Benchmark claims | Keep separate from local validation until scorer/data blockers clear |
| Mass historical backfill | Defer low-value exploratory Gan direct rows |
| Gan Qwen H1 full (verify-repair, no temporal candidates) | **Skip** for now — hard-slice H1 regressed; temporal-candidates promoted; full run unlikely to change default |
| ExECT Qwen S4 full | **Hold** as local ladder anchor (`…160914Z`); +2.0pp pooled micro vs GPT but weaker seizure/diagnosis per-family |

## Recommended Next Pull

1. Design + run S4 medication temporality post-classifier probe (`exect_s4_temporality_deterministic_v1`; precision-primary).
2. Keep L1 frozen as ExECT S1/S4 GPT default; do not promote any H2 pre-vocab variant (S1, medication slice, or S4 frequency).
3. Paper-ready registry matrix export remains optional methods prep.

## Parallelization

| Safe in parallel | Single-threaded |
| --- | --- |
| Support map doc (done) + registry matrix export | Interleaving v2 cap-25/full runs (same comparison group) |
| S4 frequency cap-25 design + run | S4 temporality classifier design (if shared scorer paths) |
| S4 frequency experiment design doc | Qwen ports (after GPT ≥2pp full-validation gain) |

## Long-Term Research Arc

1. Stabilize taxonomy-governed evidence and keep decision docs linked to registry rows.
2. Use Gan as the completed temporal-frequency case study for deterministic preconditioning versus tool-during reasoning.
3. Use ExECT S1 as the next causal test of benchmark policy, deterministic bridges, controlled vocabularies, and tool-mediated normalization.
4. Port only the strongest GPT-discovered interventions to Qwen and test whether local Qwen benefits more from deterministic scaffolding than hosted GPT under fixed comparison groups.
5. Only then reopen broad architecture ablations, optimizers, and benchmark reproduction infrastructure.
