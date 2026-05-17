from __future__ import annotations

from collections import Counter
from typing import Any, Callable, Iterable

from clinical_extraction.gan.frequency import pragmatic_category, purist_category
from clinical_extraction.gan.scoring import score_gan_frequency_prediction
from clinical_extraction.schemas import GanRecord

PredictionFixture = Callable[[GanRecord], str]


def build_gan_deterministic_baseline_report(
    records: Iterable[GanRecord],
) -> dict[str, Any]:
    """Summarize deterministic Gan scorer behavior on gold-derived fixtures."""

    records = list(records)
    fixtures: dict[str, PredictionFixture] = {
        "gold_copy": lambda record: record.gold_label,
        "surface_variant_normalization": lambda record: _surface_variant_label(
            record.gold_label
        ),
        "pragmatic_bucket_proxy": lambda record: _pragmatic_bucket_proxy(
            record.gold_label
        ),
    }

    return {
        "dataset": "gan_2026",
        "scorer": "gan_frequency_deterministic_v1",
        "counts": {
            "gold_records": len(records),
            "row_ok_records": sum(record.row_ok for record in records),
            "row_not_ok_records": sum(not record.row_ok for record in records),
            "hard_cases": sum("hard_case" in record.flags for record in records),
            "unknown_gold": sum(record.gold_label == "unknown" for record in records),
            "no_seizure_frequency_reference_gold": sum(
                record.gold_label == "no seizure frequency reference"
                for record in records
            ),
        },
        "gold_distribution": _gold_distribution(records),
        "prediction_fixtures": {
            name: _score_fixture(records, predict)
            for name, predict in fixtures.items()
        },
        "interpretation": [
            (
                "gold_copy is an upper-bound sanity check; all deterministic "
                "metrics should be perfect."
            ),
            (
                "surface_variant_normalization pluralizes time units to show that "
                "normalized and monthly metrics are stable when raw strings differ."
            ),
            (
                "pragmatic_bucket_proxy predicts only coarse Pragmatic categories; "
                "it preserves pragmatic accuracy while losing raw and monthly fidelity."
            ),
        ],
        "caveats": [
            "Gan primary gold is check__Seizure Frequency Number.seizure_frequency_number[0].",
            "Reference labels mark secondary cross-check agreement and hard cases; they are not benchmark gold.",
            "Raw exact and normalized-label exact metrics are diagnostic, not benchmark-facing.",
            "Fixture predictions are deterministic probes of scorer behavior, not model outputs.",
        ],
    }


def _gold_distribution(records: list[GanRecord]) -> dict[str, dict[str, int]]:
    return {
        "pragmatic_category_counts": dict(
            Counter(pragmatic_category(record.gold_label) for record in records)
        ),
        "purist_category_counts": dict(
            Counter(purist_category(record.gold_label) for record in records)
        ),
        "label_counts": dict(Counter(record.gold_label for record in records)),
    }


def _score_fixture(
    records: list[GanRecord],
    predict: PredictionFixture,
) -> dict[str, float | int]:
    counts = {
        "raw_exact_match": 0,
        "normalized_label_match": 0,
        "monthly_frequency_match": 0,
        "purist_category_match": 0,
        "pragmatic_category_match": 0,
    }
    for record in records:
        predicted_label = predict(record)
        score = score_gan_frequency_prediction(
            gold_label=record.gold_label,
            predicted_label=predicted_label,
        )
        counts["raw_exact_match"] += record.gold_label == predicted_label
        counts["normalized_label_match"] += score.exact_normalized_match
        counts["monthly_frequency_match"] += score.monthly_frequency_match
        counts["purist_category_match"] += score.purist_category_match
        counts["pragmatic_category_match"] += score.pragmatic_category_match

    denominator = len(records)
    return {
        "evaluated_records": denominator,
        "raw_exact_accuracy": _ratio(counts["raw_exact_match"], denominator),
        "normalized_label_accuracy": _ratio(
            counts["normalized_label_match"], denominator
        ),
        "monthly_frequency_accuracy": _ratio(
            counts["monthly_frequency_match"], denominator
        ),
        "purist_category_accuracy": _ratio(
            counts["purist_category_match"], denominator
        ),
        "pragmatic_category_accuracy": _ratio(
            counts["pragmatic_category_match"], denominator
        ),
    }


def _surface_variant_label(label: str) -> str:
    return (
        label.replace(" month", " months")
        .replace(" year", " years")
        .replace(" week", " weeks")
        .replace(" day", " days")
    )


def _pragmatic_bucket_proxy(label: str) -> str:
    category = pragmatic_category(label)
    if category == "no_seizure_information":
        return "no seizure frequency reference"
    if category == "unknown":
        return "unknown"
    if category == "infrequent":
        return "1 per 1 month"
    if category == "frequent":
        return "1 per 1 week"
    raise ValueError(f"Unsupported Pragmatic category: {category!r}")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
