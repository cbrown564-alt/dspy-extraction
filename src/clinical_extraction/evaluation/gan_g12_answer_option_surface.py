"""Gan G12 aggregation-aware answer-option surface report.

This is a no-model routing report for G10. It separates the raw inventory labels
available on the locked G6 exact-miss challenge set from the subset of current
candidate labels that already look like temporal anchoring or aggregation
products. It does not change candidate generation, scoring, loading, splits,
benchmark bridges, prompts, models, or prediction repair.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.evaluation.gan_g11_candidate_inventory_challenge import (
    DEFAULT_G11_JSON_OUTPUT,
    G11_CHALLENGE_SET_NAME,
    G9_STANDARD50_EXACT_MISS_IDS,
)
from clinical_extraction.gan.frequency import (
    label_to_monthly_frequency,
    normalize_label,
    pragmatic_category,
    purist_category,
)

DEFAULT_G12_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g12_answer_option_surface_20260529.json"
)
DEFAULT_G12_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g12_answer_option_surface_20260529.md"
)

AGGREGATE_DERIVATION_KEYWORDS = (
    "aggregat",
    "calendar",
    "dated",
    "diary",
    "documented",
    "elapsed",
    "from first month",
    "last",
    "named-month",
    "observation window",
    "over",
    "past",
    "since",
    "summed",
    "window",
    "year-to-date",
)


def build_g12_answer_option_surface_report(
    *,
    g11_json: Path = DEFAULT_G11_JSON_OUTPUT,
) -> dict[str, Any]:
    """Build the G12 no-model answer-option report from the G11 artifact."""

    g11 = json.loads(g11_json.read_text(encoding="utf-8"))
    rows = [_answer_option_row(row) for row in g11["rows"]]
    raw_summary = _summary(rows, "raw_option_view")
    constructed_summary = _summary(rows, "constructed_aggregate_option_view")
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "G12 no-model answer-option surface decision",
        "kanban_card": "G12 - Gan Aggregation-Aware Answer-Option Surface",
        "dataset": g11["dataset"],
        "split": g11["split"],
        "challenge_set": G11_CHALLENGE_SET_NAME,
        "source_artifacts": {
            "g11_candidate_inventory_challenge": g11_json.as_posix(),
            "g1_candidate_inventory": g11["fixed_controls"][
                "g1_comparison_artifact"
            ],
            "g6_evaluation_surface": g11["challenge_set_source"],
            "g9_routing_report": g11["g9_routing_report"],
        },
        "fixed_controls": {
            "model_calls": "none",
            "scorer_changed": False,
            "loader_split_bridge_or_repair_changed": False,
            "candidate_builder_changed": False,
            "prompt_or_model_changed": False,
            "prediction_repair_changed": False,
            "constructed_view_rule": (
                "uses only existing candidate_records whose derivation indicates "
                "temporal anchoring, event summation, diary/month tallying, or "
                "explicit-window aggregation"
            ),
            "aggregate_derivation_keywords": list(AGGREGATE_DERIVATION_KEYWORDS),
        },
        "summary": {
            "raw_option_view": raw_summary,
            "constructed_aggregate_option_view": constructed_summary,
            "standard50_g9_exact_miss_subset": {
                "raw_option_view": _summary(
                    [
                        row
                        for row in rows
                        if row["record_id"] in G9_STANDARD50_EXACT_MISS_IDS
                    ],
                    "raw_option_view",
                ),
                "constructed_aggregate_option_view": _summary(
                    [
                        row
                        for row in rows
                        if row["record_id"] in G9_STANDARD50_EXACT_MISS_IDS
                    ],
                    "constructed_aggregate_option_view",
                ),
            },
            "g1_g11_diff_summary": g11["g1_diff_summary"],
        },
        "decision": _decision(
            raw_summary=raw_summary,
            constructed_summary=constructed_summary,
        ),
        "rows": rows,
    }


def write_g12_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_G12_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_G12_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_g12_markdown(report), encoding="utf-8")


def render_g12_markdown(report: dict[str, Any]) -> str:
    raw = report["summary"]["raw_option_view"]["overall"]
    constructed = report["summary"]["constructed_aggregate_option_view"]["overall"]
    subset_raw = report["summary"]["standard50_g9_exact_miss_subset"][
        "raw_option_view"
    ]["overall"]
    subset_constructed = report["summary"]["standard50_g9_exact_miss_subset"][
        "constructed_aggregate_option_view"
    ]["overall"]
    decision = report["decision"]
    lines = [
        "# Gan S0 G12 Aggregation-Aware Answer-Option Surface",
        "",
        "Date: 2026-05-29",
        "Status: current synthesis / no-model answer-option decision",
        f"Kanban card: {report['kanban_card']}",
        f"Dataset/split: {report['dataset']} (`{report['split']}`)",
        f"Challenge set: `{report['challenge_set']}`",
        "Model calls: none",
        "Scorer, loader, split, bridge, prompt, model, and prediction-repair semantics: unchanged.",
        "",
        "## Summary",
        "",
        _coverage_sentence("Raw option view", raw),
        _coverage_sentence("Constructed aggregate option view", constructed),
        _coverage_sentence("G9 standard50 subset, raw view", subset_raw),
        _coverage_sentence(
            "G9 standard50 subset, constructed aggregate view",
            subset_constructed,
        ),
        (
            "Candidate diff versus stored G1/G11: "
            f"**{report['summary']['g1_g11_diff_summary']['rows_with_any_diff']}** "
            "of 21 rows differ from stored G1, all due to candidate-label changes "
            "from current abstention pruning."
        ),
        "",
        "## Option Surface Decision",
        "",
        f"- Decision: **{decision['g10_authorized_surface']}**.",
        f"- Exact-label claim: **{decision['exact_label_claim']}**.",
        f"- Category-level claim: **{decision['category_level_claim']}**.",
        f"- Required follow-up before an exact closed-option G10: {decision['required_follow_up_for_exact_closed_options']}",
        "",
        "## Coverage By Family",
        "",
        "### Raw Option View",
        "",
        _summary_table(report["summary"]["raw_option_view"]["by_label_family"]),
        "",
        "### Constructed Aggregate Option View",
        "",
        _summary_table(
            report["summary"]["constructed_aggregate_option_view"][
                "by_label_family"
            ]
        ),
        "",
        "## Row-Level Surface",
        "",
        "| Record | Gold | Raw exact/Purist/Pragmatic | Constructed exact/Purist/Pragmatic | Constructed aggregate options |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report["rows"]:
        lines.append(_row_line(row))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The current raw inventory remains category-useful but exact-label incomplete on the locked exact-miss surface.",
            "- The current constructed aggregate subset does not recover exact labels; it is a traceability subset of existing candidates, not a new aggregation algorithm.",
            "- G10 may proceed only as a category-level or candidate-ranking mechanism comparison unless it adds a separately preregistered aggregation constructor after temporal anchoring and rate/duration aggregation policy work.",
            "- Exact normalized-label and monthly-frequency results from such a narrowed G10 must be reported as unsupported diagnostics, not as evidence that exact label construction is solved.",
            "",
            "## Companion Artifact",
            "",
            "`docs/experiments/gan/gan_s0_g12_answer_option_surface_20260529.json` contains row-level raw and constructed option views, G1/G11 diffs, summaries, and fixed-control metadata.",
            "",
        ]
    )
    return "\n".join(lines)


def _answer_option_row(row: dict[str, Any]) -> dict[str, Any]:
    raw_options = _valid_option_records(row["candidate_records"], constructed_only=False)
    constructed_options = _valid_option_records(
        row["candidate_records"],
        constructed_only=True,
    )
    return {
        "record_id": row["record_id"],
        "gold_label": row["gold_label"],
        "label_family": row["label_family"],
        "hard_strata": row["hard_strata"],
        "reference_label": row["reference_label"],
        "raw_option_view": _option_view(row, raw_options),
        "constructed_aggregate_option_view": _option_view(row, constructed_options),
    }


def _valid_option_records(
    candidate_records: list[dict[str, Any]],
    *,
    constructed_only: bool,
) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in candidate_records:
        if constructed_only and not _is_constructed_aggregate(candidate):
            continue
        label = normalize_label(str(candidate.get("canonical_label") or ""))
        try:
            label_to_monthly_frequency(label)
        except ValueError:
            continue
        if label in seen:
            continue
        seen.add(label)
        options.append(
            {
                "label": label,
                "derivation": candidate.get("derivation"),
                "evidence_text": candidate.get("evidence_text"),
                "event_count": candidate.get("event_count"),
                "window_count": candidate.get("window_count"),
                "window_unit": candidate.get("window_unit"),
            }
        )
    return options


def _is_constructed_aggregate(candidate: dict[str, Any]) -> bool:
    derivation = str(candidate.get("derivation") or "").lower()
    return any(keyword in derivation for keyword in AGGREGATE_DERIVATION_KEYWORDS)


def _option_view(row: dict[str, Any], options: list[dict[str, Any]]) -> dict[str, Any]:
    labels = [option["label"] for option in options]
    purist_categories = _category_set(labels, purist_category)
    pragmatic_categories = _category_set(labels, pragmatic_category)
    return {
        "option_count": len(labels),
        "labels": labels,
        "option_records": options,
        "gold_exact_covered": row["gold_label"] in labels,
        "gold_purist_equivalent_covered": (
            row["gold_purist_category"] in purist_categories
        ),
        "gold_pragmatic_equivalent_covered": (
            row["gold_pragmatic_category"] in pragmatic_categories
        ),
    }


def _category_set(labels: list[str], category_fn: Any) -> set[str]:
    categories: set[str] = set()
    for label in labels:
        try:
            categories.add(category_fn(label))
        except ValueError:
            continue
    return categories


def _summary(rows: list[dict[str, Any]], view_key: str) -> dict[str, Any]:
    return {
        "overall": _coverage(rows, view_key),
        "by_label_family": _bucket(rows, view_key, "label_family"),
        "by_hard_stratum": _hard_strata(rows, view_key),
        "option_count_distribution": _option_count_distribution(rows, view_key),
        "category_gap_rows": [
            row["record_id"]
            for row in rows
            if not row[view_key]["gold_purist_equivalent_covered"]
            or not row[view_key]["gold_pragmatic_equivalent_covered"]
        ],
    }


def _coverage(rows: list[dict[str, Any]], view_key: str) -> dict[str, Any]:
    total = len(rows)
    exact = sum(1 for row in rows if row[view_key]["gold_exact_covered"])
    purist = sum(
        1 for row in rows if row[view_key]["gold_purist_equivalent_covered"]
    )
    pragmatic = sum(
        1 for row in rows if row[view_key]["gold_pragmatic_equivalent_covered"]
    )
    with_options = sum(1 for row in rows if row[view_key]["option_count"] > 0)
    return {
        "records": total,
        "records_with_options": with_options,
        "records_with_options_rate": _rate(with_options, total),
        "gold_exact_covered": exact,
        "gold_exact_coverage_rate": _rate(exact, total),
        "gold_purist_equivalent_covered": purist,
        "gold_purist_equivalent_coverage_rate": _rate(purist, total),
        "gold_pragmatic_equivalent_covered": pragmatic,
        "gold_pragmatic_equivalent_coverage_rate": _rate(pragmatic, total),
    }


def _bucket(
    rows: list[dict[str, Any]],
    view_key: str,
    bucket_key: str,
) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row[bucket_key])].append(row)
    return {
        name: _coverage(bucket_rows, view_key)
        for name, bucket_rows in sorted(buckets.items())
    }


def _hard_strata(rows: list[dict[str, Any]], view_key: str) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for stratum in row["hard_strata"]:
            buckets[stratum].append(row)
    return {
        name: _coverage(bucket_rows, view_key)
        for name, bucket_rows in sorted(buckets.items())
    }


def _option_count_distribution(rows: list[dict[str, Any]], view_key: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        count = row[view_key]["option_count"]
        if count == 0:
            bucket = "0"
        elif count == 1:
            bucket = "1"
        elif count <= 3:
            bucket = "2-3"
        else:
            bucket = "4+"
        counts[bucket] += 1
    return {bucket: counts[bucket] for bucket in ("0", "1", "2-3", "4+")}


def _decision(
    *,
    raw_summary: dict[str, Any],
    constructed_summary: dict[str, Any],
) -> dict[str, str]:
    raw = raw_summary["overall"]
    constructed = constructed_summary["overall"]
    if constructed["gold_exact_covered"] == constructed["records"]:
        authorized = "exact_closed_answer_options_from_constructed_aggregate_view"
        exact_claim = "authorized"
        category_claim = "authorized"
        follow_up = "none before G10"
    else:
        authorized = "category_level_selector_only_before_new_aggregation_constructor"
        exact_claim = (
            "not authorized: current constructed aggregate view exact-covers "
            f"{constructed['gold_exact_covered']}/{constructed['records']} rows"
        )
        category_claim = (
            "authorized as a narrowed G10 mechanism claim: raw options cover "
            f"{raw['gold_purist_equivalent_covered']}/{raw['records']} Purist and "
            f"{raw['gold_pragmatic_equivalent_covered']}/{raw['records']} Pragmatic "
            "equivalent rows"
        )
        follow_up = (
            "G14 temporal anchoring plus G16 rate/duration aggregation policy, "
            "or a separate deterministic aggregation constructor with fixture tests"
        )
    return {
        "g10_authorized_surface": authorized,
        "exact_label_claim": exact_claim,
        "category_level_claim": category_claim,
        "required_follow_up_for_exact_closed_options": follow_up,
    }


def _coverage_sentence(label: str, overall: dict[str, Any]) -> str:
    return (
        f"{label}: **{overall['gold_exact_covered']}/{overall['records']}** exact, "
        f"**{overall['gold_purist_equivalent_covered']}/{overall['records']}** "
        f"Purist-equivalent, and **{overall['gold_pragmatic_equivalent_covered']}/"
        f"{overall['records']}** Pragmatic-equivalent."
    )


def _summary_table(summary: dict[str, dict[str, Any]]) -> str:
    lines = [
        "| Family | Records | Options | Exact | Purist equiv. | Pragmatic equiv. |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, stats in summary.items():
        lines.append(
            f"| `{name}` | {stats['records']} | "
            f"{stats['records_with_options']} ({_pct(stats['records_with_options_rate'])}) | "
            f"{stats['gold_exact_covered']} ({_pct(stats['gold_exact_coverage_rate'])}) | "
            f"{stats['gold_purist_equivalent_covered']} "
            f"({_pct(stats['gold_purist_equivalent_coverage_rate'])}) | "
            f"{stats['gold_pragmatic_equivalent_covered']} "
            f"({_pct(stats['gold_pragmatic_equivalent_coverage_rate'])}) |"
        )
    return "\n".join(lines)


def _row_line(row: dict[str, Any]) -> str:
    raw = row["raw_option_view"]
    constructed = row["constructed_aggregate_option_view"]
    constructed_labels = (
        "<br>".join(f"`{label}`" for label in constructed["labels"]) or "`none`"
    )
    return (
        f"| `{row['record_id']}` | `{row['gold_label']}` | "
        f"{_yn(raw['gold_exact_covered'])}/"
        f"{_yn(raw['gold_purist_equivalent_covered'])}/"
        f"{_yn(raw['gold_pragmatic_equivalent_covered'])} | "
        f"{_yn(constructed['gold_exact_covered'])}/"
        f"{_yn(constructed['gold_purist_equivalent_covered'])}/"
        f"{_yn(constructed['gold_pragmatic_equivalent_covered'])} | "
        f"{constructed_labels} |"
    )


def _yn(value: bool) -> str:
    return "yes" if value else "no"


def _rate(count: int, total: int) -> float | None:
    return count / total if total else None


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1%}"


__all__ = [
    "DEFAULT_G12_JSON_OUTPUT",
    "DEFAULT_G12_MARKDOWN_OUTPUT",
    "AGGREGATE_DERIVATION_KEYWORDS",
    "build_g12_answer_option_surface_report",
    "render_g12_markdown",
    "write_g12_report_artifacts",
]
