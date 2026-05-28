"""Validate typed primitive registry metadata and cross-artifact consistency.

Usage:
    uv run python scripts/validate_primitives.py
    uv run python scripts/validate_primitives.py --errors-only
"""
from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.experiments.primitive_registry_validation import (
    format_validation_report,
    validate_primitive_registry,
    validation_failed,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate primitive registry, catalog, fixtures, and adapter bindings."
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

    issues = validate_primitive_registry(args.repo_root)
    if issues:
        print(format_validation_report(issues))

    if not issues:
        print("Primitive registry validation passed.")
        return 0

    errors_present = validation_failed(issues)
    if args.errors_only:
        return 1 if errors_present else 0
    return 1 if validation_failed(issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
