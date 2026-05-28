from __future__ import annotations

from clinical_extraction.exect.frequency_primitives import (
    build_exect_frequency_candidate_payloads,
    build_exect_frequency_pre_vocab_labels,
    exect_frequency_benchmark_bridge,
    filter_gan_temporal_candidate_for_exect,
    note_has_exect_frequency_support,
    recover_exect_frequency_benchmark_values,
    recover_exect_frequency_benchmark_values_with_post_merge,
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


def test_note_has_exect_frequency_support_detects_quantified_rates():
    assert note_has_exect_frequency_support("One seizure every three weeks.")
    assert not note_has_exect_frequency_support("Current medication: lamotrigine.")


def test_exect_frequency_post_merge_abstains_when_note_has_no_frequency_support():
    recovered, flags = recover_exect_frequency_benchmark_values_with_post_merge(
        ["seizure free"],
        "Current medication: lamotrigine 75mg bd.",
    )

    assert recovered == []
    assert "s4_bridge:spurious_seizure_free_removed" in flags


def test_exect_frequency_post_merge_keeps_model_labels_when_note_parser_misses():
    recovered, flags = recover_exect_frequency_benchmark_values_with_post_merge(
        ["15 per 4 month"],
        "Frequency is about fifteen per four months on average.",
    )

    assert "15 per 4 month" in recovered
    assert "s4_bridge:spurious_seizure_free_removed" not in flags


def test_exect_frequency_post_merge_adds_note_anchored_quantified_rates():
    recovered, flags = recover_exect_frequency_benchmark_values_with_post_merge(
        [],
        "He has about one focal seizure every three weeks.",
    )

    assert recovered == ["1 per 3 week"]
    assert "s4_bridge:note_anchored_frequency_merged" in flags


def test_exect_frequency_post_merge_unions_model_and_note_labels():
    recovered, flags = recover_exect_frequency_benchmark_values_with_post_merge(
        ["1 per 3 week"],
        (
            "He has about one focal seizure every three weeks and the frequency "
            "has increased."
        ),
    )

    assert recovered == ["1 per 3 week", "frequency increased"]
    assert "s4_bridge:frequency_co_label_augmented" in flags or (
        "s4_bridge:note_anchored_frequency_merged" in flags
    )


def test_e6_frequency_candidate_recall_improvements():
    # 1. Section-list adverbial rates
    labels_weekly = build_exect_frequency_pre_vocab_labels("Myoclonic jerks weekly.")
    assert "1 per 1 week" in labels_weekly

    labels_twice_weekly = build_exect_frequency_pre_vocab_labels("He gets jerks twice weekly.")
    assert "2 per 1 week" in labels_twice_weekly

    labels_three_monthly = build_exect_frequency_pre_vocab_labels("Seizures occur three times monthly.")
    assert "3 per 1 month" in labels_three_monthly

    # 2. Extended quantified rates
    labels_once_month = build_exect_frequency_pre_vocab_labels("About once a month she has a seizure.")
    assert "1 per 1 month" in labels_once_month

    labels_twice_week = build_exect_frequency_pre_vocab_labels("She gets focal seizures twice a week.")
    assert "2 per 1 week" in labels_twice_week

    labels_every_3_weeks = build_exect_frequency_pre_vocab_labels("Focal seizures with altered awareness every 3 weeks.")
    assert "1 per 3 week" in labels_every_3_weeks

    # 3. Zero-rate windows
    labels_several_years = build_exect_frequency_pre_vocab_labels("He has not had any generalised convulsions now for several years.")
    assert "0 per 3 year" in labels_several_years

    labels_free_5_years = build_exect_frequency_pre_vocab_labels("He has been seizure free for 5 years.")
    assert "0 per 5 year" in labels_free_5_years

    labels_no_sz_2_years = build_exect_frequency_pre_vocab_labels("No seizures in the last 2 years.")
    assert "0 per 2 year" in labels_no_sz_2_years

    labels_not_happen_5_years = build_exect_frequency_pre_vocab_labels("They have not happen now for at least 5 years.")
    assert "0 per 5 year" in labels_not_happen_5_years

    # 4. Qualitative frequency same cues
    labels_well_controlled = build_exect_frequency_pre_vocab_labels("Richard's seizures remain well controlled.")
    assert "frequency same" in labels_well_controlled

    labels_remains_same = build_exect_frequency_pre_vocab_labels("Her seizure frequency remains the same.")
    assert "frequency same" in labels_remains_same

    labels_no_change = build_exect_frequency_pre_vocab_labels("There has been no change in her seizure frequency.")
    assert "frequency same" in labels_no_change

    # 5. Alternative seizure free since year phrasings
    labels_last_event = build_exect_frequency_pre_vocab_labels("last event 2015")
    assert "seizure free since 2015" in labels_last_event

    labels_last_sz_nov = build_exect_frequency_pre_vocab_labels("last seizure was November 2015")
    assert "seizure free since 2015" in labels_last_sz_nov

    # 6. Seizure-free word boundary and negation/return guards
    labels_returned = build_exect_frequency_pre_vocab_labels("after the period of seizure freedom the seizures have returned")
    assert "seizure free" not in labels_returned
    assert "frequency increased" in labels_returned

    labels_no_more = build_exect_frequency_pre_vocab_labels("since February 6th he has not had any more seizures.")
    assert "seizure free" in labels_no_more

    # 7. Breakthrough after period
    labels_breakthrough = build_exect_frequency_pre_vocab_labels("After around 6 months without having seizures he had a cluster of seizures.")
    assert "1 per 6 month" in labels_breakthrough

    # 8. Date/month ago zero-rate mappings to seizure free
    labels_ago = build_exect_frequency_pre_vocab_labels("Her seizure was about 2 months ago.")
    assert "0 per 2 month" in labels_ago
    assert "seizure free" in labels_ago

    labels_last_occurred = build_exect_frequency_pre_vocab_labels("the last occurred three years ago.")
    assert "0 per 3 year" in labels_last_occurred

    # 9. Last seizure date to seizure free
    labels_date = build_exect_frequency_pre_vocab_labels("last seizure was on the 15th April")
    assert "seizure free" in labels_date

    # 10. Qualitative cues expansion
    labels_increasing = build_exect_frequency_pre_vocab_labels("Many thanks for referring for increasing seizures.")
    assert "frequency increased" in labels_increasing

    labels_more_frequent = build_exect_frequency_pre_vocab_labels("Huw has had more frequent seizures.")
    assert "frequency increased" in labels_more_frequent

    labels_worse_year = build_exect_frequency_pre_vocab_labels("seizures have been worse in the last year.")
    assert "frequency increased" in labels_worse_year
