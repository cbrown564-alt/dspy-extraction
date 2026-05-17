from __future__ import annotations

from random import Random
from typing import Any, Iterable


def bootstrap_mean_interval(
    observations: Iterable[bool | int | float],
    *,
    samples: int = 1000,
    seed: int = 0,
    confidence_level: float = 0.95,
) -> dict[str, Any]:
    """Estimate a percentile bootstrap confidence interval for a mean metric."""

    values = [float(value) for value in observations]
    if not values:
        raise ValueError("bootstrap requires at least one observation")
    if samples < 1:
        raise ValueError("samples must be at least 1")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be between 0 and 1")

    point_estimate = sum(values) / len(values)
    rng = Random(seed)
    bootstrap_means = sorted(
        sum(rng.choice(values) for _ in values) / len(values)
        for _ in range(samples)
    )
    alpha = (1 - confidence_level) / 2
    lower = _quantile(bootstrap_means, alpha)
    upper = _quantile(bootstrap_means, 1 - alpha)

    return {
        "point_estimate": point_estimate,
        "lower": lower,
        "upper": upper,
        "confidence_level": confidence_level,
        "method": "percentile_bootstrap_mean",
        "bootstrap_samples": samples,
        "seed": seed,
        "n": len(values),
    }


def build_bootstrap_confidence_intervals(
    metric_observations: dict[str, Iterable[bool | int | float]],
    *,
    samples: int = 1000,
    seed: int = 0,
    confidence_level: float = 0.95,
) -> dict[str, dict[str, Any]]:
    intervals: dict[str, dict[str, Any]] = {}
    for metric_name, observations in metric_observations.items():
        values = list(observations)
        if not values:
            continue
        intervals[metric_name] = bootstrap_mean_interval(
            values,
            samples=samples,
            seed=seed,
            confidence_level=confidence_level,
        )
    return intervals


def _quantile(sorted_values: list[float], probability: float) -> float:
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = probability * (len(sorted_values) - 1)
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    fraction = position - lower_index
    return sorted_values[lower_index] + (
        sorted_values[upper_index] - sorted_values[lower_index]
    ) * fraction
