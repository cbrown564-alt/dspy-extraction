from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
    load_exect_gold_documents,
)
from clinical_extraction.schemas import DocumentPrediction, ExectGoldDocument, PredictionSet

EXECT_DATASET = "exect_v2"
EXECT_SCORER = "exect_field_family_deterministic_v1"

FIELD_FAMILIES = ("diagnosis", "seizure_type", "annotated_medication")

_FIELD_ALIASES = {
    "diagnosis": "diagnosis",
    "diagnoses": "diagnosis",
    "epilepsy_diagnosis_type": "diagnosis",
    "seizure_type": "seizure_type",
    "seizure_types": "seizure_type",
    "current_medication": "annotated_medication",
    "current_medications": "annotated_medication",
    "annotated_medication": "annotated_medication",
    "annotated_medications": "annotated_medication",
    "medication": "annotated_medication",
    "medications": "annotated_medication",
}


class FieldFamilyScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    field_family: str
    gold_values: list[str]
    predicted_values: list[str]
    true_positives: list[str]
    false_positives: list[str]
    false_negatives: list[str]
    precision: float | None
    recall: float | None
    f1: float | None
    support: int


class ExectDocumentScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    document_id: str
    field_scores: dict[str, FieldFamilyScore]
    document_micro_precision: float | None
    document_micro_recall: float | None
    document_micro_f1: float | None
    gold_quality_flags: list[str]


def score_exect_document(
    *,
    gold: ExectGoldDocument,
    prediction: DocumentPrediction,
) -> ExectDocumentScore:
    gold_by_family = {
        "diagnosis": gold.diagnoses,
        "seizure_type": gold.seizure_types,
        "annotated_medication": gold.current_medications,
    }
    predicted_by_family = _prediction_values_by_family(prediction)
    field_scores = {
        family: _score_field_family(
            field_family=family,
            gold_values=gold_by_family[family],
            predicted_values=predicted_by_family[family],
        )
        for family in FIELD_FAMILIES
    }
    tp = sum(len(score.true_positives) for score in field_scores.values())
    fp = sum(len(score.false_positives) for score in field_scores.values())
    fn = sum(len(score.false_negatives) for score in field_scores.values())

    return ExectDocumentScore(
        document_id=gold.document_id,
        field_scores=field_scores,
        document_micro_precision=_precision(tp, fp),
        document_micro_recall=_recall(tp, fn),
        document_micro_f1=_f1(tp, fp, fn),
        gold_quality_flags=gold.quality_flags,
    )


