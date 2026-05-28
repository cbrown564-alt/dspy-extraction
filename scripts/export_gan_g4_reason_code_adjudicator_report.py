#!/usr/bin/env python3
"""Export the Gan S0 G4 explicit reason-code adjudicator report."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.evaluation.gan_g4_reason_code_adjudicator import (
    DEFAULT_ARM_RUNS,
    DEFAULT_JSON_OUTPUT,
    DEFAULT_MARKDOWN_OUTPUT,
    G4_ARM_ID,
    build_gan_g4_reason_code_adjudicator_report,
    write_report_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export a dual-scorer Gan S0 G4 reason-code adjudicator report."
    )
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    parser.add_argument("--g4-arm-id", default=G4_ARM_ID)
    parser.add_argument(
        "--arm-run",
        action="append",
        default=[],
        metavar="ARM_ID=RUN_DIR",
        help=(
            "Override or add an arm run directory. Repeatable. Defaults to the "
            "2026-05-28 G2 baselines plus the completed G4 slice run."
        ),
    )
    args = parser.parse_args()

    arm_runs = dict(DEFAULT_ARM_RUNS)
    for override in args.arm_run:
        arm_id, sep, run_dir = override.partition("=")
        if not sep or not arm_id.strip() or not run_dir.strip():
            raise SystemExit("--arm-run must be formatted as ARM_ID=RUN_DIR")
        arm_runs[arm_id.strip()] = Path(run_dir.strip())

    report = build_gan_g4_reason_code_adjudicator_report(
        arm_run_dirs=arm_runs,
        g4_arm_id=args.g4_arm_id,
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
