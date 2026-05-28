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

_BACKFILL_MANIFEST = Path(
    "docs/archive/experiments/synthesis/pre_component_pivot/"
    "hybrid_cap25_registry_backfill_manifest_20260528.json"
)


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
    assert "X3 refreshed registry-derived export" in markdown
    assert "May 28 component pivot" in markdown
    assert "R11-R15 Gan decisions" in markdown
    assert "X1 component-ceiling backfill" in markdown
    assert "C4 authority classes" in markdown
    assert "C10 provenance cleanup" in markdown
    assert "## gan_s0_architecture_gpt_validation_v1" in markdown
    assert "monthly_frequency_accuracy=" in markdown
    assert "## exect_s4_temporality_deterministic_v1" in markdown
    assert "**reject**" in markdown


def test_render_matrix_table_rows_are_contiguous():
    reg = json.loads(Path("docs/experiments/synthesis/experiment_registry.json").read_text(encoding="utf-8"))
    markdown = _export.render_matrix(reg, "curated")
    assert "|\n\n|" not in markdown
    assert markdown.count("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |") >= 1


def test_historical_registry_backfill_rows_live_in_retained_manifest():
    assert (
        "docs/archive/experiments/synthesis/pre_component_pivot"
        in _BACKFILL_MANIFEST.as_posix()
    )
    payload = json.loads(_BACKFILL_MANIFEST.read_text(encoding="utf-8"))
    rows = payload["rows"]

    assert payload["status"] == "archive / retained provenance"
    assert payload["source_script"].startswith("scripts/")
    assert len(rows) >= 40
    assert rows[0]["experiment_id"] == "gan_s0_stage_graph_g1_direct_cap25_gpt4_1_mini"
    assert "Cap-25 search grid" in payload["provenance_notes"][0]
