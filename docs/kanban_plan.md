# Clinical Extraction Kanban Plan

**Core direction:** `docs/outline.md`  
**Current synthesis:** `docs/experiment_taxonomy_research_synthesis_20260520.md`  
**Negative-probe synthesis:** `docs/exect_negative_probe_synthesis_20260520.md`  
**Primitive coverage audit:** `docs/taxonomy_primitive_coverage_audit_20260520.md`  
**Phase 2 preregistration:** `docs/exect_qwen_s1_seizure_gap_error_analysis_preregistration_20260520.md`  
**Taxonomy decision:** `docs/hybrid_component_taxonomy_decision_20260520.md`  
**Phase roadmap:** `docs/next_major_phases_20260520.md`  
**Registry:** `docs/experiment_registry.json` · **Matrix export:** `docs/experiment_registry_matrix_20260520.md`  
**Scorer and dataset guardrails:** `docs/deterministic_scorer_semantics.md`, `docs/exect_gold_label_audit.md`, `docs/gan_2026_label_audit.md`  
**Frozen run archive:** `docs/kanban_frozen_threads_history.md`  
**Last refreshed:** 2026-05-20, after Qwen S1 seizure-gap error-analysis preregistration
**Support map:** `docs/exect_field_family_deterministic_support_map_20260520.md`  
**Taxonomy primitives:** `docs/taxonomy_primitives_workstream_plan_20260520.md` (catalog: `docs/taxonomy_primitive_catalog.md`)

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

Research interpretation: schema breadth changes the field-family surface, so the ladder is not a simple learning curve. S1 interleaving v2, Qwen interleaving v1, and all S1/S4 family-isolated pre-vocab probes are **closed** with no promotable intervention. The next ExECT step is a decision phase, not another automatic port: choose a new hypothesis from the support map or pause model-backed ExECT runs for synthesis.

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

### Taxonomy primitives (build-before-run)

**Workstream plan:** `docs/taxonomy_primitives_workstream_plan_20260520.md`  
**Catalog / contract:** `docs/taxonomy_primitive_catalog.md`, `docs/taxonomy_primitive_contract.md`  
**Validation:** `uv run python scripts/validate_primitives.py --errors-only`

Core infrastructure is in place for taxonomy-governed experiments: shared candidate, normalization, and evidence contracts; typed primitive registry; Gan frequency and ExECT S1/S4 primitive packs; interleaving adapters; L1/H1/H2/H3/H4/D1 arm templates; deterministic fixture library; inspection templates. New model-backed runs should compose these primitives rather than ad hoc helper changes.

Decisions recorded: minimal H3 tool interface only (`docs/taxonomy_tool_interface_decision_20260520.md`); CUI/ontology primitives deferred to published benchmark reproduction (`docs/taxonomy_ontology_cui_scope_decision_20260520.md`). Broad ExECT sparse-family sketches (investigation, comorbidity, onset, etc.) are catalogued as `planned` metadata only.

Still blocked: Card 19 published ExECT CUI benchmark pack; Card 20 Gan Real(300)/Real(150) primitive validation (data access).

## Active Work

**Current mode:** documentation consolidation and next-phase scoping.

**Next model-backed comparison group:** **not selected**. `exect_s1_interleaving_qwen_validation_v1` is closed as a reject-port narrative; do not start another ExECT run until the preregistered Qwen S1 seizure-gap error analysis either names a clean new mechanism or recommends a synthesis pause.

No runs in flight. S1 interleaving GPT v2 + Qwen v1 and all S1/S4 family-isolated GPT probes **closed**.

## Next Major Phases

### Phase 1 - Consolidate the taxonomy-governed evidence base

Outcome: a clean research memory layer that tells the story of what has been tried, which mechanisms were rejected, which anchors are frozen, and which claims are safe.

Ready cards:

- **Refresh steering docs:** remove stale next-run language, align `docs/kanban_plan.md`, `docs/exect_field_family_deterministic_support_map_20260520.md`, and `docs/taxonomy_primitives_workstream_plan_20260520.md`.
- **Synthesize negative ExECT probes:** `docs/exect_negative_probe_synthesis_20260520.md` explains why S1 interleaving, H2 pre-vocab, S4 frequency pre-candidates, S4 temporality H1, and Qwen interleaving v1 did not promote.
- **Audit primitive-to-experiment coverage:** `docs/taxonomy_primitive_coverage_audit_20260520.md` classifies implemented and planned primitives as `promoted`, `diagnostic_only`, `rejected_for_current_arm`, `planned`, or `blocked`.

