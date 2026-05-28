from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clinical_extraction.evaluation.exect_frequency_event_rate_payload import build_report


def test_exect_frequency_event_rate_payload_audit_covers_validation_gold():
    report = build_report(Path("data/splits/exectv2_splits.json"), "validation")

    broad = report["candidate_modes"]["broad"]
    high_precision = report["candidate_modes"]["high_precision"]

    assert broad["documents"] == 40
    assert broad["gold_documents"] == 24
    assert broad["gold_labels"] == 43
    assert broad["matched_gold_labels"] == 43
    assert broad["coverage"] == 1.0
    assert broad["full_label_documents"] == 24
    assert broad["precision"] < 0.25

    assert high_precision["matched_gold_labels"] < broad["matched_gold_labels"]
    assert high_precision["by_gold_label_type"]["qualitative_change"]["coverage"] == 0.0
