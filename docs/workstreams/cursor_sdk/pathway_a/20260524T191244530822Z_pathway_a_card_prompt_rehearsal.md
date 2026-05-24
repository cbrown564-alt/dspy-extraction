You are running a Cursor SDK Pathway A card lane for the dspy-extraction research repo.

Workflow: Pathway A ExECT S5 card
Card: A1R
Lane: review
Repository root: C:\Users\cbrow\Code\dspy-extraction

Hard rules:
- Do not edit files.
- Cursor output is not source-of-truth evidence. It is a review artifact for Codex/human inspection.
- Preserve ExECT audit guidance, fixed split definitions, and scorer semantics.
- Do not change raw data, gold labels, split definitions, scorer denominators, normalization rules, paper claims, or operational defaults unless the card explicitly authorizes that exact change.
- Every metric claim must include run ID, config, split, model/provider, scorer mode, denominator, and caveat.
- Flag missing context instead of guessing.

Card title: Retrospective A1 Cursor review
Cursor role: review-only retrospective critic/source-map lane

Dataset and split:
- Dataset: ExECTv2
- Split: exectv2_fixed_v1:validation for validation work; use cap-25 before full validation.
- Surface: S5 core families only: diagnosis, seizure_type, annotated_medication, investigation, seizure_frequency.
- Current baseline: exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini; full validation seizure_frequency F1 60.2%, annotated-medication F1 88.7%, micro F1 81.4%.
- Scorer mode: exect_s5_core_field_family_deterministic_v1.

Primary sources:
- docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md
- runs/exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z/errors.json
- runs/exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z/predictions.json
- src/clinical_extraction/datasets/exect.py
- docs/datasets/exect/exect_gold_label_audit.md
- docs/policies/deterministic_scorer_semantics.md

Allowed write surfaces:
Review draft only; no source edits.

Forbidden changes:
No edits to raw data, gold labels, split definitions, scorers, configs, registry rows, Kanban, or paper claims.

Validation gate:
Check residual categories and per-document claims against primary artifacts and load_exect_gold_documents() where useful.

Stop rules:
Stop at discrepancies or missing evidence; do not rewrite the promoted A1 note.


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
