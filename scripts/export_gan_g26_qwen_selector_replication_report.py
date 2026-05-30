#!/usr/bin/env python3
"""Export the Gan S0 G26 Qwen selector replication report."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.evaluation.gan_g26_qwen_selector_replication import (
    DEFAULT_BASELINE_RUNS,
    DEFAULT_JSON_OUTPUT,
    DEFAULT_MARKDOWN_OUTPUT,
    build_gan_g26_qwen_selector_replication_report,
    write_report_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export a Gan S0 G26 Qwen selector replication report."
    )
    parser.add_argument(
        "--g26-run",
        type=Path,
        required=True,
        help="Run directory for the completed G26 standard50 run.",
    )
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    parser.add_argument(
        "--arm-run",
        action="append",
        default=[],
        metavar="ARM_ID=RUN_DIR",
        help="Override or add a baseline arm run directory. Repeatable.",
    )
    args = parser.parse_args()

    arm_runs = dict(DEFAULT_BASELINE_RUNS)
    for override in args.arm_run:
        arm_id, sep, run_dir = override.partition("=")
        if not sep or not arm_id.strip() or not run_dir.strip():
            raise SystemExit("--arm-run must be formatted as ARM_ID=RUN_DIR")
        arm_runs[arm_id.strip()] = Path(run_dir.strip())

    report = build_gan_g26_qwen_selector_replication_report(
        g26_run_dir=args.g26_run,
        arm_run_dirs=arm_runs,
    )
    write_report_artifacts(
        report,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
    )
    print(f"Wrote {args.json_output}")
    print(f"Wrote {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
