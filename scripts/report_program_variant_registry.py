"""Render the typed program variant registry as a Markdown inventory.

Usage:
    uv run python scripts/report_program_variant_registry.py
    uv run python scripts/report_program_variant_registry.py --output docs/experiments/synthesis/program_variant_registry.md
"""
from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.experiments.program_variant_registry import (
    render_program_variant_registry_markdown,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render the typed program variant registry inventory."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: current working directory).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional Markdown output path. Prints to stdout when omitted.",
    )
    args = parser.parse_args(argv)

    report = render_program_variant_registry_markdown(repo_root=args.repo_root)
    if args.output is None:
        print(report, end="")
        return 0

    output_path = args.output
    if not output_path.is_absolute():
        output_path = args.repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
