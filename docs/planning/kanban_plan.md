# Clinical Extraction Kanban Plan

**Core direction:** `docs/outline.md`  
**Research pivot (active doctrine):** `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`  
**Literature review:** `docs/planning/multi_stage_llm_clinical_extraction_literature_review_20260521.md`  
**Implementation plan:** `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`  
**Mechanism status (open vs arm-reject):** `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`  
**Agent skill:** `hybrid-pipeline-exploration`  
**Historical snapshot:** `docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md`  
**Taxonomy implementation log:** `docs/taxonomy/experiment_taxonomy_research_synthesis_20260520.md`  
**Negative-probe synthesis:** `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md`  
**Primitive coverage audit:** `docs/taxonomy/taxonomy_primitive_coverage_audit_20260520.md`  
**Phase 2 preregistration:** `docs/experiments/exect/exect_qwen_s1_seizure_gap_error_analysis_preregistration_20260520.md`  
**Phase 2 analysis:** `docs/experiments/exect/exect_qwen_s1_seizure_gap_error_analysis_20260520.md`  
**Phase 2 prompt-policy prereg:** `docs/experiments/exect/exect_s1_seizure_prompt_policy_qwen_preregistration_20260520.md`  
**Taxonomy decision:** `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`  
**DSPy optimizer investigation:** `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md`  
**Phase roadmap:** `docs/planning/next_major_phases_20260520.md`  
**Registry:** `docs/experiments/synthesis/experiment_registry.json` · **Matrix export:** `docs/experiments/synthesis/experiment_registry_matrix_20260520.md`  
**Evidence matrix:** `docs/research_atlas/evidence_matrix.md`  
**Scorer and dataset guardrails:** `docs/policies/deterministic_scorer_semantics.md`, `docs/datasets/exect/exect_gold_label_audit.md`, `docs/datasets/gan/gan_2026_label_audit.md`  
**Frozen run archive:** `docs/planning/kanban_frozen_threads_history.md`  
**Prior-best reanalysis:** `docs/experiments/synthesis/prior_best_vs_current_best_reanalysis_20260521.md`  
**Last refreshed:** 2026-05-21, after multi-stage LLM clinical extraction literature review (`docs/planning/multi_stage_llm_clinical_extraction_literature_review_20260521.md`)
**Lane A preregistrations:** `docs/experiments/gan/gan_s0_verification_gpt_validation_v1_preregistration_20260521.md`, `docs/experiments/gan/gan_s0_evidence_policy_gpt_validation_v1_preregistration_20260521.md`, `docs/experiments/gan/gan_s0_prompt_policy_gpt_validation_v1_preregistration_20260521.md`, `docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_preregistration_20260521.md`, `docs/experiments/exect/exect_s1_prompt_policy_gpt_validation_v1_preregistration_20260521.md`, `docs/experiments/exect/exect_s1_verification_gpt_validation_v1_preregistration_20260521.md`, `docs/experiments/exect/exect_s1_evidence_policy_gpt_validation_v1_preregistration_20260521.md`, `docs/experiments/exect/exect_s1_optimizer_gpt_cap25_v1_preregistration_20260521.md`
**Support map:** `docs/experiments/exect/exect_field_family_deterministic_support_map_20260520.md`  
**Taxonomy primitives:** `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md` (catalog: `docs/taxonomy/taxonomy_primitive_catalog.md`)

---

## Current Research Focus

**Pivot (2026-05-21):** Stop treating operational defaults as answered science. Explore hybrid pipelines on **three axes** with GPT 4.1-mini **cap-25 search grids** before narrowing again.

| Axis | Question |
| --- | --- |
| **1** | How many stages should the pipeline have? (`pipeline_stage_graph`) |
| **2** | At each stage: deterministic, LLM, or hybrid? (`stage_executor`) |
| **3** | What concrete implementation for each stage? (`implementation_variant`) — **only after 1–2** |

**Doctrine:** distinguish **reject (arm)** vs **reject (mechanism)** vs **operational freeze**. See `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` and skill `hybrid-pipeline-exploration`.

**Ontology (unchanged):** `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md` — `L0`–`D1`, interleaving positions, registry fields.

**Lane A / ladder / negative probes (complete):** valuable **arm** evidence and repeat guardrails — **not** mechanism closure. Do not rerun identical probe configs; do run new stage-graph and executor grids.

## Experimentation Model

**Search on GPT 4.1-mini cap-25** — rank arms, accept nulls, avoid mechanism-reject language on single configs.

**Confirm on slice / full validation** — only for cap-25 winners per prereg.

**Qwen35b** — confirmatory port of winning cells only; no broad speculative grids.

**Comparison groups** — one primary `varied_factor` per group; name axis in prereg (`docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`).

## Literature-Informed Follow-Ups

Source report: `docs/planning/multi_stage_llm_clinical_extraction_literature_review_20260521.md`

