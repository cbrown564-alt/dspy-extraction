#!/usr/bin/env python3
"""Export the Gan G14 temporal anchoring report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.gan_temporal_anchoring_g14 import (
    DEFAULT_G14_JSON_OUTPUT,
    DEFAULT_G14_MARKDOWN_OUTPUT,
    build_g14_temporal_anchoring_report,
    write_g14_report_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=DEFAULT_G14_JSON_OUTPUT,
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=DEFAULT_G14_MARKDOWN_OUTPUT,
    )
    args = parser.parse_args()

    report = build_g14_temporal_anchoring_report()
    write_g14_report_artifacts(
        report,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
    )
    temporal = report["summary"]["temporal_challenge"]
    print(
        json.dumps(
            {
                "split": report["split"],
                "surface": report["surfaces"]["temporal_challenge"],
                "records": temporal["records"],
                "exact_candidate_coverage": temporal["exact_candidate_coverage"],
                "temporal_slot_coverage": temporal["temporal_slot_coverage"],
                "failure_classes": temporal["failure_classes"],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
