"""Post-hoc G2 model-arm comparison for Gan S0 runs."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.cli import _gan_frequency_value, _prediction_label
from clinical_extraction.gan.scoring import (
    GAN_CANONICAL_SCORER,
    GAN_PAPER_REPRODUCTION_SCORER,
    score_gan_frequency_prediction,
)
from clinical_extraction.paths import resolve_run_directory
from clinical_extraction.schemas import DocumentPrediction, GanRecord, PredictionSet

DEFAULT_ARM_RUNS = {
    "free_adjudication": Path(
        "runs/gan_s0_g2_free_adjudication_gpt4_1_mini_slice_20260528T155000Z"
    ),
    "candidate_constrained": Path(
        "runs/gan_s0_g2_candidate_constrained_gpt4_1_mini_slice_20260528T155000Z"
    ),
    "reason_code_selector": Path(
        "runs/gan_s0_g2_reason_code_selector_gpt4_1_mini_slice_20260528T155000Z"
    ),
}
DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g2_model_arm_comparison_20260528.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g2_model_arm_comparison_20260528.md"
)
SCORER_MODES = (GAN_PAPER_REPRODUCTION_SCORER, GAN_CANONICAL_SCORER)
METRIC_KEYS = (
    "normalized_label_match",
    "monthly_frequency_match",
    "purist_category_match",
    "pragmatic_category_match",
)


@dataclass(frozen=True)
class ArmRun:
    """Loaded run artifacts for one model-arm comparison member."""

    arm_id: str
    run_dir: Path
    prediction_set: PredictionSet
    run_metadata: dict[str, Any]
    config: dict[str, Any]
    runtime: dict[str, Any]


def build_gan_g2_model_arm_comparison_report(
    *,
    arm_run_dirs: Mapping[str, Path] | None = None,
    record_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Build a dual-scorer comparison report for stored G2 Gan S0 arm runs."""

    arm_dirs = dict(arm_run_dirs or DEFAULT_ARM_RUNS)
    if not arm_dirs:
        raise ValueError("At least one arm run directory is required.")

    arms = [_load_arm_run(arm_id, run_dir) for arm_id, run_dir in arm_dirs.items()]
    _validate_arm_contexts(arms)
    gold_by_id = {record.record_id: record for record in load_gan_records()}
    ordered_ids = record_ids or _shared_ordered_prediction_ids(arms)
    missing_gold = [record_id for record_id in ordered_ids if record_id not in gold_by_id]
    if missing_gold:
        raise ValueError(f"record_ids not found in Gan gold: {missing_gold}")

    rows = [
        _record_row(record_id=record_id, gold=gold_by_id[record_id], arms=arms)
        for record_id in ordered_ids
    ]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": "gan_2026",
        "schema_level": "gan_frequency_s0",
        "comparison_group": "gan_s0_g2_model_arm_comparison_v1",
        "record_scope": {
            "split_name": _first_config_value(arms, "split_name"),
            "records": len(ordered_ids),
            "record_ids": ordered_ids,
        },
        "gold_source": "check__Seizure Frequency Number.seizure_frequency_number[0]",
        "reference_policy": (
            "reference[0] is not used as gold; it remains a difficulty signal only."
        ),
        "scorer_semantics": {
            "paper_reproduction": (
                "Gan 2026 paper-compatible scoring view for comparison reporting."
            ),
            "canonical": (
                "Audited project scorer that keeps unknown and no seizure frequency "
                "reference distinct outside paper reproduction."
            ),
        },
        "arms": [_arm_metadata(arm) for arm in arms],
        "summary": _summary(rows, arms),
        "rows": rows,
    }


def write_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_model_arm_markdown(report), encoding="utf-8")


