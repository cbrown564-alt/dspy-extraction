from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from clinical_extraction.review.export import write_review_queue_jsonl


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export evaluation error-analysis examples as JSONL review items."
    )
    parser.add_argument("--evaluation-report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    report = json.loads(args.evaluation_report.read_text(encoding="utf-8"))
    write_review_queue_jsonl(report, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
