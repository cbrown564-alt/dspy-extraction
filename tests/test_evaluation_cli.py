import json

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.cli import evaluate_gan_predictions, main
from clinical_extraction.gan.frequency import label_to_monthly_frequency
from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExtractedValue,
    GanRecord,
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
            "--bootstrap-samples",
            "200",
            "--bootstrap-seed",
            "17",
            "--scorer-mode",
            "gan_frequency_deterministic_v1",
        ]
    )

    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert report["dataset"] == "gan_2026"
    assert report["schema_level"] == "gan_frequency_s0"
    assert report["scorer"] == "gan_frequency_deterministic_v1"
    assert report["counts"]["predicted_records"] == 2
    assert report["counts"]["valid_predictions"] == 2
    assert report["benchmark_metrics"]["monthly_frequency_accuracy"] == 0.5
    monthly_interval = report["confidence_intervals"]["monthly_frequency_accuracy"]
    assert monthly_interval["point_estimate"] == 0.5
    assert monthly_interval["bootstrap_samples"] == 200
    assert monthly_interval["seed"] == 17
    assert monthly_interval["n"] == 2
    assert monthly_interval["method"] == "percentile_bootstrap_mean"
    assert report["diagnostic_metrics"]["schema_valid_prediction_rate"] == 1.0
    assert report["confidence_intervals"]["schema_valid_prediction_rate"][
        "point_estimate"
    ] == 1.0
    assert report["diagnostic_metrics"]["evidence_quote_support_rate"] == 1.0
    assert report["diagnostic_metrics"]["evidence_offsets_present_rate"] == 0.0
    assert report["diagnostic_metrics"]["evidence_offsets_valid_rate"] is None
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


def test_gan_evaluation_scores_evidence_against_source_text_only(monkeypatch):
    record = GanRecord(
        record_id="gan-paraphrase-1",
        source_row_index=1,
        note_text="History: she reports one seizure per month since March.",
        gold_label="1 per 1 month",
        gold_evidence="Patient has monthly seizures after March.",
        reference_label=None,
        reference_evidence=None,
        row_ok=True,
        labels_match_all_categories=True,
        quotes_ok_all_categories=False,
        flags=["paraphrased_gold_evidence"],
        raw={},
    )
    monkeypatch.setattr(
        "clinical_extraction.evaluation.cli.load_gan_records",
        lambda: [record],
    )
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
                        evidence=[EvidenceSpan(text="one seizure per month")],
                    )
                ],
            )
        ],
    )

    report = evaluate_gan_predictions(predictions, bootstrap_samples=10)

    assert report["diagnostic_metrics"]["evidence_quote_support_rate"] == 1.0
    assert "gold_evidence_locatable_rate" not in report["diagnostic_metrics"]
    assert "evidence_overlap_scored_rate" not in report["diagnostic_metrics"]
    assert "evidence_exact_overlap_rate" not in report["diagnostic_metrics"]
    assert "evidence.gold_unlocatable" not in report["error_analysis"]["counts"]
    assert "evidence.partial_overlap" not in report["error_analysis"]["counts"]


def test_gan_evaluation_defaults_to_paper_reproduction_but_keeps_canonical_mode(
    monkeypatch,
):
    record = GanRecord(
        record_id="gan-paper-mode-1",
        source_row_index=1,
        note_text="This administrative letter does not discuss seizures.",
        gold_label="unknown",
        gold_evidence=None,
        reference_label="no seizure frequency reference",
        reference_evidence=None,
        row_ok=True,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        flags=[],
        raw={},
    )
    monkeypatch.setattr(
        "clinical_extraction.evaluation.cli.load_gan_records",
        lambda: [record],
    )
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
                        raw_value="no seizure frequency reference",
                        normalized_value="no seizure frequency reference",
                    )
                ],
            )
        ],
    )

    paper_default = evaluate_gan_predictions(predictions, bootstrap_samples=10)
    canonical = evaluate_gan_predictions(
        predictions,
        bootstrap_samples=10,
        scorer_mode="gan_frequency_deterministic_v1",
    )

    assert paper_default["scorer"] == "gan2026_paper_reproduction"
    assert paper_default["benchmark_metrics"]["monthly_frequency_accuracy"] == 1.0
    assert "author-evaluator compatibility" in paper_default["caveats"][-1]
    assert canonical["scorer"] == "gan_frequency_deterministic_v1"
    assert canonical["benchmark_metrics"]["monthly_frequency_accuracy"] == 0.0


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
            "--scorer-mode",
            "gan_frequency_deterministic_v1",
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


