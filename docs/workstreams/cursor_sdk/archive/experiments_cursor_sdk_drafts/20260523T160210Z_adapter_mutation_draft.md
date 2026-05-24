You are drafting a review-only artifact for the dspy-extraction research repo.

Workflow: Adapter/Prompt mutation draft
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
Read the Gan Qwen/GPT error taxonomy and candidate builder code.
Draft a proposed deterministic helper function template or mutated prompt candidates
to resolve identified failure modes. Do not make edits to the source code.

Primary sources:
- docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md
- docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md
- src/clinical_extraction/gan/temporal_candidates.py

Output shape:
# Adapter and Prompt Mutation Draft

## Sources Read
List paths.

## Identified Bottlenecks
Targeted failure modes (e.g., long-window quantified counts, cluster spacing separate count, seizure-free duration).

## Draft Python Code Templates
Proposed additions to temporal_candidates.py (e.g., regex pattern matches, candidate builders) to surface the missing candidate labels.

## Draft Prompt Mutations
Proposed additions/tweaks to prompt policies (like gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice.json) to handle candidate overrides or stability statements.

## Verification checklist
List unit tests and validation steps to verify the mutated logic without introducing regressions.
