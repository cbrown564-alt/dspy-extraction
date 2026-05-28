from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clinical_extraction.exect.medication_payload import (
    build_exect_medication_payload,
    summarize_medication_payload_rows,
)


def test_medication_payload_separates_annotation_current_from_lifecycle_status():
    note = (
        "Current medication: Lamictal 100mg BD.\n"
        "Plan: To start levetiracetam 250mg nocte.\n"
        "Previous medication: carbamazepine stopped due to rash.\n"
    )
    annotations = [
        {
            "entity": "Prescription",
            "start_index": "20",
            "end_index": "28",
            "text": "Lamictal",
            "attributes": {"CUIPhrase": "lamotrigine", "DrugName": "Lamictal"},
        },
        {
            "entity": "Prescription",
            "start_index": "48",
            "end_index": "61",
            "text": "levetiracetam",
            "attributes": {"CUIPhrase": "levetiracetam", "DrugName": "levetiracetam"},
        },
    ]

    rows = build_exect_medication_payload(
        note,
        annotations=annotations,
        document_id="EA_TEST",
    )

    annotated = [row for row in rows if row.source_kind == "annotation_prescription"]
    assert [row.benchmark_medication for row in annotated] == [
        "lamictal",
        "levetiracetam",
    ]
    assert all(row.annotation_policy_current for row in annotated)
    assert annotated[1].lifecycle_status == "planned"
    assert annotated[1].benchmark_role == "annotated_current_rx"

    note_previous = next(
        row
        for row in rows
        if row.source_kind == "note_surface" and row.raw_text == "carbamazepine"
    )
    assert note_previous.lifecycle_status == "previous"
    assert note_previous.annotation_policy_current is False
    assert note_previous.benchmark_medication is None


def test_medication_payload_summary_counts_lifecycle_and_benchmark_rows():
    note = (
        "Current medication: lamotrigine 100mg BD (reduce and stop over 8 weeks).\n"
        "Plan: To start levetiracetam 250mg nocte.\n"
        "Medication: citalopram 20mg daily.\n"
    )
    annotations = [
        {
            "entity": "Prescription",
            "start_index": "20",
            "end_index": "31",
            "text": "lamotrigine",
            "attributes": {"CUIPhrase": "lamotrigine"},
        }
    ]

    summary = summarize_medication_payload_rows(
        build_exect_medication_payload(note, annotations=annotations)
    )

    assert summary["annotation_prescription_rows"] == 1
    assert summary["benchmark_medication_candidates"] == 1
    assert summary["lifecycle_status_counts"]["current"] >= 1
    assert summary["lifecycle_status_counts"]["planned"] >= 1
    assert summary["taper_or_stop_rows"] >= 1
    assert summary["non_asm_rows"] >= 1
