# Taxonomy Primitives Workstream Plan

Date: 2026-05-20  
Status: Core infrastructure complete; handoff/audit phase ready. Cards 19–20 remain blocked on external dependencies.  
Related: `docs/kanban_plan.md`, `docs/experiment_taxonomy_schema.md`, `docs/experiment_taxonomy_research_synthesis_20260520.md`, `docs/hybrid_component_taxonomy_decision_20260520.md`, `docs/exect_field_family_deterministic_support_map_20260520.md`

## Purpose

The project has moved into taxonomy-governed experimentation. The next useful infrastructure phase is to build the reusable primitives that make those experiments coherent before running a broad new wave of model-backed studies.

The goal is not to lock the research design prematurely. It is to make the common pieces explicit, typed, testable, and comparable so that later experiments vary the intended factor rather than quietly changing helper code, bridge behavior, evidence policy, or prompt surfaces at the same time.

This workstream should produce a standardized component library for:

- deterministic candidate generation
- controlled vocabularies and label-policy surfaces
- normalization and benchmark bridges
- evidence span and quote support checks
- verifier and repair policies
- tool-facing helper interfaces
- fixture and slice definitions
- experiment config templates
- registry and inspection/reporting conventions

Model-backed execution can now happen later under fixed controls, with the primitives inspected, unit-tested, and documented. The next task is not to add more primitives by default; it is to decide which implemented primitives are promoted, diagnostic-only, rejected for the current arm, planned, or blocked.

## Guiding Principles

- Build primitives around taxonomy dimensions: `hybrid_balance_class`, `interleaving_positions`, `knowledge_sources`, `control_modes`, `normalization_strategy`, `verification_strategy`, and `evidence_strategy`.
- Keep dataset policy explicit. Gan and ExECT share architectural ideas, but their gold-label semantics differ.
- Preserve raw, normalized, benchmark-facing, and evidence-supported values separately when they diverge.
- Make every primitive callable in a dry-run or deterministic test without an LLM.
- Prefer family-specific primitives over broad full-note interventions unless the experiment is explicitly testing broad context.
- Treat pre, during, tool-during, post, and eval-only use of the same knowledge source as different primitives or different adapters around one primitive.
- Do not promote a primitive merely because it exists. Promotion still requires model-backed comparison groups and inspection documents.

## Definition Of Done

This phase is complete when the repository has:

- A documented primitive catalog mapping each primitive to taxonomy fields, datasets, field families, and intended comparison groups.
- Shared interfaces for candidates, normalization, evidence support, repair decisions, and tool wrappers.
- Deterministic tests for each primitive using fixtures or audited examples.
- Config templates that compose primitives into L1/H1/H2/H3/H4 experiment arms without duplicating taxonomy metadata.
- Inspection templates that report primitive use, scorer mode, normalization rules, evidence rules, and caveats.
- A small set of no-model validation commands that prove the primitives and registry metadata are internally consistent (`uv run python scripts/validate_primitives.py --errors-only`).

## Progress Notes

2026-05-20 first pull:

- Card 1 initial primitive contract implemented in `src/clinical_extraction/primitives.py`.
- Card 16 registry location decided in `docs/taxonomy_primitive_contract.md`: typed Python metadata is the source of truth; Markdown remains the inspection surface.
- Card 2 seed catalog created in `docs/taxonomy_primitive_catalog.md`.
- Focused no-model validation: `uv run pytest tests/test_primitive_contracts.py -q`.

2026-05-20 second pull:

- Cards 3, 4, and 5 initial shared payload contracts implemented in `src/clinical_extraction/primitives.py`.
- Added `PrimitiveCandidate`, `NormalizationResult`, `EvidenceSupportResult`, and `check_evidence_support`.
- Candidate tests now cover Gan frequency, ExECT medication, and ExECT seizure-frequency examples.
- Normalization tests now distinguish benchmark bridge and scorer-only semantics.
- Evidence tests now distinguish exact substring support, normalized-interpretation support, unsupported quote, and no-reference cases.
- Focused no-model validation: `uv run pytest tests/test_primitive_contracts.py -q`.

2026-05-20 third pull:

- Card 6 initial Gan frequency primitive pack implemented in `src/clinical_extraction/gan/primitives.py`.
- Added shared-contract adapters for Gan temporal candidates, Gan label-policy normalization, and Gan evidence guard behavior.
- Registered `gan.frequency.label_policy_bridge.v1` and `gan.frequency.evidence_guard.v1` in the typed primitive registry.
- Gan audit assumptions preserved: `seizure_frequency_number[0]` remains gold, `unknown` and `no seizure frequency reference` remain distinct, and elided evidence is treated as ordered multi-span support rather than exact quote support.
- Focused no-model validation: `uv run pytest tests/test_gan_frequency_primitives.py -q`; `uv run pytest tests/test_primitive_contracts.py -q`; `uv run pytest tests/test_gan_temporal_candidates.py tests/test_gan_frequency.py tests/test_gan_scoring.py -q`.

2026-05-20 fourth pull:

- Card 7 initial ExECT medication primitive pack implemented in `src/clinical_extraction/exect/primitives.py`.
- Added note-anchored Rx candidate payloads, ExECT medication benchmark bridge behavior, and cue-based medication temporality classification.
- Registered `exect.medication.rx_candidates.v1`, `exect.medication.benchmark_bridge.v1`, and `exect.medication_temporality.post_classifier.v1` in the typed primitive registry.
- ExECT audit assumptions preserved: MarkupPrescriptions has no temporality column, planned/previous medications are not S1 current prescription outputs, and the rejected broad S1 pre-vocabulary approach remains rejected.
- Focused no-model validation: `uv run pytest tests/test_exect_medication_primitives.py -q`.

2026-05-20 seventh pull:

- Card 10 initial ExECT S4 frequency primitive pack implemented in `src/clinical_extraction/exect/primitives.py`.
- Added shared-contract adapters for note-anchored rate candidates, Gan temporal filtering to ExECT templates, and benchmark-facing frequency bridge behavior.
- Registered `exect.frequency.rate_candidates.v1` and `exect.frequency.benchmark_bridge.v1` in the typed primitive registry.
- Refactored `src/clinical_extraction/programs/exect_s4.py` to consume the primitive pack while preserving program-facing aliases.
- ExECT audit assumptions preserved: MarkupSeizureFrequency templates remain gold; Gan monthly normalization and unknown/no-reference classes do not transfer; cap-25 H2 pre-vocab rejection remains documented.
- Focused no-model validation: `uv run pytest tests/test_exect_frequency_primitives.py -q`; `uv run pytest tests/test_exect_s4_program.py tests/test_primitive_contracts.py -q`.

2026-05-20 tenth pull:

- Card 14 initial primitive fixture library implemented in `data/fixtures/primitive_cases.json` and `src/clinical_extraction/fixtures/primitive_cases.py`.
- Added 18 deterministic cases across shared evidence, Gan frequency, and ExECT medication/diagnosis/seizure-type/frequency primitives.
- Registered `shared.fixtures.primitive_cases.v1` in the typed primitive registry.
- Cases cover positive, negative, ambiguous, absent, historical, planned, and unsupported-evidence failure modes.
- Focused no-model validation: `uv run pytest tests/test_primitive_fixture_library.py -q`; `uv run pytest tests/test_primitive_contracts.py tests/test_gan_frequency_primitives.py tests/test_exect_medication_primitives.py tests/test_exect_frequency_primitives.py -q`.

2026-05-20 ninth pull:

- Card 13 initial experiment arm templates implemented in `src/clinical_extraction/experiments/arm_templates.py`.
- Added L1/H1/H2/H3/H4/D1 taxonomy defaults, comparison-group builders, primitive compatibility validation, default control presets, and `build_experiment_arm_config`.
- Card 15 initial inspection templates implemented in `docs/templates/primitive_inspection_template.md`, `docs/templates/experiment_decision_template.md`, and `src/clinical_extraction/experiments/inspection_templates.py`.
- Focused no-model validation: `uv run pytest tests/test_experiment_arm_templates.py tests/test_inspection_templates.py -q`; `uv run pytest tests/test_experiment_configs.py tests/test_primitive_contracts.py -q`; `uv run python scripts/validate_experiment_taxonomy.py --errors-only`.

2026-05-20 eighth pull:

