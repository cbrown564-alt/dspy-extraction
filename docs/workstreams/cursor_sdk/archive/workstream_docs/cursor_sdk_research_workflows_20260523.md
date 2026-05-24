# Cursor SDK Research Workflows

Date: 2026-05-23
Status: Promoted review-only operating mode
Decision scope: operational
Confidence: direct_source

## Purpose

Use the Cursor Python SDK as a review-only research operations assistant for this repository. The SDK should help draft memory, inspection, and hygiene artifacts, but it should not become part of the clinical extraction pipeline, scorer, benchmark model set, or DSPy optimizer evidence.

The promoted operating mode is intentionally narrow:

- SDK outputs are drafts for Codex or human review.
- Source-of-truth edits happen only through the normal repo workflow after review.
- Mutating SDK workflows are blocked in the shared workspace.

The reviewed read-only workflows are:

- automated research-memory passes
- experiment-inspection draft worker
- background repo hygiene
- paper narrative synthesis drafts
- model compatibility reports
- adapter/prompt mutation drafts that do not edit files

## Setup

Dependency:

```powershell
uv add cursor-sdk
```

Local credential:

```text
CURSOR_API_KEY=<set in .env>
```

Sanity check:

```powershell
uv run python scripts/cursor_sdk_workflows.py check
```

The runner loads `.env`, verifies only that `CURSOR_API_KEY` is present, and does not print the key. Draft-producing commands use local Cursor agents rooted at the repository directory.

Windows note: `scripts/cursor_sdk_workflows.py` installs a local Windows-only bridge-discovery patch before live SDK calls because `cursor-sdk` 0.1.5 uses `selectors` on the bridge stderr pipe, which fails on Windows pipe handles. The patch is scoped to this runner and does not modify the installed SDK package.

## Instrumentation

Every prompt rehearsal or live draft run appends operational metadata to:

```text
docs/workstreams/cursor_sdk/cursor_sdk_runs.jsonl
```

The human-readable ledger contract is `docs/workstreams/cursor_sdk/cursor_sdk_run_ledger_20260524.md`. Existing outputs are indexed in `docs/workstreams/cursor_sdk/cursor_sdk_draft_index_20260524.md`.

Default prompt-only outputs now include `_prompt_rehearsal` in the filename. Live outputs keep the existing draft/report suffixes.

The disposable mutation protocol is `docs/workstreams/cursor_sdk/cursor_sdk_disposable_worktree_protocol_20260524.md`.

## Shared Guardrails

- Drafts are review artifacts, not source-of-truth updates.
- The SDK agent must not directly edit docs, code, registry rows, scorer behavior, dataset policy, or run artifacts.
- Dataset audits and policies outrank all generated drafts.
- Drafts must include concrete source paths for claims.
- Drafts must preserve decision scope labels: `operational`, `arm`, `mechanism`, `open`, `blocked`, or `stale_check`.
- Clinical extraction results must keep dataset, split, schema level, model/provider, program variant, scorer mode, normalization rules, and evidence policy explicit.
- Do not treat Cursor/Composer output as a benchmark result or model-comparison track for clinical extraction.
- Use the existing GBP 15 spend limit as a budget guard for the pilot.

## Canonical Draft Folders

| Draft type | Canonical folder |
| --- | --- |
| Memory consolidation candidates | `docs/memory/dreams/` |
| Experiment-inspection drafts | `docs/experiments/cursor_sdk_drafts/` |
| Paper-synthesis drafts | `docs/experiments/cursor_sdk_drafts/` |
| Adapter/prompt mutation drafts | `docs/experiments/cursor_sdk_drafts/` |
| Hygiene scans | `docs/workstreams/cursor_sdk/hygiene_scans/` |
| Model compatibility reports | `docs/workstreams/cursor_sdk/compatibility/` |

Drafts in these folders are not registry rows, inspection docs, paper claims, or Kanban updates until a reviewer promotes specific claims into source docs.

## Draft-To-Source Promotion Boundary

Promotion requires a reviewer to:

1. Check every cited source path exists.
2. Confirm dataset, split, model/provider, program variant, scorer mode, normalization rules, and evidence policy when an experiment is discussed.
3. Preserve decision scope labels: `operational`, `arm`, `mechanism`, `open`, `blocked`, or `stale_check`.
4. Reject claims that rely on SDK prose instead of primary artifacts.
5. Apply source edits through normal Codex/human patches, not by asking the SDK agent to rewrite source-of-truth files directly.

## Mutating Workflow Block

`scripts/cursor_sdk_workflows.py test-mutations` is not approved for live use in the shared repository. It may be used with `--prompt-only` to inspect the planned mutation-test prompt, but live execution is blocked unless the operator is in a disposable clone or worktree and explicitly sets:

```powershell
$env:CURSOR_SDK_ALLOW_MUTATING_WORKFLOW="disposable-worktree"
```

The disposable workspace must also contain a `.cursor-sdk-disposable-worktree` marker file at its root. The runner refuses live mutation workflows when the marker is missing or the disposable workspace is dirty. This boundary exists because the earlier active mutation workflow rolled back `src/clinical_extraction/gan/temporal_candidates.py` and erased uncommitted Gan candidate-builder code.

Disposable worktree setup:

```powershell
git worktree add --detach ..\dspy-extraction-cursor-disposable HEAD
Set-Content -Path ..\dspy-extraction-cursor-disposable\.cursor-sdk-disposable-worktree -Value "Disposable Cursor SDK mutation workspace"
cd ..\dspy-extraction-cursor-disposable
$env:CURSOR_SDK_ALLOW_MUTATING_WORKFLOW = "disposable-worktree"
uv run python scripts/cursor_sdk_workflows.py test-mutations
```

