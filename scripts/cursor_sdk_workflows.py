"""Run review-only Cursor SDK workflows for research operations.

The workflows in this script deliberately draft Markdown for review. They do
not edit source-of-truth docs, experiment registry rows, scorers, or run
artifacts, except for explicitly gated implementation workflows that must run
inside a disposable worktree.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from cursor_sdk import Agent, LocalAgentOptions
from cursor_sdk.errors import CursorSDKError


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "composer-2.5"
LEDGER_PATH = REPO_ROOT / "docs" / "workstreams" / "cursor_sdk" / "cursor_sdk_runs.jsonl"
DISPOSABLE_WORKTREE_MARKER = ".cursor-sdk-disposable-worktree"

LIVE_OUTPUT_SUFFIXES = {
    "memory-pass": "cursor_sdk_memory_pass_candidate",
    "inspection-draft": "inspection_draft",
    "hygiene-scan": "hygiene_scan",
    "paper-synthesis": "paper_synthesis_draft",
    "adapter-mutation": "adapter_mutation_draft",
    "model-compatibility": "model_compatibility_report",
    "test-mutations": "mutation_test_report",
    "pathway-a-card": "pathway_a_card_report",
}

PROMPT_REHEARSAL_SUFFIXES = {
    "memory-pass": "cursor_sdk_memory_pass_prompt_rehearsal",
    "inspection-draft": "inspection_draft_prompt_rehearsal",
    "hygiene-scan": "hygiene_scan_prompt_rehearsal",
    "paper-synthesis": "paper_synthesis_prompt_rehearsal",
    "adapter-mutation": "adapter_mutation_prompt_rehearsal",
    "model-compatibility": "model_compatibility_prompt_rehearsal",
    "test-mutations": "mutation_test_prompt_rehearsal",
    "pathway-a-card": "pathway_a_card_prompt_rehearsal",
}

OUTPUT_FOLDERS = {
    "memory-pass": REPO_ROOT / "docs" / "memory" / "dreams",
    "inspection-draft": REPO_ROOT / "docs" / "experiments" / "cursor_sdk_drafts",
    "hygiene-scan": REPO_ROOT / "docs" / "workstreams" / "cursor_sdk" / "hygiene_scans",
    "paper-synthesis": REPO_ROOT / "docs" / "experiments" / "cursor_sdk_drafts",
    "adapter-mutation": REPO_ROOT / "docs" / "experiments" / "cursor_sdk_drafts",
    "model-compatibility": REPO_ROOT / "docs" / "workstreams" / "cursor_sdk" / "compatibility",
    "test-mutations": REPO_ROOT / "docs" / "experiments" / "cursor_sdk_drafts",
    "pathway-a-card": REPO_ROOT / "docs" / "workstreams" / "cursor_sdk" / "pathway_a",
}

PATHWAY_A_CARD_BRIEFS = {
    "A1R": {
        "title": "Retrospective A1 Cursor review",
        "role": "review-only retrospective critic/source-map lane",
        "sources": [
            "docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md",
            "runs/exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z/errors.json",
            "runs/exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z/predictions.json",
            "src/clinical_extraction/datasets/exect.py",
            "docs/datasets/exect/exect_gold_label_audit.md",
            "docs/policies/deterministic_scorer_semantics.md",
        ],
        "allowed": "Review draft only; no source edits.",
        "forbidden": "No edits to raw data, gold labels, split definitions, scorers, configs, registry rows, Kanban, or paper claims.",
        "validation": "Check residual categories and per-document claims against primary artifacts and load_exect_gold_documents() where useful.",
        "stop": "Stop at discrepancies or missing evidence; do not rewrite the promoted A1 note.",
    },
    "A2D": {
        "title": "A2 verifier design brief",
        "role": "design brief lane",
        "sources": [
            "docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md",
            "docs/planning/kanban_plan.md",
            "docs/taxonomy/taxonomy_primitive_catalog.md",
            "docs/workstreams/cursor_sdk/cursor_sdk_pathway_a_implementation_campaign_20260524.md",
            "configs/experiments/",
            "src/clinical_extraction/programs/",
            "src/clinical_extraction/experiments/",
        ],
        "allowed": "Design/report draft only unless run in a disposable implementation lane later.",
        "forbidden": "No scorer, gold, split, raw data, registry, or operational-default changes.",
        "validation": "Mission brief must name cap-25 gate, fixed scorer mode, baseline comparison, guarded-family regression threshold, allowed files, tests, and stop rules.",
        "stop": "Do not propose high-precision pruning as the arm; that candidate narrowing arm is already rejected.",
    },
    "A2I": {
        "title": "A2 verifier implementation pilot",
        "role": "disposable-worktree implementation lane",
        "sources": [
            "docs/workstreams/cursor_sdk/pathway_a/a2_verifier_mission_brief_20260524.md",
            "docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md",
            "docs/datasets/exect/exect_gold_label_audit.md",
            "docs/policies/deterministic_scorer_semantics.md",
            "docs/taxonomy/taxonomy_primitive_catalog.md",
            "configs/experiments/exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini.json",
            "src/clinical_extraction/programs/exect_s4.py",
            "src/clinical_extraction/programs/exect_s0_s1.py",
            "src/clinical_extraction/exect/primitives.py",
            "src/clinical_extraction/experiments/exect_backend.py",
            "src/clinical_extraction/experiments/config.py",
            "tests/",
        ],
        "allowed": (
            "Implementation edits only in the mission-brief allow-list: "
            "src/clinical_extraction/programs/exect_s4.py; "
            "src/clinical_extraction/exect/primitives.py only for small evidence/candidate-block guard helpers; "
            "src/clinical_extraction/experiments/exect_backend.py; "
            "src/clinical_extraction/experiments/config.py; "
            "src/clinical_extraction/experiments/exect_prompts.py only if prompt routing requires it; "
            "configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini.json; "
            "tests/test_exect_s5_frequency_verifier.py; existing focused config/scorer tests if registration needs them; "
            "and a disposable inspection draft under docs/experiments/exect/."
        ),
        "forbidden": (
            "No raw data, gold labels, split definitions, scorer denominator, scorer normalization, "
            "benchmark bridge semantics, high-recall candidate builder output/density, medication guard semantics, "
            "registry rows, Kanban status, paper claims, operational defaults, or full-validation execution."
        ),
        "validation": (
            "Run focused tests first: uv run --extra dev pytest tests/test_exect_s5_frequency_verifier.py "
            "tests/test_exect_s5_scoring.py tests/test_experiment_configs.py -q; then "
            "uv run python scripts/validate_experiment_taxonomy.py --errors-only. "
            "Run the cap-25 experiment only after tests pass."
        ),
        "stop": (
            "Stop if the verifier changes scorer/gold semantics, narrows candidates, adds labels or repairs FNs, "
            "drops labels without note-evidence rationale, materially reduces frequency recall, regresses guard families, "
            "or becomes a hidden normalization/scorer rewrite."
        ),
    },
    "A3D": {
        "title": "A3 prompt-policy design brief",
        "role": "design brief lane",
        "sources": [
            "docs/experiments/exect/exect_s5_frequency_residual_audit_20260524.md",
            "docs/planning/kanban_plan.md",
            "docs/workstreams/cursor_sdk/cursor_sdk_pathway_a_implementation_campaign_20260524.md",
            "configs/experiments/",
            "src/clinical_extraction/programs/",
        ],
        "allowed": "Design/report draft only unless run in a disposable implementation lane later.",
        "forbidden": "No scorer, gold, split, raw data, registry, or operational-default changes.",
        "validation": "Mission brief must isolate one prompt-policy factor and preserve candidate density, scorer mode, model/provider, split, and S5 guarded families.",
        "stop": "Do not encode clinical corrections as benchmark gold policy or compare cap-25 metrics as full-validation evidence.",
    },
}

PATHWAY_A_MUTATING_LANES = {"implementation"}


def _install_windows_cursor_bridge_patch() -> None:
    """Patch Cursor SDK bridge discovery for Windows pipe handles.

    cursor-sdk 0.1.5 uses ``selectors`` against the bridge process stderr.
    On Windows, anonymous pipe handles are not selectable sockets, so bridge
    startup fails before the agent can run. Keep the workaround local to this
    script and only install it on Windows.
    """
    if sys.platform != "win32":
        return

    from cursor_sdk import _bridge

    def read_discovery(process, timeout: float):
        if process.stderr is None:
            raise CursorSDKError("Bridge process stderr is unavailable")

        lines: "queue.Queue[str | None]" = queue.Queue()

        def reader() -> None:
            try:
                for line in process.stderr:
                    lines.put(line)
            finally:
                lines.put(None)

        threading.Thread(target=reader, daemon=True).start()
        deadline = datetime.now(timezone.utc).timestamp() + timeout
        stderr_lines: list[str] = []

        while datetime.now(timezone.utc).timestamp() < deadline:
            remaining = max(0.0, deadline - datetime.now(timezone.utc).timestamp())
            try:
                line = lines.get(timeout=min(0.1, remaining))
            except queue.Empty:
                if process.poll() is not None:
                    break
                continue
            if line is None:
                break
            stderr_lines.append(line)
            discovery = _bridge.parse_discovery_line(line)
            if discovery is not None:
                return discovery

        exit_code = process.poll()
        if exit_code is not None:
            raise CursorSDKError(
                f"Bridge exited before discovery with status {exit_code}: "
                + "".join(stderr_lines)
            )
        raise CursorSDKError("Timed out waiting for bridge discovery")

    _bridge._read_discovery = read_discovery


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _default_output_path(workflow: str, run_id: str, prompt_only: bool) -> Path:
    folder = OUTPUT_FOLDERS[workflow]
    suffixes = PROMPT_REHEARSAL_SUFFIXES if prompt_only else LIVE_OUTPUT_SUFFIXES
    return folder / f"{run_id}_{suffixes[workflow]}.md"


def _append_ledger_entry(entry: dict[str, object]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def _write_prompt(prompt: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(prompt, encoding="utf-8")


def _run_cursor(prompt: str, output: Path, model: str) -> None:
    _install_windows_cursor_bridge_patch()
    output.parent.mkdir(parents=True, exist_ok=True)
    with Agent.create(
        model=model,
        api_key=os.environ.get("CURSOR_API_KEY"),
        local=LocalAgentOptions(cwd=REPO_ROOT),
    ) as agent:
        run = agent.send(prompt)
        output.write_text(run.text(), encoding="utf-8")


def _ensure_mutating_workflow_allowed(workspace_root: Path = REPO_ROOT) -> None:
    """Block live mutation workflows unless the operator asserts a disposable worktree."""

    if os.environ.get("CURSOR_SDK_ALLOW_MUTATING_WORKFLOW") != "disposable-worktree":
        raise SystemExit(
            "Live Cursor SDK mutation workflows are blocked in the shared workspace. "
            "Use --prompt-only for review drafts, or run from a disposable clone/worktree "
            "with CURSOR_SDK_ALLOW_MUTATING_WORKFLOW=disposable-worktree."
        )
    workspace_root = workspace_root.resolve()
    marker = workspace_root / DISPOSABLE_WORKTREE_MARKER
    if not marker.exists():
        raise SystemExit(
            "Refusing live Cursor SDK mutation workflow because the disposable "
            f"workspace marker is missing: {marker}. Create this marker only "
            "inside a throwaway clone or git worktree."
        )
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=workspace_root,
        check=True,
        capture_output=True,
        text=True,
    )
    if status.stdout.strip():
        raise SystemExit(
            "Refusing live Cursor SDK mutation workflow because the disposable "
            "workspace is not clean:\n" + status.stdout
        )


def _source_header(workflow: str) -> str:
    return f"""You are drafting a review-only artifact for the dspy-extraction research repo.

