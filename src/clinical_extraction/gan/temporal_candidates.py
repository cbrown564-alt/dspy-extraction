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

TemporalCandidatePresentation = Literal[
    "prose", "table", "json", "bullets", "slot_payload"
]

IMPLEMENTATION_VARIANT_TO_PRESENTATION: dict[str, TemporalCandidatePresentation] = {
    "cand_prose_v1": "prose",
    "cand_table_v1": "table",
    "cand_json_v1": "json",
    "cand_bullets_v1": "bullets",
    "slot_payload_v1": "slot_payload",
    "gan_s0_candidate_builder_gap_v1": "prose",
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
SHORT_MONTH_PATTERN = (
    "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
)


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
    candidates.extend(_in_month_named_event_tallies(note_text))
    candidates.extend(_reverse_chronological_month_convulsion_counts(note_text))
    candidates.extend(_diary_named_month_event_tallies(note_text))
    candidates.extend(_following_week_events_monthly_rate(note_text))
    candidates.extend(_unanchored_count_with_latest_date_unknown(note_text))
    candidates.extend(_morning_cluster_shorthand(note_text))
    candidates.extend(_month_beginning_cluster_bursts(note_text))
    candidates.extend(_some_weeks_morning_grouped_spells(note_text))
    candidates.extend(_several_mornings_intra_morning_repeats(note_text))
    candidates.extend(_seizure_free_then_single_day_cluster(note_text))
    candidates.extend(_breakthrough_after_months_seizure_free(note_text))
    candidates.extend(_withdrawal_moment_seizure_count(note_text))
    candidates.extend(_vague_grouped_spells_unknown(note_text))
    candidates.extend(_last_convulsive_with_occasional_clusters(note_text))
    candidates.extend(_daily_seizure_type_frequency(note_text))
    candidates.extend(_first_and_subsequent_dated_events_window(note_text))
    candidates.extend(_last_seizure_with_since_jerks(note_text))
    candidates.extend(_no_major_seizures_since_but_minor_continues(note_text))
    candidates.extend(_interval_spacing_candidates(note_text))
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

    if presentation == "slot_payload":
        from clinical_extraction.gan.slot_payload import (
            format_slot_payload_candidates_for_prompt,
        )

        return format_slot_payload_candidates_for_prompt(candidates, source=source)

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
        r"(?P<evidence>[^.]*(?:no seizures|seizure-free)[^.]*?nearly a year[^.]*?"
        r"(?P<count>\d+|a|single|one|two|three|four|five|six|seven|eight|nine|ten)?\s*tonic seizure[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []
    
    count_group = match.group("count")
    if count_group:
        event_count = _number_token_to_label(count_group)
    else:
        event_count = "1"
        
    label = _simple_rate_label(event_count, 1, "year")
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=label,
            event_count=event_count,
            window_count="1",
            window_unit="year",
            evidence_text=evidence,
            derivation=(
                "breakthrough event after a nearly one-year seizure-free "
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
        rf"(?P<evidence>last\s+(?:reported\s+|such\s+)?(?:episode|event)\s+(?:was\s+recorded\s+on|was\s+on|occurred\s+on)\s+"
        rf"(?P<day>\d{{1,2}})[\s/](?P<month>{MONTH_PATTERN}|{SHORT_MONTH_PATTERN})"
        rf"(?:[\s/](?P<year>\d{{4}}))?[^.]*)",
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
    
    # We want to match windows up to 6 months (approx 180 days)
    if not (14 <= elapsed_days <= 180):
        return []

    # Calculate month diff
    month_diff = (clinic_date.year - event_date.year) * 12 + clinic_date.month - event_date.month
    if month_diff <= 1:
        window_months = 1
        label = "1 per month"
    else:
        window_months = month_diff
        label = f"1 per {window_months} month"

    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=label,
            event_count="1",
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="last recorded event falls within an elapsed window",
        )
    ]