Mutation reports remain review artifacts. Source promotion still requires a separate reviewed Codex or human patch in the shared repository.

## Workflow 1: Automated Research-Memory Passes

### Question

Can a Cursor SDK agent reduce the cost of cross-session handoff by drafting useful memory candidates from existing source artifacts?

### Inputs

- `docs/memory/README.md`
- `docs/memory/session_brief.md`
- `docs/memory/workflow_index.md`
- `docs/memory/dreams/TEMPLATE.md`
- `docs/planning/kanban_plan.md`
- `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- `docs/experiments/synthesis/experiment_registry.json`

### Command

Prompt-only rehearsal:

```powershell
uv run python scripts/cursor_sdk_workflows.py memory-pass --prompt-only
```

Live draft:

```powershell
uv run python scripts/cursor_sdk_workflows.py memory-pass
```

Default output:

```text
docs/memory/dreams/<timestamp>_cursor_sdk_memory_pass_candidate.md
```

### Success Criterion

A draft is useful if it identifies at least one reviewable memory update, stale claim, reaffirmed scoped decision, or open question while preserving source paths and decision labels.

### Failure Criterion

Reject or revise the workflow if the draft invents facts, smooths over conflicting source claims, changes source-of-truth wording without review, or turns `arm` evidence into `mechanism` evidence.

## Workflow 2: Experiment-Inspection Draft Worker

### Question

Can a Cursor SDK agent draft a first-pass inspection note from a run directory, config, and project templates without weakening reproducibility standards?

### Inputs

- run directory or artifact pointer
- relevant experiment config and model config
- `docs/templates/experiment_decision_template.md`
- `docs/planning/kanban_plan.md`
- `docs/policies/deterministic_scorer_semantics.md`
- dataset audit for the dataset in scope

### Command

Template/prompt rehearsal:

```powershell
uv run python scripts/cursor_sdk_workflows.py inspection-draft --prompt-only --topic "Gan S0 candidate-builder pilot"
```

Live draft with a run directory:

```powershell
uv run python scripts/cursor_sdk_workflows.py inspection-draft --topic "Gan S0 candidate-builder pilot" --run-dir runs/<run_id>
```

Default output:

```text
docs/experiments/cursor_sdk_drafts/<timestamp>_inspection_draft.md
```

### Success Criterion

A draft is useful if it correctly separates run facts from interpretation, names missing inputs, preserves scorer and dataset caveats, and ends with explicit human checks before promotion into `docs/experiments/`.

### Failure Criterion

Reject or revise the workflow if it overstates a result, compares across changed scorer semantics, omits split/model/scorer details, or treats capped exploratory results as full-validation or test evidence.

## Workflow 3: Background Repo Hygiene

### Question

Can a Cursor SDK agent periodically find low-risk documentation and workflow drift without creating another planning surface?

### Inputs

- `docs/planning/kanban_plan.md`
- `docs/memory/`
- `docs/workstreams/`
- `docs/policies/`
- `.agents/skills/`
- `pyproject.toml`

### Command

Prompt-only rehearsal:

```powershell
uv run python scripts/cursor_sdk_workflows.py hygiene-scan --prompt-only
```

Live draft:

```powershell
uv run python scripts/cursor_sdk_workflows.py hygiene-scan
```

Default output:

```text
docs/workstreams/cursor_sdk/hygiene_scans/<timestamp>_hygiene_scan.md
```

### Success Criterion

A scan is useful if it finds actionable contradictions, stale references, missing links, duplicate source-of-truth claims, or workflow ownership gaps, and ranks them by risk.

### Failure Criterion

Reject or revise the workflow if it proposes broad rewrites, treats generated memory as authoritative, or touches scorer semantics, dataset policy, registry rows, or operational defaults without explicit review.

## Pilot Evaluation

All three workflows were tested and evaluated in separate runs:

| Workflow | Primary Output | Evaluation / Outcome |
| --- | --- | --- |
| Automated research-memory pass | `docs/memory/dreams/20260523T093633Z_cursor_sdk_memory_pass_candidate.md` | **Useful (C1 passed)**. Identified critical session-brief/workflow-index updates and stale questions. Strictly review-only. |
| Experiment-inspection draft worker | `docs/experiments/cursor_sdk_drafts/20260523T101141Z_inspection_draft.md` | **Useful (C2 passed)**. Extracted accurate metadata, runtime, and accuracy rates directly from runs. Scoped decision recommendation to arm/slice-gate and listed required human checks. |
| Background repo hygiene | `docs/workstreams/cursor_sdk/hygiene_scans/20260523T101227Z_hygiene_scan.md` | **Useful (C3 passed)**. Identified 12 actionable findings (ranked by risk), highlighting operational default conflicts, stale memory briefs, and registry validation discrepancies. |

**Evaluation Result:** Promoted. The pilot met the promotion threshold of at least two useful drafts with zero direct edits to source-of-truth files by the SDK agent. The SDK runner is approved for ongoing review-only operations.

## Open Risks

- Token spend can grow quickly on broad repo scans despite the GBP 15 limit.
- Cursor/Composer output may sound confident when it has not read enough source context.
- Generated drafts may duplicate memory or Kanban if prompts are too broad.
- Cloud or SDK data handling should remain out of any real clinical or sensitive-data workflow unless separately reviewed.

## Status

**Completed & Promoted.** The pilot succeeded on 2026-05-23. The Cursor Python SDK remains in place as a review-only research operations assistant. All memory and registry updates identified in the pilot have been manually promoted/resolved. Live mutating workflows remain blocked outside disposable worktrees.
