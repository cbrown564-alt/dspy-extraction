from pathlib import Path

from clinical_extraction.experiments.inspection_templates import (
    DECISION_REQUIRED_HEADINGS,
    INSPECTION_REQUIRED_HEADINGS,
    TEMPLATE_PATHS,
    validate_decision_document,
    validate_inspection_document,
    validate_template_file,
)


def test_inspection_template_includes_required_headings():
    issues = validate_template_file(
        TEMPLATE_PATHS["inspection"],
        INSPECTION_REQUIRED_HEADINGS,
    )
    assert issues == []


def test_decision_template_includes_required_headings():
    issues = validate_template_file(
        TEMPLATE_PATHS["decision"],
        DECISION_REQUIRED_HEADINGS,
    )
    assert issues == []


def test_exect_s4_frequency_inspection_maps_onto_template():
    path = Path("docs/experiments/exect/exect_s4_frequency_deterministic_gpt_inspection_20260520.md")
    text = path.read_text(encoding="utf-8").lower()
    # Legacy docs use alternate section titles but retain comparability fields.
    assert "comparison group" in text
    assert "exect_s4_field_family_deterministic_v1" in text
    assert "decision" in text
    assert "interpretation" in text
    assert "run" in text
    assert "h2" in text and "l1" in text


def test_exect_s1_interleaving_preregistration_maps_onto_decision_template():
    path = Path("docs/experiments/exect/exect_s1_interleaving_experiment_preregistration_20260520.md")
    text = path.read_text(encoding="utf-8")
    assert "## Research question" in text
    assert "## Fixed controls (all arms)" in text
    assert "## Comparison group" in text
    assert "## Arms" in text
    assert "exect_field_family_deterministic_v1" in text
    assert "interleaving" in text.lower()
    assert "H1" in text and "H2" in text