def test_gan_evaluation_surfaces_full_validation_failure_boundaries(monkeypatch):
    records = [
        GanRecord(
            record_id="gan-fixture-cluster-to-unknown",
            source_row_index=1,
            note_text="Diary: one cluster each week, usually three seizures per cluster.",
            gold_label="1 cluster per week, multiple per cluster",
            gold_evidence="one cluster each week, usually three seizures per cluster",
            row_ok=True,
            labels_match_all_categories=True,
            quotes_ok_all_categories=True,
            raw={},
        ),
        GanRecord(
            record_id="gan-fixture-unknown-to-no-reference",
            source_row_index=2,
            note_text="Seizures are mentioned, but the frequency cannot be estimated.",
            gold_label="unknown",
            gold_evidence="the frequency cannot be estimated",
            row_ok=True,
            labels_match_all_categories=True,
            quotes_ok_all_categories=True,
            raw={},
        ),
        GanRecord(
            record_id="gan-fixture-denominator-window",
            source_row_index=3,
            note_text="The current baseline is one seizure per day.",
            gold_label="1 per day",
            gold_evidence="one seizure per day",
            row_ok=True,
            labels_match_all_categories=True,
            quotes_ok_all_categories=True,
            raw={},
        ),
        GanRecord(
            record_id="gan-fixture-incomplete-cluster",
            source_row_index=4,
            note_text="One cluster is reported each week, but cluster size is stated elsewhere.",
            gold_label="1 cluster per week, multiple per cluster",
            gold_evidence="One cluster is reported each week",
            row_ok=True,
            labels_match_all_categories=True,
            quotes_ok_all_categories=True,
            raw={},
        ),
        GanRecord(
            record_id="gan-fixture-abstention",
            source_row_index=5,
            note_text="There are multiple seizures each day.",
            gold_label="multiple per day",
            gold_evidence="multiple seizures each day",
            row_ok=True,
            labels_match_all_categories=True,
            quotes_ok_all_categories=True,
            raw={},
        ),
        GanRecord(
            record_id="gan-fixture-missing-evidence",
            source_row_index=6,
            note_text="The patient has one seizure per month.",
            gold_label="1 per month",
            gold_evidence="one seizure per month",
            row_ok=True,
            labels_match_all_categories=True,
            quotes_ok_all_categories=True,
            raw={},
        ),
        GanRecord(
            record_id="gan-fixture-unsupported-evidence",
            source_row_index=7,
            note_text="The patient has two seizures per month.",
            gold_label="2 per month",
            gold_evidence="two seizures per month",
            row_ok=True,
            labels_match_all_categories=True,
            quotes_ok_all_categories=True,
            raw={},
        ),
    ]
    monkeypatch.setattr(
        "clinical_extraction.evaluation.cli.load_gan_records",
        lambda: records,
    )

    predictions = PredictionSet(
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        predictions=[
            _gan_prediction(
                "gan-fixture-cluster-to-unknown",
                "unknown",
                evidence_text="one cluster each week, usually three seizures per cluster",
            ),
            _gan_prediction(
                "gan-fixture-unknown-to-no-reference",
                "no seizure frequency reference",
                evidence_text="the frequency cannot be estimated",
            ),
            _gan_prediction(
                "gan-fixture-denominator-window",
                "1 to 2 per month",
                evidence_text="one seizure per day",
            ),
            _gan_prediction(
                "gan-fixture-incomplete-cluster",
                "1 cluster per week",
                evidence_text="One cluster is reported each week",
            ),
            _gan_prediction("gan-fixture-abstention", None, quality_flags=["abstained"]),
            _gan_prediction("gan-fixture-missing-evidence", "1 per month"),
            _gan_prediction(
                "gan-fixture-unsupported-evidence",
                "2 per month",
                evidence_text="two monthly seizures",
            ),
        ],
    )

    report = evaluate_gan_predictions(
        predictions,
        max_errors=10,
        bootstrap_samples=10,
        scorer_mode="gan_frequency_deterministic_v1",
    )

    assert report["counts"]["invalid_predictions"] == 2
    assert report["error_analysis"]["counts"]["normalization.invalid_label"] == 1
    assert report["error_analysis"]["counts"]["schema.missing_value"] == 1
    assert report["error_analysis"]["counts"]["abstention.predicted_abstention"] == 1
    assert report["error_analysis"]["counts"][
        "normalization.monthly_frequency_mismatch"
    ] == 3
    assert report["error_analysis"]["counts"][
        "classification.pragmatic_category_mismatch"
    ] == 2
    assert report["error_analysis"]["counts"][
        "evidence.missing_prediction_evidence"
    ] == 1
    assert report["error_analysis"]["counts"]["evidence.unsupported_quote"] == 1
    assert {
        sample["record_id"]
        for sample in report["errors"]["monthly_frequency_mismatches"]
    } == {
        "gan-fixture-cluster-to-unknown",
        "gan-fixture-unknown-to-no-reference",
        "gan-fixture-denominator-window",
    }


def _gan_prediction(
    record_id: str,
    label: str | None,
    *,
    evidence_text: str | None = None,
    quality_flags: list[str] | None = None,
) -> DocumentPrediction:
    return DocumentPrediction(
        document_id=record_id,
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        values=[
            ExtractedValue(
                field_name="seizure_frequency_number",
                raw_value=label,
                normalized_value=label,
                evidence=[EvidenceSpan(text=evidence_text)] if evidence_text else [],
                quality_flags=quality_flags or [],
            )
        ],
    )