def render_model_arm_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Gan S0 G2 Model-Arm Comparison",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Scope",
        "",
        f"- Dataset: `{report['dataset']}`",
        f"- Split: `{report['record_scope']['split_name']}`",
        f"- Records: `{report['record_scope']['records']}` enriched validation records",
        f"- Gold source: `{report['gold_source']}`",
        f"- Comparison group: `{report['comparison_group']}`",
        "",
        "## Arm Summary",
        "",
        "| Arm | Run ID | Program variant | Valid | Paper monthly | Canonical monthly | Canonical normalized | Canonical purist | Canonical pragmatic | Mean candidates | Mean options | Selected source counts |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for arm in report["arms"]:
        summary = report["summary"]["arms"][arm["arm_id"]]
        canonical = summary["canonical"]
        paper = summary["paper_reproduction"]
        option_diag = summary["option_diagnostics"]
        lines.append(
            "| "
            f"`{arm['arm_id']}` | "
            f"`{arm['run_id']}` | "
            f"`{arm['program_variant']}` | "
            f"{summary['valid_predictions']}/{summary['records']} | "
            f"{_pct(paper['monthly_frequency_accuracy'])} | "
            f"{_pct(canonical['monthly_frequency_accuracy'])} | "
            f"{_pct(canonical['normalized_label_accuracy'])} | "
            f"{_pct(canonical['purist_category_accuracy'])} | "
            f"{_pct(canonical['pragmatic_category_accuracy'])} | "
            f"{option_diag['mean_temporal_candidates']:.1f} | "
            f"{option_diag['mean_answer_options']:.1f} | "
            f"{_counter_label(option_diag['selected_answer_source_counts'])} |"
        )

    lines.extend(
        [
            "",
            "## Pairwise Signal",
            "",
            "| Scorer | Metric | Best arms | Best accuracy |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for scorer_key in ("paper_reproduction", "canonical"):
        for metric_key, metric_label in (
            ("monthly_frequency_accuracy", "monthly"),
            ("normalized_label_accuracy", "normalized label"),
            ("pragmatic_category_accuracy", "pragmatic category"),
        ):
            best = report["summary"]["best_by_metric"][scorer_key][metric_key]
            lines.append(
                "| "
                f"`{scorer_key}` | {metric_label} | "
                f"{_arm_id_list(best['arm_ids'])} | "
                f"{_pct(best['accuracy'])} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The candidate-constrained and seeded selector arms both recover the G2 target-selection lift on this enriched slice; free full-note adjudication does not.",
            "- The seeded selector is reported as a reason-code/answer-options surrogate because it preserves option source, status, ambiguity flags, and deterministic selection metadata, but it is not a newly designed explicit reason-code adjudicator.",
            "- Slice metrics are diagnostic. They should guide mechanism selection and error forensics, not stand in for full-validation or test performance.",
            "",
            "## Differential Records",
            "",
            "| Record | Gold | Free | Candidate | Reason-code surrogate | Canonical monthly pattern |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["summary"]["differential_records"]:
        labels = row["predicted_labels"]
        pattern = row["canonical_monthly_matches"]
        lines.append(
            "| "
            f"`{row['record_id']}` | "
            f"`{row['gold_label']}` | "
            f"`{labels.get('free_adjudication', '')}` | "
            f"`{labels.get('candidate_constrained', '')}` | "
            f"`{labels.get('reason_code_selector', '')}` | "
            f"{_counter_label(pattern)} |"
        )
    lines.append("")
    return "\n".join(lines)


def _load_arm_run(arm_id: str, run_dir: Path) -> ArmRun:
    run_dir = resolve_run_directory(run_dir)
    prediction_path = run_dir / "predictions.json"
    if not prediction_path.exists():
        raise FileNotFoundError(f"Missing predictions artifact: {prediction_path}")
    prediction_set = PredictionSet.model_validate_json(
        prediction_path.read_text(encoding="utf-8")
    )
    return ArmRun(
        arm_id=arm_id,
        run_dir=run_dir,
        prediction_set=prediction_set,
        run_metadata=_load_json(run_dir / "metadata.json"),
        config=_load_json(run_dir / "config.json"),
        runtime=_load_json(run_dir / "metrics.json").get("runtime", {}),
    )


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_arm_contexts(arms: list[ArmRun]) -> None:
    for arm in arms:
        if arm.prediction_set.dataset != "gan_2026":
            raise ValueError(f"{arm.arm_id} is not a Gan run.")
        if arm.prediction_set.schema_level != "gan_frequency_s0":
            raise ValueError(f"{arm.arm_id} is not a Gan S0 run.")


def _shared_ordered_prediction_ids(arms: list[ArmRun]) -> list[str]:
    first = [prediction.document_id for prediction in arms[0].prediction_set.predictions]
    first_set = set(first)
    for arm in arms[1:]:
        arm_set = {prediction.document_id for prediction in arm.prediction_set.predictions}
        if arm_set != first_set:
            raise ValueError(
                "Arm prediction sets must share the same record IDs unless record_ids "
                "is provided."
            )
    return first


def _record_row(
    *,
    record_id: str,
    gold: GanRecord,
    arms: list[ArmRun],
) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "gold_label": gold.gold_label,
        "reference_label": gold.reference_label,
        "row_ok": gold.row_ok,
        "hard_case": "hard_case" in gold.flags,
        "arms": {
            arm.arm_id: _prediction_row(
                prediction=_predictions_by_id(arm).get(record_id),
                gold_label=gold.gold_label,
            )
            for arm in arms
        },
    }


def _predictions_by_id(arm: ArmRun) -> dict[str, DocumentPrediction]:
    return {
        prediction.document_id: prediction
        for prediction in arm.prediction_set.predictions
    }


def _prediction_row(
    *,
    prediction: DocumentPrediction | None,
    gold_label: str,
) -> dict[str, Any]:
    if prediction is None:
        return _invalid_prediction_row("missing_prediction")
    predicted_value = _gan_frequency_value(prediction)
    if predicted_value is None:
        return _invalid_prediction_row("missing_seizure_frequency_number")
    predicted_label = _prediction_label(predicted_value)
    if predicted_label is None:
        return _invalid_prediction_row("missing_predicted_label")

    try:
        scores = {
            "paper_reproduction": _score_dict(
                gold_label=gold_label,
                predicted_label=predicted_label,
                scorer_mode=GAN_PAPER_REPRODUCTION_SCORER,
            ),
            "canonical": _score_dict(
                gold_label=gold_label,
                predicted_label=predicted_label,
                scorer_mode=GAN_CANONICAL_SCORER,
            ),
        }
    except ValueError as exc:
        return {
            **_invalid_prediction_row("invalid_predicted_label"),
            "predicted_label": predicted_label,
            "invalid_reason": str(exc),
            "metadata": _option_metadata(prediction),
        }

    return {
        "status": "scored",
        "predicted_label": predicted_label,
        "raw_value": predicted_value.raw_value,
        "normalized_value": predicted_value.normalized_value,
        "evidence_count": len(predicted_value.evidence),
        "quality_flags": list(predicted_value.quality_flags),
        "scores": scores,
        "metadata": _option_metadata(prediction),
    }


def _invalid_prediction_row(reason: str) -> dict[str, Any]:
    return {
        "status": "invalid",
        "invalid_reason": reason,
        "predicted_label": None,
        "raw_value": None,
        "normalized_value": None,
        "evidence_count": 0,
        "quality_flags": [],
        "scores": {
            "paper_reproduction": _empty_score_dict(),
            "canonical": _empty_score_dict(),
        },
        "metadata": {},
    }


def _option_metadata(prediction: DocumentPrediction) -> dict[str, Any]:
    metadata = prediction.metadata
    selected = metadata.get("selected_answer_option")
    if not isinstance(selected, dict):
        selected = {}
    answer_options = metadata.get("multiple_answer_options")
    rejected_options = metadata.get("rejected_multiple_answer_options")
    temporal_candidate_labels = metadata.get("temporal_candidate_labels")
    return {
        "temporal_candidate_count": _len_or_zero(temporal_candidate_labels),
        "temporal_candidate_labels": temporal_candidate_labels or [],
        "answer_option_count": _len_or_zero(answer_options),
        "rejected_answer_option_count": _len_or_zero(rejected_options),
        "selected_answer_source": selected.get("source"),
        "selected_answer_status": selected.get("status"),
        "selected_answer_ambiguity_flags": selected.get("ambiguity_flags") or [],
        "verifier_reason": metadata.get("verifier_reason"),
    }


def _len_or_zero(value: object) -> int:
    return len(value) if isinstance(value, list) else 0


def _score_dict(
    *,
    gold_label: str,
    predicted_label: str,
    scorer_mode: str,
) -> dict[str, Any]:
    score = score_gan_frequency_prediction(
        gold_label=gold_label,
        predicted_label=predicted_label,
        scorer_mode=scorer_mode,
    )
    return {
        "normalized_label_match": score.exact_normalized_match,
        "monthly_frequency_match": score.monthly_frequency_match,
        "purist_category_match": score.purist_category_match,
        "pragmatic_category_match": score.pragmatic_category_match,
        "normalized_gold_label": score.normalized_gold_label,
        "normalized_predicted_label": score.normalized_predicted_label,
        "gold_monthly_frequency": score.gold_monthly_frequency,
        "predicted_monthly_frequency": score.predicted_monthly_frequency,
        "gold_purist_category": score.gold_purist_category,
        "predicted_purist_category": score.predicted_purist_category,
        "gold_pragmatic_category": score.gold_pragmatic_category,
        "predicted_pragmatic_category": score.predicted_pragmatic_category,
    }


def _empty_score_dict() -> dict[str, Any]:
    return {
        "normalized_label_match": False,
        "monthly_frequency_match": False,
        "purist_category_match": False,
        "pragmatic_category_match": False,
        "normalized_gold_label": None,
        "normalized_predicted_label": None,
        "gold_monthly_frequency": None,
        "predicted_monthly_frequency": None,
        "gold_purist_category": None,
        "predicted_purist_category": None,
        "gold_pragmatic_category": None,
        "predicted_pragmatic_category": None,
    }


def _arm_metadata(arm: ArmRun) -> dict[str, Any]:
    metadata = arm.run_metadata
    return {
        "arm_id": arm.arm_id,
        "run_id": metadata.get("run_id", arm.run_dir.name),
        "run_dir": str(arm.run_dir),
        "experiment_id": arm.config.get("experiment_id"),
        "program_variant": metadata.get("program_variant"),
        "prompt_version": metadata.get("metadata", {}).get("prompt_version")
        or metadata.get("prompt_version"),
        "model_provider": metadata.get("model_provider"),
        "model_name": metadata.get("model_name"),
        "runtime": arm.runtime,
    }


def _summary(rows: list[dict[str, Any]], arms: list[ArmRun]) -> dict[str, Any]:
    arm_summaries = {
        arm.arm_id: _arm_summary(rows, arm.arm_id)
        for arm in arms
    }
    return {
        "arms": arm_summaries,
        "best_by_metric": _best_by_metric(arm_summaries),
        "differential_records": _differential_records(rows, arms),
    }


def _arm_summary(rows: list[dict[str, Any]], arm_id: str) -> dict[str, Any]:
    total = len(rows)
    arm_rows = [row["arms"][arm_id] for row in rows]
    valid = [row for row in arm_rows if row["status"] == "scored"]
    return {
        "records": total,
        "valid_predictions": len(valid),
        "invalid_predictions": total - len(valid),
        "invalid_reason_counts": dict(
            Counter(row["invalid_reason"] for row in arm_rows if row["status"] != "scored")
        ),
        "paper_reproduction": _metric_summary(arm_rows, "paper_reproduction"),
        "canonical": _metric_summary(arm_rows, "canonical"),
        "option_diagnostics": _option_summary(arm_rows),
    }


def _metric_summary(arm_rows: list[dict[str, Any]], scorer_key: str) -> dict[str, Any]:
    total = len(arm_rows)
    return {
        "normalized_label_accuracy": _rate(
            row["scores"][scorer_key]["normalized_label_match"] for row in arm_rows
        ),
        "monthly_frequency_accuracy": _rate(
            row["scores"][scorer_key]["monthly_frequency_match"] for row in arm_rows
        ),
        "purist_category_accuracy": _rate(
            row["scores"][scorer_key]["purist_category_match"] for row in arm_rows
        ),
        "pragmatic_category_accuracy": _rate(
            row["scores"][scorer_key]["pragmatic_category_match"] for row in arm_rows
        ),
        "denominator": total,
    }


def _option_summary(arm_rows: list[dict[str, Any]]) -> dict[str, Any]:
    metadata_rows = [row.get("metadata", {}) for row in arm_rows]
    return {
        "mean_temporal_candidates": _mean(
            row.get("temporal_candidate_count", 0) for row in metadata_rows
        ),
        "mean_answer_options": _mean(
            row.get("answer_option_count", 0) for row in metadata_rows
        ),
        "mean_rejected_answer_options": _mean(
            row.get("rejected_answer_option_count", 0) for row in metadata_rows
        ),
        "selected_answer_source_counts": dict(
            Counter(
                str(row.get("selected_answer_source"))
                for row in metadata_rows
                if row.get("selected_answer_source") is not None
            )
        ),
        "selected_answer_status_counts": dict(
            Counter(
                str(row.get("selected_answer_status"))
                for row in metadata_rows
                if row.get("selected_answer_status") is not None
            )
        ),
    }


def _best_by_metric(arm_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, dict[str, Any]] = {}
    metric_names = (
        "normalized_label_accuracy",
        "monthly_frequency_accuracy",
        "purist_category_accuracy",
        "pragmatic_category_accuracy",
    )
    for scorer_key in ("paper_reproduction", "canonical"):
        result[scorer_key] = {}
        for metric_name in metric_names:
            scores = {
                arm_id: summary[scorer_key][metric_name]
                for arm_id, summary in arm_summaries.items()
            }
            best = max(scores.values()) if scores else 0.0
            result[scorer_key][metric_name] = {
                "accuracy": best,
                "arm_ids": [
                    arm_id for arm_id, accuracy in scores.items() if accuracy == best
                ],
            }
    return result


def _differential_records(
    rows: list[dict[str, Any]],
    arms: list[ArmRun],
) -> list[dict[str, Any]]:
    differential: list[dict[str, Any]] = []
    arm_ids = [arm.arm_id for arm in arms]
    for row in rows:
        matches = {
            arm_id: row["arms"][arm_id]["scores"]["canonical"]["monthly_frequency_match"]
            for arm_id in arm_ids
        }
        if len(set(matches.values())) <= 1:
            continue
        differential.append(
            {
                "record_id": row["record_id"],
                "gold_label": row["gold_label"],
                "predicted_labels": {
                    arm_id: row["arms"][arm_id]["predicted_label"]
                    for arm_id in arm_ids
                },
                "canonical_monthly_matches": matches,
            }
        )
    return differential


def _first_config_value(arms: list[ArmRun], key: str) -> Any:
    for arm in arms:
        value = arm.config.get(key)
        if value is not None:
            return value
    return None


def _rate(values: Any) -> float:
    observations = list(values)
    if not observations:
        return 0.0
    return sum(bool(value) for value in observations) / len(observations)


def _mean(values: Any) -> float:
    observations = list(values)
    if not observations:
        return 0.0
    return sum(float(value) for value in observations) / len(observations)


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _counter_label(counter: Mapping[str, Any]) -> str:
    if not counter:
        return ""
    return ", ".join(f"`{key}`={value}" for key, value in sorted(counter.items()))


def _arm_id_list(arm_ids: list[str]) -> str:
    return ", ".join(f"`{arm_id}`" for arm_id in arm_ids)
