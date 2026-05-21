"""Report deterministic temporal-candidate gold coverage on the residual slice."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_residual_slice import (
    assign_residual_group,
    load_residual_slice_record_ids,
)
from clinical_extraction.gan.temporal_candidates import build_temporal_frequency_candidates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("data/fixtures/gan_s0_exact_frequency_residual_slice.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/gan_residual_candidate_coverage/summary.json"),
    )
    args = parser.parse_args()

    record_ids = load_residual_slice_record_ids(args.fixture)
    records_by_id = {record.record_id: record for record in load_gan_records()}

    rows: list[dict[str, object]] = []
    by_group: dict[str, dict[str, int]] = {}

    for record_id in record_ids:
        record = records_by_id[record_id]
        labels = {
            candidate.canonical_label
            for candidate in build_temporal_frequency_candidates(record)
        }
        gold_in_candidates = record.gold_label in labels
        group = assign_residual_group(
            {
                "record_id": record_id,
                "failure_class": "benchmark_severe",
                "gold_pragmatic_category": "frequent",
            }
        )
        group_stats = by_group.setdefault(
            group,
            {"records": 0, "gold_in_candidates": 0},
        )
        group_stats["records"] += 1
        if gold_in_candidates:
            group_stats["gold_in_candidates"] += 1
        rows.append(
            {
                "record_id": record_id,
                "residual_group": group,
                "gold_label": record.gold_label,
                "gold_in_candidates": gold_in_candidates,
                "candidate_labels": sorted(labels),
            }
        )

    covered = sum(1 for row in rows if row["gold_in_candidates"])
    summary = {
        "fixture": str(args.fixture),
        "record_count": len(rows),
        "gold_in_candidates": covered,
        "coverage_rate": covered / len(rows) if rows else 0.0,
        "by_group": by_group,
        "rows": rows,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("record_count", "gold_in_candidates", "coverage_rate", "by_group")}, indent=2))


if __name__ == "__main__":
    main()
