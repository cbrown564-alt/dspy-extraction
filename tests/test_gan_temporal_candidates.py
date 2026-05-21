from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates,
    build_temporal_frequency_candidates_from_note,
    format_temporal_candidates_for_prompt,
    merge_temporal_frequency_candidates,
    parse_llm_temporal_candidates_json,
    temporal_candidate_to_dict,
)


def _record(record_id: str):
    return next(record for record in load_gan_records() if record.record_id == record_id)


def _candidate_labels(record_id: str) -> set[str]:
    return {
        candidate.canonical_label
        for candidate in build_temporal_frequency_candidates(_record(record_id))
    }


def test_temporal_candidates_represent_breakthrough_after_nearly_year_window():
    candidates = build_temporal_frequency_candidates(_record("gan_13123"))

    assert "1 per year" in {candidate.canonical_label for candidate in candidates}
    candidate = next(c for c in candidates if c.canonical_label == "1 per year")
    assert candidate.event_count == "1"
    assert candidate.window_count == "1"
    assert candidate.window_unit == "year"
    assert "no seizures for nearly a year" in candidate.evidence_text
    assert "tonic seizure" in candidate.evidence_text


def test_temporal_candidates_represent_two_dated_events_over_three_months():
    candidates = build_temporal_frequency_candidates(_record("gan_14485"))

    assert "2 per 3 month" in {candidate.canonical_label for candidate in candidates}
    candidate = next(c for c in candidates if c.canonical_label == "2 per 3 month")
    assert candidate.event_count == "2"
    assert candidate.window_count == "3"
    assert candidate.window_unit == "month"
    assert "April 2019" in candidate.evidence_text
    assert "July 2019" in candidate.evidence_text


def test_temporal_candidates_represent_last_episode_as_monthly_rate():
    candidates = build_temporal_frequency_candidates(_record("gan_14881"))

    assert "1 per month" in {candidate.canonical_label for candidate in candidates}
    candidate = next(c for c in candidates if c.canonical_label == "1 per month")
    assert candidate.event_count == "1"
    assert candidate.window_count == "1"
    assert candidate.window_unit == "month"
    assert "last episode was recorded on 26 February" in candidate.evidence_text


def test_temporal_candidates_represent_count_range_since_prior_date():
    candidates = build_temporal_frequency_candidates(_record("gan_15306"))

    assert "2 to 3 per 15 month" in {
        candidate.canonical_label for candidate in candidates
    }
    candidate = next(c for c in candidates if c.canonical_label == "2 to 3 per 15 month")
    assert candidate.event_count == "2 to 3"
    assert candidate.window_count == "15"
    assert candidate.window_unit == "month"
    assert "No further tonic-clonic seizures have occurred since 12/2020" in (
        candidate.evidence_text
    )


def test_temporal_candidates_do_not_make_short_seizure_free_gan_label():
    assert all(
        not label.startswith("seizure free for 4 month")
        for label in _candidate_labels("gan_11221")
    )


def test_build_temporal_frequency_candidates_from_note_matches_record_helper():
    record = _record("gan_15306")
    assert build_temporal_frequency_candidates_from_note(record.note_text) == (
        build_temporal_frequency_candidates(record)
    )


def test_format_temporal_candidates_for_prompt_lists_labels():
    record = _record("gan_13123")
    candidates = build_temporal_frequency_candidates(record)
    formatted = format_temporal_candidates_for_prompt(candidates)

    assert "1 per year" in formatted
    assert "Deterministic temporal frequency candidates" in formatted
    assert temporal_candidate_to_dict(candidates[0])["canonical_label"] == "1 per year"


def test_format_temporal_candidates_for_prompt_handles_empty_list():
    assert "No deterministic temporal frequency candidates" in (
        format_temporal_candidates_for_prompt([])
    )


def test_temporal_candidates_represent_ytd_documented_count_as_monthly_rate():
    candidates = build_temporal_frequency_candidates(_record("gan_12810"))

    assert "5 per 2 month" in {candidate.canonical_label for candidate in candidates}
    candidate = next(c for c in candidates if c.canonical_label == "5 per 2 month")
    assert candidate.event_count == "5"
    assert candidate.window_count == "2"
    assert candidate.window_unit == "month"
    assert "documented this year to date" in candidate.evidence_text


def test_temporal_candidates_represent_ytd_count_as_single_month_rate():
    candidates = build_temporal_frequency_candidates(_record("gan_12823"))

    assert "9 per month" in {candidate.canonical_label for candidate in candidates}
    candidate = next(c for c in candidates if c.canonical_label == "9 per month")
    assert candidate.event_count == "9"
    assert candidate.window_count == "1"
    assert candidate.window_unit == "month"


def test_temporal_candidates_represent_clusters_this_quarter():
    candidates = build_temporal_frequency_candidates(_record("gan_10052"))

    assert "4 cluster per 3 month, multiple per cluster" in {
        candidate.canonical_label for candidate in candidates
    }
    candidate = next(
        c for c in candidates if c.canonical_label == "4 cluster per 3 month, multiple per cluster"
    )
    assert "4 clusters this quarter" in candidate.evidence_text