- Card 12 initial interleaving adapter layer implemented in `src/clinical_extraction/interleaving_adapters.py`.
- Added position-specific surfaces for pre injection, during prompt rules, tool-during callable output, post processing, and eval-only diagnostics.
- Seeded bindings for Gan temporal candidates, Gan label-policy bridge, Gan evidence guard, and ExECT medication candidates/bridge.
- No-model tests prove the same primitive core payload can be rendered at different taxonomy positions without changing underlying deterministic logic.
- Focused no-model validation: `uv run pytest tests/test_interleaving_adapters.py -q`; `uv run pytest tests/test_primitive_contracts.py tests/test_gan_frequency_primitives.py tests/test_exect_medication_primitives.py -q`.

2026-05-20 fifth pull:

- Card 8 initial ExECT seizure-type benchmark bridge implemented in `src/clinical_extraction/exect/primitives.py`.
- Added deterministic bridge behavior for granular focal surfaces, fused temporal-lobe and secondary-generalisation phrases, rejected jerk/absence descriptors, focal-to-bilateral convulsive repair, and secondary-token co-listing.
- Registered `exect.seizure_type.benchmark_bridge.v1` in the typed primitive registry.
- ExECT audit assumptions preserved: seizure-type policy is based on audited Diagnosis/JSON seizure-type surfaces and explicitly does not use MarkupSeizureFrequency spans as seizure-type evidence.
- Focused no-model validation: `uv run pytest tests/test_exect_seizure_type_primitives.py -q`; `uv run pytest tests/test_primitive_contracts.py -q`; `uv run pytest tests/test_exect_medication_primitives.py tests/test_exect_seizure_type_primitives.py tests/test_exect_s0_s1_program.py -q`.

2026-05-20 sixth pull:

- Card 9 initial ExECT diagnosis benchmark bridge implemented in `src/clinical_extraction/exect/primitives.py`.
- Added deterministic bridge behavior for uncertainty stripping, audited specificity collapse, note-gated co-list augmentation, symptomatic structural focal restoration, on-awakening surface repair, seizure-descriptor header suppression, empty-list header recovery, and explicit JSON diagnosis-row certainty policy.
- Registered `exect.diagnosis.benchmark_bridge.v1` in the typed primitive registry.
- ExECT audit assumptions preserved: Diagnosis JSON rows remain the policy source, `Certainty >= 4` stays explicit, single seizure events do not become established epilepsy diagnoses, and seizure-type evidence does not create diagnosis subtype labels.
- Focused no-model validation: `uv run pytest tests/test_exect_diagnosis_primitives.py -q`; `uv run pytest tests/test_primitive_contracts.py -q`; `uv run pytest tests/test_exect_medication_primitives.py tests/test_exect_seizure_type_primitives.py tests/test_exect_s0_s1_program.py -q`.

2026-05-20 eleventh pull:

- Card 11 broad ExECT family primitive backlog sketched in `src/clinical_extraction/exect/family_backlog.py` and `docs/taxonomy_primitive_catalog.md`.
- Added 12 planned metadata records for investigation, comorbidity, birth/development, onset, cause, when diagnosed, driving, social history, pregnancy, family history, and section spans.
- Card 17 tool-interface boundary decision recorded in `docs/taxonomy_tool_interface_decision_20260520.md`: minimal adapter-level H3 support only; no broad tool-wrapper framework.
- Card 18 ontology/CUI scope decision recorded in `docs/taxonomy_ontology_cui_scope_decision_20260520.md`: defer CUI-aware primitives to benchmark-reproduction phase; CUIPhrase bridges remain string-surface canonicalization.
- Added consolidated no-model validation in `scripts/validate_primitives.py` and `src/clinical_extraction/experiments/primitive_registry_validation.py`.
- Registered deferred catalog primitives (`gan.frequency.verify_repair_policy.v1`, `gan.frequency.temporal_tool.v1`, `shared.evidence.verified_quote.v1`, `exect.ontology.cui_alignment.v1`, `gan.frequency.real_set_validation.v1`).
- Fixed `shared.evidence.substring_support.v1` registry status to `implemented`.
- Focused no-model validation: `uv run python scripts/validate_primitives.py --errors-only`; `uv run pytest tests/test_primitive_registry_validation.py tests/test_primitive_contracts.py -q`.

## Board

### Ready

#### Card 23 - Audit Primitive Coverage Against Closed Experiments

