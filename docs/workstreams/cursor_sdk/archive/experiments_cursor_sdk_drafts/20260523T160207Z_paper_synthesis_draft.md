You are drafting a review-only artifact for the dspy-extraction research repo.

Workflow: Automated paper narrative synthesis
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
Read the research outline, the experiment registry, and prior narrative reports.
Draft a results section/outline for the paper. Map paper claims directly to primary
run IDs and metrics from the registry. Do not make edits.

Primary sources:
- docs/outline.md
- docs/experiments/synthesis/experiment_registry.json
- docs/experiments/synthesis/experiments_narrative_report_20260520.md
- docs/experiments/synthesis/experiment_registry_matrix_20260520.md

Output shape:
# Paper Narrative Synthesis Draft

## Sources Read
List paths.

## Key Paper Claims Map
For each claim (e.g. model suite comparison, deterministic placement value, schema breadth effect):
1. Claim Statement: Summary of the claim.
2. Supporting Run ID: The exact run ID from the registry.
3. Supporting Metrics: Stated F1, Purist/Pragmatic accuracy, or micro accuracy.
4. Rationale: How the metric validates or caveats the claim.

## Discrepancies Or Unsupported Claims
Flag any claims in outline.md that lack backing in registry.json or narrative reports.

## Open Writing Tasks
What remains to be written or verified by a human before publication.
