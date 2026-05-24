"""Shared Explorer model-catalog schema helpers for ExECT and Gan builders."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "2026-05-24"
ARTIFACT_CLASS = "explorer_model_catalog"

DEFAULT_METRIC_LABELS = {
    "micro_f1": "Micro F1",
    "micro_precision": "Precision",
    "micro_recall": "Recall",
    "evidence_support": "Evidence",
}

GAN_METRIC_LABELS = {
    "micro_f1": "Monthly accuracy",
    "micro_precision": "Purist category",
    "micro_recall": "Pragmatic category",
    "evidence_support": "Evidence",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: float | None) -> float | None:
    return None if value is None else round(value * 100, 1)


def build_pipeline_step(
    *,
    step_id: str,
    field: str,
    raw_value: Any,
    normalized_value: Any,
    temporality: Any,
    negation: Any,
    quality_flags: list[str] | None,
    evidence: list[dict[str, Any]] | None,
    deterministic_label: str,
    deterministic_output: Any,
    metadata: dict[str, Any] | None,
    outcome: str,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "field": field,
        "raw_value": raw_value,
        "normalized_value": normalized_value,
        "temporality": temporality,
        "negation": negation,
        "quality_flags": quality_flags or [],
        "evidence": evidence or [],
        "deterministic_step": {
            "label": deterministic_label,
            "output": deterministic_output,
            "metadata": metadata or {},
        },
        "outcome": outcome,
    }


def build_document(
    document_id: str,
    quality_flags: list[str] | None,
    pipeline: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "quality_flags": quality_flags or [],
        "pipeline": pipeline,
    }


def build_run_metrics(
    *,
    micro_f1: float | None,
    micro_precision: float | None,
    micro_recall: float | None,
    field_f1: dict[str, float | None],
    evidence_support: float | None,
    seconds_per_record: float,
    evaluated_records: int | None,
) -> dict[str, Any]:
    return {
        "micro_f1": micro_f1,
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "field_f1": field_f1,
        "evidence_support": evidence_support,
        "seconds_per_record": seconds_per_record,
        "evaluated_records": evaluated_records,
    }


def build_run_entry(
    *,
    task: str,
    run_id: str,
    model_label: str,
    evidence_status: str,
    best: bool,
    run_dir: str,
    schema_level: str | None,
    scorer_mode: str | None,
    program_variant: str | None,
    prompt_version: str | None,
    metrics: dict[str, Any],
    documents: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "task": task,
        "run_id": run_id,
        "model_label": model_label,
        "evidence_status": evidence_status,
        "best": best,
        "run_dir": run_dir,
        "schema_level": schema_level,
        "scorer_mode": scorer_mode,
        "program_variant": program_variant,
        "prompt_version": prompt_version,
        "metrics": metrics,
        "documents": documents,
    }


def build_task_entry(
    task_id: str,
    label: str,
    scope: str,
    default_run_id: str,
    run_ids: list[str],
) -> dict[str, Any]:
    return {
        "id": task_id,
        "label": label,
        "scope": scope,
        "default_run_id": default_run_id,
        "run_ids": run_ids,
    }


def build_tasks_from_runs(
    task_specs: dict[str, tuple[str, str]],
    runs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for task_id, (label, scope) in task_specs.items():
        task_runs = [run for run in runs if run["task"] == task_id]
        if not task_runs:
            continue
        default_run = next((run for run in task_runs if run["best"]), task_runs[0])
        tasks.append(
            build_task_entry(
                task_id=task_id,
                label=label,
                scope=scope,
                default_run_id=default_run["run_id"],
                run_ids=[run["run_id"] for run in task_runs],
            )
        )
    return tasks


def build_catalog(
    *,
    dataset: str,
    source_note: str,
    tasks: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    metric_labels: dict[str, str] | None = None,
    source_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source: dict[str, Any] = {"note": source_note}
    if source_extra:
        source.update(source_extra)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_class": ARTIFACT_CLASS,
        "dataset": dataset,
        "metric_labels": metric_labels or DEFAULT_METRIC_LABELS,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source,
        "tasks": tasks,
        "runs": runs,
    }


def validate_catalog_envelope(catalog: dict[str, Any]) -> None:
    required_top = {
        "schema_version",
        "artifact_class",
        "dataset",
        "metric_labels",
        "generated_at_utc",
        "source",
        "tasks",
        "runs",
    }
    missing = required_top - set(catalog)
    if missing:
        raise ValueError(f"catalog missing required keys: {sorted(missing)}")
    if catalog["artifact_class"] != ARTIFACT_CLASS:
        raise ValueError(f"unexpected artifact_class: {catalog['artifact_class']}")
    if not catalog["tasks"]:
        raise ValueError("catalog must include at least one task")
    if not catalog["runs"]:
        raise ValueError("catalog must include at least one run")
    for run in catalog["runs"]:
        for key in ("task", "run_id", "model_label", "metrics", "documents"):
            if key not in run:
                raise ValueError(f"run {run.get('run_id')} missing {key}")
