import pytest

from clinical_extraction.gan.paper_reproduction_scoring import (
    paper_label_to_monthly_frequency,
    paper_pragmatic_category,
    paper_purist_category,
)
from clinical_extraction.gan.scoring import score_gan_frequency_prediction


def test_paper_reproduction_collapses_no_reference_into_unknown_category():
    canonical = score_gan_frequency_prediction(
        gold_label="unknown",
        predicted_label="no seizure frequency reference",
    )
    paper = score_gan_frequency_prediction(
        gold_label="unknown",
        predicted_label="no seizure frequency reference",
        scorer_mode="gan2026_paper_reproduction",
    )

    assert canonical.gold_monthly_frequency == pytest.approx(1000)
    assert canonical.predicted_monthly_frequency == pytest.approx(0)
    assert not canonical.monthly_frequency_match
    assert paper.gold_monthly_frequency == pytest.approx(1000)
    assert paper.predicted_monthly_frequency == pytest.approx(1000)
    assert paper.monthly_frequency_match
    assert paper.gold_purist_category == "seizure_freq_unknown"
    assert paper.predicted_pragmatic_category == "seizure_freq_unknown"


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("multiple per week", 2 * 365 / 7 / 12),
        ("multiple per month", 8 * 365 / 30 / 12),
        ("multiple per year", 18 / 12),
        ("1 cluster per week, multiple per cluster", 2 * 365 / 7 / 12),
    ],
)
def test_paper_reproduction_uses_dynamic_multiple_policy(label: str, expected: float):
    assert paper_label_to_monthly_frequency(label) == pytest.approx(expected)


def test_paper_reproduction_averages_final_rate_bounds_for_ranges():
    assert paper_label_to_monthly_frequency("1 per 2 to 3 month") == pytest.approx(
        ((1 * 365 / (3 * 30)) + (1 * 365 / (2 * 30))) / 2 / 12
    )


def test_paper_reproduction_cluster_labels_convert_through_365_day_month_math():
    assert paper_label_to_monthly_frequency(
        "2 cluster per month, 6 per cluster"
    ) == pytest.approx(12 * 365 / 30 / 12)


def test_paper_reproduction_categories_use_author_evaluator_names():
    assert paper_purist_category("seizure free for 6 month") == "currently_no_seizure"
    assert paper_pragmatic_category("seizure free for 6 month") == "currently_no_seizure"
    assert paper_purist_category("1 per week") == "seizure_freq_more1week_less1day"
    assert paper_pragmatic_category("multiple per year") == "seizure_frequent"


def test_paper_prediction_repair_is_explicit_and_scorer_only():
    unrepaired = score_gan_frequency_prediction(
        gold_label="3 per week",
        predicted_label="3x a week",
        scorer_mode="gan2026_paper_reproduction",
    )
    repaired = score_gan_frequency_prediction(
        gold_label="3 per week",
        predicted_label="3x a week",
        scorer_mode="gan2026_paper_reproduction",
        apply_paper_prediction_repair=True,
    )

    assert not unrepaired.monthly_frequency_match
    assert unrepaired.predicted_monthly_frequency == pytest.approx(-1000)
    assert repaired.normalized_predicted_label == "3 per week"
    assert repaired.monthly_frequency_match


def test_paper_prediction_range_tolerance_is_explicit():
    strict = score_gan_frequency_prediction(
        gold_label="1 per 2 month",
        predicted_label="1 per 2 to 3 month",
        scorer_mode="gan2026_paper_reproduction",
    )
    ranged = score_gan_frequency_prediction(
        gold_label="1 per 2 month",
        predicted_label="1 per 2 to 3 month",
        scorer_mode="gan2026_paper_reproduction",
        allow_prediction_range=True,
    )

    assert not strict.monthly_frequency_match
    assert ranged.monthly_frequency_match


def test_canonical_default_mode_stays_separate_from_paper_reproduction():
    canonical = score_gan_frequency_prediction(
        gold_label="multiple per year",
        predicted_label="multiple per year",
    )
    paper = score_gan_frequency_prediction(
        gold_label="multiple per year",
        predicted_label="multiple per year",
        scorer_mode="gan2026_paper_reproduction",
    )

    assert canonical.gold_monthly_frequency == pytest.approx(3 / 12)
    assert paper.gold_monthly_frequency == pytest.approx(18 / 12)
