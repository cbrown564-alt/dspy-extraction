"""Gan S0 candidate-inventory coverage reporting.

The inventory is diagnostic only. It measures whether the current deterministic
candidate substrate represents the audited gold label or an equivalent
Purist/Pragmatic category before any adjudicator, repair, or scorer change.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_multi_event_flags import (
    GanMultiEventFlags,
    build_flags_for_raw_records,
)
from clinical_extraction.evaluation.gan_run_analysis import load_split_ids
from clinical_extraction.gan.s0.candidate_inventory import (
    build_gan_s0_candidate_inventory_surface,
    gan_s0_hard_strata_for_record,
    gan_s0_label_family,
)
from clinical_extraction.schemas import GanRecord

DEFAULT_SPLIT_FILE = Path("data/splits/gan_2026_splits.json")
DEFAULT_SPLIT_NAME = "gan_2026_fixed_v1:validation"
DEFAULT_GAN_JSON = Path("data/Gan (2026)/synthetic_data_subset_1500.json")
DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.md"
)


def build_gan_candidate_inventory_report(
    *,
    records: list[GanRecord] | None = None,
    record_ids: list[str] | None = None,
    flags_by_id: dict[str, GanMultiEventFlags] | None = None,
    split_name: str = DEFAULT_SPLIT_NAME,
    candidate_source: str = "deterministic_temporal_candidates_current_d1_builder",
) -> dict[str, Any]:
    """Build a first-class Gan candidate-inventory coverage report."""

    source_records = records if records is not None else load_gan_records()
    records_by_id = {record.record_id: record for record in source_records}
    ordered_ids = record_ids if record_ids is not None else list(records_by_id)
    rows = [
        _inventory_row(
            record=records_by_id[record_id],
            flags=flags_by_id.get(record_id) if flags_by_id else None,
        )
        for record_id in ordered_ids
    ]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": "gan_2026",
        "split_name": split_name,
        "candidate_source": candidate_source,
        "gold_source": "check__Seizure Frequency Number.seizure_frequency_number[0]",
        "reference_policy": (
            "reference[0] is a secondary difficulty signal, not benchmark gold"
        ),
        "scorer_semantics": (
            "Diagnostic candidate coverage only; scorer semantics are unchanged. "
            "Purist/Pragmatic equivalence uses gan_frequency_deterministic_v1 "
            "category functions for coverage stratification."
        ),
        "summary": _summarize_rows(rows),
        "rows": rows,
    }


def build_report_from_files(
    *,
    gan_json: Path = DEFAULT_GAN_JSON,
    split_file: Path = DEFAULT_SPLIT_FILE,
    split_name: str = DEFAULT_SPLIT_NAME,
) -> dict[str, Any]:
    """Load Gan data, split IDs, and hard-stratum flags, then build the report."""

    raw_records = json.loads(gan_json.read_text(encoding="utf-8"))
    flags = build_flags_for_raw_records(raw_records)
    flags_by_id = {flag.record_id: flag for flag in flags}
    records = load_gan_records(gan_json)
    record_ids = load_split_ids(split_file, split_name)
    return build_gan_candidate_inventory_report(
        records=records,
        record_ids=record_ids,
        flags_by_id=flags_by_id,
        split_name=split_name,
    )


def write_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_candidate_inventory_markdown(report), encoding="utf-8")


def _inventory_row(
    *,
    record: GanRecord,
    flags: GanMultiEventFlags | None,
) -> dict[str, Any]:
    return build_gan_s0_candidate_inventory_surface(record=record, flags=flags)


def label_family(label: str) -> str:
    return gan_s0_label_family(label)


def hard_strata_for_record(
    record: GanRecord, flags: GanMultiEventFlags | None
) -> list[str]:
    return gan_s0_hard_strata_for_record(record, flags)


def _summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "overall": _coverage_summary(rows),
        "by_label_family": _bucketed_summary(rows, "label_family"),
        "by_hard_stratum": _hard_stratum_summary(rows),
        "by_gold_pragmatic_category": _bucketed_summary(
            rows, "gold_pragmatic_category"
        ),
        "by_gold_purist_category": _bucketed_summary(rows, "gold_purist_category"),
        "candidate_count_distribution": _candidate_count_distribution(rows),
        "invalid_candidate_labels": _invalid_candidate_summary(rows),
    }


def _bucketed_summary(
    rows: list[dict[str, Any]], key: str
) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row[key])].append(row)
    return {
        bucket: _coverage_summary(bucket_rows)
        for bucket, bucket_rows in sorted(buckets.items())
    }


def _hard_stratum_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for stratum in row["hard_strata"]:
            buckets[stratum].append(row)
    return {
        bucket: _coverage_summary(bucket_rows)
        for bucket, bucket_rows in sorted(buckets.items())
    }


def _coverage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    exact = sum(1 for row in rows if row["gold_exact_in_candidates"])
    purist = sum(1 for row in rows if row["gold_purist_in_candidates"])
    pragmatic = sum(1 for row in rows if row["gold_pragmatic_in_candidates"])
    with_candidates = sum(1 for row in rows if row["candidate_count"] > 0)
    return {
        "records": total,
        "records_with_candidates": with_candidates,
        "records_with_candidates_rate": _rate(with_candidates, total),
        "gold_exact_covered": exact,
        "gold_exact_coverage_rate": _rate(exact, total),
        "gold_purist_equivalent_covered": purist,
        "gold_purist_equivalent_coverage_rate": _rate(purist, total),
        "gold_pragmatic_equivalent_covered": pragmatic,
        "gold_pragmatic_equivalent_coverage_rate": _rate(pragmatic, total),
    }


def _candidate_count_distribution(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = defaultdict(int)
    for row in rows:
        count = row["candidate_count"]
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


def _invalid_candidate_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    invalid_rows = [row for row in rows if row["invalid_candidate_count"]]
    labels: dict[str, int] = defaultdict(int)
    for row in invalid_rows:
        for label in row["invalid_candidate_labels"]:
            labels[label] += 1
    return {
        "records": len(invalid_rows),
        "candidate_labels": dict(sorted(labels.items())),
    }


def _rate(count: int, total: int) -> float | None:
    return count / total if total else None


def render_candidate_inventory_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    overall = summary["overall"]
    rows = report["rows"]
    uncovered = [row for row in rows if not row["gold_exact_in_candidates"]]
    hard_uncovered = [
        row for row in uncovered if row["hard_strata"] and row["candidate_count"] > 0
    ]
    lines = [
        "# Gan S0 Candidate Inventory Coverage Report",
        "",
        "Date: 2026-05-28",
        "Status: G1 no-model coverage report",
        "Dataset/split: Gan 2026 synthetic validation split "
        f"(`{report['split_name']}`)",
        f"Candidate source: `{report['candidate_source']}`",
        f"Gold source: `{report['gold_source']}`",
        "Scorer semantics: unchanged; category-equivalent coverage is diagnostic.",
        "",
        "## Summary",
        "",
        (
            f"Exact gold-label coverage is "
            f"**{overall['gold_exact_covered']}/{overall['records']}** "
            f"({_pct(overall['gold_exact_coverage_rate'])})."
        ),
        (
            f"Gold-equivalent Purist coverage is "
            f"**{overall['gold_purist_equivalent_covered']}/{overall['records']}** "
            f"({_pct(overall['gold_purist_equivalent_coverage_rate'])}); "
            f"Pragmatic coverage is "
            f"**{overall['gold_pragmatic_equivalent_covered']}/{overall['records']}** "
            f"({_pct(overall['gold_pragmatic_equivalent_coverage_rate'])})."
        ),
        (
            f"The current deterministic substrate emits at least one candidate for "
            f"**{overall['records_with_candidates']}/{overall['records']}** records "
            f"({_pct(overall['records_with_candidates_rate'])})."
        ),
        "",
        "## Coverage By Label Family",
        "",
        _summary_table(summary["by_label_family"], "Label family"),
        "",
        "## Coverage By Hard Stratum",
        "",
        _summary_table(summary["by_hard_stratum"], "Hard stratum"),
        "",
        "## Candidate Count Distribution",
        "",
        "| Candidate count | Records |",
        "| --- | ---: |",
    ]
    for bucket, count in summary["candidate_count_distribution"].items():
        lines.append(f"| `{bucket}` | {count} |")

    invalid_summary = summary["invalid_candidate_labels"]
    lines.extend(
        [
            "",
            "## Candidate Schema Diagnostics",
            "",
            (
                f"Records with non-canonical candidate labels: "
                f"**{invalid_summary['records']}**."
            ),
            "",
            "| Candidate label | Count |",
            "| --- | ---: |",
        ]
    )
    if invalid_summary["candidate_labels"]:
        for label, count in invalid_summary["candidate_labels"].items():
            lines.append(f"| `{label}` | {count} |")
    else:
        lines.append("| `none` | 0 |")

    lines.extend(
        [
            "",
            "## Uncovered Exact Gold Samples",
            "",
            "| Record | Family | Strata | Gold | Candidate labels |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in uncovered[:30]:
        lines.append(_record_row(row))
    if len(uncovered) > 30:
        lines.append(
            f"| ... | ... | ... | ... | {len(uncovered) - 30} more in JSON report |"
        )

    lines.extend(
        [
            "",
            "## Hard-Stratum Misses With Candidates",
            "",
            "These are target-selection or label-construction candidates for G2/G3: "
            "the substrate found something, but not the exact gold label.",
            "",
            "| Record | Family | Strata | Gold | Candidate labels |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in hard_uncovered[:30]:
        lines.append(_record_row(row))
    if len(hard_uncovered) > 30:
        lines.append(
            "| ... | ... | ... | ... | "
            f"{len(hard_uncovered) - 30} more in JSON report |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a no-model inventory report. It does not score a run and does not "
            "change `gan_frequency_deterministic_v1` or `gan2026_paper_reproduction`.",
            "- Exact coverage measures whether the deterministic substrate already "
            "contains the audited Gan label surface.",
            "- Purist/Pragmatic coverage measures whether a candidate lands in the same "
            "diagnostic category as gold, which can be useful for separating candidate "
            "inventory failures from exact label-construction failures.",
            "- `reference[0]` is used only through hard-case flags; "
            "`seizure_frequency_number[0]` remains the gold label.",
            "",
            "## Companion Artifact",
            "",
            "`docs/experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.json` "
            "contains all record-level candidates, evidence snippets, hard-stratum flags, "
            "and exact/category coverage booleans.",
            "",
        ]
    )
    return "\n".join(lines)


def _summary_table(summary: dict[str, dict[str, Any]], label: str) -> str:
    lines = [
        f"| {label} | Records | Any candidates | Exact | Purist equiv. | Pragmatic equiv. |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, stats in summary.items():
        lines.append(
            f"| `{name}` | {stats['records']} | "
            f"{stats['records_with_candidates']} ({_pct(stats['records_with_candidates_rate'])}) | "
            f"{stats['gold_exact_covered']} ({_pct(stats['gold_exact_coverage_rate'])}) | "
            f"{stats['gold_purist_equivalent_covered']} "
            f"({_pct(stats['gold_purist_equivalent_coverage_rate'])}) | "
            f"{stats['gold_pragmatic_equivalent_covered']} "
            f"({_pct(stats['gold_pragmatic_equivalent_coverage_rate'])}) |"
        )
    return "\n".join(lines)


def _record_row(row: dict[str, Any]) -> str:
    labels = "<br>".join(f"`{label}`" for label in row["candidate_labels"]) or "`none`"
    strata = ", ".join(f"`{stratum}`" for stratum in row["hard_strata"]) or "`none`"
    return (
        f"| `{row['record_id']}` | `{row['label_family']}` | {strata} | "
        f"`{row['gold_label']}` | {labels} |"
    )


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1%}"
