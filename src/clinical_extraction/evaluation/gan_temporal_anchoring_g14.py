"""Gan G14 temporal anchoring evaluation.

This is a no-model component report over the current deterministic temporal
candidate substrate. It measures whether temporal count/window slots are
represented before any target selector, aggregation constructor, scorer repair,
or prompt change.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_candidate_inventory import (
    DEFAULT_GAN_JSON,
    DEFAULT_SPLIT_FILE,
)
from clinical_extraction.evaluation.gan_frequency_content_gate import (
    build_g13_frequency_content_gate_report,
)
from clinical_extraction.gan.frequency import (
    normalize_label,
    pragmatic_category,
    purist_category,
)
from clinical_extraction.gan.s0.candidate_inventory import gan_s0_label_family
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates,
    temporal_candidate_to_dict,
)
from clinical_extraction.schemas import GanRecord

G14_STANDARD50_NAME = "gan_s0_g6_standard50_v1"
G14_TEMPORAL_CHALLENGE_NAME = "gan_s0_g6_temporal_anchoring"
G14_STANDARD50_IDS = [
    "gan_14485",
    "gan_6532",
    "gan_10434",
    "gan_4956",
    "gan_13123",
    "gan_4702",
    "gan_10052",
    "gan_2609",
    "gan_1794",
    "gan_15306",
    "gan_7894",
    "gan_3246",
    "gan_4113",
    "gan_14881",
    "gan_536",
    "gan_4709",
    "gan_9566",
    "gan_12679",
    "gan_1584",
    "gan_15997",
    "gan_17287",
    "gan_16251",
    "gan_16772",
    "gan_16825",
    "gan_12950",
    "gan_10047",
    "gan_12810",
    "gan_10398",
    "gan_16041",
    "gan_714",
    "gan_12465",
    "gan_4011",
    "gan_804",
    "gan_22",
    "gan_16335",
    "gan_3867",
    "gan_13574",
    "gan_5974",
    "gan_6607",
    "gan_8564",
    "gan_6387",
    "gan_8264",
    "gan_14002",
    "gan_11380",
    "gan_11408",
    "gan_11841",
    "gan_7818",
    "gan_13598",
    "gan_13595",
    "gan_11874",
]
G14_TEMPORAL_CHALLENGE_IDS = [
    "gan_14485",
    "gan_13123",
    "gan_4702",
    "gan_2609",
    "gan_1794",
    "gan_12679",
    "gan_1584",
    "gan_17287",
    "gan_16772",
    "gan_16825",
    "gan_12950",
    "gan_714",
    "gan_12465",
    "gan_804",
    "gan_22",
]

DEFAULT_G14_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g14_temporal_anchoring_report_20260529.json"
)
DEFAULT_G14_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g14_temporal_anchoring_report_20260529.md"
)


def build_g14_temporal_anchoring_report(
    *,
    gan_json: Path = DEFAULT_GAN_JSON,
    split_file: Path = DEFAULT_SPLIT_FILE,
) -> dict[str, Any]:
    """Build the G14 no-model temporal anchoring report."""

    records = load_gan_records(gan_json)
    records_by_id = {record.record_id: record for record in records}
    g13_rows = build_g13_frequency_content_gate_report(
        gan_json=gan_json,
        split_file=split_file,
    )["rows"]
    g13_by_id = {row["record_id"]: row for row in g13_rows}
    standard_rows = [
        _anchoring_row(records_by_id[record_id], g13_by_id[record_id])
        for record_id in G14_STANDARD50_IDS
    ]
    temporal_rows = [
        row
        for row in standard_rows
        if row["record_id"] in set(G14_TEMPORAL_CHALLENGE_IDS)
    ]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "G14 no-model temporal anchoring evaluation",
        "kanban_card": "G14 - Gan Temporal Anchoring Evaluation and Optimization",
        "dataset": "Gan 2026 synthetic",
        "split": "gan_2026_fixed_v1:validation",
        "component": "temporal anchoring",
        "surfaces": {
            "standard50": G14_STANDARD50_NAME,
            "temporal_challenge": G14_TEMPORAL_CHALLENGE_NAME,
        },
        "surface_source": (
            "docs/experiments/gan/"
            "gan_s0_g6_evaluation_slice_standard_decision_20260528.md"
        ),
        "gate_caveat_source": (
            "docs/experiments/gan/"
            "gan_s0_g13_frequency_content_gate_report_20260529.json"
        ),
        "candidate_source": "current deterministic temporal candidate substrate",
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
            "prediction_repair_changed": False,
        },
        "metric_policy": {
            "exact_candidate_coverage": (
                "gold label appears verbatim in current candidate labels"
            ),
            "temporal_slot_coverage": (
                "candidate preserves the gold event-count/window-count/window-unit "
                "slot for labels with an explicit temporal slot; cluster rows test "
                "cluster cadence, not per-cluster burden"
            ),
            "gate_caveated_metrics": (
                "rows where the G13 source-level gate already misclassified the "
                "content state are excluded from the caveated denominator"
            ),
        },
        "summary": {
            "standard50": _summary(standard_rows),
            "temporal_challenge": _summary(temporal_rows),
        },
        "failure_classes": _failure_class_counts(standard_rows),
        "decision": _decision(standard_rows, temporal_rows),
        "rows": standard_rows,
    }


def write_g14_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_G14_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_G14_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_g14_markdown(report), encoding="utf-8")


def _anchoring_row(record: GanRecord, g13_row: dict[str, Any]) -> dict[str, Any]:
    candidates = build_temporal_frequency_candidates(record)
    candidate_labels = [candidate.canonical_label for candidate in candidates]
    candidate_records = [temporal_candidate_to_dict(candidate) for candidate in candidates]
    gold_slot = _temporal_slot(record.gold_label)
    temporal_applicable = gold_slot["temporal_applicable"]
    exact = normalize_label(record.gold_label) in {
        normalize_label(label) for label in candidate_labels
    }
    slot_match = (
        _candidate_slot_match(gold_slot, candidate_records)
        if temporal_applicable
        else None
    )
    purist = _category_covered(record.gold_label, candidate_labels, purist_category)
    pragmatic = _category_covered(
        record.gold_label,
        candidate_labels,
        pragmatic_category,
    )
    gate_match = g13_row["gate_class_match"]
    return {
        "record_id": record.record_id,
        "gold_label": record.gold_label,
        "label_family": gan_s0_label_family(record.gold_label),
        "gold_temporal_slot": gold_slot,
        "temporal_applicable": temporal_applicable,
        "candidate_count": len(candidates),
        "candidate_labels": candidate_labels,
        "candidate_records": candidate_records,
        "exact_candidate_coverage": exact,
        "temporal_slot_coverage": slot_match,
        "purist_equivalent_coverage": purist,
        "pragmatic_equivalent_coverage": pragmatic,
        "g13_gold_gate_class": g13_row["gold_gate_class"],
        "g13_predicted_gate_class": g13_row["predicted_gate_class"],
        "g13_gate_class_match": gate_match,
        "gate_caveated": not gate_match,
        "g14_failure_class": _failure_class(
            exact=exact,
            temporal_applicable=temporal_applicable,
            slot_match=slot_match,
            purist=purist,
            pragmatic=pragmatic,
            gate_match=gate_match,
        ),
        "row_ok": record.row_ok,
        "hard_case": "hard_case" in record.flags,
        "reference_label": record.reference_label,
        "gold_evidence": record.gold_evidence,
    }


def _temporal_slot(label: str) -> dict[str, Any]:
    normalized = normalize_label(label)
    if normalized in {"unknown", "no seizure frequency reference"}:
        return _slot(False, "", "", "", "special_label_no_temporal_slot")
    if normalized.startswith("unknown,"):
        return _slot(False, "", "", "", "unknown_cluster_spacing")
    if normalized.startswith("seizure free for "):
        duration = normalized.removeprefix("seizure free for ")
        parts = duration.split()
        return _slot(True, "0", parts[0], parts[1], "seizure_free_duration")
    cluster = re.fullmatch(
        r"(?P<count>.+?) cluster per (?:(?P<period>.+?) )?"
        r"(?P<unit>day|week|month|year), (?P<per_cluster>.+?) per cluster",
        normalized,
    )
    if cluster:
        return _slot(
            True,
            f"{cluster.group('count')} cluster",
            cluster.group("period") or "1",
            cluster.group("unit"),
            "cluster_cadence",
        )
    rate = re.fullmatch(
        r"(?P<count>.+?) per (?:(?P<period>.+?) )?"
        r"(?P<unit>day|week|month|year)",
        normalized,
    )
    if rate:
        return _slot(
            True,
            rate.group("count"),
            rate.group("period") or "1",
            rate.group("unit"),
            "rate_window",
        )
    return _slot(False, "", "", "", "unparsed_label")


def _slot(
    temporal_applicable: bool,
    event_count: str,
    window_count: str,
    window_unit: str,
    slot_kind: str,
) -> dict[str, Any]:
    return {
        "temporal_applicable": temporal_applicable,
        "event_count": event_count,
        "window_count": window_count,
        "window_unit": window_unit,
        "slot_kind": slot_kind,
    }


def _candidate_slot_match(
    gold_slot: dict[str, Any],
    candidate_records: list[dict[str, str]],
) -> bool:
    for candidate in candidate_records:
        if (
            normalize_label(candidate.get("event_count", ""))
            == normalize_label(gold_slot["event_count"])
            and normalize_label(candidate.get("window_count", ""))
            == normalize_label(gold_slot["window_count"])
            and normalize_label(candidate.get("window_unit", ""))
            == normalize_label(gold_slot["window_unit"])
        ):
            return True
    return False


def _category_covered(label: str, candidates: list[str], category_fn: Any) -> bool:
    try:
        gold_category = category_fn(label)
    except ValueError:
        return False
    for candidate in candidates:
        try:
            if category_fn(candidate) == gold_category:
                return True
        except ValueError:
            continue
    return False


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    temporal_rows = [row for row in rows if row["temporal_applicable"]]
    gate_clean_rows = [row for row in rows if not row["gate_caveated"]]
    temporal_gate_clean_rows = [
        row for row in temporal_rows if not row["gate_caveated"]
    ]
    return {
        "records": len(rows),
        "temporal_applicable_records": len(temporal_rows),
        "gate_caveated_records": sum(1 for row in rows if row["gate_caveated"]),
        "exact_candidate_coverage": _coverage(rows, "exact_candidate_coverage"),
        "temporal_slot_coverage": _coverage(
            temporal_rows,
            "temporal_slot_coverage",
        ),
        "purist_equivalent_coverage": _coverage(rows, "purist_equivalent_coverage"),
        "pragmatic_equivalent_coverage": _coverage(
            rows,
            "pragmatic_equivalent_coverage",
        ),
        "gate_clean_exact_candidate_coverage": _coverage(
            gate_clean_rows,
            "exact_candidate_coverage",
        ),
        "gate_clean_temporal_slot_coverage": _coverage(
            temporal_gate_clean_rows,
            "temporal_slot_coverage",
        ),
        "by_label_family": _bucketed(rows, "label_family"),
        "failure_classes": _failure_class_counts(rows),
    }


def _bucketed(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row[key])].append(row)
    return {
        bucket: {
            "records": len(bucket_rows),
            "exact_candidate_covered": sum(
                1 for row in bucket_rows if row["exact_candidate_coverage"]
            ),
            "temporal_applicable_records": sum(
                1 for row in bucket_rows if row["temporal_applicable"]
            ),
            "temporal_slot_covered": sum(
                1 for row in bucket_rows if row["temporal_slot_coverage"] is True
            ),
            "gate_caveated_records": sum(
                1 for row in bucket_rows if row["gate_caveated"]
            ),
        }
        for bucket, bucket_rows in sorted(buckets.items())
    }


def _coverage(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    total = len(rows)
    covered = sum(1 for row in rows if row[key] is True)
    return {"covered": covered, "records": total, "rate": _rate(covered, total)}


def _failure_class(
    *,
    exact: bool,
    temporal_applicable: bool,
    slot_match: bool | None,
    purist: bool,
    pragmatic: bool,
    gate_match: bool,
) -> str:
    if exact:
        return "exact_temporal_candidate_present"
    if not gate_match:
        return "upstream_g13_gate_caveat"
    if temporal_applicable and slot_match is False:
        return "temporal_slot_miss"
    if purist or pragmatic:
        return "exact_surface_or_aggregation_miss"
    return "candidate_inventory_gap"


def _failure_class_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["g14_failure_class"]] += 1
    return dict(sorted(counts.items()))


def _decision(
    standard_rows: list[dict[str, Any]],
    temporal_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    temporal_summary = _summary(temporal_rows)
    exact = temporal_summary["exact_candidate_coverage"]
    slot = temporal_summary["temporal_slot_coverage"]
    return {
        "classification": "diagnostic_temporal_component_measured",
        "mechanism_status": "open",
        "headline": (
            f"Temporal challenge exact coverage is {exact['covered']}/"
            f"{exact['records']}; slot coverage is {slot['covered']}/"
            f"{slot['records']} on temporally applicable rows."
        ),
        "optimization_decision": (
            "Do not expand fragile arithmetic or broad relative-anchor guards "
            "from this pass. Preserve the current candidate builder as support, "
            "and route the remaining exact misses to aggregation-aware answer "
            "construction plus LLM target selection."
        ),
        "standard50_failure_classes": _failure_class_counts(standard_rows),
        "temporal_challenge_failure_classes": _failure_class_counts(temporal_rows),
    }


def render_g14_markdown(report: dict[str, Any]) -> str:
    standard = report["summary"]["standard50"]
    temporal = report["summary"]["temporal_challenge"]
    lines = [
        "# Gan S0 G14 Temporal Anchoring Report",
        "",
        "Date: 2026-05-29",
        "Status: current synthesis / no-model temporal anchoring evaluation",
        f"Kanban card: {report['kanban_card']}",
        f"Dataset/split: {report['dataset']} (`{report['split']}`)",
        f"Standard surface: `{report['surfaces']['standard50']}`",
        f"Temporal challenge set: `{report['surfaces']['temporal_challenge']}`",
        f"Candidate source: `{report['candidate_source']}`",
        "Fixed controls: no model calls; no scorer, loader, split, bridge, prompt, candidate-builder, target-selection, or prediction-repair changes.",
        "",
        "## Summary",
        "",
        _summary_sentence("Standard50", standard),
        _summary_sentence("Temporal challenge", temporal),
        "",
        "Gate-caveated view: rows where G13 already misclassified the source-level content state are carried as upstream caveats, not pure temporal-anchoring failures.",
        "",
        "## Failure Classes",
        "",
        "| Surface | Failure class | Records |",
        "| --- | --- | ---: |",
    ]
    for surface, summary in (
        ("standard50", standard),
        ("temporal_challenge", temporal),
    ):
        for klass, count in summary["failure_classes"].items():
            lines.append(f"| `{surface}` | `{klass}` | {count} |")
    lines.extend(
        [
            "",
            "## Temporal Challenge Rows",
            "",
            "| Record | Gold | Exact candidate | Slot match | Gate caveat | Failure class | Candidate labels |",
            "| --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    temporal_ids = set(G14_TEMPORAL_CHALLENGE_IDS)
    for row in report["rows"]:
        if row["record_id"] in temporal_ids:
            labels = "<br>".join(f"`{label}`" for label in row["candidate_labels"])
            lines.append(
                f"| `{row['record_id']}` | `{row['gold_label']}` | "
                f"{_yes_no(row['exact_candidate_coverage'])} | "
                f"{_yes_no(row['temporal_slot_coverage'])} | "
                f"{_yes_no(row['gate_caveated'])} | "
                f"`{row['g14_failure_class']}` | {labels} |"
            )
    decision = report["decision"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Classification: **{decision['classification']}**.",
            f"- Mechanism status: **{decision['mechanism_status']}**.",
            f"- {decision['headline']}",
            f"- Optimization decision: {decision['optimization_decision']}",
            "",
            "## Interpretation",
            "",
            "- The temporal challenge surface is mostly covered by the current deterministic substrate, but two exact misses remain as true temporal-slot misses; both still have category-equivalent candidates rather than clean exact answer options.",
            "- This supports G12's conclusion that exact closed answer-option construction needs temporal anchoring plus aggregation policy; it does not justify another broad prompt loop or a fragile arithmetic expansion.",
            "- G13 gate errors remain visible in row-level JSON so G15 target-selection work does not blame source-level content confusions on temporal anchoring.",
            "",
            "## Companion Artifact",
            "",
            "`docs/experiments/gan/gan_s0_g14_temporal_anchoring_report_20260529.json` contains standard50 rows, temporal challenge rows, candidate records, slot diagnostics, G13 caveats, and failure classes.",
            "",
        ]
    )
    return "\n".join(lines)


def _summary_sentence(label: str, summary: dict[str, Any]) -> str:
    exact = summary["exact_candidate_coverage"]
    slot = summary["temporal_slot_coverage"]
    gate_clean_slot = summary["gate_clean_temporal_slot_coverage"]
    return (
        f"{label}: exact candidate coverage is **{exact['covered']}/"
        f"{exact['records']}** ({_pct(exact['rate'])}); temporal-slot coverage is "
        f"**{slot['covered']}/{slot['records']}** ({_pct(slot['rate'])}) on "
        f"temporally applicable rows; gate-clean slot coverage is "
        f"**{gate_clean_slot['covered']}/{gate_clean_slot['records']}** "
        f"({_pct(gate_clean_slot['rate'])})."
    )


def _rate(count: int, total: int) -> float | None:
    return count / total if total else None


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1%}"


def _yes_no(value: bool | None) -> str:
    if value is None:
        return "n/a"
    return "yes" if value else "no"


__all__ = [
    "DEFAULT_G14_JSON_OUTPUT",
    "DEFAULT_G14_MARKDOWN_OUTPUT",
    "G14_STANDARD50_IDS",
    "G14_STANDARD50_NAME",
    "G14_TEMPORAL_CHALLENGE_IDS",
    "G14_TEMPORAL_CHALLENGE_NAME",
    "build_g14_temporal_anchoring_report",
    "render_g14_markdown",
    "write_g14_report_artifacts",
]
