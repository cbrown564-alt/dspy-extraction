from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict

from clinical_extraction.datasets.exect import (
    canonical_birth_history_label,
    canonical_clinical_phrase,
    canonical_comorbidity_label,
    canonical_epilepsy_cause_label,
    canonical_medication_name,
    canonical_onset_label,
    canonical_when_diagnosed_label,
    normalize_investigation_phrase,
    load_exect_gold_documents,
)
from clinical_extraction.evaluation.evidence import score_evidence_support
from clinical_extraction.schemas import DocumentPrediction, ExectGoldDocument, PredictionSet

EXECT_DATASET = "exect_v2"
EXECT_SCORER = "exect_field_family_deterministic_v1"
EXECT_S2_SCORER = "exect_s2_field_family_deterministic_v1"
EXECT_S3_SCORER = "exect_s3_field_family_deterministic_v1"
EXECT_S4_SCORER = "exect_s4_field_family_deterministic_v1"

FIELD_FAMILIES = ("diagnosis", "seizure_type", "annotated_medication")
S2_FIELD_FAMILIES = (
    "diagnosis",
    "seizure_type",
    "annotated_medication",
    "investigation",
    "comorbidity",
)
S3_FIELD_FAMILIES = (
    *S2_FIELD_FAMILIES,
    "birth_history",
    "onset",
    "epilepsy_cause",
    "when_diagnosed",
)
S4_FIELD_FAMILIES = (
    *S3_FIELD_FAMILIES,
    "seizure_frequency",
    "medication_temporality",
)

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

_S2_FIELD_ALIASES = {
    **_FIELD_ALIASES,
    "investigation": "investigation",
    "investigations": "investigation",
    "eeg_finding": "investigation",
    "eeg_findings": "investigation",
    "mri_finding": "investigation",
    "mri_findings": "investigation",
    "ct_finding": "investigation",
    "comorbidity": "comorbidity",
    "comorbidities": "comorbidity",
}

_S3_FIELD_ALIASES = {
    **_S2_FIELD_ALIASES,
    "birth_history": "birth_history",
    "birth_histories": "birth_history",
    "onset": "onset",
    "onsets": "onset",
    "epilepsy_cause": "epilepsy_cause",
    "epilepsy_causes": "epilepsy_cause",
    "when_diagnosed": "when_diagnosed",
}

