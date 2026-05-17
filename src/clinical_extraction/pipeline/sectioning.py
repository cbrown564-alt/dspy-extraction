from __future__ import annotations

import re
from dataclasses import dataclass

from clinical_extraction.schemas import EvidenceSpan

HEADING_RE = re.compile(
    r"^(?P<heading>[A-Za-z][A-Za-z /_-]{1,60})(?P<separator>:)?[ \t]*(?P<body>.*)$"
)

SECTION_ALIASES = {
    "diagnosis": "diagnosis",
    "diagnoses": "diagnosis",
    "impression": "diagnosis",
    "seizure": "seizures",
    "seizures": "seizures",
    "seizure frequency": "seizure_frequency",
    "frequency": "seizure_frequency",
    "medication": "medication",
    "medications": "medication",
    "current medication": "medication",
    "anti seizure medication": "medication",
    "asm": "medication",
    "history": "history",
    "past history": "history",
    "investigation": "investigations",
    "investigations": "investigations",
    "plan": "plan",
}

FIELD_KEYWORDS = {
    "seizure_frequency_number": (
        "seizure frequency",
        "seizure",
        "seizures",
        "fit",
        "fits",
        "episode",
        "episodes",
    ),
    "diagnosis": ("diagnosis", "diagnoses", "impression", "epilepsy"),
    "seizure_type": ("seizure", "seizures", "focal", "generalised", "tonic"),
    "medication": ("medication", "medications", "lamotrigine", "levetiracetam", "asm"),
    "investigation": ("mri", "eeg", "investigation", "investigations"),
    "history": ("history", "previous", "since", "childhood"),
}


@dataclass(frozen=True)
class NoteSection:
    title: str
    text: str
    start: int
    end: int
    heading: str | None = None


def section_note(note_text: str) -> list[NoteSection]:
    """Split a note into deterministic, offset-preserving sections."""

    line_spans = list(_iter_line_spans(note_text))
    headings: list[tuple[int, int, str]] = []
    for start, _end, line in line_spans:
        heading = _heading_for_line(line)
        if heading is not None:
            headings.append((start, _end, heading))

    if not headings:
        return [
            NoteSection(
                title="document",
                text=note_text,
                start=0,
                end=len(note_text),
                heading=None,
            )
        ]

    sections: list[NoteSection] = []
    first_heading_start = headings[0][0]
    if first_heading_start > 0:
        sections.append(
            NoteSection(
                title="document",
                text=note_text[:first_heading_start],
                start=0,
                end=first_heading_start,
                heading=None,
            )
        )

    for index, (start, _line_end, heading) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(note_text)
        sections.append(
            NoteSection(
                title=_canonical_title(heading),
                text=note_text[start:end],
                start=start,
                end=end,
                heading=heading,
            )
        )
    return sections


def select_context(
    note_text: str,
    *,
    target_field: str,
    max_sections: int = 3,
) -> list[EvidenceSpan]:
    """Return section-aware context spans for a target extraction field."""

    keywords = FIELD_KEYWORDS.get(target_field, _generic_keywords(target_field))
    scored: list[tuple[int, int, NoteSection]] = []
    for index, section in enumerate(section_note(note_text)):
        haystack = f"{section.title} {section.text}".lower()
        score = sum(keyword in haystack for keyword in keywords)
        if score:
            scored.append((score, -index, section))

    selected = [
        section
        for _score, _index, section in sorted(scored, reverse=True)[:max_sections]
    ]
    return [
        EvidenceSpan(
            text=section.text,
            start=section.start,
            end=section.end,
            section=section.title,
        )
        for section in selected
    ]


def _iter_line_spans(note_text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    start = 0
    for line in note_text.splitlines(keepends=True):
        end = start + len(line)
        spans.append((start, end, line))
        start = end
    if start < len(note_text):
        spans.append((start, len(note_text), note_text[start:]))
    return spans


def _heading_for_line(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None
    match = HEADING_RE.match(stripped)
    if match is None:
        return None
    heading = match.group("heading").strip()
    body = match.group("body").strip()
    has_separator = match.group("separator") == ":"
    canonical = _canonical_title(heading)
    if canonical == "document":
        return None
    if has_separator:
        return heading
    if body:
        return None
    if not _is_known_heading(heading):
        return None
    return heading


def _canonical_title(heading: str) -> str:
    normalized = re.sub(r"\s+", " ", heading.strip().lower().replace("-", " "))
    return SECTION_ALIASES.get(normalized, normalized.replace(" ", "_"))


def _is_known_heading(heading: str) -> bool:
    normalized = re.sub(r"\s+", " ", heading.strip().lower().replace("-", " "))
    return normalized in SECTION_ALIASES


def _generic_keywords(target_field: str) -> tuple[str, ...]:
    return tuple(part for part in re.split(r"[_\W]+", target_field.lower()) if part)
