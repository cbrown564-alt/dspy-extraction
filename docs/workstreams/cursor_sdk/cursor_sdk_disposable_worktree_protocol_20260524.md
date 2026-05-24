# Cursor SDK Disposable Worktree Protocol

Date: 2026-05-24
Status: Active protocol for gated mutation pilots
Decision scope: operational

## Purpose

This protocol defines the minimum safety boundary for live Cursor SDK workflows that may edit files. It exists because the shared workspace can contain valuable uncommitted research code, and a previous mutation workflow used a rollback command against that shared workspace.

Live mutation workflows must run only in a disposable clone or git worktree. The shared repository remains reserved for reviewed Codex or human patches.

## Required Boundary

A live mutation run is allowed only when all conditions are true:

- The workspace is a throwaway clone or git worktree.
- The workspace contains a `.cursor-sdk-disposable-worktree` marker file at its root.
- `CURSOR_SDK_ALLOW_MUTATING_WORKFLOW=disposable-worktree` is set for that process.
- `git status --short` is empty before the SDK agent starts.
- The agent captures `git diff` and focused test output before rollback.
- The agent restores only the disposable workspace and verifies `git status` is clean before ending.

The marker file is intentionally separate from the environment variable. The variable is a per-run assertion; the marker is a visible filesystem assertion that the current root is not the main working directory.

## Setup Pattern

From the shared repo, create a disposable sibling worktree:

```powershell
git worktree add --detach ..\dspy-extraction-cursor-disposable HEAD
Set-Content -Path ..\dspy-extraction-cursor-disposable\.cursor-sdk-disposable-worktree -Value "Disposable Cursor SDK mutation workspace"
```

Then run live mutation workflows from the disposable workspace:

```powershell
cd ..\dspy-extraction-cursor-disposable
$env:CURSOR_SDK_ALLOW_MUTATING_WORKFLOW = "disposable-worktree"
uv run python scripts/cursor_sdk_workflows.py test-mutations
```

## Rollback Pattern

Inside the disposable workspace only, a mutation agent may restore the workspace after capturing its diff and tests:

```powershell
git diff
git restore --staged --worktree .
git status --short
```

Do not use rollback commands as a substitute for the disposable boundary. A clean status in the main workspace is not enough to approve mutation workflows.

## Promotion Boundary

Mutation reports are review artifacts. A useful report may contain:

- proposed diff
- focused test output
- regression notes
- failure analysis
- final clean-status proof

Promotion into the shared workspace requires a separate Codex or human patch after review. SDK-generated diffs are not applied directly to source-of-truth files.
