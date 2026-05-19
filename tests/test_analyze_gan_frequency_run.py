import json
from pathlib import Path

from clinical_extraction.evaluation.gan_failure_taxonomy import (
    classify_gan_frequency_failure,
    failure_action_tier,
)


def test_analysis_record_ids_uses_config_record_ids_filter(tmp_path: Path):
    from clinical_extraction.evaluation.gan_run_analysis import analysis_record_ids

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "config.json").write_text(
        json.dumps({"record_ids": ["gan_10509", "gan_10751"]}),
        encoding="utf-8",
    )
    record_ids, scope = analysis_record_ids(
        run_dir=run_dir,
        split_file=Path("data/splits/gan_2026_splits.json"),
        split_name="gan_2026_fixed_v1:validation",
        predictions_by_id={"gan_10509": object()},
    )
    assert scope == "record_ids_filter"
    assert record_ids == ["gan_10509", "gan_10751"]


def _scored_row(**overrides):
    base = {
        "status": "scored",
        "gold_label": "unknown",
        "predicted_label": "no seizure frequency reference",
        "normalized_gold_label": "unknown",
        "normalized_predicted_label": "no seizure frequency reference",
        "gold_pragmatic_category": "unknown",
        "predicted_pragmatic_category": "no_seizure_information",
        "gold_purist_category": "unknown",
        "predicted_purist_category": "no_seizure_information",
        "normalized_exact_match": False,
        "monthly_match": False,
        "purist_match": False,
        "pragmatic_match": False,
        "failure_class": "other_semantic_mismatch",
    }
    base.update(overrides)
    return base


def test_unknown_cluster_to_unknown_with_monthly_match_is_diagnostic_only():
    row = _scored_row(
        gold_label="unknown, 2 to 3 per cluster",
        predicted_label="unknown",
        normalized_gold_label="unknown, 2 to 3 per cluster",
        normalized_predicted_label="unknown",
        monthly_match=True,
        purist_match=True,
        pragmatic_match=True,
    )
    failure_class = classify_gan_frequency_failure(row)
    assert failure_class == "unknown_cluster_label_shape_mismatch"
    assert failure_action_tier(failure_class) == "diagnostic_only"


def test_seizure_free_to_no_reference_with_monthly_match_is_diagnostic_only():
    row = _scored_row(
        gold_label="seizure free for multiple year",
        predicted_label="no seizure frequency reference",
        normalized_gold_label="seizure free for multiple year",
        normalized_predicted_label="no seizure frequency reference",
        gold_pragmatic_category="infrequent",
        predicted_pragmatic_category="no_seizure_information",
        gold_purist_category="lt_1_per_6_months",
        predicted_purist_category="no_seizure_information",
        monthly_match=True,
        purist_match=True,
        pragmatic_match=True,
    )
    failure_class = classify_gan_frequency_failure(row)
    assert failure_class == "seizure_free_to_no_reference_monthly_match"
    assert failure_action_tier(failure_class) == "diagnostic_only"


def test_seizure_free_to_no_reference_without_monthly_match_is_benchmark_severe():
    row = _scored_row(
        gold_label="unknown",
        predicted_label="seizure free for 4 month",
        normalized_gold_label="unknown",
        normalized_predicted_label="seizure free for 4 month",
        monthly_match=False,
    )
    failure_class = classify_gan_frequency_failure(row)
    assert failure_class == "unknown_vs_seizure_free"
    assert failure_action_tier(failure_class) == "benchmark_severe"


def test_unknown_vs_no_reference_remains_benchmark_severe():
    row = _scored_row()
    failure_class = classify_gan_frequency_failure(row)
    assert failure_class == "unknown_vs_no_reference"
    assert failure_action_tier(failure_class) == "benchmark_severe"
