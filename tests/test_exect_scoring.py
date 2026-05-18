from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.evaluation.exect import (
    score_exect_document,
    score_exect_prediction_set,
)
from clinical_extraction.schemas import DocumentPrediction, ExtractedValue, PredictionSet


def test_exect_document_scorer_uses_audited_field_views_and_normalization():
    gold = load_exect_gold_document("EA0029")
    prediction = DocumentPrediction(
        document_id="EA0029",
        dataset="exect_v2",
        schema_level="exect_s0_s1",
        values=[
            ExtractedValue(
                field_name="diagnosis",
                raw_value="juvenile-myoclonic-epilepsy",
            ),
            ExtractedValue(
                field_name="diagnosis",
                raw_value="epilepsy",
            ),
            ExtractedValue(
                field_name="seizure_type",
                raw_value="generalised tonic chronic seizures",
            ),
            ExtractedValue(
                field_name="current_medication",
                raw_value="Keppra",
            ),
            ExtractedValue(
                field_name="current_medication",
                raw_value="lamotrigine",
            ),
        ],
    )

    score = score_exect_document(gold=gold, prediction=prediction)

    assert score.field_scores["diagnosis"].true_positives == ["juvenile myoclonic epilepsy"]
    assert score.field_scores["diagnosis"].false_positives == ["epilepsy"]
    assert score.field_scores["diagnosis"].false_negatives == []
    assert score.field_scores["seizure_type"].f1 == 1.0
    assert score.field_scores["annotated_medication"].f1 == 1.0
    assert "specificity_collapsed" in score.gold_quality_flags


def test_exect_document_scorer_counts_missing_fields_per_family():
    gold = load_exect_gold_document("EA0016")
    prediction = DocumentPrediction(
        document_id="EA0016",
        dataset="exect_v2",
        schema_level="exect_s0_s1",
        values=[],
    )

    score = score_exect_document(gold=gold, prediction=prediction)

    assert score.field_scores["diagnosis"].support == 0
    assert score.field_scores["diagnosis"].f1 is None
    assert score.field_scores["seizure_type"].false_negatives == ["focal seizure"]
    assert score.field_scores["seizure_type"].recall == 0.0
    assert score.document_micro_f1 == 0.0


def test_exect_prediction_set_scorer_reports_field_and_micro_metrics():
    perfect = load_exect_gold_document("EA0008")
    missed = load_exect_gold_document("EA0016")
    prediction_set = PredictionSet(
        dataset="exect_v2",
        schema_level="exect_s0_s1",
        predictions=[
            DocumentPrediction(
                document_id="EA0008",
                dataset="exect_v2",
                schema_level="exect_s0_s1",
                values=[
                    ExtractedValue(
                        field_name="diagnosis",
                        raw_value=perfect.diagnoses[0],
                    ),
                    ExtractedValue(
                        field_name="seizure_type",
                        raw_value=perfect.seizure_types[0],
                    ),
                    ExtractedValue(
                        field_name="current_medication",
                        raw_value=perfect.current_medications[0],
                    ),
                ],
            ),
            DocumentPrediction(
                document_id="EA0016",
                dataset="exect_v2",
                schema_level="exect_s0_s1",
                values=[],
            ),
        ],
    )

    report = score_exect_prediction_set(prediction_set, gold_documents=[perfect, missed])

    assert report["dataset"] == "exect_v2"
    assert report["scorer"] == "exect_field_family_deterministic_v1"
    assert report["counts"] == {
        "gold_records": 2,
        "predicted_records": 2,
        "evaluated_records": 2,
        "missing_predictions": 0,
        "extra_predictions": 0,
    }
    assert report["benchmark_metrics"]["micro_f1"] == 0.8571428571428571
    assert report["benchmark_metrics"]["field_f1"]["diagnosis"] == 1.0
    assert report["benchmark_metrics"]["field_f1"]["seizure_type"] == 0.6666666666666666
    assert report["diagnostic_metrics"]["documents_with_gold_quality_flags"] == 0.0


def test_exect_prediction_set_scorer_reports_evidence_quote_diagnostics():
    gold = load_exect_gold_document("EA0008")
    prediction_set = PredictionSet(
        dataset="exect_v2",
        schema_level="exect_s0_s1",
        predictions=[
            DocumentPrediction(
                document_id="EA0008",
                dataset="exect_v2",
                schema_level="exect_s0_s1",
                values=[
                    ExtractedValue(
                        field_name="diagnosis",
                        raw_value=gold.diagnoses[0],
                        evidence=[],
                    ),
                    ExtractedValue(
                        field_name="seizure_type",
                        raw_value=gold.seizure_types[0],
                        evidence=[
                            {
                                "text": "focal seizures with altered awareness",
                            }
                        ],
                    ),
                    ExtractedValue(
                        field_name="current_medication",
                        raw_value=gold.current_medications[0],
                        evidence=[
                            {
                                "text": "not a contiguous quote from this note",
                            }
                        ],
                    ),
                ],
            ),
        ],
    )

    report = score_exect_prediction_set(prediction_set, gold_documents=[gold])

    assert report["diagnostic_metrics"]["evidence_quote_support_rate"] == 0.5
    assert report["diagnostic_metrics"]["evidence_offsets_present_rate"] == 0.0
    assert report["diagnostic_metrics"]["evidence_offsets_valid_rate"] is None
    assert report["errors"]["evidence_support_errors"] == [
        {
            "document_id": "EA0008",
            "field_name": "diagnosis",
            "raw_value": gold.diagnoses[0],
            "reason": "prediction has no evidence spans",
        },
        {
            "document_id": "EA0008",
            "field_name": "current_medication",
            "raw_value": gold.current_medications[0],
            "predicted_evidence": [
                {
                    "document_id": None,
                    "end": None,
                    "section": None,
                    "start": None,
                    "text": "not a contiguous quote from this note",
                }
            ],
            "reason": "predicted evidence quote or offsets not supported by document text",
        },
    ]


def test_exect_prediction_set_scorer_separates_exact_and_repaired_evidence_quotes():
    gold = load_exect_gold_document("EA0018")
    prediction_set = PredictionSet(
        dataset="exect_v2",
        schema_level="exect_s0_s1",
        predictions=[
            DocumentPrediction(
                document_id="EA0018",
                dataset="exect_v2",
                schema_level="exect_s0_s1",
                values=[
                    ExtractedValue(
                        field_name="diagnosis",
                        raw_value=gold.diagnoses[0],
                        evidence=[
                            {
                                "text": "with epilepsy",
                            }
                        ],
                    ),
                    ExtractedValue(
                        field_name="current_medication",
                        raw_value=gold.current_medications[0],
                        evidence=[
                            {
                                "text": "Currently she is taking sodium valproate 500 mg twice a day and levetiracetam 1000 mg twice today.",
                            }
                        ],
                        quality_flags=["evidence_repair:ellipsis_contiguous_span"],
                    ),
                ],
            ),
        ],
    )

    report = score_exect_prediction_set(prediction_set, gold_documents=[gold])

    assert report["diagnostic_metrics"]["evidence_quote_support_rate"] == 1.0
    assert report["diagnostic_metrics"]["evidence_quote_support_rate_without_repairs"] == 1.0
    assert report["diagnostic_metrics"]["evidence_quote_support_rate_repaired"] == 1.0
    assert report["diagnostic_metrics"]["evidence_quote_repair_rate"] == 0.5
