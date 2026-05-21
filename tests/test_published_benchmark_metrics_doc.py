from pathlib import Path


def test_published_benchmark_metrics_note_records_values_and_alignment_caveats():
    note = Path("docs/policies/published_benchmark_metrics.md").read_text(encoding="utf-8")

    assert "ExECTv2 per-item F1" in note
    assert "| Diagnosis | 572 | 0.85 | 0.94 | 0.83 |" in note
    assert "| All | 2047 | 0.87 | 0.90 | 0.73 |" in note
    assert "micro-F1 up to 0.788" in note
    assert "0.847" in note
    assert "Partially aligned" in note
    assert "clinical_extraction.evaluation.benchmarks" in note
    assert "must not be used to claim published benchmark reproduction" in note
    assert "synthetic_data_subset_1500.json" in note
