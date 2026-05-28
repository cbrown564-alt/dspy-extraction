"""Typed family-span payloads for ExECT document-geometry experiments."""

from __future__ import annotations

import re
from typing import Iterable

from clinical_extraction.primitives import PrimitiveCandidate

EXECT_FAMILY_SPANS_PRIMITIVE_ID = "exect.sections.family_spans.v1"

FAMILY_ORDER = (
    "diagnosis_problem",
    "seizure",
    "medication",
    "investigation",
    "history_background",
    "frequency",
    "plan_follow_up",
)

_HEADING_FAMILIES = {
    "diagnosis": ("diagnosis_problem",),
    "diagnoses": ("diagnosis_problem",),
    "impression": ("diagnosis_problem",),
    "problem": ("diagnosis_problem", "history_background"),
    "problems": ("diagnosis_problem", "history_background"),
    "seizure": ("seizure",),
    "seizures": ("seizure",),
    "seizure type": ("seizure",),
    "seizure types": ("seizure",),
    "seizure frequency": ("frequency",),
    "frequency": ("frequency",),
    "seizure type and frequency": ("seizure", "frequency"),
    "medication": ("medication",),
    "medications": ("medication",),
    "current medication": ("medication",),
    "current anti epileptic medication": ("medication",),
    "current anti seizure medication": ("medication",),
    "anti seizure medication": ("medication",),
    "asm": ("medication",),
    "investigation": ("investigation",),
    "investigations": ("investigation",),
    "history": ("history_background",),
    "past history": ("history_background",),
    "background": ("history_background",),
    "family history": ("history_background",),
    "social history": ("history_background",),
    "plan": ("plan_follow_up",),
    "follow up": ("plan_follow_up",),
    "follow-up": ("plan_follow_up",),
    "outcome": ("plan_follow_up",),
}

_FAMILY_KEYWORDS = {
    "diagnosis_problem": (
        "diagnosis",
        "diagnoses",
        "impression",
        "problem",
        "epilepsy",
        "jme",
        "focal epilepsy",
        "generalized epilepsy",
        "generalised epilepsy",
    ),
    "seizure": (
        "seizure",
        "seizures",
        "gtcs",
        "tonic clonic",
        "tonic-clonic",
        "myoclonic",
        "absence",
        "absences",
        "focal",
        "aura",
        "convulsion",
        "convulsive",
        "attack",
    ),
    "medication": (
        "medication",
        "medications",
        "anti-epileptic",
        "anti epileptic",
        "asm",
        "lamotrigine",
        "lamictal",
        "levetiracetam",
        "keppra",
        "sodium valproate",
        "epilim",
        "carbamazepine",
        "topiramate",
        "zonisamide",
        "clobazam",
        "lacosamide",
        "brivaracetam",
        "oxcarbazepine",
        "phenytoin",
        "phenobarbital",
        "eslicarbazepine",
        "mg",
        " bd",
        " od",
    ),
    "investigation": (
        "investigation",
        "investigations",
        "eeg",
        "mri",
        "ct",
        "scan",
    ),
    "history_background": (
        "history",
        "previous",
        "previously",
        "past",
        "childhood",
        "birth",
        "born",
        "development",
        "family history",
        "stroke",
        "cva",
        "meningioma",
        "meningitis",
        "head injury",
        "anxiety",
        "depression",
        "arachnoid",
        "cyst",
        "learning difficulties",
        "learning disability",
        "brain atrophy",
        "cortical dysplasia",
        "hydrocephalus",
        "dementia",
        "trisomy",
        "migraine",
        "migraines",
        "lobe damage",
        "lesion",
        "malformation",
        "ischaemic",
        "ischemic",
        "heart disease",
        "diabetes",
        "dissociative",
        "perinatal",
        "trauma",
        "injury",
        "gliosis",
        "haemorrhage",
        "hemorrhage",
        "haemorhhage",
        "loss of consciousness",
        "déjà vu",
        "deja vu",
        "hypertension",
        "hypertensions",
        "diagnosed",
        "seizres",
        "sseizure",
        "sseizures",
    ),
    "frequency": (
        "seizure frequency",
        "frequency",
        "per week",
        "per month",
        "per day",
        "per year",
        "every",
        "once",
        "twice",
        "thrice",
        "seizure free",
        "seizure-free",
        "no seizures",
        "increased",
        "decreased",
        "infrequent",
        "occasional",
        "improved",
        "well controlled",
        "most recent seizure",
        "last seizure",
        "seizure chart",
    ),
    "plan_follow_up": (
        "plan",
        "review",
        "follow up",
        "follow-up",
        "appointment",
        "recommend",
        "suggest",
        "start",
        "increase",
        "reduce",
        "taper",
        "prescribe",
    ),
}