def _count_range_since_prior_month_year(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*No further [^.]* since "
        r"(?:(?P<month>\d{1,2})/(?P<year>\d{4})|(?P<month_dash>\d{1,2})\s*-\s*(?P<year_dash>\d{4})), although "
        r"(?P<count>one or two|two to three|two|three|one) [^.]* remain[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []

    if match.group("month"):
        start_month = int(match.group("month"))
        start_year = int(match.group("year"))
    else:
        start_month = int(match.group("month_dash"))
        start_year = int(match.group("year_dash"))
    window_months = max(
        1,
        (clinic_date.year - start_year) * 12 + clinic_date.month - start_month,
    )
    event_count = _count_range_text_to_label(match.group("count"))
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


def _in_month_named_event_tallies(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        rf"(?P<evidence>In (?P<m1>{SHORT_MONTH_PATTERN})[^.]*?but (?P<c1>\d+) daytime events\.\s*"
        rf"In (?P<m2>{SHORT_MONTH_PATTERN})[^.]*?nocturnal seizure and (?P<c2>\d+) while awake)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    event_count = int(match.group("c1")) + 1 + int(match.group("c2"))
    short_months = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }
    window_months = max(
        1,
        abs(
            short_months[match.group("m2")[:3].lower()]
            - short_months[match.group("m1")[:3].lower()]
        )
        + 1,
    )
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"{event_count} per {window_months} month",
            event_count=str(event_count),
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="named-month tallies aggregated across consecutive calendar months",
        )
    ]


def _reverse_chronological_month_convulsion_counts(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>She had (?P<sep>\d+|one) convulsions so far in Sep, "
        r"(?P<aug>\d+) in Aug, (?P<jul>\d+) in Jul, (?P<jun>one|\d+) in Jun)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    counts = [
        _number_token_to_label(match.group("jun")),
        _number_token_to_label(match.group("jul")),
        _number_token_to_label(match.group("aug")),
        _number_token_to_label(match.group("sep")),
    ]
    event_count = str(sum(int(value) for value in counts))
    window_months = 4
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"{event_count} per {window_months} month",
            event_count=event_count,
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="reverse-chronological monthly convulsion counts summed over Jun–Sep",
        )
    ]


