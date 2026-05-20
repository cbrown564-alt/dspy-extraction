import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from clinical_extraction.experiments.config import (
    ExperimentConfig,
    load_experiment_config,
)
from clinical_extraction.experiments.taxonomy import (
    ExperimentTaxonomy,
    registry_experiment_ids,
)
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
    EXECT_S0_S1_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_V3_PROMPT_VERSION,
    EXECT_S0_S1_V4_1_PROMPT_VERSION,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_VARIANT,
    EXECT_S0_S1_VERIFY_REPAIR_PROMPT_VERSION,
    EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
    REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY,
)
from clinical_extraction.programs.exect_s2 import (
    EXECT_S2_PROMPT_VERSION,
    EXECT_S2_SCHEMA_LEVEL,
    EXECT_S2_SCORER,
    EXECT_S2_VARIANT,
)
from clinical_extraction.programs.exect_s3 import (
    EXECT_S3_PROMPT_VERSION,
    EXECT_S3_SCHEMA_LEVEL,
    EXECT_S3_SCORER,
    EXECT_S3_VARIANT,
)
from clinical_extraction.programs.exect_s4 import (
    EXECT_S4_PROMPT_VERSION,
    EXECT_S4_SCHEMA_LEVEL,
    EXECT_S4_SCORER,
    EXECT_S4_VARIANT,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_SCORER,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
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
    assert config.optimizer.max_full_evals is None
    assert config.optimizer.reflection_minibatch_size == 1
    assert config.optimizer.add_format_failure_as_feedback
    assert config.optimizer.use_cloudpickle
    assert "optimizer-facing only" in " ".join(config.metric_caveats)


def test_qwen35b_gepa_probe_config_keeps_gepa_contract_but_marks_local_latency_scope():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_gepa_direct_cap5_qwen35b_ollama.json")
    )

    assert config.experiment_id == "gan_s0_gepa_direct_cap5_qwen35b_ollama"
    assert config.dataset == "gan_2026"
    assert config.model_config_path == Path(
        "configs/models/gan_s0_qwen35b_ollama_gepa_max10000.json"
    )
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert config.scorer_mode == GAN_FREQUENCY_S0_SCORER
    assert config.max_records == 5
    assert config.optimizer is not None
    assert config.optimizer.name == "GEPA"
    assert config.optimizer.metric_name == "synthesis_exact_with_evidence_feedback"
    assert config.optimizer.trainset_size == 4
    assert config.optimizer.max_metric_calls == 8
    assert config.optimizer.max_full_evals is None
    assert config.optimizer.reflection_minibatch_size == 1
    assert config.optimizer.add_format_failure_as_feedback
    assert config.optimizer.use_cloudpickle
    caveats = " ".join(config.metric_caveats).lower()
    assert "latency-and-transfer probe" in caveats
    assert "10000" in caveats
    assert "truncation" in caveats
    assert "explicit optimizer experiment" in caveats


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


def test_gepa_optimizer_config_rejects_multiple_budget_controls():
    payload = json.loads(
        Path("configs/experiments/gan_s0_gepa_direct_cap5_gpt4_1_mini.json").read_text(
            encoding="utf-8"
        )
    )
    payload["optimizer"]["max_full_evals"] = 2

    with pytest.raises(ValidationError, match="exactly one"):
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


def test_exect_s2_smoke_config_records_s2_field_family_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s2_smoke_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s2_smoke_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.schema_level == EXECT_S2_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S2_VARIANT
    assert config.scorer_mode == EXECT_S2_SCORER
    assert config.prompt_version == EXECT_S2_PROMPT_VERSION
    assert config.max_records == 3
    assert "partial ExECT S2" in " ".join(config.metric_caveats)


def test_exect_s3_smoke_config_records_s3_field_family_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s3_smoke_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s3_smoke_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.schema_level == EXECT_S3_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S3_VARIANT
    assert config.scorer_mode == EXECT_S3_SCORER
    assert config.prompt_version == EXECT_S3_PROMPT_VERSION
    assert config.max_records == 3
    assert "partial ExECT S3" in " ".join(config.metric_caveats)
    assert "nine" in " ".join(config.metric_caveats).lower()


def test_exect_s3_validation_cap25_config_records_s3_diagnostic_cap_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s3_validation_cap25_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s3_validation_cap25_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.schema_level == EXECT_S3_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S3_VARIANT
    assert config.scorer_mode == EXECT_S3_SCORER
    assert config.prompt_version == EXECT_S3_PROMPT_VERSION
    assert config.max_records == 25
    assert "diagnostic validation cap" in " ".join(config.metric_caveats).lower()
    assert "frozen v1.3" in " ".join(config.metric_caveats) or "frozen S2" in " ".join(
        config.metric_caveats
    )


