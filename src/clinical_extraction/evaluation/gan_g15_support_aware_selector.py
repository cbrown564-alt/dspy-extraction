"""Post-hoc G15 report for the Gan S0 support-aware target selector."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from clinical_extraction.evaluation.gan_g2_model_arm_comparison import (
    build_gan_g2_model_arm_comparison_report,
)
from clinical_extraction.paths import resolve_run_directory
from clinical_extraction.schemas import PredictionSet

G15_ARM_ID = "g15_support_aware_selector"
STANDARD50_RECORD_IDS = [
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

CHALLENGE_SETS = {
    "target_selection": [
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
        "gan_8564",
        "gan_8264",
        "gan_11380",
        "gan_7818",
        "gan_13598",
        "gan_13595",
    ],
    "seizure_free_vs_quantified": [
        "gan_14485",
        "gan_10434",
        "gan_4956",
        "gan_13123",
        "gan_15306",
        "gan_7894",
        "gan_14881",
        "gan_9566",
        "gan_12679",
        "gan_15997",
        "gan_17287",
        "gan_16825",
        "gan_4011",
        "gan_804",
        "gan_13574",
        "gan_5974",
        "gan_8564",
        "gan_8264",
        "gan_7818",
        "gan_13598",
        "gan_13595",
    ],
    "unknown_no_reference": [
        "gan_6532",
        "gan_9566",
        "gan_5974",
        "gan_6607",
        "gan_6387",
        "gan_14002",
        "gan_11380",
        "gan_11408",
        "gan_11841",
        "gan_11874",
    ],
    "candidate_coverage": [
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
    ],
    "cluster": [
        "gan_6532",
        "gan_10434",
        "gan_4956",
        "gan_4702",
        "gan_10052",
        "gan_2609",
        "gan_3246",
        "gan_4113",
        "gan_4709",
        "gan_12679",
        "gan_1584",
        "gan_15997",
        "gan_16251",
        "gan_16825",
        "gan_10047",
        "gan_10398",
        "gan_714",
        "gan_804",
        "gan_22",
        "gan_13574",
        "gan_6607",
        "gan_11380",
        "gan_13598",
        "gan_13595",
    ],
    "temporal_anchoring": [
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
    ],
    "vague_frequency": [
        "gan_4956",
        "gan_4702",
        "gan_3246",
        "gan_4709",
        "gan_16251",
        "gan_10047",
        "gan_3867",
        "gan_6607",
        "gan_13598",
        "gan_13595",
    ],
}

DEFAULT_BASELINE_RUNS = {
    "builder_gap_gpt": Path(
        "archive/runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z"
    ),
    "d1_v1_2b_schema_guard": Path(
        "runs/gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z"
    ),
    "g8_special_class_selector": Path(
        "runs/gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50_20260528T233005Z"
    ),
    "g10_candidate_ranking_selector": Path(
        "runs/gan_s0_g10_candidate_ranking_target_selector_gpt4_1_mini_standard50_20260529T005458Z"
    ),
}

DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g15_support_aware_target_selector_report_20260529.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g15_support_aware_target_selector_report_20260529.md"
)


def build_gan_g15_support_aware_selector_report(
    *,
    g15_run_dir: Path,
    arm_run_dirs: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    """Build the G15 standard50 comparison and support-aware diagnostics."""

    arm_dirs = dict(arm_run_dirs or DEFAULT_BASELINE_RUNS)
    arm_dirs[G15_ARM_ID] = g15_run_dir
    report = build_gan_g2_model_arm_comparison_report(
        arm_run_dirs=arm_dirs,
        record_ids=STANDARD50_RECORD_IDS,
    )
    _relativize_arm_run_dirs(report)
    report.update(
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "status": "completed_standard50_mechanism_slice",
            "decision_scope": "arm",
            "kanban_card": (
                "G15 - Gan Target Selection and Semantic Adjudication"
            ),
            "comparison_group": (
                "gan_s0_g15_support_aware_target_selector_gpt4_standard50_v1"
            ),
            "g15_claim_scope": (
                "target-selection and semantic adjudication over fixed candidate "
                "support; no exact aggregation-constructor claim"
            ),
            "fixed_controls": [
                "gan_2026_fixed_v1:validation split and G6 standard50 record IDs",
                "gan2026_paper_reproduction primary scorer with repair/range/tolerance disabled",
                "gan_frequency_deterministic_v1 diagnostic scorer",
                "deterministic temporal candidate builder",
                "D1 deterministic date/event payload",
                "deterministic candidate label construction",
                "no verifier or prediction-repair behavior changes",
            ],
        }
    )
    report["challenge_overlays"] = _challenge_overlays(report)
    report["upstream_caveats"] = _upstream_caveats()
    report["g15_diagnostics"] = _g15_diagnostics(
        report=report,
        g15_run_dir=g15_run_dir,
    )
    report["pairwise_paper_monthly_deltas"] = _pairwise_deltas(report)
    report["decision"] = _decision(report)
    return report


def write_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_gan_g15_markdown(report), encoding="utf-8")


def render_gan_g15_markdown(report: dict[str, Any]) -> str:
    decision = report["decision"]
    diag = report["g15_diagnostics"]
    lines = [
        "# Gan S0 G15 Support-Aware Target Selector",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Scope",
        "",
        "- Status: `completed_standard50_mechanism_slice`",
        "- Decision scope: `arm`",
        "- Dataset/split: `gan_2026` / `gan_2026_fixed_v1:validation`",
        "- Surface: `gan_s0_g6_standard50_v1` (50 records)",
        "- Model/provider: GPT-4.1-mini / OpenAI",
        "- Program variant: `gan_frequency_s0_support_aware_target_selector`",
        "- Prompt version: `gan_frequency_s0_support_aware_target_selector_v1_0`",
        "- Primary scorer: `gan2026_paper_reproduction`; canonical `gan_frequency_deterministic_v1` is diagnostic.",
        "- Claim scope: target-selection/semantic adjudication only; no exact aggregation-constructor claim.",
        "",
        "## Decision",
        "",
        f"- Recommendation: `{decision['recommendation']}`",
        f"- Stop rule: `{decision['stop_rule_result']}`",
        f"- Rationale: {decision['rationale']}",
        "",
        "## Arm Summary",
        "",
        "| Arm | Run ID | Paper monthly | Paper purist | Paper pragmatic | Canonical monthly | Canonical pragmatic |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm in report["arms"]:
        summary = report["summary"]["arms"][arm["arm_id"]]
        paper = summary["paper_reproduction"]
        canonical = summary["canonical"]
        lines.append(
            "| "
            f"`{arm['arm_id']}` | "
            f"`{arm['run_id']}` | "
            f"{_pct(paper['monthly_frequency_accuracy'])} | "
            f"{_pct(paper['purist_category_accuracy'])} | "
            f"{_pct(paper['pragmatic_category_accuracy'])} | "
            f"{_pct(canonical['monthly_frequency_accuracy'])} | "
            f"{_pct(canonical['pragmatic_category_accuracy'])} |"
        )
    lines.extend(
        [
            "",
            "## G15 Trace Diagnostics",
            "",
            f"- Support context present: {diag['support_context_present']['count']}/"
            f"{diag['support_context_present']['denominator']}",
            f"- Selected candidate references present: "
            f"{diag['selected_candidate_references_present']['count']}/"
            f"{diag['selected_candidate_references_present']['denominator']}",
            f"- Label-construction inputs present: "
            f"{diag['label_construction_inputs_present']['count']}/"
            f"{diag['label_construction_inputs_present']['denominator']}",
            "",
            "| Target semantic class | Count |",
            "| --- | ---: |",
        ]
    )
    for key, count in sorted(diag["target_semantic_class_counts"].items()):
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "| Support policy decision | Count |",
            "| --- | ---: |",
        ]
    )
    for key, count in sorted(diag["support_policy_decision_counts"].items()):
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "## Challenge Overlays",
            "",
            "| Overlay | G15 paper monthly | Builder-gap GPT | D1 v1.2b | G8 | G10 |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, overlay in report["challenge_overlays"].items():
        lines.append(
            "| "
            f"`{name}` | "
            f"{_count_pct(overlay[G15_ARM_ID]['paper_monthly'])} | "
            f"{_count_pct(overlay['builder_gap_gpt']['paper_monthly'])} | "
            f"{_count_pct(overlay['d1_v1_2b_schema_guard']['paper_monthly'])} | "
            f"{_count_pct(overlay['g8_special_class_selector']['paper_monthly'])} | "
            f"{_count_pct(overlay['g10_candidate_ranking_selector']['paper_monthly'])} |"
        )
    lines.extend(
        [
            "",
            "## Pairwise Paper-Monthly Deltas",
            "",
            "| Baseline | G15 correct / baseline wrong | G15 wrong / baseline correct |",
            "| --- | --- | --- |",
        ]
    )
    for baseline_id, deltas in report["pairwise_paper_monthly_deltas"].items():
        lines.append(
            "| "
            f"`{baseline_id}` | "
            f"{_inline_code_list(deltas['g15_correct_baseline_wrong'])} | "
            f"{_inline_code_list(deltas['g15_wrong_baseline_correct'])} |"
        )
    lines.extend(
        [
            "",
            "## Upstream Caveats",
            "",
            f"- G13 gate-caveated standard50 rows: "
            f"{_inline_code_list(report['upstream_caveats']['g13_gate_caveated_record_ids'])}.",
            f"- G14 temporal-slot misses on standard50: "
            f"{_inline_code_list(report['upstream_caveats']['g14_temporal_slot_miss_record_ids'])}.",
            "",
            "## Interpretation",
            "",
            "- G15 tests whether explicit support metadata improves target semantics over the fixed candidate surface.",
            "- The run preserves scorer, loader, split, benchmark bridge, candidate-builder, label-construction, and prediction-repair semantics.",
            "- G13 gate confusions and G14 temporal-slot misses are carried as upstream caveats rather than pure selector failures.",
            "",
        ]
    )
    return "\n".join(lines)


def _load_prediction_set(run_dir: Path) -> PredictionSet:
    resolved = resolve_run_directory(run_dir, include_archive=True)
    return PredictionSet.model_validate_json(
        (resolved / "predictions.json").read_text(encoding="utf-8")
    )


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _relativize_arm_run_dirs(report: dict[str, Any]) -> None:
    repo_root = Path.cwd().resolve()
    for arm in report.get("arms", []):
        run_dir = arm.get("run_dir")
        if not isinstance(run_dir, str):
            continue
        try:
            arm["run_dir"] = str(Path(run_dir).resolve().relative_to(repo_root))
        except ValueError:
            continue


def _challenge_overlays(report: dict[str, Any]) -> dict[str, Any]:
    overlays: dict[str, Any] = {}
    row_by_id = {row["record_id"]: row for row in report["rows"]}
    for name, record_ids in CHALLENGE_SETS.items():
        rows = [row_by_id[record_id] for record_id in record_ids if record_id in row_by_id]
        overlays[name] = {
            arm["arm_id"]: {
                "paper_monthly": _metric_count(rows, arm["arm_id"], "paper_reproduction", "monthly_frequency_match"),
                "paper_pragmatic": _metric_count(rows, arm["arm_id"], "paper_reproduction", "pragmatic_category_match"),
                "canonical_monthly": _metric_count(rows, arm["arm_id"], "canonical", "monthly_frequency_match"),
            }
            for arm in report["arms"]
        }
    return overlays


def _metric_count(
    rows: list[dict[str, Any]],
    arm_id: str,
    scorer_key: str,
    metric_key: str,
) -> dict[str, Any]:
    values = [
        bool(row["arms"][arm_id]["scores"][scorer_key][metric_key])
        for row in rows
    ]
    correct = sum(values)
    records = len(values)
    return {
        "correct": correct,
        "records": records,
        "accuracy": correct / records if records else 0.0,
    }


def _upstream_caveats() -> dict[str, Any]:
    g13_path = Path(
        "docs/experiments/gan/gan_s0_g13_frequency_content_gate_report_20260529.json"
    )
    g14_path = Path(
        "docs/experiments/gan/gan_s0_g14_temporal_anchoring_report_20260529.json"
    )
    g13_rows = {
        row["record_id"]: row
        for row in _load_json(g13_path).get("rows", [])
    }
    g14_rows = {
        row["record_id"]: row
        for row in _load_json(g14_path).get("rows", [])
    }
    return {
        "g13_gate_caveated_record_ids": [
            record_id
            for record_id in STANDARD50_RECORD_IDS
            if not bool(g13_rows.get(record_id, {}).get("gate_class_match", True))
        ],
        "g14_temporal_slot_miss_record_ids": [
            record_id
            for record_id in STANDARD50_RECORD_IDS
            if g14_rows.get(record_id, {}).get("g14_failure_class")
            == "temporal_slot_miss"
        ],
    }


def _g15_diagnostics(
    *,
    report: dict[str, Any],
    g15_run_dir: Path,
) -> dict[str, Any]:
    prediction_set = _load_prediction_set(g15_run_dir)
    predictions_by_id = {
        prediction.document_id: prediction
        for prediction in prediction_set.predictions
    }
    target_class_counts: Counter[str] = Counter()
    support_decision_counts: Counter[str] = Counter()
    conflict_resolution_counts: Counter[str] = Counter()
    reason_code_counts: Counter[str] = Counter()
    conflict_flag_counts: Counter[str] = Counter()
    support_context_present = 0
    selected_candidate_references_present = 0
    label_construction_inputs_present = 0
    failure_records: list[dict[str, Any]] = []
    caveats = report["upstream_caveats"]

    for row in report["rows"]:
        prediction = predictions_by_id[row["record_id"]]
        metadata = prediction.metadata
        adjudication = _dict_value(metadata.get("reason_code_adjudication"))
        support_context = _dict_value(metadata.get("candidate_support_context"))
        support_context_present += int(bool(support_context))
        selected_candidate_references_present += int(
            bool(metadata.get("selected_candidate_reference"))
        )
        label_construction_inputs_present += int(
            bool(metadata.get("label_construction_inputs"))
        )
        target_class_counts[
            str(
                metadata.get("target_semantic_class")
                or adjudication.get("target_semantic_class")
                or "missing"
            )
        ] += 1
        support_decision_counts[
            str(adjudication.get("support_policy_decision") or "missing")
        ] += 1
        conflict_resolution_counts[
            str(adjudication.get("competing_signal_resolution") or "none")
        ] += 1
        reason_code_counts[
            str(
                metadata.get("target_selection_reason_code")
                or adjudication.get("reason_code")
                or "missing"
            )
        ] += 1
        flags = _dict_value(support_context.get("conflict_flags"))
        for key, value in flags.items():
            if value is True:
                conflict_flag_counts[key] += 1

        g15_row = row["arms"][G15_ARM_ID]
        if not g15_row["scores"]["paper_reproduction"]["monthly_frequency_match"]:
            failure_records.append(
                {
                    "record_id": row["record_id"],
                    "gold_label": row["gold_label"],
                    "predicted_label": g15_row["predicted_label"],
                    "target_semantic_class": metadata.get("target_semantic_class"),
                    "reason_code": metadata.get("target_selection_reason_code"),
                    "error_class": metadata.get("target_selection_error_class"),
                    "g13_gate_caveat": row["record_id"]
                    in caveats["g13_gate_caveated_record_ids"],
                    "g14_temporal_slot_miss": row["record_id"]
                    in caveats["g14_temporal_slot_miss_record_ids"],
                }
            )

    denominator = len(report["rows"])
    return {
        "support_context_present": {
            "count": support_context_present,
            "denominator": denominator,
        },
        "selected_candidate_references_present": {
            "count": selected_candidate_references_present,
            "denominator": denominator,
        },
        "label_construction_inputs_present": {
            "count": label_construction_inputs_present,
            "denominator": denominator,
        },
        "target_semantic_class_counts": dict(target_class_counts),
        "support_policy_decision_counts": dict(support_decision_counts),
        "competing_signal_resolution_counts": dict(conflict_resolution_counts),
        "reason_code_counts": dict(reason_code_counts),
        "support_conflict_flag_counts": dict(conflict_flag_counts),
        "failure_records": failure_records,
    }


def _pairwise_deltas(report: dict[str, Any]) -> dict[str, dict[str, list[str]]]:
    deltas: dict[str, dict[str, list[str]]] = {}
    baseline_ids = [arm["arm_id"] for arm in report["arms"] if arm["arm_id"] != G15_ARM_ID]
    for baseline_id in baseline_ids:
        g15_correct_baseline_wrong: list[str] = []
        g15_wrong_baseline_correct: list[str] = []
        for row in report["rows"]:
            g15_match = bool(
                row["arms"][G15_ARM_ID]["scores"]["paper_reproduction"][
                    "monthly_frequency_match"
                ]
            )
            baseline_match = bool(
                row["arms"][baseline_id]["scores"]["paper_reproduction"][
                    "monthly_frequency_match"
                ]
            )
            if g15_match and not baseline_match:
                g15_correct_baseline_wrong.append(row["record_id"])
            elif not g15_match and baseline_match:
                g15_wrong_baseline_correct.append(row["record_id"])
        deltas[baseline_id] = {
            "g15_correct_baseline_wrong": g15_correct_baseline_wrong,
            "g15_wrong_baseline_correct": g15_wrong_baseline_correct,
        }
    return deltas


def _decision(report: dict[str, Any]) -> dict[str, Any]:
    summaries = report["summary"]["arms"]
    g15 = summaries[G15_ARM_ID]["paper_reproduction"]
    g15_correct = _correct_count(g15["monthly_frequency_accuracy"], g15["denominator"])
    baseline_counts = {
        arm_id: _correct_count(
            summary["paper_reproduction"]["monthly_frequency_accuracy"],
            summary["paper_reproduction"]["denominator"],
        )
        for arm_id, summary in summaries.items()
        if arm_id != G15_ARM_ID
    }
    best_baseline_id, best_baseline_correct = max(
        baseline_counts.items(), key=lambda item: item[1]
    )
    motivated_overlays = (
        "target_selection",
        "seizure_free_vs_quantified",
        "unknown_no_reference",
    )
    overlay_regressions = []
    for overlay_name in motivated_overlays:
        overlay = report["challenge_overlays"][overlay_name]
        g15_overlay = overlay[G15_ARM_ID]["paper_monthly"]["correct"]
        best_overlay = max(
            metrics["paper_monthly"]["correct"]
            for arm_id, metrics in overlay.items()
            if arm_id != G15_ARM_ID
        )
        if g15_overlay < best_overlay:
            overlay_regressions.append(overlay_name)

    if g15_correct >= best_baseline_correct + 2 and not overlay_regressions:
        recommendation = "eligible_for_full_validation_gate"
        stop_rule = "passed"
        rationale = (
            f"G15 reached {g15_correct}/50 paper monthly, at least two records "
            f"above {best_baseline_id} ({best_baseline_correct}/50), with no "
            "motivating-overlay regression."
        )
    else:
        recommendation = "do_not_full_validate_or_promote_as_tested"
        stop_rule = "failed"
        rationale = (
            f"G15 reached {g15_correct}/50 paper monthly versus best baseline "
            f"{best_baseline_id} at {best_baseline_correct}/50. "
            "The G6 stop rule requires at least a two-record lift and no "
            f"motivating-overlay regression; regressions: "
            f"{', '.join(overlay_regressions) if overlay_regressions else 'none'}."
        )
    return {
        "recommendation": recommendation,
        "decision_scope": "arm",
        "stop_rule_result": stop_rule,
        "rationale": rationale,
        "g15_paper_monthly_correct": g15_correct,
        "best_baseline_id": best_baseline_id,
        "best_baseline_paper_monthly_correct": best_baseline_correct,
        "motivating_overlay_regressions": overlay_regressions,
    }


def _dict_value(value: object) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _correct_count(accuracy: float, denominator: int) -> int:
    return int(round(accuracy * denominator))


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _count_pct(metric: Mapping[str, Any]) -> str:
    return f"{metric['correct']}/{metric['records']} ({_pct(metric['accuracy'])})"


def _inline_code_list(values: list[str]) -> str:
    if not values:
        return ""
    return ", ".join(f"`{value}`" for value in values)
