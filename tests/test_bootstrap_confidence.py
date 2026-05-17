import pytest

from clinical_extraction.evaluation.bootstrap import (
    bootstrap_mean_interval,
    build_bootstrap_confidence_intervals,
)


def test_bootstrap_mean_interval_is_seeded_and_reports_sampling_metadata():
    interval = bootstrap_mean_interval(
        [1, 0, 1, 1],
        samples=200,
        seed=17,
        confidence_level=0.90,
    )

    assert interval["point_estimate"] == 0.75
    assert interval["n"] == 4
    assert interval["bootstrap_samples"] == 200
    assert interval["seed"] == 17
    assert interval["confidence_level"] == 0.90
    assert interval["method"] == "percentile_bootstrap_mean"
    assert 0.0 <= interval["lower"] <= interval["point_estimate"]
    assert interval["point_estimate"] <= interval["upper"] <= 1.0


def test_bootstrap_mean_interval_returns_degenerate_interval_for_constant_values():
    interval = bootstrap_mean_interval([1, 1, 1], samples=50, seed=3)

    assert interval["point_estimate"] == 1.0
    assert interval["lower"] == 1.0
    assert interval["upper"] == 1.0


def test_build_bootstrap_confidence_intervals_skips_empty_metrics():
    intervals = build_bootstrap_confidence_intervals(
        {
            "monthly_frequency_accuracy": [1, 0, 1],
            "evidence_quote_support_rate": [],
        },
        samples=100,
        seed=11,
    )

    assert sorted(intervals) == ["monthly_frequency_accuracy"]


def test_bootstrap_mean_interval_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="at least one observation"):
        bootstrap_mean_interval([], samples=10, seed=1)
    with pytest.raises(ValueError, match="samples"):
        bootstrap_mean_interval([1], samples=0, seed=1)
    with pytest.raises(ValueError, match="confidence_level"):
        bootstrap_mean_interval([1], samples=10, seed=1, confidence_level=1.0)
