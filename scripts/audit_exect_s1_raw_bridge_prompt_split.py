"""Generate the ExECT S1 raw/bridge/prompt causal split audit."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.evaluation.exect_s1_split_audit import (
    build_s1_raw_bridge_prompt_audit,
    render_s1_raw_bridge_prompt_audit_markdown,
)

DEFAULT_RUN_DIRS = {
    "schema_raw_cap25": Path(
        "archive/runs/exect_s1_full_ladder_l1_cap25_gpt4_1_mini_20260521T003924Z"
    ),
    "policy_raw_cap25": Path(
        "archive/runs/exect_s1_interleaving_l1_raw_no_bridges_cap25_gpt4_1_mini_20260520T190744Z"
    ),
    "policy_post_bridge_cap25": Path(
        "archive/runs/exect_s1_interleaving_h1_post_bridge_cap25_gpt4_1_mini_20260520T190754Z"
    ),
    "policy_raw_full_validation": Path(
        "archive/runs/exect_s1_interleaving_l1_raw_no_bridges_gpt4_1_mini_20260520T190804Z"
    ),
    "policy_post_bridge_full_validation": Path(
        "archive/runs/exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z"
    ),
    "qwen_clean_validation": Path(
        "archive/runs/exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_ollama_20260525T103640Z"
    ),
    "qwen_clean_test_holdout": Path(
        "runs/test_holdout_exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_ollama_20260526T184101Z"
    ),
}

DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/exect/exect_s1_raw_bridge_prompt_split_audit_20260528.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/exect/exect_s1_raw_bridge_prompt_split_audit_20260528.md"
)


def build_report() -> dict:
    return build_s1_raw_bridge_prompt_audit(run_dirs=DEFAULT_RUN_DIRS)


def main() -> None:
    report = build_report()
    DEFAULT_JSON_OUTPUT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    DEFAULT_MARKDOWN_OUTPUT.write_text(
        render_s1_raw_bridge_prompt_audit_markdown(report),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "json_output": DEFAULT_JSON_OUTPUT.as_posix(),
                "markdown_output": DEFAULT_MARKDOWN_OUTPUT.as_posix(),
                "model_calls": report["model_calls"],
                "bridge_full_validation_delta": report["stage_deltas"][
                    "bridge_full_validation"
                ],
                "qwen_holdout_minus_validation": report["stage_deltas"][
                    "qwen_holdout_minus_validation"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
