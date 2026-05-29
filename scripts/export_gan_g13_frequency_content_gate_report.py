#!/usr/bin/env python3
"""Export the Gan G13 isolated frequency-content gate report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.gan_frequency_content_gate import (
    DEFAULT_G13_JSON_OUTPUT,
    DEFAULT_G13_MARKDOWN_OUTPUT,
    build_g13_frequency_content_gate_report,
    write_g13_report_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-output", type=Path, default=DEFAULT_G13_JSON_OUTPUT
    )
    parser.add_argument(
        "--markdown-output", type=Path, default=DEFAULT_G13_MARKDOWN_OUTPUT
    )
    args = parser.parse_args()

    report = build_g13_frequency_content_gate_report()
    write_g13_report_artifacts(
        report,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
    )
    overall = report["summary"]["overall"]
    print(
        json.dumps(
            {
                "split": report["split"],
                "records": overall["records"],
                "correct": overall["correct"],
                "accuracy": overall["accuracy"],
                "error_counts": report["summary"]["error_counts"],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
