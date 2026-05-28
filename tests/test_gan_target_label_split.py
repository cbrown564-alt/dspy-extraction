import pytest

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_multi_event_flags import GanMultiEventFlags
from clinical_extraction.gan.s0.target_selection import (
    build_gan_s0_target_selection_surface,
    construct_gan_s0_label_from_candidate_record,
)


def _record(record_id: str):
    return next(record for record in load_gan_records() if record.record_id == record_id)


def _flags(record_id: str) -> GanMultiEventFlags:
    return GanMultiEventFlags(
        record_id=record_id,
        source_row_index=1,
        clinical_record=True,
        gold_label="unknown",
        reference_label=None,
        label_reference_disagreement=False,
        gold_evidence_multispan=False,
        broad_frequency_mention_count=0,
        broad_frequency_mentions_ge_2=False,
        broad_frequency_mentions_ge_3=False,
        analysis_highest_frequency_language=False,
        analysis_multiple_frequency_language=False,
        multi_or_highest_analysis_signal=False,
        multiple_candidate_frequencies=False,
        highest_frequency_policy_required=False,
        historical_current_conflict=False,
        seizure_free_conflict=False,
        cluster_adjudication_required=False,
        unknown_with_event_mentions=False,
        flag_names=[],
    )


def test_construct_label_from_candidate_record_validates_without_scorer_repair():
    valid = construct_gan_s0_label_from_candidate_record(
        {
            "canonical_label": "Seizure free for 6 months",
            "event_count": "0",
            "window_count": "6",
            "window_unit": "month",
            "evidence_text": "No seizures for six months.",
            "derivation": "unit test",
        }
    )
    invalid = construct_gan_s0_label_from_candidate_record(
        {
            "canonical_label": "a pair of per 4 month",
            "event_count": "2",
            "window_count": "4",
            "window_unit": "month",
            "evidence_text": "A pair of seizures over four months.",
            "derivation": "unit test",
        }
    )

    assert valid.status == "constructed"
    assert valid.constructed_label == "seizure free for 6 month"
    assert valid.failure_reason is None
    assert invalid.status == "invalid_candidate_label"
    assert invalid.constructed_label is None
    assert "Unsupported Gan frequency label" in invalid.failure_reason


def test_target_selection_surface_separates_exact_and_family_selectors():
    record = _record("gan_14390")

    surface = build_gan_s0_target_selection_surface(
        record=record,
        flags=_flags(record.record_id),
    )

    constrained = surface["candidate_constrained_oracle"]
    family_selector = surface["reason_code_selector_family_oracle"]

    assert surface["candidate_labels"] == [
        "2 per 4 month",
        "2 per 3 month",
        "no seizure frequency reference",
        "unknown",
    ]
    assert surface["constructed_candidates"][-1]["constructed_label"] == "unknown"
    assert constrained["reason_code"] == "select_exact_candidate"
    assert constrained["constructed_label"] == "2 per 3 month"
    assert family_selector["reason_code"] == "select_family_quantified_rate"
    assert family_selector["constructed_label"] == "2 per 4 month"
    assert family_selector["scores"]["canonical"]["monthly_frequency_match"] is False
    assert family_selector["scores"]["canonical"]["pragmatic_category_match"] is True


def test_g2_report_separates_candidate_selection_from_label_construction():
    from clinical_extraction.evaluation.gan_target_label_split import (
        build_gan_target_label_split_report,
    )

    records = [_record("gan_13123"), _record("gan_13574"), _record("gan_14390")]
    flags_by_id = {record.record_id: _flags(record.record_id) for record in records}

    report = build_gan_target_label_split_report(
        records=records,
        record_ids=[record.record_id for record in records],
        flags_by_id=flags_by_id,
        split_name="unit",
    )

    arms = report["summary"]["arms"]
    constrained = arms["candidate_constrained_oracle"]
    family_selector = arms["reason_code_selector_family_oracle"]

    assert constrained["canonical"]["normalized_label_accuracy"] == pytest.approx(1.0)
    assert constrained["canonical"]["monthly_frequency_accuracy"] == pytest.approx(1.0)
    assert constrained["paper_reproduction"]["monthly_frequency_accuracy"] == (
        pytest.approx(1.0)
    )
    assert family_selector["canonical"]["normalized_label_accuracy"] == pytest.approx(
        2 / 3
    )
    assert family_selector["unsupported_records"] == 0
    assert report["summary"]["deterministic_label_constructor"]["invalid_candidates"] == 0
    assert report["rows"][2]["candidate_constrained_oracle"]["status"] == "supported"
    assert report["rows"][2]["candidate_constrained_oracle"]["reason_code"] == (
        "select_exact_candidate"
    )