Workflow: {workflow}
Repository root: {REPO_ROOT}

Hard rules:
- Do not edit files.
- Do not change scorer semantics, dataset policy, registry rows, Kanban, or source-of-truth docs.
- Do not treat this draft as evidence for paper claims unless it points to primary artifacts.
- Preserve decision scopes: operational, arm, mechanism, open, blocked, stale_check.
- Separate facts from interpretation and uncertainty.
- Include concrete source paths for every claim.
- Flag missing context instead of guessing.
"""


def _pathway_a_header(card: str, lane: str) -> str:
    if lane in PATHWAY_A_MUTATING_LANES:
        edit_rule = """- You may edit only the allowed write surfaces named in the card brief.
- You must first verify the workspace marker `.cursor-sdk-disposable-worktree`, `CURSOR_SDK_ALLOW_MUTATING_WORKFLOW=disposable-worktree`, and clean `git status --short`.
- Capture changed files, focused test output, and `git diff` in the final report.
- Restore the disposable worktree before ending, then report the final clean status."""
    else:
        edit_rule = "- Do not edit files."
    return f"""You are running a Cursor SDK Pathway A card lane for the dspy-extraction research repo.

Workflow: Pathway A ExECT S5 card
Card: {card}
Lane: {lane}
Repository root: {REPO_ROOT}

