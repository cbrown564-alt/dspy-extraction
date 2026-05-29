#!/usr/bin/env python3
"""Export the Gan G11 candidate-inventory challenge-set report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.gan_g11_candidate_inventory_challenge import (
    DEFAULT_G11_JSON_OUTPUT,
    DEFAULT_G11_MARKDOWN_OUTPUT,
    DEFAULT_G1_JSON,
    build_g11_candidate_inventory_challenge_report,
    write_g11_report_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g1-json", type=Path, default=DEFAULT_G1_JSON)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_G11_JSON_OUTPUT)
    parser.add_argument(
        "--markdown-output", type=Path, default=DEFAULT_G11_MARKDOWN_OUTPUT
    )
    args = parser.parse_args()

    report = build_g11_candidate_inventory_challenge_report(g1_json=args.g1_json)
    write_g11_report_artifacts(
        report,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
    )
    overall = report["summary"]["overall"]
    print(
        json.dumps(
            {
                "challenge_set": report["challenge_set"],
                "records": overall["records"],
                "gold_exact_covered": overall["gold_exact_covered"],
                "gold_purist_equivalent_covered": overall[
                    "gold_purist_equivalent_covered"
                ],
                "gold_pragmatic_equivalent_covered": overall[
                    "gold_pragmatic_equivalent_covered"
                ],
                "rows_with_g1_diff": report["g1_diff_summary"]["rows_with_any_diff"],
                "decision": report["decision"]["inventory_stage_interpretation"],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
