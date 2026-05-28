#!/usr/bin/env python3
"""Build the static Gan Explorer model catalog from local run artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from catalog_shared import (  # noqa: E402
    GAN_METRIC_LABELS,
    build_catalog,
    build_document,
    build_pipeline_step,
    build_run_entry,
    build_run_metrics,
    build_tasks_from_runs,
    pct,
    read_json,
    validate_catalog_envelope,
)
from clinical_extraction.paths import resolve_run_directory  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "exect-explorer" / "public" / "data" / "model_catalog_gan.json"


def scan_runs_for_gan() -> list[tuple[str, str, str, str, bool]]:
    """Scan the runs/ directory dynamically to build specs for Gan 2026."""
    runs_dir = ROOT / "runs"
    if not runs_dir.exists():
        return []
    
    FROZEN_RUNS = {
        "gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z",
        "gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z",
    }
    
    KNOWN_BEST = {
        "gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z",
    }

    import re
    timestamp_pattern = re.compile(r"(\d{8}T\d{6}Z)")

    run_candidates = []
    for run_path in runs_dir.iterdir():
        if not run_path.is_dir():
            continue
        metrics_file = run_path / "metrics.json"
        config_file = run_path / "config.json"
        predictions_file = run_path / "predictions.json"
        if not (metrics_file.exists() and config_file.exists() and predictions_file.exists()):
            continue
        try:
            metrics = read_json(metrics_file)
            config = read_json(config_file)
        except Exception:
            continue
            
        if metrics.get("dataset") != "gan_2026":
            continue
            
        run_candidates.append((run_path.name, config, metrics))

    def get_timestamp(run_id: str) -> str:
        m = timestamp_pattern.search(run_id)
        return m.group(1) if m else ""

    run_candidates.sort(key=lambda x: get_timestamp(x[0]), reverse=True)

    frozen_runs = []
    candidate_runs = []
    
    for run_id, config, metrics in run_candidates:
        if run_id in FROZEN_RUNS:
            frozen_runs.append((run_id, config, metrics))
        else:
            candidate_runs.append((run_id, config, metrics))
            
    # Keep up to 5 latest candidates
    candidate_runs = candidate_runs[:5]
    kept_runs = frozen_runs + candidate_runs

    best_run_id = None
    for run_id, _, _ in kept_runs:
        if run_id in KNOWN_BEST:
            best_run_id = run_id
            break
            
    if not best_run_id and kept_runs:
        def get_acc(item):
            bm = item[2].get("benchmark_metrics", {})
            return bm.get("monthly_frequency_accuracy") or 0.0
        sorted_by_perf = sorted(kept_runs, key=lambda x: (get_acc(x), x[0]), reverse=True)
        best_run_id = sorted_by_perf[0][0]

    final_specs = []
    for run_id, config, metrics in kept_runs:
        model_path = str(config.get("model_config_path", "")).lower()
        run_id_lower = run_id.lower()
        if "gpt4" in model_path or "gpt-4" in model_path or "gpt4" in run_id_lower or "gpt-4" in run_id_lower:
            model_label = "GPT-4.1-mini"
        elif "qwen" in model_path or "qwen" in run_id_lower:
            model_label = "Qwen3.6:35b"
        else:
            model_label = str(config.get("model_config_path", "")).split("/")[-1].split("\\")[-1].replace(".json", "").replace("_", " ").title()
            if "gpt4" in model_label.lower() or "gpt-4" in model_label.lower():
                model_label = "GPT-4.1-mini"
            elif "qwen" in model_label.lower():
                model_label = "Qwen3.6:35b"
            
        evidence_status = "paper_frozen" if run_id in FROZEN_RUNS else "workspace_candidate"
        best = (run_id == best_run_id)
        final_specs.append(("Gan_S0", run_id, model_label, evidence_status, best))
        
    final_specs.sort(key=lambda x: (0 if x[4] else 1, get_timestamp(x[1])), reverse=True)
    return final_specs


TASK_SPECS = {
    "Gan_S0": (
        "Gan Frequency",
        "seizure frequency normalized extraction from clinical text (Gan 2026 dataset)",
    ),
}


def mismatch_ids(metrics: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for mismatch in metrics.get("errors", {}).get("monthly_frequency_mismatches", []):
        record_id = mismatch.get("record_id")
        if record_id:
            out.add(str(record_id))
    return out


def evidence_error_values(metrics: dict[str, Any], document_id: str) -> set[str]:
    keys: set[str] = set()
    for error in metrics.get("errors", {}).get("evidence_support_errors", []):
        doc_id = error.get("record_id") or error.get("document_id")
        if doc_id == document_id:
            keys.add(str(error.get("raw_value")))
    return keys


def pipeline_steps(prediction: dict[str, Any], metrics: dict[str, Any]) -> list[dict[str, Any]]:
    document_id = str(prediction.get("document_id"))
    mismatches = mismatch_ids(metrics)
    evidence_errors = evidence_error_values(metrics, document_id)
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
            build_pipeline_step(
                step_id=f"{document_id}.{idx}.{field}",
                field=field,
                raw_value=raw_value,
                normalized_value=normalized_value,
                temporality=value.get("temporality"),
                negation=value.get("negation"),
                quality_flags=value.get("quality_flags", []),
                evidence=value.get("evidence") or [],
                deterministic_label="normalization bridge",
                deterministic_output=normalized_value,
                metadata=value.get("metadata", {}),
                outcome=outcome,
            )
        )
    return steps


def build_run(task: str, run_id: str, model_label: str, evidence_status: str, best: bool) -> dict[str, Any]:
    run_dir = resolve_run_directory(run_id, root=ROOT, include_archive=True)
    metrics = read_json(run_dir / "metrics.json")
    config = read_json(run_dir / "config.json")
    predictions = read_json(run_dir / "predictions.json")
    benchmark = metrics.get("benchmark_metrics", {})
    diagnostic = metrics.get("diagnostic_metrics", {})
    runtime = metrics.get("runtime", {})
    documents = {
        str(prediction.get("document_id")): build_document(
            document_id=str(prediction.get("document_id")),
            quality_flags=prediction.get("quality_flags", []),
            pipeline=pipeline_steps(prediction, metrics),
        )
        for prediction in predictions.get("predictions", [])
    }
    return build_run_entry(
        task=task,
        run_id=run_id,
        model_label=model_label,
        evidence_status=evidence_status,
        best=best,
        run_dir=str(run_dir.relative_to(ROOT)),
        schema_level=config.get("schema_level") or metrics.get("schema_level") or "gan_frequency_s0",
        scorer_mode=config.get("scorer_mode") or metrics.get("scorer") or "gan_frequency_deterministic_v1",
        program_variant=config.get("program_variant"),
        prompt_version=config.get("prompt_version"),
        metrics=build_run_metrics(
            micro_f1=pct(benchmark.get("monthly_frequency_accuracy")),
            micro_precision=pct(benchmark.get("purist_category_accuracy")),
            micro_recall=pct(benchmark.get("pragmatic_category_accuracy")),
            field_f1={"seizure_frequency": pct(benchmark.get("monthly_frequency_accuracy"))},
            evidence_support=pct(diagnostic.get("evidence_quote_support_rate")),
            seconds_per_record=round(runtime.get("prediction_seconds_per_record", 0), 3),
            evaluated_records=metrics.get("counts", {}).get("evaluated_records"),
        ),
        documents=documents,
    )


def build_gan_catalog() -> dict[str, Any]:
    run_specs = scan_runs_for_gan()
    runs = [build_run(*spec) for spec in run_specs]
    tasks = build_tasks_from_runs(TASK_SPECS, runs)
    catalog = build_catalog(
        dataset="gan_2026",
        source_note="Static viewer bundle generated from local runs/* artifacts for Gan 2026.",
        tasks=tasks,
        runs=runs,
        metric_labels=GAN_METRIC_LABELS,
    )
    validate_catalog_envelope(catalog)
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    catalog = build_gan_catalog()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        __import__("json").dumps(catalog, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(catalog['runs'])} runs to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