Validation: documentation links resolve; claims cite inspection docs or run IDs; no placeholder item implies a runnable experiment.

### Phase 2 - Select the next ExECT hypothesis

Outcome: one preregistered ExECT comparison group, or an explicit decision to pause ExECT model-backed work.

Current decision: start with a no-model Qwen S1 seizure-gap error analysis before any new ExECT model-backed run. Preregistration: `docs/exect_qwen_s1_seizure_gap_error_analysis_preregistration_20260520.md`.

Candidate directions:

- **Qwen seizure-gap diagnosis:** inspect whether the S1 seizure gap is prompt/model-policy failure rather than a missing deterministic bridge. This should start with error analysis, not pre-vocab injection.
- **S4 frequency mechanism redesign:** revisit ExECT frequency only if the varied factor is new, such as prompt policy, candidate presentation shape, or post-template repair, not the rejected H2 pre-candidate arm.
- **S4 medication temporality fallback:** only consider a dose-only abstention fallback if it is framed as a narrow repair to the observed recall collapse, not a broad temporality classifier retune.

Validation: a pre-registration states dataset, split, schema, model, scorer, frozen baseline, varied factor, primitive IDs, gate, and reject/hold/promote criteria.

### Phase 3 - Reproduction and external validity

Outcome: separate local diagnostic claims from published benchmark reproduction and external-data claims.

Blocked cards:

- Published ExECTv2 reproduction remains blocked on CUI-aware all-family scoring and ontology-aligned primitives.
- Gan Real(300)/Real(150) validation remains blocked on data access.

Validation: use `dataset-audit-first` and `gold-scorer-integrity`; do not compare published benchmark claims with local field-family diagnostics without caveats.

### Phase 4 - Scale-up and ablation expansion

Outcome: reopen broad architecture, optimizer, and model-family studies only after the narrow mechanism evidence is coherent.

Deferred cards:

- Broad ExECT architecture matrix.
- DSPy optimizer scale-up.
- Additional local/closed model comparisons beyond focused Qwen confirmation.

Validation: each scale-up varies one explicit factor or is documented as an interaction study.

## Recently Completed (2026-05-20)

- **Primitive catalog aligned with coverage audit:** `docs/taxonomy_primitive_catalog.md` now separates registry implementation status from evidence status; Gan S0 temporal-candidates plus verify-repair are the only promoted deterministic primitive path, while ExECT implemented primitives are marked diagnostic, planned, blocked, or rejected for current arm shapes.
- **Qwen S1 seizure-gap error analysis preregistered:** `docs/exect_qwen_s1_seizure_gap_error_analysis_preregistration_20260520.md` selects a no-model Phase 2 first step using frozen Qwen/GPT H1 artifacts before any new ExECT run.
- **S1 interleaving Qwen v1 complete:** cap-25 + full — L1 raw 66.2% / H1 post 79.0% micro full (`…210719Z` / `…210722Z`); inspection `docs/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md` — **reject port**; bridge Δ +12.8pp full (GPT v2 +23.7pp); H1 **null** vs Qwen production anchor; seizure gap −34.8pp vs GPT H1.
- **S1 seizure pre-vocab slice GPT complete:** L1 91.5% / H2 83.3% seizure_type F1 (`…205806Z` / `…205814Z`); inspection `docs/exect_s1_seizure_pre_vocab_slice_gpt_inspection_20260520.md` — **reject** H2 (−8.2pp); program `exect_s0_s1_field_family_seizure_pre_vocab_single_pass` + configs + fixture + tests.
- **S4 medication temporality planned/taper error-read:** `docs/exect_s4_temporality_planned_taper_error_read_20260520.md` — 19 H1-new FNs analyzed; 4/19 planned/taper slice, 17/19 unknown-drop on dose-only ASM evidence; **no taper retune warranted**
- **S4 medication temporality full validation GPT complete:** L1 46.4% / H1 56.5% MT precision (`…204207Z` / `…204216Z`); inspection `docs/exect_s4_temporality_deterministic_gpt_inspection_20260520.md` — **reject H1** (+10.1pp precision but −6.6pp MT F1 recall collapse on 40 records).
- **Paper-ready registry matrix export:** `docs/experiment_registry_matrix_20260520.md` (41 curated rows); regenerate via `uv run python scripts/export_experiment_registry_matrix.py`.
- **S4 medication temporality cap-25 GPT complete:** L1 46.8% / H1 61.3% medication_temporality precision (`…203755Z` / `…203803Z`); cap-25 gate passed but did not generalize to full validation.
- **Taxonomy primitives workstream:** core phase complete — registry, catalog, adapters, arm templates, fixtures, `scripts/validate_primitives.py`; see `docs/taxonomy_primitives_workstream_plan_20260520.md`.
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

