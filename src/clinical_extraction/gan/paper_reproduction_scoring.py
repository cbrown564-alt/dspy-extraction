from __future__ import annotations

import math
import re
from dataclasses import dataclass

from clinical_extraction.gan.frequency import normalize_label

PAPER_UNKNOWN_VALUE = 1000.0
PAPER_PARSE_FAILURE_VALUE = -1000.0

_DAY_IN_YEAR = 365.0
_DAYS_PER = {
    "day": 1.0,
    "week": 7.0,
    "month": 30.0,
    "year": 365.0,
}
_DECIMAL = r"(?:\d+(?:\.\d+)?)"
_RATE_RE = re.compile(
    rf"^(?P<n1>{_DECIMAL})(?:\s*to\s*(?P<n2>{_DECIMAL}))?\s+per\s+"
    rf"(?:(?P<d1>{_DECIMAL})(?:\s*to\s*(?P<d2>{_DECIMAL}))?\s+)?"
    r"(?P<unit>day|week|month|year)$"
)
_SIMPLE_RATE_RE = re.compile(
    rf"^(?P<count>{_DECIMAL})\s+per\s+(?P<unit>day|week|month|year)$"
)


@dataclass(frozen=True)
class PaperFrequencyConversion:
    normalized_label: str
    monthly_frequency: float
    min_monthly_frequency: float | None = None
    max_monthly_frequency: float | None = None
    parse_failed: bool = False
    repaired: bool = False


def paper_label_to_monthly_frequency(label: str) -> float:
    return convert_paper_label(label).monthly_frequency


def convert_paper_label(
    label: str,
    *,
    apply_prediction_repair: bool = False,
) -> PaperFrequencyConversion:
    normalized = normalize_label(str(label))
    if apply_prediction_repair:
        repaired = repair_paper_prediction_label(normalized)
        normalized = repaired
    try:
        min_year, max_year = _parse_paper_label_bounds(
            _apply_dynamic_multiple_policy(normalized)
        )
    except (AssertionError, ValueError, TypeError):
        return PaperFrequencyConversion(
            normalized_label=normalized,
            monthly_frequency=PAPER_PARSE_FAILURE_VALUE,
            parse_failed=True,
            repaired=apply_prediction_repair,
        )

    if min_year in {-1.0, -2.0} or max_year in {-1.0, -2.0}:
        return PaperFrequencyConversion(
            normalized_label=normalized,
            monthly_frequency=PAPER_UNKNOWN_VALUE,
            min_monthly_frequency=PAPER_UNKNOWN_VALUE,
            max_monthly_frequency=PAPER_UNKNOWN_VALUE,
            repaired=apply_prediction_repair,
        )

    min_monthly = min_year / 12.0
    max_monthly = max_year / 12.0
    return PaperFrequencyConversion(
        normalized_label=normalized,
        monthly_frequency=(min_monthly + max_monthly) / 2.0,
        min_monthly_frequency=min_monthly,
        max_monthly_frequency=max_monthly,
        repaired=apply_prediction_repair,
    )


def paper_purist_category(label_or_monthly: str | float) -> str:
    value = _monthly_value(label_or_monthly)
    if value == 0:
        return "currently_no_seizure"
    if value == PAPER_UNKNOWN_VALUE:
        return "seizure_freq_unknown"
    if 0 < value <= 0.16:
        return "seizure_freq_1_per_yr"
    if 0.16 < value <= 0.18:
        return "seizure_freq_1_per_6mon"
    if 0.18 < value <= 0.99:
        return "seizure_freq_more1per6mon_less1mon"
    if 0.99 < value <= 1.1:
        return "seizure_freq_1_per_mon"
    if 1.1 < value <= 3.9:
        return "seizure_freq_more1mon_less1week"
    if 3.9 < value <= 4.1:
        return "seizure_freq_1_per_week"
    if 4.1 < value <= 29:
        return "seizure_freq_more1week_less1day"
    if 29 < value <= 999:
        return "seizure_freq_1ormore_daily"
    return "seizure_freq_unknown"


def paper_pragmatic_category(label_or_monthly: str | float) -> str:
    value = _monthly_value(label_or_monthly)
    if value == 0:
        return "currently_no_seizure"
    if value == PAPER_UNKNOWN_VALUE:
        return "seizure_freq_unknown"
    if 0 < value <= 1.1:
        return "seizure_infrequent"
    if 1.1 < value <= 999:
        return "seizure_frequent"
    return "seizure_freq_unknown"


def repair_paper_prediction_label(label: str | None) -> str:
    if label is None or not str(label).strip():
        return "no seizure frequency reference"
    repaired = normalize_label(str(label))
    repaired = re.sub(r"\b(\d+(?:\.\d+)?)\s*x\s+a\s+", r"\1 per ", repaired)
    repaired = re.sub(r"\b(\d+(?:\.\d+)?)\s*x\s+per\s+", r"\1 per ", repaired)
    repaired = repaired.replace(" once ", " 1 ")
    repaired = repaired.replace(" twice ", " 2 ")
    repaired = re.sub(r"\bweekly\b", "per week", repaired)
    repaired = re.sub(r"\bmonthly\b", "per month", repaired)
    repaired = re.sub(r"\bdaily\b", "per day", repaired)
    repaired = re.sub(r"\byearly\b", "per year", repaired)
    repaired = re.sub(r"\s+", " ", repaired).strip()
    return repaired


