"""Temporal candidate extraction helpers for Gan seizure-frequency analysis.

These helpers are intentionally diagnostic. They expose event/window ingredients
for hard Gan S0 cases without changing benchmark-facing scorer semantics.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from clinical_extraction.schemas import GanRecord


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


def format_temporal_candidates_for_prompt(
    candidates: list[GanTemporalFrequencyCandidate],
) -> str:
    """Format deterministic candidates for verifier/repair model input."""

    if not candidates:
        return (
            "No deterministic temporal frequency candidates were extracted from "
            "this note."
        )

    lines = [
        "Deterministic temporal frequency candidates (diagnostic hints only):"
    ]
    for index, candidate in enumerate(candidates, start=1):
        lines.append(
            f"{index}. canonical_label={candidate.canonical_label!r}; "
            f"event_count={candidate.event_count}; "
            f"window={candidate.window_count} {candidate.window_unit}; "
            f"derivation={candidate.derivation}; "
            f"evidence_text={candidate.evidence_text!r}"
        )
    return "\n".join(lines)


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
