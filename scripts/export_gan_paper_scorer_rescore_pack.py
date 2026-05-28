#!/usr/bin/env python3
"""Export the Gan S0 G5 paper-scorer rescore pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.gan_paper_rescore_pack import (
    DEFAULT_BASELINE_SPECS,
    DEFAULT_JSON_OUTPUT,
    DEFAULT_MARKDOWN_OUTPUT,
    GanPaperRescoreBaseline,
    build_gan_paper_rescore_pack_report,
    write_report_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    parser.add_argument(
        "--baseline-run",
        action="append",
        default=[],
        metavar="BASELINE_ID=RUN_DIR",
        help=(
            "Override the default baseline set. Repeatable. When provided, only "
            "the supplied baseline runs are rescored."
        ),
    )
    parser.add_argument(
        "--apply-paper-prediction-repair",
        action="store_true",
        help="Enable author-evaluator prediction repair for the paper scorer view.",
    )
    parser.add_argument(
        "--allow-paper-prediction-range",
        action="store_true",
        help="Enable author-evaluator range containment for the paper scorer view.",
    )
    parser.add_argument(
        "--allow-paper-error-tolerance",
        action="store_true",
        help="Enable author-evaluator 1.5x numeric tolerance for the paper scorer view.",
    )
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--bootstrap-seed", type=int, default=0)
    args = parser.parse_args()

    baseline_specs = (
        _parse_baseline_overrides(args.baseline_run)
        if args.baseline_run
        else list(DEFAULT_BASELINE_SPECS)
    )
    report = build_gan_paper_rescore_pack_report(
        baseline_specs=baseline_specs,
        paper_scorer_options={
            "apply_paper_prediction_repair": args.apply_paper_prediction_repair,
            "allow_paper_prediction_range": args.allow_paper_prediction_range,
            "allow_paper_error_tolerance": args.allow_paper_error_tolerance,
        },
        bootstrap_samples=args.bootstrap_samples,
        bootstrap_seed=args.bootstrap_seed,
    )
    write_report_artifacts(
        report,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
    )
    print(
        json.dumps(
            {
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
                "paper_scorer_options": report["paper_scorer_options"],
                "summary": report["summary"]["baselines"],
            },
            indent=2,
        )
    )
    return 0


def _parse_baseline_overrides(
    overrides: list[str],
) -> list[GanPaperRescoreBaseline]:
    specs: list[GanPaperRescoreBaseline] = []
    for override in overrides:
        baseline_id, sep, run_dir = override.partition("=")
        if not sep or not baseline_id.strip() or not run_dir.strip():
            raise SystemExit("--baseline-run must be formatted as BASELINE_ID=RUN_DIR")
        clean_id = baseline_id.strip()
        specs.append(
            GanPaperRescoreBaseline(
                baseline_id=clean_id,
                label=clean_id,
                role="override baseline",
                run_dir=Path(run_dir.strip()),
            )
        )
    return specs


if __name__ == "__main__":
    raise SystemExit(main())
