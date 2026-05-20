# Taxonomy Primitives Workstream Plan

Date: 2026-05-20  
Status: In progress  
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

Model-backed execution can then happen later under fixed controls, with the primitives already inspected, unit-tested, and documented.

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
- A small set of no-model validation commands that prove the primitives and registry metadata are internally consistent.

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

## Board

### Ready

### Backlog

#### Card 10 - ExECT S4 Frequency Primitive Pack

Outcome: ExECT-specific frequency template primitives for rate candidates, qualitative change labels, multi-label blocks, no-reference handling, and benchmark-facing template repair.

Dependencies: Cards 3, 4, and 5  
Parallelizable: after shared models  
Owner: unassigned  
Validation: Deterministic tests on S4 frequency examples and cap-25 inspection failures.  
Notes: Do not copy Gan monthly normalization directly; ExECT gold surfaces are different.

#### Card 11 - Broad ExECT Family Primitive Backlog

Outcome: Scoped primitive sketches for investigation, comorbidity, birth/development, onset, cause, when diagnosed, driving, social history, pregnancy, and family history.

Dependencies: Card 2  
Parallelizable: yes  
Owner: unassigned  
Validation: Catalog review only at first; implementation tests later for high-priority families.  
Notes: Sparse families should be designed but not overbuilt until higher-signal S1/S4 probes settle.

### Ready After Contracts

#### Card 12 - Build Interleaving Adapters

Outcome: Adapter layer that can expose one primitive as pre-injected context, during-prompt rules, tool-during callable helper, postprocessor, or eval-only diagnostic where appropriate.

Dependencies: Cards 3, 4, and 5  
Parallelizable: after shared models  
Owner: unassigned  
Validation: No-model tests show the same primitive can be represented with different taxonomy positions without changing its core logic.  
Notes: This is the key to testing interleaving position rather than rewriting logic for each arm.

#### Card 13 - Create Experiment Arm Templates

Outcome: Config templates or builders for L1, H1, H2, H3, H4, and D1 experiment arms with taxonomy fields, fixed controls, intended decision, and comparison-group conventions prefilled.

Dependencies: Card 12  
Parallelizable: after adapters  
Owner: unassigned  
Validation: `uv run pytest tests/test_experiment_configs.py -q` plus taxonomy validator.  
Notes: The templates should make invalid comparison groups harder to create.

#### Card 14 - Create Primitive Fixture Library

Outcome: Small deterministic fixture set organized by dataset, family, primitive, and failure mode.

Dependencies: Cards 3, 4, and 5  
Parallelizable: yes  
Owner: unassigned  
Validation: Tests prove fixtures load deterministically on Windows and feed primitive unit tests.  
Notes: Include positive, negative, ambiguous, absent, historical, planned, and unsupported-evidence cases.

#### Card 15 - Standardize Inspection Templates

Outcome: Markdown templates for decision and inspection docs that require primitive IDs, taxonomy fields, scorer mode, normalization semantics, evidence semantics, run scope, and caveats.

Dependencies: Card 2  
Parallelizable: yes  
Owner: unassigned  
Validation: Existing inspection docs can be mapped onto the template without losing important caveats.  
Notes: This should reduce result interpretation drift after runs execute.

### Questions

#### Card 17 - Decide How Much To Generalize Tool Interfaces

Outcome: Boundary decision for H3/tool-during support after Gan ReAct failed.

Dependencies: Card 12  
Parallelizable: after adapters  
Owner: unassigned  
Validation: Decision recorded before building broad tool wrappers.  
Notes: Build enough interface to compare H3 cleanly later, but do not make H3 the default path.

#### Card 18 - Decide Ontology/CUI Scope

Outcome: Research decision on whether CUI/ontology primitives are included in this phase as stubs, deterministic lookup contracts, or deferred benchmark-reproduction infrastructure.

Dependencies: Card 2  
Parallelizable: yes  
Owner: unassigned  
Validation: Decision references the published ExECT benchmark reproduction blocker.  
Notes: Avoid mixing CUI-aware reproduction with local field-family diagnostics unless the comparison group says so.

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

## Dependency Notes

Cards 1 through 5 define the shared contracts. They should stay relatively single-threaded or be reviewed together because they determine the language used by every later primitive.

Dataset packs can proceed in parallel once the shared candidate, normalization, and evidence models exist. Gan frequency, ExECT medication, ExECT seizure type, and ExECT diagnosis should not share benchmark-policy assumptions without explicit adapter code.

Experiment arm templates should wait until interleaving adapters exist. Otherwise the templates may encode today’s program shapes instead of the taxonomy dimensions we actually want to test.

Fixture work can start early once the shared object models are stable. It is especially valuable because it exercises primitive behavior without model cost.

## Parallelization Opportunities

Safe in parallel after Card 1:

- Card 2 primitive catalog
- Card 3 candidate model
- Card 4 normalization model
- Card 5 evidence support model
- Card 18 ontology/CUI scope decision

Safe in parallel after shared models:

- Card 6 Gan frequency pack
- Card 7 ExECT medication pack
- Card 8 ExECT seizure-type pack
- Card 9 ExECT diagnosis pack
- Card 10 ExECT S4 frequency pack
- Card 14 fixture library
- Card 15 inspection templates

Should stay single-threaded:

- Card 1 primitive contract schema
- Card 12 interleaving adapters
- Card 13 experiment arm templates
- Card 16 primitive registry location

## Recommended First Pull

1. Define the primitive contract schema.
2. Decide the primitive registry location.
3. Seed `docs/taxonomy_primitive_catalog.md` from Gan frequency and ExECT S1/S4 support maps.
4. Implement the candidate, normalization, and evidence support models with deterministic tests.

That first pull creates the shared language and data contracts. After it lands, the dataset-specific primitive packs can be built in parallel without turning into disconnected helper code.

## Execution Policy

This is a build-before-run phase. New model-backed experiments should be limited to cases that answer an active research decision already in `docs/kanban_plan.md`, such as the S4 medication temporality post-classifier. The primitive workstream should otherwise favor deterministic validation, fixture design, config generation, and inspection templates until the component library is coherent enough to support the next systematic run batch.