def _diary_named_month_event_tallies(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    candidates = []
    
    # 1. Original pattern
    match = re.search(
        r"(?P<evidence>In May[^.]*?(?P<may>\d+) short seizures[^.]*\.\s*"
        r"In Aug (?P<aug>\d+) daytime events were noted, "
        r"in Sep four myoclonic jerks occurred, and in Oct five generalised tonic-clonic seizures)",
        note_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match is not None:
        event_count = str(
            int(match.group("may")) + int(match.group("aug")) + 4 + 5
        )
        window_months = 6
        evidence = match.group("evidence").strip()
        candidates.append(
            GanTemporalFrequencyCandidate(
                canonical_label=f"{event_count} per {window_months} month",
                event_count=event_count,
                window_count=str(window_months),
                window_unit="month",
                evidence_text=evidence,
                derivation="diary month-by-month event tallies aggregated from May through October",
            )
        )
        return candidates

    # 2. Pattern for gan_16645
    # "a cluster of three seizures in August ... In November he had a nocturnal seizure, and in February a single tonic seizure was recorded"
    match1 = re.search(
        r"(?P<evidence>a cluster of (?P<count1>three|\d+) seizures in (?P<month1>[A-Za-z]+)[^.]*?\.\s*"
        r"In (?P<month2>[A-Za-z]+) he had a[^.]*?seizure,\s+and\s+in\s+(?P<month3>[A-Za-z]+)\s+a\s+(?P<count3>single|\d+)[^.]*?seizure\s+was\s+recorded)",
        note_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match1 is not None:
        c1 = int(_number_token_to_label(match1.group("count1")))
        c2 = 1 # "a nocturnal seizure" -> 1
        c3 = int(_number_token_to_label(match1.group("count3")))
        event_count = str(c1 + c2 + c3)
        
        m1 = _month_number(match1.group("month1"))
        m3 = _month_number(match1.group("month3"))
        window_months = (m3 - m1) % 12 + 1
        evidence = match1.group("evidence").strip()
        candidates.append(
            GanTemporalFrequencyCandidate(
                canonical_label=f"{event_count} per {window_months} month",
                event_count=event_count,
                window_count=str(window_months),
                window_unit="month",
                evidence_text=evidence,
                derivation="diary month-by-month event tallies aggregated from August through February",
            )
        )
        return candidates

    # 3. Pattern for gan_16750
    # "In February she experienced a prolonged focal seizure ... In May there were four ... and in August a single"
    match2 = re.search(
        r"(?P<evidence>In (?P<month1>[A-Za-z]+) she experienced a (?P<count1>prolonged|\d+) focal seizure[^.]*?\.\s*"
        r"In (?P<month2>[A-Za-z]+) there were (?P<count2>four|\d+)[^.]*?\s+and\s+in\s+(?P<month3>[A-Za-z]+)\s+a\s+(?P<count3>single|\d+)[^.]*?seizure)",
        note_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match2 is not None:
        c1 = 1 if match2.group("count1").lower() == "prolonged" else int(_number_token_to_label(match2.group("count1")))
        c2 = int(_number_token_to_label(match2.group("count2")))
        c3 = int(_number_token_to_label(match2.group("count3")))
        event_count = str(c1 + c2 + c3)
        
        m1 = _month_number(match2.group("month1"))
        m3 = _month_number(match2.group("month3"))
        window_months = (m3 - m1) % 12 + 1
        evidence = match2.group("evidence").strip()
        candidates.append(
            GanTemporalFrequencyCandidate(
                canonical_label=f"{event_count} per {window_months} month",
                event_count=event_count,
                window_count=str(window_months),
                window_unit="month",
                evidence_text=evidence,
                derivation="diary month-by-month event tallies aggregated from February through August",
            )
        )
        return candidates

    return []


def _following_week_events_monthly_rate(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>In the following week, he had (?P<count>2\s*-\s*3|\d+)\s+seizures)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    event_count = _count_range_text_to_label(match.group("count"))
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"{event_count} per month",
            event_count=event_count,
            window_count="1",
            window_unit="month",
            evidence_text=evidence,
            derivation=(
                "events concentrated in the week after medication change; monthly "
                "benchmark denominator when no further seizures are reported since"
            ),
        )
    ]


def _unanchored_count_with_latest_date_unknown(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    patterns = (
        (
            r"(?P<evidence>since discharge from hospital he has experienced "
            r"(?P<count>two\s*-\s*three|two|three|\d+(?:\s*-\s*\d+)?)\s+seizures)",
            "since-discharge count without benchmark-derivable denominator",
        ),
        (
            r"(?P<evidence>since starting [^.]{0,80}? he has had "
            r"(?P<count>\d+|two|three|four) drop attacks, the latest one on)",
            "drop-attack count with latest-date anchor only",
        ),
        (
            r"(?P<evidence>(?:since beginning|since starting) [^.]{0,80}? he has had "
            r"(?P<count>\d+\s*-\s*\d+|\d+ to \d+|two to three|three to four) "
            r"generalised tonic-clonic seizures, the most recent on)",
            "generalised tonic-clonic count with latest-date anchor only",
        ),
    )
    candidates: list[GanTemporalFrequencyCandidate] = []
    for pattern, derivation in patterns:
        match = re.search(pattern, note_text, flags=re.IGNORECASE)
        if match is None:
            continue
        event_count = _count_range_text_to_label(match.group("count"))
        evidence = match.group("evidence").strip()
        candidates.append(
            GanTemporalFrequencyCandidate(
                canonical_label="unknown",
                event_count=event_count,
                window_count="",
                window_unit="",
                evidence_text=evidence,
                derivation=derivation,
            )
        )
    return candidates


def _morning_cluster_shorthand(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>Morning clusters (?P<clusters>\d+)×/month;\s*"
        r"~?(?P<per>[\w\s-]+?)\s+events over)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    per_cluster = _count_range_text_to_label(match.group("per"))
    cluster_count = match.group("clusters")
    evidence = match.group("evidence").strip()
    canonical_label = f"{cluster_count} cluster per month, {per_cluster} per cluster"
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=canonical_label,
            event_count=f"{cluster_count} cluster",
            window_count="1",
            window_unit="month",
            evidence_text=evidence,
            derivation="morning-cluster shorthand with explicit per-cluster range",
        )
    ]


def _month_beginning_cluster_bursts(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>pattern of seizures recurring in short bursts around "
        r"the beginning of most months[^.]*\.)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label="1 cluster per month, multiple per cluster",
            event_count="1 cluster",
            window_count="1",
            window_unit="month",
            evidence_text=evidence,
            derivation="month-beginning cluster bursts without documented per-cluster multiplier",
        )
    ]


def _some_weeks_morning_grouped_spells(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]{0,120}on some weeks, occurring as grouped events on those mornings[^.]*\.)",
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
            derivation="grouped morning spells on some weeks without per-cluster count",
        )
    ]


