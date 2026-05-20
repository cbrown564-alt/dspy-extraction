import json

from clinical_extraction.gan.temporal_events import (
    GanTemporalEventTable,
    format_temporal_event_table_for_prompt,
    parse_temporal_event_table_json,
    temporal_event_table_to_dict,
)


def test_parse_temporal_event_table_json_accepts_valid_payload():
    note = (
        "He reports no seizures for nearly a year before a single breakthrough "
        "tonic seizure in March."
    )
    payload = {
        "events": [
            {
                "raw_phrase": "single breakthrough tonic seizure",
                "event_count": "1",
                "window_phrase": "after nearly a year seizure-free",
                "event_date_phrase": "March",
                "seizure_type": "tonic seizure",
                "evidence_text": "single breakthrough tonic seizure",
                "role": "seizure_event",
            }
        ],
        "seizure_free_intervals": [
            {
                "raw_phrase": "no seizures for nearly a year",
                "duration_phrase": "nearly a year",
                "evidence_text": "no seizures for nearly a year",
                "qualifies_for_seizure_free_label": True,
            }
        ],
        "selected_window_note": "Use the breakthrough event over the long quiet period.",
    }

    table = parse_temporal_event_table_json(payload, note_text=note)

    assert len(table.events) == 1
    assert table.events[0].event_count == "1"
    assert len(table.seizure_free_intervals) == 1
    assert table.selected_window_note.startswith("Use the breakthrough")


def test_parse_temporal_event_table_json_drops_unsupported_evidence():
    note = "Patient reports one seizure last month."
    payload = {
        "events": [
            {
                "raw_phrase": "supported",
                "evidence_text": "one seizure last month",
            },
            {
                "raw_phrase": "unsupported",
                "evidence_text": "invented quote",
            },
        ],
        "seizure_free_intervals": [],
    }

    table = parse_temporal_event_table_json(payload, note_text=note)

    assert len(table.events) == 1
    assert table.events[0].raw_phrase == "supported"


def test_parse_temporal_event_table_json_returns_empty_table_on_invalid_json():
    assert parse_temporal_event_table_json("{not json") == GanTemporalEventTable()
    assert parse_temporal_event_table_json(None) == GanTemporalEventTable()


def test_format_temporal_event_table_for_prompt_lists_rows():
    table = parse_temporal_event_table_json(
        {
            "events": [
                {
                    "raw_phrase": "two seizures in three months",
                    "event_count": "2",
                    "window_phrase": "in three months",
                    "evidence_text": "two seizures in three months",
                }
            ],
            "seizure_free_intervals": [],
        }
    )
    formatted = format_temporal_event_table_for_prompt(table)

    assert "Structured temporal event table" in formatted
    assert "two seizures in three months" in formatted
    assert temporal_event_table_to_dict(table)["events"][0]["event_count"] == "2"


def test_format_temporal_event_table_for_prompt_handles_empty_table():
    assert "No structured temporal event table rows" in (
        format_temporal_event_table_for_prompt(GanTemporalEventTable())
    )


def test_parse_temporal_event_table_json_accepts_json_string_payload():
    table = parse_temporal_event_table_json(
        json.dumps(
            {
                "events": [
                    {
                        "raw_phrase": "weekly clusters",
                        "evidence_text": "weekly clusters",
                        "role": "cluster",
                    }
                ],
                "seizure_free_intervals": [],
            }
        ),
        note_text="Patient reports weekly clusters.",
    )

    assert table.events[0].role == "cluster"
