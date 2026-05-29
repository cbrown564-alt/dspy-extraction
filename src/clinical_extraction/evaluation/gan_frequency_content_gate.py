"""Gan G13 frequency-content gate evaluation.

This module evaluates the source-level gate separately from candidate
construction and target selection. It reuses the current deterministic temporal
candidate substrate, but reports only coarse content classes.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_candidate_inventory import (
    DEFAULT_GAN_JSON,
    DEFAULT_SPLIT_FILE,
)
from clinical_extraction.evaluation.gan_run_analysis import load_split_ids
from clinical_extraction.gan.s0.candidate_inventory import gan_s0_label_family
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates,
    temporal_candidate_to_dict,
)
from clinical_extraction.schemas import GanRecord

GateClass = Literal[
    "no_reference",
    "unknown_unclear_frequency",
    "seizure_free",
    "quantified_frequency_presence",
]

DEFAULT_SPLIT_NAME = "gan_2026_fixed_v1:validation"
DEFAULT_G13_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g13_frequency_content_gate_report_20260529.json"
)
DEFAULT_G13_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g13_frequency_content_gate_report_20260529.md"
)

GATE_CLASSES: tuple[GateClass, ...] = (
    "no_reference",
    "unknown_unclear_frequency",
    "seizure_free",
    "quantified_frequency_presence",
)


def build_g13_frequency_content_gate_report(
    *,
    gan_json: Path = DEFAULT_GAN_JSON,
    split_file: Path = DEFAULT_SPLIT_FILE,
    split_name: str = DEFAULT_SPLIT_NAME,
) -> dict[str, Any]:
    """Evaluate the isolated Gan frequency-content gate on a split."""

    records = load_gan_records(gan_json)
    records_by_id = {record.record_id: record for record in records}
    record_ids = load_split_ids(split_file, split_name)
    rows = [_gate_row(records_by_id[record_id]) for record_id in record_ids]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "G13 no-model isolated frequency-content gate evaluation",
        "kanban_card": "G13 - Gan Isolated Frequency-Content Gate Evaluation and Refinement",
        "dataset": "gan_2026",
        "split": split_name,
        "component": "frequency-content gate",
        "gate_source": "current deterministic temporal candidate substrate",
        "gold_source": "check__Seizure Frequency Number.seizure_frequency_number[0]",
        "reference_policy": (
            "reference[0] is a secondary difficulty signal, not benchmark gold"
        ),
        "fixed_controls": {
            "model_calls": "none",
            "scorer_changed": False,
            "loader_split_bridge_prompt_or_repair_changed": False,
            "candidate_builder_changed": False,
            "target_selection_changed": False,
        },
        "class_policy": {
            "no_reference": "`no seizure frequency reference` gold or sole no-reference candidate.",
            "unknown_unclear_frequency": (
                "`unknown` and `unknown, N per cluster`; cluster-spacing-unknown "
                "labels are retained as an overlay because per-cluster burden is "
                "informative but the temporal frequency remains unclear."
            ),
            "seizure_free": "`seizure free for ...` labels.",
            "quantified_frequency_presence": (
                "rate labels and cluster labels with explicit cluster spacing."
            ),
        },
        "summary": _summarize_rows(rows),
        "rows": rows,
    }


def write_g13_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_G13_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_G13_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_g13_markdown(report), encoding="utf-8")


def gold_gate_class(label: str) -> GateClass:
    """Collapse Gan canonical labels into the G13 gate target classes."""

    family = gan_s0_label_family(label)
    if family == "no_reference":
        return "no_reference"
    if family in {"unknown", "unknown_cluster"}:
        return "unknown_unclear_frequency"
    if family == "seizure_free":
        return "seizure_free"
    return "quantified_frequency_presence"


def predicted_gate_class(candidate_labels: list[str]) -> GateClass:
    """Classify the gate from candidate labels without selecting a final target."""

    families = {gan_s0_label_family(label) for label in candidate_labels}
    if families & {"quantified_rate", "vague_or_multiple_rate", "cluster"}:
        return "quantified_frequency_presence"
    if "seizure_free" in families:
        return "seizure_free"
    if families & {"unknown", "unknown_cluster"}:
        return "unknown_unclear_frequency"
    return "no_reference"


def _gate_row(record: GanRecord) -> dict[str, Any]:
    candidates = build_temporal_frequency_candidates(record)
    candidate_labels = [candidate.canonical_label for candidate in candidates]
    predicted = predicted_gate_class(candidate_labels)
    gold = gold_gate_class(record.gold_label)
    return {
        "record_id": record.record_id,
        "gold_label": record.gold_label,
        "gold_gate_class": gold,
        "predicted_gate_class": predicted,
        "gate_class_match": gold == predicted,
        "gold_label_family": gan_s0_label_family(record.gold_label),
        "candidate_count": len(candidates),
        "candidate_labels": candidate_labels,
        "candidate_label_families": sorted(
            {gan_s0_label_family(label) for label in candidate_labels}
        ),
        "row_ok": record.row_ok,
        "hard_case": "hard_case" in record.flags,
        "reference_label": record.reference_label,
        "gold_evidence": record.gold_evidence,
        "candidate_records": [
            temporal_candidate_to_dict(candidate) for candidate in candidates
        ],
    }


def _summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    correct = sum(1 for row in rows if row["gate_class_match"])
    return {
        "overall": {
            "records": total,
            "correct": correct,
            "accuracy": _rate(correct, total),
        },
        "per_class": _per_class_metrics(rows),
        "confusion_matrix": _confusion_matrix(rows),
        "by_gold_label_family": _bucketed_accuracy(rows, "gold_label_family"),
        "by_row_ok": _bucketed_accuracy(rows, "row_ok"),
        "by_hard_case": _bucketed_accuracy(rows, "hard_case"),
        "error_counts": _error_counts(rows),
        "false_positive_false_negative_focus": _fp_fn_focus(rows),
    }


def _per_class_metrics(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for klass in GATE_CLASSES:
        tp = sum(
            1
            for row in rows
            if row["gold_gate_class"] == klass and row["predicted_gate_class"] == klass
        )
        fp = sum(
            1
            for row in rows
            if row["gold_gate_class"] != klass and row["predicted_gate_class"] == klass
        )
        fn = sum(
            1
            for row in rows
            if row["gold_gate_class"] == klass and row["predicted_gate_class"] != klass
        )
        precision = _rate(tp, tp + fp)
        recall = _rate(tp, tp + fn)
        metrics[klass] = {
            "support": tp + fn,
            "predicted": tp + fp,
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "precision": precision,
            "recall": recall,
            "f1": _f1(precision, recall),
        }
    return metrics


def _confusion_matrix(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    matrix = {
        gold: {predicted: 0 for predicted in GATE_CLASSES} for gold in GATE_CLASSES
    }
    for row in rows:
        matrix[row["gold_gate_class"]][row["predicted_gate_class"]] += 1
    return matrix


def _bucketed_accuracy(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row[key])].append(row)
    return {
        bucket: {
            "records": len(bucket_rows),
            "correct": sum(1 for row in bucket_rows if row["gate_class_match"]),
            "accuracy": _rate(
                sum(1 for row in bucket_rows if row["gate_class_match"]),
                len(bucket_rows),
            ),
        }
        for bucket, bucket_rows in sorted(buckets.items())
    }


def _error_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        if not row["gate_class_match"]:
            counts[f"{row['gold_gate_class']} -> {row['predicted_gate_class']}"] += 1
    return dict(sorted(counts.items()))


def _fp_fn_focus(rows: list[dict[str, Any]]) -> dict[str, Any]:
    focus_classes = (
        "no_reference",
        "unknown_unclear_frequency",
        "quantified_frequency_presence",
    )
    focus: dict[str, Any] = {}
    for klass in focus_classes:
        false_positives = [
            _compact_error_row(row)
            for row in rows
            if row["gold_gate_class"] != klass and row["predicted_gate_class"] == klass
        ]
        false_negatives = [
            _compact_error_row(row)
            for row in rows
            if row["gold_gate_class"] == klass and row["predicted_gate_class"] != klass
        ]
        focus[klass] = {
            "false_positive_count": len(false_positives),
            "false_negative_count": len(false_negatives),
            "false_positives": false_positives,
            "false_negatives": false_negatives,
        }
    return focus


def _compact_error_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": row["record_id"],
        "gold_label": row["gold_label"],
        "gold_gate_class": row["gold_gate_class"],
        "predicted_gate_class": row["predicted_gate_class"],
        "candidate_labels": row["candidate_labels"],
        "reference_label": row["reference_label"],
        "hard_case": row["hard_case"],
    }


def render_g13_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    overall = summary["overall"]
    lines = [
        "# Gan S0 G13 Frequency-Content Gate Report",
        "",
        "Date: 2026-05-29",
        "Status: current synthesis / no-model isolated gate evaluation",
        f"Kanban card: {report['kanban_card']}",
        f"Dataset/split: Gan 2026 synthetic (`{report['split']}`)",
        f"Gate source: `{report['gate_source']}`",
        f"Gold source: `{report['gold_source']}`",
        "Fixed controls: no model calls; no scorer, loader, split, bridge, prompt, target-selection, or prediction-repair changes.",
        "",
        "## Summary",
        "",
        (
            f"Overall gate accuracy is **{overall['correct']}/{overall['records']}** "
            f"({_pct(overall['accuracy'])})."
        ),
        "",
        "## Per-Class Metrics",
        "",
        "| Gate class | Support | Predicted | Precision | Recall | F1 | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for klass in GATE_CLASSES:
        metric = summary["per_class"][klass]
        lines.append(
            "| "
            f"`{klass}` | {metric['support']} | {metric['predicted']} | "
            f"{_pct(metric['precision'])} | {_pct(metric['recall'])} | "
            f"{_pct(metric['f1'])} | {metric['false_positive']} | "
            f"{metric['false_negative']} |"
        )
    lines.extend(
        [
            "",
            "## Confusion Matrix",
            "",
            "| Gold \\ predicted | no_reference | unknown_unclear_frequency | seizure_free | quantified_frequency_presence |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for gold in GATE_CLASSES:
        cells = summary["confusion_matrix"][gold]
        lines.append(
            f"| `{gold}` | {cells['no_reference']} | "
            f"{cells['unknown_unclear_frequency']} | {cells['seizure_free']} | "
            f"{cells['quantified_frequency_presence']} |"
        )
    lines.extend(
        [
            "",
            "## Error Routing",
            "",
        ]
    )
    if summary["error_counts"]:
        for key, count in summary["error_counts"].items():
            lines.append(f"- `{key}`: {count}")
    else:
        lines.append("- No gate errors on this split.")
    lines.extend(
        [
            "",
            "## Gate Policy",
            "",
            "- `unknown` and `no seizure frequency reference` remain distinct under the canonical project policy.",
            "- `unknown, N per cluster` is counted with unclear-frequency labels for this gate because cluster spacing is unknown, while row-level JSON keeps the per-cluster burden visible.",
            "- Quantified-rate and explicit cluster-spacing candidates are counted as frequency-presence signals; final target selection remains out of scope.",
            "- Seizure-free labels are separated because later selector work needs to know whether the gate itself can identify remission evidence before adjudicating it against current quantified events.",
            "",
            "## Decision",
            "",
            "- The isolated deterministic gate is strong enough to use as a diagnostic baseline, but errors should be routed by class before G14/G15 so temporal anchoring and target selection are not blamed for source-level gate mistakes.",
            "- The row-level JSON lists false positives and false negatives for no-reference, unclear-frequency, and quantified-frequency-presence classes for follow-up inspection.",
            "",
            "## Companion Artifact",
            "",
            "`docs/experiments/gan/gan_s0_g13_frequency_content_gate_report_20260529.json` contains row-level candidate labels, candidate records, confusion counts, and false-positive/false-negative lists.",
            "",
        ]
    )
    return "\n".join(lines)


def _rate(count: int, total: int) -> float | None:
    return count / total if total else None


def _f1(precision: float | None, recall: float | None) -> float | None:
    if precision is None or recall is None or precision + recall == 0:
        return None
    return 2 * precision * recall / (precision + recall)


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


__all__ = [
    "DEFAULT_G13_JSON_OUTPUT",
    "DEFAULT_G13_MARKDOWN_OUTPUT",
    "GATE_CLASSES",
    "build_g13_frequency_content_gate_report",
    "gold_gate_class",
    "predicted_gate_class",
    "render_g13_markdown",
    "write_g13_report_artifacts",
]