def score_exect_prediction_set(
    prediction_set: PredictionSet,
    *,
    gold_documents: Iterable[ExectGoldDocument] | None = None,
) -> dict[str, Any]:
    if prediction_set.dataset != EXECT_DATASET:
        raise ValueError(f"Unsupported ExECT scorer dataset: {prediction_set.dataset!r}")

    gold_by_id = {
        gold.document_id: gold
        for gold in (gold_documents if gold_documents is not None else load_exect_gold_documents())
    }
    predictions_by_id = {
        prediction.document_id: prediction for prediction in prediction_set.predictions
    }
    expected_ids = set(gold_by_id)
    predicted_ids = set(predictions_by_id)
    evaluated_ids = sorted(expected_ids & predicted_ids)
    missing_ids = sorted(expected_ids - predicted_ids)
    extra_ids = sorted(predicted_ids - expected_ids)

    document_scores = [
        score_exect_document(
            gold=gold_by_id[document_id],
            prediction=predictions_by_id[document_id],
        )
        for document_id in evaluated_ids
    ]

    field_totals = {
        family: {"tp": 0, "fp": 0, "fn": 0, "support": 0} for family in FIELD_FAMILIES
    }
    for document_score in document_scores:
        for family, field_score in document_score.field_scores.items():
            field_totals[family]["tp"] += len(field_score.true_positives)
            field_totals[family]["fp"] += len(field_score.false_positives)
            field_totals[family]["fn"] += len(field_score.false_negatives)
            field_totals[family]["support"] += field_score.support

    micro_tp = sum(total["tp"] for total in field_totals.values())
    micro_fp = sum(total["fp"] for total in field_totals.values())
    micro_fn = sum(total["fn"] for total in field_totals.values())
    documents_with_flags = sum(
        bool(document_score.gold_quality_flags) for document_score in document_scores
    )

    return {
        "dataset": prediction_set.dataset,
        "schema_level": prediction_set.schema_level,
        "scorer": EXECT_SCORER,
        "counts": {
            "gold_records": len(expected_ids),
            "predicted_records": len(predicted_ids),
            "evaluated_records": len(evaluated_ids),
            "missing_predictions": len(missing_ids),
            "extra_predictions": len(extra_ids),
        },
        "benchmark_metrics": {
            "micro_precision": _precision(micro_tp, micro_fp),
            "micro_recall": _recall(micro_tp, micro_fn),
            "micro_f1": _f1(micro_tp, micro_fp, micro_fn),
            "field_precision": {
                family: _precision(total["tp"], total["fp"])
                for family, total in field_totals.items()
            },
            "field_recall": {
                family: _recall(total["tp"], total["fn"])
                for family, total in field_totals.items()
            },
            "field_f1": {
                family: _f1(total["tp"], total["fp"], total["fn"])
                for family, total in field_totals.items()
            },
            "field_support": {
                family: total["support"] for family, total in field_totals.items()
            },
        },
        "diagnostic_metrics": {
            "documents_with_gold_quality_flags": _ratio(
                documents_with_flags,
                len(document_scores),
            ),
        },
        "caveats": [
            "ExECT benchmark-facing fields are limited to audited diagnosis, seizure type, and annotated medication.",
            "Medication scoring uses annotated prescriptions only; planned/current status is not benchmark-facing.",
            "Raw diagnoses and gold quality flags are diagnostic context and are not scored as extra benchmark labels.",
        ],
        "errors": {
            "missing_prediction_ids": missing_ids,
            "extra_prediction_ids": extra_ids,
            "field_family_mismatches": [
                {
                    "document_id": document_score.document_id,
                    "field_family": family,
                    "false_positives": field_score.false_positives,
                    "false_negatives": field_score.false_negatives,
                    "gold_quality_flags": document_score.gold_quality_flags,
                }
                for document_score in document_scores
                for family, field_score in document_score.field_scores.items()
                if field_score.false_positives or field_score.false_negatives
            ],
        },
    }


def _score_field_family(
    *,
    field_family: str,
    gold_values: list[str],
    predicted_values: list[str],
) -> FieldFamilyScore:
    gold_set = set(gold_values)
    predicted_set = set(predicted_values)
    true_positives = [value for value in gold_values if value in predicted_set]
    false_negatives = [value for value in gold_values if value not in predicted_set]
    false_positives = [value for value in predicted_values if value not in gold_set]
    tp = len(true_positives)
    fp = len(false_positives)
    fn = len(false_negatives)

    return FieldFamilyScore(
        field_family=field_family,
        gold_values=gold_values,
        predicted_values=predicted_values,
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=_precision(tp, fp),
        recall=_recall(tp, fn),
        f1=_f1(tp, fp, fn),
        support=len(gold_values),
    )


def _prediction_values_by_family(
    prediction: DocumentPrediction,
) -> dict[str, list[str]]:
    values_by_family = {family: [] for family in FIELD_FAMILIES}
    for value in prediction.values:
        family = _FIELD_ALIASES.get(value.field_name)
        if family is None:
            continue
        for raw_value in _raw_prediction_values(value.normalized_value, value.raw_value):
            normalized = _normalize_prediction_value(family, raw_value)
            if normalized and normalized not in values_by_family[family]:
                values_by_family[family].append(normalized)
    return values_by_family


def _raw_prediction_values(normalized_value: Any, raw_value: str | None) -> list[str]:
    source = normalized_value if normalized_value is not None else raw_value
    if source is None:
        return []
    if isinstance(source, list):
        return [str(value) for value in source if value is not None]
    if isinstance(source, dict):
        return [str(value) for value in source.values() if value is not None]
    return [str(source)]


def _normalize_prediction_value(field_family: str, value: str) -> str:
    if field_family == "annotated_medication":
        return canonical_medication_name(value)
    return canonical_clinical_phrase(value)


def _precision(tp: int, fp: int) -> float | None:
    denominator = tp + fp
    if denominator == 0:
        return None
    return tp / denominator


def _recall(tp: int, fn: int) -> float | None:
    denominator = tp + fn
    if denominator == 0:
        return None
    return tp / denominator


def _f1(tp: int, fp: int, fn: int) -> float | None:
    precision = _precision(tp, fp)
    recall = _recall(tp, fn)
    if precision is None and recall is None:
        return None
    if not precision or not recall:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator
