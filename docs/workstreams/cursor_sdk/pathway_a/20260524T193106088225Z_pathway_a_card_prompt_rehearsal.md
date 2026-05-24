You are running a Cursor SDK Pathway A card lane for the dspy-extraction research repo.

Workflow: Pathway A ExECT S5 card
Card: A2I
Lane: implementation
Repository root: C:\Users\cbrow\Code\dspy-extraction

Hard rules:
- You may edit only the allowed write surfaces named in the card brief.
- You must first verify the workspace marker `.cursor-sdk-disposable-worktree`, `CURSOR_SDK_ALLOW_MUTATING_WORKFLOW=disposable-worktree`, and clean `git status --short`.
- Capture changed files, focused test output, and `git diff` in the final report.
- Restore the disposable worktree before ending, then report the final clean status.
- Cursor output is not source-of-truth evidence. It is a review artifact for Codex/human inspection.
- Preserve ExECT audit guidance, fixed split definitions, and scorer semantics.
- Do not change raw data, gold labels, split definitions, scorer denominators, normalization rules, paper claims, or operational defaults unless the card explicitly authorizes that exact change.
- Every metric claim must include run ID, config, split, model/provider, scorer mode, denominator, and caveat.
- Flag missing context instead of guessing.

Card title: A2 verifier implementation pilot
Cursor role: disposable-worktree implementation lane

Dataset and split:
- Dataset: ExECTv2
- Split: exectv2_fixed_v1:validation for validation work; use cap-25 before full validation.
- Surface: S5 core families only: diagnosis, seizure_type, annotated_medication, investigation, seizure_frequency.
- Current baseline: exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini; full validation seizure_frequency F1 60.2%, annotated-medication F1 88.7%, micro F1 81.4%.
- Scorer mode: exect_s5_core_field_family_deterministic_v1.

Primary sources:
- docs/workstreams/cursor_sdk/pathway_a/a2_verifier_mission_brief_20260524.md
- docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md
- docs/datasets/exect/exect_gold_label_audit.md
- docs/policies/deterministic_scorer_semantics.md
- docs/taxonomy/taxonomy_primitive_catalog.md
- configs/experiments/exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini.json
- src/clinical_extraction/programs/exect_s4.py
- src/clinical_extraction/programs/exect_s0_s1.py
- src/clinical_extraction/exect/primitives.py
- src/clinical_extraction/experiments/exect_backend.py
- src/clinical_extraction/experiments/config.py
- tests/

Allowed write surfaces:
Implementation edits only in the mission-brief allow-list: src/clinical_extraction/programs/exect_s4.py; src/clinical_extraction/exect/primitives.py only for small evidence/candidate-block guard helpers; src/clinical_extraction/experiments/exect_backend.py; src/clinical_extraction/experiments/config.py; src/clinical_extraction/experiments/exect_prompts.py only if prompt routing requires it; configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini.json; tests/test_exect_s5_frequency_verifier.py; existing focused config/scorer tests if registration needs them; and a disposable inspection draft under docs/experiments/exect/.

Forbidden changes:
No raw data, gold labels, split definitions, scorer denominator, scorer normalization, benchmark bridge semantics, high-recall candidate builder output/density, medication guard semantics, registry rows, Kanban status, paper claims, operational defaults, or full-validation execution.

Validation gate:
Run focused tests first: uv run --extra dev pytest tests/test_exect_s5_frequency_verifier.py tests/test_exect_s5_scoring.py tests/test_experiment_configs.py -q; then uv run python scripts/validate_experiment_taxonomy.py --errors-only. Run the cap-25 experiment only after tests pass.

Stop rules:
Stop if the verifier changes scorer/gold semantics, narrows candidates, adds labels or repairs FNs, drops labels without note-evidence rationale, materially reduces frequency recall, regresses guard families, or becomes a hidden normalization/scorer rewrite.

Operator-supplied mission brief:

# A2 Verifier Mission Brief

Date: 2026-05-24
Status: Ready for disposable implementation pilot after Codex review
Decision scope: Pathway A card A2 implementation brief

## Card

A2. Candidate-constrained frequency verifier

## Hypothesis

A post-extraction, evidence-sensitive verifier over the existing high-recall ExECT frequency candidate surface can reduce S5 `seizure_frequency` false positives without losing the recall that high-precision candidate pruning lost.

