from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.evaluation.exect import score_exect_s2_prediction_set
from clinical_extraction.schemas import DocumentPrediction, ExtractedValue, PredictionSet


def test_exect_s2_scorer_scores_investigation_and_comorbidity_families():
    gold = load_exect_gold_document("EA0007")
    prediction_set = PredictionSet(
        dataset="exect_v2",
        schema_level="exect_s2_field_family",
        predictions=[
            DocumentPrediction(
                document_id="EA0007",
                dataset="exect_v2",
                schema_level="exect_s2_field_family",
                    values=[
                        ExtractedValue(field_name="investigation", raw_value="MRI normal"),
                        ExtractedValue(field_name="comorbidity", raw_value="diabetes"),
                        ExtractedValue(field_name="comorbidity", raw_value="hypothyroidism"),
                    ],
            )
        ],
    )

    report = score_exect_s2_prediction_set(prediction_set, gold_documents=[gold])

    assert report["scorer"] == "exect_s2_field_family_deterministic_v1"
    assert report["benchmark_metrics"]["field_f1"]["investigation"] == 1.0
    assert report["benchmark_metrics"]["field_f1"]["comorbidity"] == 1.0
    assert "investigation" in report["benchmark_metrics"]["field_support"]
    assert "comorbidity" in report["benchmark_metrics"]["field_support"]
