# Cursor SDK Value And Reliability Assessment

Date: 2026-05-23  
Status: Review complete  
Decision scope: operational tooling only  
Primary board: `docs/planning/kanban_plan.md`

## Current Read

The Cursor Python SDK implementation is a useful research-operations assistant for this repository when it is kept in a review-only role. The strongest evidence comes from the pilot outputs: the memory pass identified stale handoff state, the inspection draft captured Gan G15 run metadata and caveats accurately, and the hygiene scan found real cross-document drift that would otherwise mislead future agents. The implementation is not evidence for clinical extraction quality, not a benchmark model track, and not a safe autonomous code editor in the main dirty workspace.

## Sources Reviewed

- `docs/planning/kanban_plan.md`
- `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md`
- `scripts/cursor_sdk_workflows.py`
- `docs/memory/dreams/20260523T093633Z_cursor_sdk_memory_pass_candidate.md`
- `docs/experiments/cursor_sdk_drafts/20260523T101141Z_inspection_draft.md`
- `docs/workstreams/cursor_sdk/hygiene_scans/20260523T101227Z_hygiene_scan.md`
- `docs/workstreams/cursor_sdk/compatibility/20260523T160418Z_model_compatibility_report.md`
- `docs/experiments/cursor_sdk_drafts/20260523T160219Z_paper_synthesis_draft.md`
- `docs/experiments/cursor_sdk_drafts/20260523T160319Z_adapter_mutation_draft.md`
- `docs/experiments/cursor_sdk_drafts/20260523T161218Z_mutation_test_report.md`
- `docs/experiments/cursor_sdk_drafts/20260523T163121Z_inspection_draft.md`
- `pyproject.toml`

## Implementation Assessment

### Value

The SDK is valuable where the task is broad, source-heavy, and review-oriented:

- It reads many project artifacts and produces structured drafts with source paths.
- It is good at spotting stale planning state, duplicated operational-default claims, missing registry rows, and workflow ownership gaps.
- It produces useful first-pass inspection notes that preserve dataset, split, model, scorer, evidence policy, and decision-scope caveats.
- It can draft paper-claim maps and compatibility reports that accelerate human review.

The highest downstream value is not model quality improvement directly. It is reducing the overhead of research memory, artifact inspection, and repo-hygiene review so that Codex/human attention can stay on scorer integrity, dataset policy, and experiment decisions.

### Reliability

Reliability is good for review-only drafting and moderate for technical diagnosis. The successful C1-C3 pilot met the promotion criterion: at least two useful drafts and zero source-of-truth edits by the SDK agent. Later drafts also produced useful leads, especially the model-compatibility report and the full-validation inspection draft that flagged a slice/full candidate-emission mismatch.

Reliability is not high enough for unsupervised source-of-truth changes. The mutation-test workflow is the clearest warning: it ran against a dirty workspace, then used `git checkout -- src/clinical_extraction/gan/temporal_candidates.py`, which restored the file to committed HEAD rather than the pre-session dirty state. That is acceptable only in a disposable clone or explicitly prepared worktree, not as an unattended workflow in the shared project workspace.

### Appropriate Scope

Keep:

- memory pass drafts
- experiment-inspection drafts
- repo hygiene scans
- paper narrative synthesis drafts
- model-compatibility scans
- adapter or prompt mutation proposals as prose only
- post-run anomaly triage reports

Correct / constrain:

- Move any code-mutating SDK workflow behind an explicit disposable-worktree requirement.
- Treat generated drafts as review inputs, not canonical docs.
- Add stronger prompts requiring exact source paths, missing-context flags, decision scopes, and no edits.
- Consider moving `cursor-sdk` from core runtime dependencies to an optional/dev dependency if the workflow remains operations-only.

Defer or stop in the main workspace:

- autonomous edits to scorers, loaders, registry rows, clinical schemas, or experiment configs
- direct promotion of generated memory into `session_brief.md`
- mutation testing that edits and rolls back files in a dirty tree
- any use with real clinical or sensitive data

## Reliability Risks

| Risk | Severity | Evidence | Mitigation |
| --- | --- | --- | --- |
| Confident prose from incomplete context | Medium | C1 explicitly listed several G11-G15 docs as not independently opened | Require `Sources Read` plus `Not Read` sections |
| Source-of-truth drift from generated drafts | Medium | Hygiene scan found stale Kanban/memory/mechanism defaults | Keep SDK output in draft folders only |
| Dirty-worktree mutation damage | High | Mutation-test report restored `temporal_candidates.py` to committed HEAD, not dirty baseline | Run mutating workflows only in disposable clone/worktree |
| Cost growth on broad scans | Medium | Full validation and paper synthesis prompts can read many files | Keep GBP 15 guard; prefer narrow topics |
| Dependency surface creep | Low-medium | `cursor-sdk>=0.1.5` is in core `dependencies` | Consider optional/dev dependency after next packaging review |
| Benchmark contamination | High | Generated prose could be mistaken for paper evidence | Require primary run IDs, configs, scorer mode, and caveats |