This is a reject-only verifier arm. It must not narrow pre-vocab candidates, add new labels, change scorer normalization, or reinterpret gold-empty examples as corrected benchmark truth.

## Fixed Controls

| Dimension | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Split | `exectv2_fixed_v1:validation`; cap-25 before full validation |
| Surface | S5 core families: diagnosis, seizure_type, annotated_medication, investigation, seizure_frequency |
| Baseline config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini.json` |
| Full baseline | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini.json` |
| Model/provider | `gpt-4.1-mini`, OpenAI |
| Scorer mode | `exect_s5_core_field_family_deterministic_v1` |
| Candidate policy | Keep high-recall `exect.frequency.rate_candidates.v1`; do not use high-precision pruning |
| Medication guard | Preserve `exect.medication.am_guard_non_asm_brand_alias.v1` unchanged |

## Proposed Variant

Suggested program variant name:

`exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1`

Design shape:

1. Run the current high-recall pre-vocab S5 extractor unchanged.
2. Pass only predicted `seizure_frequency` labels, their evidence, the note, and the candidate list to a frequency verifier.
3. Verifier may confirm or reject labels, but may not add labels.
4. Deterministic guard should reject evidence quotes that come from the injected candidate block rather than the clinical note.
5. Run the existing annotated-medication guard unchanged.
6. Score with the existing S5 deterministic scorer.

## Allowed Write Surfaces

- `src/clinical_extraction/programs/exect_s4.py`
- `src/clinical_extraction/exect/primitives.py`, only for small evidence/candidate-block guard helpers if needed
- `src/clinical_extraction/experiments/exect_backend.py`
- `src/clinical_extraction/experiments/config.py`
- `src/clinical_extraction/experiments/exect_prompts.py`, only if prompt routing requires it
- `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini.json`
- `tests/test_exect_s5_frequency_verifier.py`
- Existing focused config/scorer tests, if registration needs them
- A disposable-worktree inspection draft under `docs/experiments/exect/`

## Forbidden Changes

- Raw data, gold labels, split definitions
- Scorer denominator, scorer normalization, or bridge semantics
- High-recall candidate builder output or candidate density
- Medication temporality or annotated-medication scorer policy
- Registry rows, Kanban status, paper claims, or operational defaults
- Full-validation execution before cap-25 clears

## Validation Gate

Run focused tests first:

```powershell
uv run --extra dev pytest tests/test_exect_s5_frequency_verifier.py tests/test_exect_s5_scoring.py tests/test_experiment_configs.py -q
uv run python scripts/validate_experiment_taxonomy.py --errors-only
```

Run cap-25 only after tests pass:

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini.json --env-file .env
```

Provisional cap-25 pass thresholds:

- `seizure_frequency` recall no worse than baseline by more than 3.0 percentage points.
- `seizure_frequency` F1 improves by at least 2.0 points, or precision improves by at least 5.0 points.
- Diagnosis, seizure_type, annotated_medication, and investigation F1 each stay within 2.0 points of the AM-guard cap-25 baseline.
- S5 micro F1 does not drop by more than 1.0 point.

These thresholds are preregistration gates for this pilot, not general scorer policy.

## A1 Fixture Focus

Use A1 examples to test verifier behavior without claiming benchmark performance from fixtures:

| Purpose | Example docs |
| --- | --- |
| Reject unsupported qualitative labels | EA0008, EA0131, EA0174 |
| Reject candidate-block evidence echo | EA0174 |
| Reject medication-control-as-frequency-change | EA0029 |
| Handle historical/current scope cautiously | EA0069, EA0142, EA0098 |
| Preserve supported labels / monitor recall | EA0059, EA0173, EA0136, EA0137 |
| Treat gold-empty cases as caveats, not scorer bugs | EA0018, EA0109, EA0153 |

## Stop Rules

Stop and report rather than continuing if:

- The verifier changes or bypasses scorer/gold semantics.
- The implementation narrows the candidate list.
- The verifier adds labels or repairs FNs.
- Labels are dropped without note-evidence rationale in metadata or report output.
- Cap-25 recall drops materially against the baseline.
- Guard families regress beyond the thresholds above.
- The implementation becomes a hidden normalization/scorer rewrite.

## Required Cursor Report

The disposable implementation report must include changed files, tests run, cap-25 run ID or dry-run blocker, metric deltas with denominator caveats, scorer/dataset semantic checks, captured `git diff`, and final clean disposable-worktree status.


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
