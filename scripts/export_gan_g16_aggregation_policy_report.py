#!/usr/bin/env python3
"""Export the Gan G16 rate/duration aggregation policy report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.gan_g11_candidate_inventory_challenge import (
    DEFAULT_G11_JSON_OUTPUT,
)
from clinical_extraction.evaluation.gan_g16_aggregation_policy import (
    DEFAULT_G16_JSON_OUTPUT,
    DEFAULT_G16_MARKDOWN_OUTPUT,
    build_g16_aggregation_policy_report,
    write_g16_report_artifacts,
)
from clinical_extraction.evaluation.gan_temporal_anchoring_g14 import (
    DEFAULT_G14_JSON_OUTPUT,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g11-json", type=Path, default=DEFAULT_G11_JSON_OUTPUT)
    parser.add_argument("--g14-json", type=Path, default=DEFAULT_G14_JSON_OUTPUT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_G16_JSON_OUTPUT)
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=DEFAULT_G16_MARKDOWN_OUTPUT,
    )
    args = parser.parse_args()

    report = build_g16_aggregation_policy_report(
        g11_json=args.g11_json,
        g14_json=args.g14_json,
    )
    write_g16_report_artifacts(
        report,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
    )
    print(
        json.dumps(
            {
                "g11_records": report["summary"]["g11_exact_miss_challenge"]["records"],
                "standard50_records": report["summary"]["standard50"]["records"],
                "decision": report["decision"]["next_selector_authorization"],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