Outcome: A compact classification of implemented primitives as `promoted`, `diagnostic_only`, `rejected_for_current_arm`, `planned`, or `blocked`, tied to the inspection docs and comparison groups that justify the status.

Dependencies: Cards 1-18 and 22  
Parallelizable: yes  
Owner: unassigned  
Validation: `uv run python scripts/validate_primitives.py --errors-only`; review against `docs/experiment_registry.json`, `docs/exect_field_family_deterministic_support_map_20260520.md`, and the closed ExECT inspection docs.  
Notes: This is a documentation/research-memory card. Do not change primitive behavior unless the audit finds a concrete mismatch.

#### Card 24 - Align Primitive Catalog With Next-Phase Kanban

Outcome: `docs/taxonomy_primitive_catalog.md` clearly separates implemented primitives that are reusable infrastructure from primitives that should not be used to justify rerunning rejected H2/H1 arms.

Dependencies: Card 23  
Parallelizable: after Card 23  
Owner: unassigned  
Validation: Catalog rows cite intended experiments, current status, and caveats; no row implies promotion from existence alone.  
Notes: Especially important for ExECT medication, seizure-type, frequency, and medication-temporality primitives, where implemented primitives supported rejected model-backed arms.

### Backlog

#### Card 25 - Design Next ExECT Mechanism Preregistration

Outcome: A preregistration for one new ExECT mechanism, or an explicit no-run decision, using primitive IDs and taxonomy arm templates.

Dependencies: Card 23 and `docs/kanban_plan.md` Phase 2 decision  
Parallelizable: no  
Owner: unassigned  
Validation: Preregistration states dataset, split, schema, model, scorer mode, baseline, varied factor, primitive IDs, run scope, gate, and reject/hold/promote criteria.  
Notes: Candidate directions are Qwen seizure-gap diagnosis, S4 frequency mechanism redesign, or S4 medication temporality dose-only fallback. Do not use this card for S1 post-bridge reruns or broad H2 pre-vocab reruns.

### Questions

- Which implemented primitives should be described as reusable infrastructure versus experimentally rejected interventions?
- Is the next ExECT step a new model-backed hypothesis or a synthesis pause before benchmark reproduction work?
- Should Qwen seizure-gap work begin as error analysis only, or as a preregistered prompt/model-policy intervention?

### Blocked

#### Card 19 - Published ExECT Benchmark Primitive Pack

Outcome: CUI-aware all-family scorer and ontology-aligned primitives for published ExECTv2 reproduction.

Dependencies: Card 18 and benchmark-scorer design work  
Parallelizable: no  
Owner: unassigned  
Validation: Must use `dataset-audit-first` and `gold-scorer-integrity`; requires scorer tests against benchmark semantics.  
Notes: Blocked because current ExECT numbers are local field-family diagnostics, not published Table 1 reproduction.

#### Card 20 - Gan Real-Set Primitive Validation

Outcome: Validate Gan primitives on Real(300)/Real(150)-style data.

Dependencies: data access  
Parallelizable: no  
Owner: unassigned  
Validation: Reproduction-compatible run/inspection docs.  
Notes: Blocked on access to the real-set data.

### Review

No cards yet.

### Done

#### Card 1 - Define Primitive Contract Schema

Outcome: A short design doc and typed data model for primitive metadata: primitive ID, dataset, field family, knowledge source, interleaving position, control mode, input contract, output contract, caveats, and compatible experiment arms.

Dependencies: none  
Parallelizable: no  
Owner: project  
Validation: `uv run pytest tests/test_primitive_contracts.py -q`.  
Notes: Implemented in `src/clinical_extraction/primitives.py`; design summarized in `docs/taxonomy_primitive_contract.md`.

#### Card 2 - Create Primitive Catalog Document

Outcome: `docs/taxonomy_primitive_catalog.md` listing current and planned primitives across Gan and ExECT, grouped by clinical operation and taxonomy position.

Dependencies: Card 1  
Parallelizable: after Card 1  
Owner: project  
Validation: Catalog rows include dataset, family, interleaving position, control mode, current implementation status, intended experiments, and caveats.  
Notes: Seeded from the ExECT support map and Gan temporal-candidates results.

#### Card 3 - Standardize Candidate Object Model

