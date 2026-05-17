"""Run a Gan S0 experiment from an experiment config file.

Usage:
    uv run python scripts/run_experiment.py \\
        --experiment configs/experiments/gan_s0_baseline_gpt4_1_mini.json \\
        --env-file .env
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.cli import evaluate_gan_predictions
from clinical_extraction.experiments.config import load_experiment_config
from clinical_extraction.llms import LLMProviderConfig, build_dspy_lm
from clinical_extraction.programs.gan_frequency_s0 import (
    GanFrequencyS0Module,
    gan_frequency_s0_run_metadata,
    predict_gan_records,
)
from clinical_extraction.runs import create_run_artifact_layout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a clinical extraction experiment from a config file.",
    )
    parser.add_argument("--experiment", required=True, type=Path)
    parser.add_argument("--run-id", help="Override auto-generated run ID.")
    parser.add_argument("--env-file", type=Path, help="Load API keys from .env file.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and print plan without making model calls.",
    )
    args = parser.parse_args(argv)

    if args.env_file:
        _load_env_file(args.env_file)

    config = load_experiment_config(args.experiment)
    print(f"Experiment: {config.experiment_id}")
    print(f"Dataset:    {config.dataset}")
    print(f"Split:      {config.split_name}")
    print(f"Model:      {config.model_config_path}")

    split_data = json.loads(config.split_file.read_text(encoding="utf-8"))
    split_subset = config.split_name.split(":")[-1]
    if split_subset not in split_data or not isinstance(split_data[split_subset], list):
        raise SystemExit(
            f"Split subset {split_subset!r} not found in {config.split_file}."
        )

    ordered_split_ids: list[str] = split_data[split_subset]
    if config.max_records is not None:
        ordered_split_ids = ordered_split_ids[: config.max_records]

    all_records = {r.record_id: r for r in load_gan_records()}
    records = [all_records[rid] for rid in ordered_split_ids if rid in all_records]
    missing_from_gan = [rid for rid in ordered_split_ids if rid not in all_records]
    if missing_from_gan:
        print(
            f"Warning: {len(missing_from_gan)} split IDs not in Gan records: "
            f"{missing_from_gan[:5]}"
        )

    print(
        f"Records:    {len(records)}"
        + (f" (capped at max_records={config.max_records})" if config.max_records else "")
    )

    if args.dry_run:
        print("\nDry run — exiting before model calls.")
        return 0

    model_config = LLMProviderConfig.model_validate_json(
        config.model_config_path.read_text(encoding="utf-8")
    )
    lm = build_dspy_lm(model_config)
    dspy.configure(lm=lm)

    module = GanFrequencyS0Module()

    run_id = args.run_id or _make_run_id(config.experiment_id)
    metadata = gan_frequency_s0_run_metadata(
        run_id=run_id,
        split_name=config.split_name,
        model_provider=model_config.provider,
        model_name=model_config.model,
        prompt_version=config.prompt_version,
        extra={
            "experiment_id": config.experiment_id,
            "structured_output_strategy": config.structured_output_strategy,
        },
    )
    metadata = metadata.model_copy(update={"metric_caveats": config.metric_caveats})
    paths = create_run_artifact_layout(metadata, root=config.output_root)
    print(f"\nRun directory: {paths['run']}")

    paths["config"].write_text(
        json.dumps(config.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["prompts"].write_text(
        json.dumps(
            {
                "signature": "GanFrequencyS0Signature",
                "module": "GanFrequencyS0Module",
                "prompt_version": config.prompt_version,
                "structured_output_strategy": config.structured_output_strategy,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Running {len(records)} predictions...")
    prediction_set = predict_gan_records(
        module,
        records,
        model_provider=model_config.provider,
        model_name=model_config.model,
        prompt_version=config.prompt_version,
    )
    paths["predictions"].write_text(
        json.dumps(prediction_set.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Evaluating...")
    report = evaluate_gan_predictions(prediction_set)
    paths["metrics"].write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["errors"].write_text(
        json.dumps(report.get("errors", {}), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    _print_summary(report, config.metric_caveats)
    return 0


def _make_run_id(experiment_id: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{experiment_id}_{timestamp}"


def _load_env_file(path: Path) -> None:
    """Load KEY=VALUE pairs from a .env file into os.environ (existing vars win)."""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def _print_summary(report: dict[str, Any], metric_caveats: list[str]) -> None:
    counts = report.get("counts", {})
    bm = report.get("benchmark_metrics", {})
    diag = report.get("diagnostic_metrics", {})

    def pct(v: float | None) -> str:
        return f"{v:.1%}" if v is not None else "N/A"

    print("\n--- Counts ---")
    print(f"  Evaluated:  {counts.get('evaluated_records')}")
    print(f"  Valid:      {counts.get('valid_predictions')}")
    print(f"  Invalid:    {counts.get('invalid_predictions')}")
    print(f"  Missing:    {counts.get('missing_predictions')}")

    print("\n--- Benchmark metrics (not published reproduction) ---")
    print(f"  Monthly frequency accuracy:  {pct(bm.get('monthly_frequency_accuracy'))}")
    print(f"  Purist category accuracy:    {pct(bm.get('purist_category_accuracy'))}")
    print(f"  Pragmatic category accuracy: {pct(bm.get('pragmatic_category_accuracy'))}")

    print("\n--- Diagnostic metrics ---")
    print(f"  Schema validity rate:         {pct(diag.get('schema_valid_prediction_rate'))}")
    print(f"  Normalized label accuracy:    {pct(diag.get('normalized_label_accuracy'))}")
    print(f"  Evidence quote support rate:  {pct(diag.get('evidence_quote_support_rate'))}")

    if metric_caveats:
        print("\n--- Caveats ---")
        for caveat in metric_caveats:
            print(f"  * {caveat}")


if __name__ == "__main__":
    raise SystemExit(main())
