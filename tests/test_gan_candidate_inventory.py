from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_candidate_inventory import (
    build_gan_candidate_inventory_report,
    hard_strata_for_record,
    label_family,
)
from clinical_extraction.evaluation.gan_multi_event_flags import GanMultiEventFlags


def _record(record_id: str):
    return next(record for record in load_gan_records() if record.record_id == record_id)


def _flags(**overrides) -> GanMultiEventFlags:
    values = {
        "record_id": "gan_x",
        "source_row_index": 1,
        "clinical_record": True,
        "gold_label": "unknown",
        "reference_label": None,
        "label_reference_disagreement": False,
        "gold_evidence_multispan": False,
        "broad_frequency_mention_count": 0,
        "broad_frequency_mentions_ge_2": False,
        "broad_frequency_mentions_ge_3": False,
        "analysis_highest_frequency_language": False,
        "analysis_multiple_frequency_language": False,
        "multi_or_highest_analysis_signal": False,
        "multiple_candidate_frequencies": False,
        "highest_frequency_policy_required": False,
        "historical_current_conflict": False,
        "seizure_free_conflict": False,
        "cluster_adjudication_required": False,
        "unknown_with_event_mentions": False,
        "flag_names": [],
    }
    values.update(overrides)
    return GanMultiEventFlags(**values)


def test_label_family_preserves_gan_special_cases():
    assert label_family("unknown") == "unknown"
    assert label_family("no seizure frequency reference") == "no_reference"
    assert label_family("seizure free for multiple year") == "seizure_free"
    assert label_family("unknown, 3 per cluster") == "unknown_cluster"
    assert label_family("2 cluster per month, 3 per cluster") == "cluster"
    assert label_family("multiple per week") == "vague_or_multiple_rate"
    assert label_family("2 per month") == "quantified_rate"


def test_hard_strata_include_required_g1_buckets():
    record = _record("gan_10618")
    flags = _flags(
        record_id=record.record_id,
        cluster_adjudication_required=True,
        unknown_with_event_mentions=True,
        label_reference_disagreement=True,
    )

    strata = hard_strata_for_record(record, flags)

    assert "cluster" in strata
    assert "unknown_with_events" in strata
    assert "label_reference_disagreement" in strata
    assert "vague_frequency" in strata


def test_candidate_inventory_report_summarizes_exact_and_category_coverage():
    records = [_record("gan_13123"), _record("gan_13574")]
    flags_by_id = {
        "gan_13123": _flags(record_id="gan_13123"),
        "gan_13574": _flags(record_id="gan_13574", seizure_free_conflict=True),
    }

    report = build_gan_candidate_inventory_report(
        records=records,
        record_ids=["gan_13123", "gan_13574"],
        flags_by_id=flags_by_id,
        split_name="unit",
    )

    overall = report["summary"]["overall"]
    assert overall["records"] == 2
    assert overall["gold_exact_covered"] == 2
    assert overall["gold_purist_equivalent_covered"] == 2
    assert overall["gold_pragmatic_equivalent_covered"] == 2
    assert report["summary"]["by_label_family"]["quantified_rate"]["records"] == 1
    assert report["summary"]["by_label_family"]["seizure_free"]["records"] == 1
    assert report["summary"]["by_hard_stratum"]["seizure_free_conflict"][
        "gold_exact_covered"
    ] == 1


def test_candidate_inventory_report_surfaces_invalid_candidate_labels():
    record = _record("gan_14390")

    report = build_gan_candidate_inventory_report(
        records=[record],
        record_ids=[record.record_id],
        flags_by_id={record.record_id: _flags(record_id=record.record_id)},
        split_name="unit",
    )

    assert report["summary"]["invalid_candidate_labels"]["records"] == 1
    assert report["rows"][0]["invalid_candidate_labels"] == ["a pair of per 4 month"]
