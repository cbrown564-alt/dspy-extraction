from pathlib import Path


def test_first_dspy_schema_sequence_decision_records_required_controls():
    note = Path("docs/architecture/first_dspy_schema_sequence.md").read_text(encoding="utf-8")

    assert "Gan frequency first" in note
    assert "ExECT S0/S1" in note
    assert "Dataset and split" in note
    assert "Model/provider" in note
    assert "Schema level" in note
    assert "Program variant" in note
    assert "Scorer mode" in note
    assert "Metric caveats" in note