Outcome: Shared candidate representation for deterministic hints such as temporal candidates, medication candidates, label-policy candidates, section spans, and evidence spans.

Dependencies: Card 1  
Parallelizable: after Card 1  
Owner: project  
Validation: `uv run pytest tests/test_primitive_contracts.py -q`.  
Notes: Initial payload model only; dataset-specific packs still need to adopt it.

#### Card 4 - Standardize Normalization Result Model

Outcome: Shared representation for normalization outputs, including raw value, canonical value, benchmark-facing value, clinical caveat, transformation rule, and whether the transformation is prediction-affecting or scorer-only.

Dependencies: Card 1  
Parallelizable: after Card 1  
Owner: project  
Validation: `uv run pytest tests/test_primitive_contracts.py -q`.  
Notes: Initial payload model only; diagnosis and seizure-type bridge examples remain for later primitive packs.

#### Card 5 - Standardize Evidence Support Model

Outcome: Shared evidence support representation for model quotes, deterministic span matches, injected evidence candidates, verified quotes, and unsupported evidence flags.

Dependencies: Card 1  
Parallelizable: after Card 1  
Owner: project  
Validation: `uv run pytest tests/test_primitive_contracts.py -q`.  
Notes: Initial support classifier is exact-substring based and intentionally conservative.

#### Card 16 - Decide Primitive Registry Location

Outcome: Decision on whether primitive metadata lives in JSON under `docs/`, typed Python metadata under `src/`, or both with one generated from the other.

Dependencies: Card 1  
Parallelizable: no  
Owner: project  
Validation: Decision note in `docs/taxonomy_primitive_contract.md`.  
Notes: Typed Python metadata is the source of truth; Markdown remains the inspection surface.

#### Card 21 - Establish Experiment Taxonomy

Outcome: Experiment registry, schema document, config taxonomy metadata, validation script, and focused tests exist.

Dependencies: none  
Parallelizable: complete  
Owner: project  
Validation: `uv run python scripts/validate_experiment_taxonomy.py --errors-only`; `uv run pytest tests/test_experiment_registry_validation.py -q` previously passed.  
Notes: This plan builds on that completed taxonomy infrastructure.

#### Card 6 - Gan Frequency Primitive Pack

Outcome: Gan-specific temporal/frequency primitive pack covering temporal candidate generation, current-window policy, unknown versus no-reference distinction, and evidence guard behavior.

Dependencies: Cards 3 and 5
Parallelizable: after shared candidate and evidence models
Owner: project
Validation: `uv run pytest tests/test_gan_frequency_primitives.py -q`; `uv run pytest tests/test_gan_temporal_candidates.py tests/test_gan_frequency.py tests/test_gan_scoring.py -q`.
Notes: Implemented in `src/clinical_extraction/gan/primitives.py`; typed registry entries added for `gan.frequency.label_policy_bridge.v1` and `gan.frequency.evidence_guard.v1`. Monthly normalization remains Gan-specific and separate from ExECT frequency templates.

#### Card 7 - ExECT Medication Primitive Pack

Outcome: Medication candidate, brand/generic, ASM/non-ASM, benchmark prescription, and temporality helper primitives for S1 and S4.

Dependencies: Cards 3 and 4
Parallelizable: after shared candidate and normalization models
Owner: project
Validation: `uv run pytest tests/test_exect_medication_primitives.py -q`.
Notes: Implemented in `src/clinical_extraction/exect/primitives.py`; typed registry entries added for `exect.medication.rx_candidates.v1`, `exect.medication.benchmark_bridge.v1`, and `exect.medication_temporality.post_classifier.v1`. Existing H2 medication pre-vocab remains rejected; this pack supports post-classifier and narrow candidate experiments, not broad S1 pre-vocab promotion.

#### Card 8 - ExECT Seizure-Type Primitive Pack

Outcome: Seizure-type surface, coarsening, fused-phrase split, secondary-token handling, and benchmark-policy bridge primitives.