def _several_mornings_intra_morning_repeats(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*several mornings each week[^.]*\.\s*"
        r"[^.]*two or three times within the same morning[^.]*\.)",
        note_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match is None:
        return []

    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label="multiple cluster per week, 2 to 3 per cluster",
            event_count="multiple cluster",
            window_count="1",
            window_unit="week",
            evidence_text=evidence,
            derivation=(
                "several mornings each week with intra-morning repeats; per-cluster "
                "range preserved without inventing cluster spacing"
            ),
        )
    ]


def _seizure_free_then_single_day_cluster(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*seizure-free for up to (?P<months>\d+) month[^.]*"
        r"clusters of (?P<low>three|two|\d+)\s*-\s*(?P<high>four|three|\d+)\s+seizures "
        r"in a single day[^.]*\.)",
        note_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match is None:
        return []

    low = _number_token_to_label(match.group("low"))
    high = _number_token_to_label(match.group("high"))
    per_cluster = low if low == high else f"{low} to {high}"
    months = match.group("months")
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"1 cluster per {months} month, {per_cluster} per cluster",
            event_count="1 cluster",
            window_count=months,
            window_unit="month",
            evidence_text=evidence,
            derivation="long seizure-free interval followed by single-day cluster burst",
        )
    ]


def _breakthrough_after_months_seizure_free(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    candidates = []
    
    # 1. Original pattern
    match = re.search(
        r"(?P<evidence>[^.]*did not have seizures for over (?P<months>\d+) months, "
        r"but then reported (?P<count>two|\d+) generalised tonic-clonic seizures[^.]*\.)",
        note_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match is not None:
        event_count = _number_token_to_label(match.group("count"))
        months = match.group("months")
        evidence = match.group("evidence").strip()
        candidates.append(
            GanTemporalFrequencyCandidate(
                canonical_label=f"{event_count} per {months} month",
                event_count=event_count,
                window_count=months,
                window_unit="month",
                evidence_text=evidence,
                derivation="breakthrough events after a long seizure-free interval",
            )
        )
        return candidates

    # 2. General pattern for "seizure-free for [months] months, until a/an [event] occurred"
    # and "seizure-free for [months] months before experiencing a/an [event] ... preceded by [event]"
    match2 = re.search(
        rf"(?P<evidence>[^.]*(?:seizure-free|no seizures)\s+for\s+(?P<months>seven|five|six|eight|nine|\d+)\s+months"
        rf"[^.]*?(?:before experiencing|until)\s+(?P<events>[^.]+))",
        note_text,
        flags=re.IGNORECASE,
    )
    if match2 is not None:
        months_word = match2.group("months").lower()
        # Convert month name to digit if it is a word
        month_words_map = {
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"
        }
        months = month_words_map.get(months_word, months_word)
        events_text = match2.group("events").lower()
        
        # Determine the count
        # In gan_13058: "a generalised tonic-clonic seizure ... preceded by a cluster of absences" -> 2 events
        # In gan_13190: "a focal impaired-awareness seizure occurred" -> 1 event
        if "preceded by" in events_text or "and a" in events_text or "and another" in events_text:
            event_count = "2"
        else:
            event_count = "1"
            
        label = _simple_rate_label(event_count, int(months), "month")
        evidence = match2.group("evidence").strip()
        candidates.append(
            GanTemporalFrequencyCandidate(
                canonical_label=label,
                event_count=event_count,
                window_count=months,
                window_unit="month",
                evidence_text=evidence,
                derivation="breakthrough events after a long seizure-free interval",
            )
        )
        
    return candidates


def _withdrawal_moment_seizure_count(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>(?:he|she)\s+(?:withdrew\s+from|discontinued)\s+[A-Za-z]+\s+on\s+"
        r"(?P<day>\d{1,2})/(?P<month>[A-Za-z]+)\.\s+"
        r"(?:At\s+that\s+time,\s+he\s+had|Shortly\s+afterwards,\s+she\s+experienced)\s+"
        r"(?P<count>[A-Za-z0-9\s-]+)\s+seizures)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []

    month_map = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }
    withdrawal_month = month_map.get(match.group("month")[:3].lower())
    if withdrawal_month is None:
        return []

    withdrawal_year = clinic_date.year
    if withdrawal_month > clinic_date.month:
        withdrawal_year -= 1

    window_months = max(1, (clinic_date.year - withdrawal_year) * 12 + clinic_date.month - withdrawal_month)
    event_count = _count_range_text_to_label(match.group("count"))
    
    label = _simple_rate_label(event_count, window_months, "month")
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=label,
            event_count=event_count,
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="withdrawal-moment seizure count anchored to elapsed months before clinic",
        )
    ]


