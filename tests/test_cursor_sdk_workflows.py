import json
import importlib.util
import subprocess
from types import SimpleNamespace
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "cursor_sdk_workflows.py"
SPEC = importlib.util.spec_from_file_location("cursor_sdk_workflows", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
workflows = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflows)


def test_prompt_rehearsal_default_path_is_explicit():
    output = workflows._default_output_path(
        "inspection-draft",
        "20260524T120000Z",
        prompt_only=True,
    )

    assert output.name == "20260524T120000Z_inspection_draft_prompt_rehearsal.md"
    assert "cursor_sdk_drafts" in output.as_posix()


def test_live_default_path_keeps_existing_draft_suffix():
    output = workflows._default_output_path(
        "model-compatibility",
        "20260524T120001Z",
        prompt_only=False,
    )

    assert output.name == "20260524T120001Z_model_compatibility_report.md"
    assert "compatibility" in output.as_posix()


def test_append_ledger_entry_writes_jsonl(tmp_path, monkeypatch):
    ledger = tmp_path / "cursor_sdk_runs.jsonl"
    monkeypatch.setattr(workflows, "LEDGER_PATH", ledger)

    workflows._append_ledger_entry(
        {
            "run_id": "20260524T120002Z",
            "workflow": "hygiene-scan",
            "status": "success",
        }
    )

    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
    assert rows == [
        {
            "run_id": "20260524T120002Z",
            "workflow": "hygiene-scan",
            "status": "success",
        }
    ]


def test_mutating_workflow_requires_disposable_marker(tmp_path, monkeypatch):
    monkeypatch.setenv("CURSOR_SDK_ALLOW_MUTATING_WORKFLOW", "disposable-worktree")

    with pytest.raises(SystemExit, match="marker"):
        workflows._ensure_mutating_workflow_allowed(tmp_path)


def test_mutating_workflow_accepts_clean_marked_workspace(tmp_path, monkeypatch):
    monkeypatch.setenv("CURSOR_SDK_ALLOW_MUTATING_WORKFLOW", "disposable-worktree")
    (tmp_path / ".cursor-sdk-disposable-worktree").write_text(
        "review-only disposable workspace\n",
        encoding="utf-8",
    )

    calls = []

    def fake_run(command, cwd, check, capture_output, text):
        calls.append((command, cwd, check, capture_output, text))
        return SimpleNamespace(stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    workflows._ensure_mutating_workflow_allowed(tmp_path)

    assert calls == [
        (["git", "status", "--short"], tmp_path, True, True, True),
    ]


def test_mutation_prompt_uses_disposable_restore_not_shared_checkout():
    prompt = workflows.test_mutations_prompt()

    assert "git checkout --" not in prompt
    assert "disposable workspace" in prompt
