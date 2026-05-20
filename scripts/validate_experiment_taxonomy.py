"""Validate experiment configs and registry taxonomy coverage.

Usage:
    uv run python scripts/validate_experiment_taxonomy.py
    uv run python scripts/validate_experiment_taxonomy.py --errors-only
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clinical_extraction.experiments.registry_validation import (
    format_validation_report,
    validate_experiment_taxonomy,
    validation_failed,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate experiment taxonomy registry and config coverage."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: current working directory).",
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Exit 0 when only warnings remain; still print warnings.",
    )
    args = parser.parse_args(argv)

    issues = validate_experiment_taxonomy(args.repo_root)
    if issues:
        print(format_validation_report(issues))

    if not issues:
        print("Experiment taxonomy validation passed.")
        return 0

    errors_present = any(issue.level == "error" for issue in issues)
    if args.errors_only:
        return 1 if errors_present else 0
    return 1 if validation_failed(issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
