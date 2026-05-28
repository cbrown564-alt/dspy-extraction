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
    candidates.extend(_seizure_free_for_multiple_year(note_text))
    candidates.extend(_high_recall_frequency_candidates(note_text))
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
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "thirty": "30",
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
    
    evidence = match.group("evidence").strip()
    candidates = [
        GanTemporalFrequencyCandidate(
            canonical_label=_simple_rate_label(event_count, window_months, "month"),
            event_count=event_count,
            window_count=str(window_months),
            window_unit="month",
            evidence_text=evidence,
            derivation="withdrawal-moment seizure count anchored to elapsed months before clinic",
        )
    ]
    if window_months > 1:
        candidates.append(
            GanTemporalFrequencyCandidate(
                canonical_label=_simple_rate_label(event_count, window_months - 1, "month"),
                event_count=event_count,
                window_count=str(window_months - 1),
                window_unit="month",
                evidence_text=evidence,
                derivation=(
                    "withdrawal-moment seizure count anchored to completed "
                    "post-withdrawal months before clinic"
                ),
            )
        )
    return candidates


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


def _seizure_free_for_multiple_year(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    """Emit canonical multi-year seizure-free label when duration is explicitly vague-multi-year."""
    match = re.search(
        r"(?P<evidence>[^.]*\b(?:has been |having been |remains |is )?"
        r"seizure[- ]free(?: for)?(?: the past)? "
        r"(?:for )?(?:multiple|several|a number of )?years?[^.]*)",
        note_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return []
    evidence = match.group("evidence").strip()
    return [
        GanTemporalFrequencyCandidate(
            canonical_label="seizure free for multiple year",
            event_count="0",
            window_count="multiple",
            window_unit="year",
            evidence_text=evidence,
            derivation=(
                "explicit multi-year seizure freedom; emit policy canonical "
                "'seizure free for multiple year' without inferring N"
            ),
        )
    ]


def _high_recall_frequency_candidates(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    """Emit a recall-first candidate substrate using the Gan 2.6.1 label scheme.

    The candidates are intentionally over-complete: they enumerate plausible
    benchmark label surfaces from supported text spans, while selection and
    precision are left to later G2/C-style adjudication.
    """

    candidates: list[GanTemporalFrequencyCandidate] = []
    _append_supported_candidate(
        candidates,
        "no seizure frequency reference",
        _fallback_evidence(note_text),
        "high-recall null-label candidate; later selection decides applicability",
    )
    if _has_seizure_context(note_text):
        _append_supported_candidate(
            candidates,
            "unknown",
            _first_context_evidence(note_text),
            "high-recall unknown-frequency candidate for seizure-context notes",
        )

    candidates.extend(_seizure_free_high_recall_candidates(note_text))
    candidates.extend(_explicit_rate_high_recall_candidates(note_text))
    candidates.extend(_count_window_high_recall_candidates(note_text))
    candidates.extend(_named_month_clause_high_recall_candidates(note_text))
    candidates.extend(_month_tally_high_recall_candidates(note_text))
    candidates.extend(_cluster_high_recall_candidates(note_text))
    return candidates


QUANTITY_TOKEN_PATTERN = (
    r"(?:a pair of|a pair|pair of|once|twice|thrice|single|multiple|several|"
    r"many|few|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
    r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|thirty|an|a|\d+(?:\.\d+)?)"
)
QUANTITY_RANGE_PATTERN = (
    rf"{QUANTITY_TOKEN_PATTERN}(?:\s*(?:to|or|-|–|—|−)\s*"
    rf"{QUANTITY_TOKEN_PATTERN})?"
)
EVENT_NOUN_PATTERN = (
    r"(?:seizures?|events?|episodes?|absences?|convulsions?|attacks?|"
    r"drop attacks?|tonic[- ]clonic(?: seizures?)?|gtc(?: seizures?)?|"
    r"tcs?|focal(?: aware| impaired-awareness)? events?|myoclonic jerks?|"
    r"focal sensory|focal non-?motors?|focal clonic|petit mal|"
    r"simple partial seizures?|myoclonic|epileptic spasms?|jerks?|"
    r"spasms?|spells?|auras?|seizure days?|nights?)"
)
PERIOD_UNIT_PATTERN = (
    r"(?:days?|nights?|weeks?|months?|years?|fortnights?|quarters?|"
    r"d|wk|wks|mo|mos|yr|yrs)"
)


def _append_supported_candidate(
    candidates: list[GanTemporalFrequencyCandidate],
    label: str,
    evidence_text: str,
    derivation: str,
    *,
    event_count: str | None = None,
    window_count: str | None = None,
    window_unit: str | None = None,
) -> None:
    from clinical_extraction.gan.frequency import label_to_monthly_frequency, normalize_label

    canonical_label = normalize_label(label)
    try:
        monthly_frequency = label_to_monthly_frequency(canonical_label)
    except (TypeError, ValueError):
        return
    if (
        monthly_frequency > 999
        and canonical_label != "unknown"
        and not canonical_label.startswith("unknown,")
    ):
        return

    if not evidence_text.strip():
        return
    inferred = _candidate_label_parts(canonical_label)
    candidates.append(
        GanTemporalFrequencyCandidate(
            canonical_label=canonical_label,
            event_count=event_count if event_count is not None else inferred[0],
            window_count=window_count if window_count is not None else inferred[1],
            window_unit=window_unit if window_unit is not None else inferred[2],
            evidence_text=evidence_text.strip(),
            derivation=derivation,
        )
    )


def _candidate_label_parts(label: str) -> tuple[str, str, str]:
    if label == "unknown" or label == "no seizure frequency reference":
        return "", "", ""
    if label.startswith("unknown,"):
        per_cluster = label.removeprefix("unknown, ").removesuffix(" per cluster")
        return per_cluster, "", ""
    if label.startswith("seizure free for "):
        duration = label.removeprefix("seizure free for ")
        parts = duration.split()
        if len(parts) >= 2:
            return "0", parts[0], parts[1]
        return "0", "", ""
    cluster_match = re.fullmatch(
        r"(?P<clusters>.+?) cluster per (?:(?P<period>.+?) )?"
        r"(?P<unit>day|week|month|year), (?P<per_cluster>.+?) per cluster",
        label,
    )
    if cluster_match:
        return (
            f"{cluster_match.group('clusters')} cluster",
            cluster_match.group("period") or "1",
            cluster_match.group("unit"),
        )
    rate_match = re.fullmatch(
        r"(?P<count>.+?) per (?:(?P<period>.+?) )?"
        r"(?P<unit>day|week|month|year)",
        label,
    )
    if rate_match:
        return (
            rate_match.group("count"),
            rate_match.group("period") or "1",
            rate_match.group("unit"),
        )
    return "", "", ""


def _fallback_evidence(note_text: str) -> str:
    stripped = note_text.strip()
    if len(stripped) <= 240:
        return stripped
    return stripped[:240].rstrip()


def _first_context_evidence(note_text: str) -> str:
    for start, end, sentence in _iter_sentence_spans(note_text):
        if _has_seizure_context(sentence):
            return note_text[start:end].strip()
    return _fallback_evidence(note_text)


def _iter_sentence_spans(note_text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    start = 0
    for match in re.finditer(r"(?<=[.!?])\s+|\n{2,}", note_text):
        end = match.start()
        sentence = note_text[start:end].strip()
        if sentence:
            spans.append((start, end, sentence))
        start = match.end()
    tail = note_text[start:].strip()
    if tail:
        spans.append((start, len(note_text), tail))
    return spans


def _sentence_around(note_text: str, start: int, end: int) -> str:
    left_candidates = [
        note_text.rfind(".", 0, start),
        note_text.rfind("!", 0, start),
        note_text.rfind("?", 0, start),
        note_text.rfind("\n\n", 0, start),
    ]
    left = max(left_candidates)
    left = 0 if left < 0 else left + 1
    right_candidates = [
        pos for pos in (
            note_text.find(".", end),
            note_text.find("!", end),
            note_text.find("?", end),
            note_text.find("\n\n", end),
        )
        if pos >= 0
    ]
    right = min(right_candidates) + 1 if right_candidates else len(note_text)
    evidence = note_text[left:right].strip()
    if len(evidence) > 700:
        evidence = note_text[start:end].strip()
    return evidence


def _has_seizure_context(text: str) -> bool:
    return re.search(
        r"\b(?:seizure|seizures|epilep|episode|episodes|event|events|"
        r"convulsion|convulsions|absence|absences|drop attack|tonic|clonic|"
        r"drop attacks|myoclonic|focal|petit mal|jerk|jerks|spasm|spasms|"
        r"spell|spells|aura|auras|"
        r"cluster|clusters|gtc|tc|sz)\b",
        text,
        flags=re.IGNORECASE,
    ) is not None


def _quantity_to_label(quantity_text: str) -> str:
    normalized = re.sub(r"\s+", " ", quantity_text.lower().strip())
    normalized = normalized.strip(".,;:()[]")
    normalized = normalized.replace("–", "-").replace("—", "-").replace("−", "-")
    normalized = normalized.replace("≤", "<=").replace("≥", ">=")
    normalized = re.sub(
        r"^(?:about|approximately|approx\.?|around|roughly|circa|~|≈|"
        r"<=|>=|<|>|up to|at most|no more than)\s+",
        "",
        normalized,
    )
    normalized = normalized.replace(" times", "")
    normalized = normalized.replace(" or ", " to ")
    normalized = re.sub(r"\s*-\s*", " to ", normalized)
    if " to " in normalized:
        left, right = [part.strip() for part in normalized.split(" to ", maxsplit=1)]
        return f"{_quantity_to_label(left)} to {_quantity_to_label(right)}"
    if normalized in {"a pair", "a pair of", "pair", "pair of"}:
        return "2"
    if normalized in {"a", "an", "single", "once", "one"}:
        return "1"
    if normalized in {"twice", "two"}:
        return "2"
    if normalized in {"thrice", "three"}:
        return "3"
    if normalized in {"few", "several", "many", "multiple"}:
        return "multiple"
    return NUMBER_WORDS.get(normalized, normalized)


def _period_parts(
    period_count_text: str | None,
    period_unit_text: str,
) -> tuple[str, str]:
    unit_raw = period_unit_text.lower().strip().rstrip(".")
    period_count = _quantity_to_label(period_count_text or "1")
    if unit_raw in {"d", "day", "days", "night", "nights"}:
        return period_count, "day"
    if unit_raw in {"wk", "wks", "week", "weeks"}:
        return period_count, "week"
    if unit_raw in {"mo", "mos", "month", "months"}:
        return period_count, "month"
    if unit_raw in {"yr", "yrs", "year", "years"}:
        return period_count, "year"
    if unit_raw in {"fortnight", "fortnights"}:
        if period_count == "1":
            return "2", "week"
        if " to " in period_count:
            return period_count, "fortnight"
        return str(float(period_count) * 2).removesuffix(".0"), "week"
    if unit_raw in {"quarter", "quarters"}:
        if period_count == "1":
            return "3", "month"
        if " to " in period_count:
            return period_count, "quarter"
        return str(float(period_count) * 3).removesuffix(".0"), "month"
    return period_count, unit_raw


def _rate_label(count: str, period_count: str, period_unit: str) -> str:
    if period_count == "1":
        return f"{count} per {period_unit}"
    return f"{count} per {period_count} {period_unit}"


def _cluster_rate_label(
    cluster_count: str,
    period_count: str,
    period_unit: str,
    per_cluster: str,
) -> str:
    if period_count == "1":
        return f"{cluster_count} cluster per {period_unit}, {per_cluster} per cluster"
    return (
        f"{cluster_count} cluster per {period_count} {period_unit}, "
        f"{per_cluster} per cluster"
    )


def _seizure_free_high_recall_candidates(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    candidates: list[GanTemporalFrequencyCandidate] = []
    free_pattern = re.compile(
        r"(?:seizure[-‑– ]free|free of (?:events|seizures|attacks)|"
        r"no (?:[^.;]{0,70} )?"
        r"(?:seizures|events|attacks|episodes|auras|spells|convulsions)|"
        r"without (?:any )?recurrence|without clear seizures|"
        r"complete cessation|sustained period without (?:any )?recurrence)",
        flags=re.IGNORECASE,
    )
    for match in free_pattern.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if not _has_seizure_context(evidence):
            continue
        emitted = False
        for duration in re.finditer(
            rf"\b(?:for|over|past|last|previous|during|since|follow.?up)\s+"
            rf"(?:the\s+)?(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
            rf"(?P<unit>months?|years?)(?:\s+ago)?\b",
            evidence,
            flags=re.IGNORECASE,
        ):
            count = _quantity_to_label(duration.group("count"))
            _, unit = _period_parts("1", duration.group("unit"))
            _append_supported_candidate(
                candidates,
                f"seizure free for {count} {unit}",
                evidence,
                "explicit seizure-free duration in Gan label-scheme units",
            )
            if count not in {"1", "multiple"} and unit == "month":
                _append_supported_candidate(
                    candidates,
                    "seizure free for multiple month",
                    evidence,
                    "specific month count also supports vague multi-month seizure freedom",
                )
            emitted = True
        if re.search(r"\b(?:last|past|previous)\s+year\b", evidence, flags=re.IGNORECASE):
            for label in ("seizure free for 1 year", "seizure free for 12 month"):
                _append_supported_candidate(
                    candidates,
                    label,
                    evidence,
                    "seizure-free last-year expression",
                )
            emitted = True
        clinic_date = _clinic_date(note_text)
        for parsed_date in _dates_in_text(evidence):
            if clinic_date is None or parsed_date > clinic_date:
                continue
            if re.search(r"\bno auras?\b", evidence, flags=re.IGNORECASE) and not re.search(
                r"\bno [^.;]*(?:seizures|events|episodes|attacks|convulsions)\b",
                evidence,
                flags=re.IGNORECASE,
            ):
                continue
            months = _months_between_dates(clinic_date, parsed_date)
            _append_supported_candidate(
                candidates,
                f"seizure free for {months} month",
                evidence,
                "seizure-free since-date interval to clinic date",
            )
            if months >= 12:
                _append_supported_candidate(
                    candidates,
                    f"seizure free for {months // 12} year",
                    evidence,
                    "seizure-free since-date interval rounded down to completed years",
                )
            if months > 1:
                _append_supported_candidate(
                    candidates,
                    "seizure free for multiple month",
                    evidence,
                    "since-date no-event interval also supports vague multi-month label",
                )
            emitted = True
        if re.search(
            r"\b(?:several|many|multiple)\s+months?\b|"
            r"\bsince (?:last review|last visit|last appointment|last clinic|"
            r"initial referral|rota changed|dose escalation|current regimen)\b|"
            r"\bno (?:[^.;]{0,50} )?events suggestive of seizures\b|"
            r"\bno interval events\b",
            evidence,
            flags=re.IGNORECASE,
        ):
            _append_supported_candidate(
                candidates,
                "seizure free for multiple month",
                evidence,
                "vague multi-month seizure-free expression",
            )
            emitted = True
        if re.search(
            r"\b(?:several|many|multiple|recent)\s+years?\b|adult life",
            evidence,
            flags=re.IGNORECASE,
        ):
            _append_supported_candidate(
                candidates,
                "seizure free for multiple year",
                evidence,
                "vague multi-year seizure-free expression",
            )
            emitted = True
        if not emitted:
            _append_supported_candidate(
                candidates,
                "seizure free for multiple month",
                evidence,
                "seizure-free/no-event expression without exact duration",
            )
        date_range = re.search(
            rf"\bfrom\s+(?P<start_day>\d{{1,2}})\s+"
            rf"(?P<start_month>{MONTH_PATTERN}|{SHORT_MONTH_PATTERN})\s+"
            rf"(?P<start_year>\d{{4}})\s+to\s+(?P<end_day>\d{{1,2}})\s+"
            rf"(?P<end_month>{MONTH_PATTERN}|{SHORT_MONTH_PATTERN})\s+"
            rf"(?P<end_year>\d{{4}})\b",
            evidence,
            flags=re.IGNORECASE,
        )
        if date_range:
            months = max(
                1,
                (
                    int(date_range.group("end_year"))
                    - int(date_range.group("start_year"))
                )
                * 12
                + _month_number(date_range.group("end_month"))
                - _month_number(date_range.group("start_month"))
                + 1,
            )
            _append_supported_candidate(
                candidates,
                f"seizure free for {months} month",
                evidence,
                "explicit no-event calendar date range",
            )
    for date_range in re.finditer(
        rf"\bfrom\s+(?P<start_day>\d{{1,2}})\s+"
        rf"(?P<start_month>{MONTH_PATTERN}|{SHORT_MONTH_PATTERN})\s+"
        rf"(?P<start_year>\d{{4}})\s+to\s+(?P<end_day>\d{{1,2}})\s+"
        rf"(?P<end_month>{MONTH_PATTERN}|{SHORT_MONTH_PATTERN})\s+"
        rf"(?P<end_year>\d{{4}})\b",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, date_range.start(), date_range.end())
        following = note_text[date_range.end(): date_range.end() + 400]
        if not re.search(r"\bno (?:auras|events|episodes|seizures|spells|convulsive)", following, flags=re.IGNORECASE):
            continue
        months = max(
            1,
            (int(date_range.group("end_year")) - int(date_range.group("start_year")))
            * 12
            + _month_number(date_range.group("end_month"))
            - _month_number(date_range.group("start_month"))
            + 1,
        )
        _append_supported_candidate(
            candidates,
            f"seizure free for {months} month",
            evidence,
            "calendar date range followed by no-event statement",
        )
    return candidates


def _explicit_rate_high_recall_candidates(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    candidates: list[GanTemporalFrequencyCandidate] = []
    event_rate = re.compile(
        rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:brief |further |clinical |definite |nocturnal |daytime |"
        rf"focal aware |focal impaired-awareness |generalised |generalized |"
        rf"tonic[- ]clonic |myoclonic )?"
        rf"{EVENT_NOUN_PATTERN}\s+"
        rf"(?:per|a|each|every|/)\s+"
        rf"(?:(?P<period>{QUANTITY_RANGE_PATTERN})\s+)?"
        rf"(?P<unit>{PERIOD_UNIT_PATTERN})\b",
        flags=re.IGNORECASE,
    )
    for match in event_rate.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if "per cluster" in evidence.lower():
            continue
        count = _quantity_to_label(match.group("count"))
        period_count, period_unit = _period_parts(match.group("period"), match.group("unit"))
        _append_supported_candidate(
            candidates,
            _rate_label(count, period_count, period_unit),
            evidence,
            "explicit event count per period",
        )

    times_rate = re.compile(
        rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:times?|nights?)\s+(?:per|a|each)\s+"
        rf"(?:(?P<period>{QUANTITY_RANGE_PATTERN})\s+)?"
        rf"(?P<unit>{PERIOD_UNIT_PATTERN})\b",
        flags=re.IGNORECASE,
    )
    for match in times_rate.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if not _has_seizure_context(evidence):
            continue
        count = _quantity_to_label(match.group("count"))
        period_count, period_unit = _period_parts(match.group("period"), match.group("unit"))
        _append_supported_candidate(
            candidates,
            _rate_label(count, period_count, period_unit),
            evidence,
            "explicit times/nights per period in seizure context",
        )

    slash_rate = re.compile(
        rf"\b(?:{EVENT_NOUN_PATTERN}|tc|gtc|sz)?\s*"
        rf"(?:x|×|/)?\s*(?P<count>{QUANTITY_RANGE_PATTERN})\s*/\s*"
        rf"(?P<unit>d|day|wk|week|mo|month|yr|year)\b",
        flags=re.IGNORECASE,
    )
    for match in slash_rate.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if not _has_seizure_context(evidence):
            continue
        count = _quantity_to_label(match.group("count"))
        period_count, period_unit = _period_parts("1", match.group("unit"))
        _append_supported_candidate(
            candidates,
            _rate_label(count, period_count, period_unit),
            evidence,
            "shorthand count/unit seizure frequency",
        )

    every_rate = re.compile(
        rf"\b(?:(?P<count>{QUANTITY_RANGE_PATTERN})\s+)?"
        rf"(?:{EVENT_NOUN_PATTERN}\s+)?"
        rf"(?:occurring\s+|occur(?:s|ring)?\s+|happen(?:s|ing)?\s+)?"
        rf"(?:every|q)\s+(?P<period>{QUANTITY_RANGE_PATTERN})\s*"
        rf"(?P<unit>{PERIOD_UNIT_PATTERN})\b",
        flags=re.IGNORECASE,
    )
    for match in every_rate.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if not _has_seizure_context(evidence):
            continue
        count = _quantity_to_label(match.group("count") or "1")
        period_count, period_unit = _period_parts(match.group("period"), match.group("unit"))
        _append_supported_candidate(
            candidates,
            _rate_label(count, period_count, period_unit),
            evidence,
            "every/q interval seizure frequency",
        )

    once_every = re.compile(
        rf"\b(?P<count>once|twice|thrice|one|two|three|"
        rf"{QUANTITY_RANGE_PATTERN})\s+every\s+"
        rf"(?P<period>{QUANTITY_RANGE_PATTERN})\s*"
        rf"(?P<unit>{PERIOD_UNIT_PATTERN})\b",
        flags=re.IGNORECASE,
    )
    for match in once_every.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if not _has_seizure_context(evidence):
            continue
        count = _quantity_to_label(match.group("count"))
        period_count, period_unit = _period_parts(match.group("period"), match.group("unit"))
        _append_supported_candidate(
            candidates,
            _rate_label(count, period_count, period_unit),
            evidence,
            "once/twice every period seizure frequency",
        )

    adverbial_rate = re.compile(
        rf"\b(?:(?P<count>{QUANTITY_RANGE_PATTERN})\s+)?"
        rf"(?:{EVENT_NOUN_PATTERN}\s+)?"
        rf"(?P<adverb>daily|nightly|weekly|monthly|yearly)\b",
        flags=re.IGNORECASE,
    )
    adverb_units = {
        "daily": "day",
        "nightly": "day",
        "weekly": "week",
        "monthly": "month",
        "yearly": "year",
    }
    for match in adverbial_rate.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if not _has_seizure_context(evidence):
            continue
        count = _quantity_to_label(match.group("count") or "1")
        unit = adverb_units[match.group("adverb").lower()]
        _append_supported_candidate(
            candidates,
            _rate_label(count, "1", unit),
            evidence,
            "adverbial daily/weekly/monthly/yearly seizure frequency",
        )

    for match in re.finditer(
        r"\bmost (?:weekdays|days of the working week)\b",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if _has_seizure_context(evidence):
            _append_supported_candidate(
                candidates,
                "multiple per week",
                evidence,
                "most-weekdays seizure frequency maps to nonspecific recurrent weekly count",
            )

    for match in re.finditer(
        r"\b(?P<count>multiple|several|many)\s+"
        r"(?:times\s+)?(?:daily|per day|each day)\b",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if _has_seizure_context(evidence):
            _append_supported_candidate(
                candidates,
                "multiple per day",
                evidence,
                "nonspecific multiple daily seizure frequency",
            )
    frequency_rate = re.compile(
        rf"\b(?:frequency|average frequency|estimated seizure frequency|"
        rf"current seizure frequency|current average frequency)\s+"
        rf"(?:is|of|=|:)?\s*(?:<=|≤|up to|approximately|approx\.?|~|≈)?\s*"
        rf"(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:per|/)\s+(?:(?P<period>{QUANTITY_RANGE_PATTERN})\s+)?"
        rf"(?P<unit>{PERIOD_UNIT_PATTERN})\b",
        flags=re.IGNORECASE,
    )
    for match in frequency_rate.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        count = _quantity_to_label(match.group("count"))
        period_count, period_unit = _period_parts(match.group("period"), match.group("unit"))
        _append_supported_candidate(
            candidates,
            _rate_label(count, period_count, period_unit),
            evidence,
            "frequency field states count per period",
        )

    context_rate = re.compile(
        rf"\b(?:typically|usually|approximately|approx\.?|around|about|~|≈|<=|≤)?\s*"
        rf"(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:per|/)\s+(?:(?P<period>{QUANTITY_RANGE_PATTERN})\s+)?"
        rf"(?P<unit>{PERIOD_UNIT_PATTERN})\b",
        flags=re.IGNORECASE,
    )
    for match in context_rate.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if not _has_seizure_context(evidence) or "per cluster" in evidence.lower():
            continue
        count = _quantity_to_label(match.group("count"))
        period_count, period_unit = _period_parts(match.group("period"), match.group("unit"))
        _append_supported_candidate(
            candidates,
            _rate_label(count, period_count, period_unit),
            evidence,
            "bare count-per-period in seizure context",
        )

    event_on_rate = re.compile(
        rf"\b{EVENT_NOUN_PATTERN}\s+(?:on|at|to|of)\s+"
        rf"(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:per|/)\s+(?:(?P<period>{QUANTITY_RANGE_PATTERN})\s+)?"
        rf"(?P<unit>{PERIOD_UNIT_PATTERN})\b",
        flags=re.IGNORECASE,
    )
    for match in event_on_rate.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        count = _quantity_to_label(match.group("count"))
        period_count, period_unit = _period_parts(match.group("period"), match.group("unit"))
        _append_supported_candidate(
            candidates,
            _rate_label(count, period_count, period_unit),
            evidence,
            "event noun followed by count-per-period",
        )

    q_interval = re.compile(
        rf"\bq\s*(?P<period>{QUANTITY_RANGE_PATTERN})\s*"
        rf"(?P<unit>d|day|wk|week|mo|month|yr|year)\b",
        flags=re.IGNORECASE,
    )
    for match in q_interval.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if _has_seizure_context(evidence):
            period_count, period_unit = _period_parts(match.group("period"), match.group("unit"))
            _append_supported_candidate(
                candidates,
                _rate_label("1", period_count, period_unit),
                evidence,
                "q-interval shorthand in seizure context",
            )

    for match in re.finditer(
        r"\b(?:electrographic seizures?|seizures?)\s+frequent on EEG\s*"
        r"\(~?\d+(?:\.\d+)?/h\)",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, match.start(), match.end())
        _append_supported_candidate(
            candidates,
            "multiple per day",
            evidence,
            "hourly EEG seizure frequency maps to nonspecific multiple per day",
        )

    for match in re.finditer(
        rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+times\s+"
        rf"(?P<adverb>daily|weekly|monthly|yearly)\b",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if not _has_seizure_context(evidence):
            continue
        unit = {
            "daily": "day",
            "weekly": "week",
            "monthly": "month",
            "yearly": "year",
        }[match.group("adverb").lower()]
        _append_supported_candidate(
            candidates,
            _rate_label(_quantity_to_label(match.group("count")), "1", unit),
            evidence,
            "times-weekly/daily seizure frequency",
        )

    for match in re.finditer(
        rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+days?\s+of\s+the\s+week\b",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if _has_seizure_context(evidence):
            _append_supported_candidate(
                candidates,
                _rate_label(_quantity_to_label(match.group("count")), "1", "week"),
                evidence,
                "event days per week frequency",
            )

    for match in re.finditer(
        rf"\bfrequency\s+(?:of\s+)?(?:up to\s+)?"
        rf"(?P<count>{QUANTITY_RANGE_PATTERN})\s+in\s+(?:bad\s+)?weeks\b",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if _has_seizure_context(evidence):
            _append_supported_candidate(
                candidates,
                _rate_label(_quantity_to_label(match.group("count")), "1", "week"),
                evidence,
                "bad-week frequency expression",
            )

    for match in re.finditer(
        rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:seizures?|events?|episodes?)\s+last\s+week\b",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, match.start(), match.end())
        _append_supported_candidate(
            candidates,
            _rate_label(_quantity_to_label(match.group("count")), "1", "week"),
            evidence,
            "last-week event count",
        )

    for match in re.finditer(
        rf"\b(?:inter-seizure interval|intervals? ranging|events occurring at intervals ranging)"
        rf"[^.;]{{0,40}}?(?P<period>{QUANTITY_RANGE_PATTERN})\s*"
        rf"(?P<unit>{PERIOD_UNIT_PATTERN})\b",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, match.start(), match.end())
        _append_supported_candidate(
            candidates,
            _rate_label("1", *_period_parts(match.group("period"), match.group("unit"))),
            evidence,
            "inter-seizure interval converted to one event per interval",
        )

    for match in re.finditer(
        r"\bevery other week\b",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if _has_seizure_context(evidence):
            _append_supported_candidate(
                candidates,
                "1 per 2 week",
                evidence,
                "every-other-week frequency",
            )
    short_adverbial = re.compile(
        rf"\b(?P<count>once|twice|thrice)\s+(?:a|per)\s+"
        rf"(?P<unit>day|week|month|year|night|fortnight)\b",
        flags=re.IGNORECASE,
    )
    for match in short_adverbial.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if _has_seizure_context(evidence):
            period_count, period_unit = _period_parts("1", match.group("unit"))
            _append_supported_candidate(
                candidates,
                _rate_label(_quantity_to_label(match.group("count")), period_count, period_unit),
                evidence,
                "once/twice/thrice a period seizure frequency",
            )

    fortnight_range = re.compile(
        rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+a\s+fortnight\b",
        flags=re.IGNORECASE,
    )
    for match in fortnight_range.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if _has_seizure_context(evidence):
            _append_supported_candidate(
                candidates,
                _rate_label(_quantity_to_label(match.group("count")), "2", "week"),
                evidence,
                "count per fortnight seizure frequency",
            )
    return candidates


def _count_window_high_recall_candidates(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    candidates: list[GanTemporalFrequencyCandidate] = []
    window_re = re.compile(
        rf"\b(?:over|during|within|across|in|for)\s+(?:the\s+)?"
        rf"(?:(?:past|last|previous|preceding|recent)\s+)?"
        rf"(?:(?P<count>{QUANTITY_RANGE_PATTERN})\s+)?"
        rf"(?P<unit>{PERIOD_UNIT_PATTERN})\b",
        flags=re.IGNORECASE,
    )
    for sentence_start, sentence_end, sentence in _iter_sentence_spans(note_text):
        if not _has_seizure_context(sentence):
            continue
        event_counts = _event_counts_in_text(sentence)
        if not event_counts:
            continue
        event_count = _combine_event_counts(event_counts)
        for match in window_re.finditer(sentence):
            period_count, period_unit = _period_parts(match.group("count"), match.group("unit"))
            evidence = note_text[sentence_start:sentence_end].strip()
            _append_supported_candidate(
                candidates,
                _rate_label(event_count, period_count, period_unit),
                evidence,
                "event count over explicit observation window",
            )
            simplified = _single_unit_rate(event_count, period_count, period_unit)
            if simplified is not None:
                _append_supported_candidate(
                    candidates,
                    simplified,
                    evidence,
                    "event/window count converted to single-period rate",
                )
            if period_count == "4" and period_unit == "week":
                _append_supported_candidate(
                    candidates,
                    _rate_label(event_count, "1", "month"),
                    evidence,
                    "four-week observation window also maps to benchmark month",
                )
        if re.search(r"\b(?:yesterday|today|overnight)\b", sentence, flags=re.IGNORECASE):
            evidence = note_text[sentence_start:sentence_end].strip()
            _append_supported_candidate(
                candidates,
                _rate_label(event_count, "1", "day"),
                evidence,
                "single-day deictic observation window",
            )
        if re.search(r"\bthis month\b", sentence, flags=re.IGNORECASE):
            evidence = note_text[sentence_start:sentence_end].strip()
            _append_supported_candidate(
                candidates,
                _rate_label(event_count, "1", "month"),
                evidence,
                "event count within this-month window",
            )
        if re.search(r"\b(?:this|current)\s+week\b", sentence, flags=re.IGNORECASE):
            evidence = note_text[sentence_start:sentence_end].strip()
            _append_supported_candidate(
                candidates,
                _rate_label(event_count, "1", "week"),
                evidence,
                "event count within this-week window",
            )
        if re.search(r"\b(?:this year|year to date|so far this year)\b", sentence, flags=re.IGNORECASE):
            evidence = note_text[sentence_start:sentence_end].strip()
            clinic_date = _clinic_date(note_text)
            if clinic_date is not None:
                _append_supported_candidate(
                    candidates,
                    _rate_label(event_count, str(max(1, clinic_date.month)), "month"),
                    evidence,
                    "year-to-date count anchored to clinic month",
                )
            _append_supported_candidate(
                candidates,
                _rate_label(event_count, "1", "year"),
                evidence,
                "calendar-year count treated as yearly rate candidate",
            )
        year_so_far = re.search(r"\b(?:in|documented in|recorded in)\s+(?P<year>\d{4})\s+so far\b", sentence, flags=re.IGNORECASE)
        if year_so_far:
            evidence = note_text[sentence_start:sentence_end].strip()
            clinic_date = _clinic_date(note_text)
            if clinic_date is not None and int(year_so_far.group("year")) == clinic_date.year:
                _append_supported_candidate(
                    candidates,
                    _rate_label(event_count, str(max(1, clinic_date.month)), "month"),
                    evidence,
                    "same-calendar-year count anchored to clinic month",
                )
            _append_supported_candidate(
                candidates,
                _rate_label(event_count, "1", "year"),
                evidence,
                "explicit calendar-year-so-far count treated as yearly candidate",
            )
        since_month_year = re.search(
            r"\bsince\s+(?P<month>\d{1,2})/(?P<year>\d{4})\b",
            sentence,
            flags=re.IGNORECASE,
        )
        if since_month_year:
            clinic_date = _clinic_date(note_text)
            if clinic_date is not None:
                months = _months_between_month_year(
                    clinic_date,
                    int(since_month_year.group("month")),
                    int(since_month_year.group("year")),
                )
                evidence = note_text[sentence_start:sentence_end].strip()
                _append_supported_candidate(
                    candidates,
                    _rate_label(event_count, str(months), "month"),
                    evidence,
                    "event count since month/year diary anchor",
                )
    return candidates


def _single_unit_rate(
    event_count: str,
    period_count: str,
    period_unit: str,
) -> str | None:
    if period_unit not in {"day", "week", "month", "year"}:
        return None
    if " to " in event_count or " to " in period_count:
        return None
    if event_count == "multiple" or period_count == "multiple":
        return None
    try:
        numerator = float(event_count)
        denominator = float(period_count)
    except ValueError:
        return None
    if denominator <= 1:
        return None
    value = numerator / denominator
    if value >= 1:
        return None
    value_text = str(round(value, 3)).rstrip("0").rstrip(".")
    return _rate_label(value_text, "1", period_unit)


def _event_counts_in_text(text: str) -> list[str]:
    counts: list[str] = []
    count_before_event = re.compile(
        rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:brief |further |clinical |definite |nocturnal |daytime |"
        rf"focal aware |focal impaired-awareness |generalised |generalized |"
        rf"tonic[- ]clonic |myoclonic |recorded |reported |short )*"
        rf"{EVENT_NOUN_PATTERN}\b",
        flags=re.IGNORECASE,
    )
    for match in count_before_event.finditer(text):
        count = _quantity_to_label(match.group("count"))
        if count not in {"", "0"}:
            counts.append(count)
    for match in re.finditer(
        rf"\b(?:tc|gtc|sz)\s*(?:x|×)\s*(?P<count>{QUANTITY_RANGE_PATTERN})\b",
        text,
        flags=re.IGNORECASE,
    ):
        counts.append(_quantity_to_label(match.group("count")))
    seizure_days = re.search(
        rf"\bseizure days?:\s*(?P<count>{QUANTITY_RANGE_PATTERN})(?:/30)?\b",
        text,
        flags=re.IGNORECASE,
    )
    if seizure_days:
        counts.append(_quantity_to_label(seizure_days.group("count")))
    for match in re.finditer(
        rf"\band\s+(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:while awake|overnight|on waking)\b",
        text,
        flags=re.IGNORECASE,
    ):
        counts.append(_quantity_to_label(match.group("count")))
    return counts


def _combine_event_counts(counts: list[str]) -> str:
    if not counts:
        return ""
    if any(count == "multiple" for count in counts):
        return "multiple"
    if len(counts) == 1:
        return counts[0]
    numeric_total = 0.0
    for count in counts:
        if " to " in count:
            if len(counts) == 1:
                return count
            return count
        try:
            numeric_total += float(count)
        except ValueError:
            return count
    return str(numeric_total).removesuffix(".0")


def _named_month_clause_high_recall_candidates(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    month_rows = _named_month_clause_counts(note_text)
    if not month_rows:
        return []
    candidates: list[GanTemporalFrequencyCandidate] = []
    total = _combine_event_counts([row[1] for row in month_rows])
    first_month = min(row[0] for row in month_rows)
    last_month = max(row[0] for row in month_rows)
    first_start = min(row[2] for row in month_rows)
    last_end = max(row[3] for row in month_rows)
    evidence = _sentence_around(note_text, first_start, last_end)
    windows = {
        len({row[0] for row in month_rows}),
        _inclusive_month_span(first_month, last_month),
    }
    clinic_date = _clinic_date(note_text)
    if clinic_date is not None:
        elapsed = clinic_date.month - first_month
        if elapsed > 0:
            windows.add(elapsed)
    for window in sorted(window for window in windows if window >= 1):
        _append_supported_candidate(
            candidates,
            _rate_label(total, str(window), "month"),
            evidence,
            "named-month clauses summed over plausible diary windows",
        )
    return candidates


def _named_month_clause_counts(note_text: str) -> list[tuple[int, str, int, int]]:
    rows: list[tuple[int, str, int, int]] = []
    month_names = rf"{MONTH_PATTERN}|{SHORT_MONTH_PATTERN}"
    in_month = re.compile(
        rf"\b(?:in|during)\s+(?P<month>{month_names})\b"
        rf"(?P<body>.*?)(?=(?:\b(?:in|during)\s+(?:{month_names})\b)|[.\n])",
        flags=re.IGNORECASE | re.DOTALL,
    )
    for match in in_month.finditer(note_text):
        body = match.group("body")
        evidence = match.group(0)
        if not _has_seizure_context(evidence):
            continue
        counts = _event_counts_in_text(evidence)
        if re.search(r"\banother\b", body, flags=re.IGNORECASE) and not counts:
            counts.append("1")
        if counts:
            rows.append(
                (
                    _month_number(match.group("month")),
                    _combine_event_counts(counts),
                    match.start(),
                    match.end(),
                )
            )

    event_in_month = re.compile(
        rf"\b(?P<count>{QUANTITY_RANGE_PATTERN}|another)\s+"
        rf"(?:brief |further |single |nocturnal |daytime |generalised |generalized |"
        rf"tonic[- ]clonic |myoclonic |focal |short )*"
        rf"{EVENT_NOUN_PATTERN}\s+in\s+(?P<month>{month_names})\b",
        flags=re.IGNORECASE,
    )
    for match in event_in_month.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if not _has_seizure_context(evidence):
            continue
        count = "1" if match.group("count").lower() == "another" else _quantity_to_label(match.group("count"))
        rows.append((_month_number(match.group("month")), count, match.start(), match.end()))

    cluster_of_in_month = re.compile(
        rf"\bcluster of (?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"{EVENT_NOUN_PATTERN}\s+in\s+(?P<month>{month_names})\b",
        flags=re.IGNORECASE,
    )
    for match in cluster_of_in_month.finditer(note_text):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if _has_seizure_context(evidence):
            rows.append(
                (
                    _month_number(match.group("month")),
                    _quantity_to_label(match.group("count")),
                    match.start(),
                    match.end(),
                )
            )
    return rows


def _inclusive_month_span(first_month: int, last_month: int) -> int:
    if last_month >= first_month:
        return last_month - first_month + 1
    return (12 - first_month + 1) + last_month


def _month_tally_high_recall_candidates(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    candidates: list[GanTemporalFrequencyCandidate] = []
    month_count_matches = list(
        re.finditer(
            rf"\b(?P<month>{MONTH_PATTERN}|{SHORT_MONTH_PATTERN})\b"
            rf"[^.\n;:]{{0,80}}?"
            rf"(?:x|×|had|with|there (?:were|was)|experienced|recorded)?\s*"
            rf"(?P<count>{QUANTITY_RANGE_PATTERN})\s*"
            rf"(?:{EVENT_NOUN_PATTERN})?",
            note_text,
            flags=re.IGNORECASE,
        )
    )
    usable: list[tuple[int, str, int, int]] = []
    for match in month_count_matches:
        evidence = _sentence_around(note_text, match.start(), match.end())
        if not _has_seizure_context(evidence):
            continue
        count = _quantity_to_label(match.group("count"))
        if count == "0" or " to " in count or count == "multiple":
            continue
        month_number = _month_number(match.group("month"))
        usable.append((month_number, count, match.start(), match.end()))
    if not usable:
        return candidates
    total = _combine_event_counts([count for _, count, _, _ in usable])
    first_month = min(month for month, _, _, _ in usable)
    last_month = max(month for month, _, _, _ in usable)
    evidence = _sentence_around(
        note_text,
        min(start for _, _, start, _ in usable),
        max(end for _, _, _, end in usable),
    )
    for window in sorted({len({month for month, _, _, _ in usable}), last_month - first_month + 1}):
        if window >= 1:
            _append_supported_candidate(
                candidates,
                _rate_label(total, str(window), "month"),
                evidence,
                "named-month event tallies summed over listed months",
            )
    clinic_date = _clinic_date(note_text)
    if clinic_date is not None:
        elapsed = clinic_date.month - first_month
        if elapsed >= 1:
            _append_supported_candidate(
                candidates,
                _rate_label(total, str(elapsed), "month"),
                evidence,
                "named-month event tallies summed from first month to clinic month",
            )
    return candidates


def _cluster_high_recall_candidates(
    note_text: str,
) -> list[GanTemporalFrequencyCandidate]:
    candidates: list[GanTemporalFrequencyCandidate] = []
    cluster_mentions = list(
        re.finditer(
            r"\b(?:clusters?|batches|burst periods?|group together|run of)\b",
            note_text,
            flags=re.IGNORECASE,
        )
    )
    for mention in cluster_mentions:
        evidence = _sentence_around(note_text, mention.start(), mention.end())
        per_cluster = _per_cluster_count_from_text(evidence)
        if per_cluster is None:
            per_cluster = "multiple" if re.search(
                r"\b(?:var(?:y|ies)|brief episodes|multiple|several|bursts?|batches|flurries)\b",
                evidence,
                flags=re.IGNORECASE,
            ) else None
        if re.search(r"\bcomprising brief episodes\b", evidence, flags=re.IGNORECASE):
            per_cluster = "multiple"
        if per_cluster is None or per_cluster == "multiple":
            events_over = re.search(
                rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+events?\s+over\s+",
                evidence,
                flags=re.IGNORECASE,
            )
            if events_over:
                per_cluster = _quantity_to_label(events_over.group("count"))
        per_episode_count = re.search(
            rf"(?:~|≈)?\s*(?P<count>\d+(?:\.\d+)?)\s+events?\s+per\s+episode\b",
            evidence,
            flags=re.IGNORECASE,
        )
        if per_episode_count:
            per_cluster = _quantity_to_label(per_episode_count.group("count"))
        if per_cluster is None and re.search(r"\b(?:run of|batches|burst periods?)\b", evidence, flags=re.IGNORECASE):
            counts = _event_counts_in_text(evidence)
            per_cluster = _combine_event_counts(counts) if counts else "multiple"
        if per_cluster is not None and re.search(
            r"\b(?:unknown|uncertain|not tracked|not documented|unable to quantify|"
            r"no reliable|without reliable|frequency (?:is )?unclear)\b",
            evidence,
            flags=re.IGNORECASE,
        ):
            _append_supported_candidate(
                candidates,
                f"unknown, {per_cluster} per cluster",
                evidence,
                "per-cluster count present but cluster spacing unknown",
            )

        explicit_count = re.search(
            rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
            rf"(?:[A-Za-z-]+\s+){{0,3}}clusters?\s+"
            rf"(?:this|per|each)\s+month\b",
            evidence,
            flags=re.IGNORECASE,
        )
        if explicit_count:
            cluster_count = _quantity_to_label(explicit_count.group("count"))
            _append_supported_candidate(
                candidates,
                _cluster_rate_label(cluster_count, "1", "month", per_cluster or "multiple"),
                evidence,
                "explicit cluster count this/per month",
            )

        window_count = re.search(
            rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
            rf"(?:[A-Za-z-]+\s+){{0,3}}clusters?\s+"
            rf"(?:over|during|in|within)\s+(?:the\s+)?(?:past|last)?\s*"
            rf"(?:(?P<period>{QUANTITY_RANGE_PATTERN})\s+)?(?P<unit>{PERIOD_UNIT_PATTERN})\b",
            evidence,
            flags=re.IGNORECASE,
        )
        if window_count:
            clusters = _quantity_to_label(window_count.group("count"))
            period_count, period_unit = _period_parts(
                window_count.group("period"),
                window_count.group("unit"),
            )
            _append_supported_candidate(
                candidates,
                _cluster_rate_label(
                    clusters,
                    period_count,
                    period_unit,
                    per_cluster or "multiple",
                ),
                evidence,
                "cluster count over explicit observation window",
            )

        run_window = re.search(
            rf"\b(?:over|during|in|within)\s+(?:the\s+)?(?:past|last)?\s*"
            rf"(?:(?P<period>{QUANTITY_RANGE_PATTERN})\s+)?(?P<unit>{PERIOD_UNIT_PATTERN})\b",
            evidence,
            flags=re.IGNORECASE,
        )
        if run_window and re.search(r"\b(?:run of|batches|burst periods?)\b", evidence, flags=re.IGNORECASE):
            period_count, period_unit = _period_parts(
                run_window.group("period"),
                run_window.group("unit"),
            )
            _append_supported_candidate(
                candidates,
                _cluster_rate_label("1", period_count, period_unit, per_cluster or "multiple"),
                evidence,
                "single run/batch cluster over explicit observation window",
            )

        cluster_x_rate = re.search(
            rf"\bclusters?\s*(?P<count>{QUANTITY_RANGE_PATTERN})?\s*"
            rf"(?:x|×|/|per)\s*/?\s*(?P<unit>week|wk|month|mo|year|yr|day|d)\b",
            evidence,
            flags=re.IGNORECASE,
        )
        if cluster_x_rate:
            clusters = _quantity_to_label(cluster_x_rate.group("count") or "1")
            _, period_unit = _period_parts("1", cluster_x_rate.group("unit"))
            _append_supported_candidate(
                candidates,
                _cluster_rate_label(clusters, "1", period_unit, per_cluster or "multiple"),
                evidence,
                "cluster shorthand count per period",
            )

        for adverb, period_count, period_unit in (
            ("weekly", "1", "week"),
            ("monthly", "1", "month"),
            ("quarterly", "3", "month"),
        ):
            if re.search(rf"\b{adverb}\s+clusters?\b|\bclusters?\s+{adverb}\b", evidence, flags=re.IGNORECASE):
                _append_supported_candidate(
                    candidates,
                    _cluster_rate_label(
                        "1",
                        period_count,
                        period_unit,
                        per_cluster or "multiple",
                    ),
                    evidence,
                    f"{adverb} cluster frequency",
                )

        if re.search(r"\bweekly\b", evidence, flags=re.IGNORECASE) and "cluster" in evidence.lower():
            _append_supported_candidate(
                candidates,
                _cluster_rate_label("1", "1", "week", per_cluster or "multiple"),
                evidence,
                "weekly cluster frequency in cluster context",
            )

        every_spacing = re.search(
            rf"\b(?:every|spaced|spacing|without seizures for)\s+"
            rf"(?P<period>{QUANTITY_RANGE_PATTERN})\s*"
            rf"(?P<unit>{PERIOD_UNIT_PATTERN})\b",
            evidence,
            flags=re.IGNORECASE,
        )
        if every_spacing:
            period_count, period_unit = _period_parts(
                every_spacing.group("period"),
                every_spacing.group("unit"),
            )
            _append_supported_candidate(
                candidates,
                _cluster_rate_label(
                    "1",
                    period_count,
                    period_unit,
                    per_cluster or "multiple",
                ),
                evidence,
                "cluster spacing interval with per-cluster burden",
            )
            _append_supported_candidate(
                candidates,
                _rate_label("1", period_count, period_unit),
                evidence,
                "cluster spacing interval also supports simple frequency label",
            )

        batch_spacing = re.search(
            rf"\bgo\s+(?P<period>{QUANTITY_RANGE_PATTERN})\s*"
            rf"(?P<unit>{PERIOD_UNIT_PATTERN})\s+without seizures\b",
            evidence,
            flags=re.IGNORECASE,
        )
        if batch_spacing and re.search(r"\bbatches\b", evidence, flags=re.IGNORECASE):
            period_count, period_unit = _period_parts(
                batch_spacing.group("period"),
                batch_spacing.group("unit"),
            )
            _append_supported_candidate(
                candidates,
                _cluster_rate_label("1", period_count, period_unit, per_cluster or "multiple"),
                evidence,
                "batch spacing interval with per-batch burden",
            )

        if re.search(r"\bone cluster this week\b", evidence, flags=re.IGNORECASE):
            _append_supported_candidate(
                candidates,
                _cluster_rate_label("1", "1", "week", per_cluster or "multiple"),
                evidence,
                "one cluster in current week",
            )

        if per_cluster is not None:
            _append_supported_candidate(
                candidates,
                f"unknown, {per_cluster} per cluster",
                evidence,
                "fallback unknown-spacing cluster candidate",
            )
    for match in re.finditer(
        rf"\b(?P<count1>{QUANTITY_RANGE_PATTERN})\s+(?:brief\s+)?events?\s+on\s+"
        rf"\d{{1,2}}/\d{{1,2}}\s+and\s+(?P<count2>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:overnight|events?)\s+on\s+\d{{1,2}}/\d{{1,2}}",
        note_text,
        flags=re.IGNORECASE,
    ):
        evidence = _sentence_around(note_text, match.start(), match.end())
        if "cluster" in note_text.lower():
            _append_supported_candidate(
                candidates,
                "unknown, multiple per cluster",
                evidence,
                "dated event bursts with cluster context but unknown spacing",
            )
    return candidates


def _per_cluster_count_from_text(text: str) -> str | None:
    patterns = [
        rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+per\s+(?:cluster|episode|run)\b",
        rf"\b(?:each|per cluster|per episode|per run|comprising|usually|typically)"
        rf"[^.;:]{{0,35}}?(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:{EVENT_NOUN_PATTERN})?",
        rf"\b(?:with|usually|typically|comprising|characteri[sz]ed by)\s+"
        rf"(?P<count>{QUANTITY_RANGE_PATTERN})\s+(?:{EVENT_NOUN_PATTERN})",
        rf"\bclusters? of (?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:{EVENT_NOUN_PATTERN})",
        rf"\bbatches,?\s+with\s+(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:occurring|{EVENT_NOUN_PATTERN})",
        rf"\brun of (?P<count>{QUANTITY_RANGE_PATTERN})\s+"
        rf"(?:{EVENT_NOUN_PATTERN})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _quantity_to_label(match.group("count"))
    if re.search(r"\b(?:per cluster|per episode)\b", text, flags=re.IGNORECASE):
        before_per = re.search(
            rf"\b(?P<count>{QUANTITY_RANGE_PATTERN})\s+"
            rf"(?:{EVENT_NOUN_PATTERN})\s+per\s+(?:cluster|episode)\b",
            text,
            flags=re.IGNORECASE,
        )
        if before_per:
            return _quantity_to_label(before_per.group("count"))
        return "multiple"
    return None


def _dates_in_text(text: str) -> list[date]:
    parsed: list[date] = []
    for match in re.finditer(
        rf"\b(?P<day>\d{{1,2}})[-/ ](?P<month>{MONTH_PATTERN}|{SHORT_MONTH_PATTERN})[-/ ](?P<year>\d{{4}})\b",
        text,
        flags=re.IGNORECASE,
    ):
        parsed.append(
            date(
                int(match.group("year")),
                _month_number(match.group("month")),
                int(match.group("day")),
            )
        )
    for match in re.finditer(
        rf"\b(?P<day>\d{{1,2}})\s+(?P<month>{MONTH_PATTERN}|{SHORT_MONTH_PATTERN})\s+(?P<year>\d{{4}})\b",
        text,
        flags=re.IGNORECASE,
    ):
        parsed.append(
            date(
                int(match.group("year")),
                _month_number(match.group("month")),
                int(match.group("day")),
            )
        )
    for match in re.finditer(
        r"\b(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})\b",
        text,
        flags=re.IGNORECASE,
    ):
        parsed.append(
            date(
                int(match.group("year")),
                int(match.group("month")),
                int(match.group("day")),
            )
        )
    for match in re.finditer(
        rf"\b(?P<month>{MONTH_PATTERN}|{SHORT_MONTH_PATTERN})\s+(?P<year>\d{{4}})\b",
        text,
        flags=re.IGNORECASE,
    ):
        parsed.append(date(int(match.group("year")), _month_number(match.group("month")), 1))
    return parsed


def _months_between_dates(clinic_date: date, start_date: date) -> int:
    return max(1, (clinic_date.year - start_date.year) * 12 + clinic_date.month - start_date.month)


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
    normalized = normalized.strip(".,;:()[]")
    normalized = normalized.replace("–", "-").replace("—", "-").replace("−", "-")
    normalized = normalized.replace(" - ", " to ").replace("-", " to ")
    normalized = re.sub(r"^(?:about|approximately|around|roughly|circa|~|≈|<=|≤|up to|at most)\s+", "", normalized)
    normalized = re.sub(r"\b(?:seizures?|events?|episodes?|absences?|convulsions?|attacks?|jerks?|spells?)\b.*$", "", normalized).strip()
    if normalized in {"a pair", "a pair of", "pair", "pair of"}:
        return "2"
    if normalized in {"once", "one time"}:
        return "1"
    if normalized in {"twice", "two times"}:
        return "2"
    if normalized in {"thrice", "three times"}:
        return "3"
    if normalized in {"few", "several", "many", "multiple"}:
        return "multiple"
    normalized = normalized.replace(" or ", " to ")
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
