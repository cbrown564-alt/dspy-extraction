"""Tests for ExECT comorbidity residual-slice replay."""

from pathlib import Path

from clinical_extraction.evaluation.exect_residual_slice import (
    load_residual_slice_record_ids,
    replay_comorbidity_bridge_slice,
)


def test_comorbidity_residual_slice_fixture_has_six_queue_docs():
    record_ids = load_residual_slice_record_ids(
        Path("data/fixtures/exect_s2_comorbidity_residual_slice.json")
    )
    assert record_ids == [
        "EA0150",
        "EA0170",
        "EA0179",
        "EA0136",
        "EA0090",
        "EA0148",
    ]


def test_comorbidity_residual_replay_improves_ea0150_with_c0():
    payload = replay_comorbidity_bridge_slice(
        reference_run_dir=Path(
            "runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z"
        ),
        record_ids=["EA0150"],
    )
    l1 = next(
        row
        for row in payload["arms"]["L1"]["per_document"]
        if row["record_id"] == "EA0150"
    )
    c0 = next(
        row
        for row in payload["arms"]["C0"]["per_document"]
        if row["record_id"] == "EA0150"
    )
    assert "traumatic brain injury" in l1["predicted"]
    assert "traumatic" in c0["predicted"]
    assert "brain injury" in c0["predicted"]
    assert c0["f1"] > l1["f1"]
