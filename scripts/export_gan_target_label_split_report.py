#!/usr/bin/env python3
"""Export the Gan G2 target-selection and label-construction split report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.evaluation.gan_target_label_split import (
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
    constrained = report["summary"]["arms"]["candidate_constrained_oracle"]
    print(
        json.dumps(
            {
                "records": report["summary"]["records"],
                "candidate_constrained_supported": constrained[
                    "supported_predictions"
                ],
                "candidate_constrained_paper_monthly_accuracy": constrained[
                    "paper_reproduction"
                ]["monthly_frequency_accuracy"],
                "candidate_constrained_canonical_monthly_accuracy": constrained[
                    "canonical"
                ]["monthly_frequency_accuracy"],
                "invalid_candidate_labels": report["summary"][
                    "deterministic_label_constructor"
                ]["invalid_candidate_labels"],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
