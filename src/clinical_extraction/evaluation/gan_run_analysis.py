"""Helpers for Gan frequency run analysis scope selection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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


def analysis_record_ids(
    *,
    run_dir: Path,
    split_file: Path,
    split_name: str,
    predictions_by_id: dict[str, Any],
) -> tuple[list[str], str]:
    config_path = run_dir / "config.json"
    split_ids = load_split_ids(split_file, split_name)
    split_id_set = set(split_ids)

    if config_path.exists():
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
