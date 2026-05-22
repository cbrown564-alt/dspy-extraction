"""Helpers for Gan frequency run analysis scope selection."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from clinical_extraction.gan.frequency import pragmatic_category, purist_category
from clinical_extraction.gan.scoring import score_gan_frequency_prediction
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates,
    temporal_candidate_to_dict,
)
from clinical_extraction.evaluation.gan_failure_taxonomy import (
    classify_gan_frequency_failure,
    failure_action_tier,
)
from clinical_extraction.schemas import (
    DocumentPrediction,
    ExtractedValue,
    GanRecord,
    PredictionSet,
)

GAN_FREQUENCY_FIELD = "seizure_frequency_number"

GAN_RECORD_REPORT_FIELDNAMES = [
    "record_id",
    "status",
    "predicted_label",
    "gold_label",
    "normalized_predicted_label",
    "normalized_gold_label",
    "normalized_label_exact_match",
    "monthly_frequency_match",
    "purist_category_match",
    "pragmatic_category_match",
    "predicted_monthly_frequency",
    "gold_monthly_frequency",
    "predicted_purist_category",
    "gold_purist_category",
    "predicted_pragmatic_category",
    "gold_pragmatic_category",
    "evidence_citation",
    "gold_evidence",
    "prediction_quality_flags",
    "gold_record_flags",
    "failure_class",
    "failure_tier",
    "invalid_reason",
    "full_text",
]


def load_split_ids(split_file: Path, split_name: str) -> list[str]:
    payload = json.loads(split_file.read_text(encoding="utf-8"))
    if ":" in split_name:
        name, split = split_name.split(":", 1)
        if payload.get("name") != name:
            raise ValueError(f"split file name {payload.get('name')!r} != {name!r}")
        return list(payload[split])
    if split_name not in payload:
        raise ValueError(f"split {split_name!r} not found in {split_file}")
    return list(payload[split_name])


def load_record_ids_filter(path: Path) -> list[str]:
    """Load record IDs for post-hoc analysis scope from a JSON fixture."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload.get("record_ids"), list):
        return [str(record_id) for record_id in payload["record_ids"]]
    records = payload.get("records")
    if isinstance(records, list) and records:
        if isinstance(records[0], dict) and "record_id" in records[0]:
            return [str(entry["record_id"]) for entry in records]
        return [str(record_id) for record_id in records]
    raise ValueError(
        f"{path} must define record_ids or a non-empty records list with record_id entries."
    )


def build_gan_record_report_rows(
    *,
    prediction_set: PredictionSet,
    gold_by_id: dict[str, GanRecord],
    record_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Build reproducible record-level Gan frequency report rows.

    The row schema is intentionally CSV-oriented and preserves the primary audit
    distinctions: raw label, normalized label, benchmark-facing monthly/category
    matches, diagnostic evidence, failure class, and full source note text.
    """

    predictions_by_id = {
        prediction.document_id: prediction
        for prediction in prediction_set.predictions
    }
    if record_ids is None:
        ordered_record_ids = [
            prediction.document_id for prediction in prediction_set.predictions
        ]
    else:
        ordered_record_ids = list(record_ids)

    rows: list[dict[str, Any]] = []
    for record_id in ordered_record_ids:
        if record_id not in gold_by_id:
            raise ValueError(f"prediction record_id not found in Gan gold: {record_id}")
        gold = gold_by_id[record_id]
        prediction = predictions_by_id.get(record_id)
        if prediction is None:
            rows.append(_missing_gan_record_report_row(gold))
            continue

        rows.append(_prediction_gan_record_report_row(prediction, gold))

    return rows


def export_gan_record_report_csv(
    *,
    prediction_set: PredictionSet,
    gold_by_id: dict[str, GanRecord],
    output_path: Path,
    record_ids: list[str] | None = None,
) -> Path:
    """Write the reproducible Gan record-level report CSV and return its path."""

    rows = build_gan_record_report_rows(
        prediction_set=prediction_set,
        gold_by_id=gold_by_id,
        record_ids=record_ids,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GAN_RECORD_REPORT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def export_gan_run_record_report_csv(
    *,
    run_dir: Path,
    gold_by_id: dict[str, GanRecord],
    output_path: Path | None = None,
    record_ids: list[str] | None = None,
) -> Path:
    """Export a record-level CSV report from a stored Gan run directory."""

    prediction_set = PredictionSet.model_validate_json(
        (run_dir / "predictions.json").read_text(encoding="utf-8")
    )
    destination = output_path or run_dir / f"{run_dir.name}_record_report.csv"
    return export_gan_record_report_csv(
        prediction_set=prediction_set,
        gold_by_id=gold_by_id,
        output_path=destination,
        record_ids=record_ids,
    )


def _prediction_gan_record_report_row(
    prediction: DocumentPrediction,
    gold: GanRecord,
) -> dict[str, Any]:
    predicted_value = _gan_frequency_value(prediction)
    if predicted_value is None:
        return _invalid_gan_record_report_row(
            gold=gold,
            predicted_label="",
            predicted_value=None,
            failure_class="schema_missing_field",
            invalid_reason=f"missing {GAN_FREQUENCY_FIELD} prediction",
        )

    predicted_label = _prediction_label(predicted_value)
    if predicted_label is None:
        return _invalid_gan_record_report_row(
            gold=gold,
            predicted_label="",
            predicted_value=predicted_value,
            failure_class="abstention_or_missing_value",
            invalid_reason=f"missing {GAN_FREQUENCY_FIELD} label value",
        )

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold.gold_label,
            predicted_label=predicted_label,
        )
    except ValueError as exc:
        return _invalid_gan_record_report_row(
            gold=gold,
            predicted_label=predicted_label,
            predicted_value=predicted_value,
            failure_class="invalid_predicted_label",
            invalid_reason=str(exc),
        )

    tax_row = {
        "status": "scored",
        "failure_class": "",
        "normalized_gold_label": score.normalized_gold_label,
        "normalized_predicted_label": score.normalized_predicted_label,
        "normalized_exact_match": score.exact_normalized_match,
        "monthly_match": score.monthly_frequency_match,
        "purist_match": score.purist_category_match,
        "pragmatic_match": score.pragmatic_category_match,
        "gold_pragmatic_category": score.gold_pragmatic_category,
        "predicted_pragmatic_category": score.predicted_pragmatic_category,
    }
    failure_class = classify_gan_frequency_failure(tax_row)
    return {
        **_base_gan_record_report_row(gold),
        "status": "scored",
        "predicted_label": predicted_value.raw_value or predicted_label,
        "normalized_predicted_label": score.normalized_predicted_label,
        "normalized_gold_label": score.normalized_gold_label,
        "normalized_label_exact_match": _yn(score.exact_normalized_match),
        "monthly_frequency_match": _yn(score.monthly_frequency_match),
        "purist_category_match": _yn(score.purist_category_match),
        "pragmatic_category_match": _yn(score.pragmatic_category_match),
        "predicted_monthly_frequency": score.predicted_monthly_frequency,
        "gold_monthly_frequency": score.gold_monthly_frequency,
        "predicted_purist_category": score.predicted_purist_category,
        "gold_purist_category": score.gold_purist_category,
        "predicted_pragmatic_category": score.predicted_pragmatic_category,
        "gold_pragmatic_category": score.gold_pragmatic_category,
        "evidence_citation": _evidence_citation(predicted_value.evidence),
        "prediction_quality_flags": ";".join(predicted_value.quality_flags),
        "failure_class": failure_class,
        "failure_tier": failure_action_tier(failure_class),
    }


def _base_gan_record_report_row(gold: GanRecord) -> dict[str, Any]:
    return {
        "record_id": gold.record_id,
        "status": "",
        "predicted_label": "",
        "gold_label": gold.gold_label,
        "normalized_predicted_label": "",
        "normalized_gold_label": "",
        "normalized_label_exact_match": "",
        "monthly_frequency_match": "",
        "purist_category_match": "",
        "pragmatic_category_match": "",
        "predicted_monthly_frequency": "",
        "gold_monthly_frequency": "",
        "predicted_purist_category": "",
        "gold_purist_category": purist_category(gold.gold_label),
        "predicted_pragmatic_category": "",
        "gold_pragmatic_category": pragmatic_category(gold.gold_label),
        "evidence_citation": "",
        "gold_evidence": gold.gold_evidence or "",
        "prediction_quality_flags": "",
        "gold_record_flags": ";".join(gold.flags),
        "failure_class": "",
        "failure_tier": "",
        "invalid_reason": "",
        "full_text": gold.note_text,
    }


def _missing_gan_record_report_row(gold: GanRecord) -> dict[str, Any]:
    failure_class = "missing_prediction"
    return {
        **_base_gan_record_report_row(gold),
        "status": "missing_prediction",
        "failure_class": failure_class,
        "failure_tier": failure_action_tier(failure_class),
        "invalid_reason": "gold record has no prediction",
    }


def _invalid_gan_record_report_row(
    *,
    gold: GanRecord,
    predicted_label: str,
    predicted_value: ExtractedValue | None,
    failure_class: str,
    invalid_reason: str,
) -> dict[str, Any]:
    return {
        **_base_gan_record_report_row(gold),
        "status": "invalid",
        "predicted_label": predicted_value.raw_value if predicted_value else predicted_label,
        "normalized_predicted_label": predicted_label,
        "evidence_citation": (
            _evidence_citation(predicted_value.evidence) if predicted_value else ""
        ),
        "prediction_quality_flags": (
            ";".join(predicted_value.quality_flags) if predicted_value else ""
        ),
        "failure_class": failure_class,
        "failure_tier": failure_action_tier(failure_class),
        "invalid_reason": invalid_reason,
    }


def _gan_frequency_value(prediction: DocumentPrediction) -> ExtractedValue | None:
    for value in prediction.values:
        if value.field_name == GAN_FREQUENCY_FIELD:
            return value
    return None


def _prediction_label(value: ExtractedValue) -> str | None:
    if isinstance(value.normalized_value, str):
        return value.normalized_value
    return value.raw_value


def _evidence_citation(evidence: list[Any]) -> str:
    if not evidence:
        return ""
    span = evidence[0]
    text = " ".join((span.text or "").split())
    return f"{span.start}-{span.end}: {text}"


def _yn(value: bool) -> str:
    return "Y" if value else "N"


def analysis_record_ids(
    *,
    run_dir: Path,
    split_file: Path,
    split_name: str,
    predictions_by_id: dict[str, Any],
    record_ids_override: list[str] | None = None,
) -> tuple[list[str], str]:
    config_path = run_dir / "config.json"
    split_ids = load_split_ids(split_file, split_name)
    split_id_set = set(split_ids)

    record_ids = record_ids_override
    if record_ids is None and config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        record_ids = config.get("record_ids")
    if record_ids:
        missing_from_split = [
            record_id for record_id in record_ids if record_id not in split_id_set
        ]
        if missing_from_split:
            raise ValueError(
                f"record_ids not in split {split_name!r}: {missing_from_split}"
            )
        return list(record_ids), "record_ids_filter"

    predicted_ids = [
        record_id for record_id in predictions_by_id if record_id in split_id_set
    ]
    if predicted_ids and len(predicted_ids) < len(split_ids):
        return sorted(predicted_ids), "predicted_subset"

    return split_ids, "full_split"


def _is_operational_failure(row: dict[str, Any]) -> bool:
    if row.get("status") != "scored":
        return True
    return row.get("failure_action_tier") == "benchmark_severe"


def _accuracies_valid_only(valid_rows: list[dict[str, Any]]) -> dict[str, float | None]:
    if not valid_rows:
        return {
            "normalized_label": None,
            "monthly_frequency": None,
            "purist_category": None,
            "pragmatic_category": None,
        }
    count = len(valid_rows)
    return {
        "normalized_label": sum(
            1 for row in valid_rows if row.get("normalized_exact_match")
        )
        / count,
        "monthly_frequency": sum(1 for row in valid_rows if row.get("monthly_match"))
        / count,
        "purist_category": sum(1 for row in valid_rows if row.get("purist_match"))
        / count,
        "pragmatic_category": sum(1 for row in valid_rows if row.get("pragmatic_match"))
        / count,
    }


def _stratum_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid_rows = [row for row in rows if row.get("status") == "scored"]
    operational_failures = sum(1 for row in rows if _is_operational_failure(row))
    all_records = len(rows)
    return {
        "all_records": all_records,
        "valid_scored": len(valid_rows),
        "invalid_or_missing": all_records - len(valid_rows),
        "operational_failures": operational_failures,
        "operational_failure_rate": (
            operational_failures / all_records if all_records else None
        ),
        "accuracies_valid_only": _accuracies_valid_only(valid_rows),
    }


def build_temporal_candidate_diagnostics(
    *,
    record_ids: list[str],
    gold_by_id: dict[str, GanRecord],
) -> dict[str, Any]:
    """Report whether deterministic candidates cover gold-relevant labels.

    Diagnostic only — does not change ``gan_frequency_deterministic_v1`` scoring.
    """

    records: list[dict[str, Any]] = []
    for record_id in record_ids:
        record = gold_by_id[record_id]
        candidates = build_temporal_frequency_candidates(record)
        candidate_labels = [candidate.canonical_label for candidate in candidates]
        records.append(
            {
                "record_id": record_id,
                "gold_label": record.gold_label,
                "candidate_labels": candidate_labels,
                "gold_in_candidates": record.gold_label in candidate_labels,
                "candidate_count": len(candidates),
                "candidates": [
                    temporal_candidate_to_dict(candidate) for candidate in candidates
                ],
            }
        )

    covered = sum(1 for row in records if row["gold_in_candidates"])
    total = len(records)
    return {
        "records": records,
        "gold_covered_count": covered,
        "gold_covered_rate": covered / total if total else None,
        "note": (
            "Diagnostic temporal-candidate coverage only; benchmark-facing metrics "
            "use gan_frequency_deterministic_v1 on model predictions."
        ),
    }


def build_gan_stratified_reporting(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize benchmark and operational metrics by dataset stratifiers."""
    by_pragmatic: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        category = row.get("gold_pragmatic_category") or "unknown_category"
        by_pragmatic.setdefault(category, []).append(row)

    return {
        "overall": _stratum_summary(rows),
        "hard_case": {
            "true": _stratum_summary([row for row in rows if row.get("hard_case")]),
            "false": _stratum_summary(
                [row for row in rows if not row.get("hard_case")]
            ),
        },
        "row_ok": {
            "true": _stratum_summary([row for row in rows if row.get("row_ok")]),
            "false": _stratum_summary(
                [row for row in rows if not row.get("row_ok")]
            ),
        },
        "gold_pragmatic_category": {
            category: _stratum_summary(category_rows)
            for category, category_rows in sorted(by_pragmatic.items())
        },
    }
