"""Tests for ExECT epilepsy_cause residual-slice replay."""

from pathlib import Path

from clinical_extraction.evaluation.exect_residual_slice import (
    load_residual_slice_record_ids,
    replay_epilepsy_cause_bridge_slice,
)


def test_epilepsy_cause_residual_slice_fixture_has_three_queue_docs():
    record_ids = load_residual_slice_record_ids(
        Path("data/fixtures/exect_s3_epilepsy_cause_residual_slice.json")
    )
    assert record_ids == ["EA0150", "EA0016", "EA0137"]


def test_epilepsy_cause_residual_replay_l1_matches_stored_predictions():
    payload = replay_epilepsy_cause_bridge_slice(
        reference_run_dir=Path(
            "runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z"
        ),
        record_ids=["EA0016"],
    )
    l1 = next(
        row
        for row in payload["arms"]["L1"]["per_document"]
        if row["record_id"] == "EA0016"
    )
    k01 = next(
        row
        for row in payload["arms"]["K0+K1"]["per_document"]
        if row["record_id"] == "EA0016"
    )
    assert l1["predicted"] == ["stroke"]
    assert k01["predicted"] == ["stroke"]
    assert l1["f1"] == k01["f1"]
