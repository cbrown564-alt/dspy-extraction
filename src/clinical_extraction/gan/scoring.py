from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict

from clinical_extraction.gan.frequency import (
    label_to_monthly_frequency,
    normalize_label,
    pragmatic_category,
    purist_category,
)


class GanFrequencyScore(BaseModel):
    model_config = ConfigDict(frozen=True)

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


def score_gan_frequency_prediction(
    *,
    gold_label: str,
    predicted_label: str,
    monthly_tolerance: float = 1e-9,
) -> GanFrequencyScore:
    normalized_gold = normalize_label(gold_label)
    normalized_predicted = normalize_label(predicted_label)
    gold_monthly = label_to_monthly_frequency(normalized_gold)
    predicted_monthly = label_to_monthly_frequency(normalized_predicted)
    gold_purist = purist_category(normalized_gold)
    predicted_purist = purist_category(normalized_predicted)
    gold_pragmatic = pragmatic_category(normalized_gold)
    predicted_pragmatic = pragmatic_category(normalized_predicted)

    return GanFrequencyScore(
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