def test_exect_s3_validation_full_config_removes_precheck_cap():
    config = load_experiment_config(
        Path("configs/experiments/exect_s3_validation_full_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s3_validation_full_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.max_records is None
    assert config.schema_level == EXECT_S3_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S3_VARIANT
    assert config.scorer_mode == EXECT_S3_SCORER
    assert config.prompt_version == EXECT_S3_PROMPT_VERSION
    assert "full fixed ExECTv2 validation split" in " ".join(config.metric_caveats)


def test_exect_s4_smoke_config_records_s4_field_family_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s4_smoke_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s4_smoke_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.schema_level == EXECT_S4_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S4_VARIANT
    assert config.scorer_mode == EXECT_S4_SCORER
    assert config.prompt_version == EXECT_S4_PROMPT_VERSION
    assert config.max_records == 3
    assert "partial ExECT S4" in " ".join(config.metric_caveats)
    assert "eleven" in " ".join(config.metric_caveats).lower()


def test_exect_s4_validation_cap25_config_records_s4_diagnostic_cap_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s4_validation_cap25_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s4_validation_cap25_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.schema_level == EXECT_S4_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S4_VARIANT
    assert config.scorer_mode == EXECT_S4_SCORER
    assert config.prompt_version == EXECT_S4_PROMPT_VERSION
    assert config.max_records == 25
    assert "diagnostic validation cap" in " ".join(config.metric_caveats).lower()
    assert "frozen v1.2" in " ".join(config.metric_caveats) or "frozen S3" in " ".join(
        config.metric_caveats
    )


def test_exect_s4_validation_full_config_removes_precheck_cap():
    config = load_experiment_config(
        Path("configs/experiments/exect_s4_validation_full_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s4_validation_full_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.max_records is None
    assert config.schema_level == EXECT_S4_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S4_VARIANT
    assert config.scorer_mode == EXECT_S4_SCORER
    assert config.prompt_version == EXECT_S4_PROMPT_VERSION
    assert "full fixed ExECTv2 validation split" in " ".join(config.metric_caveats)


def test_exect_s2_validation_cap25_config_records_s2_diagnostic_cap_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s2_validation_cap25_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.schema_level == EXECT_S2_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S2_VARIANT
    assert config.scorer_mode == EXECT_S2_SCORER
    assert config.prompt_version == EXECT_S2_PROMPT_VERSION
    assert config.max_records == 25
    assert "diagnostic validation cap" in " ".join(config.metric_caveats).lower()
    assert "frozen v4.10" in " ".join(config.metric_caveats)


def test_exect_s2_validation_full_config_removes_precheck_cap():
    config = load_experiment_config(
        Path("configs/experiments/exect_s2_validation_full_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s2_validation_full_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.max_records is None
    assert config.schema_level == EXECT_S2_SCHEMA_LEVEL
    assert config.program_variant == EXECT_S2_VARIANT
    assert config.scorer_mode == EXECT_S2_SCORER
    assert config.prompt_version == EXECT_S2_PROMPT_VERSION
    assert "full fixed ExECTv2 validation split" in " ".join(config.metric_caveats)


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


def test_exect_s0_s1_validation_full_config_removes_precheck_cap():
    config = load_experiment_config(
        Path("configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s0_s1_validation_full_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.max_records is None
    assert config.program_variant == EXECT_S0_S1_VARIANT
    assert config.prompt_version == EXECT_S0_S1_PROMPT_VERSION
    assert "full fixed ExECTv2 validation split" in " ".join(config.metric_caveats)


def test_exect_s0_s1_validation_test_config_records_one_shot_holdout_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s0_s1_validation_test_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s0_s1_validation_test_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:test"
    assert config.split_file == Path("data/splits/exectv2_splits.json")
    assert config.max_records is None
    assert config.program_variant == EXECT_S0_S1_VARIANT
    assert config.prompt_version == EXECT_S0_S1_PROMPT_VERSION
    assert config.scorer_mode == EXECT_S0_S1_SCORER
    assert config.report_on_test_split
    assert not config.record_ids
    caveats = " ".join(config.metric_caveats).lower()
    assert "one-shot" in caveats
    assert "do not tune" in caveats
    assert "92.3%" in " ".join(config.metric_caveats)


def test_exect_s0_s1_label_policy_regression_slice_config_records_v4_contract():
    fixture = json.loads(
        Path("data/fixtures/exect_s0_label_policy_error_regression_slice.json").read_text(
            encoding="utf-8"
        )
    )
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json"
        )
    )

    assert config.experiment_id == "exect_s0_s1_label_policy_regression_slice_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.prompt_version == EXECT_S0_S1_PROMPT_VERSION
    assert config.program_variant == EXECT_S0_S1_VARIANT
    assert config.scorer_mode == EXECT_S0_S1_SCORER
    fixture_ids = [record["record_id"] for record in fixture["records"]]
    assert config.record_ids == fixture_ids
    assert len(fixture_ids) == 37
    assert "label-policy regression slice" in " ".join(config.metric_caveats).lower()


def test_exect_s0_s1_verify_repair_cap25_config_records_probe_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s0_s1_verify_repair_cap25_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s0_s1_verify_repair_cap25_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.program_variant == EXECT_S0_S1_VERIFY_REPAIR_VARIANT
    assert config.prompt_version == EXECT_S0_S1_VERIFY_REPAIR_PROMPT_VERSION
    assert config.max_records == 25
    assert config.scorer_mode == "exect_field_family_deterministic_v1"
    assert "confirm-first" in config.controls.verifier_policy


def test_exect_s0_s1_diagnosis_recall_regression_slice_config_records_probe_contract():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "exect_s0_s1_diagnosis_recall_regression_slice_gpt4_1_mini.json"
        )
    )

    assert config.experiment_id == "exect_s0_s1_diagnosis_recall_regression_slice_gpt4_1_mini"
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.program_variant == EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT
    assert config.prompt_version == "exect_s0_s1_diagnosis_recall_v1"
    assert config.scorer_mode == EXECT_S0_S1_SCORER
    assert config.record_ids == [
        "EA0045",
        "EA0061",
        "EA0098",
        "EA0116",
        "EA0125",
        "EA0131",
        "EA0137",
        "EA0143",
        "EA0148",
        "EA0150",
        "EA0170",
        "EA0173",
        "EA0174",
        "EA0188",
    ]
    assert config.controls.repair_policy == "add_only_diagnosis_recall_merge_with_deterministic_guards"
    assert "diagnosis-recall slice" in " ".join(config.metric_caveats).lower()


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
    assert config.prompt_version == EXECT_S0_S1_V3_PROMPT_VERSION
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


def test_qwen35b_guardrails_validation_config_pins_direct_path_and_cap25():
    config = load_experiment_config(
        Path(
            "configs/experiments/gan_s0_qwen35b_direct_cap25_guardrails_validation.json"
        )
    )

    assert config.experiment_id == "gan_s0_qwen35b_direct_cap25_guardrails_validation"
    assert config.model_config_path == Path("configs/models/gan_s0_qwen35b_ollama.json")
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert config.prompt_version == "gan_frequency_s0_direct_guardrails_v2_2"
    assert config.max_records == 25
    assert config.optimizer is None
    assert config.controls.repair_policy == "artifact_bridge_surface_normalization_only"
    assert "post-guardrail" in " ".join(config.metric_caveats).lower()


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


def test_qwen35b_full_validation_guardrails_config_removes_cap():
    config = load_experiment_config(
        Path(
            "configs/experiments/gan_s0_qwen35b_direct_full_validation_guardrails.json"
        )
    )

    assert config.experiment_id == "gan_s0_qwen35b_direct_full_validation_guardrails"
    assert config.model_config_path == Path("configs/models/gan_s0_qwen35b_ollama.json")
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert config.prompt_version == "gan_frequency_s0_direct_guardrails_v2_2"
    assert config.max_records is None
    assert config.optimizer is None
    assert config.controls.repair_policy == "artifact_bridge_surface_normalization_only"
    assert "full-validation" in " ".join(config.metric_caveats).lower()


def test_qwen35b_regression_slice_config_uses_record_ids_filter():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_direct_regression_slice_guardrails.json"
        )
    )

    assert config.experiment_id == "gan_s0_qwen35b_direct_regression_slice_guardrails"
    assert config.record_ids is not None
    assert len(config.record_ids) == 14
    assert "gan_10509" in config.record_ids
    assert config.max_records is None


def test_experiment_config_accepts_verify_repair_variant():
    payload = json.loads(
        Path("configs/experiments/gan_s0_baseline_gpt4_1_mini.json").read_text(
            encoding="utf-8"
        )
    )
    payload["program_variant"] = GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT
    payload["controls"]["verifier_policy"] = "dspy_predict_verifier_after_extraction"

    config = ExperimentConfig.model_validate(payload)
    assert config.program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT
    assert config.controls.verifier_policy == "dspy_predict_verifier_after_extraction"


def test_verify_repair_full_validation_config_has_no_cap():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_verify_repair_full_validation_gpt4_1_mini.json"
        )
    )

    assert config.experiment_id == (
        "gan_s0_verify_repair_full_validation_gpt4_1_mini"
    )
    assert config.program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT
    assert config.prompt_version == "gan_frequency_s0_direct_verify_repair_v2"
    assert config.max_records is None
    assert config.optimizer is None
    assert "full fixed synthetic validation" in " ".join(config.metric_caveats).lower()


