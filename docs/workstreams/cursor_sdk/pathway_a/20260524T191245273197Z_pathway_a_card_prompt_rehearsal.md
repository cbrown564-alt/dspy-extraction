You are running a Cursor SDK Pathway A card lane for the dspy-extraction research repo.

Workflow: Pathway A ExECT S5 card
Card: A3D
Lane: design
Repository root: C:\Users\cbrow\Code\dspy-extraction

Hard rules:
- Do not edit files.
- Cursor output is not source-of-truth evidence. It is a review artifact for Codex/human inspection.
- Preserve ExECT audit guidance, fixed split definitions, and scorer semantics.
- Do not change raw data, gold labels, split definitions, scorer denominators, normalization rules, paper claims, or operational defaults unless the card explicitly authorizes that exact change.
- Every metric claim must include run ID, config, split, model/provider, scorer mode, denominator, and caveat.
- Flag missing context instead of guessing.

Card title: A3 prompt-policy design brief
Cursor role: design brief lane

Dataset and split:
- Dataset: ExECTv2
- Split: exectv2_fixed_v1:validation for validation work; use cap-25 before full validation.
- Surface: S5 core families only: diagnosis, seizure_type, annotated_medication, investigation, seizure_frequency.
- Current baseline: exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini; full validation seizure_frequency F1 60.2%, annotated-medication F1 88.7%, micro F1 81.4%.
- Scorer mode: exect_s5_core_field_family_deterministic_v1.

Primary sources:
- docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md
- docs/planning/kanban_plan.md
- docs/workstreams/cursor_sdk/cursor_sdk_pathway_a_implementation_campaign_20260524.md
- configs/experiments/
- src/clinical_extraction/programs/

Allowed write surfaces:
Design/report draft only unless run in a disposable implementation lane later.

Forbidden changes:
No scorer, gold, split, raw data, registry, or operational-default changes.

Validation gate:
Mission brief must isolate one prompt-policy factor and preserve candidate density, scorer mode, model/provider, split, and S5 guarded families.

Stop rules:
Do not encode clinical corrections as benchmark gold policy or compare cap-25 metrics as full-validation evidence.


Output shape:
# Cursor SDK Pathway A Card Report

## Card
Card ID, title, lane, and whether the run was review-only or disposable mutation.

## Sources Read
List concrete source paths and any missing paths.

## Changes Proposed Or Made
For review/design lanes, list proposed changes only. For implementation lanes, list changed files.

## Tests / Runs
Commands run, test output summary, run IDs, or reason no execution was appropriate.

## Metric Claims
Only source-backed claims with config, split, model/provider, scorer mode, denominator, and caveat.

## Scorer / Dataset Semantics Check
Explicitly state whether raw data, gold labels, split definitions, scorer normalization, and denominator semantics were preserved.

## Risks
Residual risks, failure modes, and missing evidence.

## Promotion Recommendation
Use one of: reject, keep_as_lead, promote_specific_claims_after_review, implementation_ready_after_brief_review, or needs_more_source_context.
