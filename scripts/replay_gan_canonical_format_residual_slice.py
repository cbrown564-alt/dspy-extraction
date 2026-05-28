#!/usr/bin/env python3
"""Replay Gan canonical-format port C0 vs C1 on the fixed residual error-read queue."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.gan_residual_slice import (
    compare_residual_slice_arms,
    load_error_read_queue_rows,
    load_residual_slice_record_ids,
)
from clinical_extraction.paths import resolve_run_directory


DEFAULT_FIXTURE = Path("data/fixtures/gan_s0_exact_frequency_residual_slice.json")
DEFAULT_REFERENCE_QUEUE = Path(
    "runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z/analysis/exact_frequency_residual_slice/error_read_selection.jsonl"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare C0 vs C1 on the 30-record exact-frequency residual queue."
    )
    parser.add_argument(
        "--control-run-dir",
        type=Path,
        required=True,
        help="C0 run directory (or experiment_id prefix under runs/).",
    )
    parser.add_argument(
        "--treatment-run-dir",
        type=Path,
        required=True,
        help="C1 run directory (or experiment_id prefix under runs/).",
    )
    parser.add_argument(
        "--reference-queue",
        type=Path,
        default=DEFAULT_REFERENCE_QUEUE,
        help="error_read_selection.jsonl from VR full-validation export.",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_FIXTURE,
        help="Residual slice record_ids fixture.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/gan_canonical_format_residual_replay_20260521"),
        help="Directory for replay summary JSON.",
    )
    args = parser.parse_args()

    control_run_dir = resolve_run_directory(
        args.control_run_dir,
        allow_prefix_match=True,
        include_archive=True,
    )
    treatment_run_dir = resolve_run_directory(
        args.treatment_run_dir,
        allow_prefix_match=True,
        include_archive=True,
    )
    for run_dir_arg, run_dir in (
        (args.control_run_dir, control_run_dir),
        (args.treatment_run_dir, treatment_run_dir),
    ):
        if not run_dir.is_dir():
            raise FileNotFoundError(f"Could not resolve run directory for {run_dir_arg}")
    fixture_ids = load_residual_slice_record_ids(args.fixture)
    queue_rows = load_error_read_queue_rows(args.reference_queue)
    queue_ids = [row["record_id"] for row in queue_rows]
    if queue_ids != fixture_ids:
        raise ValueError(
            "Fixture record_ids do not match reference queue ordering/content."
        )

    payload = compare_residual_slice_arms(
        queue_rows=queue_rows,
        control_run_dir=control_run_dir,
        treatment_run_dir=treatment_run_dir,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    headline = payload["headline"]
    print(f"Wrote {summary_path}")
    print(f"Control run: {payload['control_run_id']}")
    print(f"Treatment run: {payload['treatment_run_id']}")
    print(
        "Normalized exact: "
        f"C0 {headline['c0_normalized_exact_rate']:.1%} | "
        f"C1 {headline['c1_normalized_exact_rate']:.1%}"
    )
    print(
        "Monthly: "
        f"C0 {headline['c0_monthly_rate']:.1%} | "
        f"C1 {headline['c1_monthly_rate']:.1%}"
    )
    print(
        "C1 vs C0 recoveries: "
        f"exact {headline['exact_recovery_c1_vs_c0']}, "
        f"monthly {headline['monthly_recovery_c1_vs_c0']}; "
        f"regressions: exact {headline['exact_regression_c1_vs_c0']}, "
        f"monthly {headline['monthly_regression_c1_vs_c0']}; "
        f"pragmatic overcall {headline['c1_pragmatic_overcall_vs_c0']}"
    )


if __name__ == "__main__":
    main()
