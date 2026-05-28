from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from clinical_extraction.evaluation.exect import EXECT_S5_SCORER
from clinical_extraction.experiments.taxonomy import DatasetValue
from clinical_extraction.gan.scoring import GAN_PAPER_REPRODUCTION_SCORER
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT,
    EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT,
    EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
    EXECT_S0_S1_DIAGNOSIS_RECALL_PROMPT_VERSION,
    EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
    EXECT_S0_S1_D1_PROMPT_VERSION,
    EXECT_S0_S1_L0_PROMPT_VERSION,
    EXECT_S0_S1_L1_SCHEMA_PROMPT_VERSION,
    EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT,
    EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_STAGE_GRAPH_BY_VARIANT,
    EXECT_S0_S1_VARIANT,
    EXECT_S0_S1_V4_11_PROMPT_VERSION,
    EXECT_S0_S1_VERIFY_REPAIR_PROMPT_VERSION,
    EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
)
from clinical_extraction.programs.exect_s2 import (
    EXECT_S2_CLEAN_LADDER_V1_VARIANT,
    EXECT_S2_COMORBIDITY_C0_C1_VARIANT,
    EXECT_S2_COMORBIDITY_C0_VARIANT,
    EXECT_S2_INV_GUARD_I0_VARIANT,
    EXECT_S2_PROMPT_VERSION,
    EXECT_S2_SCHEMA_LEVEL,
    EXECT_S2_SCORER,
    EXECT_S2_VARIANT,
)
from clinical_extraction.programs.exect_s3 import (
    EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
    EXECT_S3_CLEAN_LADDER_V1_VARIANT,
    EXECT_S3_PROMPT_VERSION,
    EXECT_S3_SCHEMA_LEVEL,
    EXECT_S3_SCORER,
    EXECT_S3_VARIANT,
)
from clinical_extraction.programs.exect_s4 import (
    EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT,
    EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
    EXECT_S4_FREQUENCY_PRE_VOCAB_HIGH_PRECISION_VARIANT,
    EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
    EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_PROMPT_VERSION,
    EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT,
    EXECT_S4_L1_VARIANT,
    EXECT_S4_MT_GUARD_NON_ASM_DOSE_CURRENT_VARIANT,
    EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
    EXECT_S4_PROMPT_VERSION,
    EXECT_S4_SCHEMA_LEVEL,
    EXECT_S4_SCORER,
    EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
    EXECT_S4_VARIANT,
    EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT,
    EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT,
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
    EXECT_S5_STAGE_GRAPH_BY_VARIANT,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
    GAN_FREQUENCY_S0_SCORER,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_STAGE_GRAPH_BY_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_NO_GUARDS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_VARIANT,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
    default_gan_frequency_s0_prompt_version,
)
from clinical_extraction.schemas import FrozenModel

EXECT_S5_SCHEMA_LEVEL = "exect_s5_core_field_family"

ProgramVariantStatusValue = Literal[
    "promoted_baseline",
    "mechanism_baseline",
    "diagnostic_baseline",
    "operational_baseline",
    "historical",
    "rejected_arm",
    "blocked",
]

LOADABLE_STATUSES = frozenset(
    {
        "promoted_baseline",
        "mechanism_baseline",
        "diagnostic_baseline",
        "operational_baseline",
        "historical",
        "rejected_arm",
    }
)
STATUS_REQUIRES_EXACT_PROMPT = frozenset(
    {
        "promoted_baseline",
        "mechanism_baseline",
        "diagnostic_baseline",
        "operational_baseline",
    }
)


class ProgramVariantSpec(FrozenModel):
    """Typed replay and cleanup contract for executable program variants."""

    variant_id: str = Field(pattern=r"^[a-z0-9]+(\.[a-z0-9_]+)+$")
    dataset: DatasetValue
    schema_level: str
    program_variant: str
    scorer_modes: tuple[str, ...] = Field(min_length=1)
    prompt_default: str
    stage_graph_id: str | None = None
    status: ProgramVariantStatusValue
    replacement_target: str | None = None
    decision_doc: str | None = None
    implementation_variant: str | None = None
    config_examples: tuple[str, ...] = ()
    notes: str = ""

    @model_validator(mode="after")
    def validate_contract_text(self) -> ProgramVariantSpec:
        for field_name in [
            "variant_id",
            "schema_level",
            "program_variant",
            "prompt_default",
        ]:
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        if len(set(self.scorer_modes)) != len(self.scorer_modes):
            raise ValueError("scorer_modes must not contain duplicates.")
        if any(not scorer.strip() for scorer in self.scorer_modes):
            raise ValueError("scorer_modes entries must be non-empty strings.")
        return self

    @property
    def is_loadable_config_contract(self) -> bool:
        return self.status in LOADABLE_STATUSES

    @property
    def dataset_label(self) -> str:
        if self.dataset == "gan_2026":
            return "Gan 2026"
        return "ExECTv2"