@pytest.mark.parametrize(
    "filename,optimizer_name,max_labeled_demos,max_bootstrapped_demos",
    [
        (
            "gan_s0_ladder_labeled_fewshot_cap25_gpt4_1_mini.json",
            "LabeledFewShot",
            4,
            0,
        ),
        (
            "gan_s0_ladder_bootstrap_cap25_gpt4_1_mini.json",
            "BootstrapFewShot",
            4,
            4,
        ),
        (
            "gan_s0_ladder_bootstrap_rs_cap25_gpt4_1_mini.json",
            "BootstrapFewShotWithRandomSearch",
            4,
            4,
        ),
    ],
)
def test_gan_s0_few_shot_ladder_configs_pin_direct_synthesis_contract(
    filename,
    optimizer_name,
    max_labeled_demos,
    max_bootstrapped_demos,
):
    config = load_experiment_config(Path("configs/experiments") / filename)

    assert config.dataset == "gan_2026"
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert config.prompt_version == "gan_frequency_s0_synthesis_v1"
    assert config.max_records == 25
    assert config.optimizer is not None
    assert config.optimizer.name == optimizer_name
    assert config.optimizer.metric_name == "synthesis_exact_with_evidence"
    assert config.optimizer.trainset_size == 50
    assert config.optimizer.max_labeled_demos == max_labeled_demos
    assert config.optimizer.max_bootstrapped_demos == max_bootstrapped_demos
    assert "direct single-pass path" in " ".join(config.metric_caveats).lower()