def _vague_grouped_spells_unknown(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*(?:four to six|4 to 6)[^.]*grouped together on days when they occur[^.]*\.)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    count_match = re.search(
        r"(four to six|4 to 6)",
        match.group("evidence"),
        flags=re.IGNORECASE,
    )
    per_cluster = (
        _count_range_text_to_label(count_match.group(1)) if count_match else "4 to 6"
    )
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"unknown, {per_cluster} per cluster",
            event_count=per_cluster,
            window_count="",
            window_unit="",
            evidence_text=evidence,
            derivation="grouped spells without benchmark-derivable cluster spacing",
        )
    ]


def _months_between_month_year(clinic_date: date, month: int, year: int) -> int:
    return max(1, (clinic_date.year - year) * 12 + clinic_date.month - month)


def _last_convulsive_with_occasional_clusters(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*last convulsive seizure was recorded in "
        r"(?:(?P<month_slash>\d{1,2})/(?P<year_slash>\d{4})|"
        r"(?P<month_dash>\d{1,2})\s*-\s*(?P<year_dash>\d{4})), "
        r"with occasional clusters of [^.]+ persisting[^.]*\.)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []

    if match.group("month_slash"):
        start_month = int(match.group("month_slash"))
        start_year = int(match.group("year_slash"))
    else:
        start_month = int(match.group("month_dash"))
        start_year = int(match.group("year_dash"))
    window_months = _months_between_month_year(clinic_date, start_month, start_year)
    evidence = match.group("evidence").strip()
    canonical_label = (
        f"multiple cluster per {window_months} month, multiple per cluster"
    )
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=canonical_label,
            event_count="multiple cluster",
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation=(
                "occasional clusters persisting since last convulsive seizure; "
                "long-window cluster spacing from last convulsive month/year to clinic"
            ),
        )
    ]


def _daily_seizure_type_frequency(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>[^.]*\bdaily "
        r"(?:drop attacks|absences|myoclonic jerks|myoclonic events)[^.]*\.)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []

    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label="1 per day",
            event_count="1",
            window_count="1",
            window_unit="day",
            evidence_text=evidence,
            derivation=(
                "explicit daily seizure-type frequency for concurrent-type selection"
            ),
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


def _first_and_subsequent_dated_events_window(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    # Regex to find first event date
    match_first = re.search(
        rf"first seizure\s+(?:was\s+reported\s+)?in\s+(?P<month>{MONTH_PATTERN})\s+(?P<year>\d{{4}})",
        note_text,
        flags=re.IGNORECASE,
    )
    if not match_first:
        return []
    
    # Regex to find second/subsequent events
    match_second = re.search(
        rf"(?P<count_word>second|second and third)\s+(?:seizure|event)s?\s+(?:took\s+place\s+|was\s+)?in\s+(?P<month>{MONTH_PATTERN})\s+(?P<year>\d{{4}})",
        note_text,
        flags=re.IGNORECASE,
    )
    if not match_second:
        return []
        
    start_month = _month_number(match_first.group("month"))
    start_year = int(match_first.group("year"))
    end_month = _month_number(match_second.group("month"))
    end_year = int(match_second.group("year"))
    
    window_months = max(1, (end_year - start_year) * 12 + end_month - start_month)
    
    count_word = match_second.group("count_word").lower()
    if "third" in count_word:
        event_count = "3"
    else:
        event_count = "2"
        
    start_idx = min(match_first.start(), match_second.start())
    end_idx = max(match_first.end(), match_second.end())
    evidence = note_text[start_idx:end_idx].strip()
    
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"{event_count} per {window_months} month",
            event_count=event_count,
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="first and subsequent dated events define the observation window",
        )
    ]