def _spec(
    variant_id: str,
    dataset: DatasetValue,
    schema_level: str,
    program_variant: str,
    scorer_modes: tuple[str, ...],
    prompt_default: str,
    status: ProgramVariantStatusValue,
    *,
    stage_graph_id: str | None = None,
    replacement_target: str | None = None,
    decision_doc: str | None = None,
    implementation_variant: str | None = None,
    config_examples: tuple[str, ...] = (),
    notes: str = "",
) -> ProgramVariantSpec:
    return ProgramVariantSpec(
        variant_id=variant_id,
        dataset=dataset,
        schema_level=schema_level,
        program_variant=program_variant,
        scorer_modes=scorer_modes,
        prompt_default=prompt_default,
        stage_graph_id=stage_graph_id,
        status=status,
        replacement_target=replacement_target,
        decision_doc=decision_doc,
        implementation_variant=implementation_variant,
        config_examples=config_examples,
        notes=notes,
    )


GAN_SCORERS = (GAN_FREQUENCY_S0_SCORER, GAN_PAPER_REPRODUCTION_SCORER)


def _gan_spec(
    variant_id: str,
    program_variant: str,
    status: ProgramVariantStatusValue = "historical",
    **overrides: object,
) -> ProgramVariantSpec:
    return _spec(
        variant_id=variant_id,
        dataset="gan_2026",
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        program_variant=program_variant,
        scorer_modes=GAN_SCORERS,
        prompt_default=str(
            overrides.pop(
                "prompt_default",
                default_gan_frequency_s0_prompt_version(program_variant),
            )
        ),
        stage_graph_id=GAN_FREQUENCY_S0_STAGE_GRAPH_BY_VARIANT.get(program_variant),
        status=status,
        **overrides,
    )


def _exect_spec(
    variant_id: str,
    schema_level: str,
    program_variant: str,
    scorer_mode: str,
    prompt_default: str,
    status: ProgramVariantStatusValue = "historical",
    **overrides: object,
) -> ProgramVariantSpec:
    return _spec(
        variant_id=variant_id,
        dataset="exect_v2",
        schema_level=schema_level,
        program_variant=program_variant,
        scorer_modes=(scorer_mode,),
        prompt_default=prompt_default,
        status=status,
        **overrides,
    )


