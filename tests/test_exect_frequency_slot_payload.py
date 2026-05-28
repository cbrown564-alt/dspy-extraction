from __future__ import annotations

from clinical_extraction.exect.slot_payload import (
    SLOT_TYPE_QUALITATIVE,
    SLOT_TYPE_QUANTIFIED,
    SLOT_TYPE_SEIZURE_FREE,
    SLOT_TYPE_ZERO_RATE,
    build_exect_frequency_slot_payloads,
    classify_exect_frequency_slot_type,
    format_exect_frequency_slot_payload_for_prompt,
)
from clinical_extraction.exect.frequency_payload import (
    recover_exect_frequency_benchmark_values_with_multi_label_retention,
)


def test_classify_exect_frequency_slot_types():
    assert classify_exect_frequency_slot_type("1 per 3 week") == SLOT_TYPE_QUANTIFIED
    assert classify_exect_frequency_slot_type("0 per 5 year") == SLOT_TYPE_ZERO_RATE
    assert classify_exect_frequency_slot_type("frequency increased") == SLOT_TYPE_QUALITATIVE
    assert classify_exect_frequency_slot_type("seizure free") == SLOT_TYPE_SEIZURE_FREE
    assert (
        classify_exect_frequency_slot_type("seizure free since 2015")
        == SLOT_TYPE_SEIZURE_FREE
    )


def test_build_exect_frequency_slot_payloads_groups_multi_label_block():
    note = (
        "He has about one focal seizure every three weeks and the frequency has increased."
    )
    payloads = build_exect_frequency_slot_payloads(note)

    assert {payload.benchmark_label for payload in payloads} == {
        "1 per 3 week",
        "frequency increased",
    }
    assert all(payload.multi_label_group == "rate_block" for payload in payloads)
    assert payloads[0].slot_type == SLOT_TYPE_QUANTIFIED
    assert payloads[0].count == "1"
    assert payloads[0].period_count == "3"
    assert payloads[0].period_unit == "week"


def test_format_exect_frequency_slot_payload_injects_table_before_note():
    note = "One seizure every three weeks."
    formatted = format_exect_frequency_slot_payload_for_prompt(note)

    assert "structured slots" in formatted.lower()
    assert "1 per 3 week" in formatted
    assert formatted.endswith(note)
    assert "---" in formatted


def test_multi_label_retention_fills_partial_block_when_model_emits_one_label():
    recovered, flags = recover_exect_frequency_benchmark_values_with_multi_label_retention(
        ["1 per 3 week"],
        (
            "He has about one focal seizure every three weeks and the frequency "
            "has increased."
        ),
    )

    assert recovered == ["1 per 3 week", "frequency increased"]
    assert any(
        flag in flags
        for flag in (
            "s4_bridge:multi_label_slot_filled",
            "s4_bridge:frequency_co_label_multi_label_retained",
            "s4_bridge:frequency_co_label_augmented",
        )
    )


def test_multi_label_retention_does_not_fill_when_model_abstains():
    recovered, flags = recover_exect_frequency_benchmark_values_with_multi_label_retention(
        [],
        "He has about one focal seizure every three weeks.",
    )

    assert recovered == []
    assert "s4_bridge:multi_label_slot_filled" not in flags
    assert "s4_bridge:note_anchored_frequency_merged" not in flags