Interpretation: recent clinical IE papers support modular extraction, but mainly when each stage has a distinct reliability function: retrieval/context selection, schema constraint, field-family decomposition, evidence grounding, deterministic validation, targeted repair/judge review, or uncertainty routing. Do not add stages unless the varied mechanism is measurable.

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| Preregister evidence-first Gan S0 retrieval ablation | **Done** | Inspection `docs/experiments/gan/gan_s0_retrieval_gpt_cap25_v1_inspection_20260521.md` — R2 hold 52%; R1/R3 reject (arm) | Current Gan temporal-candidates default; scorer semantics in `docs/datasets/gan/gan_2026_label_audit.md` | yes | Registry rows optional follow-up |
| Design Gan S0 validation ladder | **Done** | Prereg + implementation `docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_preregistration_20260521.md` — V0–V7 configs ready | Phase 2–3 cap-25 anchor (E1 52% monthly) | yes | Run cap-25 grid; inspection pending |
| Preregister ExECT S1 field-family prompt graph | **Done** | Inspection `docs/experiments/exect/exect_s1_field_family_prompt_graph_gpt_cap25_v1_inspection_20260521.md` — PG0 hold 95.8%; PG1/PG2 reject (arm) | Existing ExECT S1 stage-graph card; explicit bridge policy per arm | after bridge policy is fixed | Per-family F1, micro F1, evidence support, schema validity, bridge contribution, and merge-error analysis |
| Run fixture-to-real reality-gap audit | **Backlog** | Small report comparing deterministic fixture outcomes, cap-25 dev behavior, and full validation behavior for one Gan and one ExECT family | Existing fixture coverage plus recent Gan/ExECT inspections | yes | Documents where fixtures overstate performance; updates failure-mode tags from real dev errors |
| Audit run metadata for validation outcomes | **Done** | `docs/experiments/synthesis/run_metadata_validation_repair_audit_20260521.md` — artifacts are adequate but split across files; recommends `run_manifest.json`, resolved model config copy, selected record IDs, and standardized `validation_outcomes` | none | yes | Gap report plus narrow implementation cards if missing metadata blocks literature-grade reporting |

Dependency notes:

- Pull Gan retrieval and validation-ladder preregistration first; they test mechanisms most directly supported by CLEAR, llm_extractinator, and the multi-stage validation framework.
- Keep ExECT S1 field-family prompt graph aligned with the active stage-graph axis; bridge behavior must be explicit before results can be interpreted.
- Treat fixture/reality-gap work as research hygiene, not a blocker for cap-25 exploration unless fixture claims are being used as performance evidence.

## Prior-Best Reanalysis Follow-Ups

Source report: `docs/experiments/synthesis/prior_best_vs_current_best_reanalysis_20260521.md`

Interpretation: the older best-config report still carries useful prompt-policy evidence, especially Gan v3/v5 canonical frequency-format discipline and ExECT label-contract examples. Current best pipelines are stronger architecture bundles, so the follow-up should port those older ingredients into fixed modern skeletons rather than rerunning stale conditions.

| Card | Status | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- | --- |
| Preregister Gan S0 canonical-format port onto temporal-candidates | **Done** | `docs/experiments/gan/gan_s0_canonical_format_port_gpt_cap25_v1_preregistration_20260521.md` — C0/C1 cap-25; normalized-label exact primary | `docs/experiments/synthesis/prior_best_vs_current_best_reanalysis_20260521.md`; current Gan temporal-candidates default; scorer semantics in `docs/datasets/gan/gan_2026_label_audit.md` | yes | Prereg names dataset/split, model, fixed skeleton, varied factor `implementation_variant`, metrics, gates, and residual-slice plan |
| Implement Gan S0 canonical-format port cap-25 | **Done** | Inspection `docs/experiments/gan/gan_s0_canonical_format_port_gpt_cap25_v1_inspection_20260521.md` — C1 hold +4pp normalized exact |
| Replay Gan exact-frequency residual slice | **Done** | `docs/experiments/gan/gan_s0_canonical_format_residual_slice_replay_20260521.md` — C0/C1 null on 30-record queue (1 recovery, 1 regression); cap-50 confirm deferred |
| Preregister ExECT S4 frequency surface repair | **Done** | `docs/experiments/exect/exect_s4_frequency_surface_repair_gpt_cap25_v1_preregistration_20260521.md` — R0 v1.2 bridge vs R1 post-merge | Current S4 anchors `...071248Z` and `...160914Z`; `docs/experiments/exect/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md` | yes | Prereg defines frequency-heavy slice or cap-25 gate, scorer `exect_s4_field_family_deterministic_v1`, no-regression checks for investigation/seizure/medication |
| Implement ExECT S4 frequency surface repair cap-25 | **Done** | Inspection `docs/experiments/exect/exect_s4_frequency_surface_repair_gpt_cap25_v1_inspection_20260521.md` — R1 reject (arm) 48.1% vs R0 51.0% freq F1 | Preregister ExECT S4 frequency surface repair | yes | Frequency F1 improves without material regression in frozen S3 families; update inspection doc before any full validation |
| Preregister + run ExECT S4 frequency structured slots (Axis 3) | **Done** | Inspection `docs/experiments/exect/exect_s4_frequency_structured_slots_gpt_cap25_v1_inspection_20260521.md` — S2 hold inconclusive 51.0% = R0 | Implementation plan item 23; R1 post-merge arm-reject | yes | New `frequency_structured_slots_v1`; not Gan monthly normalization |
| ExECT S4 sparse-family surface policy memo | **Done** | `docs/experiments/exect/exect_s4_sparse_family_surface_policy_20260521.md` — annotation-faithful + CUIPhrase bridges; model spend deferred until bridge scaffolds | Item 24 gate; residual synthesis | yes | Gates cap-25 sweeps on onset/when_diagnosed/cause/birth_history |
| Replay Gemini under current S-level architecture | **Deferred** | Optional S1 first, then S4 only if needed, to decide whether the prior Gemini champion remains relevant under current prompts/scorers/bridges | Model-comparison need; stable S1/S4 anchors | no | Same split/scorer/bridge policy as GPT/Qwen anchors; report as model-comparison evidence, not stale Round 2 continuation |

Dependency notes:

- Keep the Gan canonical-format port single-factor: do not change candidate generation, adjudication skeleton, scorer semantics, evidence policy, or split at the same time.
- The residual-slice replay should follow the cap-25 port, not replace it; otherwise slice wins may overfit the exact errors already inspected.
- ExECT S4 frequency repair is independent of Gan S0 work because ExECT frequency surfaces include qualitative co-labels, zero-rate labels, and multi-row gold that Gan normalization does not model directly.
- Gemini replay is deferred unless the paper/model-comparison story specifically needs it; it should not interrupt Qwen/full-validation confirmation work.

## What We Know Now

### Gan S0 seizure frequency

Default architecture: **temporal-candidates verify-repair**.

Taxonomy interpretation: `H2_pre_deterministic` plus `H4_deterministic_first_llm_adjudicates`.

Key evidence:

- Qwen35b promoted full-validation temporal-candidates run: `...230324Z`, 65.8% monthly accuracy, 100% evidence support.
- GPT 4.1-mini promoted full-validation temporal-candidates run: `...130933Z`, 65.1% monthly, 76.5% Purist, 84.2% Pragmatic, 99.7% schema validity, 100% evidence support.
- ReAct temporal-tools H3 slice rejected: `...173943Z`, 50% schema validity and 42.9% monthly accuracy on valid predictions.

Research interpretation (operational, not mechanism-closed): promoted arm uses precomputed temporal candidates + LLM adjudication. **Open:** LLM-only candidate ID, stage-count optimum, tool-during with alternate implementations. ReAct slice = **arm-reject** for one H3 config only.

### ExECT S1-S4 schema ladder

Hosted GPT is frozen across S1-S4. Local Qwen replication has now completed through S4 full validation.

Current anchors:

| Schema | GPT 4.1-mini | Qwen35b | Interpretation |
| --- | ---: | ---: | --- |
| S1 | 92.3% micro | 79.0% micro | Qwen lags on the narrow audited S1 policy surface. |
| S2 | 80.9% micro | 82.6% micro | Qwen matches or slightly exceeds GPT under broader scope. |
| S3 | 72.1% micro | 72.2% micro | Qwen essentially matches GPT. |
| S4 | 65.5% micro | 67.5% micro (`...160914Z`) | Qwen slightly exceeds GPT on the 11-family S4 diagnostic view. |

Research interpretation: schema breadth changes the field-family surface; ladder is not a simple learning curve. S1/S4 family probes = **arm-reject** for tested configs (repeat guardrail in negative-probe doc). **Next ExECT step:** Axis 1 stage-graph grid on S1 (after Gan Phase 2), not another single-factor prompt sweep unless Axis 3 on a winning skeleton.

### Experiment taxonomy

Completed:

- `docs/experiments/synthesis/experiment_registry.json`
- `docs/taxonomy/experiment_taxonomy_schema.md`
- typed taxonomy metadata in experiment configs
- registry validation in `src/clinical_extraction/experiments/registry_validation.py`
- `scripts/validate_experiment_taxonomy.py`
- focused tests for registry/config coverage
- taxonomy synthesis answering near-term research questions

Research interpretation: taxonomy is now part of experiment design. Avoid more broad exploratory runs that cannot isolate the varied factor.

### DSPy optimizers

Full investigation: `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md` (extends `docs/workstreams/optimizer/dspy_optimizer_vs_manual_engineering_audit_20260520.md`).

Key evidence:

- ExECT S1 bootstrap cap-25 **reject** (−5.1pp micro vs v4_10 baseline with embedded policy examples): `docs/experiments/exect/exect_s1_optimizer_gpt_cap25_v1_inspection_20260521.md`
- Gan direct cap-25 ladder: **LabeledFewShot > Bootstrap > BootstrapRS** — `docs/experiments/gan/gan_s0_few_shot_ladder_cap25_inspection_20260519.md`
- Gan GEPA **reject** (prompt bloat, label regression) — `docs/experiments/gan/gan_s0_gepa_vs_synthesis_decision_20260519.md`
- Gan synthesis bootstrap full validation was a usable reference (62.9% monthly) but verify-repair v2 beat it (65.4%)

Research interpretation: optimizer integration is sound; poor results reflect wrong failure mode, stacked few-shot confounds, and missing reference rungs — not broken wiring. Manual program engineering (verify-repair, temporal-candidates, label-policy ladders) outran compile-time search on active blockers.

**Next optimizer work:** run the **full ablation ladder** from `D1_deterministic_only` through `L0_llm_only`, schema constraint, manual policy, then DSPy compile rungs — on **validation** for rungs 0–3; **train** (`exectv2_fixed_v1:train`, 120 records) for optimizer compile rungs 4–7 only; test holdout only to confirm. See `docs/policies/dataset_splits_policy.md` and investigation doc § Proposed Full Ablation Ladder. Do not repeat bootstrap against v4_10 embedded examples without L0/L1 baselines.

### Taxonomy primitives (build-before-run)

**Workstream plan:** `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md`  
**Catalog / contract:** `docs/taxonomy/taxonomy_primitive_catalog.md`, `docs/taxonomy/taxonomy_primitive_contract.md`  
**Validation:** `uv run python scripts/validate_primitives.py --errors-only`

Core infrastructure is in place for taxonomy-governed experiments: shared candidate, normalization, and evidence contracts; typed primitive registry; Gan frequency and ExECT S1/S4 primitive packs; interleaving adapters; L1/H1/H2/H3/H4/D1 arm templates; deterministic fixture library; inspection templates. New model-backed runs should compose these primitives rather than ad hoc helper changes.

Decisions recorded: minimal H3 tool interface only (`docs/taxonomy/taxonomy_tool_interface_decision_20260520.md`); CUI/ontology primitives deferred to published benchmark reproduction (`docs/taxonomy/taxonomy_ontology_cui_scope_decision_20260520.md`). Broad ExECT sparse-family sketches (investigation, comorbidity, onset, etc.) are catalogued as `planned` metadata only.

