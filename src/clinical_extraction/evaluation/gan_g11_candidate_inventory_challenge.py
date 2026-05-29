"""Gan G11 candidate-inventory challenge-set pass.

This report reuses the existing Gan candidate-inventory surface on the locked
G6 candidate-coverage exact-miss challenge set. It is intentionally no-model
and does not mutate candidate-builder, scorer, loader, split, bridge, or repair
behavior.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.evaluation.gan_candidate_inventory import (
    DEFAULT_GAN_JSON,
    DEFAULT_SPLIT_FILE,
    build_report_from_files,
)

G11_CHALLENGE_SET_NAME = "gan_s0_g6_candidate_coverage_exact_miss"
G11_CHALLENGE_SET_IDS = [
    "gan_15997",
    "gan_16772",
    "gan_16825",
    "gan_16335",
    "gan_10583",
    "gan_1463",
    "gan_9424",
    "gan_6094",
    "gan_1486",
    "gan_7431",
    "gan_16883",
    "gan_4996",
    "gan_3355",
    "gan_15129",
    "gan_9063",
    "gan_13290",
    "gan_6509",
    "gan_4378",
    "gan_6296",
    "gan_13019",
    "gan_9526",
]
G9_STANDARD50_EXACT_MISS_IDS = ["gan_15997", "gan_16772", "gan_16825", "gan_16335"]

DEFAULT_G1_JSON = Path(
    "docs/experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.json"
)
DEFAULT_G11_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g11_candidate_inventory_challenge_set_pass_20260529.json"
)
DEFAULT_G11_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g11_candidate_inventory_challenge_set_pass_20260529.md"
)


def build_g11_candidate_inventory_challenge_report(
    *,
    gan_json: Path = DEFAULT_GAN_JSON,
    split_file: Path = DEFAULT_SPLIT_FILE,
    g1_json: Path = DEFAULT_G1_JSON,
) -> dict[str, Any]:
    """Build the G11 no-model report for the locked G6 challenge set."""

    current = build_report_from_files(
        gan_json=gan_json,
        split_file=split_file,
        split_name="gan_2026_fixed_v1:validation",
    )
    current_rows_by_id = {row["record_id"]: row for row in current["rows"]}
    rows = [current_rows_by_id[record_id] for record_id in G11_CHALLENGE_SET_IDS]
    g1_rows_by_id = _load_g1_rows(g1_json)
    diffs = [
        _g1_diff(row=row, g1_row=g1_rows_by_id.get(row["record_id"])) for row in rows
    ]
    diff_summary = _diff_summary(diffs)
    standard50_rows = [
        row for row in rows if row["record_id"] in G9_STANDARD50_EXACT_MISS_IDS
    ]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "G11 no-model candidate-inventory challenge-set pass",
        "kanban_card": "G11 - Gan Candidate-Inventory Challenge-Set Pass",
        "dataset": "Gan 2026 synthetic",
        "split": "gan_2026_fixed_v1:validation",
        "challenge_set": G11_CHALLENGE_SET_NAME,
        "challenge_set_source": (
            "docs/experiments/gan/"
            "gan_s0_g6_evaluation_slice_standard_decision_20260528.md"
        ),
        "g9_routing_report": (
            "docs/experiments/gan/"
            "gan_s0_g9_exact_miss_failure_inspection_20260529.md"
        ),
        "candidate_source": current["candidate_source"],
        "gold_source": current["gold_source"],
        "reference_policy": current["reference_policy"],
        "scorer_semantics": current["scorer_semantics"],
        "fixed_controls": {
            "model_calls": "none",
            "candidate_builder_policy": (
                "current runtime prunes broad abstention options when concrete "
                "frequency candidates are present"
            ),
            "candidate_builder_changed_since_g1": diff_summary[
                "rows_with_any_diff"
            ]
            > 0,
            "scorer_changed": False,
            "loader_split_bridge_or_repair_changed": False,
            "g1_comparison_artifact": g1_json.as_posix(),
        },
        "summary": _summary(rows),
        "standard50_g9_exact_miss_summary": _summary(standard50_rows),
        "g1_diff_summary": diff_summary,
        "decision": _decision(rows),
        "rows": rows,
        "g1_diffs": diffs,
    }


def write_g11_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_G11_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_G11_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_g11_markdown(report), encoding="utf-8")


def render_g11_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    standard50 = report["standard50_g9_exact_miss_summary"]
    decision = report["decision"]
    lines = [
        "# Gan S0 G11 Candidate-Inventory Challenge-Set Pass",
        "",
        "Date: 2026-05-29",
        "Status: current synthesis / no-model coverage gate",
        f"Kanban card: {report['kanban_card']}",
        f"Dataset/split: {report['dataset']} (`{report['split']}`)",
        f"Challenge set: `{report['challenge_set']}`",
        f"Candidate source: `{report['candidate_source']}`",
        f"Gold source: `{report['gold_source']}`",
        "Scorer semantics: unchanged; category-equivalent coverage is diagnostic.",
        "",
        "## Summary",
        "",
        _coverage_sentence("Challenge set", summary),
        _coverage_sentence("G9 standard50 exact-miss subset", standard50),
        (
            "Compared with the stored G1 substrate, "
            f"**{report['g1_diff_summary']['rows_with_any_diff']}** rows changed."
        ),
        (
            "Candidate-builder policy: "
            f"{report['fixed_controls']['candidate_builder_policy']}."
        ),
        "",
        "## Coverage By Family",
        "",
        _summary_table(summary["by_label_family"], "Family"),
        "",
        "## Coverage By Hard Stratum",
        "",
        _summary_table(summary["by_hard_stratum"], "Hard stratum"),
        "",
        "## Exact-Miss Rows",
        "",
        "| Record | Gold | Family | Purist equiv. | Pragmatic equiv. | Candidate labels |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in report["rows"]:
        lines.append(_row_line(row))
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Inventory-stage interpretation: **{decision['inventory_stage_interpretation']}**.",
            f"- Follow-up: **{decision['follow_up']}**.",
            f"- G10 routing: {decision['g10_routing']}",
            "",
            "## Interpretation",
            "",
            "- The existing candidate inventory still has no exact-label coverage on the locked G6 exact-miss challenge set, but exact coverage is not always expected at the inventory boundary.",
            "- Many gold labels in this surface require temporal anchoring and aggregation across separately reported seizure-frequency events; those exact labels may not appear verbatim in the note.",
            "- Most misses have Purist or Pragmatic category-equivalent candidates, so the open question is whether the downstream aggregation/answer-option construction step can compose the right label from represented event pieces.",
            "- Four records routed by G9 from the G8 standard50 misses remain exact misses, even though all four have Purist and Pragmatic equivalent candidates.",
            "- G10 should not treat raw inventory labels as the complete answer-option set for aggregated cases; it needs an aggregation-aware answer-option surface or an explicit decision to evaluate category-level selection only.",
            "",
            "## Companion Artifact",
            "",
            "`docs/experiments/gan/gan_s0_g11_candidate_inventory_challenge_set_pass_20260529.json` "
            "contains row-level candidates, G1 diffs, summaries, and fixed-control metadata.",
            "",
        ]
    )
    return "\n".join(lines)


def _load_g1_rows(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {row["record_id"]: row for row in data["rows"]}


def _g1_diff(*, row: dict[str, Any], g1_row: dict[str, Any] | None) -> dict[str, Any]:
    if g1_row is None:
        return {"record_id": row["record_id"], "g1_row_present": False}
    compared_keys = [
        "gold_label",
        "label_family",
        "candidate_labels",
        "gold_exact_in_candidates",
        "gold_purist_in_candidates",
        "gold_pragmatic_in_candidates",
        "hard_strata",
    ]
    changed = {
        key: {"g1": g1_row.get(key), "current": row.get(key)}
        for key in compared_keys
        if g1_row.get(key) != row.get(key)
    }
    return {
        "record_id": row["record_id"],
        "g1_row_present": True,
        "changed_keys": sorted(changed),
        "changed_values": changed,
    }


def _diff_summary(diffs: list[dict[str, Any]]) -> dict[str, Any]:
    missing = sum(1 for diff in diffs if not diff.get("g1_row_present"))
    changed = [diff for diff in diffs if diff.get("changed_keys")]
    changed_key_counts = Counter(
        key for diff in changed for key in diff.get("changed_keys", [])
    )
    return {
        "rows": len(diffs),
        "rows_missing_from_g1": missing,
        "rows_with_any_diff": len(changed),
        "changed_key_counts": dict(sorted(changed_key_counts.items())),
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "overall": _coverage(rows),
        "by_label_family": _bucket(rows, "label_family"),
        "by_hard_stratum": _hard_strata(rows),
        "category_gap_rows": [
            row["record_id"]
            for row in rows
            if not row["gold_purist_in_candidates"]
            or not row["gold_pragmatic_in_candidates"]
        ],
    }


def _coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    exact = sum(1 for row in rows if row["gold_exact_in_candidates"])
    purist = sum(1 for row in rows if row["gold_purist_in_candidates"])
    pragmatic = sum(1 for row in rows if row["gold_pragmatic_in_candidates"])
    return {
        "records": total,
        "records_with_candidates": sum(1 for row in rows if row["candidate_count"] > 0),
        "gold_exact_covered": exact,
        "gold_exact_coverage_rate": _rate(exact, total),
        "gold_purist_equivalent_covered": purist,
        "gold_purist_equivalent_coverage_rate": _rate(purist, total),
        "gold_pragmatic_equivalent_covered": pragmatic,
        "gold_pragmatic_equivalent_coverage_rate": _rate(pragmatic, total),
    }


def _bucket(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row[key])].append(row)
    return {name: _coverage(bucket_rows) for name, bucket_rows in sorted(buckets.items())}


def _hard_strata(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for stratum in row["hard_strata"]:
            buckets[stratum].append(row)
    return {name: _coverage(bucket_rows) for name, bucket_rows in sorted(buckets.items())}


def _decision(rows: list[dict[str, Any]]) -> dict[str, str]:
    exact = sum(1 for row in rows if row["gold_exact_in_candidates"])
    purist = sum(1 for row in rows if row["gold_purist_in_candidates"])
    pragmatic = sum(1 for row in rows if row["gold_pragmatic_in_candidates"])
    if exact == len(rows):
        interpretation = "raw_inventory_exact_covers_gold"
        follow_up = "none_before_g10"
        routing = "G10 can proceed with raw-inventory exact-label answer options on this surface."
    else:
        interpretation = "raw_inventory_requires_aggregation_aware_answer_options"
        follow_up = "scope_temporal_anchoring_and_aggregation_answer_option_surface"
        routing = (
            "Do not use raw inventory labels alone as exact-label answer options. "
            f"Current coverage is {exact}/{len(rows)} exact, {purist}/{len(rows)} "
            f"Purist-equivalent, and {pragmatic}/{len(rows)} Pragmatic-equivalent; "
            "aggregated gold labels may need to be constructed downstream from "
            "separately reported event pieces."
        )
    return {
        "inventory_stage_interpretation": interpretation,
        "follow_up": follow_up,
        "g10_routing": routing,
    }


def _coverage_sentence(label: str, summary: dict[str, Any]) -> str:
    overall = summary["overall"]
    return (
        f"{label} coverage: **{overall['gold_exact_covered']}/{overall['records']}** "
        f"exact, **{overall['gold_purist_equivalent_covered']}/{overall['records']}** "
        f"Purist-equivalent, and **{overall['gold_pragmatic_equivalent_covered']}/"
        f"{overall['records']}** Pragmatic-equivalent."
    )


def _summary_table(summary: dict[str, dict[str, Any]], label: str) -> str:
    lines = [
        f"| {label} | Records | Exact | Purist equiv. | Pragmatic equiv. |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, stats in summary.items():
        lines.append(
            f"| `{name}` | {stats['records']} | "
            f"{stats['gold_exact_covered']} ({_pct(stats['gold_exact_coverage_rate'])}) | "
            f"{stats['gold_purist_equivalent_covered']} "
            f"({_pct(stats['gold_purist_equivalent_coverage_rate'])}) | "
            f"{stats['gold_pragmatic_equivalent_covered']} "
            f"({_pct(stats['gold_pragmatic_equivalent_coverage_rate'])}) |"
        )
    return "\n".join(lines)


def _row_line(row: dict[str, Any]) -> str:
    labels = "<br>".join(f"`{label}`" for label in row["candidate_labels"]) or "`none`"
    return (
        f"| `{row['record_id']}` | `{row['gold_label']}` | "
        f"`{row['label_family']}` | {_yes_no(row['gold_purist_in_candidates'])} | "
        f"{_yes_no(row['gold_pragmatic_in_candidates'])} | {labels} |"
    )


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _rate(count: int, total: int) -> float | None:
    return count / total if total else None


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1%}"


__all__ = [
    "DEFAULT_G11_JSON_OUTPUT",
    "DEFAULT_G11_MARKDOWN_OUTPUT",
    "G11_CHALLENGE_SET_IDS",
    "G11_CHALLENGE_SET_NAME",
    "G9_STANDARD50_EXACT_MISS_IDS",
    "build_g11_candidate_inventory_challenge_report",
    "render_g11_markdown",
    "write_g11_report_artifacts",
]
