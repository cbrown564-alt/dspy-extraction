# Cursor SDK Pathway A Implementation Campaign Plan

Date: 2026-05-24
Status: In progress
Decision scope: operational workflow for Pathway A only
Applies to: ExECT S5 Core Lift cards A1-A5 in `docs/planning/kanban_plan.md`

## Purpose

This document writes up the current failure modes in the Cursor SDK implementation/orchestration attempt and defines a full, review-gated plan for using Cursor SDK across the entire Pathway A ExECT S5 core-lift workstream.

The aim is not to let Cursor become a source of truth. The aim is to use Cursor as a bounded implementation and review engine while Codex/GPT-5.5 owns benchmark framing, scorer integrity, source verification, promotion decisions, and final research claims.

## Current Failure Writeup

### What Failed In The A1 Attempt

A1, the frequency residual audit, was completed as a Codex-only source-backed inspection rather than a true Cursor SDK implementation-orchestration run.

Observed failure:

- Codex checked for `cursor-agent` and `cursor` CLI commands.
- `cursor-agent` was not available, and `cursor` resolved only to the installed GUI command at `C:\Users\cbrow\AppData\Local\Programs\cursor\resources\app\bin\cursor.cmd`.
- Codex therefore concluded that no non-interactive Cursor implementation path was available and did not delegate a Cursor lane.
- A later check showed that the repo's Python SDK wrapper is available: `uv run python scripts/cursor_sdk_workflows.py check` reports `cursor-sdk import ok; CURSOR_API_KEY is present.`

Root cause:

- The orchestration attempt used the wrong capability probe. It looked for a standalone Cursor CLI/agent instead of using the project wrapper in `scripts/cursor_sdk_workflows.py`.
- The existing wrapper is mostly review-only and generic. It has `inspection-draft`, `paper-synthesis`, `adapter-mutation`, `model-compatibility`, and gated `test-mutations`, but no dedicated Pathway A campaign workflow that can accept a card brief, allowed write surfaces, stop rules, and validation gates.
- The handoff contract between Codex and Cursor was not materialized as a machine-runnable mission brief before the A1 work began.

Impact:

- A1's final artifact is still useful and source-backed, but it does not exercise the intended Cursor implementation-orchestration loop.
- No Cursor run ledger row exists for A1 implementation work.
- No independent Cursor critic/regression lane reviewed A1 before promotion.
- The process did not test the safety boundary needed for A2-A5, where Cursor may need to write source, tests, configs, scripts, and draft inspection artifacts.

### Current SDK Infrastructure Gaps

| Gap | Why it matters | Required fix before broad A-path use |
| --- | --- | --- |
| Wrong capability probe | Leads Codex to bypass a working Python SDK wrapper. | Use `uv run python scripts/cursor_sdk_workflows.py check` as the canonical readiness check. |
| No A-path workflow | Existing workflows do not encode benchmark target, allowed files, forbidden changes, or validation gates per A card. | Add or rehearse a `pathway-a-card` workflow/prompt template before mutation. |
| Review-only default is unclear for implementation | README says review-only, while `cursor-implementation-orchestration` permits scoped mutation. | Split workflows into review-only drafts and disposable-worktree implementation pilots. |
| Mutation workflow is too generic | `test-mutations` reads adapter mutation drafts; it is not suitable for ExECT S5 verifier/prompt/config work. | Create card-specific disposable-worktree prompts and reports. |
| Ledger lacks campaign linkage | Future runs need to tie outputs to A2/A3/A4/A5, not just workflow names. | Record `pathway`, `card`, `mission_brief`, `source_claim_status`, and `promotion_decision` in docs or JSONL companion notes. |
| Promotion boundary needs explicit review checklist | Cursor diffs must not become source-of-truth by momentum. | Require Codex diff review, focused tests, run artifact checks, and explicit promotion notes. |

## Current Readiness

Confirmed:

- `uv run python scripts/cursor_sdk_workflows.py check` passes.
- The SDK wrapper imports successfully.
- `CURSOR_API_KEY` is present.
- A disposable-worktree protocol exists at `docs/workstreams/cursor_sdk/cursor_sdk_disposable_worktree_protocol_20260524.md`.
- A1 has a source-backed residual audit: `docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md`.

Not yet ready:

- There is no disposable A-path implementation worktree currently recorded for A2-A5.
- A2/A3 implementation pilots still need disposable-worktree execution and Codex diff review before any source promotion.

2026-05-24 progress update:

- Added a first-class `pathway-a-card` workflow in `scripts/cursor_sdk_workflows.py` with card, lane, mission-brief, prompt-only, ledger, and disposable implementation-lane gating.
- Updated `docs/workstreams/cursor_sdk/README.md` with Pathway A review/design/implementation command examples.
- Ran A1R as a review-only Cursor lane: `docs/workstreams/cursor_sdk/pathway_a/20260524T191250353424Z_pathway_a_card_report.md`.
- Promoted one source-backed A1 table correction: `frequency decreased` is now listed as 1 FP and quantified-rate FPs as 15 in `docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md`.
- Ran A2D and A3D as review-only design lanes and distilled them into Codex-authored mission briefs:
  - `docs/workstreams/cursor_sdk/pathway_a/a2_verifier_mission_brief_20260524.md`
  - `docs/workstreams/cursor_sdk/pathway_a/a3_prompt_policy_mission_brief_20260524.md`
- Generated an A2 implementation prompt rehearsal from the accepted mission brief for disposable-worktree handoff.
- Ran A2I as a disposable Cursor implementation lane, but the SDK report omitted the full diff; Codex therefore implemented and reviewed the source patch manually in the shared workspace.
- A2I cap-25 run completed: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T193119Z`. Frequency precision/F1 improved versus the AM-guard cap-25 baseline, but recall fell from 92.0% to 72.0%, so the arm is on hold pending A2R rather than promoted to full validation.

## Pathway A Mission Brief

Dataset: ExECTv2

Split policy: use `exectv2_fixed_v1:validation` for validation work; use cap-25 before full validation; do not touch split definitions.

Surface: ExECT S5 core families only:

- `diagnosis`
- `seizure_type`
- `annotated_medication`
- `investigation`
- `seizure_frequency`

Current operational candidate:

- `exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini`
- Full validation: frequency F1 60.2%, annotated-medication F1 88.7%, micro F1 81.4%.
- Active bottleneck: `seizure_frequency`.

Primary benchmark target:

- Improve S5 `seizure_frequency` F1 beyond the high-recall pre-vocab baseline without regressing guarded families.

Scorer mode:

- `exect_s5_core_field_family_deterministic_v1`

No-go changes:

- No raw data edits.
- No gold-label reinterpretation.
- No split changes.
- No scorer denominator or normalization drift.
- No CUI-aware reproduction claims.
- No operational-default promotion from cap-25 alone.
- No paper claims from SDK drafts.

Required project skills for the campaign:

- `cursor-implementation-orchestration`
- `dataset-audit-first`
- `gold-scorer-integrity`
- `exect-label-policy-alignment`
- `dspy-experiment-design`
- `experiment-run-lifecycle`
- `taxonomy-primitive-design` only if a primitive/registry change is proposed
- `tdd` for source behavior changes

## Campaign Operating Model

Codex/GPT-5.5 owns:

- Card framing and stop rules.
- Choice of skills and audits.
- Allowed and forbidden write surfaces.
- Final diff review.
- Metric interpretation.
- Promotion or rejection.
- Kanban, registry, and paper-facing updates.

Cursor SDK owns:

- Draft source maps and implementation proposals.
- Disposable-worktree patches for scoped cards.
- Focused tests or smoke commands.
- Run/report drafts that list changed files, test output, caveats, and residual risks.
- Critic lanes that argue against premature promotion.

Promotion rule:

- Cursor-generated code or prose is never copied in as authority. A useful Cursor result is reviewed, then Codex or a human applies a separate source patch in the main workspace.

## Required Workflow Shape

Every A-path card should run through this sequence:

1. **Frame**: Codex writes a short card mission brief with benchmark target, input artifacts, allowed write surfaces, forbidden changes, validation gates, and stop rules.
2. **Rehearse**: Run a prompt-only Cursor SDK draft for the mission brief when the card is high-risk or touches shared source.
3. **Isolate**: Create a disposable worktree for any live mutation.
4. **Delegate**: Run one Cursor implementation lane at a time, or independent lanes that do not touch the same files.
5. **Inspect**: Require Cursor to produce a report with changed files, tests, run IDs, metric deltas, caveats, and risks.
6. **Review**: Codex reads the diff and primary artifacts, reruns focused validation, and either rejects, revises, or manually promotes.
7. **Record**: Update the Kanban, inspection notes, registry rows, and research memory only after source-backed review.

## Pathway A Card Plan

| Card | Cursor role | Write surface | Validation gate | Promotion decision |
| --- | --- | --- | --- | --- |
| A1. Frequency residual audit | Retrospective critic/source-map lane only, because the Codex audit already exists. | Review draft only; no source edits. | Confirm A1 residual categories against `errors.json`, `predictions.json`, and `load_exect_gold_documents()`. | Promote only corrections to the A1 note if Cursor finds source-backed mistakes. |
| A2. Candidate-constrained frequency verifier | Implementation lane plus regression lane. | Program variant, prompt module, config, tests, and inspection draft in disposable worktree. | Cap-25 run beats or matches high-recall frequency recall while improving precision; no guard-family regression beyond preregistered threshold. | Promote as arm only after Codex reruns focused tests and reviews cap-25 artifacts. |
| A3. Frequency prompt/policy refinement | Prompt-policy implementation lane plus critic lane. | Prompt/config variants and tests for prompt routing; no scorer edits. | Cap-25 improves frequency F1 and preserves medication/diagnosis/seizure-type/investigation. Full validation only if cap-25 clears. | Promote only if metric deltas cite run IDs, scorer mode, denominator, and caveats. |
| A4. Medication temporal evidence guard | Design/prereg lane first, then implementation only if prereg passes. | Prereg note, optional guard primitive/program variant/tests; no medication scorer change. | Cap-25 medication precision improves without recall collapse and without changing S5 family definition. | Keep separate from A2/A3; do not merge with frequency work. |
| A5. S2/S3 middle-ladder reruns | Runner/report lane only. | Config/run docs/registry-compatible inspection notes; no source changes unless stale configs fail. | Reruns complete with stable scorer semantics and caveats that family sets differ. | Promote as paper anchor only if D1/D3 require these rows. |

## Detailed Card Slices

### A1 Retrospective Cursor Review

Purpose: recover the intended independent Cursor review signal without redoing the whole audit.

Cursor task:

- Read `docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md`.
- Read primary artifacts from `runs/exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z`.
- Check whether the residual categories and per-document labels are source-backed.
- Report discrepancies only; do not rewrite the note.

Validation:

- Review draft lists checked documents and exact primary artifact paths.
- Any proposed correction includes document ID, current wording, source evidence, and replacement wording.

### A2 Candidate-Constrained Frequency Verifier

Hypothesis:

- A verifier over high-recall candidates can reject unsupported qualitative and historical labels without losing the recall that high-precision pruning lost.

Cursor lanes:

| Lane | Task | Files allowed in disposable worktree |
| --- | --- | --- |
| Implementation | Build the smallest verifier/program variant and cap-25 config. | `src/clinical_extraction/experiments/*`, `src/clinical_extraction/programs/*`, `configs/experiments/*`, `tests/*` |
| Regression | Try to break evidence support, S5 field-family isolation, and medication guard stability. | Tests and review report only |
| Critic | Argue whether the verifier is just a hidden scorer change or recall-suppressing candidate pruning. | Review report only |

Stop rules:

- Stop if the verifier changes gold/scorer behavior.
- Stop if it discards candidate labels without note-evidence rationale.
- Stop if cap-25 recall drops materially versus high-recall pre-vocab.

### A3 Frequency Prompt/Policy Refinement

Hypothesis:

- Prompt guidance can reduce qualitative over-emission and temporal-scope errors while keeping candidate density unchanged.

Cursor lanes:

| Lane | Task | Files allowed in disposable worktree |
| --- | --- | --- |
| Prompt implementation | Draft one compact policy variant for qualitative labels, historical rates, limited seizure-free intervals, and multi-type frequency. | Prompt/config/program variant files and tests |
| A1 example harness | Build or reuse a small fixture/checklist from A1 examples to inspect output policy behavior. | Tests or analysis scripts |
| Critic | Check whether the prompt encodes gold-policy caveats as if they were clinical truth. | Review report only |

Validation:

- Cap-25 before full validation.
- Report per-family F1, precision, recall, and evidence quote support separately.
- Compare against high-recall pre-vocab cap-25 and full-validation baseline only when the split and scorer mode match.

### A4 Medication Temporal Evidence Guard

Hypothesis:

- A narrow planned/history/future ASM guard may reduce residual medication precision leakage, but it is policy-risky because S5 excludes medication temporality.

Cursor lanes:

| Lane | Task | Files allowed in disposable worktree |
| --- | --- | --- |
| Prereg/design | Draft the intervention and explicitly state why it is not a scorer or S5 definition change. | Design/prereg doc only |
| Implementation | Only after prereg approval, implement guard or prompt variant. | Guard/program/config/tests |
| Regression | Check current-medication recall, brand alias handling, and non-ASM filtering. | Tests/report only |

Validation:

- Must preserve the existing annotated-medication guard outcome.
- Must not import medication temporality into S5 scoring.
- Must report annotation-policy ambiguity rather than treating planned/history labels as corrected gold.

### A5 S2/S3 Middle-Ladder Reruns

Purpose:

- Refresh paper anchors only if D1/D3 table-freeze work needs intermediate schema ladder rows.

Cursor role:

- Runner/report assistant, not source implementer.

Validation:

- Use existing configs unless a stale config failure is source-backed.
- Report family sets explicitly because S2/S3/S5 micro F1 are not directly comparable.
- Preserve run IDs, configs, scorer modes, model/provider, split, and caveats.

## Dependency Board

| Card | Status | Owner | Dependencies | Parallelizable | Definition of done |
| --- | --- | --- | --- | --- | --- |
| A0. Add Pathway A Cursor workflow template | Completed | Codex + Cursor SDK | Existing wrapper | no | `pathway-a-card` supports prompt-only and disposable-worktree implementation lanes with ledger metadata. |
| A1R. Retrospective A1 Cursor review | Completed | Cursor review lane, Codex reviewer | A1 audit exists | yes | Review confirmed A1 and promoted one source-backed table correction. |
| A2D. A2 verifier design brief | Completed | Codex | A1 audit | yes | Mission brief names hypothesis, controls, files, stop rules, and cap-25 gate. |
| A2I. A2 verifier implementation pilot | Completed; hold as arm | Cursor implementation lane + Codex manual promotion/review | A0, A2D | no | Implemented verifier config and run `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T193119Z`; F1 improved but recall gate failed. |
| A2R. A2 regression/critic review | Completed | Cursor critic + Codex | A2I | yes after implementation | Explain recall loss and verify scorer preservation. Report at [20260524T203900Z_pathway_a_card_report.md](pathway_a/20260524T203900Z_pathway_a_card_report.md). |
| A3D. A3 prompt-policy design brief | Completed | Codex | A1 audit | yes | Brief names exact policy knobs and examples from A1. |
| A3I. A3 prompt-policy pilot | Ready after A0/A3D | Cursor implementation lane | A0, A3D | no if touching same prompts as A2 | Cap-25 artifact and comparison report. |
| A4P. A4 medication guard prereg | Backlog | Cursor draft + Codex reviewer | AM guard inspection | yes, separate from frequency | Prereg accepted or rejected before code changes. |
| A4I. A4 guard implementation pilot | Blocked | Cursor implementation lane | A4P approval | no | Disposable-worktree diff, tests, cap-25 run/report. |
| A5R. S2/S3 rerun need decision | Backlog | Codex | D1/D3 paper-table needs | yes | Decision note says rerun needed or not needed. |
| A5E. S2/S3 execution/reporting | Blocked | Cursor runner/report lane | A5R says needed | yes | Run IDs, configs, scorer modes, caveats, and inspection notes. |

## Parallelization Opportunities

Safe to run immediately:

- A0 workflow-template design.
- A1R retrospective Cursor review.
- A2D verifier design brief.
- A3D prompt-policy design brief.
- A4P prereg draft, if medication precision becomes urgent.

Should stay single-threaded:

- A2I and A3I if they touch the same prompt/program/config files.
- Any scorer-adjacent primitive or bridge change.
- Any Kanban, registry, or operational-default promotion.

Blocked:

- A2I and A3I until A0 exists or a temporary card-specific disposable-worktree prompt is approved.
- A4I until A4P is reviewed.
- A5E until paper evidence freeze says S2/S3 reruns are needed.

## Recommended First Pull

1. Add or rehearse an A-path Cursor SDK card workflow template.
2. Run A1R as a review-only Cursor lane against the completed A1 note.
3. Draft A2D and A3D in parallel, then choose only one implementation pilot to run first.
4. Prefer A2I first if the goal is precision repair without changing candidate density; prefer A3I first if the team wants a lower-code prompt-policy arm.

## Minimum Prompt Contract For A-Path Cursor Runs

Each Cursor SDK prompt should include:

- Card ID and title.
- Dataset, split, schema level, scorer mode, and model/provider.
- Primary source paths.
- Allowed write surfaces.
- Forbidden changes.
- Exact validation commands or run gates.
- Required report shape.
- Stop rules.
- Instruction that draft prose is not source-of-truth evidence.

Required report shape:

```text
# Cursor SDK Pathway A Card Report

## Card
## Sources Read
## Changes Proposed Or Made
## Tests / Runs
## Metric Claims
## Scorer / Dataset Semantics Check
## Risks
## Promotion Recommendation
```

## Open Decisions

1. Whether to extend `scripts/cursor_sdk_workflows.py` with a first-class `pathway-a-card` workflow, or keep A-path prompts as manually generated prompt-only artifacts until A2 design is stable.
2. Whether A2 and A3 should be competing arms or a staged verifier-plus-policy sequence.
3. What guard-family regression threshold is acceptable on cap-25 before full validation is allowed.
4. Whether gold-empty clinical-frequency examples from A1 deserve a separate gold-policy review card outside Pathway A.

## Final Guardrails

- Cursor can accelerate implementation, but it cannot certify research claims.
- Every metric must name run ID, config, split, model/provider, scorer mode, denominator, and caveat.
- Every source edit must survive Codex diff review and focused validation.
- A-path implementation must preserve ExECT audit guidance: frequency rows are not seizure-type gold, certainty/specificity policies remain fixed, and medication temporality stays outside S5 unless explicitly reopened.
- High-recall frequency candidates remain the baseline; high-precision pruning is already rejected as an arm.
