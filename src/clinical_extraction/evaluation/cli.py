from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.bootstrap import (
    build_bootstrap_confidence_intervals,
)
from clinical_extraction.evaluation.evidence import score_evidence_support
from clinical_extraction.evaluation.error_analysis import ErrorTaxonomy
from clinical_extraction.gan.scoring import score_gan_frequency_prediction
from clinical_extraction.schemas import DocumentPrediction, ExtractedValue, PredictionSet

GAN_FREQUENCY_FIELD = "seizure_frequency_number"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate stored clinical extraction predictions."
    )
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--max-errors",
        default=20,
        type=int,
        help="Maximum number of diagnostic error samples to write.",
    )
    parser.add_argument(
        "--bootstrap-samples",
        default=1000,
        type=int,
        help="Bootstrap resamples for metric confidence intervals.",
    )
    parser.add_argument(
        "--bootstrap-seed",
        default=0,
        type=int,
        help="Seed for bootstrap confidence interval resampling.",
    )
    args = parser.parse_args(argv)

    prediction_set = PredictionSet.model_validate_json(
        args.predictions.read_text(encoding="utf-8")
    )

    if prediction_set.dataset != "gan_2026":
        raise SystemExit(
            f"Unsupported dataset for deterministic CLI: {prediction_set.dataset!r}"
        )

    report = evaluate_gan_predictions(
        prediction_set,
        max_errors=args.max_errors,
        bootstrap_samples=args.bootstrap_samples,
        bootstrap_seed=args.bootstrap_seed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


def evaluate_gan_predictions(
    prediction_set: PredictionSet,
    *,
    max_errors: int = 20,
    bootstrap_samples: int = 1000,
    bootstrap_seed: int = 0,
) -> dict[str, Any]:
    gold_by_id = {record.record_id: record for record in load_gan_records()}
    predictions_by_id = {
        prediction.document_id: prediction for prediction in prediction_set.predictions
    }
    expected_ids = set(gold_by_id)
    predicted_ids = set(predictions_by_id)
    evaluated_ids = sorted(expected_ids & predicted_ids)
    missing_ids = sorted(expected_ids - predicted_ids)
    extra_ids = sorted(predicted_ids - expected_ids)

    metric_counts = {
        "raw_exact_match": 0,
        "normalized_label_match": 0,
        "monthly_frequency_match": 0,
        "purist_category_match": 0,
        "pragmatic_category_match": 0,
    }
    invalid_predictions: list[dict[str, Any]] = []
    error_samples: list[dict[str, Any]] = []
    evidence_error_samples: list[dict[str, Any]] = []
    evidence_counts = {
        "predictions_with_evidence": 0,
        "predictions_with_offsets": 0,
        "quote_supported": 0,
        "offsets_valid": 0,
    }
    metric_observations: dict[str, list[int]] = {
        "monthly_frequency_accuracy": [],
        "purist_category_accuracy": [],
        "pragmatic_category_accuracy": [],
        "raw_exact_accuracy": [],
        "normalized_label_accuracy": [],
        "schema_valid_prediction_rate": [],
        "evidence_quote_support_rate": [],
        "evidence_offsets_valid_rate": [],
        "evidence_offsets_present_rate": [],
    }
    taxonomy = ErrorTaxonomy(max_examples=max_errors)

    for record_id in missing_ids:
        taxonomy.add(
            "schema.missing_prediction",
            record_id=record_id,
            reason="gold record has no prediction",
        )
    for record_id in extra_ids:
        taxonomy.add(
            "schema.extra_prediction",
            record_id=record_id,
            reason="prediction does not match a gold record",
        )

    for record_id in evaluated_ids:
        gold = gold_by_id[record_id]
        prediction = predictions_by_id[record_id]
        predicted_value = _gan_frequency_value(prediction)
        if predicted_value is None:
            metric_observations["schema_valid_prediction_rate"].append(0)
            invalid_predictions.append(
                {
                    "record_id": record_id,
                    "reason": f"missing {GAN_FREQUENCY_FIELD} prediction",
                    "gold_label": gold.gold_label,
                }
            )
            taxonomy.add(
                "schema.missing_field",
                record_id=record_id,
                reason=f"missing {GAN_FREQUENCY_FIELD} prediction",
                details={"gold_label": gold.gold_label},
            )
            continue
        predicted_label = _prediction_label(predicted_value)
        if predicted_label is None:
            metric_observations["schema_valid_prediction_rate"].append(0)
            if "abstained" in predicted_value.quality_flags:
                taxonomy.add(
                    "abstention.predicted_abstention",
                    record_id=record_id,
                    reason="prediction value is flagged as abstained",
                )
            invalid_predictions.append(
                {
                    "record_id": record_id,
                    "reason": f"missing {GAN_FREQUENCY_FIELD} label value",
                    "gold_label": gold.gold_label,
                }
            )
            taxonomy.add(
                "schema.missing_value",
                record_id=record_id,
                reason=f"missing {GAN_FREQUENCY_FIELD} label value",
                details={"gold_label": gold.gold_label},
            )
            continue

        try:
            score = score_gan_frequency_prediction(
                gold_label=gold.gold_label,
                predicted_label=predicted_label,
            )
        except ValueError as exc:
            metric_observations["schema_valid_prediction_rate"].append(0)
            invalid_predictions.append(
                {
                    "record_id": record_id,
                    "reason": str(exc),
                    "gold_label": gold.gold_label,
                    "predicted_label": predicted_label,
                }
            )
            taxonomy.add(
                "normalization.invalid_label",
                record_id=record_id,
                reason=str(exc),
                details={
                    "gold_label": gold.gold_label,
                    "predicted_label": predicted_label,
                },
            )
            continue

        metric_observations["schema_valid_prediction_rate"].append(1)
        metric_counts["raw_exact_match"] += gold.gold_label == predicted_label
        metric_counts["normalized_label_match"] += score.exact_normalized_match
        metric_counts["monthly_frequency_match"] += score.monthly_frequency_match
        metric_counts["purist_category_match"] += score.purist_category_match
        metric_counts["pragmatic_category_match"] += score.pragmatic_category_match
        metric_observations["raw_exact_accuracy"].append(
            int(gold.gold_label == predicted_label)
        )
        metric_observations["normalized_label_accuracy"].append(
            int(score.exact_normalized_match)
        )
        metric_observations["monthly_frequency_accuracy"].append(
            int(score.monthly_frequency_match)
        )
        metric_observations["purist_category_accuracy"].append(
            int(score.purist_category_match)
        )
        metric_observations["pragmatic_category_accuracy"].append(
            int(score.pragmatic_category_match)
        )

        if not score.exact_normalized_match:
            taxonomy.add(
                "normalization.label_mismatch",
                record_id=record_id,
                reason="normalized predicted label differs from gold",
                details={
                    "normalized_gold_label": score.normalized_gold_label,
                    "normalized_predicted_label": score.normalized_predicted_label,
                },
            )
        if not score.monthly_frequency_match:
            taxonomy.add(
                "normalization.monthly_frequency_mismatch",
                record_id=record_id,
                reason="monthly frequency differs from gold",
                details={
                    "gold_monthly_frequency": score.gold_monthly_frequency,
                    "predicted_monthly_frequency": score.predicted_monthly_frequency,
                },
            )
        if not score.purist_category_match:
            taxonomy.add(
                "classification.purist_category_mismatch",
                record_id=record_id,
                reason="Purist category differs from gold",
                details={
                    "gold_purist_category": score.gold_purist_category,
                    "predicted_purist_category": score.predicted_purist_category,
                },
            )
        if not score.pragmatic_category_match:
            taxonomy.add(
                "classification.pragmatic_category_mismatch",
                record_id=record_id,
                reason="Pragmatic category differs from gold",
                details={
                    "gold_pragmatic_category": score.gold_pragmatic_category,
                    "predicted_pragmatic_category": score.predicted_pragmatic_category,
                },
            )
        if predicted_value.negation not in ("affirmed", "not_applicable", "unknown"):
            taxonomy.add(
                "negation.non_affirmed_prediction",
                record_id=record_id,
                reason="prediction carries a non-affirmed negation status",
                details={"negation": predicted_value.negation},
            )
        if predicted_value.temporality in ("historical", "planned", "future"):
            taxonomy.add(
                "temporality.non_current_prediction",
                record_id=record_id,
                reason="prediction carries a non-current temporality status",
                details={"temporality": predicted_value.temporality},
            )
        if "abstained" in predicted_value.quality_flags:
            taxonomy.add(
                "abstention.predicted_abstention",
                record_id=record_id,
                reason="prediction value is flagged as abstained",
            )
        if predicted_value.metadata.get("repair_applied") is True:
            taxonomy.add(
                "repair.applied",
                record_id=record_id,
                reason="prediction metadata indicates repair was applied",
            )

        if not score.monthly_frequency_match and len(error_samples) < max_errors:
            error_samples.append(
                {
                    "record_id": record_id,
                    "gold_label": score.gold_label,
                    "predicted_label": score.predicted_label,
                    "gold_monthly_frequency": score.gold_monthly_frequency,
                    "predicted_monthly_frequency": score.predicted_monthly_frequency,
                    "gold_pragmatic_category": score.gold_pragmatic_category,
                    "predicted_pragmatic_category": score.predicted_pragmatic_category,
                }
            )

        evidence_score = score_evidence_support(
            document_text=gold.note_text,
            predicted_evidence=predicted_value.evidence,
        )
        if evidence_score.predicted_evidence_count:
            evidence_counts["predictions_with_evidence"] += 1
            evidence_counts["predictions_with_offsets"] += (
                evidence_score.predicted_evidence_with_offsets > 0
            )
            evidence_counts["quote_supported"] += evidence_score.quote_supported
            evidence_counts["offsets_valid"] += evidence_score.offsets_valid is True
            metric_observations["evidence_quote_support_rate"].append(
                int(evidence_score.quote_supported)
            )
            metric_observations["evidence_offsets_present_rate"].append(
                int(evidence_score.predicted_evidence_with_offsets > 0)
            )
            if evidence_score.offsets_valid is not None:
                metric_observations["evidence_offsets_valid_rate"].append(
                    int(evidence_score.offsets_valid)
                )
            if evidence_score.offsets_valid is False:
                taxonomy.add(
                    "evidence.invalid_offsets",
                    record_id=record_id,
                    reason="predicted evidence offsets do not match document text",
                )
            if (
                not evidence_score.quote_supported
                and len(evidence_error_samples) < max_errors
            ):
                taxonomy.add(
                    "evidence.unsupported_quote",
                    record_id=record_id,
                    reason="predicted evidence quote or offsets not supported by document text",
                )
                evidence_error_samples.append(
                    {
                        "record_id": record_id,
                        "predicted_evidence": [
                            evidence.model_dump(mode="json")
                            for evidence in predicted_value.evidence
                        ],
                        "reason": "predicted evidence quote or offsets not supported by document text",
                    }
                )
        else:
            taxonomy.add(
                "evidence.missing_prediction_evidence",
                record_id=record_id,
                reason="prediction has no evidence spans",
            )

    denominator = len(evaluated_ids)
    valid_denominator = denominator - len(invalid_predictions)
    evidence_denominator = evidence_counts["predictions_with_evidence"]
    offset_denominator = evidence_counts["predictions_with_offsets"]
    confidence_intervals = build_bootstrap_confidence_intervals(
        metric_observations,
        samples=bootstrap_samples,
        seed=bootstrap_seed,
    )
    return {
        "dataset": prediction_set.dataset,
        "schema_level": prediction_set.schema_level,
        "scorer": "gan_frequency_deterministic_v1",
        "counts": {
            "gold_records": len(expected_ids),
            "predicted_records": len(predicted_ids),
            "evaluated_records": denominator,
            "valid_predictions": valid_denominator,
            "invalid_predictions": len(invalid_predictions),
            "missing_predictions": len(missing_ids),
            "extra_predictions": len(extra_ids),
        },
        "benchmark_metrics": {
            "monthly_frequency_accuracy": _ratio(
                metric_counts["monthly_frequency_match"], valid_denominator
            ),
            "purist_category_accuracy": _ratio(
                metric_counts["purist_category_match"], valid_denominator
            ),
            "pragmatic_category_accuracy": _ratio(
                metric_counts["pragmatic_category_match"], valid_denominator
            ),
        },
        "diagnostic_metrics": {
            "raw_exact_accuracy": _ratio(
                metric_counts["raw_exact_match"], valid_denominator
            ),
            "normalized_label_accuracy": _ratio(
                metric_counts["normalized_label_match"], valid_denominator
            ),
            "schema_valid_prediction_rate": _ratio(valid_denominator, denominator),
            "evidence_quote_support_rate": _ratio(
                evidence_counts["quote_supported"], evidence_denominator
            ),
            "evidence_offsets_valid_rate": _ratio(
                evidence_counts["offsets_valid"], offset_denominator
            ),
            "evidence_offsets_present_rate": _ratio(
                evidence_counts["predictions_with_offsets"], evidence_denominator
            ),
        },
        "confidence_intervals": confidence_intervals,
        "caveats": [
            "Gan primary gold is check__Seizure Frequency Number.seizure_frequency_number[0].",
            "Raw exact and normalized-label exact metrics are diagnostic, not benchmark-facing.",
            "Evidence metrics are diagnostic source-grounding checks: predicted evidence is evaluated by deterministic quote/offset support in the note text, not by overlap with Gan evidence annotations.",
        ],
        "errors": {
            "missing_prediction_ids": missing_ids[:max_errors],
            "extra_prediction_ids": extra_ids[:max_errors],
            "invalid_predictions": invalid_predictions[:max_errors],
            "monthly_frequency_mismatches": error_samples,
            "evidence_support_errors": evidence_error_samples,
        },
        "error_analysis": taxonomy.to_report(),
    }


def _gan_frequency_value(prediction: DocumentPrediction) -> ExtractedValue | None:
    for value in prediction.values:
        if value.field_name == GAN_FREQUENCY_FIELD:
            return value
    return None


def _prediction_label(value: ExtractedValue) -> str | None:
    if isinstance(value.normalized_value, str):
        return value.normalized_value
    return value.raw_value


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


if __name__ == "__main__":
    raise SystemExit(main())