Dependencies: Cards 3 and 4
Parallelizable: after shared candidate and normalization models
Owner: project
Validation: `uv run pytest tests/test_exect_seizure_type_primitives.py -q`; `uv run pytest tests/test_exect_s0_s1_program.py -q`.
Notes: Implemented in `src/clinical_extraction/exect/primitives.py`; typed registry entry added for `exect.seizure_type.benchmark_bridge.v1`. Tests include Qwen-style granular focal failure examples, fused phrase splits, secondary-token co-listing, and prediction-affecting versus scorer-only bridge semantics. MarkupSeizureFrequency remains excluded as seizure-type evidence.

#### Card 9 - ExECT Diagnosis Primitive Pack

Outcome: Diagnosis specificity, certainty, co-list augmentation, uncertainty stripping, symptomatic/JME surfaces, and empty-list handling primitives.

Dependencies: Card 4
Parallelizable: yes, after normalization model
Owner: project
Validation: `uv run pytest tests/test_exect_diagnosis_primitives.py -q`; `uv run pytest tests/test_exect_s0_s1_program.py -q`.
Notes: Implemented in `src/clinical_extraction/exect/primitives.py`; typed registry entry added for `exect.diagnosis.benchmark_bridge.v1`. Tests cover uncertainty stripping, specificity collapse, symptomatic structural focal restoration, note-gated generic epilepsy co-listing, empty-list header recovery, seizure-descriptor header suppression, and explicit Certainty >= 4 annotation policy.

#### Card 10 - ExECT S4 Frequency Primitive Pack

Outcome: ExECT-specific frequency template primitives for rate candidates, qualitative change labels, multi-label blocks, no-reference handling, and benchmark-facing template repair.

Dependencies: Cards 3, 4, and 5
Parallelizable: after shared models
Owner: project
Validation: `uv run pytest tests/test_exect_frequency_primitives.py -q`; `uv run pytest tests/test_exect_s4_program.py -q`.
Notes: Implemented in `src/clinical_extraction/exect/primitives.py`; typed registry entries added for `exect.frequency.rate_candidates.v1` and `exect.frequency.benchmark_bridge.v1`. Tests cover quantified and qualitative candidates, Gan temporal filtering, near-miss repair, seizure-type stripping, non-audited period blocking, co-label augmentation, seizure-free prose collapse, and empty-list abstention policy. Cap-25 H2 pre-vocab remains rejected per `docs/exect_s4_frequency_deterministic_gpt_inspection_20260520.md`.

#### Card 12 - Build Interleaving Adapters

Outcome: Adapter layer that can expose one primitive as pre-injected context, during-prompt rules, tool-during callable helper, postprocessor, or eval-only diagnostic where appropriate.

Dependencies: Cards 3, 4, and 5
Parallelizable: after shared models
Owner: project
Validation: `uv run pytest tests/test_interleaving_adapters.py -q`.
Notes: Implemented in `src/clinical_extraction/interleaving_adapters.py`; initial bindings cover Gan temporal candidates, Gan label-policy bridge, Gan evidence guard, and ExECT medication candidates/bridge. Candidate primitives can render pre, during, and tool_during surfaces from one core invoke path; bridge and evidence primitives share post/eval_only payloads with different prediction-affecting flags.

#### Card 13 - Create Experiment Arm Templates

Outcome: Config templates or builders for L1, H1, H2, H3, H4, and D1 experiment arms with taxonomy fields, fixed controls, intended decision, and comparison-group conventions prefilled.

Dependencies: Card 12
Parallelizable: after adapters
Owner: project
Validation: `uv run pytest tests/test_experiment_arm_templates.py -q`; `uv run pytest tests/test_experiment_configs.py -q`; `uv run python scripts/validate_experiment_taxonomy.py --errors-only`.
Notes: Implemented in `src/clinical_extraction/experiments/arm_templates.py`; builders validate primitive arm compatibility, comparison-group naming, and shared-suite metadata before emitting `ExperimentConfig` records.

#### Card 15 - Standardize Inspection Templates

Outcome: Markdown templates for decision and inspection docs that require primitive IDs, taxonomy fields, scorer mode, normalization semantics, evidence semantics, run scope, and caveats.

Dependencies: Card 2
Parallelizable: yes
Owner: project
Validation: `uv run pytest tests/test_inspection_templates.py -q`.
Notes: Templates live under `docs/templates/` with section contracts in `src/clinical_extraction/experiments/inspection_templates.py`.

#### Card 14 - Create Primitive Fixture Library

