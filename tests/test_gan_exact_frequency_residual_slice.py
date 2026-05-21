from pathlib import Path

from clinical_extraction.evaluation.gan_residual_slice import (
    assign_residual_group,
    compare_residual_slice_arms,
    load_residual_slice_record_ids,
    select_error_read_rows,
)
from clinical_extraction.schemas import DocumentPrediction, ExtractedValue, PredictionSet


def _row(record_id: str, failure_class: str, gold_pragmatic: str = "frequent") -> dict:
    return {
        "record_id": record_id,
        "status": "scored",
        "monthly_match": False,
        "failure_class": failure_class,
        "failure_action_tier": "benchmark_severe",
        "gold_pragmatic_category": gold_pragmatic,
    }


def test_assign_residual_group_prioritizes_exact_frequency_mechanisms():
    assert (
        assign_residual_group(_row("a", "pragmatic_match_monthly_divergence"))
        == "arithmetic_window_precision"
    )
    assert (
        assign_residual_group(_row("b", "unknown_as_high_rate"))
        == "unknown_vs_quantified"
    )
    assert (
        assign_residual_group(_row("c", "cluster_semantic_mismatch"))
        == "cluster_composition"
    )
    assert (
        assign_residual_group(
            _row("d", "frequent_overcalled", gold_pragmatic="infrequent")
        )
        == "infrequent_long_denominator_or_boundary"
    )


def test_select_error_read_rows_returns_disjoint_targeted_sample():
    rows = [
        *[
            _row(f"arith_{index}", "pragmatic_match_monthly_divergence")
            for index in range(12)
        ],
        *[_row(f"unk_{index}", "unknown_as_high_rate") for index in range(9)],
        *[_row(f"cluster_{index}", "cluster_semantic_mismatch") for index in range(9)],
        *[
            _row(f"infreq_{index}", "frequent_overcalled", gold_pragmatic="infrequent")
            for index in range(6)
        ],
    ]

    selected = select_error_read_rows(
        rows,
        targets={
            "arithmetic_window_precision": 10,
            "unknown_vs_quantified": 8,
            "cluster_composition": 8,
            "infrequent_long_denominator_or_boundary": 4,
        },
    )

    assert len(selected) == 30
    assert len({row["record_id"] for row in selected}) == 30
    assert [row["residual_group"] for row in selected].count(
        "arithmetic_window_precision"
    ) == 10
    assert [row["residual_group"] for row in selected].count(
        "unknown_vs_quantified"
    ) == 8
    assert [row["residual_group"] for row in selected].count("cluster_composition") == 8
    assert [row["residual_group"] for row in selected].count(
        "infrequent_long_denominator_or_boundary"
    ) == 4


def test_load_residual_slice_record_ids_reads_fixture():
    fixture = Path("data/fixtures/gan_s0_exact_frequency_residual_slice.json")
    record_ids = load_residual_slice_record_ids(fixture)
    assert len(record_ids) == 30
    assert record_ids[0] == "gan_12562"


def test_compare_residual_slice_arms_reports_recovery_and_group_counts(tmp_path):
    queue_rows = [
        {
            "record_id": "gan_12562",
            "residual_group": "arithmetic_window_precision",
            "failure_class": "purist_bin_boundary_within_pragmatic",
            "gold_label": "1 per day",
            "predicted_label": "4 per week",
            "normalized_exact_match": False,
            "monthly_match": False,
            "pragmatic_match": True,
        },
        {
            "record_id": "gan_10031",
            "residual_group": "cluster_composition",
            "failure_class": "cluster_collapsed_to_rate",
            "gold_label": "1 cluster per week, multiple per cluster",
            "predicted_label": "unknown",
            "normalized_exact_match": False,
            "monthly_match": False,
            "pragmatic_match": True,
        },
    ]

    def _write_predictions(run_dir: Path, labels: dict[str, str]) -> None:
        predictions = [
            DocumentPrediction(
                document_id=record_id,
                dataset="gan_2026",
                schema_level="gan_frequency_s0",
                values=[
                    ExtractedValue(
                        field_name="seizure_frequency_number",
                        raw_value=label,
                        normalized_value=label,
                        evidence=[],
                    )
                ],
                metadata={},
            )
            for record_id, label in labels.items()
        ]
        run_dir.mkdir(parents=True)
        (run_dir / "predictions.json").write_text(
            PredictionSet(
                dataset="gan_2026",
                schema_level="gan_frequency_s0",
                predictions=predictions,
            ).model_dump_json(indent=2),
            encoding="utf-8",
        )

    control_dir = tmp_path / "control"
    treatment_dir = tmp_path / "treatment"
    _write_predictions(
        control_dir,
        {
            "gan_12562": "4 per week",
            "gan_10031": "unknown",
        },
    )
    _write_predictions(
        treatment_dir,
        {
            "gan_12562": "1 per day",
            "gan_10031": "1 cluster per week, multiple per cluster",
        },
    )

    payload = compare_residual_slice_arms(
        queue_rows=queue_rows,
        control_run_dir=control_dir,
        treatment_run_dir=treatment_dir,
    )

    assert payload["headline"]["exact_recovery_c1_vs_c0"] == 2
    assert payload["headline"]["exact_regression_c1_vs_c0"] == 0
    assert payload["by_group"]["arithmetic_window_precision"]["exact_recovery"] == 1
    assert payload["by_group"]["cluster_composition"]["exact_recovery"] == 1
