#!/usr/bin/env python3
"""Build the static ExECT Explorer model catalog from local run artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "exect-explorer" / "public" / "data" / "model_catalog.json"

RUN_SPECS = [
    ("S1", "exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z", "GPT-4.1-mini", "paper_frozen", True),
    ("S1", "exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z", "Qwen3.6:35b", "paper_frozen", False),
    ("S2", "exect_s2_validation_full_gpt4_1_mini_20260519T231223Z", "GPT-4.1-mini", "paper_frozen", False),
    ("S2", "exect_s2_validation_full_qwen35b_ollama_20260520T073552Z", "Qwen3.6:35b", "paper_frozen", True),
    ("S3", "exect_s3_validation_full_gpt4_1_mini_20260519T235439Z", "GPT-4.1-mini", "paper_frozen", False),
    ("S3", "exect_s3_validation_full_qwen35b_ollama_20260520T092244Z", "Qwen3.6:35b", "paper_frozen", True),
    ("S4", "exect_s4_validation_full_gpt4_1_mini_20260520T071248Z", "GPT-4.1-mini", "paper_frozen", False),
    ("S4", "exect_s4_validation_full_qwen35b_ollama_20260520T160914Z", "Qwen3.6:35b", "paper_frozen", True),
    ("S5", "exect_s5_validation_full_gpt4_1_mini_20260524T142812Z", "GPT-4.1-mini baseline", "workspace_candidate", False),
    ("S5", "exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z", "GPT-4.1-mini frequency vocab", "workspace_candidate", True),
]

TASK_SCOPES = {
    "S1": "diagnosis, seizure type, annotated medication",
    "S2": "S1 plus investigation and comorbidity",
    "S3": "S2 plus birth history, onset, epilepsy cause, when diagnosed",
    "S4": "S3 plus seizure frequency and medication temporality",
    "S5": "core S5 candidate surface with frequency vocabulary experiments",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: float | None) -> float | None:
    return None if value is None else round(value * 100, 1)


def mismatch_map(metrics: dict[str, Any], document_id: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for mismatch in metrics.get("errors", {}).get("field_family_mismatches", []):
        if mismatch.get("document_id") == document_id:
            out[str(mismatch.get("field_family"))] = mismatch
    return out


def evidence_error_keys(metrics: dict[str, Any], document_id: str) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for error in metrics.get("errors", {}).get("evidence_support_errors", []):
        if error.get("document_id") == document_id:
            keys.add((str(error.get("field_name")), str(error.get("raw_value"))))
    return keys


def pipeline_steps(prediction: dict[str, Any], metrics: dict[str, Any]) -> list[dict[str, Any]]:
    document_id = str(prediction.get("document_id"))
    mismatches = mismatch_map(metrics, document_id)
    evidence_errors = evidence_error_keys(metrics, document_id)
    steps = []
    for idx, value in enumerate(prediction.get("values", [])):
        field = str(value.get("field_name"))
        raw_value = value.get("raw_value")
        normalized_value = value.get("normalized_value")
        outcome = "matched"
        family = mismatches.get(field)
        if family:
            fp = {str(item).lower() for item in family.get("false_positives", [])}
            fn = {str(item).lower() for item in family.get("false_negatives", [])}
            normalized = str(normalized_value or raw_value or "").lower()
            outcome = "false_positive" if normalized in fp else "miss_or_partial"
            if normalized in fn:
                outcome = "false_negative"
        if (field, str(raw_value)) in evidence_errors:
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
                    "label": "policy bridge / scorer normalization",
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
        "schema_level": config.get("schema_level") or metrics.get("schema_level"),
        "scorer_mode": config.get("scorer_mode") or metrics.get("scorer"),
        "program_variant": config.get("program_variant"),
        "prompt_version": config.get("prompt_version"),
        "metrics": {
            "micro_f1": pct(benchmark.get("micro_f1")),
            "micro_precision": pct(benchmark.get("micro_precision")),
            "micro_recall": pct(benchmark.get("micro_recall")),
            "field_f1": {k: pct(v) for k, v in benchmark.get("field_f1", {}).items()},
            "evidence_support": pct(diagnostic.get("evidence_quote_support_rate")),
            "seconds_per_record": round(runtime.get("prediction_seconds_per_record", 0), 3),
            "evaluated_records": metrics.get("counts", {}).get("evaluated_records"),
        },
        "documents": documents,
    }


def build_catalog() -> dict[str, Any]:
    runs = [build_run(*spec) for spec in RUN_SPECS]
    tasks = []
    for task_id in ["S1", "S2", "S3", "S4", "S5"]:
        task_runs = [run for run in runs if run["task"] == task_id]
        default_run = next((run for run in task_runs if run["best"]), task_runs[0])
        tasks.append(
            {
                "id": task_id,
                "label": f"ExECT {task_id}",
                "scope": TASK_SCOPES[task_id],
                "default_run_id": default_run["run_id"],
                "run_ids": [run["run_id"] for run in task_runs],
            }
        )
    return {
        "schema_version": "2026-05-24",
        "artifact_class": "exect_explorer_model_catalog",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": {
            "note": "Static viewer bundle generated from local runs/* artifacts; Cursor SDK prompt rehearsal was not used as evidence.",
            "cursor_sdk_prompt_rehearsal": "docs/experiments/cursor_sdk_drafts/20260524T181503Z_inspection_draft_prompt_rehearsal.md",
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