@pytest.mark.parametrize(
    "filename,optimizer_name,max_labeled_demos,max_bootstrapped_demos",
    [
        (
            "gan_s0_cot_ladder_labeled_fewshot_cap25_gpt4_1_mini.json",
            "LabeledFewShot",
            4,
            0,
        ),
        (
            "gan_s0_cot_ladder_bootstrap_cap25_gpt4_1_mini.json",
            "BootstrapFewShot",
            4,
            4,
        ),
        (
            "gan_s0_cot_ladder_bootstrap_rs_cap25_gpt4_1_mini.json",
            "BootstrapFewShotWithRandomSearch",
            4,
            4,
        ),
    ],
)
def test_gan_s0_cot_few_shot_ladder_configs_pin_cot_synthesis_contract(
    filename,
    optimizer_name,
    max_labeled_demos,
    max_bootstrapped_demos,
):
    config = load_experiment_config(Path("configs/experiments") / filename)

    assert config.dataset == "gan_2026"
    assert config.program_variant == GAN_FREQUENCY_S0_VARIANT
    assert config.prompt_version == "gan_frequency_s0_synthesis_v1"
    assert config.max_records == 25
    assert config.optimizer is not None
    assert config.optimizer.name == optimizer_name
    assert config.optimizer.metric_name == "synthesis_exact_with_evidence"
    assert config.optimizer.trainset_size == 50
    assert config.optimizer.max_labeled_demos == max_labeled_demos
    assert config.optimizer.max_bootstrapped_demos == max_bootstrapped_demos
    assert "cot single-pass path" in " ".join(config.metric_caveats).lower()


def test_gan_s0_ladder_zero_shot_config_matches_direct_ladder_surface():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_ladder_zero_shot_cap25_gpt4_1_mini.json")
    )

    assert config.dataset == "gan_2026"
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert config.prompt_version == "gan_frequency_s0_synthesis_v1"
    assert config.max_records == 25
    assert config.optimizer is None
    assert config.controls.few_shot_policy == "none"
    assert "extraction-only" in " ".join(config.metric_caveats).lower()


def test_labeled_fewshot_optimizer_config_requires_positive_demo_count():
    payload = json.loads(
        Path(
            "configs/experiments/gan_s0_ladder_labeled_fewshot_cap25_gpt4_1_mini.json"
        ).read_text(encoding="utf-8")
    )
    payload["optimizer"]["max_labeled_demos"] = 0

    with pytest.raises(ValidationError, match="max_labeled_demos"):
        ExperimentConfig.model_validate(payload)


def test_verify_repair_cap25_config_uses_v2_prompt():
    config = ExperimentConfig.model_validate(
        json.loads(
            Path(
                "configs/experiments/gan_s0_verify_repair_cap25_gpt4_1_mini.json"
            ).read_text(encoding="utf-8")
        )
    )
    assert config.program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT
    assert config.prompt_version == "gan_frequency_s0_direct_verify_repair_v2"


def test_gan_s0_semantic_bootstrap_cap25_config_records_semantic_optimizer():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_semantic_bootstrap_cap25_gpt4_1_mini.json")
    )

    assert config.experiment_id == "gan_s0_semantic_bootstrap_cap25_gpt4_1_mini"
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert config.scorer_mode == GAN_FREQUENCY_S0_SCORER
    assert config.max_records == 25
    assert config.optimizer is not None
    assert config.optimizer.name == "BootstrapFewShot"
    assert config.optimizer.metric_name == "semantic_frequency_with_evidence"
    assert config.optimizer.trainset_size == 50
    caveats = " ".join(config.metric_caveats).lower()
    assert "optimizer-facing only" in caveats
    assert "gan_frequency_deterministic_v1" in caveats
    assert "verify-repair v2" in caveats


def test_gan_s0_semantic_bootstrap_full_validation_config_has_no_cap():
    config = load_experiment_config(
        Path(
            "configs/experiments/gan_s0_semantic_bootstrap_full_validation_gpt4_1_mini.json"
        )
    )

    assert config.experiment_id == "gan_s0_semantic_bootstrap_full_validation_gpt4_1_mini"
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert config.max_records is None
    assert config.optimizer is not None
    assert config.optimizer.metric_name == "semantic_frequency_with_evidence"
    assert "full fixed synthetic validation" in " ".join(config.metric_caveats).lower()


def test_gan_s0_smoke_gemini31_flash_lite_config_records_direct_contract():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_smoke_gemini31_flash_lite.json")
    )

    assert config.experiment_id == "gan_s0_smoke_gemini31_flash_lite"
    assert config.model_config_path == Path("configs/models/gan_s0_gemini31_flash_lite.json")
    assert config.max_records == 1
    assert config.optimizer is None
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert config.scorer_mode == GAN_FREQUENCY_S0_SCORER
    assert "gemini-3.1-flash-lite" in " ".join(config.metric_caveats).lower()
    assert "smoke run" in " ".join(config.metric_caveats).lower()


def test_gan_s0_direct_cap25_gemini31_flash_lite_config_records_matched_slice():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_direct_cap25_gemini31_flash_lite.json")
    )

    assert config.experiment_id == "gan_s0_direct_cap25_gemini31_flash_lite"
    assert config.model_config_path == Path("configs/models/gan_s0_gemini31_flash_lite.json")
    assert config.max_records == 25
    assert config.optimizer is None
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    caveats = " ".join(config.metric_caveats).lower()
    assert "verify-repair v2" in caveats
    assert "gemini-3.1-flash-lite" in caveats


