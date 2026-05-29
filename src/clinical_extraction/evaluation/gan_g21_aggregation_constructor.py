"""Gan G21 deterministic aggregation-constructor fixture report."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_g11_candidate_inventory_challenge import (
    DEFAULT_G11_JSON_OUTPUT,
    G11_CHALLENGE_SET_NAME,
)
from clinical_extraction.evaluation.gan_g16_aggregation_policy import (
    DEFAULT_G16_JSON_OUTPUT,
)
from clinical_extraction.evaluation.gan_temporal_anchoring_g14 import (
    DEFAULT_G14_JSON_OUTPUT,
    G14_STANDARD50_NAME,
)
from clinical_extraction.gan.frequency import normalize_label
from clinical_extraction.gan.s0.aggregation_constructor import (
    GAN_S0_AGGREGATION_CONSTRUCTOR_PRIMITIVE_ID,
    construct_gan_s0_aggregation_options,
)

DEFAULT_G21_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.json"
)
DEFAULT_G21_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.md"
)


def build_g21_aggregation_constructor_report(
    *,
    g11_json: Path = DEFAULT_G11_JSON_OUTPUT,
    g14_json: Path = DEFAULT_G14_JSON_OUTPUT,
    g16_json: Path = DEFAULT_G16_JSON_OUTPUT,
) -> dict[str, Any]:
    """Build the G21 no-model fixture report."""

    g11 = json.loads(g11_json.read_text(encoding="utf-8"))
    g14 = json.loads(g14_json.read_text(encoding="utf-8"))
    g16 = json.loads(g16_json.read_text(encoding="utf-8"))
    records_by_id = {record.record_id: record for record in load_gan_records()}
    g16_g11 = {
        row["record_id"]: row for row in g16["rows"]["g11_exact_miss_challenge"]
    }
    g16_standard = {row["record_id"]: row for row in g16["rows"]["standard50"]}

    g11_rows = [
        _constructor_row(
            source_row=row,
            policy_row=g16_g11[row["record_id"]],
            record=records_by_id[row["record_id"]],
        )
        for row in g11["rows"]
    ]
    standard_rows = [
        _constructor_row(
            source_row=row,
            policy_row=g16_standard[row["record_id"]],
            record=records_by_id[row["record_id"]],
        )
        for row in g14["rows"]
    ]
    g11_summary = _summary(g11_rows)
    standard_summary = _summary(standard_rows)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "G21 deterministic aggregation-constructor fixture implementation",
        "kanban_card": "G21 - Gan Deterministic Aggregation Constructor Fixture Implementation",
        "dataset": "Gan 2026 synthetic",
        "split": "gan_2026_fixed_v1:validation",
        "surfaces": {
            "standard50": G14_STANDARD50_NAME,
            "g11_exact_miss_challenge": G11_CHALLENGE_SET_NAME,
        },
        "primitive_id": GAN_S0_AGGREGATION_CONSTRUCTOR_PRIMITIVE_ID,
        "source_artifacts": {
            "g11_candidate_inventory_challenge": g11_json.as_posix(),
            "g14_temporal_anchoring": g14_json.as_posix(),
            "g16_aggregation_policy": g16_json.as_posix(),
        },
        "fixed_controls": {
            "model_calls": "none",
            "scorer_changed": False,
            "loader_split_bridge_prompt_or_repair_changed": False,
            "candidate_builder_changed": False,
            "target_selection_changed": False,
            "prediction_repair_changed": False,
            "raw_candidate_records_mutated": False,
        },
        "policy": {
            "eligible_policy_class": "aggregation_required_temporal_slot_missing",
            "deferred_or_negative_policy_classes": [
                "duration_aggregation_policy_required",
                "candidate_inventory_gap_before_aggregation",
                "outside_rate_duration_aggregation_policy",
                "closed_option_already_available",
                "upstream_gate_caveat_before_aggregation",
            ],
            "scope": (
                "Construct quantified-rate answer options only; do not construct "
                "duration, special-label, cluster-flattening, or final target labels."
            ),
        },
        "summary": {
            "g11_exact_miss_challenge": g11_summary,
            "standard50": standard_summary,
        },
        "decision": _decision(g11_summary, standard_summary),
        "rows": {
            "g11_exact_miss_challenge": g11_rows,
            "standard50": standard_rows,
        },
    }


def write_g21_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_G21_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_G21_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_g21_markdown(report), encoding="utf-8")


def render_g21_markdown(report: dict[str, Any]) -> str:
    g11 = report["summary"]["g11_exact_miss_challenge"]
    standard = report["summary"]["standard50"]
    decision = report["decision"]
    lines = [
        "# Gan S0 G21 Aggregation Constructor Report",
        "",
        "Date: 2026-05-29",
        "Status: current synthesis / fixture-tested no-model constructor",
        f"Kanban card: {report['kanban_card']}",
        f"Dataset/split: {report['dataset']} (`{report['split']}`)",
        f"Primitive ID: `{report['primitive_id']}`",
        "Model calls: none",
        "Scorer, loader, split, bridge, prompt, model, candidate-builder, target-selection, and prediction-repair semantics: unchanged.",
        "",
        "## Summary",
        "",
        _summary_sentence("Standard50", standard),
        _summary_sentence("G11 exact-miss challenge", g11),
        (
            "Negative/deferred control constructions: "
            f"**{g11['negative_or_deferred_constructed']}** on G11 and "
            f"**{standard['negative_or_deferred_constructed']}** on Standard50."
        ),
        "",
        "## Decision",
        "",
        f"- Standard50 gate passed: **{_yn(decision['standard50_gate_passed'])}**.",
        f"- G11 gate passed: **{_yn(decision['g11_gate_passed'])}**.",
        f"- Classification: **{decision['classification']}**.",
        f"- Next authorization: {decision['next_authorization']}",
        "",
        "## G11 Fixture Rows",
        "",
        "| Record | Gold | Policy class | Raw exact | Constructed exact | Constructed labels |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in report["rows"]["g11_exact_miss_challenge"]:
        labels = (
            "<br>".join(
                f"`{option['constructed_label']}`"
                for option in row["constructed_options"]
            )
            or "`none`"
        )
        lines.append(
            f"| `{row['record_id']}` | `{row['gold_label']}` | "
            f"`{row['policy_class']}` | {_yn(row['raw_exact_covered'])} | "
            f"{_yn(row['constructed_exact_covered'])} | {labels} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- G21 creates a separate constructed answer-option surface; raw temporal candidates are preserved unchanged.",
            "- Coverage gains are answer-option coverage only, not selector, Purist, Pragmatic, canonical monthly, or paper-reproduction performance.",
            "- Duration rows, inventory gaps, special labels, unknown clusters, and final target selection remain outside this constructor.",
            "",
            "## Companion Artifact",
            "",
            "`docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.json` contains row-level constructor diagnostics, raw candidate snapshots, constructed options, and fixed-control metadata.",
            "",
        ]
    )
    return "\n".join(lines)


def _constructor_row(
    *,
    source_row: dict[str, Any],
    policy_row: dict[str, Any],
    record: Any,
) -> dict[str, Any]:
    raw_candidate_records = list(source_row["candidate_records"])
    options = construct_gan_s0_aggregation_options(
        record=record,
        policy_class=policy_row["policy_class"],
        candidate_records=raw_candidate_records,
    )
    constructed = [option.to_dict() for option in options]
    gold = normalize_label(source_row["gold_label"])
    constructed_labels = {
        normalize_label(option["constructed_label"]) for option in constructed
    }
    raw_labels = {
        normalize_label(candidate.get("canonical_label") or "")
        for candidate in raw_candidate_records
    }
    raw_exact = gold in raw_labels
    constructed_exact = gold in constructed_labels
    return {
        "record_id": source_row["record_id"],
        "gold_label": source_row["gold_label"],
        "label_family": source_row["label_family"],
        "policy_class": policy_row["policy_class"],
        "raw_candidate_labels": source_row["candidate_labels"],
        "raw_candidate_records": raw_candidate_records,
        "post_constructor_raw_candidate_records": list(raw_candidate_records),
        "constructed_options": constructed,
        "constructed_labels": [option["constructed_label"] for option in constructed],
        "raw_exact_covered": raw_exact,
        "constructed_exact_covered": constructed_exact,
        "combined_exact_covered": raw_exact or constructed_exact,
        "negative_or_deferred_constructed": (
            bool(constructed)
            and policy_row["policy_class"]
            != "aggregation_required_temporal_slot_missing"
        ),
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    policy_counts = Counter(row["policy_class"] for row in rows)
    return {
        "records": len(rows),
        "raw_exact_covered": sum(1 for row in rows if row["raw_exact_covered"]),
        "constructed_exact_covered": sum(
            1 for row in rows if row["constructed_exact_covered"]
        ),
        "combined_exact_covered": sum(
            1 for row in rows if row["combined_exact_covered"]
        ),
        "constructed_option_rows": sum(
            1 for row in rows if row["constructed_options"]
        ),
        "constructed_option_count": sum(
            len(row["constructed_options"]) for row in rows
        ),
        "negative_or_deferred_constructed": sum(
            1 for row in rows if row["negative_or_deferred_constructed"]
        ),
        "policy_class_counts": dict(sorted(policy_counts.items())),
        "constructed_exact_record_ids": [
            row["record_id"] for row in rows if row["constructed_exact_covered"]
        ],
    }


def _decision(
    g11_summary: dict[str, Any],
    standard_summary: dict[str, Any],
) -> dict[str, Any]:
    standard_gate = (
        standard_summary["constructed_exact_covered"] >= 3
        and standard_summary["negative_or_deferred_constructed"] == 0
    )
    g11_gate = (
        g11_summary["constructed_exact_covered"] >= 10
        and g11_summary["negative_or_deferred_constructed"] == 0
    )
    return {
        "standard50_gate_passed": standard_gate,
        "g11_gate_passed": g11_gate,
        "classification": (
            "deterministic_quantified_rate_constructor_gate_passed"
            if standard_gate and g11_gate
            else "deterministic_quantified_rate_constructor_needs_revision"
        ),
        "next_authorization": (
            "A later selector card may compare closed-option target selection "
            "with a row-level before/after ledger; this report itself is not "
            "selector performance."
            if standard_gate and g11_gate
            else "Do not proceed to selector work from this constructor surface."
        ),
    }


def _summary_sentence(label: str, summary: dict[str, Any]) -> str:
    return (
        f"{label}: raw exact **{summary['raw_exact_covered']}/"
        f"{summary['records']}**, constructed exact **"
        f"{summary['constructed_exact_covered']}/{summary['records']}**, "
        f"combined exact **{summary['combined_exact_covered']}/"
        f"{summary['records']}**."
    )


def _yn(value: bool) -> str:
    return "yes" if value else "no"


__all__ = [
    "DEFAULT_G21_JSON_OUTPUT",
    "DEFAULT_G21_MARKDOWN_OUTPUT",
    "build_g21_aggregation_constructor_report",
    "render_g21_markdown",
    "write_g21_report_artifacts",
]
