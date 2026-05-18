import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from clinical_extraction.experiments.config import (
    ExperimentConfig,
    load_experiment_config,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_SCORER,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_VARIANT,
)


def test_gan_s0_baseline_experiment_config_records_required_controls():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_baseline_gpt4_1_mini.json")
    )

    assert config.experiment_id == "gan_s0_baseline_gpt4_1_mini"
    assert config.dataset == "gan_2026"
    assert config.split_name == "gan_2026_fixed_v1:validation"
    assert config.split_file == Path("data/splits/gan_2026_splits.json")
    assert config.model_config_path == Path("configs/models/gan_s0_gpt4_1_mini.json")
    assert config.schema_level == GAN_FREQUENCY_S0_SCHEMA_LEVEL
    assert config.program_variant == GAN_FREQUENCY_S0_VARIANT
    assert config.scorer_mode == GAN_FREQUENCY_S0_SCORER
    assert config.prompt_version == "gan_frequency_s0_v1"
    assert config.controls.few_shot_policy == "none"
    assert config.controls.context_policy == "full_note"
    assert config.controls.verifier_policy == "none"
    assert config.controls.repair_policy == "none"
    assert config.controls.abstention_policy == "allow_explicit_abstain_flag"
    assert config.structured_output_strategy == "provider_json_schema_with_pydantic_validation"
    assert not config.report_on_test_split
    assert "monthly-frequency" in " ".join(config.metric_caveats).lower()


def test_gan_s0_synthesis_bootstrap_config_records_optimizer_target():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_synthesis_bootstrap_gpt4_1_mini.json")
    )

    assert config.experiment_id == "gan_s0_synthesis_bootstrap_gpt4_1_mini"
    assert config.prompt_version == "gan_frequency_s0_synthesis_v1"
    assert config.max_records == 25
    assert config.optimizer is not None
    assert config.optimizer.metric_name == "synthesis_exact_with_evidence"
    assert config.optimizer.max_labeled_demos == 4
    assert config.optimizer.trainset_size == 50
    assert config.controls.few_shot_policy == (
        "BootstrapFewShot with synthesis exact-label and evidence-support metric"
    )
    assert "evidence" in " ".join(config.metric_caveats).lower()


def test_experiment_config_rejects_test_reporting_without_explicit_flag():
    payload = json.loads(
        Path("configs/experiments/gan_s0_baseline_gpt4_1_mini.json").read_text(
            encoding="utf-8"
        )
    )
    payload["split_name"] = "gan_2026_fixed_v1:test"
    payload["report_on_test_split"] = False

    with pytest.raises(ValidationError, match="test split"):
        ExperimentConfig.model_validate(payload)


def test_constrained_json_decoding_strategy_note_records_decision_and_fallback():
    note = Path("docs/constrained_json_decoding_strategy.md").read_text(
        encoding="utf-8"
    )

    assert "provider JSON-schema response format" in note
    assert "Pydantic validation" in note
    assert "strict JSON prompt fallback" in note
    assert "GanFrequencyS0Signature" in note
