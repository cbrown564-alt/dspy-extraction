import json

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.cli import main
from clinical_extraction.gan.frequency import label_to_monthly_frequency
from clinical_extraction.schemas import DocumentPrediction, ExtractedValue, PredictionSet


def test_gan_evaluation_cli_writes_metrics_and_error_samples(tmp_path):
    records = load_gan_records()
    correct = records[0]
    wrong = next(
        record
        for record in records[1:]
        if label_to_monthly_frequency(record.gold_label) != 1.0
    )
    predictions = PredictionSet(
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        predictions=[
            DocumentPrediction(
                document_id=correct.record_id,
                dataset="gan_2026",
                schema_level="gan_frequency_s0",
                values=[
                    ExtractedValue(
                        field_name="seizure_frequency_number",
                        raw_value=correct.gold_label,
                        normalized_value=correct.gold_label,
                    )
                ],
            ),
            DocumentPrediction(
                document_id=wrong.record_id,
                dataset="gan_2026",
                schema_level="gan_frequency_s0",
                values=[
                    ExtractedValue(
                        field_name="seizure_frequency_number",
                        raw_value="1 per 1 month",
                        normalized_value="1 per 1 month",
                    )
                ],
            ),
        ],
    )
    predictions_path = tmp_path / "predictions.json"
    output_path = tmp_path / "metrics.json"
    predictions_path.write_text(predictions.model_dump_json(indent=2), encoding="utf-8")

    exit_code = main(
        [
            "--predictions",
            str(predictions_path),
            "--output",
            str(output_path),
            "--max-errors",
            "5",
        ]
    )

    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert report["dataset"] == "gan_2026"
    assert report["schema_level"] == "gan_frequency_s0"
    assert report["counts"]["predicted_records"] == 2
    assert report["counts"]["valid_predictions"] == 2
    assert report["benchmark_metrics"]["monthly_frequency_accuracy"] == 0.5
    assert report["diagnostic_metrics"]["schema_valid_prediction_rate"] == 1.0
    assert report["errors"]["monthly_frequency_mismatches"] == [
        {
            "record_id": wrong.record_id,
            "gold_label": wrong.gold_label,
            "predicted_label": "1 per 1 month",
            "gold_monthly_frequency": report["errors"]["monthly_frequency_mismatches"][
                0
            ]["gold_monthly_frequency"],
            "predicted_monthly_frequency": 1.0,
            "gold_pragmatic_category": report["errors"]["monthly_frequency_mismatches"][
                0
            ]["gold_pragmatic_category"],
            "predicted_pragmatic_category": "infrequent",
        }
    ]
