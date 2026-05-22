#!/usr/bin/env python3
"""Export a record-level Gan frequency CSV report from a stored run."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_run_analysis import (
    export_gan_run_record_report_csv,
    load_record_ids_filter,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export a per-record Gan frequency prediction/gold CSV report."
    )
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="CSV destination. Defaults to <run-dir>/<run-id>_record_report.csv.",
    )
    parser.add_argument(
        "--record-ids-file",
        type=Path,
        default=None,
        help="Optional JSON file defining record_ids or records for explicit scope.",
    )
    args = parser.parse_args(argv)

    gold_by_id = {record.record_id: record for record in load_gan_records()}
    record_ids = (
        load_record_ids_filter(args.record_ids_file)
        if args.record_ids_file is not None
        else None
    )
    output_path = export_gan_run_record_report_csv(
        run_dir=args.run_dir,
        gold_by_id=gold_by_id,
        output_path=args.output,
        record_ids=record_ids,
    )
    print(output_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
