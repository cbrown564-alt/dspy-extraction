# Taxonomy Ontology / CUI Scope Decision

Date: 2026-05-20  
Status: Decision recorded (Card 18)  
Related: `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md`, `docs/policies/published_benchmark_metrics.md`, `docs/datasets/exect/exect_gold_label_audit.md`, Card 19 blocked benchmark pack

## Question

Should CUI/ontology primitives be included in the current taxonomy-primitives phase as stubs, deterministic lookup contracts, or deferred benchmark-reproduction infrastructure?

## Decision

**Defer CUI-aware primitives to the published benchmark-reproduction phase.** The current phase keeps string-based field-family diagnostics and records one planned stub only.

### Current phase (build-before-run)

1. Local ExECT scoring remains **normalized string / CUIPhrase-surface** field-family diagnostics, as documented in `docs/policies/published_benchmark_metrics.md`.
2. S3 sparse-family backlog primitives (`exect.*.cui_phrase_bridge.v1`) refer to **affirmed CUIPhrase surfaces from JSON markup**, not live CUI graph lookup or feature-aware Table 1 matching.
3. One planned registry stub exists: `exect.ontology.cui_alignment.v1` with status `planned` and explicit deferral caveats.
4. No CUI lookup tables, ontology APIs, or prediction-affecting CUI bridges are implemented in this phase.

### Deferred phase (Card 19)

Published ExECTv2 Table 1 reproduction requires:

- CUI-plus-feature matching across all annotation families,
- ontology-aligned normalization distinct from local benchmark bridges,
- scorer tests under `gold-scorer-integrity` against benchmark semantics,
- explicit separation from local field-family diagnostic runs.

That work remains blocked on Card 19 until benchmark-scorer design is in scope.

## Rationale

Mixing CUI-aware reproduction with local field-family diagnostics would blur comparison groups:

| Mode | Scorer | Comparable to Table 1? |
| --- | --- | --- |
| Local S1/S4 field-family | Normalized strings, audited bridges | Partial only |
| Published reproduction | CUI + certainty/feature rules | Yes, when fully built |

The repo already documents that current numbers are **not** Table 1 reproduction. Adding partial CUI hooks now would create a third ambiguous scorer mode without unlocking the main research gap.

Sparse S3 families (`onset`, `when_diagnosed`, `birth_history`, `epilepsy_cause`) need **surface canonicalization** against audited CUIPhrase labels loaded from JSON, which the existing loaders and S3 bridges already approximate. Full ontology alignment is a separate, heavier infrastructure layer.

## What “CUIPhrase bridge” means in Card 11 sketches

Planned `exect.*.cui_phrase_bridge.v1` primitives mean:

- Input: raw model or deterministic prediction strings plus note text.
- Output: canonical **clinical phrase surfaces** aligned to gold JSON CUIPhrase labels.
- Knowledge source: audited markup tables and `canonical_*_label` helpers in `src/clinical_extraction/datasets/exect.py`.
- Not included: UMLS lookup, CUI code assignment, or feature-level Table 1 scoring.

## Gan ontology scope

Gan 2026 benchmark reproduction depends on Real(300)/Real(150) access (Card 20), not CUI alignment. No Gan ontology primitives are added in this phase.

## Registry artifact

`exect.ontology.cui_alignment.v1` remains `planned` with:

- `knowledge_sources`: `cui_or_ontology`, `benchmark_label_policy`, `gold_audit_policy`
- `interleaving_positions`: `post`, `eval_only`
- `compatible_experiment_arms`: `H1`, `D1`
- Blocked dependency: Card 19 published benchmark primitive pack

## Revisit triggers

Start CUI/ontology primitive implementation when:

1. `docs/planning/kanban_plan.md` explicitly schedules published ExECT Table 1 reproduction, and
2. A benchmark-scorer design doc defines CUI+feature rules per annotation family, and
3. The comparison group separates reproduction runs from local diagnostic runs in registry metadata.

Until then, treat CUI references in primitive metadata as **future benchmark infrastructure**, not active build targets.
