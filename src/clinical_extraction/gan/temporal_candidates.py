"""Temporal candidate extraction helpers for Gan seizure-frequency analysis.

These helpers are intentionally diagnostic. They expose event/window ingredients
for hard Gan S0 cases without changing benchmark-facing scorer semantics.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

from clinical_extraction.schemas import GanRecord

TemporalCandidatePresentation = Literal["prose", "table", "json", "bullets"]

IMPLEMENTATION_VARIANT_TO_PRESENTATION: dict[str, TemporalCandidatePresentation] = {
    "cand_prose_v1": "prose",
    "cand_table_v1": "table",
    "cand_json_v1": "json",
    "cand_bullets_v1": "bullets",
}


def presentation_for_implementation_variant(
    implementation_variant: str | None,
) -> TemporalCandidatePresentation | None:
    """Map Axis-3 implementation_variant IDs to formatter presentation keys."""

    if implementation_variant is None:
        return None
    return IMPLEMENTATION_VARIANT_TO_PRESENTATION.get(implementation_variant)


@dataclass(frozen=True)
class GanTemporalFrequencyCandidate:
    """A candidate event/window interpretation for a canonical Gan label."""

    canonical_label: str
    event_count: str
    window_count: str
    window_unit: str
    evidence_text: str
    derivation: str


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

MONTH_PATTERN = "|".join(name.title() for name in MONTHS)


def build_temporal_frequency_candidates(
    record: GanRecord,
) -> list[GanTemporalFrequencyCandidate]:
    """Build auditable temporal candidates from explicit event/window text.

    This is a first scaffold for the Gan temporal-candidate pivot. It captures
    high-value infrequent patterns observed in the Qwen regression slice, but it
    does not replace model extraction or deterministic Gan scoring.
    """

    return build_temporal_frequency_candidates_from_note(record.note_text)


def build_temporal_frequency_candidates_from_note(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    """Build temporal candidates from raw note text (DSPy module / analyzer path)."""

    candidates: list[GanTemporalFrequencyCandidate] = []
    candidates.extend(_breakthrough_after_nearly_year(note_text))
    candidates.extend(_two_dated_events_window(note_text))
    candidates.extend(_last_episode_monthly_candidate(note_text))
    candidates.extend(_count_range_since_prior_month_year(note_text))
    candidates.extend(_ytd_documented_seizure_count(note_text))
    candidates.extend(_clusters_this_quarter(note_text))
    candidates.extend(_weekly_cluster_with_per_cluster_range(note_text))
    candidates.extend(_weekly_clusters_without_per_cluster_count(note_text))
    candidates.extend(_several_times_each_week(note_text))
    return _dedupe_candidates(candidates)


def temporal_candidate_to_dict(
    candidate: GanTemporalFrequencyCandidate,
) -> dict[str, str]:
    """Serialize a candidate for run artifacts and analyzer output."""

    return {
        "canonical_label": candidate.canonical_label,
        "event_count": candidate.event_count,
        "window_count": candidate.window_count,
        "window_unit": candidate.window_unit,
        "evidence_text": candidate.evidence_text,
        "derivation": candidate.derivation,
    }


def _temporal_candidate_header(source: str) -> str:
    if source == "llm":
        return "LLM-extracted temporal frequency candidates (diagnostic hints only):"
    if source == "hybrid":
        return (
            "Hybrid deterministic+LLM temporal frequency candidates "
            "(diagnostic hints only):"
        )
    return "Deterministic temporal frequency candidates (diagnostic hints only):"


def _empty_temporal_candidate_message(source: str) -> str:
    if source == "llm":
        prefix = "LLM-extracted"
    elif source == "hybrid":
        prefix = "Hybrid deterministic+LLM"
    else:
        prefix = "Deterministic"
    return (
        f"No {prefix.lower()} temporal frequency candidates were extracted "
        "from this note."
    )


def _format_temporal_candidates_prose(
    candidates: list[GanTemporalFrequencyCandidate],
    *,
    header: str,
) -> str:
    lines = [header]
    for index, candidate in enumerate(candidates, start=1):
        lines.append(
            f"{index}. canonical_label={candidate.canonical_label!r}; "
            f"event_count={candidate.event_count}; "
            f"window={candidate.window_count} {candidate.window_unit}; "
            f"derivation={candidate.derivation}; "
            f"evidence_text={candidate.evidence_text!r}"
        )
    return "\n".join(lines)


def _format_temporal_candidates_bullets(
    candidates: list[GanTemporalFrequencyCandidate],
    *,
    header: str,
) -> str:
    lines = [header]
    for candidate in candidates:
        lines.append(
            f"- {candidate.canonical_label!r}: "
            f"{candidate.event_count} event(s) per "
            f"{candidate.window_count} {candidate.window_unit}; "
            f"{candidate.derivation}; evidence={candidate.evidence_text!r}"
        )
    return "\n".join(lines)


def _format_temporal_candidates_table(
    candidates: list[GanTemporalFrequencyCandidate],
    *,
    header: str,
) -> str:
    rows = [
        "| # | canonical_label | event_count | window | derivation | evidence_text |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for index, candidate in enumerate(candidates, start=1):
        window = f"{candidate.window_count} {candidate.window_unit}"
        rows.append(
            f"| {index} | {candidate.canonical_label!r} | {candidate.event_count} | "
            f"{window} | {candidate.derivation} | {candidate.evidence_text!r} |"
        )
    return "\n".join([header, *rows])


def _format_temporal_candidates_json(
    candidates: list[GanTemporalFrequencyCandidate],
    *,
    header: str,
) -> str:
    payload = {
        "candidates": [temporal_candidate_to_dict(candidate) for candidate in candidates]
    }
    return f"{header}\n{json.dumps(payload, indent=2)}"


def format_temporal_candidates_for_prompt(
    candidates: list[GanTemporalFrequencyCandidate],
    *,
    source: str = "deterministic",
    presentation: TemporalCandidatePresentation = "prose",
) -> str:
    """Format temporal candidates for adjudication or verifier/repair input."""

    if not candidates:
        return _empty_temporal_candidate_message(source)

    header = _temporal_candidate_header(source)
    if presentation == "table":
        return _format_temporal_candidates_table(candidates, header=header)
    if presentation == "json":
        return _format_temporal_candidates_json(candidates, header=header)
    if presentation == "bullets":
        return _format_temporal_candidates_bullets(candidates, header=header)
    return _format_temporal_candidates_prose(candidates, header=header)


def parse_llm_temporal_candidates_json(
    payload: str | dict[str, Any] | None,
    *,
    note_text: str | None = None,
) -> list[GanTemporalFrequencyCandidate]:
    """Parse and validate model-generated temporal candidate JSON.

    Returns an empty list when parsing fails. When ``note_text`` is provided,
    drops candidates whose ``evidence_text`` is not an exact contiguous substring.
    """

    if payload is None:
        return []
    if isinstance(payload, str):
        stripped = payload.strip()
        if not stripped or stripped.lower() in {"none", "null"}:
            return []
        try:
            raw = json.loads(stripped)
        except json.JSONDecodeError:
            return []
    else:
        raw = payload

    if isinstance(raw, list):
        candidate_rows = raw
    elif isinstance(raw, dict):
        candidate_rows = raw.get("candidates") or raw.get("temporal_candidates") or []
    else:
        return []

    if not isinstance(candidate_rows, list):
        return []

    parsed: list[GanTemporalFrequencyCandidate] = []
    for row in candidate_rows:
        if not isinstance(row, dict):
            continue
        try:
            candidate = GanTemporalFrequencyCandidate(
                canonical_label=str(row["canonical_label"]).strip(),
                event_count=str(row.get("event_count") or ""),
                window_count=str(row.get("window_count") or ""),
                window_unit=str(row.get("window_unit") or ""),
                evidence_text=str(row.get("evidence_text") or "").strip(),
                derivation=str(row.get("derivation") or "llm_candidate"),
            )
        except (KeyError, TypeError, ValueError):
            continue
        if not candidate.canonical_label or not candidate.evidence_text:
            continue
        if note_text is not None and candidate.evidence_text not in note_text:
            continue
        parsed.append(candidate)
    return _dedupe_candidates(parsed)


def merge_temporal_frequency_candidates(
    *candidate_lists: list[GanTemporalFrequencyCandidate],
) -> list[GanTemporalFrequencyCandidate]:
    """Merge multiple candidate lists with canonical-label deduplication."""

    merged: list[GanTemporalFrequencyCandidate] = []
    for candidates in candidate_lists:
        merged.extend(candidates)
    return _dedupe_candidates(merged)


def _breakthrough_after_nearly_year(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*no seizures for nearly a year[^.]*"
        r"tonic seizure[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label="1 per year",
            event_count="1",
            window_count="1",
            window_unit="year",
            evidence_text=evidence,
            derivation=(
                "single breakthrough event after a nearly one-year seizure-free "
                "window"
            ),
        )
    ]


def _two_dated_events_window(note_text: str) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        rf"(?P<evidence>[^.]*initial event was in "
        rf"(?P<month1>{MONTH_PATTERN}) (?P<year1>\d{{4}})[^.]*\."
        rf".*?A second event occurred[^.]*?"
        rf"(?P<month2>{MONTH_PATTERN}) (?P<year2>\d{{4}})[^.]*\.)",
        note_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match is None:
        return []

    start_month = _month_number(match.group("month1"))
    end_month = _month_number(match.group("month2"))
    start_year = int(match.group("year1"))
    end_year = int(match.group("year2"))
    window_months = max(1, (end_year - start_year) * 12 + end_month - start_month)
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"2 per {window_months} month",
            event_count="2",
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="two explicitly dated events define the observation window",
        )
    ]


def _last_episode_monthly_candidate(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        rf"(?P<evidence>[^.]*last episode was recorded on "
        rf"(?P<day>\d{{1,2}}) (?P<month>{MONTH_PATTERN})"
        rf"(?: (?P<year>\d{{4}}))?[^.]*\.)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []

    event_year = int(match.group("year") or clinic_date.year)
    event_date = date(
        event_year,
        _month_number(match.group("month")),
        int(match.group("day")),
    )
    elapsed_days = (clinic_date - event_date).days
    if not 14 <= elapsed_days <= 45:
        return []

    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label="1 per month",
            event_count="1",
            window_count="1",
            window_unit="month",
            evidence_text=evidence,
            derivation=(
                "last recorded event falls roughly one month before the clinic date"
            ),
        )
    ]


def _count_range_since_prior_month_year(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*No further [^.]* since "
        r"(?P<month>\d{1,2})/(?P<year>\d{4}), although "
        r"(?P<count>two to three|two|three) [^.]* remain[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []

    start_month = int(match.group("month"))
    start_year = int(match.group("year"))
    window_months = max(
        1,
        (clinic_date.year - start_year) * 12 + clinic_date.month - start_month,
    )
    event_count = _count_phrase_to_label(match.group("count"))
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"{event_count} per {window_months} month",
            event_count=event_count,
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="count range is anchored to an explicit prior month/year",
        )
    ]


NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}


def _ytd_documented_seizure_count(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*\b(?P<count>one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b"
        r"[^.]*seizures documented this year to date[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []

    event_count = _number_token_to_label(match.group("count"))
    window_months = max(1, clinic_date.month)
    canonical_label = _simple_rate_label(event_count, window_months, "month")
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=canonical_label,
            event_count=event_count,
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation=(
                "year-to-date seizure count anchored to calendar months elapsed "
                "before the clinic date"
            ),
        )
    ]


def _clusters_this_quarter(note_text: str) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*\b(?P<count>one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b"
        r"\s+clusters this quarter[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    cluster_count = _number_token_to_label(match.group("count"))
    evidence = match.group("evidence").strip()
    canonical_label = f"{cluster_count} cluster per 3 month, multiple per cluster"
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=canonical_label,
            event_count=f"{cluster_count} cluster",
            window_count="3",
            window_unit="month",
            evidence_text=evidence,
            derivation="explicit cluster count over a calendar quarter",
        )
    ]


def _weekly_cluster_with_per_cluster_range(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*\bweekly,\s*"
        r"(?P<low>one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+or\s+"
        r"(?P<high>one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+per cluster[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    low = _number_token_to_label(match.group("low"))
    high = _number_token_to_label(match.group("high"))
    per_cluster = low if low == high else f"{low} to {high}"
    evidence = match.group("evidence").strip()
    canonical_label = f"1 cluster per week, {per_cluster} per cluster"
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=canonical_label,
            event_count="1 cluster",
            window_count="1",
            window_unit="week",
            evidence_text=evidence,
            derivation="weekly cluster cadence with explicit per-cluster count range",
        )
    ]


def _weekly_clusters_without_per_cluster_count(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*\bweekly[^.]*clusters reported;\s*"
        r"number per cluster not documented[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label="1 cluster per week, multiple per cluster",
            event_count="1 cluster",
            window_count="1",
            window_unit="week",
            evidence_text=evidence,
            derivation="weekly cluster cadence without a documented per-cluster multiplier",
        )
    ]


def _several_times_each_week(note_text: str) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*several times each week[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label="multiple per week",
            event_count="multiple",
            window_count="1",
            window_unit="week",
            evidence_text=evidence,
            derivation="qualitative several-times-per-week phrasing maps to multiple per week",
        )
    ]


def _clinic_date(note_text: str) -> date | None:
    match = re.search(
        rf"(?:Clinic Date|Date):\s*(?P<day>\d{{1,2}}) "
        rf"(?P<month>{MONTH_PATTERN}) (?P<year>\d{{4}})",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    return date(
        int(match.group("year")),
        _month_number(match.group("month")),
        int(match.group("day")),
    )


def _month_number(month_name: str) -> int:
    return MONTHS[month_name.lower()]


def _count_phrase_to_label(count_phrase: str) -> str:
    normalized = count_phrase.lower().strip()
    if normalized == "two to three":
        return "2 to 3"
    if normalized == "two":
        return "2"
    if normalized == "three":
        return "3"
    raise ValueError(f"Unsupported count phrase: {count_phrase!r}")


def _number_token_to_label(token: str) -> str:
    normalized = token.lower().strip()
    if normalized in NUMBER_WORDS:
        return NUMBER_WORDS[normalized]
    return normalized


def _simple_rate_label(event_count: str, window_count: int, window_unit: str) -> str:
    if window_unit == "month" and window_count == 1:
        return f"{event_count} per month"
    return f"{event_count} per {window_count} {window_unit}"


def _dedupe_candidates(
    candidates: list[GanTemporalFrequencyCandidate],
) -> list[GanTemporalFrequencyCandidate]:
    seen: set[tuple[str, str]] = set()
    deduped: list[GanTemporalFrequencyCandidate] = []
    for candidate in candidates:
        key = (candidate.canonical_label, candidate.evidence_text)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped
