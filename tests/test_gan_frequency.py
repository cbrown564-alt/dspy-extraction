import pytest

from clinical_extraction.gan.frequency import (
    canonicalize_leading_inequality_label,
    gan_label_policy_failure_class,
    label_to_monthly_frequency,
    normalize_label,
    pragmatic_category,
    purist_category,
)


def test_plural_units_are_normalized():
    assert normalize_label("seizure free for 6 months") == "seizure free for 6 month"
    assert normalize_label("seizure free for 2 years") == "seizure free for 2 year"


def test_year_month_equivalent_rates_convert_to_same_monthly_frequency():
    assert label_to_monthly_frequency("12 per 1 year") == pytest.approx(
        label_to_monthly_frequency("1 per 1 month")
    )


def test_cluster_label_multiplies_cluster_rate_by_seizures_per_cluster():
    assert label_to_monthly_frequency("2 cluster per month, 6 per cluster") == pytest.approx(12)


def test_unknown_and_no_reference_stay_distinct_categories():
    assert label_to_monthly_frequency("unknown") == pytest.approx(1000)
    assert label_to_monthly_frequency("unknown, 2 to 3 per cluster") == pytest.approx(1000)
    assert label_to_monthly_frequency("no seizure frequency reference") == pytest.approx(0)
    assert purist_category("unknown") == "unknown"
    assert purist_category("unknown, 2 to 3 per cluster") == "unknown"
    assert purist_category("no seizure frequency reference") == "no_seizure_information"
    assert pragmatic_category("unknown") == "unknown"
    assert pragmatic_category("unknown, 2 to 3 per cluster") == "unknown"
    assert pragmatic_category("no seizure frequency reference") == "no_seizure_information"


@pytest.mark.parametrize(
    "label",
    [
        "unknown, 6 per hour",
        "unknown, 3 per week",
        "unknown, 2 per month",
    ],
)
def test_unknown_suffix_must_be_per_cluster(label: str):
    with pytest.raises(ValueError, match="Unsupported Gan frequency label"):
        label_to_monthly_frequency(label)


@pytest.mark.parametrize(
    ("label", "failure_class"),
    [
        ("unknown, 2 per month", "unknown_quantified_hybrid"),
        (None, "abstention_or_missing_value"),
        ("2 per week, 1 per 2 week", "multiple_frequency_labels"),
        ("<= 2 per day", "inequality_operator"),
        (
            "3 per week, drop attacks in batches",
            "prose_appended_label",
        ),
        (
            "2 to 3 cluster per week, unknown, multiple per cluster",
            "malformed_cluster_unknown_slot",
        ),
    ],
)
def test_gan_label_policy_failure_class_covers_r1_1_invalid_schema_classes(
    label: str | None,
    failure_class: str,
):
    assert gan_label_policy_failure_class(label) == failure_class


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("<= 2 per day", "2 per day"),
        ("≤ 7 to 8 per month", "7 to 8 per month"),
        ("at most 3 per week", "3 per week"),
    ],
)
def test_leading_inequality_surface_can_be_canonicalized_narrowly(
    label: str,
    expected: str,
):
    assert canonicalize_leading_inequality_label(label) == expected


@pytest.mark.parametrize(
    "label",
    [
        "unknown, 2 per month",
        "2 per week, 1 per 2 week",
        "3 per week, drop attacks in batches",
    ],
)
def test_leading_inequality_repair_rejects_non_inequality_invalid_surfaces(label: str):
    assert canonicalize_leading_inequality_label(label) is None
