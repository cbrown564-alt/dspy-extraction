"""Structured seizure event tables for Gan temporal-candidate B2 scaffolding."""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import Field, ValidationError

from clinical_extraction.schemas import FrozenModel

SeizureEventRole = Literal["seizure_event", "cluster", "aura", "other"]


class GanSeizureEventMention(FrozenModel):
    """One auditable seizure or cluster mention from the note."""

    raw_phrase: str
    evidence_text: str
    event_count: str | None = None
    window_phrase: str | None = None
    event_date_phrase: str | None = None
    seizure_type: str | None = None
    role: SeizureEventRole = "seizure_event"


class GanSeizureFreeInterval(FrozenModel):
    """A seizure-free interval kept separate from counted seizure events."""

    raw_phrase: str
    evidence_text: str
    duration_phrase: str | None = None
    qualifies_for_seizure_free_label: bool = False


class GanTemporalEventTable(FrozenModel):
    """Model-extracted event table before final Gan label selection."""

    events: list[GanSeizureEventMention] = Field(default_factory=list)
    seizure_free_intervals: list[GanSeizureFreeInterval] = Field(default_factory=list)
    selected_window_note: str | None = None


def parse_temporal_event_table_json(
    payload: str | dict[str, Any] | None,
    *,
    note_text: str | None = None,
) -> GanTemporalEventTable:
    """Parse and validate a model event-table payload.

    Returns an empty table when parsing fails. When ``note_text`` is provided,
    drops rows whose ``evidence_text`` is not an exact contiguous substring.
    """

    if payload is None:
        return GanTemporalEventTable()
    if isinstance(payload, str):
        stripped = payload.strip()
        if not stripped or stripped.lower() in {"none", "null"}:
            return GanTemporalEventTable()
        try:
            raw = json.loads(stripped)
        except json.JSONDecodeError:
            return GanTemporalEventTable()
    else:
        raw = payload

    try:
        table = GanTemporalEventTable.model_validate(raw)
    except ValidationError:
        return GanTemporalEventTable()

    if note_text is None:
        return table

    return GanTemporalEventTable(
        events=[
            event
            for event in table.events
            if event.evidence_text and event.evidence_text in note_text
        ],
        seizure_free_intervals=[
            interval
            for interval in table.seizure_free_intervals
            if interval.evidence_text and interval.evidence_text in note_text
        ],
        selected_window_note=table.selected_window_note,
    )


def temporal_event_table_to_dict(table: GanTemporalEventTable) -> dict[str, Any]:
    """Serialize an event table for run artifacts and analyzer output."""

    return table.model_dump()


def format_temporal_event_table_for_prompt(table: GanTemporalEventTable) -> str:
    """Format a structured event table for verifier/repair model input."""

    if not table.events and not table.seizure_free_intervals:
        return "No structured temporal event table rows were extracted from this note."

    lines = ["Structured temporal event table (diagnostic hints only):"]
    for index, event in enumerate(table.events, start=1):
        lines.append(
            f"{index}. role={event.role}; raw_phrase={event.raw_phrase!r}; "
            f"event_count={event.event_count!r}; window_phrase={event.window_phrase!r}; "
            f"event_date_phrase={event.event_date_phrase!r}; "
            f"seizure_type={event.seizure_type!r}; "
            f"evidence_text={event.evidence_text!r}"
        )
    for index, interval in enumerate(table.seizure_free_intervals, start=1):
        lines.append(
            f"SF{index}. raw_phrase={interval.raw_phrase!r}; "
            f"duration_phrase={interval.duration_phrase!r}; "
            f"qualifies_for_seizure_free_label={interval.qualifies_for_seizure_free_label}; "
            f"evidence_text={interval.evidence_text!r}"
        )
    if table.selected_window_note:
        lines.append(f"selected_window_note={table.selected_window_note!r}")
    return "\n".join(lines)
