from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clinical_extraction.evaluation.exect_holdout_residual_attribution import (
    build_report,
)


def test_e11_holdout_residual_attribution_separates_transfer_causes():
    report = build_report(
        splits_path=Path("data/splits/exectv2_splits.json"),
        e2_audit_path=Path(
            "docs/experiments/exect/"
            "exect_s1_raw_bridge_prompt_split_audit_20260528.json"
        ),
    )

    assert report["kanban_card"] == "E11 - ExECT Holdout Residual Attribution"
    assert report["model_calls"] == 0
    assert report["scorer_semantics_changed"] is False
    assert report["loader_split_bridge_prompt_changed"] is False

    s1_gpt_delta = report["transfer_deltas"]["s1_gpt_validation_to_test"]
    assert round(s1_gpt_delta["micro_f1_delta"], 3) == -0.145
    assert s1_gpt_delta["field_f1_delta"]["diagnosis"] < -0.20
    assert s1_gpt_delta["field_f1_delta"]["seizure_type"] < -0.20
    assert abs(s1_gpt_delta["field_f1_delta"]["annotated_medication"]) < 0.01

    frequency = report["frequency_attribution"]
    assert (
        frequency["validation"]["surface_summaries"]["broad_event_rate_payload"][
            "recall"
        ]
        == 1.0
    )
    assert (
        frequency["test"]["surface_summaries"]["broad_event_rate_payload"]["tp"]
        == 31
    )
    assert (
        frequency["test"]["surface_summaries"]["broad_event_rate_payload"]["fn"]
        == 13
    )
    assert (
        frequency["test"]["surface_summaries"]["candidate_constrained_oracle"]["f1"]
        < 0.83
    )
    assert (
        frequency["test"]["s5_frequency_category_counts"][
            "fn:payload_coverage_gap:seizure_free"
        ]
        == 4
    )

    medication = report["medication_attribution"]["surface_summaries"]
    assert medication["isolated_current_rx_payload"]["f1"] == 1.0
    assert (
        medication["s5_gpt_surface"]["f1"]
        < medication["s1_gpt_surface"]["f1"]
    )
