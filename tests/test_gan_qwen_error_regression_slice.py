import json
from pathlib import Path

from clinical_extraction.datasets.gan_qwen_regression_slice import (
    gan_qwen_error_regression_failure_modes,
    gan_qwen_error_regression_record_ids,
    load_gan_qwen_error_regression_slice,
)
from clinical_extraction.experiments.config import load_experiment_config


def test_gan_qwen_error_regression_slice_records_remain_in_validation_split():
    slice_payload = load_gan_qwen_error_regression_slice()
    split_data = json.loads(
        Path("data/splits/gan_2026_splits.json").read_text(encoding="utf-8")
    )
    validation_ids = set(split_data["validation"])
    record_ids = gan_qwen_error_regression_record_ids()
    assert slice_payload["split_name"] == "gan_2026_fixed_v1:validation"
    assert len(record_ids) == 14
    assert set(record_ids) <= validation_ids


def test_gan_qwen_error_regression_slice_covers_documented_failure_modes():
    modes = set(gan_qwen_error_regression_failure_modes().values())
    assert "unknown_vs_no_reference" in modes
    assert "no_clinical_content_null_output" in modes
    assert "highest_current_quantified_frequency" in modes
    assert "year_to_date_denominator" in modes
    assert "incomplete_cluster_label" in modes
    assert "cluster_multiplier_preservation" in modes
    assert "short_seizure_free_threshold" in modes
    assert "infrequent_quantified_over_unknown" in modes


def test_qwen_regression_slice_experiment_config_uses_record_ids_filter():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_direct_regression_slice_guardrails.json"
        )
    )
    assert config.experiment_id == "gan_s0_qwen35b_direct_regression_slice_guardrails"
    assert set(config.record_ids) == set(gan_qwen_error_regression_record_ids())


def test_qwen35b_20260522_pragmatic_error_slice_records_validation_scope():
    path = Path("data/fixtures/gan_s0_qwen35b_20260522_pragmatic_error_slice.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    split_data = json.loads(
        Path("data/splits/gan_2026_splits.json").read_text(encoding="utf-8")
    )
    validation_ids = set(split_data["validation"])
    record_ids = [record["record_id"] for record in payload["records"]]
    modes = {record["failure_mode"] for record in payload["records"]}

    assert payload["split_name"] == "gan_2026_fixed_v1:validation"
    assert payload["source_run"].endswith(
        "gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama_20260522T131822Z"
    )
    assert len(record_ids) == 25
    assert len(record_ids) == len(set(record_ids))
    assert set(record_ids) <= validation_ids
    assert "counted_window_no_further_events_over_unknown" in modes
    assert "seizure_free_over_unknown" in modes
    assert "cluster_frequency_over_unknown" in modes


def test_qwen35b_error_taxonomy_policy_config_uses_pragmatic_error_slice():
    fixture = json.loads(
        Path("data/fixtures/gan_s0_qwen35b_20260522_pragmatic_error_slice.json")
        .read_text(encoding="utf-8")
    )
    fixture_ids = [record["record_id"] for record in fixture["records"]]
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_qwen35b_error_taxonomy_policy_cap25.json")
    )

    assert config.experiment_id == "gan_s0_qwen35b_error_taxonomy_policy_cap25"
    assert config.record_ids == fixture_ids
    assert config.max_records is None
    assert (
        config.prompt_version
        == "gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy"
    )
    assert "prompt-only policy test" in " ".join(config.metric_caveats).lower()
