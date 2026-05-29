"""Deterministic Gan S0 quantified-rate answer-option constructor.

This layer is intentionally downstream of the raw temporal-candidate inventory.
It emits separate constructed answer options for G20/G21 quantified-rate
aggregation fixtures and leaves raw candidate records unchanged.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

from clinical_extraction.gan.frequency import normalize_label
from clinical_extraction.schemas import GanRecord

GAN_S0_AGGREGATION_CONSTRUCTOR_PRIMITIVE_ID = (
    "gan.frequency.aggregation_constructor.v1"
)
ELIGIBLE_POLICY_CLASSES = {"aggregation_required_temporal_slot_missing"}

_MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}
_MONTH_PATTERN = "|".join(sorted(_MONTHS, key=len, reverse=True))
_NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "another": 1,
    "single": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}
_QUANTITY_PATTERN = (
    r"\d+(?:\.\d+)?|a|an|another|single|one|two|three|four|five|six|seven|"
    r"eight|nine|ten|eleven|twelve"
)
_EVENT_NOUN_PATTERN = (
    r"seizures?|events?|episodes?|spells?|jerks?|convulsions?|"
    r"generalised tonic[-– ]clonic seizures?|tonic[-– ]clonic seizures?"
)


@dataclass(frozen=True)
class GanAggregationConstructedOption:
    """Constructed quantified-rate answer option with provenance."""

    constructed_label: str
    source_record_id: str
    source_evidence: str
    numerator: str
    denominator: str
    unit: str
    derivation_kind: str
    policy_class: str
    contributing_candidate_labels: tuple[str, ...]
    contributing_candidate_evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "primitive_id": GAN_S0_AGGREGATION_CONSTRUCTOR_PRIMITIVE_ID,
            "constructed_label": self.constructed_label,
            "canonical_label": self.constructed_label,
            "source": "deterministic_aggregation_constructor",
            "source_record_id": self.source_record_id,
            "source_evidence": self.source_evidence,
            "evidence_text": self.source_evidence,
            "numerator": self.numerator,
            "event_count": self.numerator,
            "denominator": self.denominator,
            "window_count": self.denominator,
            "unit": self.unit,
            "window_unit": self.unit,
            "derivation_kind": self.derivation_kind,
            "derivation": self.derivation_kind,
            "policy_class": self.policy_class,
            "contributing_candidate_labels": list(self.contributing_candidate_labels),
            "contributing_candidate_evidence": list(self.contributing_candidate_evidence),
        }


def construct_gan_s0_aggregation_options(
    *,
    record: GanRecord,
    policy_class: str,
    candidate_records: list[dict[str, Any]],
) -> list[GanAggregationConstructedOption]:
    """Construct quantified-rate answer options for eligible G20 policy rows."""

    if policy_class not in ELIGIBLE_POLICY_CLASSES:
        return []

    constructed: list[GanAggregationConstructedOption] = []
    for result in (
        _construct_month_tally(record.note_text),
        _construct_compound_last_month(record.note_text),
        _construct_past_weeks(record.note_text),
        _construct_dated_diary(record.note_text),
    ):
        if result is None:
            continue
        numerator, denominator, unit, evidence, derivation = result
        options_to_add = [
            _option(
                record=record,
                candidate_records=candidate_records,
                numerator=numerator,
                denominator=denominator,
                unit=unit,
                evidence=evidence,
                derivation=derivation,
                policy_class=policy_class,
            )
        ]
        reduced_numerator, reduced_denominator = _simplify(numerator, denominator)
        if (reduced_numerator, reduced_denominator) != (numerator, denominator):
            options_to_add.append(
                _option(
                    record=record,
                    candidate_records=candidate_records,
                    numerator=reduced_numerator,
                    denominator=reduced_denominator,
                    unit=unit,
                    evidence=evidence,
                    derivation=f"{derivation}_reduced_equivalent",
                    policy_class=policy_class,
                )
            )
        for option in options_to_add:
            if option.constructed_label not in {
                existing.constructed_label for existing in constructed
            }:
                constructed.append(option)
    return constructed

def _construct_month_tally(text: str) -> tuple[int, int, str, str, str] | None:
    rows = _month_tally_rows(text)
    if len(rows) < 2:
        return None
    window = _month_tally_window([row[0] for row in rows])
    total = sum(count for _, count, _, _ in rows)
    if total <= 0 or window <= 0:
        return None
    evidence = _span_text(text, min(row[2] for row in rows), max(row[3] for row in rows))
    return (
        total,
        window,
        "month",
        evidence,
        "g21_month_tally_aggregation",
    )


def _month_tally_rows(text: str) -> list[tuple[int, int, int, int]]:
    rows: list[tuple[int, int, int, int]] = []
    month = rf"(?P<month>{_MONTH_PATTERN})"
    x_table = re.compile(
        rf"\b{month}\s*x\s*(?P<count>\d+)\b",
        flags=re.IGNORECASE,
    )
    for match in x_table.finditer(text):
        rows.append(
            (
                _month_number(match.group("month")),
                int(match.group("count")),
                match.start(),
                match.end(),
            )
        )

    prefix = re.compile(
        rf"\b(?:in|during)?\s*{month}\b"
        rf"(?P<body>.*?)(?=\b(?:in|during)\s+(?:{_MONTH_PATTERN})\b|[.\n])",
        flags=re.IGNORECASE,
    )
    for match in prefix.finditer(text):
        body = match.group("body")
        count = _count_in_month_body(body)
        if count is not None:
            rows.append((_month_number(match.group("month")), count, match.start(), match.end()))

    suffix = re.compile(
        rf"\b(?P<count>{_QUANTITY_PATTERN})\s+"
        rf"(?:(?:brief|further|single|nocturnal|daytime|generalised|"
        rf"generalized|tonic[-– ]clonic|tonic|myoclonic|focal|short)\s+)*"
        rf"(?:(?:{_EVENT_NOUN_PATTERN})\s+)?in\s+{month}\b",
        flags=re.IGNORECASE,
    )
    for match in suffix.finditer(text):
        evidence = _span_text(text, match.start(), match.end())
        if _seizure_context(evidence):
            rows.append(
                (
                    _month_number(match.group("month")),
                    _quantity_to_int(match.group("count")),
                    match.start(),
                    match.end(),
                )
            )

    cluster_suffix = re.compile(
        rf"\bcluster of (?P<count>{_QUANTITY_PATTERN})\s+"
        rf"(?:{_EVENT_NOUN_PATTERN})\s+in\s+{month}\b",
        flags=re.IGNORECASE,
    )
    for match in cluster_suffix.finditer(text):
        rows.append(
            (
                _month_number(match.group("month")),
                _quantity_to_int(match.group("count")),
                match.start(),
                match.end(),
            )
        )
    return _dedupe_month_rows(sorted(rows, key=lambda row: row[2]))


def _count_in_month_body(body: str) -> int | None:
    x_match = re.search(r"\bx\s*(?P<count>\d+)\b", body, flags=re.IGNORECASE)
    if x_match:
        return int(x_match.group("count"))
    counts: list[int] = []
    for event_count in re.finditer(
        rf"\b(?P<count>{_QUANTITY_PATTERN})\s+"
        rf"(?:brief |further |single |nocturnal |daytime |generalised |"
        rf"generalized |tonic[-– ]clonic |tonic |myoclonic |focal |short )*"
        rf"(?:{_EVENT_NOUN_PATTERN})\b",
        body,
        flags=re.IGNORECASE,
    ):
        counts.append(_quantity_to_int(event_count.group("count")))
    for contextual_count in re.finditer(
        rf"\b(?P<count>{_QUANTITY_PATTERN})\s+"
        r"(?:in sleep|during sleep|while awake|at night|overnight|during respite care)\b",
        body,
        flags=re.IGNORECASE,
    ):
        counts.append(_quantity_to_int(contextual_count.group("count")))
    if re.search(r"\banother\b", body, flags=re.IGNORECASE) and not counts:
        counts.append(1)
    if counts:
        return sum(counts)
    return None


def _construct_compound_last_month(text: str) -> tuple[int, int, str, str, str] | None:
    match = re.search(
        rf"(?P<evidence>[^.]*\b(?P<count1>{_QUANTITY_PATTERN})\s+focal sensory"
        rf"[^.]*?\band\s+(?P<count2>{_QUANTITY_PATTERN})\s+focal non-motor"
        rf"[^.]*?\bin last month[^.]*)",
        text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    total = _quantity_to_int(match.group("count1")) + _quantity_to_int(match.group("count2"))
    return (
        total,
        1,
        "month",
        match.group("evidence").strip(),
        "g21_compound_last_month_count_aggregation",
    )


def _construct_past_weeks(text: str) -> tuple[int, int, str, str, str] | None:
    match = re.search(
        rf"(?P<evidence>[^.]*\b(?P<count>{_QUANTITY_PATTERN})\s+"
        rf"(?:brief |generalised |generalized |tonic[-– ]clonic |focal )*"
        rf"(?:{_EVENT_NOUN_PATTERN})\s+[^.]*?\b(?:past|last)\s+"
        rf"(?:(?P<weeks>{_QUANTITY_PATTERN})\s+weeks?|fortnight)\b[^.]*)",
        text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    event_count = _quantity_to_int(match.group("count"))
    weeks = 2 if "fortnight" in match.group(0).lower() else _quantity_to_int(match.group("weeks"))
    if weeks % 4 == 0:
        numerator, denominator = _simplify(event_count, weeks // 4)
        unit = "month"
    else:
        numerator, denominator = _simplify(event_count, weeks)
        unit = "week"
    return (
        numerator,
        denominator,
        unit,
        match.group("evidence").strip(),
        "g21_explicit_week_window_aggregation",
    )


def _construct_dated_diary(text: str) -> tuple[int, int, str, str, str] | None:
    match = re.search(
        r"(?P<evidence>[^.]*\bSeizure events on (?P<dates>[^\".]+)[\".]?)",
        text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    dates = re.findall(r"\b(?P<month>\d{1,2})[-/](?P<day>\d{1,2})\b", match.group("dates"))
    if len(dates) < 2:
        return None
    months = [int(month) for month, _day in dates]
    window = max(1, months[-1] - months[0])
    numerator, denominator = _simplify(len(dates), window)
    return (
        numerator,
        denominator,
        "month",
        match.group("evidence").strip(),
        "g21_dated_diary_event_window_aggregation",
    )


def _option(
    *,
    record: GanRecord,
    candidate_records: list[dict[str, Any]],
    numerator: int,
    denominator: int,
    unit: str,
    evidence: str,
    derivation: str,
    policy_class: str,
) -> GanAggregationConstructedOption:
    label = _rate_label(numerator, denominator, unit)
    contributing = _contributing_candidates(candidate_records, evidence)
    return GanAggregationConstructedOption(
        constructed_label=normalize_label(label),
        source_record_id=record.record_id,
        source_evidence=evidence,
        numerator=str(numerator),
        denominator=str(denominator),
        unit=unit,
        derivation_kind=derivation,
        policy_class=policy_class,
        contributing_candidate_labels=tuple(
            str(candidate.get("canonical_label") or "") for candidate in contributing
        ),
        contributing_candidate_evidence=tuple(
            str(candidate.get("evidence_text") or "") for candidate in contributing
        ),
    )


def _contributing_candidates(
    candidate_records: list[dict[str, Any]],
    evidence: str,
) -> list[dict[str, Any]]:
    overlap = [
        candidate
        for candidate in candidate_records
        if _text_overlap(str(candidate.get("evidence_text") or ""), evidence)
    ]
    return overlap or candidate_records


def _text_overlap(candidate_evidence: str, evidence: str) -> bool:
    candidate_words = set(re.findall(r"[a-z0-9]+", candidate_evidence.lower()))
    evidence_words = set(re.findall(r"[a-z0-9]+", evidence.lower()))
    return len(candidate_words & evidence_words) >= 4


def _dedupe_month_rows(
    rows: list[tuple[int, int, int, int]],
) -> list[tuple[int, int, int, int]]:
    deduped: list[tuple[int, int, int, int]] = []
    seen: set[tuple[int, int, int]] = set()
    for row in rows:
        key = (row[0], row[1], row[2] // 20)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _rate_label(numerator: int, denominator: int, unit: str) -> str:
    if denominator == 1:
        return f"{numerator} per {unit}"
    return f"{numerator} per {denominator} {unit}"


def _simplify(numerator: int, denominator: int) -> tuple[int, int]:
    divisor = math.gcd(numerator, denominator)
    return numerator // divisor, denominator // divisor


def _inclusive_month_span(first_month: int, last_month: int) -> int:
    if last_month >= first_month:
        return last_month - first_month + 1
    return 12 - first_month + 1 + last_month


def _month_tally_window(months: list[int]) -> int:
    if not months:
        return 0
    if len(months) >= 2 and all(
        earlier >= later for earlier, later in zip(months, months[1:])
    ):
        same_year_span = max(months) - min(months) + 1
        wrapped_span = _inclusive_month_span(months[0], months[-1])
        return min(same_year_span, wrapped_span)
    return _inclusive_month_span(months[0], months[-1])


def _month_number(month: str) -> int:
    return _MONTHS[month.strip().lower()[:3]]


def _quantity_to_int(value: str | None) -> int:
    if value is None:
        return 1
    normalized = value.strip().lower()
    if normalized.isdigit():
        return int(normalized)
    return _NUMBER_WORDS.get(normalized, 1)


def _seizure_context(text: str) -> bool:
    return bool(
        re.search(
            r"\b(seizures?|events?|episodes?|spells?|jerks?|convulsions?|gtc|tonic|clonic)\b",
            text,
            flags=re.IGNORECASE,
        )
    )


def _span_text(text: str, start: int, end: int) -> str:
    left = text.rfind(".", 0, start)
    right = text.find(".", end)
    if left == -1:
        left = max(0, start - 120)
    else:
        left += 1
    if right == -1:
        right = min(len(text), end + 120)
    return " ".join(text[left:right].split())


__all__ = [
    "ELIGIBLE_POLICY_CLASSES",
    "GAN_S0_AGGREGATION_CONSTRUCTOR_PRIMITIVE_ID",
    "GanAggregationConstructedOption",
    "construct_gan_s0_aggregation_options",
]
