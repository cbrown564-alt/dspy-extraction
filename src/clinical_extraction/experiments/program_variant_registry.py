from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from clinical_extraction.experiments.taxonomy import DatasetValue
from clinical_extraction.gan.scoring import GAN_PAPER_REPRODUCTION_SCORER
from clinical_extraction.gan.s0.variant_routing import (
    GAN_FREQUENCY_S0_SCORER,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_STAGE_GRAPH_BY_VARIANT,
    default_gan_frequency_s0_prompt_version,
)
from clinical_extraction.schemas import FrozenModel

EXECT_S5_SCHEMA_LEVEL = "exect_s5_core_field_family"

ProgramVariantStatusValue = Literal[
    "promoted_baseline",
    "mechanism_baseline",
    "diagnostic_baseline",
    "operational_baseline",
    "replay_provenance",
    "historical_arm",
    "rejected_arm",
    "blocked",
]

CURRENT_AUTHORITY_STATUSES = frozenset(
    {
        "promoted_baseline",
        "mechanism_baseline",
        "diagnostic_baseline",
        "operational_baseline",
    }
)
PROVENANCE_ONLY_STATUSES = frozenset(
    {
        "replay_provenance",
        "historical_arm",
        "rejected_arm",
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
    taxonomy_filters: tuple[tuple[str, str], ...] = ()
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
        return self.status != "blocked"

    @property
    def is_current_authority(self) -> bool:
        return self.status in CURRENT_AUTHORITY_STATUSES

    @property
    def authority_class(self) -> str:
        if self.is_current_authority:
            return "current_authority"
        if self.status in PROVENANCE_ONLY_STATUSES:
            return "docs_provenance"
        return "blocked"

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
    taxonomy_filters: tuple[tuple[str, str], ...] = (),
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
        taxonomy_filters=taxonomy_filters,
        config_examples=config_examples,
        notes=notes,
    )


GAN_SCORERS = (GAN_FREQUENCY_S0_SCORER, GAN_PAPER_REPRODUCTION_SCORER)


def _gan_spec(
    variant_id: str,
    program_variant: str,
    status: ProgramVariantStatusValue = "historical_arm",
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
    status: ProgramVariantStatusValue = "historical_arm",
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
    _spec(
        variant_id="gan.s0.builder_gap_v1",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        program_variant="gan_frequency_s0_temporal_candidates_single_pass",
        scorer_modes=("gan_frequency_deterministic_v1", "gan2026_paper_reproduction"),
        prompt_default="gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy",
        stage_graph_id="g2_candidates_adjudicate",
        status="promoted_baseline",
        decision_doc="docs/experiments/gan/gan_s0_operational_default_promotion_review_20260523.md",
        implementation_variant="gan_s0_candidate_builder_gap_v1",
        config_examples=(
            "configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json",
            "configs/experiments/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation.json",
        ),
        notes=(
            "Synthetic validation operational surface; direct paper-comparison tables "
            "must rescore with gan2026_paper_reproduction."
        ),
    ),
    _spec(
        variant_id="gan.s0.d1_v1_2b_schema_guard_only",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        program_variant="gan_frequency_s0_date_events_candidates_single_pass",
        scorer_modes=("gan_frequency_deterministic_v1", "gan2026_paper_reproduction"),
        prompt_default="gan_frequency_s0_date_events_candidates_v1_2b_schema_guard_only",
        stage_graph_id="g3_date_events_candidates_adjudicate",
        status="mechanism_baseline",
        decision_doc="docs/experiments/gan/gan_s0_r15_d1_guardrail_ablation_decision_20260528.md",
        config_examples=(
            "configs/experiments/gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini.json",
        ),
        notes="Current decomposed Gan S0 mechanism baseline after the May 28 pivot.",
    ),
    _spec(
        variant_id="gan.s0.temporal_candidates_adjudicate_constrained",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        program_variant="gan_frequency_s0_temporal_candidates_single_pass",
        scorer_modes=("gan_frequency_deterministic_v1", "gan2026_paper_reproduction"),
        prompt_default="gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy",
        stage_graph_id="g2_candidates_adjudicate",
        status="diagnostic_baseline",
        decision_doc="docs/experiments/gan/gan_s0_g2_model_arm_comparison_20260528.md",
        implementation_variant="candidate_constrained_adjudication_v1",
        config_examples=(
            "configs/experiments/gan_s0_g2_candidate_constrained_gpt4_1_mini_slice.json",
        ),
        notes=(
            "G2 model-arm comparison Arm B: deterministic candidates constraint "
            "target selection."
        ),
    ),
    _spec(
        variant_id="gan.s0.explicit_reason_code_adjudicator",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        program_variant="gan_frequency_s0_explicit_reason_code_adjudicator",
        scorer_modes=("gan_frequency_deterministic_v1", "gan2026_paper_reproduction"),
        prompt_default="gan_frequency_s0_explicit_reason_code_adjudicator_v1_0",
        stage_graph_id="g4_reason_code_adjudicator",
        status="diagnostic_baseline",
        decision_doc=(
            "docs/experiments/gan/"
            "gan_s0_g4_explicit_reason_code_adjudicator_report_20260528.md"
        ),
        implementation_variant="explicit_reason_code_adjudicator_v1",
        config_examples=(
            "configs/experiments/"
            "gan_s0_g4_explicit_reason_code_adjudicator_gpt4_1_mini_slice.json",
        ),
        notes=(
            "G4 same-slice reason-code adjudicator. Preserves trace fields but did "
            "not promote as tested because it underperformed the G2 constrained "
            "baselines via seizure-free-over-quantified target-selection failures."
        ),
    ),
    _spec(
        variant_id="gan.s0.special_class_target_selector",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        program_variant="gan_frequency_s0_special_class_target_selector",
        scorer_modes=("gan_frequency_deterministic_v1", "gan2026_paper_reproduction"),
        prompt_default="gan_frequency_s0_special_class_target_selector_v1_0",
        stage_graph_id="g7_special_class_target_selector",
        status="diagnostic_baseline",
        decision_doc=(
            "docs/experiments/gan/"
            "gan_s0_g8_special_class_target_selector_report_20260529.md"
        ),
        implementation_variant="special_class_target_selector_v1",
        config_examples=(
            "configs/experiments/"
            "gan_s0_g8_special_class_target_selector_gpt4_1_mini_smoke25.json",
            "configs/experiments/"
            "gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50.json",
        ),
        notes=(
            "G8/G7-protocol arm: D1 date/event payload plus indexed candidates, "
            "varying target-selection policy for quantified, seizure-free, "
            "unknown, no-reference, and cluster special classes."
        ),
    ),
    _spec(
        variant_id="gan.s0.candidate_ranking_target_selector",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        program_variant="gan_frequency_s0_candidate_ranking_target_selector",
        scorer_modes=("gan_frequency_deterministic_v1", "gan2026_paper_reproduction"),
        prompt_default="gan_frequency_s0_candidate_ranking_target_selector_v1_0",
        stage_graph_id="g10_candidate_ranking_target_selector",
        status="diagnostic_baseline",
        decision_doc=(
            "docs/experiments/gan/"
            "gan_s0_g10_candidate_ranking_target_selector_report_20260529.md"
        ),
        implementation_variant="candidate_ranking_target_selector_v1",
        config_examples=(
            "configs/experiments/"
            "gan_s0_g10_candidate_ranking_target_selector_gpt4_1_mini_standard50.json",
        ),
        notes=(
            "G10 narrowed category-ranking selector arm. Preserves category and "
            "candidate-rank traces, but is rejected as tested because it "
            "underperformed G8, D1 v1.2b, and builder-gap GPT on standard50."
        ),
    ),
    _spec(
        variant_id="gan.s0.support_aware_target_selector",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        program_variant="gan_frequency_s0_support_aware_target_selector",
        scorer_modes=("gan_frequency_deterministic_v1", "gan2026_paper_reproduction"),
        prompt_default="gan_frequency_s0_support_aware_target_selector_v1_0",
        stage_graph_id="g15_support_aware_target_selector",
        status="diagnostic_baseline",
        decision_doc=(
            "docs/experiments/gan/"
            "gan_s0_g15_support_aware_target_selector_report_20260529.md"
        ),
        implementation_variant="support_aware_target_selector_v1",
        config_examples=(
            "configs/experiments/"
            "gan_s0_g15_support_aware_target_selector_gpt4_1_mini_standard50.json",
        ),
        notes=(
            "G15 selector arm: fixed deterministic candidate/date payloads plus "
            "support metadata carrying G13 gate and G14 temporal caveats, varying "
            "only target-selection and semantic adjudication over candidate support."
        ),
    ),
    _spec(
        variant_id="exect.s1.clean_ladder_v1",
        dataset="exect_v2",
        schema_level="exect_s0_s1_field_family",
        program_variant="exect_s1_clean_ladder_v1_single_pass",
        scorer_modes=("exect_field_family_deterministic_v1",),
        prompt_default="exect_s0_s1_field_family_v4_10_label_policy",
        status="diagnostic_baseline",
    ),
    _spec(
        variant_id="exect.s1.clean_ladder_v1_family_span",
        dataset="exect_v2",
        schema_level="exect_s0_s1_field_family",
        program_variant="exect_s1_clean_ladder_v1_family_span_single_pass",
        scorer_modes=("exect_field_family_deterministic_v1",),
        prompt_default="exect_s0_s1_field_family_v4_10_label_policy",
        stage_graph_id="g1_l1_policy_bridges",
        status="diagnostic_baseline",
        decision_doc=(
            "docs/experiments/exect/"
            "exect_family_span_prompt_comparison_e8_preregistration_20260528.md"
        ),
        implementation_variant="clean_ladder_v1_family_span_context",
        config_examples=(
            "configs/experiments/exect_s1_family_span_e8_cap25_gpt4_1_mini.json",
        ),
        notes=(
            "E8 cap-slice mechanism probe: same S1 clean-ladder prompt/scorer as "
            "the full-note baseline, with E4 family-span context as the varied factor."
        ),
    ),
    _spec(
        variant_id="exect.s1.clean_ladder_v2_diagnosis_stable",
        dataset="exect_v2",
        schema_level="exect_s0_s1_field_family",
        program_variant="exect_s1_clean_ladder_v2_diagnosis_stable_ensemble",
        scorer_modes=("exect_field_family_deterministic_v1",),
        prompt_default="exect_s0_s1_field_family_v4_11_label_policy",
        stage_graph_id="g2_field_family_prompt_graph",
        status="diagnostic_baseline",
        decision_doc="docs/experiments/exect/exect_s1_clean_ladder_qwen_validation_v1_inspection_20260525.md",
        implementation_variant="v4_10_diagnosis_v4_11_seizure_medication_am_guard",
        config_examples=(
            "configs/experiments/exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_ollama.json",
            "configs/experiments/test_holdout/exect_s1_clean_ladder_v2_qwen35b_test.json",
        ),
    ),
    _spec(
        variant_id="exect.s2.clean_ladder_v1",
        dataset="exect_v2",
        schema_level="exect_s2_field_family",
        program_variant="exect_s2_field_family_clean_ladder_v1_single_pass",
        scorer_modes=("exect_s2_field_family_deterministic_v1",),
        prompt_default="exect_s2_field_family_v1_3_label_policy",
        stage_graph_id="g1_l1_policy_bridges",
        status="diagnostic_baseline",
        decision_doc=(
            "docs/archive/experiments/exect/s0_s1_label_policy_trail/"
            "exect_s2_s3_clean_ladder_gpt_validation_v1_inspection_20260525.md"
        ),
        implementation_variant="clean_ladder_v1_i0_c0_c1_am_guard",
        config_examples=(
            "configs/experiments/exect_s2_clean_ladder_v1_full_gpt4_1_mini.json",
            "configs/experiments/test_holdout/exect_s2_clean_ladder_v1_gpt4_test.json",
        ),
    ),
    _spec(
        variant_id="exect.s3.clean_ladder_v1",
        dataset="exect_v2",
        schema_level="exect_s3_field_family",
        program_variant="exect_s3_field_family_clean_ladder_v1_single_pass",
        scorer_modes=("exect_s3_field_family_deterministic_v1",),
        prompt_default="exect_s3_field_family_v1_2_label_policy",
        stage_graph_id="g1_l1_policy_bridges",
        status="diagnostic_baseline",
        decision_doc=(
            "docs/archive/experiments/exect/s0_s1_label_policy_trail/"
            "exect_s2_s3_clean_ladder_gpt_validation_v1_inspection_20260525.md"
        ),
        implementation_variant="clean_ladder_v1_s2_guards_plus_cause_k0_k1",
        config_examples=(
            "configs/experiments/exect_s3_clean_ladder_v1_full_gpt4_1_mini.json",
            "configs/experiments/test_holdout/exect_s3_clean_ladder_v1_gpt4_test.json",
        ),
    ),
    _spec(
        variant_id="exect.s4.operational_k0_k1",
        dataset="exect_v2",
        schema_level="exect_s4_field_family",
        program_variant="exect_s4_field_family_cause_bridge_k0_k1_single_pass",
        scorer_modes=("exect_s4_field_family_deterministic_v1",),
        prompt_default="exect_s4_field_family_v1_2_label_policy",
        stage_graph_id="g1_l1_policy_bridges",
        status="diagnostic_baseline",
        decision_doc=(
            "docs/archive/experiments/exect/model_comparison_diagnostics/"
            "exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md"
        ),
        config_examples=(
            "configs/experiments/exect_s4_validation_full_gpt4_1_mini.json",
            "configs/experiments/test_holdout/exect_s4_clean_ladder_v1_gpt4_test.json",
        ),
    ),
    _spec(
        variant_id="exect.s4.mt_guard_non_asm",
        dataset="exect_v2",
        schema_level="exect_s4_field_family",
        program_variant="exect_s4_field_family_mt_guard_non_asm_single_pass",
        scorer_modes=("exect_s4_field_family_deterministic_v1",),
        prompt_default="exect_s4_field_family_v1_2_label_policy",
        status="diagnostic_baseline",
        config_examples=(
            "configs/experiments/exect_s4_mt_guard_non_asm_full_gpt4_1_mini.json",
        ),
    ),
    _spec(
        variant_id="exect.s4.mt_guard_non_asm_dose_current",
        dataset="exect_v2",
        schema_level="exect_s4_field_family",
        program_variant="exect_s4_field_family_mt_guard_non_asm_dose_current_single_pass",
        scorer_modes=("exect_s4_field_family_deterministic_v1",),
        prompt_default="exect_s4_field_family_v1_2_label_policy",
        status="diagnostic_baseline",
        config_examples=(
            "configs/experiments/exect_s4_mt_guard_non_asm_dose_current_full_gpt4_1_mini.json",
        ),
    ),
    _spec(
        variant_id="exect.s5.v2b_operational",
        dataset="exect_v2",
        schema_level="exect_s5_core_field_family",
        program_variant="exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b",
        scorer_modes=("exect_s5_core_field_family_deterministic_v1",),
        prompt_default="exect_s4_field_family_v1_2_label_policy",
        stage_graph_id="g2_extract_verify",
        status="operational_baseline",
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
)

ARCHIVED_PROGRAM_VARIANT_PROVENANCE_PATH = (
    Path("docs")
    / "archive"
    / "experiments"
    / "synthesis"
    / "program_variant_registry_provenance_20260528.json"
)



@lru_cache(maxsize=1)
def program_variant_registry_by_id() -> dict[str, ProgramVariantSpec]:
    return {spec.variant_id: spec for spec in PROGRAM_VARIANT_REGISTRY}


@lru_cache(maxsize=1)
def archived_program_variant_specs() -> tuple[ProgramVariantSpec, ...]:
    path = ARCHIVED_PROGRAM_VARIANT_PROVENANCE_PATH
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.is_file():
        return ()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return tuple(
        ProgramVariantSpec.model_validate(row)
        for row in payload.get("variants", [])
    )


def _program_variant_specs(
    *, include_archive: bool = False
) -> tuple[ProgramVariantSpec, ...]:
    if include_archive:
        return PROGRAM_VARIANT_REGISTRY + archived_program_variant_specs()
    return PROGRAM_VARIANT_REGISTRY


def program_variant_specs_for_contract(
    *,
    dataset: str,
    schema_level: str,
    program_variant: str,
    include_archive: bool = False,
) -> tuple[ProgramVariantSpec, ...]:
    return tuple(
        spec
        for spec in _program_variant_specs(include_archive=include_archive)
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
    include_archive: bool = False,
) -> bool:
    return any(
        scorer_mode in spec.scorer_modes and spec.is_loadable_config_contract
        for spec in program_variant_specs_for_contract(
            dataset=dataset,
            schema_level=schema_level,
            program_variant=program_variant,
            include_archive=include_archive,
        )
    )


def current_authority_program_variant_specs() -> tuple[ProgramVariantSpec, ...]:
    return tuple(
        spec for spec in PROGRAM_VARIANT_REGISTRY if spec.is_current_authority
    )


def active_program_variant_specs() -> tuple[ProgramVariantSpec, ...]:
    """Legacy alias; use current_authority_program_variant_specs in new code."""

    return current_authority_program_variant_specs()


ConfigInventorySource = Literal["active", "archive", "all"]


def _config_roots(repo_root: Path, source: ConfigInventorySource) -> tuple[Path, ...]:
    active_root = repo_root / "configs" / "experiments"
    archive_root = repo_root / "archive" / "configs"
    if source == "active":
        return (active_root,)
    if source == "archive":
        return (archive_root,)
    return (active_root, archive_root)


def _iter_config_payloads(
    repo_root: Path, *, source: ConfigInventorySource = "active"
) -> list[tuple[Path, dict]]:
    payloads: list[tuple[Path, dict]] = []
    for config_root in _config_roots(repo_root, source):
        if not config_root.exists():
            continue
        for path in sorted(config_root.rglob("*.json")):
            try:
                payloads.append(
                    (
                        path.relative_to(repo_root),
                        json.loads(path.read_text(encoding="utf-8")),
                    )
                )
            except json.JSONDecodeError:
                continue
    return payloads


def _taxonomy_value(payload: dict, key: str) -> str | None:
    taxonomy = payload.get("taxonomy") or {}
    value = taxonomy.get(key)
    if isinstance(value, str):
        return value
    return None


def _config_matches_spec(payload: dict, spec: ProgramVariantSpec) -> bool:
    if payload.get("dataset") != spec.dataset:
        return False
    if payload.get("schema_level") != spec.schema_level:
        return False
    if payload.get("program_variant") != spec.program_variant:
        return False
    if payload.get("scorer_mode") not in spec.scorer_modes:
        return False
    if payload.get("prompt_version") != spec.prompt_default:
        return False
    if spec.implementation_variant:
        if (
            _taxonomy_value(payload, "implementation_variant")
            != spec.implementation_variant
        ):
            return False
    for key, expected_value in spec.taxonomy_filters:
        if _taxonomy_value(payload, key) != expected_value:
            return False
    return True


def _spec_match_score(
    spec: ProgramVariantSpec, *, config_path: Path | None
) -> tuple[int, int, int, int]:
    path_text = config_path.as_posix() if config_path is not None else ""
    return (
        int(path_text in spec.config_examples),
        len(spec.taxonomy_filters),
        int(spec.implementation_variant is not None),
        int(spec.is_current_authority),
    )


def resolve_program_variant_spec_for_config(
    payload: dict,
    *,
    config_path: Path | None = None,
    include_archive: bool = False,
) -> ProgramVariantSpec | None:
    matches = [
        spec
        for spec in _program_variant_specs(include_archive=include_archive)
        if _config_matches_spec(payload, spec)
    ]
    if not matches:
        return None
    return max(
        matches, key=lambda spec: _spec_match_score(spec, config_path=config_path)
    )


def config_count_for_spec(spec: ProgramVariantSpec, *, repo_root: Path) -> int:
    payloads = _iter_config_payloads(repo_root, source="active")
    return sum(
        1
        for path, payload in payloads
        if resolve_program_variant_spec_for_config(payload, config_path=path) == spec
    )


def archived_config_count_for_spec(
    spec: ProgramVariantSpec, *, repo_root: Path
) -> int:
    payloads = _iter_config_payloads(repo_root, source="archive")
    return sum(
        1
        for path, payload in payloads
        if resolve_program_variant_spec_for_config(
            payload, config_path=path, include_archive=True
        )
        == spec
    )


class ExperimentConfigInventoryRow(FrozenModel):
    """Resolved status row for one active or archived experiment config file."""

    config_path: str
    experiment_id: str
    variant_id: str
    dataset: str
    status: ProgramVariantStatusValue
    authority_class: str
    split_name: str
    run_scope: str
    scorer_mode: str
    prompt_version: str
    decision_doc: str | None = None


def _config_run_scope(payload: dict) -> str:
    if payload.get("report_on_test_split"):
        return "test_holdout"
    record_ids = payload.get("record_ids")
    if isinstance(record_ids, list):
        return f"cap_{len(record_ids)}"
    max_records = payload.get("max_records")
    if isinstance(max_records, int):
        return f"cap_{max_records}"
    return "full_validation"


def _config_authority_class(path: Path, spec: ProgramVariantSpec) -> str:
    if (
        len(path.parts) >= 2
        and path.parts[0] == "archive"
        and path.parts[1] == "configs"
    ):
        return "docs_provenance"
    return spec.authority_class


def experiment_config_inventory(
    *, repo_root: Path, source: ConfigInventorySource = "active"
) -> tuple[ExperimentConfigInventoryRow, ...]:
    rows: list[ExperimentConfigInventoryRow] = []
    include_archive = source in {"archive", "all"}
    for path, payload in _iter_config_payloads(repo_root, source=source):
        spec = resolve_program_variant_spec_for_config(
            payload,
            config_path=path,
            include_archive=include_archive,
        )
        if spec is None:
            continue
        rows.append(
            ExperimentConfigInventoryRow(
                config_path=path.as_posix(),
                experiment_id=str(payload.get("experiment_id", "")),
                variant_id=spec.variant_id,
                dataset=spec.dataset_label,
                status=spec.status,
                authority_class=_config_authority_class(path, spec),
                split_name=str(payload.get("split_name", "")),
                run_scope=_config_run_scope(payload),
                scorer_mode=str(payload.get("scorer_mode", "")),
                prompt_version=str(payload.get("prompt_version", "")),
                decision_doc=spec.decision_doc,
            )
        )
    return tuple(rows)


def render_program_variant_registry_markdown(repo_root: Path | None = None) -> str:
    root = repo_root or Path.cwd()
    lines = [
        "# Program Variant Registry",
        "",
        "Status: current synthesis",
        "",
        "Generated from `clinical_extraction.experiments.program_variant_registry`.",
        "",
        "C28 authority rule: ordinary config loading is active-only; archived",
        "configs are docs/file provenance, not active experiment counts. A row is",
        "current authority only when",
        "`Authority Class` is `current_authority`; rejected, historical, and replay",
        "rows preserve provenance without default replay/loadability guarantees.",
        "",
        "Status glossary:",
        "",
        "- `promoted_baseline`, `mechanism_baseline`, `diagnostic_baseline`, and",
        "  `operational_baseline` are current-authority rows with different caveats.",
        "- `replay_provenance` and `historical_arm` are docs/file provenance, not",
        "  current steering evidence.",
        "- `rejected_arm` preserves failed-arm provenance without an active replay",
        "  guarantee.",
        "- `blocked` is not a loadable experiment contract.",
        "",
        "C28 archive rule: rows under `Archived Config Inventory` are",
        "docs/file provenance by path, even when they describe a variant family",
        "whose status is current authority. Use explicit replay/reporting tools",
        "for archive artifacts.",
        "",
        "## Variant Status",
        "",
        "| Variant ID | Dataset | Status | Authority Class | Schema Level | Program Variant | Prompt Default | Stage Graph | Scorers | Active Config Count | Archived Config Count | Decision Doc |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for spec in _program_variant_specs(include_archive=True):
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
                    spec.authority_class,
                    spec.schema_level,
                    spec.program_variant,
                    spec.prompt_default,
                    stage_graph,
                    scorers,
                    str(config_count_for_spec(spec, repo_root=root)),
                    str(archived_config_count_for_spec(spec, repo_root=root)),
                    decision_doc,
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Active Config Inventory",
            "",
            "| Config Path | Experiment ID | Variant ID | Status | Authority Class | Split | Run Scope | Scorer | Prompt Version |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in experiment_config_inventory(repo_root=root, source="active"):
        lines.append(
            "| "
            + " | ".join(
                [
                    row.config_path,
                    row.experiment_id,
                    row.variant_id,
                    row.status,
                    row.authority_class,
                    row.split_name,
                    row.run_scope,
                    row.scorer_mode,
                    row.prompt_version,
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Archived Config Inventory",
            "",
            "| Config Path | Experiment ID | Variant ID | Status | Authority Class | Split | Run Scope | Scorer | Prompt Version |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in experiment_config_inventory(repo_root=root, source="archive"):
        lines.append(
            "| "
            + " | ".join(
                [
                    row.config_path,
                    row.experiment_id,
                    row.variant_id,
                    row.status,
                    row.authority_class,
                    row.split_name,
                    row.run_scope,
                    row.scorer_mode,
                    row.prompt_version,
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"
