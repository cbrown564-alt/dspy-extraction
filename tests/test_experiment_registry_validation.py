from __future__ import annotations

from pathlib import Path

from clinical_extraction.experiments.registry_validation import (
    ValidationIssue,
    validate_comparison_groups,
    validate_experiment_taxonomy,
    validate_registry_row_canonical_run,
    validate_registry_row_controlled_values,
    validate_registry_row_decision_doc,
    validation_failed,
)


def test_repository_experiment_taxonomy_validation_passes_errors_only():
    issues = validate_experiment_taxonomy(Path.cwd())
    errors = [issue for issue in issues if issue.level == "error"]
    assert errors == [], "\n".join(issue.format() for issue in errors)


def test_registry_row_rejects_invalid_controlled_value():
    row = {
        "experiment_id": "example_invalid",
        "dataset": "not_a_dataset",
        "hybrid_balance_class": ["H1_post_deterministic"],
    }
    issues = validate_registry_row_controlled_values(row, experiment_index=0)
    assert any(issue.code == "invalid_controlled_value" for issue in issues)


def test_registry_row_requires_array_fields_to_be_arrays():
    row = {
        "experiment_id": "example_array",
        "dataset": "gan_2026",
        "hybrid_balance_class": "H1_post_deterministic",
    }
    issues = validate_registry_row_controlled_values(row, experiment_index=0)
    assert any(issue.code == "array_field_not_array" for issue in issues)


def test_registry_row_requires_decision_doc_for_reject_outcome(tmp_path: Path):
    row = {
        "experiment_id": "example_reject",
        "outcome": "reject",
        "decision_doc": "pending_backfill",
    }
    issues = validate_registry_row_decision_doc(row, repo_root=tmp_path)
    assert any(issue.code == "decision_doc_missing" for issue in issues)


def test_registry_row_accepts_existing_decision_doc(tmp_path: Path):
    doc = tmp_path / "docs" / "decision.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# Decision\n", encoding="utf-8")
    row = {
        "experiment_id": "example_promote",
        "outcome": "promote",
        "decision_doc": "docs/decision.md",
    }
    issues = validate_registry_row_decision_doc(row, repo_root=tmp_path)
    assert issues == []


def test_registry_row_canonical_run_missing_is_error_without_documentation(tmp_path: Path):
    row = {
        "experiment_id": "example_run",
        "canonical_run_id": "missing_run_id",
    }
    issues = validate_registry_row_canonical_run(row, runs_root=tmp_path / "runs")
    assert any(issue.code == "canonical_run_missing" for issue in issues)


def test_registry_row_canonical_run_missing_can_be_warning_when_documented(tmp_path: Path):
    row = {
        "experiment_id": "example_run",
        "canonical_run_id": "missing_run_id",
        "notes": "run directory is referenced by docs but is not present in the current local runs folder.",
    }
    issues = validate_registry_row_canonical_run(row, runs_root=tmp_path / "runs")
    assert issues == [
        ValidationIssue(
            level="warning",
            code="canonical_run_missing_documented",
            message=(
                "canonical_run_id 'missing_run_id' is absent under runs/, but the row "
                "documents the missing artifact."
            ),
            path="experiments[example_run].canonical_run_id",
        )
    ]


def test_comparison_group_allows_schema_ladder_with_caveat():
    rows = [
        {
            "experiment_id": "exect_s1",
            "comparison_group": "exect_schema_complexity_gpt_validation_v1",
            "schema_complexity": "exect_s1",
            "model_track": "gpt4_1_mini",
            "varied_factor": "schema_complexity",
            "comparison_caveat": "schema ladder caveat",
            "fixed_controls": {
                "scorer": "exect_field_family_deterministic_v1",
                "split": "exectv2_fixed_v1:validation",
            },
        },
        {
            "experiment_id": "exect_s2",
            "comparison_group": "exect_schema_complexity_gpt_validation_v1",
            "schema_complexity": "exect_s2",
            "model_track": "gpt4_1_mini",
            "varied_factor": "schema_complexity",
            "comparison_caveat": "schema ladder caveat",
            "fixed_controls": {
                "scorer": "exect_s2_field_family_deterministic_v1",
                "split": "exectv2_fixed_v1:validation",
            },
        },
    ]
    issues = validate_comparison_groups(rows)
    assert issues == []


def test_comparison_group_flags_unexplained_scorer_mix():
    rows = [
        {
            "experiment_id": "a",
            "comparison_group": "bad_group",
            "schema_complexity": "gan_s0",
            "model_track": "gpt4_1_mini",
            "varied_factor": "program_architecture",
            "fixed_controls": {
                "scorer": "gan_frequency_deterministic_v1",
                "split": "gan_2026_fixed_v1:validation",
            },
        },
        {
            "experiment_id": "b",
            "comparison_group": "bad_group",
            "schema_complexity": "gan_s0",
            "model_track": "gpt4_1_mini",
            "varied_factor": "program_architecture",
            "fixed_controls": {
                "scorer": "other_scorer",
                "split": "gan_2026_fixed_v1:validation",
            },
        },
    ]
    issues = validate_comparison_groups(rows)
    assert any(issue.code == "comparison_group_incompatible" for issue in issues)


def test_validation_failed_treats_warnings_as_failure_by_default():
    issues = [
        ValidationIssue(
            level="warning",
            code="canonical_run_missing_documented",
            message="documented missing run",
        )
    ]
    assert validation_failed(issues)
    assert not validation_failed(issues, include_warnings=False)
