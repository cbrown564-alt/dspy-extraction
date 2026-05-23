from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
    EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
    EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT,
    EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_VARIANT,
    EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
)
from clinical_extraction.programs.exect_s2 import (
    EXECT_S2_COMORBIDITY_C0_C1_VARIANT,
    EXECT_S2_COMORBIDITY_C0_VARIANT,
    EXECT_S2_INV_GUARD_I0_VARIANT,
    EXECT_S2_SCHEMA_LEVEL,
    EXECT_S2_SCORER,
    EXECT_S2_VARIANT,
)
from clinical_extraction.programs.exect_s3 import (
    EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
    EXECT_S3_SCHEMA_LEVEL,
    EXECT_S3_SCORER,
    EXECT_S3_VARIANT,
)
from clinical_extraction.programs.exect_s4 import (
    EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT,
    EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
    EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
    EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT,
    EXECT_S4_L1_VARIANT,
    EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
    EXECT_S4_SCHEMA_LEVEL,
    EXECT_S4_SCORER,
    EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
    EXECT_S4_VARIANT,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
    GAN_FREQUENCY_S0_SCORER,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_NO_GUARDS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_VARIANT,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
)
from clinical_extraction.experiments.taxonomy import (
    ExperimentTaxonomy,
    TaxonomyExemptionValue,
    taxonomy_covers_config,
)
from clinical_extraction.schemas import FrozenModel


StructuredOutputStrategy = Literal[
    "provider_json_schema_with_pydantic_validation",
    "strict_json_prompt_with_pydantic_validation",
]


class OptimizerConfig(FrozenModel):
    """DSPy optimizer hyperparameters for module compilation."""

    name: Literal[
        "BootstrapFewShot",
        "BootstrapFewShotWithRandomSearch",
        "LabeledFewShot",
        "GEPA",
    ] = "BootstrapFewShot"
    metric_name: Literal[
        "pragmatic_category",
        "semantic_frequency_with_evidence",
        "semantic_frequency_with_evidence_feedback",
        "synthesis_exact_with_evidence",
        "synthesis_exact_with_evidence_feedback",
        "exect_field_family_micro_f1",
        "exect_field_family_micro_f1_raw",
    ] = "semantic_frequency_with_evidence"
    max_bootstrapped_demos: int = Field(default=4, ge=0)
    max_labeled_demos: int = Field(default=0, ge=0)
    max_rounds: int = Field(default=1, ge=1)
    num_candidate_programs: int = Field(default=16, ge=1)
    trainset_size: int | None = Field(default=None, gt=0)
    auto: Literal["light", "medium", "heavy"] | None = None
    max_full_evals: int | None = Field(default=None, gt=0)
    max_metric_calls: int | None = Field(default=None, gt=0)
    reflection_minibatch_size: int = Field(default=3, ge=1)
    candidate_selection_strategy: Literal["pareto", "current_best"] = "pareto"
    skip_perfect_score: bool = True
    add_format_failure_as_feedback: bool = False
    track_stats: bool = False
    track_best_outputs: bool = False
    use_cloudpickle: bool = False
    num_threads: int | None = Field(default=None, gt=0)
    seed: int | None = 0

    @model_validator(mode="after")
    def validate_optimizer_settings(self) -> OptimizerConfig:
        if self.name == "LabeledFewShot":
            if self.max_labeled_demos < 1:
                raise ValueError(
                    "LabeledFewShot optimizer configs must set max_labeled_demos >= 1."
                )
            if self.metric_name in {
                "semantic_frequency_with_evidence_feedback",
                "synthesis_exact_with_evidence_feedback",
            }:
                raise ValueError(
                    "LabeledFewShot optimizer configs must use a scalar metric."
                )
            return self

        if self.name in {"BootstrapFewShot", "BootstrapFewShotWithRandomSearch"}:
            if self.max_bootstrapped_demos < 1:
                raise ValueError(
                    f"{self.name} optimizer configs must set max_bootstrapped_demos >= 1."
                )
            if self.metric_name in {
                "semantic_frequency_with_evidence_feedback",
                "synthesis_exact_with_evidence_feedback",
            }:
                raise ValueError(
                    f"{self.name} optimizer configs must use a scalar metric."
                )
            return self

        if self.metric_name not in {
            "semantic_frequency_with_evidence_feedback",
            "synthesis_exact_with_evidence_feedback",
        }:
            raise ValueError("GEPA optimizer configs must use a feedback metric.")
        configured_budgets = sum(
            value is not None
            for value in (self.auto, self.max_full_evals, self.max_metric_calls)
        )
        if configured_budgets == 0:
            raise ValueError(
                "GEPA optimizer configs must set auto, max_full_evals, or max_metric_calls."
            )
        if configured_budgets != 1:
            raise ValueError(
                "GEPA optimizer configs must set exactly one of auto, max_full_evals, "
                "or max_metric_calls."
            )
        return self


class ExperimentControls(FrozenModel):
    few_shot_policy: str
    context_policy: str
    verifier_policy: str
    repair_policy: str
    abstention_policy: str

    @model_validator(mode="after")
    def validate_required_text_fields(self) -> ExperimentControls:
        for field in [
            "few_shot_policy",
            "context_policy",
            "verifier_policy",
            "repair_policy",
            "abstention_policy",
        ]:
            if not getattr(self, field).strip():
                raise ValueError(f"{field} must be a non-empty string.")
        return self


class ExperimentConfig(FrozenModel):
    experiment_id: str
    hypothesis: str
    dataset: Literal["gan_2026", "exect_v2"]
    split_name: str
    split_file: Path
    model_config_path: Path
    schema_level: Literal[
        "gan_frequency_s0",
        "exect_s0_s1_field_family",
        "exect_s2_field_family",
        "exect_s3_field_family",
        "exect_s4_field_family",
    ] = GAN_FREQUENCY_S0_SCHEMA_LEVEL
    program_variant: Literal[
        "gan_frequency_s0_single_pass",
        "gan_frequency_s0_direct_single_pass",
        "gan_frequency_s0_direct_verify_repair",
        "gan_frequency_s0_temporal_candidates_verify_repair",
        "gan_frequency_s0_temporal_candidates_single_pass",
        "gan_frequency_s0_llm_temporal_candidates_single_pass",
        "gan_frequency_s0_hybrid_temporal_candidates_single_pass",
        "gan_frequency_s0_temporal_candidates_adjudicate_verify_repair",
        "gan_frequency_s0_temporal_candidates_adjudicate_constrained_verifier",
        "gan_frequency_s0_temporal_candidates_adjudicate_det_guards",
        "gan_frequency_s0_temporal_candidates_adjudicate_det_evidence",
        "gan_frequency_s0_temporal_candidates_adjudicate_confirm_only",
        "gan_frequency_s0_temporal_candidates_adjudicate_verify_repair_no_guards",
        "gan_frequency_s0_llm_temporal_candidates_verify_repair",
        "gan_frequency_s0_temporal_event_table_verify_repair",
        "gan_frequency_s0_temporal_event_table_single_pass",
        "gan_frequency_s0_multiple_answer_det_selector",
        "gan_frequency_s0_react_temporal_tools",
        "exect_s0_s1_field_family_single_pass",
        "exect_s0_s1_field_family_pre_vocab_single_pass",
        "exect_s0_s1_field_family_medication_pre_vocab_single_pass",
        "exect_s0_s1_field_family_seizure_pre_vocab_single_pass",
        "exect_s0_s1_field_family_section_aware",
        "exect_s0_s1_field_family_prompt_graph_parallel",
        "exect_s0_s1_field_family_prompt_graph_sequential",
        "exect_s0_s1_field_family_diagnosis_recall",
        "exect_s0_s1_field_family_verify_repair",
        "exect_s0_s1_field_family_deterministic_only",
        "exect_s2_field_family_single_pass",
        "exect_s2_field_family_comorbidity_c0_single_pass",
        "exect_s2_field_family_comorbidity_c0_c1_single_pass",
        "exect_s2_field_family_inv_guard_i0_single_pass",
        "exect_s3_field_family_single_pass",
        "exect_s3_field_family_cause_bridge_k0_k1_single_pass",
        "exect_s4_field_family_single_pass",
        "exect_s4_field_family_frequency_pre_vocab_single_pass",
        "exect_s4_field_family_frequency_post_merge_single_pass",
        "exect_s4_field_family_frequency_structured_slots_single_pass",
        "exect_s4_field_family_temporality_post_classifier_single_pass",
        "exect_s4_field_family_mt_guard_non_asm_single_pass",
        "exect_s4_field_family_cause_bridge_k0_k1_single_pass",
    ] = GAN_FREQUENCY_S0_VARIANT
    scorer_mode: Literal[
        "gan_frequency_deterministic_v1",
        "exect_field_family_deterministic_v1",
        "exect_s2_field_family_deterministic_v1",
        "exect_s3_field_family_deterministic_v1",
        "exect_s4_field_family_deterministic_v1",
    ] = GAN_FREQUENCY_S0_SCORER
    prompt_version: str
    controls: ExperimentControls
    structured_output_strategy: StructuredOutputStrategy
    output_root: Path = Path("runs")
    max_records: int | None = Field(default=None, gt=0)
    record_ids: list[str] | None = None
    report_on_test_split: bool = False
    metric_caveats: list[str] = Field(default_factory=list)
    optimizer: OptimizerConfig | None = None
    taxonomy: ExperimentTaxonomy | None = None
    taxonomy_exemption: TaxonomyExemptionValue | None = None

    @model_validator(mode="after")
    def validate_taxonomy_fields(self) -> ExperimentConfig:
        if self.taxonomy is not None and self.taxonomy_exemption is not None:
            raise ValueError(
                "Experiment configs must set either taxonomy or taxonomy_exemption, not both."
            )
        if self.taxonomy is not None and not taxonomy_covers_config(
            self.dataset, self.taxonomy
        ):
            raise ValueError(
                "taxonomy.dataset must match the top-level dataset field on the config."
            )
        return self

    @model_validator(mode="after")
    def validate_experiment_context(self) -> ExperimentConfig:
        for field in [
            "experiment_id",
            "hypothesis",
            "split_name",
            "prompt_version",
        ]:
            if not getattr(self, field).strip():
                raise ValueError(f"{field} must be a non-empty string.")

        expected_contracts = {
            "gan_2026": [
                (
                    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
                    {
                        GAN_FREQUENCY_S0_VARIANT,
                        GAN_FREQUENCY_S0_DIRECT_VARIANT,
                        GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
                        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
                        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
                        GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
                        GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
                        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT,
                        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT,
                        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT,
                        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT,
                        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT,
                        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_NO_GUARDS_VARIANT,
                        GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
                        GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
                        GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT,
                        GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
                        GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
                    },
                    GAN_FREQUENCY_S0_SCORER,
                )
            ],
            "exect_v2": [
                (
                    EXECT_S0_S1_SCHEMA_LEVEL,
                    {
                        EXECT_S0_S1_VARIANT,
                        EXECT_S0_S1_PRE_VOCAB_VARIANT,
                        EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
                        EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
                        EXECT_S0_S1_SECTION_AWARE_VARIANT,
                        EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT,
                        EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT,
                        EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
                        EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
                        EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
                    },
                    EXECT_S0_S1_SCORER,
                ),
                (
                    EXECT_S2_SCHEMA_LEVEL,
                    {
                        EXECT_S2_VARIANT,
                        EXECT_S2_COMORBIDITY_C0_VARIANT,
                        EXECT_S2_COMORBIDITY_C0_C1_VARIANT,
                        EXECT_S2_INV_GUARD_I0_VARIANT,
                    },
                    EXECT_S2_SCORER,
                ),
                (
                    EXECT_S3_SCHEMA_LEVEL,
                    {
                        EXECT_S3_VARIANT,
                        EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
                    },
                    EXECT_S3_SCORER,
                ),
                (
                    EXECT_S4_SCHEMA_LEVEL,
                    {
                        EXECT_S4_VARIANT,
                        EXECT_S4_L1_VARIANT,
                        EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
                        EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
                        EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT,
                        EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
                        EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
                        EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT,
                    },
                    EXECT_S4_SCORER,
                ),
            ],
        }
        valid_contracts = expected_contracts[self.dataset]
        if not any(
            self.schema_level == expected_schema
            and self.program_variant in expected_variants
            and self.scorer_mode == expected_scorer
            for expected_schema, expected_variants, expected_scorer in valid_contracts
        ):
            raise ValueError(
                f"{self.dataset} experiment configs must use one of the registered "
                f"schema_level/program_variant/scorer_mode contracts."
            )

        if self.split_name.endswith(":test") and not self.report_on_test_split:
            raise ValueError(
                "Experiment configs must explicitly set "
                "report_on_test_split=true before reporting on the test split."
            )
        if self.record_ids is not None:
            if not self.record_ids:
                raise ValueError("record_ids must be a non-empty list when set.")
            if any(not record_id.strip() for record_id in self.record_ids):
                raise ValueError("record_ids entries must be non-empty strings.")
        return self


def load_experiment_config(path: Path) -> ExperimentConfig:
    return ExperimentConfig.model_validate_json(path.read_text(encoding="utf-8"))


def write_experiment_config(config: ExperimentConfig, path: Path) -> None:
    path.write_text(
        json.dumps(config.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