def build_exect_family_span_payloads(note_text: str) -> list[PrimitiveCandidate]:
    """Return line-anchored ExECT family spans as soft deterministic hints."""

    spans: list[PrimitiveCandidate] = []
    seen: set[tuple[str, int, int]] = set()
    line_items: list[tuple[int, int, str, list[tuple[str, str]]]] = []
    for start, end, line in _iter_line_spans(note_text):
        trimmed = line.strip()
        if not trimmed:
            continue
        span_start = start + (len(line) - len(line.lstrip()))
        span_end = start + len(line.rstrip())
        families = _families_for_line(trimmed)
        line_items.append((span_start, span_end, note_text[span_start:span_end], families))
        for family, rule_name in families:
            _append_span(
                spans,
                seen,
                note_text=note_text,
                family=family,
                start=span_start,
                end=span_end,
                rule_name=rule_name,
            )
    _append_contiguous_family_blocks(spans, seen, note_text=note_text, lines=line_items)
    return sorted(spans, key=lambda item: (item.start or 0, str(item.normalized_value)))


def family_span_context(
    note_text: str,
    *,
    families: Iterable[str],
) -> str:
    """Render family-filtered note context for no-model prompt-substrate audits."""

    selected = set(families)
    ranges: list[tuple[int, int, set[str]]] = []
    for span in build_exect_family_span_payloads(note_text):
        family = str(span.normalized_value)
        if family not in selected:
            continue
        if span.start is None or span.end is None:
            continue
        ranges.append((span.start, span.end, {family}))

    merged = _merge_ranges(ranges)
    lines: list[str] = []
    for _start, _end, families_for_range in merged:
        span_families = [
            family
            for family in FAMILY_ORDER
            if family in families_for_range
        ]
        lines.append(f"[{','.join(span_families)}] {note_text[_start:_end].strip()}")
    return "\n".join(lines)


def _families_for_line(line: str) -> list[tuple[str, str]]:
    normalized = _normalize_heading(line)
    families: dict[str, str] = {}
    for heading, heading_families in _HEADING_FAMILIES.items():
        if normalized == heading or normalized.startswith(f"{heading} "):
            for family in heading_families:
                families[family] = "family_span_heading"

    line_lower = line.lower()
    for family, keywords in _FAMILY_KEYWORDS.items():
        if family in families:
            continue
        if any(keyword in line_lower for keyword in keywords):
            families[family] = "family_span_keyword"
    if "frequency" not in families and _looks_like_frequency_line(line_lower):
        families["frequency"] = "family_span_frequency_pattern"
    if "history_background" not in families and _looks_like_clinical_history_line(
        line_lower
    ):
        families["history_background"] = "family_span_history_pattern"

    return [
        (family, families[family])
        for family in FAMILY_ORDER
        if family in families
    ]


def _normalize_heading(line: str) -> str:
    head = line.split(":", 1)[0]
    head = re.sub(r"\s+", " ", head.strip().lower().replace("-", " "))
    return head.replace("_", " ")


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


def _append_span(
    spans: list[PrimitiveCandidate],
    seen: set[tuple[str, int, int]],
    *,
    note_text: str,
    family: str,
    start: int,
    end: int,
    rule_name: str,
) -> None:
    key = (family, start, end)
    if key in seen or start >= end:
        return
    seen.add(key)
    source_span_text = note_text[start:end]
    spans.append(
        PrimitiveCandidate(
            primitive_id=EXECT_FAMILY_SPANS_PRIMITIVE_ID,
            dataset="exect_v2",
            field_family="multi_family",
            raw_text=source_span_text.strip(),
            normalized_value=family,
            benchmark_value=None,
            source_span_text=source_span_text,
            start=start,
            end=end,
            rule_name=rule_name,
            confidence=1.0,
            caveats=[
                "Family spans are document-geometry hints, not benchmark labels.",
                "Section filtering requires full-note baselines before promotion.",
            ],
            metadata={
                "family": family,
                "families": [family],
                "section_role": family,
            },
        )
    )


