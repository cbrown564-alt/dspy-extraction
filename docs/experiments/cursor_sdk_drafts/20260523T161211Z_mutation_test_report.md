You are drafting a review-only artifact for the dspy-extraction research repo.

Workflow: Cursor SDK Mutation Testing
Repository root: C:\Users\cbrow\Code\dspy-extraction

CRITICAL RULES FOR COMMAND EXECUTION:
1. You are running as an agent in the repository workspace. You have the ability to read, edit files, and execute terminal commands.
2. Before making any modifications, you MUST verify that you are on a clean git working directory. Run `git status` to verify.
3. Read the latest adapter mutation draft file in `docs/experiments/cursor_sdk_drafts/*_adapter_mutation_draft.md`.
4. Implement the drafted helper functions (like `_seizure_free_for_multiple_year`, `_seizure_free_for_multiple_month`, etc.) and register them in `src/clinical_extraction/gan/temporal_candidates.py`.
5. Run `uv run pytest tests/test_gan_temporal_candidates.py` to check for regressions.
6. Diagnose any failures, modify the code, and rerun the tests until all 49+ tests pass.
7. Verify if the coverage on the pragmatics slice (`test_enriched_gap_slice_gold_label_coverage_improves` or `test_residual_slice_gold_label_coverage_improves`) changes or passes.
8. Run `git diff` to capture all your modifications.
9. CRITICAL RESTORATION: You MUST undo all your modifications to `src/clinical_extraction/gan/temporal_candidates.py` before ending your turn. Run `git checkout -- src/clinical_extraction/gan/temporal_candidates.py` and verify with `git status` that the workspace is completely clean. Do not leave the workspace dirty.
10. Write the final report detailing your steps, outcomes, and the captured git diff.

Output shape:
# Cursor SDK Mutation Test Report

## Executive Summary
Stated outcomes: whether existing tests passed, whether any new test cases passed, and whether the workspace was successfully rolled back to a clean state.

## Implementation Steps
Details of the changes you attempted.

## Test Outcomes & Debugging
The output of the pytest execution. Details of any test failures and how you debugged/corrected them.

## Captured Git Diff
The full `git diff` block of the implemented code mutations before they were rolled back.

## Restoration Verification
The output of `git status` confirming the workspace is clean.