def test_temporal_candidates_represent_weekly_cluster_with_per_cluster_range():
    candidates = build_temporal_frequency_candidates(_record("gan_10410"))

    assert "1 cluster per week, 3 to 4 per cluster" in {
        candidate.canonical_label for candidate in candidates
    }
    candidate = next(
        c
        for c in candidates
        if c.canonical_label == "1 cluster per week, 3 to 4 per cluster"
    )
    assert "weekly, 3 or 4 per cluster" in candidate.evidence_text


def test_temporal_candidates_represent_weekly_clusters_without_per_cluster_count():
    candidates = build_temporal_frequency_candidates(_record("gan_10003"))

    assert "1 cluster per week, multiple per cluster" in {
        candidate.canonical_label for candidate in candidates
    }
    candidate = next(
        c
        for c in candidates
        if c.canonical_label == "1 cluster per week, multiple per cluster"
    )
    assert "number per cluster not documented" in candidate.evidence_text


def test_temporal_candidates_represent_several_times_each_week_as_multiple_per_week():
    candidates = build_temporal_frequency_candidates(_record("gan_12130"))

    assert "multiple per week" in {candidate.canonical_label for candidate in candidates}
    candidate = next(c for c in candidates if c.canonical_label == "multiple per week")
    assert "several times each week" in candidate.evidence_text


def test_parse_llm_temporal_candidates_json_filters_unsupported_evidence():
    record = _record("gan_13123")
    supported_evidence = (
        "In terms of seizure control, She had no seizures for nearly a year "
        "following initiation of Valproate, then developed myoclonic jerks "
        "leading to a tonic seizure three Saturdays ago"
    )
    payload = {
        "candidates": [
            {
                "canonical_label": "1 per year",
                "event_count": "1",
                "window_count": "1",
                "window_unit": "year",
                "evidence_text": supported_evidence,
                "derivation": "llm_test",
            },
            {
                "canonical_label": "2 per week",
                "event_count": "2",
                "window_count": "1",
                "window_unit": "week",
                "evidence_text": "invented unsupported span",
                "derivation": "llm_test",
            },
        ]
    }

    parsed = parse_llm_temporal_candidates_json(payload, note_text=record.note_text)

    assert len(parsed) == 1
    assert parsed[0].canonical_label == "1 per year"


def test_merge_temporal_frequency_candidates_dedupes_by_label_and_evidence():
    record = _record("gan_13123")
    deterministic = build_temporal_frequency_candidates(record)
    llm_only = parse_llm_temporal_candidates_json(
        {
            "candidates": [
                {
                    "canonical_label": "1 per month",
                    "event_count": "1",
                    "window_count": "1",
                    "window_unit": "month",
                    "evidence_text": "about once a month",
                    "derivation": "llm_test",
                }
            ]
        },
        note_text=record.note_text,
    )

    merged = merge_temporal_frequency_candidates(deterministic, llm_only, llm_only)

    keys = {(c.canonical_label, c.evidence_text) for c in merged}
    assert len(keys) == len(merged)
    assert any(candidate.canonical_label == "1 per year" for candidate in merged)


def test_format_temporal_candidates_for_prompt_supports_llm_and_hybrid_sources():
    record = _record("gan_13123")
    candidates = build_temporal_frequency_candidates(record)

    llm_formatted = format_temporal_candidates_for_prompt(candidates, source="llm")
    hybrid_formatted = format_temporal_candidates_for_prompt(
        candidates,
        source="hybrid",
    )

    assert "LLM-extracted temporal frequency candidates" in llm_formatted
    assert "Hybrid deterministic+LLM temporal frequency candidates" in hybrid_formatted


def test_format_temporal_candidates_for_prompt_supports_presentation_variants():
    record = _record("gan_13123")
    candidates = build_temporal_frequency_candidates(record)

    table_formatted = format_temporal_candidates_for_prompt(
        candidates,
        presentation="table",
    )
    json_formatted = format_temporal_candidates_for_prompt(
        candidates,
        presentation="json",
    )
    bullets_formatted = format_temporal_candidates_for_prompt(
        candidates,
        presentation="bullets",
    )

    assert "| canonical_label |" in table_formatted
    assert '"candidates"' in json_formatted
    assert bullets_formatted.startswith(
        "Deterministic temporal frequency candidates (diagnostic hints only):"
    )
    assert bullets_formatted.splitlines()[1].startswith("- ")


def test_presentation_for_implementation_variant_maps_axis3_ids():
    from clinical_extraction.gan.temporal_candidates import (
        presentation_for_implementation_variant,
    )

    assert presentation_for_implementation_variant("cand_table_v1") == "table"
    assert presentation_for_implementation_variant("cand_json_v1") == "json"
    assert presentation_for_implementation_variant("unknown") is None