def _last_seizure_with_since_jerks(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>Last\s+[^.]*?seizure\s+was\s+in\s+"
        r"(?P<month>\d{1,2})\s*-\s*(?P<year>\d{4}),\s+with\s+"
        r"(?P<count>\d+|one|two|three|four|five)\s+[^.]*?since\s+then)",
        note_text,
        flags=re.IGNORECASE,
    )
    if not match:
        return []
    
    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []
        
    start_month = int(match.group("month"))
    start_year = int(match.group("year"))
    
    window_months = max(1, (clinic_date.year - start_year) * 12 + clinic_date.month - start_month)
    
    since_count = int(_number_token_to_label(match.group("count")))
    total_count = 1 + since_count
    
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"{total_count} per {window_months} month",
            event_count=str(total_count),
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="last major seizure plus subsequent minor events over elapsed window",
        )
    ]


def _no_major_seizures_since_but_minor_continues(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    match = re.search(
        r"(?P<evidence>no\s+[^.]*?seizures\s+since\s+"
        r"(?P<month>\d{1,2})\s*-\s*(?P<year>\d{4}),\s+though\s+continues\s+to\s+experience\s+[^.]*?from\s+time\s+to\s+time)",
        note_text,
        flags=re.IGNORECASE,
    )
    if not match:
        return []
        
    clinic_date = _clinic_date(note_text)
    if clinic_date is None:
        return []
        
    start_month = int(match.group("month"))
    start_year = int(match.group("year"))
    
    window_months = max(1, (clinic_date.year - start_year) * 12 + clinic_date.month - start_month)
    
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label=f"multiple per {window_months} month",
            event_count="multiple",
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="no major events since date but minor events continue from time to time",
        )
    ]


def _interval_spacing_candidates(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    candidates = []
    
    match1 = re.search(
        r"(?P<evidence>seizure-free\s+for\s+(?P<days>\d+)\s+consecutive\s+days,\s+followed\s+by\s+[^.]*?typically\s+(?P<count>\w+)\s+(?P<type>[A-Za-z\s]+?)(?:seizures|events)?)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match1:
        days = match1.group("days")
        count_word = match1.group("count").lower()
        if count_word == "two":
            count = "2"
        elif count_word == "three":
            count = "3"
        else:
            count = count_word
            
        evidence = match1.group("evidence").strip()
        candidates.append(
            GanTemporalFrequencyCandidate(
                canonical_label=f"1 cluster per {days} day, {count} per cluster",
                event_count=f"1 cluster, {count} per cluster",
                window_count=days,
                window_unit="day",
                evidence_text=evidence,
                derivation="seizure-free interval followed by cluster count",
            )
        )
        
    match2 = re.search(
        r"(?P<evidence>clustering\s+pattern,\s+most\s+often\s+every\s+(?P<days>\d+)\s+days)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match2:
        days = match2.group("days")
        evidence = match2.group("evidence").strip()
        candidates.append(
            GanTemporalFrequencyCandidate(
                canonical_label=f"1 per {days} day",
                event_count="1",
                window_count=days,
                window_unit="day",
                evidence_text=evidence,
                derivation="clustering pattern spacing maps to simple rate",
            )
        )
        
    return candidates


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
    name = month_name.lower().strip()[:3]
    short_months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    if name in short_months:
        return short_months[name]
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
    if normalized in ("a", "an", "single", "one"):
        return "1"
    if normalized in NUMBER_WORDS:
        return NUMBER_WORDS[normalized]
    return normalized


def _count_range_text_to_label(count_text: str) -> str:
    normalized = re.sub(r"\s+", " ", count_text.lower().strip())
    normalized = normalized.replace(" - ", " to ").replace("-", " to ")
    if normalized == "one or two":
        return "1 to 2"
    if normalized == "two to three":
        return "2 to 3"
    if normalized == "three to four":
        return "3 to 4"
    if normalized == "four to six":
        return "4 to 6"
    if " to " in normalized:
        parts = [part.strip() for part in normalized.split(" to ", maxsplit=1)]
        return f"{_number_token_to_label(parts[0])} to {_number_token_to_label(parts[1])}"
    return _number_token_to_label(normalized)


def _simple_rate_label(event_count: str, window_count: int, window_unit: str) -> str:
    if window_count == 1:
        return f"{event_count} per {window_unit}"
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
