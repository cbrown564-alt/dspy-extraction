# Next Major Phases

Date: 2026-05-20  
Status: Planning note after S1 interleaving Qwen validation v1 closed as reject port  
Related: `docs/kanban_plan.md`, `docs/exect_negative_probe_synthesis_20260520.md`, `docs/taxonomy_primitive_coverage_audit_20260520.md`, `docs/exect_field_family_deterministic_support_map_20260520.md`, `docs/taxonomy_primitives_workstream_plan_20260520.md`, `docs/experiment_taxonomy_research_synthesis_20260520.md`

## Context

The project has completed a dense wave of taxonomy-governed ExECT and Gan experiments. Gan S0 seizure frequency has a promoted deterministic-preconditioning narrative. ExECT S1/S4 deterministic probes have produced useful negative evidence, but no new promotable intervention: S1 interleaving, medication H2, seizure H2, S4 frequency H2, S4 temporality H1, and Qwen interleaving v1 are all closed or rejected.

The next phase should therefore avoid automatic reruns. The useful work now is to consolidate what the negative results mean, classify which primitives are reusable infrastructure versus rejected interventions, and only then choose the next model-backed comparison group.

## Phase 1 - Consolidate Evidence

Research question: What can we safely claim from the completed taxonomy-governed run batch?

Deliverables:

- Aligned steering docs with no stale next-run queue.
- A negative-probe synthesis note covering the closed ExECT arms: `docs/exect_negative_probe_synthesis_20260520.md`.
- Primitive coverage audit that labels implemented primitives as `promoted`, `diagnostic_only`, `rejected_for_current_arm`, `planned`, or `blocked`: `docs/taxonomy_primitive_coverage_audit_20260520.md`.
- Refreshed registry matrix if registry metadata changes.

Definition of done:

- Claims cite run IDs, inspection docs, or registry rows.
- No documentation implies that rejected H1/H2 arms should be rerun by default.
- Local field-family diagnostics remain clearly separated from published benchmark reproduction.

## Phase 2 - Select One ExECT Mechanism

Research question: Is there a new, single-factor ExECT mechanism worth testing?

Candidate directions:

- Qwen S1 seizure-gap diagnosis, starting with error analysis before any intervention.
- S4 seizure-frequency mechanism redesign, only if the varied factor differs from the rejected pre-candidate arm.
- S4 medication-temporality dose-only abstention fallback, only as a narrow repair to the observed recall collapse.
- No-run synthesis pause if none of the above can be preregistered cleanly.

Definition of done:

- One preregistration names dataset, split, schema, model, scorer, frozen baseline, varied factor, primitive IDs, run scope, gate, and reject/hold/promote criteria.
- The comparison group changes one intended factor unless explicitly documented as an interaction study.

## Phase 3 - Reproduction And External Validity

Research question: Which claims survive beyond local diagnostic validation?

Blocked work:

- Published ExECTv2 reproduction remains blocked on CUI-aware all-family scoring and ontology-aligned primitives.
- Gan Real(300)/Real(150) validation remains blocked on data access.

Definition of done:

- Reproduction work uses `dataset-audit-first` and `gold-scorer-integrity`.
- Reports distinguish published benchmark reproduction from local field-family diagnostics.
- Gan synthetic-validation claims are not generalized to unavailable real-set data.

## Phase 4 - Scale-Up And Ablation Expansion

Research question: Once narrow mechanisms are stable, how do architecture, optimizer, and model-family choices interact?

Deferred work:

- Broad ExECT architecture matrix.
- DSPy optimizer scale-up.
- Wider local/closed model comparisons.

Definition of done:

- Broad experiments are reopened only with stable scorer semantics and explicit interaction hypotheses.
- Optimizer results are not mixed with fixed-program comparisons unless the optimizer is the named experimental factor.

## Recommended Next Pull

1. Align the primitive catalog with the negative-probe synthesis and primitive coverage audit.
2. Preregister the selected Phase 2 path, or explicitly record a no-run synthesis pause.
3. Decide whether Phase 2 starts with Qwen seizure-gap error analysis, S4 frequency redesign, medication-temporality fallback, or a synthesis pause.
