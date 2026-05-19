import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from clinical_extraction.experiments.config import (
    ExperimentConfig,
    load_experiment_config,
)
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_VARIANT,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
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


def test_gan_s0_synthesis_full_validation_config_removes_precheck_cap():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini.json"
        )
    )

    assert config.experiment_id == (
        "gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini"
    )
    assert config.prompt_version == "gan_frequency_s0_synthesis_v1"
    assert config.max_records is None
    assert config.optimizer is not None
    assert config.optimizer.metric_name == "synthesis_exact_with_evidence"
    assert "full fixed synthetic validation" in " ".join(config.metric_caveats)


def test_gan_s0_gepa_direct_config_records_shared_optimizer_contract():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_gepa_direct_cap5_gpt4_1_mini.json")
    )

    assert config.experiment_id == "gan_s0_gepa_direct_cap5_gpt4_1_mini"
    assert config.dataset == "gan_2026"
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert config.scorer_mode == GAN_FREQUENCY_S0_SCORER
    assert config.max_records == 5
    assert config.optimizer is not None
    assert config.optimizer.name == "GEPA"
    assert config.optimizer.metric_name == "synthesis_exact_with_evidence_feedback"
    assert config.optimizer.trainset_size == 4
    assert config.optimizer.max_metric_calls == 8
    assert config.optimizer.reflection_minibatch_size == 1
    assert config.optimizer.add_format_failure_as_feedback
    assert "optimizer-facing only" in " ".join(config.metric_caveats)


def test_gepa_optimizer_config_requires_feedback_metric():
    payload = json.loads(
        Path("configs/experiments/gan_s0_synthesis_bootstrap_gpt4_1_mini.json").read_text(
            encoding="utf-8"
        )
    )
    payload["optimizer"]["name"] = "GEPA"
    payload["optimizer"]["max_metric_calls"] = 4

    with pytest.raises(ValidationError, match="feedback metric"):
        ExperimentConfig.model_validate(payload)


def test_exect_s0_s1_smoke_config_records_field_family_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s0_s1_smoke_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.split_file == Path("data/splits/exectv2_splits.json")
    assert config.model_config_path == Path("configs/models/gan_s0_gpt4_1_mini.json")
    assert config.schema_level == EXECT_S0_S1_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S0_S1_VARIANT
    assert config.scorer_mode == EXECT_S0_S1_SCORER
    assert config.prompt_version == EXECT_S0_S1_PROMPT_VERSION
    assert config.controls.few_shot_policy == (
        "embedded benchmark-facing label-policy examples"
    )
    assert config.controls.context_policy == "full_note"
    assert config.controls.verifier_policy == "none"
    assert config.controls.repair_policy == "none"
    assert config.max_records == 3
    assert "partial ExECT S0/S1" in " ".join(config.metric_caveats)


def test_exect_s0_s1_validation_cap25_config_records_diagnostic_cap_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s0_s1_validation_cap25_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.split_file == Path("data/splits/exectv2_splits.json")
    assert config.model_config_path == Path("configs/models/gan_s0_gpt4_1_mini.json")
    assert config.schema_level == EXECT_S0_S1_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S0_S1_VARIANT
    assert config.scorer_mode == EXECT_S0_S1_SCORER
    assert config.prompt_version == EXECT_S0_S1_PROMPT_VERSION
    assert config.controls.few_shot_policy == (
        "embedded benchmark-facing label-policy examples"
    )
    assert config.controls.context_policy == "full_note"
    assert config.controls.verifier_policy == "none"
    assert config.controls.repair_policy == "none"
    assert config.max_records == 25
    assert "diagnostic validation cap" in " ".join(config.metric_caveats).lower()


