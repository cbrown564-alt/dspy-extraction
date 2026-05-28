from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clinical_extraction.exect.family_spans import (
    EXECT_FAMILY_SPANS_PRIMITIVE_ID,
    build_exect_family_span_payloads,
    family_span_context,
)
from clinical_extraction.primitives import primitive_registry_by_id
from clinical_extraction.evaluation.exect_family_span_payload import build_report


def test_family_span_payloads_emit_typed_family_spans_with_offsets():
    note = (
        "Diagnosis: Focal epilepsy.\n"
        "Seizure type and frequency: focal seizures twice per month.\n"
        "Medication: lamotrigine 100mg BD.\n"
        "Investigations: MRI normal.\n"
        "Plan: Review in six months.\n"
    )

    spans = build_exect_family_span_payloads(note)
    by_family = {span.normalized_value: span for span in spans}

    assert by_family["diagnosis_problem"].primitive_id == EXECT_FAMILY_SPANS_PRIMITIVE_ID
    assert by_family["diagnosis_problem"].field_family == "multi_family"
    assert by_family["frequency"].source_span_text.startswith(
        "Seizure type and frequency:"
    )
    assert note[by_family["medication"].start : by_family["medication"].end].strip() == (
        "Medication: lamotrigine 100mg BD."
    )
    assert by_family["plan_follow_up"].metadata["family"] == "plan_follow_up"


def test_family_span_context_groups_selected_families_without_full_note():
    note = (
        "Administrative header.\n"
        "Diagnosis: Focal epilepsy.\n"
        "Medication: lamotrigine 100mg BD.\n"
        "Plan: Review in six months.\n"
    )

    context = family_span_context(note, families=["diagnosis_problem", "medication"])

    assert "Diagnosis: Focal epilepsy." in context
    assert "Medication: lamotrigine 100mg BD." in context
    assert "Administrative header." not in context
    assert "Plan: Review in six months." not in context


def test_family_span_primitive_is_registered_as_implemented():
    registry = primitive_registry_by_id()

    assert registry[EXECT_FAMILY_SPANS_PRIMITIVE_ID].status == "implemented"
    assert registry[EXECT_FAMILY_SPANS_PRIMITIVE_ID].field_families == ["multi_family"]


def test_family_span_audit_reports_validation_coverage_and_cap_slice_comparison():
    report = build_report(Path("data/splits/exectv2_splits.json"), "validation")

    assert report["candidate_summary"]["documents"] == 40
    assert "diagnosis_problem" in report["gold_coverage_by_family"]
    assert report["gold_coverage_by_family"]["medication"]["gold_annotations"] > 0
    assert report["gold_coverage_by_family"]["medication"]["coverage"] >= 0.8
    assert report["cap_slice_prompt_comparison"]["documents"] == 25
    assert report["cap_slice_prompt_comparison"]["family_span_chars"] < (
        report["cap_slice_prompt_comparison"]["full_note_chars"]
    )
