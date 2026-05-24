You are drafting a review-only artifact for the dspy-extraction research repo.

Workflow: Experiment-inspection draft worker
Repository root: C:\Users\cbrow\Code\dspy-extraction

Hard rules:
- Do not edit files.
- Do not change scorer semantics, dataset policy, registry rows, Kanban, or source-of-truth docs.
- Do not treat this draft as evidence for paper claims unless it points to primary artifacts.
- Preserve decision scopes: operational, arm, mechanism, open, blocked, stale_check.
- Separate facts from interpretation and uncertainty.
- Include concrete source paths for every claim.
- Flag missing context instead of guessing.

Task:
Draft an experiment inspection note for review.

Topic: ExECT Explorer backend/UI plan for selecting S1-S5 model runs and visualizing LLM plus deterministic pipeline steps
Run directory or artifact pointer: No run directory supplied. Draft a template and list required inputs.

Use these sources when present:
- docs/templates/experiment_decision_template.md
- docs/planning/kanban_plan.md
- docs/policies/deterministic_scorer_semantics.md
- docs/datasets/exect/exect_gold_label_audit.md, if ExECT is in scope
- docs/datasets/gan/gan_2026_label_audit.md, if Gan is in scope
- configs/experiments/, configs/models/, and the supplied run directory

Output shape:
# Experiment Inspection Draft

## Scope
Dataset, split, model/provider, schema level or field group, DSPy program
variant, scorer mode, normalization rules, and evidence policy. Use "unknown"
where not discoverable.

## Sources Read
List concrete paths.

## Run Summary
Metrics, run IDs, artifact paths, and comparison controls.

## Interpretation
What the result suggests, scoped to the comparison group.

## Caveats
Scorer, dataset, cap/full/test, validation, or billing caveats.

## Decision Recommendation
Use hold, promote, reject-as-tested, rerun, or needs-review, with rationale.

## Required Human Checks
List checks before promoting this draft into docs/experiments/.
