from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.react_tools import (
    compute_elapsed_days,
    count_react_tool_calls,
    extract_clinic_date,
    find_temporal_frequency_candidates,
    validate_cluster_format,
    validate_evidence_quote,
    validate_gan_frequency_label,
)


def test_find_temporal_frequency_candidates_returns_gan_14881_candidate():
    record = next(r for r in load_gan_records() if r.record_id == "gan_14881")
    formatted = find_temporal_frequency_candidates(record.note_text)
    assert "1 per month" in formatted


def test_extract_clinic_date_returns_iso_date_for_gan_14881():
    record = next(r for r in load_gan_records() if r.record_id == "gan_14881")
    assert extract_clinic_date(record.note_text) == "2014-03-21"


def test_compute_elapsed_days_between_last_episode_and_clinic_date():
    assert compute_elapsed_days("2014-02-26", "2014-03-21") == "23"


def test_validate_gan_frequency_label_accepts_canonical_rate():
    assert validate_gan_frequency_label("1 per month").startswith("ok:")


def test_validate_cluster_format_requires_per_cluster_suffix():
    assert validate_cluster_format("1 cluster per week").startswith("error:")
    assert validate_cluster_format(
        "1 cluster per week, multiple per cluster"
    ).startswith("ok:")


def test_validate_evidence_quote_checks_exact_substring():
    record = next(r for r in load_gan_records() if r.record_id == "gan_15306")
    quote = record.gold_evidence
    assert quote
    assert validate_evidence_quote(record.note_text, quote).startswith("ok:")
    assert validate_evidence_quote(record.note_text, "missing quote").startswith(
        "error:"
    )


def test_count_react_tool_calls_ignores_finish():
    trajectory = {
        "tool_name_0": "find_temporal_frequency_candidates",
        "tool_name_1": "finish",
    }
    assert count_react_tool_calls(trajectory) == 1