PROGRAM_VARIANT_REGISTRY: tuple[ProgramVariantSpec, ...] = (
    _gan_spec("gan.s0.single_pass", GAN_FREQUENCY_S0_VARIANT),
    _gan_spec("gan.s0.direct_single_pass", GAN_FREQUENCY_S0_DIRECT_VARIANT),
    _gan_spec("gan.s0.direct_verify_repair", GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT),
    _gan_spec(
        "gan.s0.temporal_candidates_verify_repair",
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    ),
    _gan_spec(
        "gan.s0.temporal_candidates_single_pass",
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    ),
    _gan_spec(
        "gan.s0.builder_gap_v1",
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
        status="promoted_baseline",
        prompt_default="gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy",
        implementation_variant="gan_s0_candidate_builder_gap_v1",
        decision_doc="docs/experiments/gan/gan_s0_operational_default_promotion_review_20260523.md",
        config_examples=(
            "configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json",
            "configs/experiments/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation.json",
        ),
        notes=(
            "Synthetic validation operational surface; direct paper-comparison tables "
            "must rescore with gan2026_paper_reproduction."
        ),
    ),
    _gan_spec(
        "gan.s0.llm_temporal_candidates_single_pass",
        GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    ),
    _gan_spec(
        "gan.s0.hybrid_temporal_candidates_single_pass",
        GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    ),
    _gan_spec(
        "gan.s0.date_events_candidates_single_pass",
        GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    ),
    _gan_spec(
        "gan.s0.d1_v1_2b_schema_guard_only",
        GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
        status="mechanism_baseline",
        prompt_default="gan_frequency_s0_date_events_candidates_v1_2b_schema_guard_only",
        decision_doc="docs/experiments/gan/gan_s0_r15_d1_guardrail_ablation_decision_20260528.md",
        config_examples=(
            "configs/experiments/gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini.json",
        ),
        notes="Current decomposed Gan S0 mechanism baseline after the May 28 pivot.",
    ),
    _gan_spec(
        "gan.s0.llm_date_events_candidates_single_pass",
        GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    ),
    _gan_spec(
        "gan.s0.hybrid_date_events_candidates_single_pass",
        GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    ),
    _gan_spec(
        "gan.s0.entity_tags_date_events_single_pass",
        GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_VARIANT,
        status="rejected_arm",
        decision_doc="docs/experiments/gan/gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md",
        replacement_target="gan.s0.d1_v1_2b_schema_guard_only",
    ),
    _gan_spec(
        "gan.s0.temporal_candidates_adjudicate_verify_repair",
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT,
    ),
    _gan_spec(
        "gan.s0.temporal_candidates_adjudicate_constrained_verifier",
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT,
    ),
    _gan_spec(
        "gan.s0.temporal_candidates_adjudicate_det_guards",
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT,
    ),
    _gan_spec(
        "gan.s0.temporal_candidates_adjudicate_det_evidence",
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT,
    ),
    _gan_spec(
        "gan.s0.temporal_candidates_adjudicate_confirm_only",
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT,
    ),
    _gan_spec(
        "gan.s0.temporal_candidates_adjudicate_verify_repair_no_guards",
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_NO_GUARDS_VARIANT,
    ),
    _gan_spec(
        "gan.s0.llm_temporal_candidates_verify_repair",
        GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    ),
    _gan_spec(
        "gan.s0.temporal_event_table_verify_repair",
        GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
    ),
    _gan_spec(
        "gan.s0.temporal_event_table_single_pass",
        GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT,
    ),
    _gan_spec(
        "gan.s0.multiple_answer_det_selector",
        GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    ),
    _gan_spec(
        "gan.s0.seeded_multiple_answer_det_selector",
        GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    ),
    _gan_spec(
        "gan.s0.react_temporal_tools",
        GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
        status="rejected_arm",
        replacement_target="gan.s0.builder_gap_v1",
    ),
    _gan_spec(
        "gan.s0.self_consistency",
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
        status="rejected_arm",
        decision_doc="docs/experiments/gan/gan_s0_r13_self_consistency_variance_probe_decision_20260528.md",
        replacement_target="gan.s0.d1_v1_2b_schema_guard_only",
        config_examples=(
            "configs/experiments/gan_s0_self_consistency_sample5_cap25_gpt4_1_mini.json",
            "configs/experiments/gan_s0_self_consistency_sample5_cap25_qwen35b.json",
        ),
    ),
    _exect_spec(
        "exect.s1.single_pass",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_PROMPT_VERSION,
        stage_graph_id=EXECT_S0_S1_STAGE_GRAPH_BY_VARIANT.get(EXECT_S0_S1_VARIANT),
    ),
    _exect_spec(
        "exect.s1.pre_vocab",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_PRE_VOCAB_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s1.medication_pre_vocab",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_PROMPT_VERSION,
        status="rejected_arm",
    ),
    _exect_spec(
        "exect.s1.seizure_pre_vocab",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_V4_11_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s1.clean_ladder_v1",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_PROMPT_VERSION,
        status="diagnostic_baseline",
    ),
    _exect_spec(
        "exect.s1.clean_ladder_v2_diagnosis_stable",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_V4_11_PROMPT_VERSION,
        status="diagnostic_baseline",
        stage_graph_id="g2_field_family_prompt_graph",
        implementation_variant="v4_10_diagnosis_v4_11_seizure_medication_am_guard",
        decision_doc="docs/experiments/exect/exect_s1_clean_ladder_qwen_validation_v1_inspection_20260525.md",
        config_examples=(
            "configs/experiments/exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_ollama.json",
            "configs/experiments/test_holdout/exect_s1_clean_ladder_v2_qwen35b_test.json",
        ),
    ),
    _exect_spec(
        "exect.s1.section_aware",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_SECTION_AWARE_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_PROMPT_VERSION,
        status="rejected_arm",
        stage_graph_id=EXECT_S0_S1_STAGE_GRAPH_BY_VARIANT.get(
            EXECT_S0_S1_SECTION_AWARE_VARIANT
        ),
    ),
    _exect_spec(
        "exect.s1.prompt_graph_parallel",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_PROMPT_VERSION,
        status="rejected_arm",
        stage_graph_id=EXECT_S0_S1_STAGE_GRAPH_BY_VARIANT.get(
            EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT
        ),
    ),
    _exect_spec(
        "exect.s1.prompt_graph_sequential",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_PROMPT_VERSION,
        stage_graph_id=EXECT_S0_S1_STAGE_GRAPH_BY_VARIANT.get(
            EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT
        ),
    ),
    _exect_spec(
        "exect.s1.diagnosis_recall",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_DIAGNOSIS_RECALL_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s1.verify_repair",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_VERIFY_REPAIR_PROMPT_VERSION,
        stage_graph_id=EXECT_S0_S1_STAGE_GRAPH_BY_VARIANT.get(
            EXECT_S0_S1_VERIFY_REPAIR_VARIANT
        ),
    ),
    _exect_spec(
        "exect.s1.deterministic_only",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_D1_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s1.l0_minimal",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_L0_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s1.l1_schema",
        EXECT_S0_S1_SCHEMA_LEVEL,
        EXECT_S0_S1_VARIANT,
        EXECT_S0_S1_SCORER,
        EXECT_S0_S1_L1_SCHEMA_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s2.single_pass",
        EXECT_S2_SCHEMA_LEVEL,
        EXECT_S2_VARIANT,
        EXECT_S2_SCORER,
        EXECT_S2_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s2.comorbidity_c0",
        EXECT_S2_SCHEMA_LEVEL,
        EXECT_S2_COMORBIDITY_C0_VARIANT,
        EXECT_S2_SCORER,
        EXECT_S2_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s2.comorbidity_c0_c1",
        EXECT_S2_SCHEMA_LEVEL,
        EXECT_S2_COMORBIDITY_C0_C1_VARIANT,
        EXECT_S2_SCORER,
        EXECT_S2_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s2.investigation_guard_i0",
        EXECT_S2_SCHEMA_LEVEL,
        EXECT_S2_INV_GUARD_I0_VARIANT,
        EXECT_S2_SCORER,
        EXECT_S2_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s2.clean_ladder_v1",
        EXECT_S2_SCHEMA_LEVEL,
        EXECT_S2_CLEAN_LADDER_V1_VARIANT,
        EXECT_S2_SCORER,
        EXECT_S2_PROMPT_VERSION,
        status="diagnostic_baseline",
        stage_graph_id="g1_l1_policy_bridges",
        implementation_variant="clean_ladder_v1_i0_c0_c1_am_guard",
        decision_doc=(
            "docs/archive/experiments/exect/s0_s1_label_policy_trail/"
            "exect_s2_s3_clean_ladder_gpt_validation_v1_inspection_20260525.md"
        ),
        config_examples=(
            "configs/experiments/exect_s2_clean_ladder_v1_full_gpt4_1_mini.json",
            "configs/experiments/test_holdout/exect_s2_clean_ladder_v1_gpt4_test.json",
        ),
    ),
    _exect_spec(
        "exect.s3.single_pass",
        EXECT_S3_SCHEMA_LEVEL,
        EXECT_S3_VARIANT,
        EXECT_S3_SCORER,
        EXECT_S3_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s3.cause_bridge_k0_k1",
        EXECT_S3_SCHEMA_LEVEL,
        EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
        EXECT_S3_SCORER,
        EXECT_S3_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s3.clean_ladder_v1",
        EXECT_S3_SCHEMA_LEVEL,
        EXECT_S3_CLEAN_LADDER_V1_VARIANT,
        EXECT_S3_SCORER,
        EXECT_S3_PROMPT_VERSION,
        status="diagnostic_baseline",
        stage_graph_id="g1_l1_policy_bridges",
        implementation_variant="clean_ladder_v1_s2_guards_plus_cause_k0_k1",
        decision_doc=(
            "docs/archive/experiments/exect/s0_s1_label_policy_trail/"
            "exect_s2_s3_clean_ladder_gpt_validation_v1_inspection_20260525.md"
        ),
        config_examples=(
            "configs/experiments/exect_s3_clean_ladder_v1_full_gpt4_1_mini.json",
            "configs/experiments/test_holdout/exect_s3_clean_ladder_v1_gpt4_test.json",
        ),
    ),
    _exect_spec(
        "exect.s4.l1_single_pass",
        EXECT_S4_SCHEMA_LEVEL,
        EXECT_S4_L1_VARIANT,
        EXECT_S4_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s4.operational_k0_k1",
        EXECT_S4_SCHEMA_LEVEL,
        EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT,
        EXECT_S4_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="diagnostic_baseline",
        stage_graph_id="g1_l1_policy_bridges",
        decision_doc=(
            "docs/archive/experiments/exect/model_comparison_diagnostics/"
            "exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md"
        ),
        config_examples=(
            "configs/experiments/exect_s4_validation_full_gpt4_1_mini.json",
            "configs/experiments/test_holdout/exect_s4_clean_ladder_v1_gpt4_test.json",
        ),
    ),
    _exect_spec(
        "exect.s4.frequency_pre_vocab",
        EXECT_S4_SCHEMA_LEVEL,
        EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
        EXECT_S4_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="rejected_arm",
    ),
    _exect_spec(
        "exect.s4.frequency_pre_vocab_high_precision",
        EXECT_S4_SCHEMA_LEVEL,
        EXECT_S4_FREQUENCY_PRE_VOCAB_HIGH_PRECISION_VARIANT,
        EXECT_S4_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="rejected_arm",
    ),
    _exect_spec(
        "exect.s4.frequency_post_merge",
        EXECT_S4_SCHEMA_LEVEL,
        EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
        EXECT_S4_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s4.frequency_structured_slots",
        EXECT_S4_SCHEMA_LEVEL,
        EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT,
        EXECT_S4_SCORER,
        EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s4.temporality_post_classifier",
        EXECT_S4_SCHEMA_LEVEL,
        EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
        EXECT_S4_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="rejected_arm",
    ),
    _exect_spec(
        "exect.s4.mt_guard_non_asm",
        EXECT_S4_SCHEMA_LEVEL,
        EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
        EXECT_S4_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s4.mt_guard_non_asm_dose_current",
        EXECT_S4_SCHEMA_LEVEL,
        EXECT_S4_MT_GUARD_NON_ASM_DOSE_CURRENT_VARIANT,
        EXECT_S4_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s5.s4_l1_compat",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S4_L1_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s5.s4_operational_k0_k1_compat",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S4_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s5.s4_frequency_pre_vocab_compat",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="rejected_arm",
    ),
    _exect_spec(
        "exect.s5.s4_frequency_pre_vocab_high_precision_compat",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S4_FREQUENCY_PRE_VOCAB_HIGH_PRECISION_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="rejected_arm",
    ),
    _exect_spec(
        "exect.s5.s4_frequency_post_merge_compat",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s5.s4_frequency_structured_slots_compat",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s5.s4_temporality_post_classifier_compat",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="rejected_arm",
    ),
    _exect_spec(
        "exect.s5.s4_mt_guard_non_asm_compat",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s5.s4_mt_guard_non_asm_dose_current_compat",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S4_MT_GUARD_NON_ASM_DOSE_CURRENT_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s5.am_guard_non_asm_brand_alias",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s5.frequency_pre_vocab_am_guard",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s5.frequency_verify_v1",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
    ),
    _exect_spec(
        "exect.s5.frequency_verify_v2",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="rejected_arm",
        replacement_target="exect.s5.v2b_operational",
    ),
    _exect_spec(
        "exect.s5.v2b_operational",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="operational_baseline",
        stage_graph_id="g2_extract_verify",
        decision_doc=(
            "docs/experiments/exect/"
            "exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md"
        ),
        config_examples=(
            "configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini.json",
            "configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama.json",
            "configs/experiments/test_holdout/exect_s5_v2b_gpt4_test.json",
        ),
        notes="Current stacked ExECT S5 baseline, not an isolated component ceiling.",
    ),
    _exect_spec(
        "exect.s5.temporal_frequency_verify",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="rejected_arm",
    ),
    _exect_spec(
        "exect.s5.core_parallel_v2b",
        EXECT_S5_SCHEMA_LEVEL,
        EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT,
        EXECT_S5_SCORER,
        EXECT_S4_PROMPT_VERSION,
        status="rejected_arm",
        stage_graph_id=EXECT_S5_STAGE_GRAPH_BY_VARIANT.get(
            EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT
        ),
        replacement_target="exect.s5.v2b_operational",
    ),
)