def _apply_dynamic_multiple_policy(label: str) -> str:
    adjusted = label
    adjusted = adjusted.replace(" per multiple week", " per 2 week")
    adjusted = adjusted.replace(" per multiple month", " per 2 month")
    adjusted = adjusted.replace(" per multiple year", " per 2 year")
    adjusted = adjusted.replace(" per multiple day", " per 2 day")

    if adjusted.endswith("week") or "week," in adjusted:
        adjusted = adjusted.replace("multiple per ", "2 per ")
        adjusted = adjusted.replace("multiple cluster per ", "2 cluster per ")
    elif adjusted.endswith("month") or "month," in adjusted:
        adjusted = adjusted.replace("multiple per ", "8 per ")
        adjusted = adjusted.replace("multiple cluster per ", "8 cluster per ")
    elif adjusted.endswith("year") or "year," in adjusted:
        adjusted = adjusted.replace("multiple per ", "18 per ")
        adjusted = adjusted.replace("multiple cluster per ", "18 cluster per ")
    elif adjusted.endswith("day") or "day," in adjusted:
        adjusted = adjusted.replace("multiple per ", "2 per ")
        adjusted = adjusted.replace("multiple cluster per ", "2 cluster per ")

    if "cluster" in adjusted:
        adjusted = adjusted.replace("multiple per cluster", "2 per cluster")
        if "unknown" in adjusted:
            return "unknown"
        adjusted = _collapse_cluster_to_rate(adjusted)
    return adjusted


def _collapse_cluster_to_rate(label: str) -> str:
    cluster = re.search(rf"({_DECIMAL}(?:\s*to\s*{_DECIMAL})?)\s+cluster\b", label)
    if cluster is None:
        raise AssertionError(f"Unparsable cluster label: {label!r}")
    period = re.search(
        rf"cluster\s+per\s+((?:{_DECIMAL}(?:\s*to\s*{_DECIMAL})?\s+)?(?:day|week|month|year))",
        label,
    )
    if period is None:
        raise AssertionError(f"Unparsable cluster period: {label!r}")
    per_cluster = re.search(
        rf"({_DECIMAL}(?:\s*to\s*{_DECIMAL})?)\s+per\s+cluster\b", label
    )
    if per_cluster is None:
        raise AssertionError(f"Unparsable per-cluster label: {label!r}")

    cluster_min, cluster_max = _parse_quantity_bounds(cluster.group(1))
    per_cluster_min, per_cluster_max = _parse_quantity_bounds(per_cluster.group(1))
    min_count = cluster_min * per_cluster_min
    max_count = cluster_max * per_cluster_max
    count = _format_number(min_count)
    if not math.isclose(min_count, max_count):
        count = f"{count} to {_format_number(max_count)}"
    return f"{count} per {period.group(1)}"


def _parse_paper_label_bounds(label: str) -> tuple[float, float]:
    if not isinstance(label, str):
        raise AssertionError(f"label is not a string: {label!r}")

    normalized = _clean_label(label)
    if "seizure free" in normalized:
        return 0.0, 0.0
    if "unknown" in normalized or normalized.startswith("multiple per"):
        return -1.0, -1.0
    if "no seizure frequency reference" in normalized:
        return -2.0, -2.0
    if re.search(r"\s+per\s+multiple\s+(?:day|week|month|year)", normalized):
        return -1.0, -1.0

    match = _RATE_RE.match(normalized)
    if match:
        n_min, n_max = _numeric_bounds(match.group("n1"), match.group("n2"))
        d_min, d_max = _numeric_bounds(
            match.group("d1"), match.group("d2"), default=1.0
        )
        days = _DAYS_PER[match.group("unit")]
        return (
            n_min * _DAY_IN_YEAR / (d_max * days),
            n_max * _DAY_IN_YEAR / (d_min * days),
        )

    simple_match = _SIMPLE_RATE_RE.match(normalized)
    if simple_match:
        value = float(simple_match.group("count")) * _DAY_IN_YEAR / _DAYS_PER[
            simple_match.group("unit")
        ]
        return value, value

    raise AssertionError(f"Unparsable label: {label!r}")


def _clean_label(label: str) -> str:
    cleaned = normalize_label(label)
    cleaned = re.sub(r",\s*[^,]*?\bper\s+cluster\b.*$", "", cleaned)
    cleaned = re.sub(r"(\d+)\s*[-–—]\s*(\d+)", r"\1 to \2", cleaned)
    cleaned = re.sub(r"\bclusters?\b", "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _parse_quantity_bounds(value: str) -> tuple[float, float]:
    parts = [float(part.strip()) for part in value.split(" to ")]
    if len(parts) == 1:
        return parts[0], parts[0]
    return min(parts), max(parts)


def _numeric_bounds(
    first: str | None,
    second: str | None,
    *,
    default: float | None = None,
) -> tuple[float, float]:
    if first is None:
        if default is None:
            raise AssertionError("missing numeric value")
        return default, default
    if second is None:
        value = float(first)
        return value, value
    low = min(float(first), float(second))
    high = max(float(first), float(second))
    return low, high


def _format_number(value: float) -> str:
    if math.isclose(value, round(value)):
        return str(int(round(value)))
    return str(value)


def _monthly_value(label_or_monthly: str | float) -> float:
    if isinstance(label_or_monthly, (int, float)):
        return float(label_or_monthly)
    return paper_label_to_monthly_frequency(label_or_monthly)
