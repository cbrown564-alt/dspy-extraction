---
name: cursor-sdk-research-ops
description: Use when planning, running, reviewing, or promoting Cursor SDK workflows in this repo, including review-only agent swarms, paper-synthesis drafts, experiment-inspection drafts, memory passes, hygiene scans, model-compatibility reviews, adapter/mutation proposals, disposable-worktree mutation pilots, or any task that mentions the Cursor SDK as a research-operations assistant.
---

# Cursor SDK Research Ops

## Overview

Use Cursor SDK as a bounded research-operations assistant: useful for parallel drafting, contradiction discovery, source mapping, and proposal generation; not authoritative for benchmark evidence, scorer semantics, registry rows, dataset policy, or source-of-truth edits.

Primary project docs:

- `docs/workstreams/cursor_sdk/README.md`
- `docs/workstreams/cursor_sdk/cursor_sdk_review_queue_20260524.md`
- `docs/workstreams/cursor_sdk/cursor_sdk_run_ledger_20260524.md`
- `docs/workstreams/cursor_sdk/cursor_sdk_draft_index_20260524.md`
- `docs/workstreams/cursor_sdk/cursor_sdk_disposable_worktree_protocol_20260524.md`
- `scripts/cursor_sdk_workflows.py`

Read `references/source-map.md` when choosing a workflow or designing a swarm.

## Hard Rules

- Treat every SDK output as `needs_review` until source paths and claims are checked against primary artifacts.
- Do not cite SDK drafts as paper evidence, benchmark evidence, registry evidence, scorer evidence, or dataset-policy evidence.
- Do not promote SDK prose directly. Apply any verified claim through a separate Codex or human patch.
- Do not allow live mutation in the shared workspace.
- Do not run high-volume SDK swarms without checking the JSONL ledger and draft index first.
- Keep `decision_scope` explicit: `operational`, `arm`, `mechanism`, `open`, `blocked`, or `stale_check`.
- If a workflow touches loaders, scorers, schemas, splits, gold labels, experiment configs, or model runs, also use the relevant project skill before acting on any SDK output.

## Workflow Choice

Run a sanity check before live use:

```powershell
uv run python scripts/cursor_sdk_workflows.py check
```

Use prompt rehearsal first when the topic is broad, risky, or likely to create review burden:

```powershell
uv run python scripts/cursor_sdk_workflows.py <workflow> --prompt-only --topic "<specific topic>"
```

Review-only live workflows:

```powershell
uv run python scripts/cursor_sdk_workflows.py memory-pass
uv run python scripts/cursor_sdk_workflows.py inspection-draft --topic "<topic>" --run-dir runs/<run_id>
uv run python scripts/cursor_sdk_workflows.py hygiene-scan
uv run python scripts/cursor_sdk_workflows.py paper-synthesis --topic "<topic>"
uv run python scripts/cursor_sdk_workflows.py model-compatibility
uv run python scripts/cursor_sdk_workflows.py adapter-mutation
```

Live mutation workflows are allowed only in a disposable worktree:

```powershell
git worktree add --detach ..\dspy-extraction-cursor-disposable HEAD
Set-Content -Path ..\dspy-extraction-cursor-disposable\.cursor-sdk-disposable-worktree -Value "Disposable Cursor SDK mutation workspace"
cd ..\dspy-extraction-cursor-disposable
$env:CURSOR_SDK_ALLOW_MUTATING_WORKFLOW = "disposable-worktree"
uv run python scripts/cursor_sdk_workflows.py test-mutations
```

The mutation report is a proposal only. Reimplement or patch useful changes separately in the shared workspace after review.

## Swarm Pattern

Use swarms for independent review lanes, not for source-of-truth editing. A good swarm has disjoint roles, a source manifest, and a synthesis pass that verifies claims before promotion.

Good lanes for the current research program:

- Gan evidence lane: inspect Gan stage-graph, stage-executor, builder-gap, Qwen transfer, and residual-forensics sources.
- ExECT S1 lane: inspect S1 stage-graph, stage-executor, verification, optimizer, and interleaving artifacts.
- ExECT S4/S5 lane: inspect broad-ladder, S5 surface, frequency audit, and sparse-family caveats.
- Registry/metrics lane: reconcile run IDs, configs, scorer modes, denominators, and metric caveats.
- Critic lane: try to falsify proposed report claims against primary artifacts and identify confounds.

For each lane, require:

- source paths read
- claims supported
- claims not supported
- missing/confounded comparisons
- recommended wording and decision scope
- whether any cited SDK draft needs promotion, rejection, or archival

## Review And Promotion

After any SDK run or swarm:

- Open `docs/workstreams/cursor_sdk/cursor_sdk_runs.jsonl` and record the run IDs/output paths used.
- Check `docs/workstreams/cursor_sdk/cursor_sdk_review_queue_20260524.md` before reading archived drafts.
- Verify every metric against `runs/*/metrics.json`, promoted inspection docs, or `docs/experiments/synthesis/experiment_registry.json`.
- Prefer promoted source docs over SDK drafts. If an SDK draft is useful, promote only specific verified claims.
- Update the review queue or a promoted source document with the review decision when the task materially depends on SDK output.

## Anti-Patterns

- Running a broad paper-synthesis swarm and pasting its prose into the manuscript without source verification.
- Letting SDK drafts redefine the active Kanban, operational defaults, benchmark status, or scorer semantics.
- Treating prompt rehearsals as live agent findings.
- Using mutation reports as patches.
- Comparing metrics across changed scorer semantics, different splits, capped/full runs, or invalid denominators without caveats.
- Closing a mechanism based on one SDK draft or one failed arm.