Hard rules:
{edit_rule}
- Cursor output is not source-of-truth evidence. It is a review artifact for Codex/human inspection.
- Preserve ExECT audit guidance, fixed split definitions, and scorer semantics.
- Do not change raw data, gold labels, split definitions, scorer denominators, normalization rules, paper claims, or operational defaults unless the card explicitly authorizes that exact change.
- Every metric claim must include run ID, config, split, model/provider, scorer mode, denominator, and caveat.
- Flag missing context instead of guessing.
"""


def pathway_a_card_prompt(
    card: str | None,
    lane: str | None,
    mission_brief_path: Path | None,
) -> str:
    card_id = card or "A1R"
    lane_name = lane or "review"
    brief = PATHWAY_A_CARD_BRIEFS.get(card_id)
    if brief is None:
        known = ", ".join(sorted(PATHWAY_A_CARD_BRIEFS))
        raise SystemExit(f"Unknown Pathway A card '{card_id}'. Known cards: {known}.")

    mission_brief_text = ""
    if mission_brief_path is not None:
        path = mission_brief_path
        if not path.is_absolute():
            path = REPO_ROOT / path
        if not path.exists():
            raise SystemExit(f"Mission brief path does not exist: {path}")
        mission_brief_text = path.read_text(encoding="utf-8")

    sources = "\n".join(f"- {source}" for source in brief["sources"])
    extra = (
        "\nOperator-supplied mission brief:\n\n"
        + mission_brief_text
        if mission_brief_text
        else ""
    )
    return (
        _pathway_a_header(card_id, lane_name)
        + f"""
