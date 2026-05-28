from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.cli import _gan_frequency_value, _prediction_label
from clinical_extraction.evaluation.gan_failure_taxonomy import (
    classify_gan_frequency_failure,
    failure_action_tier,
)
from clinical_extraction.gan.frequency import pragmatic_category, purist_category
from clinical_extraction.gan.scoring import score_gan_frequency_prediction
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates_from_note,
)
from clinical_extraction.schemas import PredictionSet


ARITHMETIC_FAILURE_CLASSES = {
    "pragmatic_match_monthly_divergence",
    "purist_bin_boundary_within_pragmatic",
}
UNKNOWN_FAILURE_CLASSES = {
    "unknown_as_high_rate",
    "unknown_as_quantified_rate",
    "unknown_vs_no_reference",
    "unknown_vs_seizure_free",
    "cluster_structure_swap",
}
CLUSTER_FAILURE_CLASSES = {
    "cluster_collapsed_to_rate",
    "cluster_semantic_mismatch",
}

DEFAULT_ERROR_READ_TARGETS = {
    "arithmetic_window_precision": 10,
    "unknown_vs_quantified": 8,
    "cluster_composition": 8,
    "infrequent_long_denominator_or_boundary": 4,
}


def assign_residual_group(row: dict[str, Any]) -> str:
    failure_class = str(row.get("failure_class", ""))
    if failure_class in ARITHMETIC_FAILURE_CLASSES:
        return "arithmetic_window_precision"
    if failure_class in UNKNOWN_FAILURE_CLASSES:
        return "unknown_vs_quantified"
    if failure_class in CLUSTER_FAILURE_CLASSES:
        return "cluster_composition"
    if row.get("gold_pragmatic_category") == "infrequent":
        return "infrequent_long_denominator_or_boundary"
    return "other_benchmark_severe"


def monthly_miss_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    misses = [
        row
        for row in rows
        if row.get("status") == "scored"
        and row.get("monthly_match") is False
        and row.get("failure_action_tier") == "benchmark_severe"
    ]
    enriched: list[dict[str, Any]] = []
    for row in misses:
        enriched.append({**row, "residual_group": assign_residual_group(row)})
    return enriched


def select_error_read_rows(
    rows: list[dict[str, Any]],
    *,
    targets: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    target_counts = targets or DEFAULT_ERROR_READ_TARGETS
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    rows_with_groups = [
        row if "residual_group" in row else {**row, "residual_group": assign_residual_group(row)}
        for row in rows
    ]

    for group, target in target_counts.items():
        group_rows = [
            row
            for row in rows_with_groups
            if row.get("residual_group") == group and row["record_id"] not in selected_ids
        ]
        group_rows.sort(key=_selection_sort_key)
        for row in group_rows[:target]:
            selected.append(row)
            selected_ids.add(row["record_id"])

    return selected


def load_analysis_rows(records_jsonl: Path) -> list[dict[str, Any]]:
    rows = []
    with records_jsonl.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def build_residual_slice(
    *,
    records_jsonl: Path,
    predictions_json: Path,
) -> dict[str, Any]:
    rows = monthly_miss_rows(load_analysis_rows(records_jsonl))
    gold_by_id = {record.record_id: record for record in load_gan_records()}
    prediction_set = PredictionSet.model_validate_json(
        predictions_json.read_text(encoding="utf-8")
    )
    prediction_by_id = {
        prediction.document_id: prediction for prediction in prediction_set.predictions
    }

    enriched_rows = []
    for row in rows:
        record = gold_by_id[row["record_id"]]
        prediction = prediction_by_id.get(row["record_id"])
        temporal_candidates = build_temporal_frequency_candidates_from_note(record.note_text)
        enriched_rows.append(
            {
                **row,
                "gold_evidence": record.gold_evidence,
                "reference_evidence": record.reference_evidence,
                "note_text": record.note_text,
                "prediction_metadata": prediction.metadata if prediction else {},
                "predicted_evidence": [
                    span.model_dump()
                    for value in (prediction.values if prediction else [])
                    for span in value.evidence
                ],
                "deterministic_temporal_candidates": [
                    asdict(candidate) for candidate in temporal_candidates
                ],
                "gold_in_deterministic_temporal_candidates": any(
                    candidate.canonical_label == record.gold_label
                    for candidate in temporal_candidates
                ),
            }
        )

    selected = select_error_read_rows(enriched_rows)
    return {
        "rows": enriched_rows,
        "selected_rows": selected,
        "summary": summarize_residual_slice(enriched_rows, selected),
    }


def summarize_residual_slice(
    rows: list[dict[str, Any]], selected_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "monthly_miss_count": len(rows),
        "residual_group_counts": dict(Counter(row["residual_group"] for row in rows)),
        "failure_class_counts": dict(Counter(row["failure_class"] for row in rows)),
        "selected_count": len(selected_rows),
        "selected_group_counts": dict(
            Counter(row["residual_group"] for row in selected_rows)
        ),
        "selected_record_ids": [row["record_id"] for row in selected_rows],
        "gold_in_candidate_count": sum(
            1 for row in rows if row["gold_in_deterministic_temporal_candidates"]
        ),
        "any_candidate_count": sum(
            1 for row in rows if row["deterministic_temporal_candidates"]
        ),
    }


def write_residual_slice_outputs(
    *,
    output_dir: Path,
    doc_path: Path,
    run_id: str,
    slice_payload: dict[str, Any],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(slice_payload["summary"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "monthly_misses.jsonl").open("w", encoding="utf-8") as handle:
        for row in slice_payload["rows"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    with (output_dir / "error_read_selection.jsonl").open("w", encoding="utf-8") as handle:
        for row in slice_payload["selected_rows"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    doc_path.write_text(
        render_error_read_markdown(
            run_id=run_id,
            summary=slice_payload["summary"],
            selected_rows=slice_payload["selected_rows"],
        ),
        encoding="utf-8",
    )


def render_error_read_markdown(
    *,
    run_id: str,
    summary: dict[str, Any],
    selected_rows: list[dict[str, Any]],
) -> str:
    lines = [
        "# Gan S0 Exact-Frequency Residual Slice Error Read",
        "",
        "Date: 2026-05-21",
        f"Run: `{run_id}`",
        "Dataset / split: `gan_2026_fixed_v1:validation`",
        "Scorer: `gan_frequency_deterministic_v1`",
        "",
        "## Scope",
        "",
        f"This read queue contains {summary['selected_count']} representative records from "
        f"{summary['monthly_miss_count']} benchmark-severe monthly-frequency misses.",
        "",
        "## Slice Counts",
        "",
        "| Group | Count | Selected |",
        "| --- | ---: | ---: |",
    ]
    selected_counts = Counter(row["residual_group"] for row in selected_rows)
    for group, count in summary["residual_group_counts"].items():
        lines.append(f"| `{group}` | {count} | {selected_counts.get(group, 0)} |")
    lines.extend(
        [
            "",
            "## Read Queue",
            "",
            "| Group | record_id | failure_class | gold | predicted | reference | candidates |",
            "| --- | --- | --- | --- | --- | --- | ---: |",
        ]
    )
    for row in selected_rows:
        lines.append(
            "| "
            f"`{row['residual_group']}` | "
            f"`{row['record_id']}` | "
            f"`{row['failure_class']}` | "
            f"`{row['gold_label']}` | "
            f"`{row.get('predicted_label', '')}` | "
            f"`{row.get('reference_label', '')}` | "
            f"{len(row['deterministic_temporal_candidates'])} |"
        )

    lines.extend(["", "## Record Notes", ""])
    for index, row in enumerate(selected_rows, start=1):
        lines.extend(
            [
                f"### {index}. `{row['record_id']}` — `{row['residual_group']}`",
                "",
                f"- Failure: `{row['failure_class']}` / pattern `{row.get('metric_pattern', '')}`",
                f"- Gold: `{row['gold_label']}` ({row.get('gold_monthly_frequency')}/month, `{row.get('gold_pragmatic_category')}`, `{row.get('gold_purist_category')}`)",
                f"- Predicted: `{row.get('predicted_label')}` ({row.get('predicted_monthly_frequency')}/month, `{row.get('predicted_pragmatic_category')}`, `{row.get('predicted_purist_category')}`)",
                f"- Reference: `{row.get('reference_label')}`; hard case: `{row.get('hard_case')}`; row_ok: `{row.get('row_ok')}`",
                f"- Gold in deterministic candidates: `{row['gold_in_deterministic_temporal_candidates']}`; candidate count: `{len(row['deterministic_temporal_candidates'])}`",
                "",
                "**Gold Evidence**",
                "",
                _fenced(row.get("gold_evidence") or ""),
                "",
                "**Predicted Evidence**",
                "",
                _fenced("\n\n".join(span.get("text", "") for span in row["predicted_evidence"])),
                "",
                "**Verifier Reason**",
                "",
                _fenced(str(row.get("prediction_metadata", {}).get("verifier_reason", ""))),
                "",
                "**Candidate Labels**",
                "",
                _fenced(
                    "\n".join(
                        candidate["canonical_label"]
                        for candidate in row["deterministic_temporal_candidates"]
                    )
                ),
                "",
                "**Frequency Context Snippet**",
                "",
                _fenced(_frequency_context(row["note_text"], row)),
                "",
                "**Manual Read Notes**",
                "",
                "- Mechanism:",
                "- Candidate-slot implication:",
                "- Deterministic repair allowed?:",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _selection_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("metric_pattern", ""),
        row.get("failure_class", ""),
        row.get("gold_pragmatic_category", ""),
        row.get("record_id", ""),
    )


def _frequency_context(note_text: str, row: dict[str, Any]) -> str:
    anchors = [
        row.get("gold_evidence"),
        *(span.get("text") for span in row.get("predicted_evidence", [])),
    ]
    snippets = []
    for anchor in anchors:
        if not anchor:
            continue
        index = note_text.find(anchor)
        if index == -1:
            continue
        start = max(0, index - 350)
        end = min(len(note_text), index + len(anchor) + 350)
        snippet = note_text[start:end].strip()
        if snippet and snippet not in snippets:
            snippets.append(snippet)
    if snippets:
        return "\n\n---\n\n".join(snippets)
    return note_text[:1400].strip()


def _fenced(text: str) -> str:
    return "```text\n" + (text.strip() or "(empty)") + "\n```"


def load_residual_slice_record_ids(fixture_path: Path) -> list[str]:
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    record_ids = payload.get("record_ids")
    if not isinstance(record_ids, list) or not record_ids:
        raise ValueError(f"{fixture_path} must define a non-empty record_ids list.")
    return [str(record_id) for record_id in record_ids]


def load_error_read_queue_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def build_scored_rows_for_run(
    *,
    run_dir: Path,
    record_ids: list[str],
) -> dict[str, dict[str, Any]]:
    prediction_set = PredictionSet.model_validate_json(
        (run_dir / "predictions.json").read_text(encoding="utf-8")
    )
    gold_by_id = {record.record_id: record for record in load_gan_records()}
    predictions_by_id = {
        prediction.document_id: prediction
        for prediction in prediction_set.predictions
    }

    scored_by_id: dict[str, dict[str, Any]] = {}
    for record_id in record_ids:
        gold = gold_by_id[record_id]
        base = {
            "record_id": record_id,
            "gold_label": gold.gold_label,
            "reference_label": gold.reference_label,
            "gold_pragmatic_category": pragmatic_category(gold.gold_label),
            "gold_purist_category": purist_category(gold.gold_label),
        }
        prediction = predictions_by_id.get(record_id)
        if prediction is None:
            scored_by_id[record_id] = {
                **base,
                "status": "missing_prediction",
            }
            continue

        predicted_value = _gan_frequency_value(prediction)
        if predicted_value is None:
            scored_by_id[record_id] = {
                **base,
                "status": "invalid",
                "predicted_label": None,
            }
            continue

        predicted_label = _prediction_label(predicted_value)
        if predicted_label is None:
            scored_by_id[record_id] = {
                **base,
                "status": "invalid",
                "predicted_label": None,
            }
            continue

        score = score_gan_frequency_prediction(
            gold_label=gold.gold_label,
            predicted_label=predicted_label,
        )
        row = {
            **base,
            "status": "scored",
            "predicted_label": predicted_label,
            "normalized_gold_label": score.normalized_gold_label,
            "normalized_predicted_label": score.normalized_predicted_label,
            "normalized_exact_match": score.exact_normalized_match,
            "monthly_match": score.monthly_frequency_match,
            "purist_match": score.purist_category_match,
            "pragmatic_match": score.pragmatic_category_match,
            "predicted_pragmatic_category": score.predicted_pragmatic_category,
        }
        row["failure_class"] = classify_gan_frequency_failure(row)
        row["failure_action_tier"] = failure_action_tier(row["failure_class"])
        scored_by_id[record_id] = row
    return scored_by_id


def compare_residual_slice_arms(
    *,
    queue_rows: list[dict[str, Any]],
    control_run_dir: Path,
    treatment_run_dir: Path,
    control_arm_id: str = "C0",
    treatment_arm_id: str = "C1",
    reference_arm_id: str = "VR",
) -> dict[str, Any]:
    record_ids = [row["record_id"] for row in queue_rows]
    control_by_id = build_scored_rows_for_run(
        run_dir=control_run_dir, record_ids=record_ids
    )
    treatment_by_id = build_scored_rows_for_run(
        run_dir=treatment_run_dir, record_ids=record_ids
    )

    per_record: list[dict[str, Any]] = []
    group_stats: dict[str, dict[str, int]] = {}

    for queue_row in queue_rows:
        record_id = queue_row["record_id"]
        residual_group = queue_row.get("residual_group") or assign_residual_group(
            queue_row
        )
        reference = {
            "predicted_label": queue_row.get("predicted_label"),
            "normalized_exact_match": queue_row.get("normalized_exact_match"),
            "monthly_match": queue_row.get("monthly_match"),
            "pragmatic_match": queue_row.get("pragmatic_match"),
        }
        control = control_by_id[record_id]
        treatment = treatment_by_id[record_id]

        c0_exact = control.get("normalized_exact_match") is True
        c1_exact = treatment.get("normalized_exact_match") is True
        c0_monthly = control.get("monthly_match") is True
        c1_monthly = treatment.get("monthly_match") is True
        ref_monthly = reference.get("monthly_match") is True

        exact_recovery = (not c0_exact) and c1_exact
        exact_regression = c0_exact and (not c1_exact)
        monthly_recovery = (not c0_monthly) and c1_monthly
        monthly_regression = c0_monthly and (not c1_monthly)
        c1_pragmatic_overcall = (
            treatment.get("status") == "scored"
            and treatment.get("pragmatic_match") is False
            and control.get("pragmatic_match") is True
        )

        entry = {
            "record_id": record_id,
            "residual_group": residual_group,
            "failure_class": queue_row.get("failure_class"),
            "gold_label": queue_row.get("gold_label"),
            reference_arm_id: reference,
            control_arm_id: control,
            treatment_arm_id: treatment,
            "exact_recovery_c1_vs_c0": exact_recovery,
            "exact_regression_c1_vs_c0": exact_regression,
            "monthly_recovery_c1_vs_c0": monthly_recovery,
            "monthly_regression_c1_vs_c0": monthly_regression,
            "c1_pragmatic_overcall_vs_c0": c1_pragmatic_overcall,
            "reference_monthly_miss": ref_monthly is False,
        }
        per_record.append(entry)

        bucket = group_stats.setdefault(
            residual_group,
            {
                "records": 0,
                "exact_recovery": 0,
                "exact_regression": 0,
                "monthly_recovery": 0,
                "monthly_regression": 0,
                "c1_pragmatic_overcall_vs_c0": 0,
                "c0_normalized_exact": 0,
                "c1_normalized_exact": 0,
                "c0_monthly": 0,
                "c1_monthly": 0,
            },
        )
        bucket["records"] += 1
        bucket["exact_recovery"] += int(exact_recovery)
        bucket["exact_regression"] += int(exact_regression)
        bucket["monthly_recovery"] += int(monthly_recovery)
        bucket["monthly_regression"] += int(monthly_regression)
        bucket["c1_pragmatic_overcall_vs_c0"] += int(c1_pragmatic_overcall)
        bucket["c0_normalized_exact"] += int(c0_exact)
        bucket["c1_normalized_exact"] += int(c1_exact)
        bucket["c0_monthly"] += int(c0_monthly)
        bucket["c1_monthly"] += int(c1_monthly)

    scored_control = [
        row for row in control_by_id.values() if row.get("status") == "scored"
    ]
    scored_treatment = [
        row for row in treatment_by_id.values() if row.get("status") == "scored"
    ]

    return {
        "record_count": len(per_record),
        "per_record": per_record,
        "by_group": group_stats,
        "headline": {
            "exact_recovery_c1_vs_c0": sum(
                1 for row in per_record if row["exact_recovery_c1_vs_c0"]
            ),
            "exact_regression_c1_vs_c0": sum(
                1 for row in per_record if row["exact_regression_c1_vs_c0"]
            ),
            "monthly_recovery_c1_vs_c0": sum(
                1 for row in per_record if row["monthly_recovery_c1_vs_c0"]
            ),
            "monthly_regression_c1_vs_c0": sum(
                1 for row in per_record if row["monthly_regression_c1_vs_c0"]
            ),
            "c1_pragmatic_overcall_vs_c0": sum(
                1 for row in per_record if row["c1_pragmatic_overcall_vs_c0"]
            ),
            "c0_normalized_exact_rate": (
                sum(1 for row in scored_control if row["normalized_exact_match"])
                / len(scored_control)
                if scored_control
                else None
            ),
            "c1_normalized_exact_rate": (
                sum(1 for row in scored_treatment if row["normalized_exact_match"])
                / len(scored_treatment)
                if scored_treatment
                else None
            ),
            "c0_monthly_rate": (
                sum(1 for row in scored_control if row["monthly_match"])
                / len(scored_control)
                if scored_control
                else None
            ),
            "c1_monthly_rate": (
                sum(1 for row in scored_treatment if row["monthly_match"])
                / len(scored_treatment)
                if scored_treatment
                else None
            ),
            "missing_predictions": {
                control_arm_id: sum(
                    1
                    for row in control_by_id.values()
                    if row.get("status") == "missing_prediction"
                ),
                treatment_arm_id: sum(
                    1
                    for row in treatment_by_id.values()
                    if row.get("status") == "missing_prediction"
                ),
            },
        },
        "control_run_id": control_run_dir.name,
        "treatment_run_id": treatment_run_dir.name,
    }