@lru_cache(maxsize=1)
def program_variant_registry_by_id() -> dict[str, ProgramVariantSpec]:
    return {spec.variant_id: spec for spec in PROGRAM_VARIANT_REGISTRY}


def program_variant_specs_for_contract(
    *,
    dataset: str,
    schema_level: str,
    program_variant: str,
) -> tuple[ProgramVariantSpec, ...]:
    return tuple(
        spec
        for spec in PROGRAM_VARIANT_REGISTRY
        if spec.dataset == dataset
        and spec.schema_level == schema_level
        and spec.program_variant == program_variant
    )


def program_contract_allows(
    *,
    dataset: str,
    schema_level: str,
    program_variant: str,
    scorer_mode: str,
) -> bool:
    return any(
        scorer_mode in spec.scorer_modes and spec.is_loadable_config_contract
        for spec in program_variant_specs_for_contract(
            dataset=dataset,
            schema_level=schema_level,
            program_variant=program_variant,
        )
    )


def active_program_variant_specs() -> tuple[ProgramVariantSpec, ...]:
    inactive_statuses = {"historical", "rejected_arm", "blocked"}
    return tuple(
        spec for spec in PROGRAM_VARIANT_REGISTRY if spec.status not in inactive_statuses
    )


def _iter_config_payloads(repo_root: Path) -> list[tuple[Path, dict]]:
    config_root = repo_root / "configs" / "experiments"
    payloads: list[tuple[Path, dict]] = []
    if not config_root.exists():
        return payloads
    for path in sorted(config_root.rglob("*.json")):
        try:
            payloads.append(
                (path.relative_to(repo_root), json.loads(path.read_text(encoding="utf-8")))
            )
        except json.JSONDecodeError:
            continue
    return payloads


