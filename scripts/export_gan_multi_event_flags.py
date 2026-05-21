#!/usr/bin/env python3
"""Export Gan multi-event/single-label diagnostic flags and run stratification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.gan_multi_event_flags import (
    build_flags_for_raw_records,
    build_validation_stratification,
    write_flag_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Export diagnostic flags for Gan records with multi-event/single-label "
            "adjudication signals."
        )
    )
    parser.add_argument(
        "--gan-json",
        type=Path,
        default=Path("data/Gan (2026)/synthetic_data_subset_1500.json"),
        help="Gan synthetic JSON source file.",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Optional run directory with analysis/records.jsonl to stratify.",
    )
    parser.add_argument(
        "--split-file",
        type=Path,
        default=Path("data/splits/gan_2026_splits.json"),
        help="Split file used when stratifying a run.",
    )
    parser.add_argument(
        "--split-name",
        default="gan_2026_fixed_v1:validation",
        help="Split name used when stratifying a run.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/gan_multi_event_flags_20260521"),
        help="Output directory for flags.jsonl and summary.json.",
    )
    args = parser.parse_args()

    raw_records = json.loads(args.gan_json.read_text(encoding="utf-8"))
    flags = build_flags_for_raw_records(raw_records)
    validation = None
    if args.run_dir is not None:
        validation = build_validation_stratification(
            flags=flags,
            records_jsonl=args.run_dir / "analysis" / "records.jsonl",
            split_file=args.split_file,
            split_name=args.split_name,
        )

    write_flag_artifacts(
        flags=flags,
        output_dir=args.output_dir,
        validation_stratification=validation,
    )
    print(f"Wrote {args.output_dir / 'summary.json'}")
    print(f"Wrote {args.output_dir / 'flags.jsonl'}")


if __name__ == "__main__":
    main()