def _append_contiguous_family_blocks(
    spans: list[PrimitiveCandidate],
    seen: set[tuple[str, int, int]],
    *,
    note_text: str,
    lines: list[tuple[int, int, str, list[tuple[str, str]]]],
) -> None:
    for family in FAMILY_ORDER:
        block_start: int | None = None
        block_end: int | None = None
        block_line_count = 0
        for start, end, _text, families in lines:
            line_has_family = any(item_family == family for item_family, _ in families)
            if line_has_family:
                if block_end is not None and start > block_end + 1:
                    if block_start is not None and block_line_count > 1:
                        _append_span(
                            spans,
                            seen,
                            note_text=note_text,
                            family=family,
                            start=block_start,
                            end=block_end,
                            rule_name="family_span_contiguous_block",
                        )
                    block_start = start
                    block_line_count = 1
                elif block_start is None:
                    block_start = start
                    block_line_count = 1
                else:
                    block_line_count += 1
                block_end = end
                continue
            if block_start is not None and block_end is not None and block_line_count > 1:
                _append_span(
                    spans,
                    seen,
                    note_text=note_text,
                    family=family,
                    start=block_start,
                    end=block_end,
                    rule_name="family_span_contiguous_block",
                )
            block_start = None
            block_end = None
            block_line_count = 0
        if block_start is not None and block_end is not None and block_line_count > 1:
            _append_span(
                spans,
                seen,
                note_text=note_text,
                family=family,
                start=block_start,
                end=block_end,
                rule_name="family_span_contiguous_block",
            )


def _merge_ranges(
    ranges: list[tuple[int, int, set[str]]],
) -> list[tuple[int, int, set[str]]]:
    if not ranges:
        return []
    sorted_ranges = sorted(ranges, key=lambda item: (item[0], item[1]))
    merged: list[tuple[int, int, set[str]]] = []
    current_start, current_end, current_families = sorted_ranges[0]
    for start, end, families in sorted_ranges[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
            current_families.update(families)
            continue
        merged.append((current_start, current_end, set(current_families)))
        current_start, current_end, current_families = start, end, set(families)
    merged.append((current_start, current_end, set(current_families)))
    return merged


def _looks_like_frequency_line(line_lower: str) -> bool:
    seizure_terms = r"(?:seizures?|fits?|episodes?|events?|jerks|absences|convulsions?)"
    temporal_terms = (
        r"(?:over|during|within|for|every|per|weekly|daily|monthly|yearly|"
        r"annually|last event|last one|ago|several times|worse|more frequent)"
    )
    return bool(
        re.search(rf"\b\d+\s+{seizure_terms}\b", line_lower)
        or re.search(rf"\b{seizure_terms}\b.{{0,100}}\b{temporal_terms}\b", line_lower)
        or re.search(rf"\b{temporal_terms}\b.{{0,100}}\b{seizure_terms}\b", line_lower)
    )


def _looks_like_clinical_history_line(line_lower: str) -> bool:
    if any(marker in line_lower for marker in ("previous", "previously", "history")):
        return True
    return bool(
        re.search(
            r"\b(?:born|childhood|stroke|cva|meningioma|meningitis|"
            r"head injury|anxiety|depression|arachnoid|cyst|"
            r"learning difficult(?:y|ies)|learning disability|brain atrophy|"
            r"cortical dysplasia|hydrocephalus|dementia|trisomy|"
            r"migraine|migraines|lobe damage|lesion|malformation|"
            r"ischaemic|ischemic|heart disease|diabetes|dissociative|"
            r"perinatal|trauma|injury|gliosis|haemorrhage|hemorrhage|"
            r"haemorhhage|loss of consciousness|déjà vu|deja vu|"
            r"hypertensions?|diagnosed|"
            r"seizres|sseizures?)\b",
            line_lower,
        )
    )


__all__ = [
    "EXECT_FAMILY_SPANS_PRIMITIVE_ID",
    "FAMILY_ORDER",
    "build_exect_family_span_payloads",
    "family_span_context",
]