def _config_matches_spec(payload: dict, spec: ProgramVariantSpec) -> bool:
    if payload.get("dataset") != spec.dataset:
        return False
    if payload.get("schema_level") != spec.schema_level:
        return False
    if payload.get("program_variant") != spec.program_variant:
        return False
    if payload.get("scorer_mode") not in spec.scorer_modes:
        return False
    if (
        spec.status in STATUS_REQUIRES_EXACT_PROMPT
        and payload.get("prompt_version") != spec.prompt_default
    ):
        return False
    if spec.implementation_variant:
        taxonomy = payload.get("taxonomy") or {}
        if taxonomy.get("implementation_variant") != spec.implementation_variant:
            return False
    return True


def config_count_for_spec(spec: ProgramVariantSpec, *, repo_root: Path) -> int:
    payloads = _iter_config_payloads(repo_root)
    return sum(1 for _, payload in payloads if _config_matches_spec(payload, spec))


def render_program_variant_registry_markdown(repo_root: Path | None = None) -> str:
    root = repo_root or Path.cwd()
    lines = [
        "# Program Variant Registry",
        "",
        "Status: current synthesis",
        "",
        "Generated from `clinical_extraction.experiments.program_variant_registry`.",
        "",
        "| Variant ID | Dataset | Status | Schema Level | Program Variant | Prompt Default | Stage Graph | Scorers | Config Count | Decision Doc |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for spec in PROGRAM_VARIANT_REGISTRY:
        decision_doc = spec.decision_doc or ""
        stage_graph = spec.stage_graph_id or ""
        scorers = ", ".join(spec.scorer_modes)
        lines.append(
            "| "
            + " | ".join(
                [
                    spec.variant_id,
                    spec.dataset_label,
                    spec.status,
                    spec.schema_level,
                    spec.program_variant,
                    spec.prompt_default,
                    stage_graph,
                    scorers,
                    str(config_count_for_spec(spec, repo_root=root)),
                    decision_doc,
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"