Card title: {brief["title"]}
Cursor role: {brief["role"]}

Dataset and split:
- Dataset: ExECTv2
- Split: exectv2_fixed_v1:validation for validation work; use cap-25 before full validation.
- Surface: S5 core families only: diagnosis, seizure_type, annotated_medication, investigation, seizure_frequency.
- Current baseline: exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini; full validation seizure_frequency F1 60.2%, annotated-medication F1 88.7%, micro F1 81.4%.
- Scorer mode: exect_s5_core_field_family_deterministic_v1.

Primary sources:
{sources}

Allowed write surfaces:
{brief["allowed"]}

Forbidden changes:
{brief["forbidden"]}

Validation gate:
{brief["validation"]}

Stop rules:
{brief["stop"]}
{extra}

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
"""
    )


def memory_pass_prompt() -> str:
    return (
        _source_header("Automated research-memory pass")
        + """
Task:
Read the active research-memory and planning sources, then draft a memory
consolidation candidate.

Primary sources:
- docs/memory/README.md
- docs/memory/session_brief.md
- docs/memory/workflow_index.md
- docs/memory/dreams/TEMPLATE.md
- docs/planning/kanban_plan.md
- docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md
- docs/experiments/synthesis/experiment_registry.json

Output shape:
# Cursor SDK Memory Pass Candidate

## Sources Read
List paths.

## Proposed Memory Updates
Use target file, status, confidence, source paths, and proposed wording.

## Stale Or Conflicting Claims
Flag exact phrases or sections and explain the risk.

## Decisions Reaffirmed
Scope each decision as operational, arm, mechanism, open, blocked, or stale_check.

