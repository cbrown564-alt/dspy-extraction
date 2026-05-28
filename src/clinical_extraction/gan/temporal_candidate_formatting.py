"""Prompt formatting and presentation routing for Gan temporal candidates."""

from __future__ import annotations

import json
from typing import Literal

from clinical_extraction.gan.temporal_candidate_records import (
    GanTemporalFrequencyCandidate,
    temporal_candidate_to_dict,
)

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


__all__ = [
    "IMPLEMENTATION_VARIANT_TO_PRESENTATION",
    "TemporalCandidatePresentation",
    "format_temporal_candidates_for_prompt",
    "presentation_for_implementation_variant",
]
