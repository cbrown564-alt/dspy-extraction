from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.gan.frequency import (
    label_to_monthly_frequency,
    normalize_label,
    pragmatic_category,
    purist_category,
)
from clinical_extraction.gan.paper_reproduction_scoring import (
    convert_paper_label,
    paper_pragmatic_category,
    paper_purist_category,
)

GAN_CANONICAL_SCORER = "gan_frequency_deterministic_v1"
GAN_PAPER_REPRODUCTION_SCORER = "gan2026_paper_reproduction"


class GanFrequencyScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    scorer_mode: str = GAN_CANONICAL_SCORER
    gold_label: str
    predicted_label: str
    normalized_gold_label: str
    normalized_predicted_label: str
    exact_normalized_match: bool
    gold_monthly_frequency: float
    predicted_monthly_frequency: float
    monthly_frequency_match: bool
    gold_purist_category: str
    predicted_purist_category: str
    purist_category_match: bool
    gold_pragmatic_category: str
    predicted_pragmatic_category: str
    pragmatic_category_match: bool
    scorer_options: dict[str, bool] = Field(default_factory=dict)


def score_gan_frequency_prediction(
    *,
    gold_label: str,
    predicted_label: str,
    monthly_tolerance: float = 1e-9,
    scorer_mode: str = GAN_CANONICAL_SCORER,
    apply_paper_prediction_repair: bool = False,
    allow_prediction_range: bool = False,
    allow_error_tolerance: bool = False,
) -> GanFrequencyScore:
    if scorer_mode == GAN_PAPER_REPRODUCTION_SCORER:
        return _score_gan_paper_reproduction_prediction(
            gold_label=gold_label,
            predicted_label=predicted_label,
            monthly_tolerance=monthly_tolerance,
            apply_paper_prediction_repair=apply_paper_prediction_repair,
            allow_prediction_range=allow_prediction_range,
            allow_error_tolerance=allow_error_tolerance,
        )
    if scorer_mode != GAN_CANONICAL_SCORER:
        raise ValueError(f"Unsupported Gan scorer mode: {scorer_mode!r}")

    normalized_gold = normalize_label(gold_label)
    normalized_predicted = normalize_label(predicted_label)
    gold_monthly = label_to_monthly_frequency(normalized_gold)
    predicted_monthly = label_to_monthly_frequency(normalized_predicted)
    gold_purist = purist_category(normalized_gold)
    predicted_purist = purist_category(normalized_predicted)
    gold_pragmatic = pragmatic_category(normalized_gold)
    predicted_pragmatic = pragmatic_category(normalized_predicted)

    return GanFrequencyScore(
        scorer_mode=GAN_CANONICAL_SCORER,
        gold_label=gold_label,
        predicted_label=predicted_label,
        normalized_gold_label=normalized_gold,
        normalized_predicted_label=normalized_predicted,
        exact_normalized_match=normalized_gold == normalized_predicted,
        gold_monthly_frequency=gold_monthly,
        predicted_monthly_frequency=predicted_monthly,
        monthly_frequency_match=math.isclose(
            gold_monthly,
            predicted_monthly,
            rel_tol=monthly_tolerance,
            abs_tol=monthly_tolerance,
        ),
        gold_purist_category=gold_purist,
        predicted_purist_category=predicted_purist,
        purist_category_match=gold_purist == predicted_purist,
        gold_pragmatic_category=gold_pragmatic,
        predicted_pragmatic_category=predicted_pragmatic,
        pragmatic_category_match=gold_pragmatic == predicted_pragmatic,
    )


def _score_gan_paper_reproduction_prediction(
    *,
    gold_label: str,
    predicted_label: str,
    monthly_tolerance: float,
    apply_paper_prediction_repair: bool,
    allow_prediction_range: bool,
    allow_error_tolerance: bool,
) -> GanFrequencyScore:
    gold = convert_paper_label(gold_label)
    predicted = convert_paper_label(
        predicted_label,
        apply_prediction_repair=apply_paper_prediction_repair,
    )
    predicted_monthly = predicted.monthly_frequency
    monthly_match = math.isclose(
        gold.monthly_frequency,
        predicted_monthly,
        rel_tol=monthly_tolerance,
        abs_tol=monthly_tolerance,
    )

    if (
        allow_prediction_range
        and predicted.min_monthly_frequency is not None
        and predicted.max_monthly_frequency is not None
        and predicted.min_monthly_frequency <= gold.monthly_frequency <= predicted.max_monthly_frequency
    ):
        predicted_monthly = gold.monthly_frequency
        monthly_match = True

    if (
        allow_error_tolerance
        and not monthly_match
        and gold.monthly_frequency != 0
        and gold.monthly_frequency / 1.5 <= predicted_monthly <= gold.monthly_frequency * 1.5
    ):
        predicted_monthly = gold.monthly_frequency
        monthly_match = True

    gold_purist = paper_purist_category(gold.monthly_frequency)
    predicted_purist = paper_purist_category(predicted_monthly)
    gold_pragmatic = paper_pragmatic_category(gold.monthly_frequency)
    predicted_pragmatic = paper_pragmatic_category(predicted_monthly)

    return GanFrequencyScore(
        scorer_mode=GAN_PAPER_REPRODUCTION_SCORER,
        gold_label=gold_label,
        predicted_label=predicted_label,
        normalized_gold_label=gold.normalized_label,
        normalized_predicted_label=predicted.normalized_label,
        exact_normalized_match=gold.normalized_label == predicted.normalized_label,
        gold_monthly_frequency=gold.monthly_frequency,
        predicted_monthly_frequency=predicted_monthly,
        monthly_frequency_match=monthly_match,
        gold_purist_category=gold_purist,
        predicted_purist_category=predicted_purist,
        purist_category_match=gold_purist == predicted_purist,
        gold_pragmatic_category=gold_pragmatic,
        predicted_pragmatic_category=predicted_pragmatic,
        pragmatic_category_match=gold_pragmatic == predicted_pragmatic,
        scorer_options={
            "apply_paper_prediction_repair": apply_paper_prediction_repair,
            "allow_prediction_range": allow_prediction_range,
            "allow_error_tolerance": allow_error_tolerance,
        },
    )