_S4_FIELD_ALIASES = {
    **_S3_FIELD_ALIASES,
    "seizure_frequency": "seizure_frequency",
    "seizure_frequencies": "seizure_frequency",
    "current_seizure_frequency": "seizure_frequency",
    "medication_temporality": "medication_temporality",
    "medication_temporalities": "medication_temporality",
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
    return _score_exect_document_for_families(
        gold=gold,
        prediction=prediction,
        field_families=FIELD_FAMILIES,
        field_aliases=_FIELD_ALIASES,
    )


def score_exect_s2_document(
    *,
    gold: ExectGoldDocument,
    prediction: DocumentPrediction,
) -> ExectDocumentScore:
    return _score_exect_document_for_families(
        gold=gold,
        prediction=prediction,
        field_families=S2_FIELD_FAMILIES,
        field_aliases=_S2_FIELD_ALIASES,
    )


def score_exect_s3_document(
    *,
    gold: ExectGoldDocument,
    prediction: DocumentPrediction,
) -> ExectDocumentScore:
    return _score_exect_document_for_families(
        gold=gold,
        prediction=prediction,
        field_families=S3_FIELD_FAMILIES,
        field_aliases=_S3_FIELD_ALIASES,
    )


def score_exect_s4_document(
    *,
    gold: ExectGoldDocument,
    prediction: DocumentPrediction,
) -> ExectDocumentScore:
    return _score_exect_document_for_families(
        gold=gold,
        prediction=prediction,
        field_families=S4_FIELD_FAMILIES,
        field_aliases=_S4_FIELD_ALIASES,
    )


def _score_exect_document_for_families(
    *,
    gold: ExectGoldDocument,
    prediction: DocumentPrediction,
    field_families: tuple[str, ...],
    field_aliases: dict[str, str],
) -> ExectDocumentScore:
    gold_by_family = _gold_values_by_family(gold, field_families=field_families)
    predicted_by_family = _prediction_values_by_family(
        prediction,
        field_families=field_families,
        field_aliases=field_aliases,
    )
    field_scores = {
        family: _score_field_family(
            field_family=family,
            gold_values=gold_by_family[family],
            predicted_values=predicted_by_family[family],
        )
        for family in field_families
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


def _gold_values_by_family(
    gold: ExectGoldDocument,
    *,
    field_families: tuple[str, ...],
) -> dict[str, list[str]]:
    mapping = {
        "diagnosis": gold.diagnoses,
        "seizure_type": gold.seizure_types,
        "annotated_medication": gold.current_medications,
        "investigation": gold.investigations,
        "comorbidity": gold.comorbidities,
        "birth_history": gold.birth_histories,
        "onset": gold.onsets,
        "epilepsy_cause": gold.epilepsy_causes,
        "when_diagnosed": gold.when_diagnosed,
        "seizure_frequency": gold.seizure_frequencies,
        "medication_temporality": gold.medication_temporalities,
    }
    return {family: mapping[family] for family in field_families}


def score_exect_prediction_set(
    prediction_set: PredictionSet,
    *,
    gold_documents: Iterable[ExectGoldDocument] | None = None,
) -> dict[str, Any]:
    return _score_exect_prediction_set_for_families(
        prediction_set,
        gold_documents=gold_documents,
        field_families=FIELD_FAMILIES,
        field_aliases=_FIELD_ALIASES,
        scorer=EXECT_SCORER,
        caveats=[
            "ExECT benchmark-facing fields are limited to audited diagnosis, seizure type, and annotated medication.",
            "Medication scoring uses annotated prescriptions only; planned/current status is not benchmark-facing.",
            "Raw diagnoses and gold quality flags are diagnostic context and are not scored as extra benchmark labels.",
            "Evidence metrics are diagnostic source-grounding checks and are not part of benchmark-facing field-family F1.",
        ],
    )


def score_exect_s2_prediction_set(
    prediction_set: PredictionSet,
    *,
    gold_documents: Iterable[ExectGoldDocument] | None = None,
) -> dict[str, Any]:
    return _score_exect_prediction_set_for_families(
        prediction_set,
        gold_documents=gold_documents,
        field_families=S2_FIELD_FAMILIES,
        field_aliases=_S2_FIELD_ALIASES,
        scorer=EXECT_S2_SCORER,
        caveats=[
            "ExECT S2 benchmark-facing fields extend audited S1 with investigation and comorbidity families.",
            "Investigation labels use modality+result canonical strings (eeg/mri/ct + normal/abnormal/unknown).",
            "Comorbidity labels come from affirmed PatientHistory annotations excluding seizure-history phrases.",
            "This is a partial ExECTv2 diagnostic view, not CUI-aware Table 1 reproduction.",
            "Medication scoring uses annotated prescriptions only; planned/current status is not benchmark-facing.",
            "Evidence metrics are diagnostic source-grounding checks and are not part of benchmark-facing field-family F1.",
        ],
    )


def score_exect_s3_prediction_set(
    prediction_set: PredictionSet,
    *,
    gold_documents: Iterable[ExectGoldDocument] | None = None,
) -> dict[str, Any]:
    return _score_exect_prediction_set_for_families(
        prediction_set,
        gold_documents=gold_documents,
        field_families=S3_FIELD_FAMILIES,
        field_aliases=_S3_FIELD_ALIASES,
        scorer=EXECT_S3_SCORER,
        caveats=[
            "ExECT S3 benchmark-facing fields extend frozen S2 with birth history, onset, epilepsy cause, and when diagnosed.",
            "S3 gold uses affirmed BirthHistory, Onset, EpilepsyCause, and WhenDiagnosed JSON entities only.",
            "Overlapping phrases across families (for example meningitis as cause vs comorbidity) are scored independently per family.",
            "Onset and when_diagnosed gold are CUIPhrase surfaces; temporal age/year attributes are not benchmark labels.",
            "This is a partial ExECTv2 diagnostic view, not CUI-aware Table 1 reproduction.",
            "Medication scoring uses annotated prescriptions only; planned/current status is not benchmark-facing.",
            "Evidence metrics are diagnostic source-grounding checks and are not part of benchmark-facing field-family F1.",
        ],
    )


def score_exect_s4_prediction_set(
    prediction_set: PredictionSet,
    *,
    gold_documents: Iterable[ExectGoldDocument] | None = None,
) -> dict[str, Any]:
    return _score_exect_prediction_set_for_families(
        prediction_set,
        gold_documents=gold_documents,
        field_families=S4_FIELD_FAMILIES,
        field_aliases=_S4_FIELD_ALIASES,
        scorer=EXECT_S4_SCORER,
        caveats=[
            "ExECT S4 benchmark-facing fields extend frozen S3 with seizure frequency and medication temporality.",
            "Seizure-frequency gold uses SeizureFrequency JSON entities; see docs/exect_s4_gold_policy.md.",
            "Medication temporality gold is inferred from annotated Prescription span text; JSON has no temporality column.",
            "Planned medications mentioned in letters but not tagged as Prescription are absent from gold.",
            "Overlapping phrases across families are scored independently per family.",
            "This is a partial ExECTv2 diagnostic view, not CUI-aware Table 1 reproduction.",
            "Evidence metrics are diagnostic source-grounding checks and are not part of benchmark-facing field-family F1.",
        ],
    )


def _score_exect_prediction_set_for_families(
    prediction_set: PredictionSet,
    *,
    gold_documents: Iterable[ExectGoldDocument] | None,
    field_families: tuple[str, ...],
    field_aliases: dict[str, str],
    scorer: str,
    caveats: list[str],
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
        _score_exect_document_for_families(
            gold=gold_by_id[document_id],
            prediction=predictions_by_id[document_id],
            field_families=field_families,
            field_aliases=field_aliases,
        )
        for document_id in evaluated_ids
    ]

    field_totals = {
        family: {"tp": 0, "fp": 0, "fn": 0, "support": 0} for family in field_families
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
    evidence_diagnostics = _evidence_diagnostics(
        gold_by_id=gold_by_id,
        predictions_by_id=predictions_by_id,
        evaluated_ids=evaluated_ids,
        field_aliases=field_aliases,
    )

    return {
        "dataset": prediction_set.dataset,
        "schema_level": prediction_set.schema_level,
        "scorer": scorer,
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
            "evidence_quote_support_rate": _ratio(
                evidence_diagnostics["quote_supported"],
                evidence_diagnostics["values_with_evidence"],
            ),
            "evidence_quote_support_rate_without_repairs": _ratio(
                evidence_diagnostics["unrepaired_quote_supported"],
                evidence_diagnostics["unrepaired_values_with_evidence"],
            ),
            "evidence_quote_support_rate_repaired": _ratio(
                evidence_diagnostics["repaired_quote_supported"],
                evidence_diagnostics["repaired_values_with_evidence"],
            ),
            "evidence_quote_repair_rate": _ratio(
                evidence_diagnostics["repaired_values_with_evidence"],
                evidence_diagnostics["values_with_evidence"],
            ),
            "evidence_offsets_present_rate": _ratio(
                evidence_diagnostics["values_with_offsets"],
                evidence_diagnostics["values_with_evidence"],
            ),
            "evidence_offsets_valid_rate": _ratio(
                evidence_diagnostics["offsets_valid"],
                evidence_diagnostics["values_with_offsets"],
            ),
        },
        "caveats": caveats,
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
            "evidence_support_errors": evidence_diagnostics["errors"],
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
    *,
    field_families: tuple[str, ...] = FIELD_FAMILIES,
    field_aliases: dict[str, str] = _FIELD_ALIASES,
) -> dict[str, list[str]]:
    values_by_family = {family: [] for family in field_families}
    for value in prediction.values:
        family = field_aliases.get(value.field_name)
        if family is None:
            continue
        for raw_value in _raw_prediction_values(value.normalized_value, value.raw_value):
            normalized = _normalize_prediction_value(family, raw_value)
            if normalized and normalized not in values_by_family[family]:
                values_by_family[family].append(normalized)
    return values_by_family


def _evidence_diagnostics(
    *,
    gold_by_id: dict[str, ExectGoldDocument],
    predictions_by_id: dict[str, DocumentPrediction],
    evaluated_ids: list[str],
    field_aliases: dict[str, str] = _FIELD_ALIASES,
) -> dict[str, Any]:
    values_with_evidence = 0
    values_with_offsets = 0
    quote_supported = 0
    offsets_valid = 0
    repaired_values_with_evidence = 0
    repaired_quote_supported = 0
    unrepaired_values_with_evidence = 0
    unrepaired_quote_supported = 0
    errors: list[dict[str, Any]] = []

    for document_id in evaluated_ids:
        gold = gold_by_id[document_id]
        prediction = predictions_by_id[document_id]
        for value in prediction.values:
            family = field_aliases.get(value.field_name)
            if family is None:
                continue
            if not value.evidence:
                errors.append(
                    {
                        "document_id": document_id,
                        "field_name": value.field_name,
                        "raw_value": value.raw_value,
                        "reason": "prediction has no evidence spans",
                    }
                )
                continue

            evidence_score = score_evidence_support(
                document_text=gold.text,
                predicted_evidence=value.evidence,
            )
            used_repair = "evidence_repair:ellipsis_contiguous_span" in value.quality_flags
            values_with_evidence += 1
            has_offsets = evidence_score.predicted_evidence_with_offsets > 0
            values_with_offsets += int(has_offsets)
            quote_supported += int(evidence_score.quote_supported)
            offsets_valid += int(evidence_score.offsets_valid is True)
            if used_repair:
                repaired_values_with_evidence += 1
                repaired_quote_supported += int(evidence_score.quote_supported)
            else:
                unrepaired_values_with_evidence += 1
                unrepaired_quote_supported += int(evidence_score.quote_supported)

            if not evidence_score.quote_supported:
                errors.append(
                    {
                        "document_id": document_id,
                        "field_name": value.field_name,
                        "raw_value": value.raw_value,
                        "predicted_evidence": [
                            evidence.model_dump(mode="json")
                            for evidence in value.evidence
                        ],
                        "reason": "predicted evidence quote or offsets not supported by document text",
                    }
                )

    return {
        "values_with_evidence": values_with_evidence,
        "values_with_offsets": values_with_offsets,
        "quote_supported": quote_supported,
        "offsets_valid": offsets_valid,
        "repaired_values_with_evidence": repaired_values_with_evidence,
        "repaired_quote_supported": repaired_quote_supported,
        "unrepaired_values_with_evidence": unrepaired_values_with_evidence,
        "unrepaired_quote_supported": unrepaired_quote_supported,
        "errors": errors,
    }


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
    if field_family == "investigation":
        return normalize_investigation_phrase(value)
    if field_family == "comorbidity":
        return canonical_comorbidity_label(value)
    if field_family == "birth_history":
        return canonical_birth_history_label(value)
    if field_family == "onset":
        return canonical_onset_label(value)
    if field_family == "epilepsy_cause":
        return canonical_epilepsy_cause_label(value)
    if field_family == "when_diagnosed":
        return canonical_when_diagnosed_label(value)
    if field_family == "seizure_frequency":
        return canonical_clinical_phrase(value)
    if field_family == "medication_temporality":
        if "|" not in value:
            return canonical_clinical_phrase(value)
        medication, temporality = value.split("|", 1)
        return f"{canonical_medication_name(medication)}|{canonical_clinical_phrase(temporality)}"
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
