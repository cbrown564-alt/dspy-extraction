import pytest
from pydantic import ValidationError

from clinical_extraction.experiments.arm_templates import (
    ArmStudyContext,
    build_arm_controls,
    build_arm_taxonomy,
    build_comparison_group_id,
    build_experiment_arm_config,
    list_arm_template_definitions,
    validate_arm_comparison_suite,
    validate_comparison_group_id,
    validate_primitives_for_arm,
)
from clinical_extraction.experiments.config import ExperimentConfig
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_VARIANT,
    REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY,
    REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES,
)
from clinical_extraction.programs.exect_s4 import (
    EXECT_S4_PROMPT_VERSION,
    EXECT_S4_SCHEMA_LEVEL,
    EXECT_S4_SCORER,
    EXECT_S4_VARIANT,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_SCORER,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
)


def test_arm_template_definitions_cover_l1_through_d1():
    definitions = {item.arm: item for item in list_arm_template_definitions()}

    assert set(definitions) == {"L1", "H1", "H2", "H3", "H4", "D1"}
    assert definitions["H1"].hybrid_balance_class == ["H1_post_deterministic"]
    assert definitions["H3"].interleaving_positions == ["tool_during", "during"]
    assert definitions["D1"].interleaving_positions == ["eval_only"]


def test_build_comparison_group_id_follows_taxonomy_convention():
    group_id = build_comparison_group_id(
        schema_complexity="exect_s1",
        factor="interleaving",
        model_track="gpt",
        scope="validation",
        version=2,
    )

    assert group_id == "exect_s1_interleaving_gpt_validation_v2"
    validate_comparison_group_id(group_id, dataset="exect_v2")

    qwen_group = build_comparison_group_id(
        schema_complexity="exect_s1",
        factor="interleaving",
        model_track="qwen",
        scope="validation",
        version=1,
    )
    assert qwen_group == "exect_s1_interleaving_qwen_validation_v1"


def test_validate_comparison_group_id_rejects_invalid_suffix():
    with pytest.raises(ValueError, match="_v<number>"):
        validate_comparison_group_id("exect_s1_interleaving_gpt_validation")


def test_validate_primitives_for_arm_rejects_incompatible_h1_bridge_on_h2():
    with pytest.raises(ValueError, match="compatible_experiment_arms"):
        validate_primitives_for_arm(
            "H2",
            ["exect.medication.benchmark_bridge.v1"],
        )


def test_validate_primitives_for_arm_accepts_exect_s1_h1_bridge_pack():
    validate_primitives_for_arm(
        "H1",
        [
            "exect.diagnosis.benchmark_bridge.v1",
            "exect.seizure_type.benchmark_bridge.v1",
            "exect.medication.benchmark_bridge.v1",
        ],
    )


def test_build_arm_taxonomy_prefills_exect_s1_interleaving_h1():
    ctx = ArmStudyContext(
        dataset="exect_v2",
        schema_complexity="exect_s1",
        program_architecture="single_pass",
        clinical_task_family=["diagnosis", "seizure_type", "medication"],
        comparison_group="exect_s1_interleaving_gpt_validation_v2",
    )

    taxonomy = build_arm_taxonomy("H1", ctx)

    assert taxonomy.hybrid_balance_class == ["H1_post_deterministic"]
    assert taxonomy.interleaving_positions == ["during", "post"]
    assert taxonomy.comparison_group == "exect_s1_interleaving_gpt_validation_v2"
    assert taxonomy.varied_factor == "interleaving_position"


def test_build_arm_controls_prefills_exect_s1_l1_raw_and_h1_post_bridge():
    ctx = ArmStudyContext(
        dataset="exect_v2",
        schema_complexity="exect_s1",
        program_architecture="single_pass",
        clinical_task_family=["diagnosis", "seizure_type", "medication"],
        comparison_group="exect_s1_interleaving_gpt_validation_v2",
    )

    l1_controls = build_arm_controls("L1", ctx, raw_l1=True)
    h1_controls = build_arm_controls(
        "H1",
        ctx,
        primitive_ids=[
            "exect.diagnosis.benchmark_bridge.v1",
            "exect.seizure_type.benchmark_bridge.v1",
            "exect.medication.benchmark_bridge.v1",
        ],
    )

    assert l1_controls.repair_policy == REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES
    assert h1_controls.repair_policy == REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY


def test_build_experiment_arm_config_matches_exect_s1_h2_medication_slice_shape():
    ctx = ArmStudyContext(
        dataset="exect_v2",
        schema_complexity="exect_s1",
        program_architecture="single_pass",
        clinical_task_family=["medication"],
        comparison_group="exect_s1_medication_pre_vocab_slice_gpt_v1",
    )

    config = build_experiment_arm_config(
        "H2",
        ctx,
        experiment_id="exect_s1_interleaving_h2_medication_pre_vocab_slice_gpt4_1_mini",
        hypothesis="Medication-only pre-vocabulary injection improves annotated_medication recall.",
        split_name="exectv2_fixed_v1:validation",
        split_file="data/splits/exectv2_splits.json",
        model_config_path="configs/models/gan_s0_gpt4_1_mini.json",
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        program_variant=EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
        scorer_mode=EXECT_S0_S1_SCORER,
        prompt_version=EXECT_S0_S1_PROMPT_VERSION,
        primitive_ids=["exect.medication.rx_candidates.v1"],
        metric_caveats=["14-record medication slice."],
        record_ids=["EA0135", "EA0150"],
        include_archive=True,
    )

    assert isinstance(config, ExperimentConfig)
    assert config.program_variant == EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT
    assert (
        config.controls.context_policy
        == "full_note_plus_precomputed_medication_candidates"
    )
    assert config.taxonomy.hybrid_balance_class == ["H2_pre_deterministic"]
    assert config.taxonomy.comparison_group == "exect_s1_medication_pre_vocab_slice_gpt_v1"


def test_build_experiment_arm_config_matches_exect_s1_h2_seizure_slice_shape():
    ctx = ArmStudyContext(
        dataset="exect_v2",
        schema_complexity="exect_s1",
        program_architecture="single_pass",
        clinical_task_family=["seizure_type"],
        comparison_group="exect_s1_seizure_pre_vocab_slice_gpt_v1",
    )

    config = build_experiment_arm_config(
        "H2",
        ctx,
        experiment_id="exect_s1_interleaving_h2_seizure_pre_vocab_slice_gpt4_1_mini",
        hypothesis="Seizure-type-only pre-vocabulary injection improves seizure_type recall.",
        split_name="exectv2_fixed_v1:validation",
        split_file="data/splits/exectv2_splits.json",
        model_config_path="configs/models/gan_s0_gpt4_1_mini.json",
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        program_variant=EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
        scorer_mode=EXECT_S0_S1_SCORER,
        prompt_version=EXECT_S0_S1_PROMPT_VERSION,
        metric_caveats=["15-record seizure slice."],
        record_ids=["EA0008", "EA0016"],
        include_archive=True,
    )

    assert isinstance(config, ExperimentConfig)
    assert config.program_variant == EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT
    assert (
        config.controls.context_policy
        == "full_note_plus_precomputed_seizure_type_candidates"
    )
    assert config.taxonomy.hybrid_balance_class == ["H2_pre_deterministic"]
    assert config.taxonomy.comparison_group == "exect_s1_seizure_pre_vocab_slice_gpt_v1"


def test_build_experiment_arm_config_matches_exect_s4_frequency_l1_baseline():
    ctx = ArmStudyContext(
        dataset="exect_v2",
        schema_complexity="exect_s4",
        program_architecture="single_pass",
        clinical_task_family=["frequency"],
        comparison_group="exect_s4_frequency_deterministic_v1",
        varied_factor="program_architecture",
    )

    config = build_experiment_arm_config(
        "L1",
        ctx,
        experiment_id="exect_s4_frequency_l1_baseline_cap25_gpt4_1_mini",
        hypothesis="Frozen S4 single-pass baseline on cap-25.",
        split_name="exectv2_fixed_v1:validation",
        split_file="data/splits/exectv2_splits.json",
        model_config_path="configs/models/gan_s0_gpt4_1_mini.json",
        schema_level=EXECT_S4_SCHEMA_LEVEL,
        program_variant=EXECT_S4_VARIANT,
        scorer_mode=EXECT_S4_SCORER,
        prompt_version=EXECT_S4_PROMPT_VERSION,
        max_records=25,
    )

    assert config.taxonomy.hybrid_balance_class == ["L1_llm_constrained"]
    assert config.taxonomy.varied_factor == "program_architecture"
    assert config.controls.repair_policy == "none"


def test_build_experiment_arm_config_h4_allows_temporal_candidate_primitive():
    ctx = ArmStudyContext(
        dataset="gan_2026",
        schema_complexity="gan_s0",
        program_architecture="temporal_candidates_verify_repair",
        clinical_task_family="frequency",
        comparison_group="gan_s0_architecture_gpt_validation_v1",
        varied_factor="program_architecture",
    )

    config = build_experiment_arm_config(
        "H4",
        ctx,
        experiment_id="gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_cap25",
        hypothesis="Temporal candidates plus verify-repair adjudication.",
        split_name="gan_2026_fixed_v1:validation",
        split_file="data/splits/gan_2026_splits.json",
        model_config_path="configs/models/gan_s0_gpt4_1_mini.json",
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
        scorer_mode=GAN_FREQUENCY_S0_SCORER,
        prompt_version="gan_frequency_s0_temporal_candidates_verify_repair_v1_1",
        primitive_ids=["gan.frequency.temporal_candidates.v1"],
        max_records=25,
        include_archive=True,
    )

    assert "H4_deterministic_first_llm_adjudicates" in config.taxonomy.hybrid_balance_class
    assert "H2_pre_deterministic" in config.taxonomy.hybrid_balance_class
    assert config.controls.context_policy == "full_note_plus_deterministic_temporal_candidates"


def test_build_experiment_arm_config_h3_react_tools_shape():
    ctx = ArmStudyContext(
        dataset="gan_2026",
        schema_complexity="gan_s0",
        program_architecture="react_temporal_tools",
        clinical_task_family="frequency",
        comparison_group="gan_s0_hard_slice_qwen_architecture_v1",
        varied_factor="interleaving_position",
        intended_decision="reject",
    )

    config = build_experiment_arm_config(
        "H3",
        ctx,
        experiment_id="gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails",
        hypothesis="Bounded ReAct temporal tools on guardrail slice.",
        split_name="gan_2026_fixed_v1:validation",
        split_file="data/splits/gan_2026_splits.json",
        model_config_path="configs/models/gan_s0_qwen35b_ollama_verify_repair.json",
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        program_variant=GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
        scorer_mode=GAN_FREQUENCY_S0_SCORER,
        prompt_version="gan_frequency_s0_react_temporal_tools_v1_1",
        structured_output_strategy="strict_json_prompt_with_pydantic_validation",
        include_archive=True,
    )

    assert config.taxonomy.hybrid_balance_class == ["H3_interleaved_tool_hybrid"]
    assert config.taxonomy.intended_decision == "reject"
    assert "react" in config.controls.context_policy.lower()


def test_validate_arm_comparison_suite_requires_shared_comparison_group():
    ctx_a = ArmStudyContext(
        dataset="exect_v2",
        schema_complexity="exect_s1",
        program_architecture="single_pass",
        clinical_task_family=["medication"],
        comparison_group="exect_s1_interleaving_gpt_validation_v2",
    )
    ctx_b = ArmStudyContext(
        dataset="exect_v2",
        schema_complexity="exect_s1",
        program_architecture="single_pass",
        clinical_task_family=["medication"],
        comparison_group="exect_s1_interleaving_gpt_validation_v1",
    )

    with pytest.raises(ValueError, match="comparison_group"):
        validate_arm_comparison_suite(
            {
                "L1": build_arm_taxonomy("L1", ctx_a),
                "H1": build_arm_taxonomy("H1", ctx_b),
            }
        )


def test_build_experiment_arm_config_rejects_mismatched_dataset_taxonomy():
    ctx = ArmStudyContext(
        dataset="exect_v2",
        schema_complexity="exect_s1",
        program_architecture="single_pass",
        clinical_task_family=["medication"],
        comparison_group="exect_s1_interleaving_gpt_validation_v2",
    )

    with pytest.raises(ValidationError):
        build_experiment_arm_config(
            "L1",
            ctx,
            experiment_id="bad_dataset_mismatch",
            hypothesis="Should fail because top-level dataset does not match taxonomy.",
            split_name="exectv2_fixed_v1:validation",
            split_file="data/splits/exectv2_splits.json",
            model_config_path="configs/models/gan_s0_gpt4_1_mini.json",
            schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
            program_variant=EXECT_S0_S1_VARIANT,
            scorer_mode=EXECT_S0_S1_SCORER,
            prompt_version=EXECT_S0_S1_PROMPT_VERSION,
            dataset="gan_2026",
        )


def test_d1_arm_config_uses_eval_only_taxonomy_without_model_required_fields():
    ctx = ArmStudyContext(
        dataset="gan_2026",
        schema_complexity="gan_s0",
        program_architecture="single_pass",
        clinical_task_family="frequency",
        comparison_group="gan_s0_primitive_diagnostics_v1",
        varied_factor="hybrid_balance_class",
        intended_decision="exploratory",
    )

    taxonomy = build_arm_taxonomy("D1", ctx)

    assert taxonomy.hybrid_balance_class == ["D1_deterministic_only"]
    assert taxonomy.interleaving_positions == ["eval_only"]

    validate_primitives_for_arm(
        "D1",
        [
            "gan.frequency.label_policy_bridge.v1",
            "gan.frequency.evidence_guard.v1",
        ],
    )
