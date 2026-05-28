from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import dspy
from scripts.run_self_consistency import main


def test_run_self_consistency_disables_dspy_cache(tmp_path, capsys):
    # 1. Create a dummy model config file
    model_config_path = tmp_path / "model_config.json"
    model_config_path.write_text(
        json.dumps(
            {
                "provider": "openai",
                "model": "gpt-4.1-mini",
                "api_key_env": "OPENAI_API_KEY",
                "temperature": 0.7,
            }
        ),
        encoding="utf-8",
    )

    # 2. Create a dummy experiment config file
    config_path = tmp_path / "experiment_config.json"
    config_path.write_text(
        json.dumps(
            {
                "experiment_id": "test_self_consistency_cache",
                "hypothesis": "test cache disabled",
                "dataset": "gan_2026",
                "split_name": "gan_2026_fixed_v1:validation",
                "split_file": "data/splits/gan_2026_splits.json",
                "model_config_path": str(model_config_path),
                "prompt_version": "gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy",
                "program_variant": "gan_frequency_s0_temporal_candidates_single_pass",
                "scorer_mode": "gan_frequency_deterministic_v1",
                "structured_output_strategy": "provider_json_schema_with_pydantic_validation",
                "controls": {
                    "few_shot_policy": "none",
                    "context_policy": "full_note_plus_deterministic_temporal_candidates",
                    "verifier_policy": "none",
                    "repair_policy": "artifact_bridge_surface_normalization_only",
                    "abstention_policy": "allow_explicit_abstain",
                },
                "record_ids": ["gan_13058"],
            }
        ),
        encoding="utf-8",
    )

    mock_backend = MagicMock()
    mock_record = MagicMock(record_id="gan_13058", note_text="dummy note text")
    mock_record.gold_label = "1 per month"
    mock_backend.load_records_by_id.return_value = {"gan_13058": mock_record}
    mock_backend.build_module.return_value = MagicMock()
    mock_backend.evaluate_predictions.return_value = {
        "benchmark_metrics": {
            "monthly_frequency_accuracy": 1.0,
            "purist_category_accuracy": 1.0,
            "pragmatic_category_accuracy": 1.0,
        },
        "diagnostic_metrics": {
            "schema_valid_prediction_rate": 1.0,
            "evidence_quote_support_rate": 1.0,
        },
    }

    from clinical_extraction.schemas import DocumentPrediction, ExtractedValue
    mock_val = ExtractedValue(
        field_name="seizure_frequency_number",
        raw_value="1 per month",
        normalized_value="1 per month",
        evidence=[],
        quality_flags=[],
    )
    mock_doc = DocumentPrediction(
        document_id="gan_13058",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        values=[mock_val],
    )

    # Dummy LM configuration
    mock_lm = MagicMock(spec=dspy.LM)
    mock_lm.cache = True  # starts as True

    # Mock all the external calls in run_self_consistency.py
    with patch("scripts.run_self_consistency.get_backend", return_value=mock_backend), \
         patch("scripts.run_self_consistency.build_dspy_lm", return_value=mock_lm) as mock_build_lm, \
         patch("clinical_extraction.experiments.runner.load_split_records", return_value=([mock_record], [])), \
         patch("scripts.run_self_consistency._predict_record", return_value=mock_doc), \
         patch("scripts.run_self_consistency.score_gan_frequency_prediction", return_value={}):

        # We also need to patch output files to avoid writing to actual runs/ directory
        with patch("pathlib.Path.mkdir"), patch("pathlib.Path.write_text"):
            exit_code = main(["--config", str(config_path)])
            assert exit_code == 0

        # Assert that cache was set to False on the built LM
        assert mock_lm.cache is False
