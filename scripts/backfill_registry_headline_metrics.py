"""Backfill headline_metric on registry rows that unlock concrete comparisons."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / "docs" / "experiment_registry.json"

BACKFILLS: dict[str, dict] = {
    "gan_s0_qwen35b_direct_full_validation_guardrails": {
        "name": "monthly_frequency_accuracy",
        "value": 0.559,
        "secondary": {
            "purist_category_accuracy": 0.619,
            "pragmatic_category_accuracy": 0.705,
            "evidence_quote_support_rate": 0.996,
            "schema_valid_prediction_rate": 0.94,
        },
    },
    "gan_s0_qwen35b_direct_regression_slice_guardrails": {
        "name": "monthly_frequency_accuracy",
        "value": 0.714,
        "secondary": {
            "purist_category_accuracy": 0.714,
            "pragmatic_category_accuracy": 0.714,
            "schema_valid_prediction_rate": 1.0,
            "evidence_quote_support_rate": 1.0,
        },
    },
    "gan_s0_qwen35b_verify_repair_regression_slice_guardrails": {
        "name": "monthly_frequency_accuracy",
        "value": 0.462,
        "secondary": {
            "purist_category_accuracy": 0.538,
            "pragmatic_category_accuracy": 0.615,
            "schema_valid_prediction_rate": 0.929,
            "evidence_quote_support_rate": 1.0,
        },
    },
    "gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails": {
        "name": "monthly_frequency_accuracy",
        "value": 1.0,
        "secondary": {
            "purist_category_accuracy": 1.0,
            "pragmatic_category_accuracy": 1.0,
            "schema_valid_prediction_rate": 1.0,
        },
    },
    "gan_s0_qwen35b_temporal_event_table_regression_slice_guardrails": {
        "name": "monthly_frequency_accuracy",
        "value": 1.0,
        "secondary": {
            "purist_category_accuracy": 1.0,
            "pragmatic_category_accuracy": 1.0,
            "schema_valid_prediction_rate": 1.0,
        },
    },
}

DECISION_DOCS: dict[str, str] = {
    "gan_s0_qwen35b_direct_full_validation_guardrails": (
        "docs/gan_s0_qwen35b_direct_full_validation_guardrails_error_analysis.md"
    ),
    "gan_s0_qwen35b_direct_regression_slice_guardrails": (
        "docs/gan_s0_qwen35b_regression_slice_inspection_20260519.md"
    ),
    "gan_s0_qwen35b_verify_repair_regression_slice_guardrails": (
        "docs/gan_s0_qwen35b_verify_repair_regression_slice_guardrails_error_analysis.md"
    ),
    "gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails": (
        "docs/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_b1_error_analysis.md"
    ),
    "gan_s0_qwen35b_temporal_event_table_regression_slice_guardrails": (
        "docs/gan_s0_qwen35b_temporal_event_table_regression_slice_b2_error_analysis.md"
    ),
}


def main() -> None:
    reg = json.loads(REG_PATH.read_text(encoding="utf-8"))
    updated: list[str] = []
    for row in reg["experiments"]:
        eid = row["experiment_id"]
        if eid not in BACKFILLS:
            continue
        row["headline_metric"] = BACKFILLS[eid]
        if row.get("decision_doc") == "pending_backfill" and eid in DECISION_DOCS:
            row["decision_doc"] = DECISION_DOCS[eid]
        if eid == "gan_s0_qwen35b_direct_full_validation_guardrails":
            row["varied_factor"] = "program_architecture"
        updated.append(eid)
    REG_PATH.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {len(updated)} rows: {', '.join(updated)}")


if __name__ == "__main__":
    main()
