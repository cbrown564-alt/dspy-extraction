"""Tests for experiment registry matrix export."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_EXPORT = Path("scripts/export_experiment_registry_matrix.py")
_spec = importlib.util.spec_from_file_location("export_experiment_registry_matrix", _EXPORT)
assert _spec and _spec.loader
_export = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_export)


def test_curated_matrix_includes_s4_temporality_group():
    reg = json.loads(Path("docs/experiments/synthesis/experiment_registry.json").read_text(encoding="utf-8"))
    rows = _export._filter_rows(reg["experiments"], "curated")
    groups = {row["comparison_group"] for row in rows}
    assert "exect_s4_temporality_deterministic_v1" in groups
    temporality = [
        r for r in rows if r["comparison_group"] == "exect_s4_temporality_deterministic_v1"
    ]
    assert len(temporality) == 4
    outcomes = {r["outcome"] for r in temporality}
    assert outcomes == {"hold", "reject"}


def test_render_matrix_contains_comparison_group_sections():
    reg = json.loads(Path("docs/experiments/synthesis/experiment_registry.json").read_text(encoding="utf-8"))
    markdown = _export.render_matrix(reg, "decided")
    assert "## gan_s0_architecture_gpt_validation_v1" in markdown
    assert "monthly_frequency_accuracy=" in markdown
    assert "## exect_s4_temporality_deterministic_v1" in markdown
    assert "**reject**" in markdown


def test_render_matrix_table_rows_are_contiguous():
    reg = json.loads(Path("docs/experiments/synthesis/experiment_registry.json").read_text(encoding="utf-8"))
    markdown = _export.render_matrix(reg, "curated")
    assert "|\n\n|" not in markdown
    assert markdown.count("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |") >= 1
