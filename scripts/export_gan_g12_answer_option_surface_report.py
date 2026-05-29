#!/usr/bin/env python3
"""Export the Gan G12 aggregation-aware answer-option surface report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.gan_g12_answer_option_surface import (
    DEFAULT_G12_JSON_OUTPUT,
    DEFAULT_G12_MARKDOWN_OUTPUT,
    build_g12_answer_option_surface_report,
    write_g12_report_artifacts,
)
from clinical_extraction.evaluation.gan_g11_candidate_inventory_challenge import (
    DEFAULT_G11_JSON_OUTPUT,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g11-json", type=Path, default=DEFAULT_G11_JSON_OUTPUT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_G12_JSON_OUTPUT)
    parser.add_argument(
        "--markdown-output", type=Path, default=DEFAULT_G12_MARKDOWN_OUTPUT
    )
    args = parser.parse_args()

    report = build_g12_answer_option_surface_report(g11_json=args.g11_json)
    write_g12_report_artifacts(
        report,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
    )
    raw = report["summary"]["raw_option_view"]["overall"]
    constructed = report["summary"]["constructed_aggregate_option_view"]["overall"]
    print(
        json.dumps(
            {
                "challenge_set": report["challenge_set"],
                "records": raw["records"],
                "raw_exact": raw["gold_exact_covered"],
                "raw_purist": raw["gold_purist_equivalent_covered"],
                "raw_pragmatic": raw["gold_pragmatic_equivalent_covered"],
                "constructed_exact": constructed["gold_exact_covered"],
                "constructed_purist": constructed[
                    "gold_purist_equivalent_covered"
                ],
                "constructed_pragmatic": constructed[
                    "gold_pragmatic_equivalent_covered"
                ],
                "decision": report["decision"]["g10_authorized_surface"],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
