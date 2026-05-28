from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clinical_extraction.exect.medication_payload import (
    build_exect_medication_payload,
    summarize_medication_payload_rows,
)
from clinical_extraction.evaluation.exect_medication_current_rx_lifecycle_payload import (
    build_report,
)
from clinical_extraction.evaluation.exect_medication_current_rx_ceiling_probe import (
    DEFAULT_S1_RUN,
    DEFAULT_S5_RUN,
    build_report as build_ceiling_report,
)
from clinical_extraction.evaluation.exect_medication_stack_interference_probe import (
    build_report as build_stack_interference_report,
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


def test_medication_payload_audit_reproduces_validation_current_rx_gold():
    report = build_report(Path("data/splits/exectv2_splits.json"), "validation")

    current = report["current_rx_summary"]
    lifecycle = report["note_lifecycle_current_summary"]

    assert current["documents"] == 40
    assert current["gold_labels"] == 47
    assert current["matched_gold_labels"] == 47
    assert current["coverage"] == 1.0
    assert lifecycle["matched_gold_labels"] < current["matched_gold_labels"]
    assert report["decision"]["medication_lifecycle_temporality"] == (
        "diagnostic/deferred"
    )


def test_medication_current_rx_ceiling_probe_compares_s1_and_s5_surfaces():
    report = build_ceiling_report(
        splits_path=Path("data/splits/exectv2_splits.json"),
        split_name="validation",
        e3_payload_path=Path(
            "docs/experiments/exect/"
            "exect_medication_current_rx_lifecycle_payload_audit_20260528.json"
        ),
        s1_run=DEFAULT_S1_RUN,
        s5_run=DEFAULT_S5_RUN,
    )

    isolated = report["surface_summaries"]["isolated_current_rx_payload"]
    s1 = report["surface_summaries"]["s1_gpt_surface"]
    s5 = report["surface_summaries"]["s5_gpt_surface"]

    assert isolated["gold_support"] == 47
    assert isolated["tp"] == 47
    assert isolated["fp"] == 0
    assert isolated["fn"] == 0
    assert isolated["f1"] == 1.0

    assert s1["tp"] == 45
    assert s1["fp"] == 5
    assert s1["fn"] == 2
    assert s5["tp"] == 47
    assert s5["fp"] == 12
    assert s5["fn"] == 0
    assert report["lifecycle_policy"].startswith("Lifecycle rows are diagnostic")


def test_medication_stack_interference_probe_attributes_s5_false_positives():
    report = build_stack_interference_report(
        splits_path=Path("data/splits/exectv2_splits.json"),
        split_name="validation",
        e3_payload_path=Path(
            "docs/experiments/exect/"
            "exect_medication_current_rx_lifecycle_payload_audit_20260528.json"
        ),
        s1_run=DEFAULT_S1_RUN,
        s5_run=DEFAULT_S5_RUN,
    )

    delta = report["stack_delta_summary"]
    categories = report["interference_category_counts"]

    assert delta["s5_false_positives"] == 12
    assert delta["s5_only_false_positives"] == 8
    assert delta["shared_s1_s5_false_positives"] == 4
    assert delta["s5_recovered_s1_false_negatives"] == 2

    assert categories["planned_or_future_evidence"] == 3
    assert categories["historical_failed_or_switched_evidence"] == 6
    assert categories["missing_gold_or_annotation_policy"] == 2
    assert categories["other_medication_or_non_current_section"] == 1
    assert report["decision"]["next_mechanism"] == (
        "payload routing or prompt isolation before a broader medication temporality guard"
    )
