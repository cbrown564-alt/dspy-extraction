# Cursor SDK Workstream

Status: Active review-only operations surface  
Last consolidated: 2026-05-24  
Decision scope: operational tooling only

## Current Position

Cursor SDK is approved only as a review-only research-operations assistant. It may draft memory candidates, experiment inspections, hygiene scans, compatibility reports, paper-claim maps, and mutation proposals. It is not part of the clinical extraction pipeline, not benchmark evidence, not a model-comparison track, and not an authority for scorer, loader, registry, schema, or dataset-policy edits.

The prior pilot and evening queue generated useful leads, but also created review burden. This directory is now the small active surface:

| File | Purpose |
| --- | --- |
| `README.md` | Current operating guide and source of truth for the SDK workstream. |
| `cursor_sdk_review_queue_20260524.md` | Current review queue after archiving old generated drafts. |
| `cursor_sdk_draft_index_20260524.md` | Archive map and status vocabulary for old SDK outputs. |
| `cursor_sdk_run_ledger_20260524.md` | Human-readable contract for `cursor_sdk_runs.jsonl`. |
| `cursor_sdk_runs.jsonl` | Machine ledger for SDK workflow attempts. |
| `cursor_sdk_disposable_worktree_protocol_20260524.md` | Required boundary for live mutating workflows. |
| `archive/` | Superseded drafts, prompt rehearsals, old reports, and historical workstream docs. |

## Operating Rules

- Treat every SDK output as `needs_review` until a reviewer verifies the cited source paths and claims against primary artifacts.
- Do not cite SDK drafts as paper evidence, benchmark evidence, registry evidence, scorer evidence, or dataset-policy evidence.
- Do not promote SDK prose directly into source-of-truth docs. Promotion requires a separate Codex or human patch.
- Keep generated drafts in their configured output folders only during active review; archive them once indexed.
- Use the active Kanban, audits, policies, run artifacts, configs, and promoted inspection docs as the source of truth.
- Live mutation is blocked in the shared workspace. It is allowed only in a clean disposable clone or git worktree with `.cursor-sdk-disposable-worktree` and `CURSOR_SDK_ALLOW_MUTATING_WORKFLOW=disposable-worktree`.

## Commands

Sanity check:

```powershell
uv run python scripts/cursor_sdk_workflows.py check
```

Review-only drafts:

```powershell
uv run python scripts/cursor_sdk_workflows.py memory-pass
uv run python scripts/cursor_sdk_workflows.py inspection-draft --topic "<topic>" --run-dir runs/<run_id>
uv run python scripts/cursor_sdk_workflows.py hygiene-scan
uv run python scripts/cursor_sdk_workflows.py paper-synthesis
uv run python scripts/cursor_sdk_workflows.py model-compatibility
uv run python scripts/cursor_sdk_workflows.py adapter-mutation
```

Prompt rehearsal:

```powershell
uv run python scripts/cursor_sdk_workflows.py <workflow> --prompt-only
```

Mutation testing:

```powershell
# Shared workspace: blocked
uv run python scripts/cursor_sdk_workflows.py test-mutations --prompt-only

# Live mutation: disposable worktree only
$env:CURSOR_SDK_ALLOW_MUTATING_WORKFLOW = "disposable-worktree"
uv run python scripts/cursor_sdk_workflows.py test-mutations
```

## Review Flow

1. Check `cursor_sdk_runs.jsonl` for run metadata and output path.
2. Check `cursor_sdk_review_queue_20260524.md` before reading an archived draft.
3. Verify all source paths used by the draft.
4. Recompute or open primary artifacts for any metric, run, scorer, or dataset claim.
5. Decide one of: `promote_specific_claims`, `keep_as_lead`, `defer`, `reject`, or `archive_no_action`.
6. Record the decision in the review queue or a promoted source document.

## Current Review Priorities

1. Use the promoted model compatibility backlog through `docs/policies/model_config_compatibility_backlog_20260524.md`, not the archived or active SDK reports. The current promoted follow-ups are B6 (`build_dspy_lm` config-level coverage) and B7 (explicit Gemini `reasoning_effort` policy before broad Gemini comparisons).
2. Use the reviewed Gan mutation-pilot outcome only through `docs/experiments/gan/gan_s0_cursor_sdk_mutation_pilot_review_20260524.md`. No mutation diff is promoted; the only technical lead is the narrow `seizure free for multiple year` candidate gap for `gan_13574`/`gan_13598`.
3. Use the reviewed paper/core-research-question synthesis through `docs/experiments/synthesis/core_research_questions_pipeline_review_20260524.md` and its generated registry appendix, not the archived SDK paper draft.
4. Treat the fresh paper result-table source map `docs/experiments/cursor_sdk_drafts/20260524T131249Z_paper_synthesis_draft.md` as `keep_as_lead` only. It can guide table assembly, but no paper metric or operational-default wording was promoted from it.
5. Use the reviewed ExECT S4/S5 frequency audit promotion only through its promoted audit doc and machine-readable artifact, not the archived SDK draft.
6. Keep remaining Gan, paper-synthesis, memory, and hygiene drafts archived unless a current source task explicitly reopens them.
7. Do not run cloud/PR experiments until there is a specific operational need and the same review-only boundary is preserved.