## Open Questions
Only questions that affect future work.

## Promotion Checklist
Use the checklist from docs/memory/README.md.
"""
    )


def inspection_draft_prompt(run_dir: str | None, topic: str | None) -> str:
    run_context = run_dir or "No run directory supplied. Draft a template and list required inputs."
    topic_context = topic or "Experiment inspection draft"
    return (
        _source_header("Experiment-inspection draft worker")
        + f"""
Task:
Draft an experiment inspection note for review.

Topic: {topic_context}
Run directory or artifact pointer: {run_context}

Use these sources when present:
- docs/templates/experiment_decision_template.md
- docs/planning/kanban_plan.md
- docs/policies/deterministic_scorer_semantics.md
- docs/datasets/exect/exect_gold_label_audit.md, if ExECT is in scope
- docs/datasets/gan/gan_2026_label_audit.md, if Gan is in scope
- configs/experiments/, configs/models/, and the supplied run directory

Output shape:
# Experiment Inspection Draft

## Scope
Dataset, split, model/provider, schema level or field group, DSPy program
variant, scorer mode, normalization rules, and evidence policy. Use "unknown"
where not discoverable.

## Sources Read
List concrete paths.

## Run Summary
Metrics, run IDs, artifact paths, and comparison controls.

## Interpretation
What the result suggests, scoped to the comparison group.

## Caveats
Scorer, dataset, cap/full/test, validation, or billing caveats.

## Decision Recommendation
Use hold, promote, reject-as-tested, rerun, or needs-review, with rationale.

## Required Human Checks
List checks before promoting this draft into docs/experiments/.
"""
    )


def hygiene_scan_prompt() -> str:
    return (
        _source_header("Background repo hygiene")
        + """
Task:
Run a background documentation and workflow hygiene scan. Focus on contradictions,
stale wording, missing links, duplicate source-of-truth claims, and unclear
workflow ownership. Do not make edits.

Primary sources:
- docs/planning/kanban_plan.md
- docs/memory/README.md
- docs/memory/session_brief.md
- docs/memory/workflow_index.md
- docs/workstreams/
- docs/policies/
- .agents/skills/
- pyproject.toml

Output shape:
# Cursor SDK Hygiene Scan

## Sources Read
List paths.

## Findings
Prioritize by risk. Include source path, issue, impact, and suggested owner.

## Low-Risk Cleanups
Small documentation or workflow fixes safe to batch later.

## Do Not Change Without Explicit Review
Anything involving scorer semantics, dataset policy, registry rows, or active
operational defaults.

## Suggested Follow-Up Cards
Cards suitable for docs/planning/kanban_plan.md if the findings are accepted.
"""
    )


def paper_synthesis_prompt() -> str:
    return (
        _source_header("Automated paper narrative synthesis")
        + """
Task:
Read the research outline, the experiment registry, and prior narrative reports.
Draft a results section/outline for the paper. Map paper claims directly to primary
run IDs and metrics from the registry. Do not make edits.

Primary sources:
- docs/outline.md
- docs/experiments/synthesis/experiment_registry.json
- docs/experiments/synthesis/experiments_narrative_report_20260520.md
- docs/experiments/synthesis/experiment_registry_matrix_20260520.md

Output shape:
# Paper Narrative Synthesis Draft

## Sources Read
List paths.

## Key Paper Claims Map
For each claim (e.g. model suite comparison, deterministic placement value, schema breadth effect):
1. Claim Statement: Summary of the claim.
2. Supporting Run ID: The exact run ID from the registry.
3. Supporting Metrics: Stated F1, Purist/Pragmatic accuracy, or micro accuracy.
4. Rationale: How the metric validates or caveats the claim.

## Discrepancies Or Unsupported Claims
Flag any claims in outline.md that lack backing in registry.json or narrative reports.

## Open Writing Tasks
What remains to be written or verified by a human before publication.
"""
    )


def adapter_mutation_prompt() -> str:
    return (
        _source_header("Adapter/Prompt mutation draft")
        + """
Task:
Read the Gan Qwen/GPT error taxonomy and candidate builder code.
Draft a proposed deterministic helper function template or mutated prompt candidates
to resolve identified failure modes. Do not make edits to the source code.

