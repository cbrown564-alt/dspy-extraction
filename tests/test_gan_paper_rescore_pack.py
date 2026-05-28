import json
from pathlib import Path

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_paper_rescore_pack import (
    GanPaperRescoreBaseline,
    build_gan_paper_rescore_pack_report,
    write_report_artifacts,
)
from clinical_extraction.schemas import DocumentPrediction, ExtractedValue, PredictionSet


def _write_run(run_dir: Path, *, predictions: list[DocumentPrediction]) -> None:
    run_dir.mkdir()
    prediction_set = PredictionSet(
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        predictions=predictions,
    )
    (run_dir / "predictions.json").write_text(
        prediction_set.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (run_dir / "metadata.json").write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "split_name": "gan_2026_fixed_v1:validation",
                "model_provider": "unit",
                "model_name": "unit-model",
                "program_variant": "gan_frequency_s0_unit",
                "metadata": {"prompt_version": "unit_prompt"},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "experiment_id": "unit_experiment",
                "split_name": "gan_2026_fixed_v1:validation",
                "scorer_mode": "gan_frequency_deterministic_v1",
                "model_config_path": "configs/models/unit.json",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "metrics.json").write_text(
        json.dumps({"benchmark_metrics": {}, "diagnostic_metrics": {}, "counts": {}}),
        encoding="utf-8",
    )


def _prediction(record_id: str, label: str) -> DocumentPrediction:
    return DocumentPrediction(
        document_id=record_id,
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        values=[
            ExtractedValue(
                field_name="seizure_frequency_number",
                raw_value=label,
                normalized_value=label,
            )
        ],
    )


def test_gan_paper_rescore_pack_keeps_paper_and_canonical_views_separate(tmp_path):
    unknown_record = next(
        record for record in load_gan_records() if record.gold_label == "unknown"
    )
    run_dir = tmp_path / "gan_unit_run"
    _write_run(
        run_dir,
        predictions=[
            _prediction(
                unknown_record.record_id,
                "no seizure frequency reference",
            )
        ],
    )

    report = build_gan_paper_rescore_pack_report(
        baseline_specs=[
            GanPaperRescoreBaseline(
                baseline_id="unit",
                label="Unit baseline",
                role="unit test",
                run_dir=run_dir,
            )
        ],
        bootstrap_samples=10,
    )

    baseline = report["summary"]["baselines"][0]
    assert report["paper_scorer_options"] == {
        "apply_paper_prediction_repair": False,
        "allow_paper_prediction_range": False,
        "allow_paper_error_tolerance": False,
    }
    assert baseline["paper_reproduction"]["benchmark_metrics"][
        "monthly_frequency_accuracy"
    ] == 1.0
    assert baseline["canonical"]["benchmark_metrics"][
        "monthly_frequency_accuracy"
    ] == 0.0
    assert baseline["paper_minus_canonical"]["monthly_frequency_accuracy"] == 1.0
    assert baseline["paper_reproduction"]["counts"]["valid_predictions"] == 1
    assert baseline["canonical"]["counts"]["valid_predictions"] == 1


def test_gan_paper_rescore_pack_writes_json_and_markdown(tmp_path):
    record = load_gan_records()[0]
    run_dir = tmp_path / "gan_unit_run"
    _write_run(run_dir, predictions=[_prediction(record.record_id, record.gold_label)])

    report = build_gan_paper_rescore_pack_report(
        baseline_specs=[
            GanPaperRescoreBaseline(
                baseline_id="unit",
                label="Unit baseline",
                role="unit test",
                run_dir=run_dir,
            )
        ],
        bootstrap_samples=10,
    )
    json_output = tmp_path / "report.json"
    markdown_output = tmp_path / "report.md"

    write_report_artifacts(
        report,
        json_output=json_output,
        markdown_output=markdown_output,
    )

    loaded = json.loads(json_output.read_text(encoding="utf-8"))
    markdown = markdown_output.read_text(encoding="utf-8")
    assert loaded["kanban_card"] == "G5 - Gan Paper-Scorer Rescore Pack"
    assert "Paper Scorer Options" in markdown
    assert "Unit baseline" in markdown
