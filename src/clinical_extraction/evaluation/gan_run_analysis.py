"""Helpers for Gan frequency run analysis scope selection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates,
    temporal_candidate_to_dict,
)
from clinical_extraction.schemas import GanRecord


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