## Ready After Consolidation

### Optional Gan model-interaction robustness slice

Only run this if the Gan narrative needs model-interaction evidence. Keep the same records, scorer, schema, and temporal-candidates architecture across GPT and Qwen.

### ExECT next-hypothesis pre-registration

Ready after Phase 1 synthesis identifies a mechanism worth testing. The preregistration must name the baseline, run scope, scorer mode, primitive IDs, and decision gate before any model-backed execution.

## Blocked Or Deferred

### Published ExECTv2 benchmark reproduction

Blocked on CUI-aware all-family scoring. Current ExECT numbers are local field-family diagnostics, not published Table 1 reproduction.

Use `dataset-audit-first` and `gold-scorer-integrity` before touching this.

### Published Gan real-set reproduction

Blocked on access to Gan Real(300)/Real(150) style data. Current Gan claims are fixed synthetic validation claims.

### Broad ExECT architecture ablation

Deferred. S1 interleaving v1/v2 and S4 family-isolated probes are complete; reopen only after a promotable single-factor arm exists or for an explicit pre-registered architecture matrix.

### Optimizer scale-up

Deferred. ExECT compile infrastructure can be reopened later, but optimizers should be explicit ablation factors, not silent prompt tuning.

## Current Decisions

| Decision | Current position |
| --- | --- |
| Experiment loop | Explore primarily on GPT 4.1-mini; reserve Qwen35b for selected high-value focus experiments |
| Gan default architecture | Temporal-candidates verify-repair (`H2` + `H4`) |
| Gan ReAct H3 | Rejected as default path; keep as negative control |
| ExECT S1 interleaving Qwen v1 | **Complete — reject port** — full bridge Δ +12.8pp micro; H1 null vs Qwen anchor; does not close GPT seizure gap |
| ExECT next experiment | **Decision phase** — no further S1 interleaving or H2 pre-vocab reruns without a new mechanism and preregistered comparison group |
| ExECT S1 seizure H2 slice | **Reject** — 83.3% vs 91.5% seizure_type F1 on 15-record slice (−8.2pp) |
| ExECT S1 seizure L1 slice | **Hold (slice reference)** — 91.5% seizure_type F1 |
| ExECT S4 temporality error-read | **Done** — dose-only unknown-abstention caused recall collapse; planned/taper slice 4/19 FNs; no taper retune |
| ExECT S4 temporality H1 full | **Reject** — 56.5% vs 46.4% MT precision (+10.1pp) but −6.6pp MT F1 on full validation (40) |
| ExECT S4 temporality H1 cap-25 | **Hold (cap-25 only)** — gate passed on 25 records; full validation rejected |
| ExECT S4 temporality L1 full | **Hold (full-validation reference)** — 46.4% MT precision |
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

1. Execute the preregistered Qwen S1 seizure-gap error analysis and write `docs/exect_qwen_s1_seizure_gap_error_analysis_20260520.md`.
2. Use that analysis to decide whether the next model-backed path is prompt-policy preregistration, narrow post-template repair, manual audit review, or synthesis pause.
3. Keep L1 frozen as ExECT S1/S4 GPT default; keep Qwen S1 production anchor frozen at 79.0% micro.
4. Regenerate `docs/experiment_registry_matrix_20260520.md` after registry changes.

## Parallelization

| Safe in parallel | Single-threaded |
| --- | --- |
| Kanban/support-map wording cleanup | Choosing the next model-backed ExECT comparison group |
| Primitive catalog coverage audit | Any preregistration that changes scorer, schema, or baseline semantics |
| Registry matrix regeneration after metadata edits | Model-backed full validation runs |
| Negative-probe synthesis drafting | Published benchmark reproduction design |

## Long-Term Research Arc

1. Consolidate taxonomy-governed evidence and keep decision docs linked to registry rows.
2. Use Gan as the completed temporal-frequency case study for deterministic preconditioning versus tool-during reasoning.
3. Treat ExECT as a mechanism-selection problem: only run new S1/S4 probes when the varied factor differs from the rejected post-bridge and H2 pre-vocab shapes.
4. Port only promotable GPT-discovered interventions to Qwen; use Qwen diagnostics when the research question is local-model feasibility or model-specific failure.
5. Separate local diagnostic validation from published benchmark reproduction until CUI-aware ExECT scoring and Gan real-set access are resolved.
6. Reopen broad architecture ablations and optimizers only after the next narrow mechanism has a clean hold/promote signal.
