---
name: taxonomy-primitive-design
description: Use when adding, implementing, or changing taxonomy primitives, primitive registry metadata, interleaving adapters, benchmark bridges, deterministic fixture cases, or primitive validation for Gan and ExECT experiments.
---

# Taxonomy Primitive Design

Use this skill when deterministic helpers, benchmark bridges, evidence checks, or interleaving surfaces need to become typed, registry-backed primitives rather than ad hoc program code.

## Required Context

Read in this order:

1. `docs/taxonomy/taxonomy_primitive_contract.md`
2. `docs/taxonomy/taxonomy_primitive_catalog.md`
3. `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md` for current status and blocked cards
4. Dataset audit for the target family:
   - Gan: `docs/datasets/gan/gan_2026_label_audit.md`
   - ExECT: `docs/datasets/exect/exect_gold_label_audit.md`
5. Nearby implementation patterns in `src/clinical_extraction/primitives.py` and the relevant dataset pack under `src/clinical_extraction/gan/` or `src/clinical_extraction/exect/`

## Workflow

1. Decide whether the helper is a new primitive or an adapter around an existing one.
2. Register typed metadata in Python first. `PrimitiveMetadata` in `src/clinical_extraction/primitives.py` is the source of truth; Markdown catalog rows follow the registry.
3. Reuse shared payload contracts when applicable:
   - `PrimitiveCandidate`
   - `NormalizationResult`
   - `EvidenceSupportResult`
4. Implement deterministic logic in the dataset pack. Keep prediction-affecting behavior explicit; default bridges and evidence guards to scorer-only or diagnostic mode unless the experiment requires otherwise.
5. Add interleaving bindings in `src/clinical_extraction/interleaving_adapters.py` when the primitive must appear at multiple taxonomy positions.
6. Add focused tests and, when useful, fixture cases in `data/fixtures/primitive_cases.json`.
7. Update `docs/taxonomy/taxonomy_primitive_catalog.md` if the primitive changes intended comparison groups or caveats.
8. Run validation before finishing.

## Registry Rules

- Use stable dotted IDs ending in a version, such as `exect.medication.benchmark_bridge.v1`.
- Declare dataset, field families, knowledge sources, hybrid balance class, interleaving positions, control modes, compatible experiment arms, and status.
- Keep `planned` metadata in the registry when the contract is known but implementation is deferred.
- Do not add a second JSON or Markdown metadata source of truth.

## Validation Commands

Run focused tests first, then consolidated validation:

```powershell
uv run pytest tests/test_<relevant>_primitives.py -q
uv run python scripts/validate_primitives.py --errors-only
```

When the change also affects experiment configs or arm templates:

```powershell
uv run pytest tests/test_experiment_arm_templates.py tests/test_interleaving_adapters.py -q
uv run python scripts/validate_experiment_taxonomy.py --errors-only
```

## Validation Warning Triage

Treat `--errors-only` warnings as known debt, not as noise to ignore blindly.
Before changing nearby primitive metadata, catalog rows, implementation refs, or
interleaving adapters:

1. Run the relevant validator and note the current warning count.
2. Fix warnings that are in the touched primitive family when the fix is
   mechanical and semantics-preserving.
3. Preserve unrelated warnings only when they are documented existing debt.
4. Do not add new warnings without explaining why the primitive is intentionally
   catalog-only, planned, adapter-extended, or provenance-only.

As of the May 28 review, expected primitive warnings include missing catalog rows
for `exect.comorbidity.atomization_bridge.v1` and
`exect.investigation.drop_ecg_guard.v1`, adapter-extended interleaving
positions for selected Gan/ExECT primitives, and stale implementation refs for
some older ExECT primitive docs. Prefer shrinking this list when touching those
families.

## Scope Boundaries

- Minimal H3/tool-during support only. Do not build a broad tool-wrapper framework. See `docs/taxonomy/taxonomy_tool_interface_decision_20260520.md`.
- Defer CUI/ontology-aware primitives to published benchmark reproduction. See `docs/taxonomy/taxonomy_ontology_cui_scope_decision_20260520.md`.
- Do not promote a primitive merely because it exists. Promotion still requires model-backed comparison groups and inspection documents.
- Prefer family-specific primitives over broad full-note interventions unless the experiment explicitly tests broad context.

## Completion Criteria

Before finishing, summarize:

- primitive ID(s) added or changed
- dataset and field families affected
- whether behavior is prediction-affecting, scorer-only, or diagnostic-only
- tests and fixture cases added
- validation commands run
- catalog or adapter updates needed next