Outcome: Small deterministic fixture set organized by dataset, family, primitive, and failure mode.

Dependencies: Cards 3, 4, and 5
Parallelizable: yes
Owner: project
Validation: `uv run pytest tests/test_primitive_fixture_library.py -q`.
Notes: Implemented in `data/fixtures/primitive_cases.json` and `src/clinical_extraction/fixtures/primitive_cases.py`; cases cover all required failure modes and invoke primitives without LLM calls.

#### Card 11 - Broad ExECT Family Primitive Backlog

Outcome: Scoped primitive sketches for investigation, comorbidity, birth/development, onset, cause, when diagnosed, driving, social history, pregnancy, and family history.

Dependencies: Card 2
Parallelizable: yes
Owner: project
Validation: Catalog review plus `uv run python scripts/validate_primitives.py --errors-only`.
Notes: Planned metadata in `src/clinical_extraction/exect/family_backlog.py`; implementation deferred until S1/S4 high-signal probes settle.

#### Card 17 - Decide How Much To Generalize Tool Interfaces

Outcome: Boundary decision for H3/tool-during support after Gan ReAct failed.

Dependencies: Card 12
Parallelizable: after adapters
Owner: project
Validation: Decision recorded in `docs/taxonomy_tool_interface_decision_20260520.md`.
Notes: Minimal adapter-level H3 support only; do not make H3 the default path.

#### Card 18 - Decide Ontology/CUI Scope

Outcome: Research decision on whether CUI/ontology primitives are included in this phase as stubs, deterministic lookup contracts, or deferred benchmark-reproduction infrastructure.

Dependencies: Card 2
Parallelizable: yes
Owner: project
Validation: Decision recorded in `docs/taxonomy_ontology_cui_scope_decision_20260520.md`.
Notes: Defer CUI-aware reproduction primitives to Card 19; CUIPhrase bridges remain string-surface canonicalization in this phase.

#### Card 22 - Consolidated Primitive Validation Command

Outcome: No-model validation command proving registry, catalog, fixture, and adapter metadata are internally consistent.

Dependencies: Cards 1, 2, 14, and 16
Parallelizable: after registry and catalog
Owner: project
Validation: `uv run python scripts/validate_primitives.py --errors-only`; `uv run pytest tests/test_primitive_registry_validation.py -q`.
Notes: Implemented in `scripts/validate_primitives.py` and `src/clinical_extraction/experiments/primitive_registry_validation.py`.

## Dependency Notes

Cards 1 through 22 define the completed primitive infrastructure. They should now be treated as a stable contract layer unless the coverage audit finds a mismatch with documented scorer or audit semantics.

Dataset packs can support new experiments, but primitive existence is not promotion evidence. Gan frequency, ExECT medication, ExECT seizure type, and ExECT diagnosis should not share benchmark-policy assumptions without explicit adapter code and a named comparison group.

Experiment arm templates and interleaving adapters now exist. New configs should use them to make the varied factor explicit before a model-backed run starts.

Fixture work is available for no-model validation. Add fixtures when a new primitive behavior or failure mode is being introduced, not as a substitute for model-backed promotion evidence.

## Parallelization Opportunities

Safe in parallel now:

- Card 23 primitive coverage audit
- Kanban/support-map documentation cleanup
- Registry matrix regeneration after metadata edits
- Negative-probe synthesis drafting

Blocked on Card 23:

- Card 24 catalog alignment
- Card 25 next ExECT mechanism preregistration

Should stay single-threaded:

- Any change to primitive contracts, registry source-of-truth policy, or scorer semantics
- Any model-backed comparison group selection
- Published ExECT benchmark reproduction design

## Recommended Next Pull

1. Complete Card 23 and classify primitives against closed experiments.
2. Update the catalog and support map so implemented primitives do not imply rejected arms should be rerun.
3. Use the audit to decide whether the next ExECT phase is Qwen seizure-gap diagnosis, S4 frequency mechanism redesign, medication temporality fallback, or synthesis pause.

## Execution Policy

The build-before-run phase has produced the core component library. New model-backed experiments should now be limited to cases that answer an active research decision already in `docs/kanban_plan.md` and have a preregistered comparison group. The primitive workstream should favor coverage audit, catalog alignment, deterministic validation, and inspection traceability over adding more helper code.
