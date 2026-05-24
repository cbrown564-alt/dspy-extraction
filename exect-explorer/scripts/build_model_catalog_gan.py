#!/usr/bin/env python3
"""Build the static Gan Explorer model catalog from local run artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "exect-explorer" / "public" / "data" / "model_catalog_gan.json"

RUN_SPECS = [
    ("Gan_S0", "gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z", "GPT-4.1-mini candidate-builder gap v1", "paper_frozen", True),
    ("Gan_S0", "gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z", "Qwen3.6:35b candidate-builder gap v1", "paper_frozen", False),
]

TASK_SCOPES = {
    "Gan_S0": "seizure frequency normalized extraction from clinical text (Gan 2026 dataset)",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: float | None) -> float | None:
    return None if value is None else round(value * 100, 1)


def mismatch_map(metrics: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for mismatch in metrics.get("errors", {}).get("monthly_frequency_mismatches", []):
        record_id = mismatch.get("record_id")
        if record_id:
            out.add(str(record_id))
    return out


def evidence_error_keys(metrics: dict[str, Any], document_id: str) -> set[str]:
    keys: set[str] = set()
    for error in metrics.get("errors", {}).get("evidence_support_errors", []):
        doc_id = error.get("record_id") or error.get("document_id")
        if doc_id == document_id:
            keys.add(str(error.get("raw_value")))
    return keys


def pipeline_steps(prediction: dict[str, Any], metrics: dict[str, Any]) -> list[dict[str, Any]]:
    document_id = str(prediction.get("document_id"))
    mismatches = mismatch_map(metrics)
    evidence_errors = evidence_error_keys(metrics, document_id)
    steps = []
    for idx, value in enumerate(prediction.get("values", [])):
        field = str(value.get("field_name"))
        raw_value = value.get("raw_value")
        normalized_value = value.get("normalized_value")
        outcome = "matched"
        
        if document_id in mismatches:
            outcome = "false_positive"
        if str(raw_value) in evidence_errors:
            outcome = "evidence_issue"
            
        steps.append(
            {
                "id": f"{document_id}.{idx}.{field}",
                "field": field,
                "raw_value": raw_value,
                "normalized_value": normalized_value,
                "temporality": value.get("temporality"),
                "negation": value.get("negation"),
                "quality_flags": value.get("quality_flags", []),
                "evidence": value.get("evidence") or [],
                "deterministic_step": {
                    "label": "normalization bridge",
                    "output": normalized_value,
                    "metadata": value.get("metadata", {}),
                },
                "outcome": outcome,
            }
        )
    return steps


def build_run(task: str, run_id: str, model_label: str, evidence_status: str, best: bool) -> dict[str, Any]:
    run_dir = ROOT / "runs" / run_id
    metrics = read_json(run_dir / "metrics.json")
    config = read_json(run_dir / "config.json")
    predictions = read_json(run_dir / "predictions.json")
    benchmark = metrics.get("benchmark_metrics", {})
    diagnostic = metrics.get("diagnostic_metrics", {})
    runtime = metrics.get("runtime", {})
    documents = {
        str(prediction.get("document_id")): {
            "document_id": str(prediction.get("document_id")),
            "quality_flags": prediction.get("quality_flags", []),
            "pipeline": pipeline_steps(prediction, metrics),
        }
        for prediction in predictions.get("predictions", [])
    }
    return {
        "task": task,
        "run_id": run_id,
        "model_label": model_label,
        "evidence_status": evidence_status,
        "best": best,
        "run_dir": str(run_dir.relative_to(ROOT)),
        "schema_level": config.get("schema_level") or metrics.get("schema_level") or "gan_s0",
        "scorer_mode": config.get("scorer_mode") or metrics.get("scorer") or "gan_frequency_deterministic_v1",
        "program_variant": config.get("program_variant"),
        "prompt_version": config.get("prompt_version"),
        "metrics": {
            "micro_f1": pct(benchmark.get("monthly_frequency_accuracy")),
            "micro_precision": pct(benchmark.get("purist_category_accuracy")),
            "micro_recall": pct(benchmark.get("pragmatic_category_accuracy")),
            "field_f1": {"seizure_frequency": pct(benchmark.get("monthly_frequency_accuracy"))},
            "evidence_support": pct(diagnostic.get("evidence_quote_support_rate")),
            "seconds_per_record": round(runtime.get("prediction_seconds_per_record", 0), 3),
            "evaluated_records": metrics.get("counts", {}).get("evaluated_records"),
        },
        "documents": documents,
    }


def build_catalog() -> dict[str, Any]:
    runs = [build_run(*spec) for spec in RUN_SPECS]
    tasks = []
    for task_id in ["Gan_S0"]:
        task_runs = [run for run in runs if run["task"] == task_id]
        default_run = next((run for run in task_runs if run["best"]), task_runs[0])
        tasks.append(
            {
                "id": task_id,
                "label": "Gan Frequency",
                "scope": TASK_SCOPES[task_id],
                "default_run_id": default_run["run_id"],
                "run_ids": [run["run_id"] for run in task_runs],
            }
        )
    return {
        "schema_version": "2026-05-24",
        "artifact_class": "gan_explorer_model_catalog",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": {
            "note": "Static viewer bundle generated from local runs/* artifacts for Gan 2026.",
        },
        "tasks": tasks,
        "runs": runs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    catalog = build_catalog()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(catalog['runs'])} runs to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
