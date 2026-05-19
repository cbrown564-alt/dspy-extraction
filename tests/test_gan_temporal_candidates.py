from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates,
    build_temporal_frequency_candidates_from_note,
    format_temporal_candidates_for_prompt,
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