def test_exect_s0_s1_section_aware_cap25_config_keeps_non_architecture_controls_fixed():
    config = load_experiment_config(
        Path("configs/experiments/exect_s0_s1_section_aware_cap25_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s0_s1_section_aware_cap25_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.split_file == Path("data/splits/exectv2_splits.json")
    assert config.model_config_path == Path("configs/models/gan_s0_gpt4_1_mini.json")
    assert config.schema_level == EXECT_S0_S1_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S0_S1_SECTION_AWARE_VARIANT
    assert config.scorer_mode == EXECT_S0_S1_SCORER
    assert config.prompt_version == EXECT_S0_S1_PROMPT_VERSION
    assert config.controls.few_shot_policy == (
        "embedded benchmark-facing label-policy examples"
    )
    assert config.controls.context_policy == "deterministic_section_aware_per_family"
    assert config.controls.verifier_policy == "none"
    assert config.controls.repair_policy == "none"
    assert config.max_records == 25
    assert "architecture ablation" in " ".join(config.metric_caveats).lower()


@pytest.mark.parametrize(
    "filename,model_config_path,experiment_id",
    [
        (
            "gan_s0_smoke_gpt4_1_mini.json",
            "configs/models/gan_s0_gpt4_1_mini.json",
            "gan_s0_smoke_gpt4_1_mini",
        ),
        (
            "gan_s0_smoke_gpt5_5_openai.json",
            "configs/models/gan_s0_gpt5_5_openai.json",
            "gan_s0_smoke_gpt5_5_openai",
        ),
        (
            "gan_s0_smoke_gemini3_flash.json",
            "configs/models/gan_s0_gemini3_flash.json",
            "gan_s0_smoke_gemini3_flash",
        ),
        (
            "gan_s0_smoke_qwen35b_ollama.json",
            "configs/models/gan_s0_qwen35b_ollama.json",
            "gan_s0_smoke_qwen35b_ollama",
        ),
        (
            "gan_s0_smoke_qwen9b_ollama.json",
            "configs/models/gan_s0_qwen9b_ollama.json",
            "gan_s0_smoke_qwen9b_ollama",
        ),
    ],
)
def test_gan_s0_provider_smoke_configs_are_one_record_single_pass_runs(
    filename,
    model_config_path,
    experiment_id,
):
    config = load_experiment_config(Path("configs/experiments") / filename)

    assert config.experiment_id == experiment_id
    assert config.model_config_path == Path(model_config_path)
    assert config.dataset == "gan_2026"
    assert config.split_name == "gan_2026_fixed_v1:validation"
    assert config.max_records == 1
    assert config.optimizer is None
    assert config.program_variant == GAN_FREQUENCY_S0_VARIANT
    assert config.scorer_mode == GAN_FREQUENCY_S0_SCORER
    assert "smoke run" in " ".join(config.metric_caveats).lower()
    assert not config.report_on_test_split


@pytest.mark.parametrize(
    "filename,program_variant,optimizer_expected",
    [
        (
            "gan_s0_latency_qwen9b_direct_cap3.json",
            GAN_FREQUENCY_S0_DIRECT_VARIANT,
            False,
        ),
        (
            "gan_s0_latency_qwen9b_cot_cap3.json",
            GAN_FREQUENCY_S0_VARIANT,
            False,
        ),
        (
            "gan_s0_latency_qwen9b_direct_bootstrap_cap3.json",
            GAN_FREQUENCY_S0_DIRECT_VARIANT,
            True,
        ),
        (
            "gan_s0_latency_qwen9b_cot_bootstrap_cap3.json",
            GAN_FREQUENCY_S0_VARIANT,
            True,
        ),
    ],
)
def test_qwen9b_latency_ablation_configs_hold_split_and_cap_fixed(
    filename,
    program_variant,
    optimizer_expected,
):
    config = load_experiment_config(Path("configs/experiments") / filename)

    assert config.dataset == "gan_2026"
    assert config.model_config_path == Path("configs/models/gan_s0_qwen9b_ollama.json")
    assert config.split_name == "gan_2026_fixed_v1:validation"
    assert config.max_records == 3
    assert config.program_variant == program_variant
    assert config.scorer_mode == GAN_FREQUENCY_S0_SCORER
    assert (config.optimizer is not None) is optimizer_expected
    assert "latency" in " ".join(config.metric_caveats).lower()


def test_qwen35b_direct_gate_configs_avoid_reasoning_and_optimizer():
    smoke = load_experiment_config(
        Path("configs/experiments/gan_s0_smoke_qwen35b_direct_ollama.json")
    )
    cap = load_experiment_config(
        Path("configs/experiments/gan_s0_latency_qwen35b_direct_cap3.json")
    )

    for config in [smoke, cap]:
        assert config.model_config_path == Path("configs/models/gan_s0_qwen35b_ollama.json")
        assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
        assert config.optimizer is None
        assert "avoids chainofthought and bootstrapfewshot" in (
            " ".join(config.metric_caveats).lower()
        )
    assert smoke.max_records == 1
    assert cap.max_records == 3


@pytest.mark.parametrize(
    "filename,model_config_path,program_variant,optimizer_expected,max_records",
    [
        (
            "gan_s0_maxbudget_qwen9b_direct_cap3.json",
            "configs/models/gan_s0_qwen9b_ollama_max81920.json",
            GAN_FREQUENCY_S0_DIRECT_VARIANT,
            False,
            3,
        ),
        (
            "gan_s0_maxbudget_qwen9b_cot_cap3.json",
            "configs/models/gan_s0_qwen9b_ollama_max81920.json",
            GAN_FREQUENCY_S0_VARIANT,
            False,
            3,
        ),
        (
            "gan_s0_maxbudget_qwen9b_direct_bootstrap_cap3.json",
            "configs/models/gan_s0_qwen9b_ollama_max81920.json",
            GAN_FREQUENCY_S0_DIRECT_VARIANT,
            True,
            3,
        ),
        (
            "gan_s0_maxbudget_qwen9b_cot_bootstrap_cap3.json",
            "configs/models/gan_s0_qwen9b_ollama_max81920.json",
            GAN_FREQUENCY_S0_VARIANT,
            True,
            3,
        ),
        (
            "gan_s0_maxbudget_qwen35b_direct_cap1.json",
            "configs/models/gan_s0_qwen35b_ollama_max81920.json",
            GAN_FREQUENCY_S0_DIRECT_VARIANT,
            False,
            1,
        ),
        (
            "gan_s0_maxbudget_qwen35b_cot_cap1.json",
            "configs/models/gan_s0_qwen35b_ollama_max81920.json",
            GAN_FREQUENCY_S0_VARIANT,
            False,
            1,
        ),
    ],
)
def test_qwen_maxbudget_configs_raise_output_budget_without_changing_split_or_scorer(
    filename,
    model_config_path,
    program_variant,
    optimizer_expected,
    max_records,
):
    config = load_experiment_config(Path("configs/experiments") / filename)
    model_config_payload = json.loads(Path(model_config_path).read_text(encoding="utf-8"))

    assert config.dataset == "gan_2026"
    assert config.model_config_path == Path(model_config_path)
    assert model_config_payload["max_tokens"] == 81920
    assert model_config_payload["extra_body"]["options"]["num_ctx"] == 262144
    assert config.split_name == "gan_2026_fixed_v1:validation"
    assert config.max_records == max_records
    assert config.program_variant == program_variant
    assert config.scorer_mode == GAN_FREQUENCY_S0_SCORER
    assert (config.optimizer is not None) is optimizer_expected
    assert "max_tokens" in " ".join(config.metric_caveats).lower()
    assert "thinking disabled" in " ".join(config.metric_caveats).lower()


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