def test_gan_s0_verify_repair_cap25_gemini31_flash_lite_config_records_v2_contract():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_verify_repair_cap25_gemini31_flash_lite.json")
    )

    assert config.experiment_id == "gan_s0_verify_repair_cap25_gemini31_flash_lite"
    assert config.model_config_path == Path("configs/models/gan_s0_gemini31_flash_lite.json")
    assert config.max_records == 25
    assert config.optimizer is None
    assert config.program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT
    assert config.prompt_version == "gan_frequency_s0_direct_verify_repair_v2"
    caveats = " ".join(config.metric_caveats).lower()
    assert "gemini" in caveats
    assert "verify-repair v2" in caveats


def test_gan_s0_direct_full_validation_gemini31_flash_lite_config_has_no_cap():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_direct_full_validation_gemini31_flash_lite.json")
    )

    assert config.experiment_id == "gan_s0_direct_full_validation_gemini31_flash_lite"
    assert config.model_config_path == Path("configs/models/gan_s0_gemini31_flash_lite.json")
    assert config.max_records is None
    assert config.optimizer is None
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    caveats = " ".join(config.metric_caveats).lower()
    assert "full fixed synthetic validation" in caveats
    assert "gemini" in caveats


def test_gan_s0_semantic_labeled_fewshot_cap25_config_records_semantic_metric():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_semantic_labeled_fewshot_cap25_gpt4_1_mini.json")
    )

    assert config.experiment_id == "gan_s0_semantic_labeled_fewshot_cap25_gpt4_1_mini"
    assert config.max_records == 25
    assert config.optimizer is not None
    assert config.optimizer.name == "LabeledFewShot"
    assert config.optimizer.metric_name == "semantic_frequency_with_evidence"
    assert config.optimizer.max_bootstrapped_demos == 0
    assert config.optimizer.max_labeled_demos == 4
    caveats = " ".join(config.metric_caveats).lower()
    assert "optimizer-facing only" in caveats
    assert "verify-repair v2" in caveats


def test_gan_s0_semantic_gepa_cap25_config_records_semantic_feedback_metric():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_semantic_gepa_cap25_gpt4_1_mini.json")
    )

    assert config.experiment_id == "gan_s0_semantic_gepa_cap25_gpt4_1_mini"
    assert config.max_records == 25
    assert config.optimizer is not None
    assert config.optimizer.name == "GEPA"
    assert config.optimizer.metric_name == "semantic_frequency_with_evidence_feedback"
    assert config.optimizer.max_metric_calls == 16
    assert config.optimizer.trainset_size == 50
    assert config.optimizer.use_cloudpickle
    caveats = " ".join(config.metric_caveats).lower()
    assert "optimizer-facing only" in caveats
    assert "verify-repair v2" in caveats


def test_qwen35b_verify_repair_regression_slice_config_uses_v2_4_and_record_ids():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_verify_repair_regression_slice_guardrails.json"
        )
    )

    assert (
        config.experiment_id
        == "gan_s0_qwen35b_verify_repair_regression_slice_guardrails"
    )
    assert config.model_config_path == Path(
        "configs/models/gan_s0_qwen35b_ollama_verify_repair.json"
    )
    assert config.program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT
    assert config.prompt_version == "gan_frequency_s0_direct_verify_repair_v2_4"
    assert config.record_ids is not None
    assert len(config.record_ids) == 14
    assert "gan_13123" in config.record_ids
    assert config.optimizer is None
    assert "confirm-first" in config.controls.verifier_policy.lower()


def test_qwen35b_verify_repair_cap25_config_uses_v2_4():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_verify_repair_cap25_guardrails_validation.json"
        )
    )

    assert config.experiment_id == "gan_s0_qwen35b_verify_repair_cap25_guardrails_validation"
    assert config.model_config_path == Path(
        "configs/models/gan_s0_qwen35b_ollama_verify_repair.json"
    )
    assert config.program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT
    assert config.prompt_version == "gan_frequency_s0_direct_verify_repair_v2_4"
    assert config.max_records == 25
    assert config.optimizer is None
    assert "37.5%" in " ".join(config.metric_caveats)


def test_qwen35b_verify_repair_model_config_raises_max_tokens_for_verifier_reason():
    model_config = json.loads(
        Path("configs/models/gan_s0_qwen35b_ollama_verify_repair.json").read_text(
            encoding="utf-8"
        )
    )
    baseline = json.loads(
        Path("configs/models/gan_s0_qwen35b_ollama.json").read_text(encoding="utf-8")
    )

    assert model_config["max_tokens"] > baseline["max_tokens"]


def test_qwen35b_labeled_fewshot_regression_slice_config_uses_synthesis_optimizer():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_labeled_fewshot_regression_slice_guardrails.json"
        )
    )

    assert (
        config.experiment_id
        == "gan_s0_qwen35b_labeled_fewshot_regression_slice_guardrails"
    )
    assert config.model_config_path == Path("configs/models/gan_s0_qwen35b_ollama.json")
    assert config.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert config.prompt_version == "gan_frequency_s0_direct_guardrails_v2_2"
    assert config.record_ids is not None
    assert len(config.record_ids) == 14
    assert config.optimizer is not None
    assert config.optimizer.name == "LabeledFewShot"
    assert config.optimizer.metric_name == "synthesis_exact_with_evidence"
    assert config.optimizer.max_labeled_demos == 4


