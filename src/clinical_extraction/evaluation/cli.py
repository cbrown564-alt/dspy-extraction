from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.scoring import score_gan_frequency_prediction
from clinical_extraction.schemas import DocumentPrediction, PredictionSet

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

    for record_id in evaluated_ids:
        gold = gold_by_id[record_id]
        prediction = predictions_by_id[record_id]
        predicted_label = _gan_frequency_label(prediction)
        if predicted_label is None:
            invalid_predictions.append(
                {
                    "record_id": record_id,
                    "reason": f"missing {GAN_FREQUENCY_FIELD} prediction",
                    "gold_label": gold.gold_label,
                }
            )
            continue

        try:
            score = score_gan_frequency_prediction(
                gold_label=gold.gold_label,
                predicted_label=predicted_label,
            )
        except ValueError as exc:
            invalid_predictions.append(
                {
                    "record_id": record_id,
                    "reason": str(exc),
                    "gold_label": gold.gold_label,
                    "predicted_label": predicted_label,
                }
            )
            continue

        metric_counts["raw_exact_match"] += gold.gold_label == predicted_label
        metric_counts["normalized_label_match"] += score.exact_normalized_match
        metric_counts["monthly_frequency_match"] += score.monthly_frequency_match
        metric_counts["purist_category_match"] += score.purist_category_match
        metric_counts["pragmatic_category_match"] += score.pragmatic_category_match

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

    denominator = len(evaluated_ids)
    valid_denominator = denominator - len(invalid_predictions)
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
        },
        "caveats": [
            "Gan primary gold is check__Seizure Frequency Number.seizure_frequency_number[0].",
            "Raw exact and normalized-label exact metrics are diagnostic, not benchmark-facing.",
        ],
        "errors": {
            "missing_prediction_ids": missing_ids[:max_errors],
            "extra_prediction_ids": extra_ids[:max_errors],
            "invalid_predictions": invalid_predictions[:max_errors],
            "monthly_frequency_mismatches": error_samples,
        },
    }


def _gan_frequency_label(prediction: DocumentPrediction) -> str | None:
    for value in prediction.values:
        if value.field_name != GAN_FREQUENCY_FIELD:
            continue
        if isinstance(value.normalized_value, str):
            return value.normalized_value
        return value.raw_value
    return None


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


if __name__ == "__main__":
    raise SystemExit(main())
