"""Shared lexical and date parsing helpers for Gan temporal candidates."""

from __future__ import annotations

import re
from datetime import date

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

NUMBER_WORDS = {
    "a": "1",
    "an": "1",
    "one": "1",
    "single": "1",
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
    "few": "multiple",
    "several": "multiple",
    "multiple": "multiple",
    "many": "multiple",
}

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


def months_between_month_year(clinic_date: date, month: int, year: int) -> int:
    return max(1, (clinic_date.year - year) * 12 + (clinic_date.month - month))


def months_between_dates(clinic_date: date, start_date: date) -> int:
    return max(1, (clinic_date.year - start_date.year) * 12 + clinic_date.month - start_date.month)


def clinic_date(note_text: str) -> date | None:
    match = re.search(
        rf"(?:Clinic Date|Date):\s*(?P<day>\d{{1,2}}) "
        rf"(?P<month>{MONTH_PATTERN}) (?P<year>\d{{4}})",
        note_text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    return date(
        int(match.group("year")),
        MONTHS[match.group("month").lower()],
        int(match.group("day")),
    )


def month_number(month_name: str) -> int:
    name = month_name.lower().strip()[:3]
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
    if name in short_months:
        return short_months[name]
    return MONTHS[month_name.lower()]


def count_phrase_to_label(count_phrase: str) -> str:
    normalized = count_phrase.lower().strip()
    if normalized == "two to three":
        return "2 to 3"
    if normalized == "two":
        return "2"
    if normalized == "three":
        return "3"
    raise ValueError(f"Unsupported count phrase: {count_phrase!r}")


def number_token_to_label(token: str) -> str:
    normalized = token.lower().strip()
    if normalized in ("a", "an", "single", "one"):
        return "1"
    if normalized in NUMBER_WORDS:
        return NUMBER_WORDS[normalized]
    return normalized


def count_range_text_to_label(count_text: str) -> str:
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
        return f"{number_token_to_label(parts[0])} to {number_token_to_label(parts[1])}"
    return number_token_to_label(normalized)


def simple_rate_label(event_count: str, window_count: int, window_unit: str) -> str:
    if window_count == 1:
        return f"{event_count} per {window_unit}"
    return f"{event_count} per {window_count} {window_unit}"


__all__ = [
    "EVENT_NOUN_PATTERN",
    "MONTHS",
    "MONTH_PATTERN",
    "NUMBER_WORDS",
    "PERIOD_UNIT_PATTERN",
    "QUANTITY_RANGE_PATTERN",
    "QUANTITY_TOKEN_PATTERN",
    "SHORT_MONTH_PATTERN",
    "clinic_date",
    "count_phrase_to_label",
    "count_range_text_to_label",
    "month_number",
    "months_between_dates",
    "months_between_month_year",
    "number_token_to_label",
    "simple_rate_label",
]