def test_qwen35b_labeled_fewshot_verify_repair_regression_slice_config():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_labeled_fewshot_verify_repair_regression_slice_guardrails.json"
        )
    )

    assert (
        config.experiment_id
        == "gan_s0_qwen35b_labeled_fewshot_verify_repair_regression_slice_guardrails"
    )
    assert config.model_config_path == Path(
        "configs/models/gan_s0_qwen35b_ollama_verify_repair.json"
    )
    assert config.program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT
    assert config.prompt_version == "gan_frequency_s0_direct_verify_repair_v2_4"
    assert config.record_ids is not None
    assert len(config.record_ids) == 14
    assert config.optimizer is not None
    assert config.optimizer.name == "LabeledFewShot"
    assert config.optimizer.metric_name == "synthesis_exact_with_evidence"
    assert config.optimizer.max_labeled_demos == 4
    assert "hybrid" in config.hypothesis.lower()
    assert "confirm-first" in config.controls.verifier_policy.lower()


def test_qwen35b_temporal_candidates_verify_repair_regression_slice_config():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails.json"
        )
    )

    assert (
        config.experiment_id
        == "gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails"
    )
    assert config.model_config_path == Path(
        "configs/models/gan_s0_qwen35b_ollama_verify_repair.json"
    )
    assert (
        config.program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT
    )
    assert config.prompt_version == "gan_frequency_s0_temporal_candidates_verify_repair_v1_1"
    assert config.record_ids is not None
    assert len(config.record_ids) == 14
    assert config.optimizer is None
    assert "temporal" in config.hypothesis.lower()
    assert "temporal" in config.controls.context_policy.lower()


def test_qwen35b_temporal_event_table_regression_slice_config():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_temporal_event_table_regression_slice_guardrails.json"
        )
    )

    assert (
        config.experiment_id
        == "gan_s0_qwen35b_temporal_event_table_regression_slice_guardrails"
    )
    assert (
        config.program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT
    )
    assert config.prompt_version == "gan_frequency_s0_temporal_event_table_verify_repair_v1_0"
    assert len(config.record_ids or []) == 14
    assert "event table" in config.hypothesis.lower()
    assert "event_table" in config.controls.context_policy.lower()


def test_qwen35b_react_temporal_tools_regression_slice_config():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json"
        )
    )

    assert (
        config.experiment_id
        == "gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails"
    )
    assert config.program_variant == GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT
    assert config.prompt_version == "gan_frequency_s0_react_temporal_tools_v1_1"
    assert len(config.record_ids or []) == 14
    assert "react" in config.hypothesis.lower()
    assert "react" in config.controls.context_policy.lower()


def test_qwen35b_temporal_candidates_verify_repair_cap25_config():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_temporal_candidates_verify_repair_cap25_guardrails_validation.json"
        )
    )

    assert (
        config.experiment_id
        == "gan_s0_qwen35b_temporal_candidates_verify_repair_cap25_guardrails_validation"
    )
    assert config.max_records == 25
    assert (
        config.program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT
    )
    assert config.prompt_version == "gan_frequency_s0_temporal_candidates_verify_repair_v1_1"
    assert config.record_ids is None
    assert "37.5%" in " ".join(config.metric_caveats)


def test_gpt4_1_mini_temporal_candidates_verify_repair_cap25_config():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_cap25_guardrails_validation.json"
        )
    )

    assert (
        config.experiment_id
        == "gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_cap25_guardrails_validation"
    )
    assert config.model_config_path == Path("configs/models/gan_s0_gpt4_1_mini.json")
    assert config.max_records == 25
    assert (
        config.program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT
    )
    assert config.prompt_version == "gan_frequency_s0_temporal_candidates_verify_repair_v1_1"
    assert config.record_ids is None
    assert "34.8%" in " ".join(config.metric_caveats)


def test_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_config():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails.json"
        )
    )

    assert (
        config.experiment_id
        == "gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails"
    )
    assert config.model_config_path == Path("configs/models/gan_s0_gpt4_1_mini.json")
    assert config.max_records is None
    assert (
        config.program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT
    )
    assert config.prompt_version == "gan_frequency_s0_temporal_candidates_verify_repair_v1_1"
    assert config.record_ids is None
    assert "65.4%" in " ".join(config.metric_caveats)


def test_qwen35b_temporal_candidates_verify_repair_full_validation_config():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails.json"
        )
    )

    assert (
        config.experiment_id
        == "gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails"
    )
    assert config.model_config_path == Path(
        "configs/models/gan_s0_qwen35b_ollama_verify_repair.json"
    )
    assert config.max_records is None
    assert (
        config.program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT
    )
    assert config.prompt_version == "gan_frequency_s0_temporal_candidates_verify_repair_v1_1"
    assert config.record_ids is None
    assert config.optimizer is None
    assert "55.9%" in " ".join(config.metric_caveats)
    assert "cap-25" in " ".join(config.metric_caveats).lower()


EXECT_QWEN35B_MODEL_CONFIG = Path("configs/models/exect_qwen35b_ollama.json")


@pytest.mark.parametrize(
    "filename,expected_id,prompt_version,program_variant,schema_level,scorer_mode,max_records",
    [
        (
            "exect_s0_s1_smoke_qwen35b_ollama.json",
            "exect_s0_s1_smoke_qwen35b_ollama",
            EXECT_S0_S1_PROMPT_VERSION,
            EXECT_S0_S1_VARIANT,
            EXECT_S0_S1_SCHEMA_LEVEL,
            EXECT_S0_S1_SCORER,
            3,
        ),
        (
            "exect_s0_s1_validation_cap25_qwen35b_ollama.json",
            "exect_s0_s1_validation_cap25_qwen35b_ollama",
            EXECT_S0_S1_PROMPT_VERSION,
            EXECT_S0_S1_VARIANT,
            EXECT_S0_S1_SCHEMA_LEVEL,
            EXECT_S0_S1_SCORER,
            25,
        ),
        (
            "exect_s0_s1_validation_full_qwen35b_ollama.json",
            "exect_s0_s1_validation_full_qwen35b_ollama",
            EXECT_S0_S1_PROMPT_VERSION,
            EXECT_S0_S1_VARIANT,
            EXECT_S0_S1_SCHEMA_LEVEL,
            EXECT_S0_S1_SCORER,
            None,
        ),
        (
            "exect_s0_s1_label_policy_regression_slice_qwen35b_ollama.json",
            "exect_s0_s1_label_policy_regression_slice_qwen35b_ollama",
            EXECT_S0_S1_PROMPT_VERSION,
            EXECT_S0_S1_VARIANT,
            EXECT_S0_S1_SCHEMA_LEVEL,
            EXECT_S0_S1_SCORER,
            None,
        ),
        (
            "exect_s2_smoke_qwen35b_ollama.json",
            "exect_s2_smoke_qwen35b_ollama",
            EXECT_S2_PROMPT_VERSION,
            EXECT_S2_VARIANT,
            EXECT_S2_SCHEMA_LEVEL,
            EXECT_S2_SCORER,
            3,
        ),
        (
            "exect_s2_validation_cap25_qwen35b_ollama.json",
            "exect_s2_validation_cap25_qwen35b_ollama",
            EXECT_S2_PROMPT_VERSION,
            EXECT_S2_VARIANT,
            EXECT_S2_SCHEMA_LEVEL,
            EXECT_S2_SCORER,
            25,
        ),
        (
            "exect_s2_validation_full_qwen35b_ollama.json",
            "exect_s2_validation_full_qwen35b_ollama",
            EXECT_S2_PROMPT_VERSION,
            EXECT_S2_VARIANT,
            EXECT_S2_SCHEMA_LEVEL,
            EXECT_S2_SCORER,
            None,
        ),
        (
            "exect_s3_smoke_qwen35b_ollama.json",
            "exect_s3_smoke_qwen35b_ollama",
            EXECT_S3_PROMPT_VERSION,
            EXECT_S3_VARIANT,
            EXECT_S3_SCHEMA_LEVEL,
            EXECT_S3_SCORER,
            3,
        ),
        (
            "exect_s3_validation_cap25_qwen35b_ollama.json",
            "exect_s3_validation_cap25_qwen35b_ollama",
            EXECT_S3_PROMPT_VERSION,
            EXECT_S3_VARIANT,
            EXECT_S3_SCHEMA_LEVEL,
            EXECT_S3_SCORER,
            25,
        ),
        (
            "exect_s3_validation_full_qwen35b_ollama.json",
            "exect_s3_validation_full_qwen35b_ollama",
            EXECT_S3_PROMPT_VERSION,
            EXECT_S3_VARIANT,
            EXECT_S3_SCHEMA_LEVEL,
            EXECT_S3_SCORER,
            None,
        ),
        (
            "exect_s4_smoke_qwen35b_ollama.json",
            "exect_s4_smoke_qwen35b_ollama",
            EXECT_S4_PROMPT_VERSION,
            EXECT_S4_VARIANT,
            EXECT_S4_SCHEMA_LEVEL,
            EXECT_S4_SCORER,
            3,
        ),
        (
            "exect_s4_validation_cap25_qwen35b_ollama.json",
            "exect_s4_validation_cap25_qwen35b_ollama",
            EXECT_S4_PROMPT_VERSION,
            EXECT_S4_VARIANT,
            EXECT_S4_SCHEMA_LEVEL,
            EXECT_S4_SCORER,
            25,
        ),
        (
            "exect_s4_validation_full_qwen35b_ollama.json",
            "exect_s4_validation_full_qwen35b_ollama",
            EXECT_S4_PROMPT_VERSION,
            EXECT_S4_VARIANT,
            EXECT_S4_SCHEMA_LEVEL,
            EXECT_S4_SCORER,
            None,
        ),
    ],
)
def test_exect_qwen35b_ladder_configs_pin_frozen_prompts_and_local_model(
    filename: str,
    expected_id: str,
    prompt_version: str,
    program_variant: str,
    schema_level: str,
    scorer_mode: str,
    max_records: int | None,
) -> None:
    config = load_experiment_config(Path("configs/experiments") / filename)

    assert config.experiment_id == expected_id
    assert config.dataset == "exect_v2"
    assert config.split_name == "exectv2_fixed_v1:validation"
    assert config.model_config_path == EXECT_QWEN35B_MODEL_CONFIG
    assert config.prompt_version == prompt_version
    assert config.program_variant == program_variant
    assert config.schema_level == schema_level
    assert config.scorer_mode == scorer_mode
    assert config.max_records == max_records
    assert config.optimizer is None
    assert config.report_on_test_split is False
    caveats = " ".join(config.metric_caveats).lower()
    assert "chainofthought" in caveats
    assert "bootstrapfewshot" in caveats
    assert "do not compare" in caveats


def test_exect_qwen35b_regression_slice_config_has_37_record_ids():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "exect_s0_s1_label_policy_regression_slice_qwen35b_ollama.json"
        )
    )

    assert config.experiment_id == "exect_s0_s1_label_policy_regression_slice_qwen35b_ollama"
    assert len(config.record_ids or []) == 37


def test_exect_qwen35b_model_config_raises_output_budget_for_structured_extraction():
    payload = json.loads(EXECT_QWEN35B_MODEL_CONFIG.read_text(encoding="utf-8"))

    assert payload["model"] == "qwen3.6:35b"
    assert payload["max_tokens"] >= 8192
    assert payload["extra_body"]["options"]["num_ctx"] >= 32768


EXPERIMENT_CONFIG_DIR = Path("configs/experiments")
REGISTRY_IDS = registry_experiment_ids()


@pytest.mark.parametrize(
    "filename",
    sorted(path.name for path in EXPERIMENT_CONFIG_DIR.glob("*.json")),
)
def test_experiment_config_has_inline_taxonomy_or_registry_coverage(filename: str):
    config = load_experiment_config(EXPERIMENT_CONFIG_DIR / filename)

    if config.taxonomy is not None:
        assert config.taxonomy_exemption is None
        assert config.taxonomy.dataset == config.dataset
        return

    if config.taxonomy_exemption is not None:
        assert config.taxonomy is None
        return

    assert config.experiment_id in REGISTRY_IDS, (
        f"{filename} must include a taxonomy block, taxonomy_exemption, or a matching "
        f"row in docs/experiment_registry.json."
    )


def test_gpt_temporal_full_validation_config_records_taxonomy_metadata():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails.json"
        )
    )

    assert config.taxonomy is not None
    assert config.taxonomy.schema_complexity == "gan_s0"
    assert config.taxonomy.program_architecture == "temporal_candidates_verify_repair"
    assert "H2_pre_deterministic" in config.taxonomy.hybrid_balance_class
    assert config.taxonomy.comparison_group == "gan_s0_architecture_gpt_validation_v1"
    assert config.taxonomy.intended_decision == "promote"
    assert config.taxonomy.varied_factor == "program_architecture"


def test_react_temporal_tools_slice_config_records_taxonomy_metadata():
    config = load_experiment_config(
        Path(
            "configs/experiments/"
            "gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json"
        )
    )

    assert config.taxonomy is not None
    assert config.taxonomy.hybrid_balance_class == ["H3_interleaved_tool_hybrid"]
    assert config.taxonomy.interleaving_positions == ["tool_during", "during"]
    assert config.taxonomy.intended_decision == "reject"
    assert config.taxonomy.varied_factor == "interleaving_position"


def test_exect_s1_interleaving_h1_config_records_post_bridge_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s1_interleaving_h1_post_bridge_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s1_interleaving_h1_post_bridge_gpt4_1_mini"
    assert config.program_variant == EXECT_S0_S1_VARIANT
    assert config.controls.repair_policy == REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY
    assert config.taxonomy is not None
    assert config.taxonomy.hybrid_balance_class == ["H1_post_deterministic"]
    assert config.taxonomy.comparison_group == "exect_s1_interleaving_gpt_validation_v1"


def test_exect_s1_interleaving_h2_config_records_pre_vocab_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini.json")
    )

    assert config.experiment_id == "exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini"
    assert config.program_variant == EXECT_S0_S1_PRE_VOCAB_VARIANT
    assert config.controls.context_policy == "full_note_plus_precomputed_family_candidates"
    assert config.controls.repair_policy == "none"
    assert config.taxonomy is not None
    assert config.taxonomy.hybrid_balance_class == ["H2_pre_deterministic"]


def test_exect_s1_interleaving_cap25_configs_record_gates():
    h1 = load_experiment_config(
        Path(
            "configs/experiments/exect_s1_interleaving_h1_post_bridge_cap25_gpt4_1_mini.json"
        )
    )
    h2 = load_experiment_config(
        Path("configs/experiments/exect_s1_interleaving_h2_pre_vocab_cap25_gpt4_1_mini.json")
    )

    assert h1.max_records == 25
    assert h2.max_records == 25
    assert h1.controls.repair_policy == REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY
    assert h2.program_variant == EXECT_S0_S1_PRE_VOCAB_VARIANT


def test_experiment_config_rejects_conflicting_taxonomy_and_exemption():
    payload = json.loads(
        Path("configs/experiments/gan_s0_baseline_gpt4_1_mini.json").read_text(
            encoding="utf-8"
        )
    )
    payload["taxonomy"] = {
        "dataset": "gan_2026",
        "schema_complexity": "gan_s0",
        "program_architecture": "single_pass",
        "hybrid_balance_class": ["L1_llm_constrained"],
        "interleaving_positions": ["during"],
        "varied_factor": "program_architecture",
        "comparison_group": "gan_s0_architecture_gpt_validation_v1",
        "intended_decision": "exploratory",
    }
    payload["taxonomy_exemption"] = "legacy_registry"

    with pytest.raises(ValidationError):
        ExperimentConfig.model_validate(payload)
