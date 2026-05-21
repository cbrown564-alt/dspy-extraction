"""Tests for the generated research atlas."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_EXPORT = Path("scripts/export_research_atlas.py")
_spec = importlib.util.spec_from_file_location("export_research_atlas", _EXPORT)
assert _spec and _spec.loader
_export = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_export)


def test_render_journey_mermaid_contains_major_research_phases():
    reg = json.loads(Path("docs/experiment_registry.json").read_text(encoding="utf-8"))
    mermaid = _export.render_journey_mermaid(reg)
    assert "flowchart LR" in mermaid
    assert "Gan temporal-candidates promoted" in mermaid
    assert "ExECT S1-S4 schema ladder frozen" in mermaid
    assert "Current frontier" in mermaid


def test_render_decision_map_groups_registered_comparisons():
    reg = json.loads(Path("docs/experiment_registry.json").read_text(encoding="utf-8"))
    mermaid = _export.render_decision_map_mermaid(reg)
    assert "flowchart TD" in mermaid
    assert "gan_s0_architecture_qwen_validation_v1" in mermaid
    assert "exect_s4_temporality_deterministic_v1" in mermaid
    assert "classDef reject" in mermaid


def test_render_evidence_matrix_shows_open_empty_cells_and_metrics():
    reg = json.loads(Path("docs/experiment_registry.json").read_text(encoding="utf-8"))
    markdown = _export.render_evidence_matrix(reg)
    assert "# Evidence Matrix" in markdown
    assert "| gan_s0 |" in markdown
    assert "| exect_s4 |" in markdown
    assert "monthly_frequency_accuracy=" in markdown
    assert "Empty cells are useful" in markdown


def test_write_atlas_creates_expected_files(tmp_path: Path):
    reg = json.loads(Path("docs/experiment_registry.json").read_text(encoding="utf-8"))
    kanban = Path("docs/kanban_plan.md").read_text(encoding="utf-8")
    output_dir = tmp_path / "research_atlas"
    index = tmp_path / "research_atlas.md"
    _export.write_atlas(reg, kanban, output_dir, index)

    assert index.exists()
    assert (output_dir / "journey.mmd").exists()
    assert (output_dir / "decision_map.mmd").exists()
    assert (output_dir / "evidence_matrix.md").exists()
    assert (output_dir / "open_frontiers.md").exists()
    assert "Recommended Next Pull" in (output_dir / "open_frontiers.md").read_text(
        encoding="utf-8"
    )
