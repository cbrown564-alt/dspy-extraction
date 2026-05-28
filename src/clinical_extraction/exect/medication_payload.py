"""Medication current-Rx and lifecycle payloads for ExECT decomposition."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Literal

from pydantic import Field

from clinical_extraction.datasets.exect import canonical_medication_name
from clinical_extraction.exect.medication_primitives import (
    build_exect_medication_candidate_payloads,
    exect_medication_benchmark_bridge,
    infer_exect_medication_temporality,
)
from clinical_extraction.pipeline.sectioning import section_note
from clinical_extraction.schemas import FrozenModel

MedicationPayloadSource = Literal["annotation_prescription", "note_surface"]
MedicationLifecycleStatus = Literal["current", "planned", "previous", "unknown"]
MedicationBenchmarkRole = Literal[
    "annotated_current_rx",
    "note_lifecycle_current_candidate",
    "lifecycle_diagnostic",
]

EXECT_MEDICATION_PAYLOAD_ID = "exect.medication.rx_candidates.v1"

_DOSE_LINE_RE = re.compile(
    r"\b(?:\d+(?:\.\d+)?\s*)?"
    r"(?:mg|mgs|milligram|milligrams|milligrammes|mcg|micrograms)\b"
    r"|"
    r"\b(?:bd|od|tds|qds|nocte|twice a day|once a day|daily|morning|evening)\b",
    re.IGNORECASE,
)
_TAPER_OR_STOP_RE = re.compile(
    r"\b(?:reduce and stop|reduce|wean|weaned|taper|stop over|until it stops)\b",
    re.IGNORECASE,
)


class ExectMedicationPayloadRow(FrozenModel):
    """A medication row that separates benchmark-current policy from lifecycle cues."""

    payload_id: str = EXECT_MEDICATION_PAYLOAD_ID
    document_id: str | None = None
    source_kind: MedicationPayloadSource
    raw_text: str
    canonical_medication: str
    benchmark_medication: str | None = None
    lifecycle_status: MedicationLifecycleStatus
    annotation_policy_current: bool = False
    benchmark_role: MedicationBenchmarkRole
    is_asm: bool
    prescription_list_member: bool = False
    dose_line: bool = False
    taper_or_stop: bool = False
    section: str | None = None
    evidence_text: str
    start: int | None = None
    end: int | None = None
    caveats: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_exect_medication_payload(
    note_text: str,
    *,
    annotations: list[dict[str, Any]] | None = None,
    document_id: str | None = None,
) -> list[ExectMedicationPayloadRow]:
    """Return medication rows for benchmark current-Rx and lifecycle diagnostics.

    Prescription annotations define the benchmark current-Rx surface, even when
    local text contains lifecycle cues. Note-surface candidates are retained as
    diagnostic lifecycle rows so planned, previous, tapering, non-ASM, and
    dose-line cases can be measured without changing ExECT scorer policy.
    """

    rows: list[ExectMedicationPayloadRow] = []
    for annotation in annotations or []:
        if annotation.get("entity") != "Prescription":
            continue
        row = _annotation_prescription_row(
            note_text,
            annotation=annotation,
            document_id=document_id,
        )
        if row is not None:
            rows.append(row)

    for candidate in build_exect_medication_candidate_payloads(note_text):
        rows.append(
            _note_surface_row(
                note_text,
                candidate=candidate,
                document_id=document_id,
            )
        )

    return sorted(
        rows,
        key=lambda row: (
            row.start if row.start is not None else 10**9,
            row.source_kind,
            row.raw_text.lower(),
        ),
    )


def benchmark_current_rx_values(
    rows: list[ExectMedicationPayloadRow],
) -> list[str]:
    """Return canonical benchmark current-Rx values from annotation rows."""

    return _dedupe(
        [
            row.canonical_medication
            for row in rows
            if row.source_kind == "annotation_prescription"
            and row.annotation_policy_current
            and row.canonical_medication
        ]
    )


def note_lifecycle_current_values(
    rows: list[ExectMedicationPayloadRow],
) -> list[str]:
    """Return canonical note-surface current candidates for diagnostic comparison."""

    return _dedupe(
        [
            row.canonical_medication
            for row in rows
            if row.source_kind == "note_surface"
            and row.lifecycle_status == "current"
            and row.is_asm
            and row.benchmark_medication is not None
        ]
    )


def summarize_medication_payload_rows(
    rows: list[ExectMedicationPayloadRow],
) -> dict[str, Any]:
    source_counts = Counter(row.source_kind for row in rows)
    status_counts = Counter(row.lifecycle_status for row in rows)
    return {
        "rows": len(rows),
        "annotation_prescription_rows": source_counts["annotation_prescription"],
        "note_surface_rows": source_counts["note_surface"],
        "benchmark_medication_candidates": len(benchmark_current_rx_values(rows)),
        "note_lifecycle_current_candidates": len(note_lifecycle_current_values(rows)),
        "lifecycle_status_counts": dict(sorted(status_counts.items())),
        "non_asm_rows": sum(not row.is_asm for row in rows),
        "planned_rows": status_counts["planned"],
        "previous_rows": status_counts["previous"],
        "unknown_temporality_rows": status_counts["unknown"],
        "taper_or_stop_rows": sum(row.taper_or_stop for row in rows),
        "dose_line_rows": sum(row.dose_line for row in rows),
        "dose_only_rows": sum(
            row.dose_line and row.lifecycle_status == "unknown" for row in rows
        ),
        "prescription_list_rows": sum(row.prescription_list_member for row in rows),
    }


def _annotation_prescription_row(
    note_text: str,
    *,
    annotation: dict[str, Any],
    document_id: str | None,
) -> ExectMedicationPayloadRow | None:
    attrs = annotation.get("attributes", {})
    raw_value = str(
        attrs.get("CUIPhrase")
        or attrs.get("DrugName")
        or annotation.get("text")
        or ""
    )
    canonical = canonical_medication_name(raw_value)
    if not canonical:
        return None

    start, end = _annotation_offsets(annotation)
    evidence = _evidence_for_offsets(note_text, start, end) or str(
        annotation.get("text") or raw_value
    ).replace("-", " ")
    context = _local_context(note_text, start, end) if start is not None and end is not None else evidence
    bridge = exect_medication_benchmark_bridge(
        raw_value,
        note_text=note_text,
        evidence_text=context,
    )
    temporality = infer_exect_medication_temporality(context)
    lifecycle_status = _coerce_lifecycle_status(temporality.canonical_value)
    is_asm = bool(bridge.metadata.get("is_asm"))
    caveats = [
        "Prescription annotations are treated as benchmark current-Rx by ExECT policy.",
        "Lifecycle status is diagnostic because prescription JSON has no native temporality column.",
    ]
    if temporality.clinical_caveat:
        caveats.append(temporality.clinical_caveat)
    if bridge.clinical_caveat:
        caveats.append(bridge.clinical_caveat)

    return ExectMedicationPayloadRow(
        document_id=document_id,
        source_kind="annotation_prescription",
        raw_text=_clean_raw_text(annotation.get("text") or raw_value),
        canonical_medication=canonical,
        benchmark_medication=bridge.benchmark_value if is_asm else None,
        lifecycle_status=lifecycle_status,
        annotation_policy_current=True,
        benchmark_role="annotated_current_rx",
        is_asm=is_asm,
        prescription_list_member=True,
        dose_line=_has_dose_line(context),
        taper_or_stop=_has_taper_or_stop(context),
        section=_section_for_offset(note_text, start),
        evidence_text=context,
        start=start,
        end=end,
        caveats=caveats,
        metadata={
            "drug_name": attrs.get("DrugName"),
            "cui_phrase": attrs.get("CUIPhrase"),
            "lifecycle_cues": temporality.metadata.get("cues", []),
            "benchmark_surface_policy": bridge.metadata.get("benchmark_surface_policy"),
        },
    )


def _note_surface_row(
    note_text: str,
    *,
    candidate: Any,
    document_id: str | None,
) -> ExectMedicationPayloadRow:
    evidence = str(candidate.metadata.get("context") or candidate.source_span_text)
    bridge = exect_medication_benchmark_bridge(
        str(candidate.raw_text),
        note_text=note_text,
        evidence_text=evidence,
    )
    lifecycle_status = _coerce_lifecycle_status(candidate.metadata.get("temporality"))
    is_asm = bool(bridge.metadata.get("is_asm"))
    benchmark_medication = (
        str(candidate.benchmark_value)
        if candidate.benchmark_value is not None and is_asm
        else None
    )
    benchmark_role: MedicationBenchmarkRole = (
        "note_lifecycle_current_candidate"
        if benchmark_medication is not None and lifecycle_status == "current"
        else "lifecycle_diagnostic"
    )

    return ExectMedicationPayloadRow(
        document_id=document_id,
        source_kind="note_surface",
        raw_text=str(candidate.raw_text),
        canonical_medication=str(candidate.normalized_value or bridge.canonical_value),
        benchmark_medication=benchmark_medication,
        lifecycle_status=lifecycle_status,
        annotation_policy_current=False,
        benchmark_role=benchmark_role,
        is_asm=is_asm,
        prescription_list_member=_is_prescription_list_context(evidence),
        dose_line=_has_dose_line(evidence),
        taper_or_stop=_has_taper_or_stop(evidence),
        section=_section_for_offset(note_text, candidate.start),
        evidence_text=evidence,
        start=candidate.start,
        end=candidate.end,
        caveats=list(candidate.caveats),
        metadata={
            **candidate.metadata,
            "benchmark_surface_policy": bridge.metadata.get("benchmark_surface_policy"),
        },
    )


def _annotation_offsets(annotation: dict[str, Any]) -> tuple[int | None, int | None]:
    try:
        start = int(annotation.get("start_index"))
        end = int(annotation.get("end_index"))
    except (TypeError, ValueError):
        return None, None
    if start < 0 or end < start:
        return None, None
    return start, end


def _evidence_for_offsets(note_text: str, start: int | None, end: int | None) -> str | None:
    if start is None or end is None or start >= len(note_text):
        return None
    return note_text[start : min(end, len(note_text))]


def _local_context(note_text: str, start: int | None, end: int | None) -> str:
    if start is None or end is None:
        return ""
    line_start = note_text.rfind("\n", 0, start) + 1
    line_end = note_text.find("\n", end)
    if line_end == -1:
        line_end = len(note_text)
    previous_sentence = note_text.rfind(". ", 0, start)
    sentence_start = max(
        line_start,
        previous_sentence + 2 if previous_sentence != -1 else line_start,
    )
    sentence_end = note_text.find(". ", end)
    if sentence_end == -1:
        sentence_end = line_end
    else:
        sentence_end = min(sentence_end + 1, line_end)
    return note_text[sentence_start:sentence_end].strip()


def _section_for_offset(note_text: str, offset: int | None) -> str | None:
    if offset is None:
        return None
    for section in section_note(note_text):
        if section.start <= offset < section.end:
            return section.title
    return None


def _coerce_lifecycle_status(value: Any) -> MedicationLifecycleStatus:
    if value in {"current", "planned", "previous"}:
        return value
    return "unknown"


def _has_dose_line(text: str) -> bool:
    return bool(_DOSE_LINE_RE.search(text or ""))


def _has_taper_or_stop(text: str) -> bool:
    return bool(_TAPER_OR_STOP_RE.search(text or ""))


def _is_prescription_list_context(text: str) -> bool:
    lowered = (text or "").strip().lower()
    return lowered.startswith(("current medication", "medication", "current anti"))


def _clean_raw_text(text: Any) -> str:
    return str(text or "").replace("-", " ").strip()


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


__all__ = [
    "EXECT_MEDICATION_PAYLOAD_ID",
    "ExectMedicationPayloadRow",
    "benchmark_current_rx_values",
    "build_exect_medication_payload",
    "note_lifecycle_current_values",
    "summarize_medication_payload_rows",
]
