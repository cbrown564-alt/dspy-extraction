import json

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.cli import main
from clinical_extraction.gan.frequency import label_to_monthly_frequency
from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExtractedValue,
    PredictionSet,
)


def test_gan_evaluation_cli_writes_metrics_and_error_samples(tmp_path):
    records = load_gan_records()
    correct = records[0]
    wrong = next(
        record
        for record in records[1:]
        if label_to_monthly_frequency(record.gold_label) > 1.1
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
                        evidence=[EvidenceSpan(text=correct.gold_evidence or "")],
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
    assert report["diagnostic_metrics"]["evidence_quote_support_rate"] == 1.0
    assert report["diagnostic_metrics"]["evidence_offsets_present_rate"] == 0.0
    assert report["diagnostic_metrics"]["evidence_offsets_valid_rate"] is None
    assert report["diagnostic_metrics"]["evidence_exact_overlap_rate"] == 1.0
    assert report["errors"]["evidence_support_errors"] == []
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
    assert report["error_analysis"]["counts"]["schema.missing_prediction"] == (
        len(records) - 2
    )
    assert report["error_analysis"]["counts"][
        "normalization.monthly_frequency_mismatch"
    ] == 1
    assert report["error_analysis"]["counts"][
        "classification.pragmatic_category_mismatch"
    ] == 1
    assert report["error_analysis"]["counts"][
        "evidence.missing_prediction_evidence"
    ] == 1
    assert report["error_analysis"]["examples"][
        "normalization.monthly_frequency_mismatch"
    ] == [
        {
            "record_id": wrong.record_id,
            "reason": "monthly frequency differs from gold",
            "gold_monthly_frequency": report["errors"]["monthly_frequency_mismatches"][
                0
            ]["gold_monthly_frequency"],
            "predicted_monthly_frequency": 1.0,
        }
    ]


def test_gan_evaluation_cli_reports_invalid_labels(tmp_path):
    record = load_gan_records()[0]
    predictions = PredictionSet(
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        predictions=[
            DocumentPrediction(
                document_id=record.record_id,
                dataset="gan_2026",
                schema_level="gan_frequency_s0",
                values=[
                    ExtractedValue(
                        field_name="seizure_frequency_number",
                        raw_value="often",
                        evidence=[EvidenceSpan(text="not in the source letter")],
                    )
                ],
            ),
        ],
    )
    predictions_path = tmp_path / "predictions.json"
    output_path = tmp_path / "metrics.json"
    predictions_path.write_text(predictions.model_dump_json(indent=2), encoding="utf-8")

    main(
        [
            "--predictions",
            str(predictions_path),
            "--output",
            str(output_path),
            "--max-errors",
            "3",
        ]
    )

    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["counts"]["invalid_predictions"] == 1
    assert report["error_analysis"]["counts"]["normalization.invalid_label"] == 1
    assert report["error_analysis"]["examples"]["normalization.invalid_label"] == [
        {
            "record_id": record.record_id,
            "reason": "Unsupported Gan frequency label: 'often'",
            "gold_label": record.gold_label,
            "predicted_label": "often",
        }
    ]


def test_gan_evaluation_cli_reports_unsupported_evidence(tmp_path):
    record = load_gan_records()[0]
    predictions = PredictionSet(
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        predictions=[
            DocumentPrediction(
                document_id=record.record_id,
                dataset="gan_2026",
                schema_level="gan_frequency_s0",
                values=[
                    ExtractedValue(
                        field_name="seizure_frequency_number",
                        raw_value=record.gold_label,
                        normalized_value=record.gold_label,
                        evidence=[EvidenceSpan(text="not in the source letter")],
                    )
                ],
            ),
        ],
    )
    predictions_path = tmp_path / "predictions.json"
    output_path = tmp_path / "metrics.json"
    predictions_path.write_text(predictions.model_dump_json(indent=2), encoding="utf-8")

    main(
        [
            "--predictions",
            str(predictions_path),
            "--output",
            str(output_path),
            "--max-errors",
            "3",
        ]
    )

    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["error_analysis"]["counts"]["evidence.unsupported_quote"] == 1
    assert report["errors"]["evidence_support_errors"] == [
        {
            "record_id": record.record_id,
            "gold_evidence": record.gold_evidence,
            "predicted_evidence": [
                {
                    "text": "not in the source letter",
                    "start": None,
                    "end": None,
                    "document_id": None,
                    "section": None,
                }
            ],
            "reason": "predicted evidence quote or offsets not supported by document text",
        }
    ]