Still blocked: Card 19 published ExECT CUI benchmark pack; Card 20 Gan Real(300)/Real(150) primitive validation (data access).

## Active Work

**Current mode:** three-axis exploration (GPT cap-25 grids first).

Use skill **`hybrid-pipeline-exploration`** for all new experiment design and inspections.

### Phase 0–1 (doctrine + inventory)

| Card | Status | Deliverable |
| --- | --- | --- |
| Pivot report + implementation plan | **Done** | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`, `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` |
| Agent skill + AGENTS.md | **Done** | `.agents/skills/hybrid-pipeline-exploration/SKILL.md` |
| Mechanism status table | **Done** | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| Retag registry notes (canonical rows) | **Done** | `decision_scope` in high-value registry `notes` — `scripts/retag_registry_decision_scope.py` |

### Phase 2 — Gan S0 Axis 1 (stage-graph grid) — **cap-25 complete**

| Card | Status | Deliverable |
| --- | --- | --- |
| Preregister `gan_s0_pipeline_stage_graph_gpt_cap25_v1` | **Done** | `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_preregistration_20260521.md` — 5 arms, deterministic candidate-source control |
| Program variants | **Done** | `temporal_candidates_single_pass` + `stage_graph_id` metadata in `gan_frequency_s0.py` |
| Config batch + cap-25 runs | **Done** | `configs/experiments/gan_s0_stage_graph_*` — runs `…T012156Z`–`…T012243Z` |
| Inspection | **Done** | `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md` — A3 hold, others reject (arm) |
| Registry rows | **Done** | `scripts/backfill_hybrid_cap25_registry.py` (10 rows) |

### Phase 3–4 — Gan Axis 2–3 — **done**

| Card | Status | Deliverable |
| --- | --- | --- |
| Stage-executor grid | **Done** | `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md` |
| Implementation sweep (presentation) | **Done** | `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md` — table/JSON/bullets 56% vs prose 52% |

### Phase 5 — Gan validation ladder + ExECT S1 stage-graph

| Card | Status | Deliverable |
| --- | --- | --- |
| Gan S0 validation ladder cap-25 | **Done** | Inspection `docs/experiments/gan/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md` — V0/V2/V6 hold; V3–V5/V7 reject |
| ExECT S1 stage-graph cap-25 | **Done** | Prereg + 5 configs + runs + inspection + registry backfill |

### Phase 7 — Qwen port + canonical-format follow-up

| Card | Status | Deliverable |
| --- | --- | --- |
| Gan Qwen g2_candidates_adjudicate cap-25 | **Done** | Inspection `docs/experiments/gan/gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_inspection_20260521.md` — reject (arm) 40% monthly vs GPT E1 52% |
| Gan canonical-format port prereg | **Done** | `docs/experiments/gan/gan_s0_canonical_format_port_gpt_cap25_v1_preregistration_20260521.md` |
| Gan canonical-format port cap-25 | **Done** | C1 hold +4pp normalized exact — inspection linked |
| Residual-slice replay tooling | **Done** | `gan_residual_slice.py`, `export_gan_exact_frequency_residual_slice.py`, `replay_gan_canonical_format_residual_slice.py` |
| Gan canonical-format residual-slice replay | **Done** | `docs/experiments/gan/gan_s0_canonical_format_residual_slice_replay_20260521.md` — null on hard queue; no cap-50 promotion |
| Gan exact-frequency slot payload prereg + scaffold | **Done** | Inspection `docs/experiments/gan/gan_s0_exact_frequency_slot_payload_gpt_cap25_v1_inspection_20260521.md` — S1 hold +8pp monthly; residual null |

### Phase 5–6 — ExECT S1 executor + optimizer (Axis 2–3)

| Card | Status | Notes |
| --- | --- | --- |
| ExECT S1 stage-executor cap-25 | **Done** | Prereg + 5 configs + runs + inspection + registry backfill |
| Optimizer automation thesis | **Done** | Axis 3 — `docs/experiments/exect/exect_s1_ladder_optimizer_automation_inspection_20260521.md`; thesis not supported (best 71.7% micro) |

### Completed batches (arm evidence — not mechanism closure)

| Batch | Inspection | Arm outcomes (not mechanism) |
| --- | --- | --- |
| Gan S0 stage-graph Axis 1 cap-25 | `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md` | A3 hold; A1/A2/A4/A5 reject (arm) |
| ExECT S1 stage-graph Axis 1 cap-25 | `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md` | S1/S4 hold (95.8%); S3/S5 reject (arm); bridge Δ +23pp |
| ExECT S1 stage-executor Axis 2 cap-25 | `docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md` | E1/E2 hold (95.8%); E3–E5 reject (arm); bridge placement null |
| Lane A GPT cap-25 (Gan + ExECT) | `docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md`, `docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md` | See mechanism status doc |
| ExECT S1 ladder rungs 0–3 | `docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md` | Decomposition reference |
| Lane Q Qwen v4_11 | `docs/experiments/exect/exect_s1_seizure_prompt_policy_qwen_v1_inspection_20260520.md` | Hold promote blocked |
| Negative probes | `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md` | Repeat guardrail only |

**No Gan runs queued.** V1 VR bundle **hold (arm)**: **65.8%** monthly — loses to F0 **68.1%** (−2.3pp), edges pre-exp VR **65.1%** (+0.7pp); **keep F0 as monthly leader** (`docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_inspection_20260521.md`; run `…T074513Z`).

**ExECT S1 optimizer pilot interpretation notes (2026-05-21):**

- Judge the optimizer arm only against the paired in-group cap-25 baseline (`exect_s1_optimizer_baseline_cap25_gpt4_1_mini`), not against older full-validation S1 anchors.
- Keep the first pilot's optimizer metric bridge-on: `exect_field_family_micro_f1` uses the same inline benchmark-bridge path as production `repair_policy=none`. Caveat any positive result as optimizer behavior under the current production bridge surface, not raw bridge-free model alignment.
- Freeze the trainset as the first 40 records from `exectv2_fixed_v1:train`; changing the train subset after seeing cap-25 results requires a new preregistered optimizer design.
- Interpret the preregistered "schema >= 95%" gate for ExECT S1 as: all 25 cap records produce Pydantic-valid `PredictionSet` / `DocumentPrediction` objects, zero missing predictions, and no material evidence-support regression versus the paired baseline. ExECT S1 does not currently expose a Gan-style `schema_valid_prediction_rate`; field-family errors remain F1 errors.

**Next optimizer workstream (post-pilot):** see `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md`. Preregister and implement the full reference ladder (D1 → L0 → L1 → policy → LabeledFewShot → Bootstrap → BootstrapRS → GEPA) on ExECT S1 dev before any further optimizer probes or test-holdout confirmation. Gan S0 can reuse the same ladder template.

| Step | Status | Blocker |
| --- | --- | --- |
| Optimizer investigation report | **Done** | — |
| ExECT S1 full-ladder preregistration | **Done** | `docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_preregistration_20260521.md` (supersedes dev draft) |
| L0 prompt + D1 arm scaffolding | **Done** | `exect_s0_s1_field_family_l0_minimal`, `l1_schema`, `deterministic_only` variant |
| Rungs 0–3 on validation | **Done** | D1 58.4% → L0 60.0% → L1 67.7% cap-25; L1+policy 92.3% full (matches frozen anchor) — `docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md` |
| Optimizer automation thesis (rungs 4a–4c) | **Done** | `docs/experiments/exect/exect_s1_ladder_optimizer_automation_inspection_20260521.md` — thesis not supported |
| Rungs 6–7 (BootstrapRS, GEPA) | **Deferred** | Only if train-demo surface alignment fixed |
| Test holdout confirmation | **Deferred** | Only for arms clearing dev + cap gates |

## Next Major Phases

### Phase 1 - Consolidate the taxonomy-governed evidence base

Outcome: a clean research memory layer that tells the story of what has been tried, which mechanisms were rejected, which anchors are frozen, and which claims are safe.

Ready cards:

- **Refresh steering docs:** remove stale next-run language, align `docs/planning/kanban_plan.md`, `docs/experiments/exect/exect_field_family_deterministic_support_map_20260520.md`, and `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md`.
- **Synthesize negative ExECT probes:** `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md` explains why S1 interleaving, H2 pre-vocab, S4 frequency pre-candidates, S4 temporality H1, and Qwen interleaving v1 did not promote.
- **Audit primitive-to-experiment coverage:** `docs/taxonomy/taxonomy_primitive_coverage_audit_20260520.md` classifies implemented and planned primitives as `promoted`, `diagnostic_only`, `rejected_for_current_arm`, `planned`, or `blocked`.

Validation: documentation links resolve; claims cite inspection docs or run IDs; no placeholder item implies a runnable experiment.

### Phase 2 - Clean factor-isolation GPT ablations

Outcome: a clean set of rapid GPT 4.1-mini comparison groups that fill or clarify the research-atlas evidence matrix without recategorizing historical bundled rows.

Current decision: run **new clean experiments** for the missing or bundled Gan S0 and ExECT S1 factors. Historical rows remain useful as motivation and priors, but they should not be treated as paper-safe single-factor evidence unless rerun under a clean comparison group.

Ready cards:

- **Gan S0 verification ablation:** direct vs verify-repair vs temporal-candidates/no-repair if feasible vs temporal-candidates + verify-repair.
- **Gan S0 evidence-policy ablation:** no evidence requirement vs model quote required vs deterministic span-check or verified quote.
- **Gan S0 prompt-policy ablation:** frozen baseline vs guardrails prompt vs temporal benchmark-policy prompt.
- **ExECT S1 prompt-policy ablation:** v4_10 vs v4_11 seizure-focused policy vs one broader benchmark-policy prompt if justified.
- **ExECT S1 optimizer pilot:** frozen prompt baseline vs optimizer-compiled variant on cap-25 before any full validation. **Complete — reject bootstrap**; see `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md` for full ladder follow-up.
- **ExECT S1 verification ablation:** single-pass vs verify-repair with fixed prompt, scorer, split, and bridge policy.
- **ExECT S1 evidence-policy ablation:** normal quote vs stricter evidence requirement vs diagnostic-only/no hard evidence policy.

Validation: each pre-registration states dataset, split, schema, model, scorer, frozen baseline, varied factor, fixed controls, primitive IDs if applicable, gate, and reject/hold/promote criteria. Registry rows must use the clean varied factor rather than `program_architecture` unless the architecture itself is the tested factor.

### Phase 3 - Reproduction and external validity

Outcome: separate local diagnostic claims from published benchmark reproduction and external-data claims.

Blocked cards:

- Published ExECTv2 reproduction remains blocked on CUI-aware all-family scoring and ontology-aligned primitives.
- Gan Real(300)/Real(150) validation remains blocked on data access.

Validation: use `dataset-audit-first` and `gold-scorer-integrity`; do not compare published benchmark claims with local field-family diagnostics without caveats.

### Phase 4 - Scale-up and Qwen confirmation

Outcome: port only useful GPT-discovered factor-isolation results to Qwen and reopen broader studies only after the narrow mechanism evidence is coherent.

Deferred cards:

- Broad ExECT architecture matrix.
- Ad hoc DSPy optimizer probes (bootstrap/GEPA) without the full reference ladder on dev.
- Additional local/closed model comparisons beyond focused Qwen confirmation.

Validation: each scale-up varies one explicit factor or is documented as an interaction study.

## Recently Completed (2026-05-21)

- **DSPy optimizer investigation:** `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md` — integration sound; historical rejects justified; defines full D1→L0→optimizer ladder on dev before test holdout.
- **ExECT S1 optimizer cap-25 (2 runs):** `docs/experiments/exect/exect_s1_optimizer_gpt_cap25_v1_inspection_20260521.md` — baseline **hold** (95.8% micro); bootstrap **reject** (−5.1pp micro, −9.2pp seizure); runs `…000602Z` / `…000608Z`.
- **ExECT S1 GPT factor-isolation cap-25 (3 groups, 7 runs):** `docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md` — prompt v4_11 **reject** on GPT; verify-repair **reject** (−9.4pp micro); evidence standard **hold**, soft **reject**. Runs `…232829Z`–`…233326Z`.
- **Lane A Gan GPT cap-25 (9 runs):** `docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md` — verification null (44% all arms); evidence reject optional/span-check; prompt hold guardrails +4pp / reject synthesis.
- **Lane A clean factor-isolation preregistrations (7 groups):** Gan + ExECT S1 groups preregistered; ExECT optimizer runner support now ready for cap-25 baseline + bootstrap execution.

## Recently Completed (2026-05-20)

- **v4_11 seizure prompt-policy Qwen v1 full:** `exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama_20260520T231850Z` — seizure F1 **74.2%** (+18.5pp vs `…210722Z`), micro **84.3%**; **Hold (promote blocked)** — inspection `docs/experiments/exect/exect_s1_seizure_prompt_policy_qwen_v1_inspection_20260520.md`, error read `runs/exect_s1_seizure_prompt_policy_qwen_v1_error_read.json`.
- **v4_11 seizure prompt-policy implementation:** `docs/experiments/exect/exect_s0_label_policy_v4_11_implementation.md` — prompt-only addendum + 7 policy examples; cap-25 GPT/Qwen gates passed (Qwen cap-25 amended).
- **Qwen S1 seizure-gap error analysis:** `docs/experiments/exect/exect_qwen_s1_seizure_gap_error_analysis_20260520.md` — 19 Qwen vs 6 GPT mismatch docs; dominant Qwen-only modes are inflection (14 atoms), secondary-policy (14), absence/myoclonic overcall (6); **recommend prompt-policy preregistration**; script `scripts/analyze_exect_qwen_s1_seizure_gap_error_read.py`.
- **Primitive catalog aligned with coverage audit:** `docs/taxonomy/taxonomy_primitive_catalog.md` now separates registry implementation status from evidence status; Gan S0 temporal-candidates plus verify-repair are the only promoted deterministic primitive path, while ExECT implemented primitives are marked diagnostic, planned, blocked, or rejected for current arm shapes.
- **Qwen S1 seizure-gap error analysis preregistered:** `docs/experiments/exect/exect_qwen_s1_seizure_gap_error_analysis_preregistration_20260520.md` selects a no-model Phase 2 first step using frozen Qwen/GPT H1 artifacts before any new ExECT run.
- **S1 interleaving Qwen v1 complete:** cap-25 + full — L1 raw 66.2% / H1 post 79.0% micro full (`…210719Z` / `…210722Z`); inspection `docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md` — **reject port**; bridge Δ +12.8pp full (GPT v2 +23.7pp); H1 **null** vs Qwen production anchor; seizure gap −34.8pp vs GPT H1.
- **S1 seizure pre-vocab slice GPT complete:** L1 91.5% / H2 83.3% seizure_type F1 (`…205806Z` / `…205814Z`); inspection `docs/experiments/exect/exect_s1_seizure_pre_vocab_slice_gpt_inspection_20260520.md` — **reject** H2 (−8.2pp); program `exect_s0_s1_field_family_seizure_pre_vocab_single_pass` + configs + fixture + tests.
- **S4 medication temporality planned/taper error-read:** `docs/experiments/exect/exect_s4_temporality_planned_taper_error_read_20260520.md` — 19 H1-new FNs analyzed; 4/19 planned/taper slice, 17/19 unknown-drop on dose-only ASM evidence; **no taper retune warranted**
- **S4 medication temporality full validation GPT complete:** L1 46.4% / H1 56.5% MT precision (`…204207Z` / `…204216Z`); inspection `docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md` — **reject H1** (+10.1pp precision but −6.6pp MT F1 recall collapse on 40 records).
- **Paper-ready registry matrix export:** `docs/experiments/synthesis/experiment_registry_matrix_20260520.md` (41 curated rows); regenerate via `uv run python scripts/export_experiment_registry_matrix.py`.
- **S4 medication temporality cap-25 GPT complete:** L1 46.8% / H1 61.3% medication_temporality precision (`…203755Z` / `…203803Z`); cap-25 gate passed but did not generalize to full validation.
- **Taxonomy primitives workstream:** core phase complete — registry, catalog, adapters, arm templates, fixtures, `scripts/validate_primitives.py`; see `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md`.
- **S4 frequency pre-candidate cap-25 GPT complete:** L1 49.1% / H2 47.1% seizure_frequency F1 (`…191914Z` / `…191951Z`); inspection `docs/experiments/exect/exect_s4_frequency_deterministic_gpt_inspection_20260520.md` — **reject** H2 (−2.0pp); program `exect_s4_field_family_frequency_pre_vocab_single_pass` + configs + preregistration.
- **Medication pre-vocab slice GPT complete:** L1 98.3% / H2 95.1% medication F1 (`…191336Z` / `…191345Z`); inspection `docs/experiments/exect/exect_s1_medication_pre_vocab_slice_gpt_inspection_20260520.md` — **reject** H2 (−3.2pp medication F1); registry rows added.
- **Interleaving v2 registry rows:** four rows under `exect_s1_interleaving_gpt_validation_v2` (`docs/experiments/synthesis/experiment_registry.json`).
- **S1 interleaving v2 GPT complete:** L1 raw 68.6% / H1 post 92.3% full micro (`…190804Z` / `…190807Z`); inspection `docs/experiments/exect/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md` — bridges contribute ~24pp micro vs raw.
- **Medication-only H2 slice scaffold:** `exect_s0_s1_field_family_medication_pre_vocab_single_pass`, slice fixture, L1/H2 slice configs, tests (`exect_s1_medication_pre_vocab_slice_gpt_v1`).
- **Bridge-free S1 repair policy:** `REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES` in `exect_s0_s1.py`; interleaving v2 configs `exect_s1_interleaving_l1_raw_no_bridges_{cap25,full}_gpt4_1_mini.json`.
- **ExECT field-family deterministic support map:** `docs/experiments/exect/exect_field_family_deterministic_support_map_20260520.md` — S1–S4 per-family GPT/Qwen anchors, deterministic inventory, interleaving lessons, ranked experiment queue (bridge-free baseline → family-isolated probes).
- **S1 interleaving GPT phase 1 complete:** H1 cap-25/full + H2 cap-25/full; inspection `docs/experiments/exect/exect_s1_interleaving_gpt_validation_v1_inspection_20260520.md`; registry rows under `exect_s1_interleaving_gpt_validation_v1`. H1 **hold (null)** vs L1; H2 **reject** (−4.8pp full micro); H3 deferred.
- S1 interleaving H1/H2 program paths + cap-25/full configs (`src/clinical_extraction/programs/exect_s0_s1.py`, `scripts/run_experiment.py`)
- ExECT Qwen S4 full inspection: `docs/experiments/exect/exect_s4_validation_full_qwen35b_ollama_inspection_20260520.md` (`…160914Z`, 67.5% micro, +2.0pp vs GPT v1.2)
- Registry row: `exect_s4_validation_full_qwen35b_ollama` (cap-25 row `…133930Z` remains gate-only)
- S1 interleaving pre-registration + v2 configs (see v2 inspection doc)
- Gan Qwen H1 full comparator: **deferred** — slice evidence sufficient; see **Current Decisions**

## Ready After Consolidation

### Lane A clean GPT factor-isolation queue

Lane A factor-isolation cap-25 groups are **complete** (see Lane A table above). Full reference ladder rungs **0–3 complete** on validation (`exect_s1_full_ladder_gpt_validation_v1`): policy+bridges account for ~25pp over schema-only L1; optimizer bootstrap already reject. **Train** reserved for optional rungs 4–7. See `docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md` and `docs/policies/dataset_splits_policy.md`.

### Optional Gan model-interaction robustness slice

Only run this if the Gan narrative needs model-interaction evidence after the clean GPT factor groups. Keep the same records, scorer, schema, and temporal-candidates architecture across GPT and Qwen.

## Blocked Or Deferred

### Published ExECTv2 benchmark reproduction

Blocked on CUI-aware all-family scoring. Current ExECT numbers are local field-family diagnostics, not published Table 1 reproduction.

Use `dataset-audit-first` and `gold-scorer-integrity` before touching this.

### Published Gan real-set reproduction

Blocked on access to Gan Real(300)/Real(150) style data. Current Gan claims are fixed synthetic validation claims.

### Broad ExECT architecture ablation

Deferred. S1 interleaving v1/v2 and S4 family-isolated probes are complete; reopen only after a promotable single-factor arm exists or for an explicit pre-registered architecture matrix.

### Optimizer scale-up

ExECT S1 cap-25 bootstrap pilot is **complete — reject**. Do not scale bootstrap or GEPA without the full reference ladder (`docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md`): D1 deterministic baseline → L0 bare LLM → L1 schema → manual policy → DSPy compile rungs, explored on **dev** first; test holdout only to confirm. Optimizers remain explicit ablation factors, not silent prompt tuning.

## Current Decisions

**Reading guide (post-pivot):** Rows marked **Reject** below are **reject (arm)** unless `decision_scope: mechanism` is stated in the linked inspection. Operational defaults are **not** mechanism-closed. See `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`.

| Decision | Current position |
| --- | --- |
| Research doctrine | **Three-axis exploration** — `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` |
| Decision language | **arm / operational / mechanism** — skill `hybrid-pipeline-exploration` |
| Experiment loop | Explore primarily on GPT 4.1-mini; reserve Qwen35b for selected high-value focus experiments |
| Gan default architecture | Temporal-candidates verify-repair (`H2` + `H4`) |
| Gan ReAct H3 | **arm-reject** (one tool surface); mechanism **open** — not default |
| ExECT S1 interleaving Qwen v1 | **Complete — reject port** — full bridge Δ +12.8pp micro; H1 null vs Qwen anchor; does not close GPT seizure gap |
| ExECT next experiment | **Clean factor-isolation queue** — prompt policy, optimizer pilot, verification, and evidence ablations on GPT 4.1-mini before Qwen confirmation |
| Lane A policy | **New clean experiments only** — do not recategorize old bundled rows as the clean evidence base |
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
| ExECT S1 GPT prompt policy v4_11 (cap-25) | **Reject on GPT** — 93.9% seizure F1 vs 95.4% v4_10 (−1.5pp); Qwen port remains separate |
| ExECT S1 GPT verify-repair (cap-25) | **Reject** — 86.4% micro vs 95.8% single-pass (−9.4pp) |
| ExECT S1 GPT evidence policy (cap-25) | **Hold standard** — strict null (+0.6pp micro); soft reject (−3.1pp seizure, −4.4pp evidence) |
| ExECT S1 GPT optimizer bootstrap (cap-25) | **Reject** — 90.7% micro vs 95.8% baseline (−5.1pp); seizure −9.2pp; no full validation |
| ExECT S1 GPT optimizer baseline (cap-25) | **Hold (in-group anchor)** — 95.8% micro; matches clean v4_10 cap-25 reference |
| DSPy optimizer strategy | **Full reference ladder next** — see `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md`; dev-first, no ad hoc bootstrap vs embedded policy |
| ExECT Qwen S4 full | **Hold** as local ladder anchor (`…160914Z`); +2.0pp pooled micro vs GPT but weaker seizure/diagnosis per-family |
| ExECT Qwen S1 v4_11 full (seizure prompt-policy) | **Hold (promote blocked)** — seizure +18.5pp vs `…210722Z`; diagnosis −5.1pp; mismatch docs 14; Qwen prod stays v4_10 |
| ExECT S1 full-ladder GPT validation v1 | **Ready to run** — validation cap-25 (D1/L0/L1) + full 40 (L1+policy); dev for optimizer compile only |

## Recommended Next Pull

1. ~~**Cap-50 prose+expanded-builders**~~ **Done** — confirm +6pp (`docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_cap50_v1_inspection_20260521.md`).
2. ~~**ExECT S4 frequency structured slots (item 23)**~~ **Done** — S2 null vs R0; inspection `docs/experiments/exect/exect_s4_frequency_structured_slots_gpt_cap25_v1_inspection_20260521.md`.
3. ~~**Sparse-family surface policy memo (item 24 gate)**~~ **Done** — `docs/experiments/exect/exect_s4_sparse_family_surface_policy_20260521.md`.
4. ~~**ExECT S1–S3 P0 fixtures + cap-25 grids**~~ **Done** — fixtures green; comorbidity bridge null on cap-25 (`exect_s2_comorbidity_surface_bridge_gpt_cap25_v1_inspection_20260521.md`); I0 investigation +5.6pp (`exect_ladder_investigation_guard_gpt_cap25_v1_inspection_20260521.md`); S3 cause bridge K0+K1 +20pp cause F1 (`exect_s3_epilepsy_cause_bridge_gpt_cap25_v1_inspection_20260521.md`).
5. ~~**Next (ExECT S4, no-model):** wire K0+K1 cause bridge into S4 artifact recovery path~~ **Done** — `exect_s4_field_family_cause_bridge_k0_k1_single_pass`.
6. ~~**Next (ExECT S1–S3):** S3 cause-bridge full-validation prereg on sparse-family qualitative queue~~ **Done** — prereg + 3-doc residual replay (null) — `exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1_preregistration_20260521.md`.
7. ~~**Next (ExECT S1–S3):** run S3 cause-bridge full validation (L1 vs K0+K1)~~ **Done** — K0+K1 +11.1pp cause F1; hold operational candidate — `exect_s3_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md`.
8. ~~**Research hygiene parallel slot:** audit run metadata for validation/repair outcomes (Literature Card 5)~~ **Done** — `docs/experiments/synthesis/run_metadata_validation_repair_audit_20260521.md`.
9. **New ExECT S4 frequency repair variant** only if revisiting — do not rerun R1 or S2 unchanged.
10. **Gemini replay deferred:** only run if a model-comparison narrative requires current S1/S4 Gemini evidence.

## Operational Defaults vs Open Mechanisms

| Operational default (freeze for runs) | Open mechanism class (must grid-search) |
| --- | --- |
| Gan temporal-candidates + VR v1.1 | Optimal stage count; LLM vs det candidate generation |
| ExECT S1 GPT v4_10 + inline bridges | Optimal S1 stage graph; bridge placement; pre strategies (non-section-aware) |
| ExECT S2–S4 GPT frozen ladder | Per-family det support on broad schema |

Full table: `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`

## Parallelization

| Safe in parallel | Single-threaded |
| --- | --- |
| Gan verification/evidence/prompt-policy cap-25 config drafts | Changing scorer semantics or benchmark label policy |
| ExECT full-ladder preregistration + L0/D1 scaffolding | ExECT optimizer runner changes (compile path — done) |
| Gan canonical-format prereg + ExECT S4 frequency-repair prereg | Implementing shared frequency normalizers or scorers |
| ExECT S4 frequency-repair prereg | Gan residual-mechanism primitive design |
| Ladder rungs 0–3 dev configs (after L0/D1 impl) | Qwen full validation runs |
| Research atlas and matrix regeneration after metadata edits | Qwen full validation runs |
| Gan prompt-policy port implementation (synthesis/guardrails onto temporal+VR) | Published benchmark reproduction design |

## Long-Term Research Arc

1. **Search** hybrid pipelines on Axes 1→2→3 (GPT cap-25 grids) per `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`.
2. **Confirm** only cap-25 winners on slice/full validation; **Qwen** ports winning cells only.
3. Keep taxonomy registry and `decision_scope` discipline; mechanism status doc is the open/closed index.
4. Gan leads Axis 1–2 (temporal frequency); ExECT S1 follows with bridge caveats; S2–S4 after S1 skeleton exists.
5. Separate local diagnostic validation from published benchmark reproduction (CUI ExECT, Gan real-set).
6. Treat Lane A, ladder, and negative probes as **arm libraries** — not permission to stop exploring placement.