Primary sources:
- docs/experiments/gan/gan_s0_qwen35b_20260522_error_taxonomy.md
- docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md
- src/clinical_extraction/gan/temporal_candidates.py

Output shape:
# Adapter and Prompt Mutation Draft

## Sources Read
List paths.

## Identified Bottlenecks
Targeted failure modes (e.g., long-window quantified counts, cluster spacing separate count, seizure-free duration).

## Draft Python Code Templates
Proposed additions to temporal_candidates.py (e.g., regex pattern matches, candidate builders) to surface the missing candidate labels.

## Draft Prompt Mutations
Proposed additions/tweaks to prompt policies (like gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice.json) to handle candidate overrides or stability statements.

## Verification checklist
List unit tests and validation steps to verify the mutated logic without introducing regressions.
"""
    )


def model_compatibility_prompt() -> str:
    return (
        _source_header("Model config compatibility check")
        + """
Task:
Scan the model configurations and source wrapper code to identify potential compatibility issues.
Draft compatibility adapters, wrappers, or parameters validation lists. Do not make edits.

Primary sources:
- configs/models/
- src/clinical_extraction/llms.py
- docs/policies/model_config_smoke_tests.md
- .agents/skills/model-config-compatibility/SKILL.md

Output shape:
# Model Compatibility and Adapter Report

## Sources Read
List paths.

## Model Config Gaps & Gaps Matrix
Analyze the differences in settings across:
- local Qwen configs (e.g., context length, Ollama specifics)
- hosted Gemini / OpenAI / Anthropic configs (e.g. reasoning parameters, json mode)
Flag unsupported parameters or risk of timeouts.

## Draft Adapter Wrapper/Interface Proposals
Provide Python code snippets or configuration recommendations to map provider-specific parameters safely in clinical_extraction wrappers.

## Recommended Parameter Validations
Rules to check during startup to prevent API crashes.
"""
    )


def test_mutations_prompt() -> str:
    return f"""You are drafting a review-only artifact for the dspy-extraction research repo.

Workflow: Cursor SDK Mutation Testing
Repository root: {REPO_ROOT}

CRITICAL RULES FOR COMMAND EXECUTION:
1. You are running as an agent in the repository workspace. You have the ability to read, edit files, and execute terminal commands.
2. This workflow may run only in a disposable workspace with a `.cursor-sdk-disposable-worktree` marker. Before making any modifications, you MUST verify that you are on a clean git working directory. Run `git status` to verify.
3. Read the latest adapter mutation draft file in `docs/experiments/cursor_sdk_drafts/*_adapter_mutation_draft.md`.
4. Implement the drafted helper functions (like `_seizure_free_for_multiple_year`, `_seizure_free_for_multiple_month`, etc.) and register them in `src/clinical_extraction/gan/temporal_candidates.py`.
5. Run `uv run pytest tests/test_gan_temporal_candidates.py` to check for regressions.
6. Diagnose any failures, modify the code, and rerun the tests until all 49+ tests pass.
7. Verify if the coverage on the pragmatics slice (`test_enriched_gap_slice_gold_label_coverage_improves` or `test_residual_slice_gold_label_coverage_improves`) changes or passes.
8. Run `git diff` to capture all your modifications.
9. CRITICAL RESTORATION: Because this is a disposable workspace, you MUST undo all modifications before ending your turn. After capturing the diff, run `git restore --staged --worktree .` and verify with `git status` that the disposable workspace is completely clean. Do not leave the workspace dirty.
10. Write the final report detailing your steps, outcomes, and the captured git diff.

Output shape:
# Cursor SDK Mutation Test Report

## Executive Summary
Stated outcomes: whether existing tests passed, whether any new test cases passed, and whether the workspace was successfully rolled back to a clean state.

## Implementation Steps
Details of the changes you attempted.

## Test Outcomes & Debugging
The output of the pytest execution. Details of any test failures and how you debugged/corrected them.

## Captured Git Diff
The full `git diff` block of the implemented code mutations before they were rolled back.

