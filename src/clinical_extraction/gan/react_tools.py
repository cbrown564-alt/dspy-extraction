"""Deterministic tools for the Gan S0 bounded ReAct temporal probe."""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Any

from clinical_extraction.gan.frequency import (
    label_to_monthly_frequency,
    normalize_label,
    pragmatic_category,
    purist_category,
)
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates_from_note,
    format_temporal_candidates_for_prompt,
    temporal_candidate_to_dict,
)

_FREQUENCY_SENTENCE_RE = re.compile(
    r"\b("
    r"seizure|seizures|cluster|clusters|episode|episodes|"
    r"frequency|per week|per month|per year|seizure free|"
    r"year to date|ytd|last seizure|last episode"
    r")\b",
    re.IGNORECASE,
)
_DATE_ANCHOR_RE = re.compile(
    r"(?:Clinic Date|Date):\s*\d{1,2}\s+\w+\s+\d{4}|"
    r"\blast (?:seizure|episode)[^.]{0,80}|"
    r"\bsince \d{1,2}/\d{4}|"
    r"\b(?:january|february|march|april|may|june|july|august|"
    r"september|october|november|december)\b[^.]{0,40}|"
    r"\bseizure free for [^.]{0,40}|"
    r"\byear to date\b|\bytd\b",
    re.IGNORECASE,
)
_CLUSTER_LABEL_RE = re.compile(
    r"(?P<clusters>.+?) cluster per (?:(?P<period>.+?) )?(?P<unit>day|week|month|year), "
    r"(?P<per_cluster>.+?) per cluster",
    re.IGNORECASE,
)


def find_temporal_frequency_candidates(note_text: str) -> str:
    """Return deterministic temporal frequency candidates extracted from the note."""

    candidates = build_temporal_frequency_candidates_from_note(note_text)
    if not candidates:
        return "No deterministic temporal frequency candidates were found."
    return format_temporal_candidates_for_prompt(candidates)


def list_temporal_frequency_candidate_records(note_text: str) -> str:
    """Return temporal candidates as JSON for structured tool observations."""

    candidates = build_temporal_frequency_candidates_from_note(note_text)
    payload = [temporal_candidate_to_dict(candidate) for candidate in candidates]
    return json.dumps(payload, indent=2)


def find_frequency_mention_spans(note_text: str) -> str:
    """Return note sentences that mention seizure frequency or temporal anchors."""

    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", note_text) if part.strip()]
    matches = [sentence for sentence in sentences if _FREQUENCY_SENTENCE_RE.search(sentence)]
    if not matches:
        return "No frequency-related sentences were found."
    return "\n".join(f"- {sentence}" for sentence in matches[:20])


def extract_temporal_anchors(note_text: str) -> str:
    """Return clinic-date and relative temporal anchor phrases from the note."""

    lines: list[str] = []
    clinic_date = extract_clinic_date(note_text)
    if clinic_date != "not found":
        lines.append(f"clinic_date={clinic_date}")
    anchors = []
    for match in _DATE_ANCHOR_RE.finditer(note_text):
        phrase = match.group(0).strip()
        if phrase and phrase not in anchors:
            anchors.append(phrase)
    if not anchors:
        lines.append("No additional temporal anchors were found.")
    else:
        lines.extend(f"- {anchor}" for anchor in anchors[:20])
    return "\n".join(lines)


def extract_clinic_date(note_text: str) -> str:
    """Return the clinic or letter date as YYYY-MM-DD when present."""

    match = re.search(
        r"(?:Clinic Date|Date):\s*(?P<day>\d{1,2})\s+"
        r"(?P<month>January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+(?P<year>\d{4})",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return "not found"
    month_map = {
        name.lower(): index
        for index, name in enumerate(
            [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
            start=1,
        )
    }
    month = month_map[match.group("month").lower()]
    return date(int(match.group("year")), month, int(match.group("day"))).isoformat()


def compute_elapsed_days(start_date_iso: str, end_date_iso: str) -> str:
    """Compute inclusive elapsed days between two YYYY-MM-DD dates."""

    try:
        start = date.fromisoformat(start_date_iso.strip())
        end = date.fromisoformat(end_date_iso.strip())
    except ValueError:
        return "error: dates must be YYYY-MM-DD"
    elapsed = (end - start).days
    return str(elapsed)


def validate_gan_frequency_label(label: str) -> str:
    """Validate a candidate Gan label against deterministic parsing utilities."""

    normalized = normalize_label(label)
    if normalized in {"unknown", "no seizure frequency reference"}:
        return f"ok: special label {normalized!r}"
    if normalized.startswith("seizure free for "):
        return f"ok: seizure-free label {normalized!r}"
    try:
        monthly = label_to_monthly_frequency(label)
        return (
            f"ok: monthly={monthly:.4f}; purist={purist_category(label)}; "
            f"pragmatic={pragmatic_category(label)}"
        )
    except ValueError as exc:
        return f"error: {exc}"


def validate_cluster_format(label: str) -> str:
    """Check that cluster labels include both cluster period and per-cluster count."""

    normalized = normalize_label(label)
    if "cluster per" not in normalized:
        return "ok: not a cluster label"
    if _CLUSTER_LABEL_RE.fullmatch(normalized):
        return "ok: complete cluster label"
    return (
        "error: cluster label must include both "
        "'N cluster per unit' and 'M per cluster'"
    )


def validate_evidence_quote(note_text: str, evidence_text: str) -> str:
    """Check whether evidence_text is an exact contiguous substring of note_text."""

    if not evidence_text.strip():
        return "error: evidence_text is empty"
    start = note_text.find(evidence_text)
    if start < 0:
        return "error: evidence_text is not an exact contiguous substring of note_text"
    end = start + len(evidence_text)
    return f"ok: start={start}; end={end}"


GAN_REACT_TEMPORAL_MAX_ITERS = 4

GAN_REACT_TEMPORAL_TOOLS: list[Any] = [
    find_temporal_frequency_candidates,
    list_temporal_frequency_candidate_records,
    find_frequency_mention_spans,
    extract_temporal_anchors,
    extract_clinic_date,
    compute_elapsed_days,
    validate_gan_frequency_label,
    validate_cluster_format,
    validate_evidence_quote,
]


def count_react_tool_calls(trajectory: dict[str, Any]) -> int:
    """Count non-finish tool invocations in a ReAct trajectory."""

    return sum(
        1
        for key, value in trajectory.items()
        if key.startswith("tool_name_") and value != "finish"
    )


def serialize_react_trajectory(trajectory: dict[str, Any]) -> dict[str, Any]:
    """Normalize a ReAct trajectory for run artifacts."""

    return dict(trajectory)