## Tasks Well-Suited For Autonomous Multi-Hour Runs Tonight

These are safe because they produce drafts only and can run while human attention is elsewhere.

### 1. Paper Claim Map Refresh

Command:

```powershell
uv run python scripts/cursor_sdk_workflows.py paper-synthesis --topic "post-G16 model-suite and Gan builder-gap paper claim map"
```

Expected output: `docs/experiments/cursor_sdk_drafts/<timestamp>_paper_synthesis_draft.md`

Why it is suitable: It can read registry, narrative reports, and planning docs and produce a claim-to-artifact table. Human review can later decide which claims are paper-ready.

Validation: The draft must list exact run IDs, metric paths, decision scopes, and unsupported claims.

### 2. Full-Validation Inspection Drafts

Command pattern:

```powershell
uv run python scripts/cursor_sdk_workflows.py inspection-draft --topic "<run/topic>" --run-dir runs/<run_id>
```

Candidate topic tonight: G16 / `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T161524Z`, with explicit instruction to reconcile slice-vs-full candidate-emission mismatch.

Why it is suitable: Inspection drafting is one of the best pilot successes. It is artifact-heavy, structured, and review-only.

Validation: The draft must separate facts from interpretation, identify comparison controls, and end with required human checks.

### 3. Repo Hygiene Scan After Board Refresh

Command:

```powershell
uv run python scripts/cursor_sdk_workflows.py hygiene-scan
```

Why it is suitable: The first hygiene scan found real planning drift. A second scan after current updates can check whether the board, memory, mechanism status, and workflow index remain coherent.

Validation: Findings must be ranked by risk and must not propose direct scorer/dataset/registry edits without review.

### 4. Model Compatibility Follow-Up

Command:

```powershell
uv run python scripts/cursor_sdk_workflows.py model-compatibility
```

Why it is suitable: This is a bounded technical scan. It is useful while Qwen/Ollama jobs are idle or while hosted API jobs run separately.

Validation: It should produce provider-specific config risks and test suggestions, not apply patches.

### 5. Adapter Mutation Proposal, Prose Only

Command:

```powershell
uv run python scripts/cursor_sdk_workflows.py adapter-mutation
```

Why it is suitable: It can synthesize error taxonomies and candidate-builder gaps into proposed helper families and tests.

Validation: It must label already-implemented helpers, identify blocked policy questions, and avoid claiming that proposals passed tests.

### 6. Draft Review Queue Consolidation

Command pattern:

```powershell
uv run python scripts/cursor_sdk_workflows.py memory-pass
```

Why it is suitable: It can consolidate new drafts into a review queue without editing promoted memory.

Validation: The output must name target files, exact source paths, confidence levels, and promotion checklist status.

## Tasks Not Suitable For Autonomous Cursor SDK Runs Tonight

- `test-mutations` in the current workspace.
- Any workflow that edits `src/clinical_extraction/gan/temporal_candidates.py`, scorer code, dataset loaders, schema models, registry rows, or Kanban directly.
- Long local Ollama inference launched through Cursor/IDE background shells. Use detached PowerShell launchers and log monitoring instead.
- Any task involving real clinical data or sensitive notes.

## Recommended Operating Mode Tonight

Run the SDK as a background drafting assistant in 2-4 independent passes, each writing to `docs/experiments/cursor_sdk_drafts/` or `docs/workstreams/cursor_sdk/`. Keep the main workspace source-of-truth untouched until a human/Codex review pass promotes selected findings.

Suggested sequence:

1. Run a targeted G16 inspection draft.
2. Run paper-synthesis after the inspection draft exists.
3. Run model-compatibility or hygiene-scan as the long background pass.
4. Do not run `test-mutations` unless a clean disposable worktree has been created and the rollback target is that worktree only.

## Supervisor Judgment

Continue the Cursor SDK workstream, but narrow its authority. The implementation has real value as a second-pass research operations reviewer and can safely run unattended for multi-hour draft production. Its appropriate boundary is artifact synthesis, contradiction discovery, and proposal drafting. It should not autonomously mutate the research codebase or canonical research memory until the project has a disposable-worktree harness and stricter rollback guarantees.

