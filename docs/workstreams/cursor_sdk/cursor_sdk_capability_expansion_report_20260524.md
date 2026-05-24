# Cursor SDK Capability Expansion Report

Date: 2026-05-24  
Status: Draft for review  
Decision scope: operational tooling and research operations  
Audience: project maintainer / experiment reviewer

## Executive Judgment

The current Cursor SDK implementation proved the narrow case: it is useful as a review-only research-operations worker for memory, inspection, hygiene, compatibility, and paper-synthesis drafts. The pilot was conservative for good reasons, but the external SDK direction and official examples suggest the project can be much more ambitious if it treats the SDK as an orchestrated agent runtime rather than a single background drafter.

The next step should not be "let it edit the main repo." The next step should be a controlled capability expansion: many parallel, typed, disposable, observable agents that produce either review artifacts or isolated PR/worktree patches. The weekend discount window should be used to run high-volume experiments that map the SDK's reliability frontier, especially on tasks that are expensive for a single Codex/human thread: cross-artifact consistency checks, run inspection, error taxonomy synthesis, disposable mutation attempts, and paper-claim validation.

## Evidence Reviewed

Local project evidence:

- `scripts/cursor_sdk_workflows.py`
- `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md`
- `docs/workstreams/cursor_sdk/cursor_sdk_value_reliability_assessment_20260523.md`
- `docs/workstreams/cursor_sdk/hygiene_scans/20260523T101227Z_hygiene_scan.md`
- `docs/workstreams/cursor_sdk/hygiene_scans/20260523T164844Z_hygiene_scan.md`
- `docs/workstreams/cursor_sdk/compatibility/20260523T160418Z_model_compatibility_report.md`
- `docs/workstreams/cursor_sdk/compatibility/20260523T164950Z_model_compatibility_report.md`
- `docs/experiments/cursor_sdk_drafts/`
- `docs/experiments/gan/gan_s0_g16_candidate_builder_gap_incident_report.md`
- `docs/planning/kanban_plan.md`
- `docs/memory/workflow_index.md`

External sources:

- Cursor SDK announcement and usage patterns: [Build programmatic agents with the Cursor SDK](https://cursor.com/blog/typescript-sdk)
- Cursor official agent best practices: [Best practices for coding with agents](https://cursor.com/blog/agent-best-practices)
- Cursor SDK plugin guidance: [Cursor SDK marketplace skill](https://cursor.com/marketplace/cursor/cursor-sdk) and [source skill](https://raw.githubusercontent.com/cursor/plugins/main/cursor-sdk/skills/cursor-sdk/SKILL.md)
- Official examples: [cursor/cookbook](https://github.com/cursor/cookbook), especially SDK quickstart, coding-agent CLI, kanban board, prototyping tool, and DAG task runner
- Composer 2.5 / current pricing context: [Composer 2.5 changelog](https://cursor.com/changelog/composer-2-5) and third-party pricing summaries found during web search. I did not independently verify a "90% off this weekend" claim from an official Cursor pricing page; treat that as user-provided budget context unless the dashboard confirms it.

## Current Implementation Read

The implementation is a Python wrapper around `cursor-sdk>=0.1.5` with one command surface:

- `check`
- `memory-pass`
- `inspection-draft`
- `hygiene-scan`
- `paper-synthesis`
- `adapter-mutation`
- `model-compatibility`
- `test-mutations`

The runner loads `.env`, checks `CURSOR_API_KEY`, sets `LocalAgentOptions(cwd=REPO_ROOT)`, sends a single prompt to a local Cursor agent, and writes the returned text to canonical draft folders. It also carries a Windows-only bridge-discovery patch for `cursor-sdk` 0.1.5, because the SDK's bridge discovery uses selectors on a stderr pipe that fails on Windows pipe handles.

The safety design is now coherent:

- Prompt headers say "Do not edit files."
- Outputs go to draft folders rather than promoted docs.
- The workflow docs preserve decision-scope labels such as `operational`, `arm`, `mechanism`, `open`, `blocked`, and `stale_check`.
- `test-mutations` is blocked unless `CURSOR_SDK_ALLOW_MUTATING_WORKFLOW=disposable-worktree`.
- Live mutation also refuses a dirty disposable workspace.

This is a good minimal operating system, but it is still a single-agent, single-prompt, local-only runner. It does not yet exploit SDK capabilities that external examples emphasize: durable agents, streaming observability, cloud agents, resume, cancellation, dashboards, subagents, MCP, hooks, or DAG orchestration.

## Outcome Review

### What Worked

The pilot met its stated promotion criterion: at least two useful drafts and zero source-of-truth edits by the SDK agent. The workflow doc records three useful pilot outputs:

- C1 memory pass: identified stale session-brief/workflow-index updates and open questions.
- C2 inspection draft: extracted run metadata, runtime, accuracy rates, and caveats from Gan slice artifacts.
- C3 hygiene scan: found 12 actionable cross-document findings, including operational-default conflicts, stale memory, and registry validation discrepancies.

The evening queue also produced meaningful follow-on artifacts:

- G16/full-validation inspection drafts flagged a slice/full candidate-emission mismatch and correctly marked it as `stale_check`.
- Paper-synthesis drafts produced claim-to-artifact maps and repeatedly warned that registry/headline claims needed primary run verification.
- Compatibility reports identified provider config and test coverage gaps without applying changes.
- A later hygiene scan caught the post-pilot bookkeeping problem: multiple drafts existed, but no canonical review index told humans which one to trust.

The strongest value signal is not that the SDK wrote perfect prose. It is that it found real repo drift across many documents faster than a single focused implementation turn usually would.

### What Failed Or Nearly Failed

The dangerous failure was the mutation workflow incident. The incident report states that a Cursor SDK active mutation runner restored `src/clinical_extraction/gan/temporal_candidates.py` using `git checkout -- ...` in a dirty workspace, wiping uncommitted deterministic builder work. That failure is exactly the boundary condition this repo cares about: locally valuable but uncommitted research code can be destroyed by an agent that assumes `HEAD` is a safe rollback target.

There were also softer failures:

- Some prompt-only rehearsal files sit beside substantive drafts, increasing review confusion.
- Multiple drafts per workflow exist without an accepted/canonical pointer.
- SDK-generated paper drafts can preserve stale narratives if not tied to promoted primary artifacts.
- Broad scans can sound more complete than their actual source coverage; some drafts explicitly list important sources not independently opened.
- `cursor-sdk` remains in core dependencies even though the workflow is operational tooling rather than library runtime.

## External Research: Relevant Patterns

Cursor's current SDK positioning is broader than this repo's implementation. The official announcement frames the SDK as a way to run the same agent harness used in Cursor desktop, CLI, and web app from TypeScript, locally or in cloud VMs, with streaming, reconnect, PR creation, model selection, MCP, skills, hooks, and subagents. The official examples include:

- Quickstart: one local agent, one prompt, streamed response.
- Coding agent CLI: local default, cloud switch, model selection, and interactive TUI.
- Prototyping tool: cloud sandbox agents for new-project scaffolding.
- Kanban board: agent-powered work cards that can open PRs and attach results.
- DAG task runner: decomposes a task into a JSON dependency graph, runs independent ranks concurrently, streams status to a Cursor Canvas, enforces timeouts, and passes bounded upstream summaries to child agents.

The Cursor SDK plugin guidance adds practical traps that matter here:

- Choose local vs cloud explicitly; missing runtime config can silently default to local.
- Distinguish startup errors from run failures.
- Dispose agents after use to avoid leaked processes/resources.
- Always wait for terminal run status, even if streaming output.
- Log agent/run IDs immediately for later inspection.
- Use one-shot calls for true one-offs; use durable agents when follow-ups/resume matter.
- Confirm model IDs through the model catalog rather than hardcoding exotic names.

Cursor's agent best-practices article also aligns with the local pilot: rules should be short, point to canonical examples, and specify validation commands. It explicitly calls out long-running loops that continue until a verifiable target is met, such as tests passing or a UI matching a design. That is the pattern to adapt, but only in disposable worktrees for this project.

## Capability Gap

Current runner:

- Single local agent.
- Text-only terminal result.
- No live stream capture.
- No durable run IDs stored in a ledger.
- No resume/follow-up.
- No structured task graph.
- No cost/usage capture.
- No cloud or PR mode.
- No dashboard/canvas.
- No canonical draft index.
- No automatic source coverage audit.

Ambitious target:

- A batch orchestrator that can launch many bounded agents across independent cards.
- A run ledger storing prompt, workflow, model, runtime, output path, start/end time, status, sources claimed, and human-review result.
- Separate lanes for review-only local runs, disposable-worktree mutation runs, and cloud PR experiments.
- A DAG mode for multi-step research jobs where upstream audit/inspection outputs feed downstream synthesis.
- An SDK draft review index that marks `stub`, `substantive`, `superseded`, `accepted_for_review`, `promoted`, or `rejected`.
- A reliability scorecard: useful lead rate, verified-lead rate, hallucinated-source rate, stale-claim rate, promotion rate, cost per promoted finding, and time saved.

## Weekend Experiment Program

### Tier 0: Instrument Before Spending

Goal: make high-volume experimentation measurable.

Tasks:

1. Add a lightweight SDK run ledger under `docs/workstreams/cursor_sdk/run_ledger_20260524.md` or JSONL under `artifacts/cursor_sdk/`.
2. Add output naming that distinguishes prompt rehearsal from live draft, e.g. `_prompt_rehearsal.md`.
3. Add a draft index for existing outputs with status: stub, substantive, duplicate, canonical-for-review, superseded.
4. Record model, runtime, command, output path, start/end time, and whether the draft cited missing context.

Success criterion: no new run is hard to attribute or review.

### Tier 1: High-Volume Review-Only Agents

Goal: spend aggressively while keeping the shared repo safe.

Run multiple independent passes:

- Experiment registry validator: find rows whose run IDs, metrics, decision docs, or artifact paths are missing or stale.
- Paper claim verifier: map every paper-level claim to primary artifacts and mark `paper_ready`, `needs_metrics`, `needs_caveat`, or `unsupported`.
- Dataset/scorer caveat audit: check all synthesis docs for claims that omit Gan primary gold semantics, ExECT label policy, scorer mode, or evidence policy.
- Run inspection swarm: one agent per important run directory, each drafting a short inspection with exact metric path references.
- Config coverage scanner: compare every experiment config against model/provider adapter tests and smoke-test policy.
- Memory contradiction scanner: compare `session_brief`, `workflow_index`, Kanban, frozen history, and registry.

These are safe because they produce source-linked reports only. They should be run in parallel or batched.

### Tier 2: Disposable-Worktree Mutation Sprints

Goal: test whether SDK agents can generate useful code changes without risking the shared workspace.

Rules:

- Create a disposable clone/worktree per run.
- Refuse dirty worktree at start.
- Commit or stash the baseline before agent execution.
- Agent may edit only the disposable worktree.
- Agent must run focused tests.
- The parent process captures diff, test output, and final status.
- Never use `git checkout --` as the only rollback mechanism against a shared workspace.

Candidate mutation experiments:

- Provider adapter validation fixes from compatibility drafts.
- Additional Gan temporal candidate builder helpers from the adapter mutation drafts.
- Unit-test generation for known gap families.
- Registry validation repair proposals in a disposable copy.
- Prompt/config variants that produce new JSON configs but do not launch expensive model inference.

Success criterion: at least 20-30% of mutation sprints produce a patch worth human review, with zero shared-workspace modifications.

### Tier 3: DAG-Orchestrated Research Jobs

Goal: move beyond isolated drafts into structured research workflows.

Example DAG: "Paper claim readiness audit."

Ranks:

1. Inspect registry, current Kanban, and recent synthesis docs independently.
2. Inspect Gan run artifacts, ExECT run artifacts, and model-provider configs independently.
3. Merge into claim matrix with support/caveat status.
4. Draft final paper-results update with only verified claims.

This is the official DAG-task-runner pattern translated into this repo's research process. It is especially promising because sibling agents can read different artifact families without fighting over files.

### Tier 4: Cloud / PR Experiments

Goal: test full SDK capability beyond local agents.

Candidate experiments:

- Cloud agent opens a draft PR that only updates documentation generated from a supplied canonical source note.
- Cloud agent runs a provider-adapter test patch in a branch and opens a PR with test logs.
- Cloud agent performs a repo hygiene pass and opens a PR with low-risk link/wording updates only.

Guardrails:

- Use a non-sensitive repo state only.
- No raw clinical/sensitive data.
- No source-of-truth scorer/dataset changes unless the task is explicitly a disposable PR for review.
- Require CI/test evidence before merge.

This should be done after Tier 0/Tier 2 instrumentation, not first.

## New Areas Worth Broadening Into

### 1. Research CI

Use SDK agents as scheduled or triggered reviewers after major runs:

- "A run directory appeared; draft inspection."
- "Registry changed; verify artifact paths."
- "Paper synthesis changed; check every metric against primary runs."
- "Kanban operational default changed; find stale peer docs."

This turns the SDK into a research integrity monitor.

### 2. Experiment Design Critic

Before expensive model runs, ask independent agents to critique preregistrations:

- Is the hypothesis explicit?
- Is the split clear?
- Are scorer mode and normalization rules named?
- Is this arm/mechanism/test scope?
- Are comparison controls valid?
- Is there a cheaper cap or fixture test first?

This could reduce wasted model spend.

### 3. Error Taxonomy Expansion

Fan out one agent per failure family:

- temporal-window errors
- unknown vs no-reference confusions
- evidence support failures
- current vs historical frequency
- seizure-free duration normalization
- provider/config errors

Each agent produces a proposed fixture pack, not source edits.

### 4. Agentic Paper Assistant With Hard Verification

Use a two-agent loop:

- Writer agent drafts a paragraph or claim table.
- Verifier agent tries to falsify each claim against registry and metrics.

Promotion requires verifier acceptance plus human review.

### 5. Multi-Model / Multi-Prompt Ideation

Because current pricing makes broad experimentation attractive, run multiple agents with different prompt roles:

- skeptical reviewer
- implementation planner
- clinical label-policy reviewer
- reproducibility auditor
- paper reviewer
- Windows portability reviewer

The output is not "truth"; it is a ranked set of leads.

### 6. Local Dashboard / Canvas

Adopt the official Kanban/DAG-dashboard idea:

- active SDK runs
- output paths
- status
- review queue
- canonical-vs-duplicate drafts
- promoted/rejected counts
- cost/time estimates

This matters because the current failure mode is not lack of output; it is output bookkeeping.

## Recommended Architecture Changes

1. Keep the current Python runner for immediate continuity, but add a TypeScript SDK harness for first-party features. The external SDK guidance says the first-party SDK is TypeScript; the local Python package is a wrapper and required a Windows bridge patch.
2. Introduce a `cursor_sdk_runs.jsonl` ledger with run metadata and human review status.
3. Add `--live-output-kind prompt|draft|report|diff-report` and encode it in filenames.
4. Add `--max-sources` / `--source-manifest` arguments so broad agents read a deliberate source set.
5. Add `--disposable-worktree` support that creates, verifies, and deletes or preserves isolated worktrees.
6. Add a DAG runner for independent research tasks; do not let same-rank tasks write the same files.
7. Add a "verify draft" workflow where a second agent checks cited paths and claim support.
8. Add model catalog checks before using non-default models.
9. Move SDK dependencies toward optional/dev tooling after the capability expansion, unless they become part of project automation.

## Safety Rules That Should Not Move

- No SDK agent edits to canonical scorer, loader, registry, dataset-policy, or clinical schema files in the shared workspace.
- No generated prose becomes paper evidence without primary artifact support.
- No real clinical or sensitive data goes through Cursor cloud or SDK workflows without separate governance review.
- No mutation workflow runs without a clean disposable workspace.
- No rollback command should target user work unless the pre-run baseline was committed/stashed and the workspace is disposable.
- No broad model-spend run should proceed without a clear output artifact and review rubric.

## Proposed Immediate Weekend Queue

Run in this order:

1. Create SDK draft index for all existing outputs.
2. Run three review-only swarms:
   - paper claim verifier
   - registry/artifact verifier
   - memory/Kanban/source-doc drift verifier
3. Run a 5-agent disposable mutation pilot:
   - two provider config/test patches
   - two Gan candidate-helper fixture proposals
   - one docs-only workflow-index cleanup patch
4. Run one DAG experiment for paper claim readiness.
5. If the above is clean, run one cloud/PR experiment on a docs-only change.

Stop conditions:

- Any shared-workspace source change by an SDK agent.
- Any draft with more than two invented/nonexistent source paths.
- Any mutation run that cannot prove pre/post git status.
- Any run whose cost or token use cannot be attributed.

## Metrics For Judging The Capability Expansion

Track per workflow:

- number of agents run
- cost / token use if available
- wall-clock time
- source paths claimed
- nonexistent source path count
- human-verified useful findings
- promoted findings
- stale or false claims
- duplicate outputs
- patches worth review
- tests passed in disposable worktree
- incidents / guardrail violations

Decision thresholds:

- Promote a workflow if at least 50% of substantive outputs contain one verified useful finding and false-source rate stays below 5%.
- Keep mutation workflows gated unless at least 3 consecutive disposable-worktree runs preserve git state and produce complete diffs/test logs.
- Stop or redesign any workflow whose outputs mostly duplicate prior drafts or create more review burden than they remove.

## Bottom Line

The Cursor SDK workstream should expand, but along an orchestration axis, not an authority axis. The project has already proven that SDK agents can find drift and draft useful research artifacts. The larger opportunity is to run many bounded agents as a research operations swarm: inspect, verify, critique, propose, and only mutate inside disposable isolation. That is ambitious enough to exploit the discounted window, while still respecting the clinical extraction project's core constraint: benchmark truth comes from primary artifacts, audited labels, stable scorers, and reviewed source changes.

