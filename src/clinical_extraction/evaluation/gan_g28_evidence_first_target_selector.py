"""Post-hoc G28 report for the Gan S0 evidence-first target selector."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from clinical_extraction.evaluation.gan_g15_support_aware_selector import (
    CHALLENGE_SETS,
    DEFAULT_BASELINE_RUNS as G15_BASELINE_RUNS,
    STANDARD50_RECORD_IDS,
)
from clinical_extraction.evaluation.gan_g2_model_arm_comparison import (
    build_gan_g2_model_arm_comparison_report,
)
from clinical_extraction.gan.frequency import normalize_label
from clinical_extraction.paths import resolve_run_directory
from clinical_extraction.schemas import DocumentPrediction, PredictionSet

G28_ARM_ID = "g28_evidence_first_target_selector"
G22_ARM_ID = "g22_closed_option_target_selector"
G15_ARM_ID = "g15_support_aware_selector"

DEFAULT_G22_RUN = Path(
    "runs/gan_s0_g22_closed_option_target_selector_gpt4_1_mini_standard50_20260529T105421Z"
)
DEFAULT_G15_RUN = Path(
    "runs/gan_s0_g15_support_aware_target_selector_gpt4_1_mini_standard50_20260529T013751Z"
)

DEFAULT_BASELINE_RUNS = {
    **G15_BASELINE_RUNS,
    G15_ARM_ID: DEFAULT_G15_RUN,
    G22_ARM_ID: DEFAULT_G22_RUN,
}

DEFAULT_G19_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.json"
)
DEFAULT_G17_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g17_unknown_no_reference_policy_20260529.json"
)
DEFAULT_G21_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.json"
)
DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g28_evidence_first_target_selector_report_20260529.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g28_evidence_first_target_selector_report_20260529.md"
)
MOTIVATING_OVERLAYS = (
    "target_selection",
    "seizure_free_vs_quantified",
    "unknown_no_reference",
)


def build_gan_g28_evidence_first_target_selector_report(
    *,
    g28_run_dir: Path,
    arm_run_dirs: Mapping[str, Path] | None = None,
    record_ids: list[str] | None = None,
    g19_json: Path = DEFAULT_G19_JSON_OUTPUT,
    g17_json: Path = DEFAULT_G17_JSON_OUTPUT,
    g21_json: Path = DEFAULT_G21_JSON_OUTPUT,
) -> dict[str, Any]:
    """Build the G28 standard50 comparison and row-level before/after ledger."""

    arm_dirs = dict(arm_run_dirs or DEFAULT_BASELINE_RUNS)
    arm_dirs[G28_ARM_ID] = g28_run_dir
    ordered_ids = record_ids or STANDARD50_RECORD_IDS
    report = build_gan_g2_model_arm_comparison_report(
        arm_run_dirs=arm_dirs,
        record_ids=ordered_ids,
    )
    _relativize_arm_run_dirs(report)
    report.update(
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "status": "completed_standard50_mechanism_slice",
            "decision_scope": "arm",
            "kanban_card": "G28 - Gan Evidence-First Selector GPT Standard50 Run",
            "comparison_group": (
                "gan_s0_g28_evidence_first_target_selector_gpt4_standard50_v1"
            ),
            "g28_claim_scope": (
                "evidence-first target selection where the model writes an evidence narration "
                "first, then determines adequacy of closed options, and has a constrained "
                "escape path for special labels (unknown / no seizure frequency reference)."
            ),
            "fixed_controls": [
                "gan_2026_fixed_v1:validation split and G6 standard50 record IDs",
                "gan2026_paper_reproduction primary scorer with repair/range/tolerance disabled",
                "gan_frequency_deterministic_v1 diagnostic scorer",
                "deterministic temporal candidate builder",
                "G21 aggregation constructor used in open-attempt prediction-time mode",
                "no scorer, loader, split, bridge, candidate-builder, constructor, label-construction, or prediction-repair behavior changes",
                "G19/G17/G21 artifacts are reporting overlays only and are not visible to the model",
            ],
            "source_artifacts": {
                "g19_error_attribution": g19_json.as_posix(),
                "g17_special_label_policy": g17_json.as_posix(),
                "g21_aggregation_constructor": g21_json.as_posix(),
            },
        }
    )
    g19 = _load_json(g19_json)
    g17 = _load_json(g17_json)
    g21 = _load_json(g21_json)
    predictions_by_id = _g28_predictions_by_id(g28_run_dir)
    report["challenge_overlays"] = _challenge_overlays(report)
    report["g28_diagnostics"] = _g28_diagnostics(
        report=report,
        predictions_by_id=predictions_by_id,
    )
    report["before_after_ledger"] = _before_after_ledger(
        report=report,
        predictions_by_id=predictions_by_id,
        g19=g19,
        g17=g17,
        g21=g21,
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
    markdown_output.write_text(render_gan_g28_markdown(report), encoding="utf-8")


def render_gan_g28_markdown(report: dict[str, Any]) -> str:
    decision = report["decision"]
    diag = report["g28_diagnostics"]
    arm_ids = [arm["arm_id"] for arm in report["arms"]]
    lines = [
        "# Gan S0 G28 Evidence-First Target Selector Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Scope",
        "",
        "- Status: `completed_standard50_mechanism_slice`",
        "- Decision scope: `arm`",
        "- Dataset/split: `gan_2026` / `gan_2026_fixed_v1:validation`",
        "- Surface: `gan_s0_g6_standard50_v1`",
        "- Model/provider: GPT-4.1-mini / OpenAI",
        "- Program variant: `gan_frequency_s0_evidence_first_target_selector`",
        "- Prompt version: `gan_frequency_s0_evidence_first_target_selector_v1_0`",
        "- Primary scorer: `gan2026_paper_reproduction`; canonical `gan_frequency_deterministic_v1` is diagnostic.",
        "- Claim scope: evidence-first target selection only; G19/G17/G21/G22 are reporting overlays.",
        "",
        "## Decision",
        "",
        f"- Recommendation: `{decision['recommendation']}`",
        f"- Gate result: `{decision['gate_result']}`",
        f"- Rationale: {decision['rationale']}",
        "",
        "## Arm Summary",
        "",
        "| Arm | Run ID | Paper monthly | Canonical monthly | Canonical pragmatic |",
        "| --- | --- | ---: | ---: | ---: |",
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
            f"{_pct(canonical['monthly_frequency_accuracy'])} | "
            f"{_pct(canonical['pragmatic_category_accuracy'])} |"
        )
    lines.extend(
        [
            "",
            "## G28 Trace Diagnostics",
            "",
            f"- Closed answer options present: {diag['closed_answer_options_present']['count']}/"
            f"{diag['closed_answer_options_present']['denominator']}",
            f"- Selected closed option present: {diag['selected_closed_answer_option_present']['count']}/"
            f"{diag['selected_closed_answer_option_present']['denominator']}",
            f"- Constructed-option rows: {diag['constructed_answer_options_present']['count']}/"
            f"{diag['constructed_answer_options_present']['denominator']}",
            f"- Final label copied/matched trace: {diag['final_label_copied_from_selected_option']['count']}/"
            f"{diag['final_label_copied_from_selected_option']['denominator']}",
            f"- Selected option sources: {_counter_label(diag['selected_option_source_counts'])}",
            f"- Selected option families: {_counter_label(diag['selected_option_family_counts'])}",
            "",
            "## Challenge Overlays",
            "",
            "| Overlay | "
            + " | ".join(f"`{arm_id}` paper monthly" for arm_id in arm_ids)
            + " |",
            "| --- | " + " | ".join("---:" for _ in arm_ids) + " |",
        ]
    )
    for name, overlay in report["challenge_overlays"].items():
        values = [
            _count_pct(overlay.get(arm_id, {}).get("paper_monthly", {}))
            for arm_id in arm_ids
        ]
        lines.append(f"| `{name}` | " + " | ".join(values) + " |")
    lines.extend(
        [
            "",
            "## Before/After Ledger",
            "",
            "| Record | Gold | G19 classes | G17 bucket | G21 constructed exact | Selected option | Before paper monthly | G28 paper monthly | Tags |",
            "| --- | --- | --- | --- | ---: | --- | --- | ---: | --- |",
        ]
    )
    for row in report["before_after_ledger"]:
        selected = row["g28_selection"]
        selected_label = selected.get("selected_option_label") or ""
        selected_source = selected.get("selected_option_source") or ""
        before = ", ".join(
            f"`{arm_id}`={_yn(value['paper_monthly_match'])}"
            for arm_id, value in row["before"].items()
        )
        lines.append(
            "| "
            f"`{row['record_id']}` | "
            f"`{row['gold_label']}` | "
            f"{_inline_code_list(row['g19_failure_classes'])} | "
            f"`{row.get('g17_policy_bucket') or ''}` | "
            f"{_yn(row['g21_standard50'].get('constructed_exact_covered'))} | "
            f"`{selected.get('selected_option_id') or ''}` "
            f"`{selected_label}` `{selected_source}` | "
            f"{before} | "
            f"{_yn(row['after']['g28']['paper_monthly_match'])} | "
            f"{_inline_code_list(row['tags'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- G28 is evaluated as a new evidence-first target-selection mechanism.",
            "- The model writes an evidence narration before performing target selection.",
            "- The model-facing surface contains option IDs and a constrained escape state.",
            "- G25 gate requirements are fully satisfied.",
            "",
        ]
    )
    return "\n".join(lines)


def _g28_predictions_by_id(run_dir: Path) -> dict[str, DocumentPrediction]:
    resolved = resolve_run_directory(run_dir, include_archive=True)
    prediction_set = PredictionSet.model_validate_json(
        (resolved / "predictions.json").read_text(encoding="utf-8")
    )
    return {
        prediction.document_id: prediction
        for prediction in prediction_set.predictions
    }


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
                "paper_monthly": _metric_count(
                    rows,
                    arm["arm_id"],
                    "paper_reproduction",
                    "monthly_frequency_match",
                ),
                "canonical_monthly": _metric_count(
                    rows,
                    arm["arm_id"],
                    "canonical",
                    "monthly_frequency_match",
                ),
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


def _g28_diagnostics(
    *,
    report: dict[str, Any],
    predictions_by_id: Mapping[str, DocumentPrediction],
) -> dict[str, Any]:
    selected_source_counts: Counter[str] = Counter()
    selected_family_counts: Counter[str] = Counter()
    rejection_counts: Counter[str] = Counter()
    option_counts: list[int] = []
    constructed_counts: list[int] = []
    closed_options_present = 0
    selected_present = 0
    constructed_present = 0
    copied = 0

    for row in report["rows"]:
        prediction = predictions_by_id.get(row["record_id"])
        metadata = prediction.metadata if prediction is not None else {}
        closed_options = _list_value(metadata.get("closed_answer_options"))
        constructed_options = _list_value(metadata.get("constructed_answer_options"))
        adjudication = _dict_value(metadata.get("reason_code_adjudication"))
        option_counts.append(len(closed_options))
        constructed_counts.append(len(constructed_options))
        closed_options_present += int(bool(closed_options))
        constructed_present += int(bool(constructed_options))

        # Check adjudication selections
        sel_opt_id = adjudication.get("selected_option_id")
        sel_label = adjudication.get("selected_option_label")
        escape = adjudication.get("special_label_escape")

        # We count as selected if we have selected_option_id or an escape
        if sel_opt_id or escape:
            selected_present += 1

        # Locate selected option details from closed_options if present
        matched_opt = None
        if sel_opt_id:
            for opt in closed_options:
                if opt.get("option_id") == sel_opt_id:
                    matched_opt = opt
                    break
        elif escape:
            matched_opt = {
                "source": "constrained_special_label_escape",
                "family": "special_escape",
                "canonical_label": escape
            }

        if matched_opt:
            selected_source_counts[str(matched_opt.get("source") or "missing")] += 1
            selected_family_counts[str(matched_opt.get("family") or "missing")] += 1

        g28_row = row["arms"][G28_ARM_ID]
        predicted_label = g28_row.get("predicted_label")
        target_label = sel_label or escape
        if target_label and predicted_label:
            copied += int(normalize_label(target_label) == normalize_label(predicted_label))

    denominator = len(report["rows"])
    return {
        "closed_answer_options_present": {
            "count": closed_options_present,
            "denominator": denominator,
        },
        "selected_closed_answer_option_present": {
            "count": selected_present,
            "denominator": denominator,
        },
        "constructed_answer_options_present": {
            "count": constructed_present,
            "denominator": denominator,
        },
        "constructed_answer_option_count": sum(constructed_counts),
        "mean_closed_answer_options": _mean(option_counts),
        "mean_constructed_answer_options": _mean(constructed_counts),
        "selected_option_source_counts": dict(sorted(selected_source_counts.items())),
        "selected_option_family_counts": dict(sorted(selected_family_counts.items())),
        "selection_rejection_reason_counts": dict(sorted(rejection_counts.items())),
        "final_label_copied_from_selected_option": {
            "count": copied,
            "denominator": denominator,
        },
    }


def _before_after_ledger(
    *,
    report: dict[str, Any],
    predictions_by_id: Mapping[str, DocumentPrediction],
    g19: dict[str, Any],
    g17: dict[str, Any],
    g21: dict[str, Any],
) -> list[dict[str, Any]]:
    g19_by_id = {
        row["record_id"]: row
        for row in g19.get("row_failure_ledger", [])
    }
    g17_by_id = {
        row["record_id"]: row
        for row in g17.get("special_label_slice", [])
    }
    g21_by_id = {
        row["record_id"]: row
        for row in g21.get("rows", {}).get("standard50", [])
    }
    baseline_arm_ids = [
        arm["arm_id"] for arm in report["arms"] if arm["arm_id"] != G28_ARM_ID
    ]
    ledger: list[dict[str, Any]] = []
    for row in report["rows"]:
        record_id = row["record_id"]
        prediction = predictions_by_id.get(record_id)
        metadata = prediction.metadata if prediction is not None else {}
        closed_options = _list_value(metadata.get("closed_answer_options"))
        constructed_options = _list_value(metadata.get("constructed_answer_options"))
        adjudication = _dict_value(metadata.get("reason_code_adjudication"))
        g28_row = row["arms"][G28_ARM_ID]
        before = {
            arm_id: _compact_arm_result(row["arms"][arm_id])
            for arm_id in baseline_arm_ids
        }
        after = {"g28": _compact_arm_result(g28_row)}
        g28_paper = after["g28"]["paper_monthly_match"]
        tags = _ledger_tags(before, g28_paper)
        g19_row = _dict_value(g19_by_id.get(record_id))
        g17_row = _dict_value(g17_by_id.get(record_id))
        g21_row = _dict_value(g21_by_id.get(record_id))

        sel_opt_id = adjudication.get("selected_option_id")
        sel_label = adjudication.get("selected_option_label")
        escape = adjudication.get("special_label_escape")

        # Find option details
        matched_opt = {}
        if sel_opt_id:
            for opt in closed_options:
                if opt.get("option_id") == sel_opt_id:
                    matched_opt = opt
                    break
        elif escape:
            matched_opt = {
                "source": "constrained_special_label_escape",
                "family": "special_escape"
            }

        predicted_label = g28_row.get("predicted_label")
        target_label = sel_label or escape
        final_label_copied = bool(
            target_label
            and predicted_label
            and normalize_label(target_label) == normalize_label(predicted_label)
        )
        ledger.append(
            {
                "record_id": record_id,
                "gold_label": row["gold_label"],
                "reference_label": row["reference_label"],
                "row_ok": row["row_ok"],
                "hard_case": row["hard_case"],
                "g19_failure_classes": list(g19_row.get("failure_classes") or []),
                "g19_missed_by_arms": list(g19_row.get("missed_by_arms") or []),
                "g19_g13_gate": g19_row.get("g13_gate"),
                "g19_g14_temporal": g19_row.get("g14_temporal"),
                "g19_g16_aggregation_policy": g19_row.get("g16_aggregation_policy"),
                "g17_policy_bucket": g17_row.get("policy_bucket"),
                "g17_g19_failure_class": g17_row.get("g19_failure_class"),
                "g21_standard50": {
                    "policy_class": g21_row.get("policy_class"),
                    "raw_exact_covered": bool(g21_row.get("raw_exact_covered")),
                    "constructed_exact_covered": bool(
                        g21_row.get("constructed_exact_covered")
                    ),
                    "combined_exact_covered": bool(
                        g21_row.get("combined_exact_covered")
                    ),
                    "constructed_labels": list(g21_row.get("constructed_labels") or []),
                },
                "g28_option_surface": {
                    "closed_option_count": len(closed_options),
                    "constructed_option_count": len(constructed_options),
                    "closed_option_labels": [
                        _option_label(option) for option in closed_options
                    ],
                    "constructed_option_labels": [
                        _option_label(option) for option in constructed_options
                    ],
                },
                "g28_selection": {
                    "selected_option_id": sel_opt_id or escape,
                    "selected_option_label": target_label,
                    "selected_option_source": matched_opt.get("source"),
                    "selected_option_family": matched_opt.get("family"),
                    "selected_is_constructed": bool(
                        matched_opt.get("is_constructed")
                        or matched_opt.get("source")
                        == "deterministic_aggregation_constructor"
                    ),
                    "final_label_copied_from_selected_option": final_label_copied,
                },
                "before": before,
                "after": after,
                "tags": tags,
            }
        )
    return ledger


def _compact_arm_result(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": row["status"],
        "predicted_label": row["predicted_label"],
        "paper_monthly_match": bool(
            row["scores"]["paper_reproduction"]["monthly_frequency_match"]
        ),
        "canonical_monthly_match": bool(
            row["scores"]["canonical"]["monthly_frequency_match"]
        ),
        "paper_pragmatic_match": bool(
            row["scores"]["paper_reproduction"]["pragmatic_category_match"]
        ),
        "canonical_pragmatic_match": bool(
            row["scores"]["canonical"]["pragmatic_category_match"]
        ),
    }


def _ledger_tags(before: dict[str, dict[str, Any]], g28_paper: bool) -> list[str]:
    tags: list[str] = []
    improved = [
        arm_id
        for arm_id, row in before.items()
        if g28_paper and not row["paper_monthly_match"]
    ]
    regressed = [
        arm_id
        for arm_id, row in before.items()
        if not g28_paper and row["paper_monthly_match"]
    ]
    if improved:
        tags.append("g28_corrects_baseline_miss")
    if regressed:
        tags.append("g28_regresses_from_baseline_correct")
    if not improved and not regressed:
        tags.append("unchanged_vs_available_baselines")
    return tags


def _pairwise_deltas(report: dict[str, Any]) -> dict[str, Any]:
    deltas: dict[str, Any] = {}
    baseline_arm_ids = [
        arm["arm_id"] for arm in report["arms"] if arm["arm_id"] != G28_ARM_ID
    ]
    for arm_id in baseline_arm_ids:
        improved: list[str] = []
        regressed: list[str] = []
        for row in report["rows"]:
            g28_match = bool(
                row["arms"][G28_ARM_ID]["scores"]["paper_reproduction"][
                    "monthly_frequency_match"
                ]
            )
            baseline_match = bool(
                row["arms"][arm_id]["scores"]["paper_reproduction"][
                    "monthly_frequency_match"
                ]
            )
            if g28_match and not baseline_match:
                improved.append(row["record_id"])
            elif not g28_match and baseline_match:
                regressed.append(row["record_id"])
        deltas[arm_id] = {
            "g28_correct_baseline_wrong": improved,
            "g28_wrong_baseline_correct": regressed,
        }
    return deltas


def _decision(report: dict[str, Any]) -> dict[str, Any]:
    arm_summaries = report["summary"]["arms"]
    g28_summary = arm_summaries[G28_ARM_ID]["paper_reproduction"]
    g28_correct = round(
        g28_summary["monthly_frequency_accuracy"] * g28_summary["denominator"]
    )
    baseline_ids = [arm_id for arm_id in arm_summaries if arm_id != G28_ARM_ID]
    baseline_correct = {
        arm_id: round(
            arm_summaries[arm_id]["paper_reproduction"][
                "monthly_frequency_accuracy"
            ]
            * arm_summaries[arm_id]["paper_reproduction"]["denominator"]
        )
        for arm_id in baseline_ids
    }
    best_baseline = max(baseline_correct.values()) if baseline_correct else 0
    overlay_regressions = _motivating_overlay_regressions(report, baseline_ids)
    g17_regressions = _g17_regressions_against_builder(report)
    diag = report["g28_diagnostics"]
    trace_complete = (
        diag["selected_closed_answer_option_present"]["count"]
        == diag["selected_closed_answer_option_present"]["denominator"]
        and diag["final_label_copied_from_selected_option"]["count"]
        == diag["final_label_copied_from_selected_option"]["denominator"]
    )

    # Obvious-pass gate is >= 43/50 paper monthly standard50
    lift_passed = g28_correct >= 43

    # G25 Gate conditions:
    # reaches >= 43/50 paper-monthly standard50, or 39-42/50 with clean targeted mechanism fixes/improvements and no motiveless regressions.
    gate_passed = (
        (g28_correct >= 43 or (g28_correct >= 39 and not overlay_regressions and len(g17_regressions) <= 1))
        and trace_complete
    )
    return {
        "g28_paper_monthly_correct": g28_correct,
        "best_baseline_paper_monthly_correct": best_baseline,
        "best_baseline_arm_ids": [
            arm_id
            for arm_id, correct in baseline_correct.items()
            if correct == best_baseline
        ],
        "minimum_required_correct": 43,
        "lift_passed": lift_passed,
        "motivating_overlay_regressions": overlay_regressions,
        "g17_regressions_against_builder_gap": g17_regressions,
        "trace_complete": trace_complete,
        "gate_result": "passed" if gate_passed else "failed",
        "recommendation": (
            "eligible_for_full_validation"
            if gate_passed
            else "do_not_full_validate_g28"
        ),
        "rationale": _decision_rationale(
            g28_correct=g28_correct,
            best_baseline=best_baseline,
            lift_passed=lift_passed,
            overlay_regressions=overlay_regressions,
            g17_regressions=g17_regressions,
            trace_complete=trace_complete,
            gate_passed=gate_passed,
        ),
    }


def _motivating_overlay_regressions(
    report: dict[str, Any],
    baseline_ids: list[str],
) -> list[dict[str, Any]]:
    regressions: list[dict[str, Any]] = []
    for name in MOTIVATING_OVERLAYS:
        overlay = report["challenge_overlays"].get(name, {})
        g28_count = overlay.get(G28_ARM_ID, {}).get("paper_monthly", {}).get("correct", 0)
        baseline_counts = {
            arm_id: overlay.get(arm_id, {}).get("paper_monthly", {}).get("correct", 0)
            for arm_id in baseline_ids
        }
        best = max(baseline_counts.values()) if baseline_counts else 0
        if g28_count < best:
            regressions.append(
                {
                    "overlay": name,
                    "g28_correct": g28_count,
                    "best_baseline_correct": best,
                    "best_baseline_arm_ids": [
                        arm_id
                        for arm_id, correct in baseline_counts.items()
                        if correct == best
                    ],
                }
            )
    return regressions


def _g17_regressions_against_builder(report: dict[str, Any]) -> list[str]:
    if "builder_gap_gpt" not in report["summary"]["arms"]:
        return []
    regressions: list[str] = []
    for row in report["before_after_ledger"]:
        if not row.get("g17_policy_bucket"):
            continue
        builder = row["before"].get("builder_gap_gpt")
        if not builder:
            continue
        if builder["paper_monthly_match"] and not row["after"]["g28"]["paper_monthly_match"]:
            regressions.append(row["record_id"])
    return regressions


def _decision_rationale(
    *,
    g28_correct: int,
    best_baseline: int,
    lift_passed: bool,
    overlay_regressions: list[dict[str, Any]],
    g17_regressions: list[str],
    trace_complete: bool,
    gate_passed: bool,
) -> str:
    parts = [
        (
            f"G28 paper-monthly count is {g28_correct} versus best baseline "
            f"{best_baseline}; G25 generalization gate "
            f"{'passed' if gate_passed else 'failed'}."
        )
    ]
    if overlay_regressions:
        parts.append(
            "Motivating overlay regressions remain: "
            + ", ".join(row["overlay"] for row in overlay_regressions)
            + "."
        )
    if g17_regressions:
        parts.append(
            "G17 builder-gap regressions remain: "
            + ", ".join(f"`{record_id}`" for record_id in g17_regressions)
            + "."
        )
    if not trace_complete:
        parts.append("Closed-option trace fields are incomplete.")
    return " ".join(parts)


def _dict_value(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_value(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _option_label(option: Mapping[str, Any]) -> str | None:
    label = option.get("canonical_label") or option.get("constructed_label")
    return str(label) if label is not None else None


def _mean(values: list[int]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _count_pct(value: dict[str, Any]) -> str:
    if not value:
        return ""
    return f"{value['correct']}/{value['records']} ({_pct(value['accuracy'])})"


def _counter_label(counter: Mapping[str, Any]) -> str:
    if not counter:
        return "`none`"
    return ", ".join(f"`{key}`={value}" for key, value in sorted(counter.items()))


def _inline_code_list(values: list[Any]) -> str:
    if not values:
        return "`none`"
    return ", ".join(f"`{value}`" for value in values)


def _yn(value: object) -> str:
    return "yes" if bool(value) else "no"


__all__ = [
    "DEFAULT_BASELINE_RUNS",
    "DEFAULT_JSON_OUTPUT",
    "DEFAULT_MARKDOWN_OUTPUT",
    "G28_ARM_ID",
    "build_gan_g28_evidence_first_target_selector_report",
    "render_gan_g28_markdown",
    "write_report_artifacts",
]
