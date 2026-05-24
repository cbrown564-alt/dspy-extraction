from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.evaluation.exect import score_exect_s5_prediction_set
from clinical_extraction.schemas import DocumentPrediction, ExtractedValue, PredictionSet


def test_exect_s5_scorer_scores_core_surface_only():
    gold = load_exect_gold_document("EA0008")
    prediction_set = PredictionSet(
        dataset="exect_v2",
        schema_level="exect_s5_core_field_family",
        predictions=[
            DocumentPrediction(
                document_id="EA0008",
                dataset="exect_v2",
                schema_level="exect_s5_core_field_family",
                values=[
                    ExtractedValue(field_name="diagnosis", raw_value="focal epilepsy"),
                    ExtractedValue(field_name="seizure_type", raw_value="focal seizures with altered awareness"),
                    ExtractedValue(field_name="annotated_medication", raw_value="lamotrigine"),
                    ExtractedValue(field_name="investigation", raw_value="mri abnormal"),
                    ExtractedValue(field_name="seizure_frequency", raw_value="1 per 3 week"),
                    ExtractedValue(field_name="seizure_frequency", raw_value="frequency increased"),
                    ExtractedValue(field_name="medication_temporality", raw_value="lamotrigine|current"),
                ],
            )
        ],
    )

    report = score_exect_s5_prediction_set(prediction_set, gold_documents=[gold])

    assert report["scorer"] == "exect_s5_core_field_family_deterministic_v1"
    assert set(report["benchmark_metrics"]["field_f1"]) == {
        "diagnosis",
        "seizure_type",
        "annotated_medication",
        "investigation",
        "seizure_frequency",
    }
    assert "medication_temporality" not in report["benchmark_metrics"]["field_f1"]
    assert report["benchmark_metrics"]["field_f1"]["seizure_frequency"] == 1.0
