"""Run a clinical extraction experiment from an experiment config file.

Usage:
    uv run python scripts/run_experiment.py \\
        --experiment configs/experiments/gan_s0_baseline_gpt4_1_mini.json \\
        --env-file .env
"""
from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.experiments.runner import run_experiment


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
    return run_experiment(
        args.experiment,
        run_id=args.run_id,
        env_file=args.env_file,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
