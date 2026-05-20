from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.evaluation.exect import score_exect_s4_prediction_set
from clinical_extraction.schemas import DocumentPrediction, ExtractedValue, PredictionSet


def test_exect_s4_scorer_scores_s4_field_families():
    gold = load_exect_gold_document("EA0008")
    prediction_set = PredictionSet(
        dataset="exect_v2",
        schema_level="exect_s4_field_family",
        predictions=[
            DocumentPrediction(
                document_id="EA0008",
                dataset="exect_v2",
                schema_level="exect_s4_field_family",
                values=[
                    ExtractedValue(field_name="seizure_frequency", raw_value="1 per 3 week"),
                    ExtractedValue(field_name="seizure_frequency", raw_value="frequency increased"),
                    ExtractedValue(
                        field_name="medication_temporality",
                        raw_value="lamotrigine|current",
                    ),
                ],
            )
        ],
    )

    report = score_exect_s4_prediction_set(prediction_set, gold_documents=[gold])

    assert report["scorer"] == "exect_s4_field_family_deterministic_v1"
    assert report["benchmark_metrics"]["field_f1"]["seizure_frequency"] == 1.0
    assert report["benchmark_metrics"]["field_f1"]["medication_temporality"] == 1.0
    assert "birth_history" in report["benchmark_metrics"]["field_f1"]


def test_exect_s4_scorer_includes_frozen_s3_families():
    gold = load_exect_gold_document("EA0062")
    prediction_set = PredictionSet(
        dataset="exect_v2",
        schema_level="exect_s4_field_family",
        predictions=[
            DocumentPrediction(
                document_id="EA0062",
                dataset="exect_v2",
                schema_level="exect_s4_field_family",
                values=[
                    ExtractedValue(field_name="birth_history", raw_value="born normally"),
                ],
            )
        ],
    )

    report = score_exect_s4_prediction_set(prediction_set, gold_documents=[gold])

    assert report["benchmark_metrics"]["field_f1"]["birth_history"] == 1.0
    assert "investigation" in report["benchmark_metrics"]["field_f1"]
