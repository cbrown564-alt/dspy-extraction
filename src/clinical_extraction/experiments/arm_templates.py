"""Experiment arm templates for taxonomy-governed hybrid comparisons.

Builders prefill L1/H1/H2/H3/H4/D1 taxonomy metadata, default controls, and
primitive compatibility checks so new configs vary the intended factor instead
of silently drifting helper semantics or comparison-group conventions.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from clinical_extraction.experiments.config import (
    ExperimentConfig,
    ExperimentControls,
    StructuredOutputStrategy,
)
from clinical_extraction.experiments.taxonomy import (
    ClinicalTaskFamilyValue,
    DatasetValue,
    ExperimentTaxonomy,
    HybridBalanceClassValue,
    IntendedDecisionValue,
    InterleavingPositionValue,
    ProgramArchitectureValue,
    SchemaComplexityValue,
    VariedFactorValue,
)
from clinical_extraction.primitives import (
    PrimitiveArmValue,
    PrimitiveMetadata,
    primitive_registry_by_id,
)
from clinical_extraction.schemas import FrozenModel

ExperimentArmKind = Literal["L1", "H1", "H2", "H3", "H4", "D1"]

COMPARISON_GROUP_SUFFIX_PATTERN = re.compile(r"^[_a-z0-9]+_v[0-9]+$")

ARM_HYBRID_BALANCE: dict[ExperimentArmKind, list[HybridBalanceClassValue]] = {
    "L1": ["L1_llm_constrained"],
    "H1": ["H1_post_deterministic"],
    "H2": ["H2_pre_deterministic"],
    "H3": ["H3_interleaved_tool_hybrid"],
    "H4": ["H4_deterministic_first_llm_adjudicates"],
    "D1": ["D1_deterministic_only"],
}

ARM_INTERLEAVING_POSITIONS: dict[ExperimentArmKind, list[InterleavingPositionValue]] = {
    "L1": ["during"],
    "H1": ["during", "post"],
    "H2": ["pre", "during"],
    "H3": ["tool_during", "during"],
    "H4": ["pre", "during", "post"],
    "D1": ["eval_only"],
}

ARM_EXPECTED_PRIMITIVE_POSITIONS: dict[ExperimentArmKind, frozenset[InterleavingPositionValue]] = {
    "L1": frozenset(),
    "H1": frozenset({"post", "eval_only"}),
    "H2": frozenset({"pre"}),
    "H3": frozenset({"tool_during"}),
    "H4": frozenset({"pre", "during", "post"}),
    "D1": frozenset({"eval_only", "post"}),
}


class ArmTemplateDefinition(FrozenModel):
    arm: ExperimentArmKind
    hybrid_balance_class: list[HybridBalanceClassValue]
    interleaving_positions: list[InterleavingPositionValue]
    default_varied_factor: VariedFactorValue = "interleaving_position"
    description: str


class ArmStudyContext(FrozenModel):
    dataset: DatasetValue
    schema_complexity: SchemaComplexityValue
    program_architecture: ProgramArchitectureValue
    clinical_task_family: ClinicalTaskFamilyValue | list[ClinicalTaskFamilyValue]
    comparison_group: str
    varied_factor: VariedFactorValue = "interleaving_position"
    intended_decision: IntendedDecisionValue = "pending"

    @model_validator(mode="after")
    def validate_comparison_group(self) -> ArmStudyContext:
        validate_comparison_group_id(self.comparison_group, dataset=self.dataset)
        return self


def list_arm_template_definitions() -> tuple[ArmTemplateDefinition, ...]:
    descriptions = {
        "L1": "LLM extraction with schema constraints; no deterministic bridge or pre-candidate injection.",
        "H1": "LLM extraction followed by post-hoc benchmark bridges or evidence guards.",
        "H2": "Deterministic candidates or vocabularies injected before LLM extraction.",
        "H3": "LLM can call deterministic tools during reasoning or extraction.",
        "H4": "Deterministic candidates first; LLM verifies, adjudicates, or repairs.",
        "D1": "Deterministic-only diagnostics, scorer checks, or primitive validation.",
    }
    return tuple(
        ArmTemplateDefinition(
            arm=arm,
            hybrid_balance_class=ARM_HYBRID_BALANCE[arm],
            interleaving_positions=ARM_INTERLEAVING_POSITIONS[arm],
            description=descriptions[arm],
        )
        for arm in ("L1", "H1", "H2", "H3", "H4", "D1")
    )


def build_comparison_group_id(
    *,
    schema_complexity: SchemaComplexityValue,
    factor: str,
    model_track: str,
    scope: str,
    version: int,
) -> str:
    if version < 1:
        raise ValueError("comparison group version must be >= 1.")
    for part_name, part in [
        ("factor", factor),
        ("model_track", model_track),
        ("scope", scope),
    ]:
        if not part or not part.strip():
            raise ValueError(f"{part_name} must be a non-empty string.")
        if " " in part:
            raise ValueError(f"{part_name} must not contain spaces.")
    group_id = f"{schema_complexity}_{factor}_{model_track}_{scope}_v{version}"
    validate_comparison_group_id(group_id)
    return group_id


def validate_comparison_group_id(
    comparison_group: str,
    *,
    dataset: DatasetValue | None = None,
) -> None:
    if not comparison_group or not comparison_group.strip():
        raise ValueError("comparison_group must be a non-empty string.")
    if " " in comparison_group:
        raise ValueError("comparison_group must not contain spaces.")
    if not COMPARISON_GROUP_SUFFIX_PATTERN.search(comparison_group):
        raise ValueError(
            "comparison_group must use lowercase snake_case and end with _v<number>."
        )
    if dataset == "gan_2026" and comparison_group.startswith("exect_"):
        raise ValueError(
            "gan_2026 comparison groups must not use an exect_* prefix."
        )
    if dataset == "exect_v2" and comparison_group.startswith("gan_"):
        raise ValueError(
            "exect_v2 comparison groups must not use a gan_* prefix."
        )


def validate_primitives_for_arm(
    arm: ExperimentArmKind,
    primitive_ids: list[str],
) -> None:
    registry = primitive_registry_by_id()
    expected_positions = ARM_EXPECTED_PRIMITIVE_POSITIONS[arm]
    for primitive_id in primitive_ids:
        metadata = registry.get(primitive_id)
        if metadata is None:
            raise ValueError(f"Unknown primitive_id: {primitive_id}")
        if arm not in metadata.compatible_experiment_arms:
            raise ValueError(
                f"Primitive {primitive_id} is not compatible with arm {arm}; "
                f"compatible_experiment_arms={metadata.compatible_experiment_arms}."
            )
        if expected_positions and not (
            set(metadata.interleaving_positions) & expected_positions
        ):
            raise ValueError(
                f"Primitive {primitive_id} interleaving_positions "
                f"{metadata.interleaving_positions} do not match arm {arm} "
                f"expected positions {sorted(expected_positions)}."
            )


def validate_arm_comparison_suite(
    arm_taxonomies: dict[ExperimentArmKind, ExperimentTaxonomy],
) -> None:
    if not arm_taxonomies:
        raise ValueError("arm_taxonomies must include at least one arm.")
    reference = next(iter(arm_taxonomies.values()))
    for arm, taxonomy in arm_taxonomies.items():
        if taxonomy.comparison_group != reference.comparison_group:
            raise ValueError(
                f"Arm {arm} comparison_group {taxonomy.comparison_group!r} "
                f"does not match suite anchor {reference.comparison_group!r}."
            )
        if taxonomy.dataset != reference.dataset:
            raise ValueError(
                f"Arm {arm} dataset {taxonomy.dataset!r} does not match suite anchor."
            )
        if taxonomy.schema_complexity != reference.schema_complexity:
            raise ValueError(
                f"Arm {arm} schema_complexity {taxonomy.schema_complexity!r} "
                "does not match suite anchor."
            )


def build_arm_taxonomy(
    arm: ExperimentArmKind,
    context: ArmStudyContext,
    *,
    include_h2_with_h4: bool = False,
) -> ExperimentTaxonomy:
    hybrid_balance = list(ARM_HYBRID_BALANCE[arm])
    if arm == "H4" and include_h2_with_h4:
        hybrid_balance = [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ]
    return ExperimentTaxonomy(
        dataset=context.dataset,
        schema_complexity=context.schema_complexity,
        program_architecture=context.program_architecture,
        hybrid_balance_class=hybrid_balance,
        interleaving_positions=list(ARM_INTERLEAVING_POSITIONS[arm]),
        varied_factor=context.varied_factor,
        comparison_group=context.comparison_group,
        intended_decision=context.intended_decision,
        clinical_task_family=context.clinical_task_family,
    )


def _family_label(
    clinical_task_family: ClinicalTaskFamilyValue | list[ClinicalTaskFamilyValue],
) -> str:
    if isinstance(clinical_task_family, list):
        if len(clinical_task_family) == 1:
            return clinical_task_family[0]
        return "multi_family"
    return clinical_task_family


def _default_context_policy(
    arm: ExperimentArmKind,
    *,
    family_label: str,
    primitive_ids: list[str],
) -> str:
    if arm == "L1":
        return "full_note"
    if arm == "H2":
        if family_label == "medication" or any(
            pid.startswith("exect.medication.") for pid in primitive_ids
        ):
            return "full_note_plus_precomputed_medication_candidates"
        if family_label == "frequency" or any(
            pid.startswith("exect.frequency.") or pid.startswith("gan.frequency.")
            for pid in primitive_ids
        ):
            return "full_note_plus_precomputed_seizure_frequency_candidates"
        return "full_note_plus_precomputed_family_candidates"
    if arm == "H3":
        return "full_note_plus_bounded_react_temporal_tools"
    if arm == "H4":
        if any(pid == "gan.frequency.temporal_candidates.v1" for pid in primitive_ids):
            return "full_note_plus_deterministic_temporal_candidates"
        return "full_note_plus_precomputed_family_candidates"
    return "full_note"


def _default_repair_policy(arm: ExperimentArmKind, *, raw_l1: bool) -> str:
    if arm == "L1":
        return "raw_no_benchmark_bridges" if raw_l1 else "none"
    if arm == "H1":
        return "artifact_benchmark_bridge_only"
    if arm in {"H3", "H4"}:
        return "artifact_bridge_surface_normalization_only"
    return "none"


def _default_verifier_policy(arm: ExperimentArmKind) -> str:
    if arm == "H4":
        return (
            "explicit two-stage confirm-first verify/repair with deterministic "
            "temporal-candidate hints"
        )
    if arm == "H3":
        return (
            "bounded dspy.ReAct loop with deterministic temporal tools "
            "(max 4 iterations) then ChainOfThought extract"
        )
    return "none"


def _default_abstention_policy(dataset: DatasetValue) -> str:
    if dataset == "gan_2026":
        return "allow_explicit_abstain_flag"
    return "empty_lists_for_no_supported_field_values"


def build_arm_controls(
    arm: ExperimentArmKind,
    context: ArmStudyContext,
    *,
    primitive_ids: list[str] | None = None,
    raw_l1: bool = False,
    repair_policy: str | None = None,
    context_policy: str | None = None,
    verifier_policy: str | None = None,
    few_shot_policy: str | None = None,
    abstention_policy: str | None = None,
) -> ExperimentControls:
    primitive_ids = primitive_ids or []
    if primitive_ids:
        validate_primitives_for_arm(arm, primitive_ids)
    family_label = _family_label(context.clinical_task_family)
    return ExperimentControls(
        few_shot_policy=(
            few_shot_policy
            or (
                "none"
                if context.dataset == "gan_2026"
                else "embedded benchmark-facing label-policy examples"
            )
        ),
        context_policy=context_policy
        or _default_context_policy(arm, family_label=family_label, primitive_ids=primitive_ids),
        verifier_policy=verifier_policy or _default_verifier_policy(arm),
        repair_policy=repair_policy or _default_repair_policy(arm, raw_l1=raw_l1),
        abstention_policy=abstention_policy or _default_abstention_policy(context.dataset),
    )


def _default_metric_caveats(
    arm: ExperimentArmKind,
    context: ArmStudyContext,
    *,
    primitive_ids: list[str],
) -> list[str]:
    caveats = [
        f"{arm} arm in comparison group {context.comparison_group}.",
        f"varied_factor={context.varied_factor}; intended_decision={context.intended_decision}.",
    ]
    if primitive_ids:
        caveats.append(f"Primitive IDs: {', '.join(primitive_ids)}.")
    registry = primitive_registry_by_id()
    for primitive_id in primitive_ids:
        metadata = registry[primitive_id]
        if metadata.caveats:
            caveats.append(f"{primitive_id}: {metadata.caveats[0]}")
    return caveats


def build_experiment_arm_config(
    arm: ExperimentArmKind,
    context: ArmStudyContext,
    *,
    experiment_id: str,
    hypothesis: str,
    split_name: str,
    split_file: str | Path,
    model_config_path: str | Path,
    schema_level: str,
    program_variant: str,
    scorer_mode: str,
    prompt_version: str,
    dataset: DatasetValue | None = None,
    primitive_ids: list[str] | None = None,
    metric_caveats: list[str] | None = None,
    raw_l1: bool = False,
    include_h2_with_h4: bool = False,
    structured_output_strategy: StructuredOutputStrategy = (
        "provider_json_schema_with_pydantic_validation"
    ),
    output_root: str | Path = "runs",
    max_records: int | None = None,
    record_ids: list[str] | None = None,
    report_on_test_split: bool = False,
    repair_policy: str | None = None,
    context_policy: str | None = None,
    verifier_policy: str | None = None,
    few_shot_policy: str | None = None,
    abstention_policy: str | None = None,
) -> ExperimentConfig:
    primitive_ids = list(primitive_ids or [])
    if primitive_ids:
        validate_primitives_for_arm(arm, primitive_ids)
    if arm == "H4" and any(
        pid == "gan.frequency.temporal_candidates.v1" for pid in primitive_ids
    ):
        include_h2_with_h4 = True

    taxonomy = build_arm_taxonomy(
        arm,
        context,
        include_h2_with_h4=include_h2_with_h4,
    )
    controls = build_arm_controls(
        arm,
        context,
        primitive_ids=primitive_ids,
        raw_l1=raw_l1,
        repair_policy=repair_policy,
        context_policy=context_policy,
        verifier_policy=verifier_policy,
        few_shot_policy=few_shot_policy,
        abstention_policy=abstention_policy,
    )
    merged_caveats = _default_metric_caveats(arm, context, primitive_ids=primitive_ids)
    if metric_caveats:
        merged_caveats.extend(metric_caveats)

    return ExperimentConfig(
        experiment_id=experiment_id,
        hypothesis=hypothesis,
        dataset=dataset or context.dataset,
        split_name=split_name,
        split_file=Path(split_file),
        model_config_path=Path(model_config_path),
        schema_level=schema_level,
        program_variant=program_variant,
        scorer_mode=scorer_mode,
        prompt_version=prompt_version,
        controls=controls,
        structured_output_strategy=structured_output_strategy,
        output_root=Path(output_root),
        max_records=max_records,
        record_ids=record_ids,
        report_on_test_split=report_on_test_split,
        metric_caveats=merged_caveats,
        taxonomy=taxonomy,
    )


def primitive_ids_for_arms(*arms: ExperimentArmKind) -> dict[ExperimentArmKind, list[str]]:
    """Return implemented primitive IDs grouped by compatible experiment arm."""
    grouped: dict[ExperimentArmKind, list[str]] = {arm: [] for arm in arms}
    for metadata in primitive_registry_by_id().values():
        if metadata.status not in {"implemented", "validated"}:
            continue
        for arm in metadata.compatible_experiment_arms:
            if arm in grouped and metadata.primitive_id not in grouped[arm]:
                grouped[arm].append(metadata.primitive_id)
    for arm in grouped:
        grouped[arm].sort()
    return grouped


def arm_for_primitive(metadata: PrimitiveMetadata) -> list[PrimitiveArmValue]:
    return list(metadata.compatible_experiment_arms)
