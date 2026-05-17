import pytest

from clinical_extraction.gan.frequency import (
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
    assert label_to_monthly_frequency("no seizure frequency reference") == pytest.approx(0)
    assert purist_category("unknown") == "unknown"
    assert purist_category("no seizure frequency reference") == "no_seizure_information"
    assert pragmatic_category("unknown") == "unknown"
    assert pragmatic_category("no seizure frequency reference") == "no_seizure_information"
