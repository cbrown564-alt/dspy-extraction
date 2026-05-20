from __future__ import annotations

from clinical_extraction.exect.primitives import (
    build_exect_frequency_candidate_payloads,
    build_exect_frequency_pre_vocab_labels,
    exect_frequency_benchmark_bridge,
    filter_gan_temporal_candidate_for_exect,
    recover_exect_frequency_benchmark_values,
    repair_exect_frequency_surface,
)
from clinical_extraction.primitives import primitive_registry_by_id


def test_exect_frequency_rate_candidates_emit_quantified_and_change_labels():
    note = (
        "He has about one focal seizure every three weeks and the frequency has increased."
    )
    payloads = build_exect_frequency_candidate_payloads(note)

    assert {payload.benchmark_value for payload in payloads} == {
        "1 per 3 week",
        "frequency increased",
    }
    assert all(
        payload.primitive_id == "exect.frequency.rate_candidates.v1"
        for payload in payloads
    )
    assert all(
        "Gan monthly normalization" in " ".join(payload.caveats) for payload in payloads
    )


def test_exect_frequency_pre_vocab_labels_match_payload_benchmark_values():
    note = "About one seizure per week with decreased frequency and infrequent clusters."
    labels = build_exect_frequency_pre_vocab_labels(note)
    payloads = build_exect_frequency_candidate_payloads(note)

    assert "1 per 1 week" in labels
    assert "frequency decreased" in labels
    assert "infrequent" in labels
    assert {payload.benchmark_value for payload in payloads} == set(labels)


def test_exect_frequency_gan_temporal_filter_keeps_exect_templates_only():
    assert filter_gan_temporal_candidate_for_exect("multiple per week") is None
    assert (
        filter_gan_temporal_candidate_for_exect(
            "1 cluster per week, multiple per cluster"
        )
        is None
    )
    assert filter_gan_temporal_candidate_for_exect("1 per 3 week") == "1 per 3 week"
    assert filter_gan_temporal_candidate_for_exect("1 per month") == "1 per 1 month"


def test_exect_frequency_bridge_repairs_near_miss_quantified_rates():
    results = exect_frequency_benchmark_bridge(
        ["1 per day", "1 per month", "frequency increased"],
        note_text="One seizure per day and one per month; frequency has increased.",
    )

    assert [result.benchmark_value for result in results] == [
        "1 per 1 day",
        "1 per 1 month",
        "frequency increased",
    ]
    assert results[0].primitive_id == "exect.frequency.benchmark_bridge.v1"
    assert "s4_bridge:frequency_missing_time_period_inserted" in (
        results[0].metadata["bridge_flags"]
    )


def test_exect_frequency_bridge_strips_seizure_types_and_blocks_non_audited_periods():
    recovered, flags = recover_exect_frequency_benchmark_values(
        ["1 per 3 week", "focal seizures", "1 per 30 day"],
        "Seizure type focal seizures. One per three weeks.",
    )

    assert recovered == ["1 per 3 week"]
    assert "s4_bridge:seizure_type_removed_from_frequency" in flags
    assert "s4_bridge:non_audited_frequency_removed" in flags


def test_exect_frequency_bridge_adds_co_labels_when_note_supports_change_cues():
    results = exect_frequency_benchmark_bridge(
        ["1 per 3 week"],
        note_text=(
            "He has about one focal seizure every three weeks and the frequency has increased."
        ),
    )

    assert [result.benchmark_value for result in results] == [
        "1 per 3 week",
        "frequency increased",
    ]
    assert "s4_bridge:frequency_co_label_augmented" in results[0].metadata["bridge_flags"]


def test_exect_frequency_bridge_collapses_seizure_free_prose():
    repaired, flags = repair_exect_frequency_surface(
        "seizure free for more than five years"
    )

    assert repaired == "seizure free"
    assert "s4_bridge:seizure_free_prose_collapsed" in flags


def test_exect_frequency_bridge_documents_abstention_not_gan_no_reference():
    results = exect_frequency_benchmark_bridge(
        ["focal seizures"],
        note_text="Seizure type: focal seizures only.",
    )

    assert len(results) == 1
    assert results[0].benchmark_value is None
    assert results[0].metadata["abstention"]
    assert results[0].metadata["no_reference_policy"] == "empty_list_not_gan_no_reference"


def test_exect_frequency_registry_entries_are_implemented():
    registry = primitive_registry_by_id()
    rate = registry["exect.frequency.rate_candidates.v1"]
    bridge = registry["exect.frequency.benchmark_bridge.v1"]

    assert rate.status == "implemented"
    assert bridge.status == "implemented"
    assert rate.interleaving_positions == ["pre"]
    assert bridge.interleaving_positions == ["post"]
