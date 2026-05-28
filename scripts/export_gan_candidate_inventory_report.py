#!/usr/bin/env python3
"""Export the Gan S0 candidate-inventory coverage report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.gan_candidate_inventory import (
    DEFAULT_GAN_JSON,
    DEFAULT_JSON_OUTPUT,
    DEFAULT_MARKDOWN_OUTPUT,
    DEFAULT_SPLIT_FILE,
    DEFAULT_SPLIT_NAME,
    build_report_from_files,
    write_report_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gan-json", type=Path, default=DEFAULT_GAN_JSON)
    parser.add_argument("--split-file", type=Path, default=DEFAULT_SPLIT_FILE)
    parser.add_argument("--split-name", default=DEFAULT_SPLIT_NAME)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    args = parser.parse_args()

    report = build_report_from_files(
        gan_json=args.gan_json,
        split_file=args.split_file,
        split_name=args.split_name,
    )
    write_report_artifacts(
        report,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
    )
    print(
        json.dumps(
            {
                "records": report["summary"]["overall"]["records"],
                "gold_exact_covered": report["summary"]["overall"][
                    "gold_exact_covered"
                ],
                "gold_exact_coverage_rate": report["summary"]["overall"][
                    "gold_exact_coverage_rate"
                ],
                "gold_purist_equivalent_covered": report["summary"]["overall"][
                    "gold_purist_equivalent_covered"
                ],
                "gold_pragmatic_equivalent_covered": report["summary"]["overall"][
                    "gold_pragmatic_equivalent_covered"
                ],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