## Restoration Verification
The output of `git status` confirming the workspace is clean.
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "workflow",
        choices=[
            "check",
            "memory-pass",
            "inspection-draft",
            "hygiene-scan",
            "paper-synthesis",
            "adapter-mutation",
            "model-compatibility",
            "test-mutations",
            "pathway-a-card",
        ],
    )
    parser.add_argument("--env-file", type=Path, default=REPO_ROOT / ".env")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--prompt-only", action="store_true")
    parser.add_argument("--run-dir")
    parser.add_argument("--topic")
    parser.add_argument(
        "--card",
        help="Pathway A card ID for pathway-a-card, such as A1R, A2D, A2I, or A3D.",
    )
    parser.add_argument(
        "--lane",
        choices=["review", "design", "implementation", "regression", "critic", "runner"],
        help="Pathway A lane type for pathway-a-card.",
    )
    parser.add_argument(
        "--mission-brief",
        type=Path,
        help="Optional Pathway A mission brief file to append to the generated prompt.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    _load_env_file(args.env_file)

    if args.workflow == "check":
        if not os.environ.get("CURSOR_API_KEY"):
            raise SystemExit("CURSOR_API_KEY is not set in the environment or .env file.")
        print("cursor-sdk import ok; CURSOR_API_KEY is present.")
        return 0

    if args.workflow == "memory-pass":
        prompt = memory_pass_prompt()
    elif args.workflow == "inspection-draft":
        prompt = inspection_draft_prompt(args.run_dir, args.topic)
    elif args.workflow == "hygiene-scan":
        prompt = hygiene_scan_prompt()
    elif args.workflow == "paper-synthesis":
        prompt = paper_synthesis_prompt()
    elif args.workflow == "adapter-mutation":
        prompt = adapter_mutation_prompt()
    elif args.workflow == "model-compatibility":
        prompt = model_compatibility_prompt()
    elif args.workflow == "test-mutations":
        prompt = test_mutations_prompt()
    elif args.workflow == "pathway-a-card":
        prompt = pathway_a_card_prompt(args.card, args.lane, args.mission_brief)
    else:
        raise ValueError(f"Unknown workflow: {args.workflow}")

    run_id = _utc_stamp()
    default_output = _default_output_path(args.workflow, run_id, args.prompt_only)
    output = args.output or default_output
    if not output.is_absolute():
        output = REPO_ROOT / output

    started_at = datetime.now(timezone.utc)
    status = "success"
    error: str | None = None
    try:
        if args.prompt_only:
            _write_prompt(prompt, output)
            print(f"Wrote prompt to {output}")
            return 0

        if args.workflow == "test-mutations" or (
            args.workflow == "pathway-a-card" and args.lane in PATHWAY_A_MUTATING_LANES
        ):
            _ensure_mutating_workflow_allowed()

        if not os.environ.get("CURSOR_API_KEY"):
            raise SystemExit("CURSOR_API_KEY is not set in the environment or .env file.")

        _run_cursor(prompt, output, args.model)
        print(f"Wrote Cursor SDK draft to {output}")
        return 0
    except BaseException as exc:
        status = "failed"
        error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        ended_at = datetime.now(timezone.utc)
        entry = {
            "run_id": run_id,
            "workflow": args.workflow,
            "model": args.model,
            "prompt_only": args.prompt_only,
            "output_kind": "prompt_rehearsal" if args.prompt_only else "live_draft",
            "output_path": _relative_path(output),
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "duration_seconds": round((ended_at - started_at).total_seconds(), 3),
            "status": status,
            "topic": args.topic,
            "run_dir": args.run_dir,
            "command": " ".join(sys.argv),
            "human_review_status": "needs_review",
            "source_claim_status": "unchecked",
        }
        if args.workflow == "pathway-a-card":
            entry["pathway"] = "A"
            entry["card"] = args.card
            entry["lane"] = args.lane
            entry["mission_brief"] = _relative_path(args.mission_brief) if args.mission_brief else None
            entry["promotion_decision"] = "pending_review"
        if error:
            entry["error"] = error
        _append_ledger_entry(entry)


if __name__ == "__main__":
    raise SystemExit(main())
