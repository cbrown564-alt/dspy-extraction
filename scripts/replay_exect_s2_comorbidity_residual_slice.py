#!/usr/bin/env python3
"""Replay S2 comorbidity C0/C1 bridges on the fixed 6-doc qualitative queue."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.exect_residual_slice import (
    DEFAULT_COMORBIDITY_SLICE_FIXTURE,
    load_residual_slice_record_ids,
    replay_comorbidity_bridge_slice,
)


def _resolve_run_dir(path: Path) -> Path:
    if path.is_dir():
        return path
    matches = sorted(Path("runs").glob(f"{path.name}*"))
    if len(matches) == 1:
        return matches[0]
    if matches:
        return matches[-1]
    raise FileNotFoundError(f"Could not resolve run directory for {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-score L1 vs C0 vs C0+C1 comorbidity bridges on the 6-doc queue."
    )
    parser.add_argument(
        "--reference-run-dir",
        type=Path,
        default=Path(
            "runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z"
        ),
        help="S2 run with raw comorbidity labels (full validation anchor).",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_COMORBIDITY_SLICE_FIXTURE,
        help="Residual slice record_ids fixture.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/exect_s2_comorbidity_residual_replay_20260521"),
        help="Directory for replay summary JSON.",
    )
    args = parser.parse_args()

    reference_run_dir = _resolve_run_dir(args.reference_run_dir)
    record_ids = load_residual_slice_record_ids(args.fixture)
    payload = replay_comorbidity_bridge_slice(
        reference_run_dir=reference_run_dir,
        record_ids=record_ids,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    headline = payload["headline"]
    print(f"Wrote {summary_path}")
    print(f"Reference run: {payload['reference_run_id']}")
    print(
        "Comorbidity F1: "
        f"L1 {headline['l1_comorbidity_f1']:.1%} | "
        f"C0 {headline['c0_comorbidity_f1']:.1%} | "
        f"C0+C1 {headline['c0_c1_comorbidity_f1']:.1%}"
    )
    print(
        "Delta vs L1: "
        f"C0 {headline['c0_vs_l1_f1_delta']:+.1%} | "
        f"C0+C1 {headline['c0_c1_vs_l1_f1_delta']:+.1%}"
    )
    print(
        "Doc-level label changes vs L1: "
        f"fixes {headline['label_fixes_vs_l1']}, "
        f"regressions {headline['label_regressions_vs_l1']}"
    )


if __name__ == "__main__":
    main()
