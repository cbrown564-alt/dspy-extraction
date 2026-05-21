#!/usr/bin/env python3
"""Export a representative Gan S0 exact-frequency residual slice."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.evaluation.gan_residual_slice import (
    build_residual_slice,
    write_residual_slice_outputs,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export monthly-frequency miss rows and a 30-record error-read queue."
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Run directory containing predictions.json and analysis/records.jsonl.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory. Defaults to <run-dir>/analysis/exact_frequency_residual_slice.",
    )
    parser.add_argument(
        "--doc-path",
        type=Path,
        default=Path("docs/gan_s0_exact_frequency_residual_slice_error_read_20260521.md"),
        help="Markdown read-queue document path.",
    )
    args = parser.parse_args()

    run_dir = args.run_dir
    output_dir = args.output_dir or run_dir / "analysis" / "exact_frequency_residual_slice"
    payload = build_residual_slice(
        records_jsonl=run_dir / "analysis" / "records.jsonl",
        predictions_json=run_dir / "predictions.json",
    )
    write_residual_slice_outputs(
        output_dir=output_dir,
        doc_path=args.doc_path,
        run_id=run_dir.name,
        slice_payload=payload,
    )
    print(f"Wrote {output_dir / 'summary.json'}")
    print(f"Wrote {output_dir / 'monthly_misses.jsonl'}")
    print(f"Wrote {output_dir / 'error_read_selection.jsonl'}")
    print(f"Wrote {args.doc_path}")


if __name__ == "__main__":
    main()
