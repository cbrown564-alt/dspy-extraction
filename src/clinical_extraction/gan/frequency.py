from __future__ import annotations

import math
import re

UNIT_FACTORS_PER_MONTH = {
    "day": 30.0,
    "week": 4.33,
    "month": 1.0,
    "year": 1.0 / 12.0,
}

UNKNOWN_VALUE = 1000.0
NO_REFERENCE_VALUE = 0.0
UNKNOWN_CLUSTER_LABEL_RE = re.compile(r"^unknown, .+? per cluster$")
LEADING_INEQUALITY_RE = re.compile(r"^(?:<=|>=|<|>|≤|≥|at most|at least|up to)\s*")
RATE_LABEL_RE = re.compile(
    r"(?P<count>.+?) per (?:(?P<period>.+?) )?(?P<unit>day|week|month|year)$"
)
CLUSTER_LABEL_RE = re.compile(
    r"(?P<clusters>.+?) cluster per (?:(?P<period>.+?) )?(?P<unit>day|week|month|year), "
    r"(?P<per_cluster>.+?) per cluster$"
)


def normalize_label(label: str) -> str:
    normalized = re.sub(r"\s+", " ", label.strip().lower())
    normalized = normalized.replace("≤", "<=").replace("≥", ">=")
    normalized = normalized.replace("months", "month").replace("years", "year")
    normalized = normalized.replace("weeks", "week").replace("days", "day")
    return normalized


def gan_label_policy_failure_class(label: str | None) -> str | None:
    """Classify non-canonical Gan final-label surfaces without repairing them."""

    if label is None or not str(label).strip():
        return "abstention_or_missing_value"

    normalized = normalize_label(str(label))
    if _is_supported_label(normalized):
        return None
    if LEADING_INEQUALITY_RE.match(normalized):
        return "inequality_operator"
    if normalized.startswith("unknown,") and not UNKNOWN_CLUSTER_LABEL_RE.fullmatch(
        normalized
    ):
        if "cluster per" in normalized and "unknown," in normalized:
            return "malformed_cluster_unknown_slot"
        return "unknown_quantified_hybrid"
    if "cluster per" in normalized and "unknown," in normalized:
        return "malformed_cluster_unknown_slot"
    if "," in normalized and not CLUSTER_LABEL_RE.fullmatch(normalized):
        head, tail = [part.strip() for part in normalized.split(",", maxsplit=1)]
        if _is_supported_label(head) and " per " in tail:
            return "multiple_frequency_labels"
        if _is_supported_label(head):
            return "prose_appended_label"
        if " per " in tail:
            return "multiple_frequency_labels"
    return "invalid_label"


def canonicalize_leading_inequality_label(label: str) -> str | None:
    """Return a canonical label after stripping a leading inequality operator.

    This is intentionally narrow: only a leading operator is removed, and the
    stripped value must already satisfy the audited Gan label taxonomy.
    """

    normalized = normalize_label(label)
    if LEADING_INEQUALITY_RE.match(normalized) is None:
        return None
    candidate = LEADING_INEQUALITY_RE.sub("", normalized).strip()
    return candidate if _is_supported_label(candidate) else None


def _is_supported_label(label: str) -> bool:
    try:
        label_to_monthly_frequency(label)
    except (TypeError, ValueError):
        return False
    return True


def label_to_monthly_frequency(label: str) -> float:
    normalized = normalize_label(label)

    if normalized == "no seizure frequency reference":
        return NO_REFERENCE_VALUE
    if normalized == "unknown" or UNKNOWN_CLUSTER_LABEL_RE.fullmatch(normalized):
        return UNKNOWN_VALUE
    if normalized.startswith("unknown,"):
        raise ValueError(f"Unsupported Gan frequency label: {label!r}")
    if normalized.startswith("seizure free for "):
        return NO_REFERENCE_VALUE

    cluster_match = CLUSTER_LABEL_RE.fullmatch(normalized)
    if cluster_match:
        clusters_per_month = _rate_to_monthly(
            cluster_match.group("clusters"),
            cluster_match.group("period") or "1",
            cluster_match.group("unit"),
        )
        per_cluster = _parse_quantity(cluster_match.group("per_cluster"))
        return clusters_per_month * per_cluster

    rate_match = RATE_LABEL_RE.fullmatch(normalized)
    if rate_match:
        return _rate_to_monthly(
            rate_match.group("count"),
            rate_match.group("period") or "1",
            rate_match.group("unit"),
        )

    raise ValueError(f"Unsupported Gan frequency label: {label!r}")


def purist_category(label: str) -> str:
    normalized = normalize_label(label)
    if normalized == "unknown" or UNKNOWN_CLUSTER_LABEL_RE.fullmatch(normalized):
        return "unknown"
    if normalized == "no seizure frequency reference":
        return "no_seizure_information"

    value = label_to_monthly_frequency(normalized)
    if math.isclose(value, 0.0):
        return "no_seizure_information"
    if 0 < value <= 0.16:
        return "lt_1_per_6_months"
    if 0.16 < value <= 0.18:
        return "eq_1_per_6_months"
    if 0.18 < value <= 0.99:
        return "gt_1_per_6_months_lt_1_per_month"
    if 0.99 < value <= 1.1:
        return "eq_1_per_month"
    if 1.1 < value <= 3.9:
        return "gt_1_per_month_lt_1_per_week"
    if 3.9 < value <= 4.1:
        return "eq_1_per_week"
    if 4.1 < value <= 29:
        return "gt_1_per_week_lt_1_per_day"
    if 29 < value <= 999:
        return "gte_1_per_day"
    if math.isclose(value, UNKNOWN_VALUE):
        return "unknown"
    raise ValueError(f"Value outside Purist categories for {label!r}: {value}")


def pragmatic_category(label: str) -> str:
    normalized = normalize_label(label)
    if normalized == "unknown" or UNKNOWN_CLUSTER_LABEL_RE.fullmatch(normalized):
        return "unknown"
    if normalized == "no seizure frequency reference":
        return "no_seizure_information"

    value = label_to_monthly_frequency(normalized)
    if math.isclose(value, 0.0):
        return "no_seizure_information"
    if 0 < value <= 1.1:
        return "infrequent"
    if 1.1 < value <= 999:
        return "frequent"
    raise ValueError(f"Value outside Pragmatic categories for {label!r}: {value}")


def _rate_to_monthly(count: str, period: str, unit: str) -> float:
    numerator = _parse_quantity(count)
    denominator = _parse_quantity(period)
    return (numerator / denominator) * UNIT_FACTORS_PER_MONTH[unit]


def _parse_quantity(value: str) -> float:
    value = value.strip()
    if value == "multiple":
        return 3.0
    range_match = re.fullmatch(r"(\d+(?:\.\d+)?) to (\d+(?:\.\d+)?)", value)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        return (low + high) / 2.0
    return float(value)
