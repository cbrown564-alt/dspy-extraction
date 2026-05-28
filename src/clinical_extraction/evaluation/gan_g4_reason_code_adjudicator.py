"""Post-hoc G4 report for the Gan S0 explicit reason-code adjudicator."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_g2_model_arm_comparison import (
    DEFAULT_ARM_RUNS as DEFAULT_G2_ARM_RUNS,
    build_gan_g2_model_arm_comparison_report,
)
from clinical_extraction.paths import resolve_run_directory
from clinical_extraction.schemas import PredictionSet

G4_ARM_ID = "g4_explicit_reason_code_adjudicator"
DEFAULT_G4_RUN = Path(
    "runs/gan_s0_g4_explicit_reason_code_adjudicator_gpt4_1_mini_slice_20260528T220121Z"
)
DEFAULT_ARM_RUNS = {**DEFAULT_G2_ARM_RUNS, G4_ARM_ID: DEFAULT_G4_RUN}
DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g4_explicit_reason_code_adjudicator_report_20260528.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g4_explicit_reason_code_adjudicator_report_20260528.md"
)


def build_gan_g4_reason_code_adjudicator_report(
    *,
    arm_run_dirs: Mapping[str, Path] | None = None,
    g4_arm_id: str = G4_ARM_ID,
) -> dict[str, Any]:
    """Build a G4 dual-scorer comparison plus explicit reason-code diagnostics."""

    arm_dirs = dict(arm_run_dirs or DEFAULT_ARM_RUNS)
    if g4_arm_id not in arm_dirs:
        raise ValueError(f"Missing G4 arm {g4_arm_id!r}.")

    report = build_gan_g2_model_arm_comparison_report(arm_run_dirs=arm_dirs)
    _relativize_arm_run_dirs(report)
    report["generated_at"] = datetime.now(UTC).isoformat()
    report["kanban_card"] = "G4 - Gan Explicit Reason-Code Adjudicator"
    report["comparison_group"] = "gan_s0_g4_explicit_reason_code_adjudicator_v1"
    report["g4_arm_id"] = g4_arm_id
    report["g4_diagnostics"] = _g4_diagnostics(
        report=report,
        g4_run_dir=arm_dirs[g4_arm_id],
        g4_arm_id=g4_arm_id,
    )
    report["decision"] = _decision(report, g4_arm_id=g4_arm_id)
    return report


def write_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_MARKDOWN_OUTPUT,
) -> None:
    """Write G4 JSON and Markdown report artifacts."""

    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_gan_g4_markdown(report), encoding="utf-8")


def render_gan_g4_markdown(report: dict[str, Any]) -> str:
    """Render a compact Markdown decision report for G4."""

    g4_arm_id = report["g4_arm_id"]
    diagnostics = report["g4_diagnostics"]
    decision = report["decision"]
    lines = [
        "# Gan S0 G4 Explicit Reason-Code Adjudicator",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Scope",
        "",
        f"- Dataset: `{report['dataset']}`",
        f"- Split: `{report['record_scope']['split_name']}`",
        f"- Records: `{report['record_scope']['records']}` enriched validation records",
        f"- G4 arm: `{g4_arm_id}`",
        f"- Gold source: `{report['gold_source']}`",
        "- Scorer views: `gan2026_paper_reproduction` and "
        "`gan_frequency_deterministic_v1`.",
        "",
        "## Decision",
        "",
        f"- Recommendation: `{decision['promotion_recommendation']}`",
        f"- Scope: `{decision['decision_scope']}`",
        f"- Rationale: {decision['rationale']}",
        "",
        "## Arm Summary",
        "",
        "| Arm | Run ID | Paper monthly | Canonical monthly | Canonical pragmatic |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for arm in report["arms"]:
        summary = report["summary"]["arms"][arm["arm_id"]]
        lines.append(
            "| "
            f"`{arm['arm_id']}` | "
            f"`{arm['run_id']}` | "
            f"{_pct(summary['paper_reproduction']['monthly_frequency_accuracy'])} | "
            f"{_pct(summary['canonical']['monthly_frequency_accuracy'])} | "
            f"{_pct(summary['canonical']['pragmatic_category_accuracy'])} |"
        )

    lines.extend(
        [
            "",
            "## G4 Traceability Diagnostics",
            "",
            f"- Selected candidate references present: "
            f"{diagnostics['selected_candidate_references_present']['count']}/"
            f"{diagnostics['selected_candidate_references_present']['denominator']}",
            f"- Label-construction inputs present: "
            f"{diagnostics['label_construction_inputs_present']['count']}/"
            f"{diagnostics['label_construction_inputs_present']['denominator']}",
            f"- Unsupported selected-candidate cases: "
            f"{len(diagnostics['unsupported_candidate_cases'])}",
            f"- Model final-label mismatches after deterministic construction: "
            f"{diagnostics['model_final_label_mismatch_count']}",
            "",
            "| Reason code | Count |",
            "| --- | ---: |",
        ]
    )
    for key, count in sorted(diagnostics["reason_code_counts"].items()):
        lines.append(f"| `{key}` | {count} |")

    lines.extend(
        [
            "",
            "| Primary failure type | Count |",
            "| --- | ---: |",
        ]
    )
    for key, count in sorted(diagnostics["primary_failure_type_counts"].items()):
        lines.append(f"| `{key}` | {count} |")

    lines.extend(
        [
            "",
            "| Failure signal | Count |",
            "| --- | ---: |",
        ]
    )
    for key, count in sorted(diagnostics["failure_signal_counts"].items()):
        lines.append(f"| `{key}` | {count} |")

    lines.extend(
        [
            "",
            "## G4 Failure Records",
            "",
            "| Record | Gold | G4 prediction | Reason code | Selected candidate | Primary failure | Signals |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for failure in diagnostics["failure_records"]:
        lines.append(
            "| "
            f"`{failure['record_id']}` | "
            f"`{failure['gold_label']}` | "
            f"`{failure['predicted_label']}` | "
            f"`{failure['reason_code']}` | "
            f"`{failure['selected_candidate_label']}` | "
            f"`{failure['primary_failure_type']}` | "
            f"{_inline_code_list(failure['failure_signals'])} |"
        )

    lines.extend(
        [
            "",
            "## Pairwise Deltas",
            "",
            "| Baseline | G4 correct / baseline wrong | G4 wrong / baseline correct |",
            "| --- | --- | --- |",
        ]
    )
    for baseline_id, deltas in diagnostics["pairwise_deltas"].items():
        lines.append(
            "| "
            f"`{baseline_id}` | "
            f"{_inline_code_list(deltas['g4_correct_baseline_wrong'])} | "
            f"{_inline_code_list(deltas['g4_wrong_baseline_correct'])} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- G4 preserves the requested trace fields: explicit reason code, selected "
            "candidate reference, and label-construction inputs.",
            "- The tested implementation underperforms the G2 candidate-constrained and "
            "seeded answer-options baselines on the same slice.",
            "- All G4 misses are primary target-selection failures with a policy-conflict "
            "signal: a seizure-free-duration candidate was selected despite a "
            "gold-compatible quantified candidate being present.",
            "- No label-construction or evidence-support failure was observed in this "
            "slice.",
            "",
        ]
    )
    return "\n".join(lines)


def _g4_diagnostics(
    *,
    report: dict[str, Any],
    g4_run_dir: Path,
    g4_arm_id: str,
) -> dict[str, Any]:
    prediction_set = _load_prediction_set(g4_run_dir)
    predictions_by_id = {
        prediction.document_id: prediction
        for prediction in prediction_set.predictions
    }
    records_by_id = {record.record_id: record for record in load_gan_records()}

    reason_code_counts: Counter[str] = Counter()
    error_class_counts: Counter[str] = Counter()
    selected_candidate_index_counts: Counter[str] = Counter()
    selected_candidate_label_counts: Counter[str] = Counter()
    primary_failure_type_counts: Counter[str] = Counter({"none": 0})
    failure_signal_counts: Counter[str] = Counter()
    selected_candidate_references_present = 0
    label_construction_inputs_present = 0
    model_final_label_mismatch_count = 0
    unsupported_candidate_cases: list[dict[str, Any]] = []
    failure_records: list[dict[str, Any]] = []

    for row in report["rows"]:
        record_id = row["record_id"]
        prediction = predictions_by_id[record_id]
        metadata = prediction.metadata
        selected = _dict_value(metadata.get("selected_candidate_reference"))
        adjudication = _dict_value(metadata.get("reason_code_adjudication"))
        label_inputs = _dict_value(metadata.get("label_construction_inputs"))
        g4_row = row["arms"][g4_arm_id]
        candidate_labels = _list_value(metadata.get("temporal_candidate_labels"))

        reason_code = _string_value(
            metadata.get("target_selection_reason_code")
            or adjudication.get("reason_code"),
            default="missing",
        )
        error_class = _string_value(
            metadata.get("target_selection_error_class")
            or adjudication.get("error_class"),
            default="missing",
        )
        selected_index = selected.get("candidate_index")
        selected_label = _string_value(
            selected.get("constructed_label")
            or adjudication.get("selected_candidate_label"),
            default="missing",
        )

        reason_code_counts[reason_code] += 1
        error_class_counts[error_class] += 1
        selected_candidate_index_counts[str(selected_index)] += 1
        selected_candidate_label_counts[selected_label] += 1
        selected_candidate_references_present += int(bool(selected))
        label_construction_inputs_present += int(bool(label_inputs))

        mismatch = metadata.get("model_final_label_mismatch")
        if mismatch:
            model_final_label_mismatch_count += 1

        unsupported_reasons = _unsupported_candidate_reasons(
            selected=selected,
            candidate_labels=candidate_labels,
            record_note=records_by_id[record_id].note_text,
        )
        for reason in unsupported_reasons:
            unsupported_candidate_cases.append(
                {
                    "record_id": record_id,
                    "reason": reason,
                    "reason_code": reason_code,
                    "selected_candidate_label": selected_label,
                }
            )

        monthly_match = bool(
            g4_row["scores"]["canonical"]["monthly_frequency_match"]
        )
        primary_failure_type, failure_signals = _failure_classification(
            monthly_match=monthly_match,
            gold_label=row["gold_label"],
            predicted_label=g4_row["predicted_label"],
            selected_label=selected_label,
            reason_code=reason_code,
            unsupported_reasons=unsupported_reasons,
            construction_mismatch=bool(mismatch),
            candidate_labels=candidate_labels,
        )
        primary_failure_type_counts[primary_failure_type] += 1
        failure_signal_counts.update(failure_signals)

        if primary_failure_type != "none":
            failure_records.append(
                {
                    "record_id": record_id,
                    "gold_label": row["gold_label"],
                    "predicted_label": g4_row["predicted_label"],
                    "reason_code": reason_code,
                    "selected_candidate_index": selected_index,
                    "selected_candidate_label": selected_label,
                    "primary_failure_type": primary_failure_type,
                    "failure_signals": failure_signals,
                    "gold_label_in_candidates": row["gold_label"] in candidate_labels,
                    "selected_evidence_text": selected.get("evidence_text"),
                }
            )

    denominator = len(report["rows"])
    return {
        "reason_code_counts": dict(reason_code_counts),
        "error_class_counts": dict(error_class_counts),
        "selected_candidate_index_counts": dict(selected_candidate_index_counts),
        "selected_candidate_label_counts": dict(selected_candidate_label_counts),
        "selected_candidate_references_present": {
            "count": selected_candidate_references_present,
            "denominator": denominator,
        },
        "label_construction_inputs_present": {
            "count": label_construction_inputs_present,
            "denominator": denominator,
        },
        "model_final_label_mismatch_count": model_final_label_mismatch_count,
        "unsupported_candidate_cases": unsupported_candidate_cases,
        "primary_failure_type_counts": dict(primary_failure_type_counts),
        "failure_signal_counts": dict(failure_signal_counts),
        "failure_records": failure_records,
        "pairwise_deltas": _pairwise_deltas(report, g4_arm_id=g4_arm_id),
    }


def _load_prediction_set(run_dir: Path) -> PredictionSet:
    resolved = resolve_run_directory(run_dir, include_archive=True)
    return PredictionSet.model_validate_json(
        (resolved / "predictions.json").read_text(encoding="utf-8")
    )


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


def _unsupported_candidate_reasons(
    *,
    selected: Mapping[str, Any],
    candidate_labels: list[str],
    record_note: str,
) -> list[str]:
    reasons: list[str] = []
    if not selected:
        return ["missing_selected_candidate_reference"]

    selected_index = selected.get("candidate_index")
    if not isinstance(selected_index, int) or not (
        1 <= selected_index <= len(candidate_labels)
    ):
        reasons.append("selected_candidate_index_out_of_range")

    evidence_text = selected.get("evidence_text")
    if not isinstance(evidence_text, str) or not evidence_text.strip():
        reasons.append("selected_candidate_evidence_missing")
    elif evidence_text not in record_note:
        reasons.append("selected_candidate_evidence_unsupported")
    return reasons


def _failure_classification(
    *,
    monthly_match: bool,
    gold_label: str,
    predicted_label: str | None,
    selected_label: str,
    reason_code: str,
    unsupported_reasons: list[str],
    construction_mismatch: bool,
    candidate_labels: list[str],
) -> tuple[str, list[str]]:
    if monthly_match:
        return "none", []

    signals: list[str] = []
    if unsupported_reasons:
        signals.append("evidence")
        return "evidence", signals
    if construction_mismatch:
        signals.append("label_construction")
        return "label_construction", signals

    if gold_label in candidate_labels:
        signals.append("target_selection")
        primary = "target_selection"
    else:
        signals.append("candidate_coverage")
        primary = "candidate_coverage"

    if _is_seizure_free_label(selected_label) and _has_quantified_candidate(
        candidate_labels
    ):
        signals.append("policy")
    if _reason_code_label_incoherent(reason_code, selected_label):
        signals.append("reason_code_label_incoherent")
    if predicted_label != selected_label:
        signals.append("prediction_selected_label_mismatch")
    return primary, signals


def _pairwise_deltas(
    report: dict[str, Any],
    *,
    g4_arm_id: str,
) -> dict[str, dict[str, list[str]]]:
    deltas: dict[str, dict[str, list[str]]] = {}
    baseline_ids = [arm["arm_id"] for arm in report["arms"] if arm["arm_id"] != g4_arm_id]
    for baseline_id in baseline_ids:
        g4_correct_baseline_wrong: list[str] = []
        g4_wrong_baseline_correct: list[str] = []
        for row in report["rows"]:
            g4_match = bool(
                row["arms"][g4_arm_id]["scores"]["canonical"][
                    "monthly_frequency_match"
                ]
            )
            baseline_match = bool(
                row["arms"][baseline_id]["scores"]["canonical"][
                    "monthly_frequency_match"
                ]
            )
            if g4_match and not baseline_match:
                g4_correct_baseline_wrong.append(row["record_id"])
            elif not g4_match and baseline_match:
                g4_wrong_baseline_correct.append(row["record_id"])
        deltas[baseline_id] = {
            "g4_correct_baseline_wrong": g4_correct_baseline_wrong,
            "g4_wrong_baseline_correct": g4_wrong_baseline_correct,
        }
    return deltas


def _decision(report: dict[str, Any], *, g4_arm_id: str) -> dict[str, Any]:
    summaries = report["summary"]["arms"]
    g4 = summaries[g4_arm_id]["canonical"]
    candidate = summaries.get("candidate_constrained", {}).get("canonical", {})
    reason = summaries.get("reason_code_selector", {}).get("canonical", {})
    best_baseline_monthly = max(
        candidate.get("monthly_frequency_accuracy", 0.0),
        reason.get("monthly_frequency_accuracy", 0.0),
    )
    best_baseline_pragmatic = max(
        candidate.get("pragmatic_category_accuracy", 0.0),
        reason.get("pragmatic_category_accuracy", 0.0),
    )
    if (
        g4["monthly_frequency_accuracy"] >= best_baseline_monthly
        and g4["pragmatic_category_accuracy"] >= best_baseline_pragmatic
    ):
        recommendation = "eligible_for_full_validation_gate"
        rationale = (
            "G4 matched the strongest same-slice G2 baselines under the canonical "
            "monthly and pragmatic scorer views while adding explicit traceability."
        )
    else:
        recommendation = "do_not_promote_as_tested"
        rationale = (
            "G4 reached "
            f"{_pct(g4['monthly_frequency_accuracy'])} canonical monthly and "
            f"{_pct(g4['pragmatic_category_accuracy'])} pragmatic accuracy, below "
            f"the best same-slice G2 baselines ({_pct(best_baseline_monthly)} "
            f"monthly, {_pct(best_baseline_pragmatic)} pragmatic)."
        )
    return {
        "promotion_recommendation": recommendation,
        "decision_scope": "diagnostic_slice_only",
        "rationale": rationale,
    }


def _dict_value(value: object) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _list_value(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _string_value(value: object, *, default: str) -> str:
    if isinstance(value, str) and value:
        return value
    return default


def _is_seizure_free_label(label: str) -> bool:
    return label.startswith("seizure free")


def _has_quantified_candidate(candidate_labels: list[str]) -> bool:
    return any(
        label
        and label not in {"unknown", "no seizure frequency reference"}
        and not _is_seizure_free_label(label)
        for label in candidate_labels
    )


def _reason_code_label_incoherent(reason_code: str, selected_label: str) -> bool:
    if reason_code == "select_seizure_free_duration":
        return not _is_seizure_free_label(selected_label)
    if reason_code == "select_current_quantified_rate":
        return _is_seizure_free_label(selected_label)
    return False


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _inline_code_list(values: list[str]) -> str:
    if not values:
        return ""
    return ", ".join(f"`{value}`" for value in values)
