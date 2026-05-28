"""Shared Gan temporal-candidate record helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GanTemporalFrequencyCandidate:
    """A candidate event/window interpretation for a canonical Gan label."""

    canonical_label: str
    event_count: str
    window_count: str
    window_unit: str
    evidence_text: str
    derivation: str


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
    return dedupe_temporal_frequency_candidates(parsed)


def merge_temporal_frequency_candidates(
    *candidate_lists: list[GanTemporalFrequencyCandidate],
) -> list[GanTemporalFrequencyCandidate]:
    """Merge multiple candidate lists with canonical-label deduplication."""

    merged: list[GanTemporalFrequencyCandidate] = []
    for candidates in candidate_lists:
        merged.extend(candidates)
    return dedupe_temporal_frequency_candidates(merged)


def dedupe_temporal_frequency_candidates(
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


__all__ = [
    "GanTemporalFrequencyCandidate",
    "dedupe_temporal_frequency_candidates",
    "merge_temporal_frequency_candidates",
    "parse_llm_temporal_candidates_json",
    "temporal_candidate_to_dict",
]
