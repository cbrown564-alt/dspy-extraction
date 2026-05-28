"""Typed ExECT S1 raw/bridge/final inspection surfaces."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
)
from clinical_extraction.schemas import ExtractedValue, FrozenModel, NormalizedValue

EXECT_S1_BOUNDARY_SURFACE_VERSION = "exect_s1_boundary_surfaces.v1"
EXECT_S1_BOUNDARY_FIELDS = (
    "diagnosis",
    "seizure_type",
    "annotated_medication",
)

S1FieldName = Literal["diagnosis", "seizure_type", "annotated_medication"]
S1BridgeStage = Literal["inline", "post", "none"]
S1BridgeStatus = Literal["kept", "dropped", "augmented"]


class S1BridgePolicy(FrozenModel):
    """Prediction-time benchmark-bridge policy used for an S1 artifact."""

    apply_benchmark_bridges: bool
    bridge_stage: S1BridgeStage
    repair_policy: str
    program_variant: str


class S1PromptPolicyEffects(FrozenModel):
    """Prompt-policy provenance for raw model outputs before deterministic bridges."""

    prompt_version: str
    source_prompt_version_by_field: dict[S1FieldName, str]
    raw_output_count_by_field: dict[S1FieldName, int]
    notes: list[str] = Field(default_factory=list)


class S1RawModelOutput(FrozenModel):
    """One raw model-emitted S1 value before deterministic bridge policy."""

    field_name: S1FieldName
    raw_value: str
    evidence_text: str | None = None
    output_index: int


class S1BridgeSurfaceValue(FrozenModel):
    """One deterministic bridge row, including dropped and augmented values."""

    field_name: S1FieldName
    raw_value: str | None = None
    canonical_value: NormalizedValue = None
    benchmark_value: NormalizedValue = None
    evidence_text: str | None = None
    bridge_flags: list[str] = Field(default_factory=list)
    bridge_status: S1BridgeStatus
    source_stage: str


class S1FinalArtifactValue(FrozenModel):
    """One final benchmark-facing value as it appears in DocumentPrediction."""

    field_name: S1FieldName
    raw_value: str | None = None
    normalized_value: NormalizedValue = None
    evidence_texts: list[str] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)


class S1BoundarySurfaces(FrozenModel):
    """Inspection metadata separating raw, bridge, prompt, and final S1 surfaces."""

    boundary_version: str = EXECT_S1_BOUNDARY_SURFACE_VERSION
    bridge_policy: S1BridgePolicy
    prompt_policy_effects: S1PromptPolicyEffects
    raw_model_outputs: dict[S1FieldName, list[S1RawModelOutput]]
    deterministic_bridge_values: dict[S1FieldName, list[S1BridgeSurfaceValue]]
    bridge_flags: dict[S1FieldName, list[str]]
    final_artifact_values: dict[S1FieldName, list[S1FinalArtifactValue]]


def build_s1_boundary_surfaces_metadata(
    *,
    pred: object,
    values: list[ExtractedValue],
    prompt_version: str,
    program_variant: str,
    repair_policy: str,
    apply_benchmark_bridges: bool,
    bridge_stage: str,
) -> dict[str, object]:
    """Build additive S1 inspection metadata without changing scored values."""

    raw_outputs = _s1_raw_model_output_surface(pred)
    final_values = _s1_final_artifact_surface(values)
    bridge_values = (
        _s1_bridge_value_surface(
            raw_outputs=raw_outputs,
            final_values=values,
        )
        if apply_benchmark_bridges
        else _empty_s1_surface_map()
    )
    bridge_flags = {
        field_name: _dedupe(
            [
                flag
                for row in bridge_values[field_name]
                for flag in row.bridge_flags
            ]
        )
        for field_name in EXECT_S1_BOUNDARY_FIELDS
    }

    surfaces = S1BoundarySurfaces(
        bridge_policy=S1BridgePolicy(
            apply_benchmark_bridges=apply_benchmark_bridges,
            bridge_stage=bridge_stage,
            repair_policy=repair_policy,
            program_variant=program_variant,
        ),
        prompt_policy_effects=_s1_prompt_policy_effects(
            pred=pred,
            prompt_version=prompt_version,
            raw_outputs=raw_outputs,
        ),
        raw_model_outputs=raw_outputs,
        deterministic_bridge_values=bridge_values,
        bridge_flags=bridge_flags,
        final_artifact_values=final_values,
    )
    return surfaces.model_dump()


def _empty_s1_surface_map() -> dict[str, list]:
    return {field_name: [] for field_name in EXECT_S1_BOUNDARY_FIELDS}


def _s1_raw_model_output_surface(
    pred: object,
) -> dict[str, list[S1RawModelOutput]]:
    outputs: dict[str, list[S1RawModelOutput]] = _empty_s1_surface_map()
    for field_name in EXECT_S1_BOUNDARY_FIELDS:
        raw_values = _as_list(getattr(pred, field_name, []))
        evidence_values = _as_list(getattr(pred, f"{field_name}_evidence", []))
        outputs[field_name] = [
            S1RawModelOutput(
                field_name=field_name,
                raw_value=raw_value,
                evidence_text=_evidence_at(evidence_values, index),
                output_index=index,
            )
            for index, raw_value in enumerate(raw_values)
        ]
    return outputs


def _s1_prompt_policy_effects(
    *,
    pred: object,
    prompt_version: str,
    raw_outputs: dict[str, list[S1RawModelOutput]],
) -> S1PromptPolicyEffects:
    source_prompt_version_by_field = {
        field_name: prompt_version
        for field_name in EXECT_S1_BOUNDARY_FIELDS
    }
    diagnosis_prompt_version = getattr(pred, "diagnosis_source_prompt_version", None)
    if diagnosis_prompt_version:
        source_prompt_version_by_field["diagnosis"] = str(diagnosis_prompt_version)

    seizure_medication_prompt_version = getattr(
        pred,
        "seizure_medication_source_prompt_version",
        None,
    )
    if seizure_medication_prompt_version:
        source_prompt_version_by_field["seizure_type"] = str(
            seizure_medication_prompt_version
        )
        source_prompt_version_by_field["annotated_medication"] = str(
            seizure_medication_prompt_version
        )

    notes: list[str] = []
    if len(set(source_prompt_version_by_field.values())) > 1:
        notes.append("field_prompt_policy_split")

    return S1PromptPolicyEffects(
        prompt_version=prompt_version,
        source_prompt_version_by_field=source_prompt_version_by_field,
        raw_output_count_by_field={
            field_name: len(raw_outputs[field_name])
            for field_name in EXECT_S1_BOUNDARY_FIELDS
        },
        notes=notes,
    )


def _s1_final_artifact_surface(
    values: list[ExtractedValue],
) -> dict[str, list[S1FinalArtifactValue]]:
    final_values: dict[str, list[S1FinalArtifactValue]] = _empty_s1_surface_map()
    for value in values:
        if value.field_name not in final_values:
            continue
        final_values[value.field_name].append(
            S1FinalArtifactValue(
                field_name=value.field_name,
                raw_value=value.raw_value,
                normalized_value=value.normalized_value,
                evidence_texts=[span.text for span in value.evidence],
                quality_flags=value.quality_flags,
            )
        )
    return final_values


def _s1_bridge_value_surface(
    *,
    raw_outputs: dict[str, list[S1RawModelOutput]],
    final_values: list[ExtractedValue],
) -> dict[str, list[S1BridgeSurfaceValue]]:
    bridge_values: dict[str, list[S1BridgeSurfaceValue]] = _empty_s1_surface_map()
    final_by_field = {
        field_name: [
            value for value in final_values if value.field_name == field_name
        ]
        for field_name in EXECT_S1_BOUNDARY_FIELDS
    }
    raw_signatures = {
        (field_name, raw_output.raw_value)
        for field_name in EXECT_S1_BOUNDARY_FIELDS
        for raw_output in raw_outputs[field_name]
    }

    for field_name in EXECT_S1_BOUNDARY_FIELDS:
        for raw_output in raw_outputs[field_name]:
            matched_values = [
                value
                for value in final_by_field[field_name]
                if value.raw_value == raw_output.raw_value
            ]
            if not matched_values:
                bridge_values[field_name].append(
                    S1BridgeSurfaceValue(
                        field_name=field_name,
                        raw_value=raw_output.raw_value,
                        canonical_value=_normalize_value(
                            field_name,
                            raw_output.raw_value,
                        ),
                        benchmark_value=None,
                        evidence_text=raw_output.evidence_text,
                        bridge_flags=[],
                        bridge_status="dropped",
                        source_stage="deterministic_bridge",
                    )
                )
                continue

            for value in matched_values:
                bridge_values[field_name].append(
                    _s1_bridge_surface_value_from_final(
                        field_name=field_name,
                        value=value,
                        evidence_text=raw_output.evidence_text,
                        bridge_status="kept",
                    )
                )

        for value in final_by_field[field_name]:
            if (field_name, value.raw_value) in raw_signatures:
                continue
            bridge_values[field_name].append(
                _s1_bridge_surface_value_from_final(
                    field_name=field_name,
                    value=value,
                    evidence_text=_first_value_evidence_text(value),
                    bridge_status="augmented",
                )
            )

    return bridge_values


def _s1_bridge_surface_value_from_final(
    *,
    field_name: str,
    value: ExtractedValue,
    evidence_text: str | None,
    bridge_status: str,
) -> S1BridgeSurfaceValue:
    raw_or_final_value = value.raw_value or (
        str(value.normalized_value) if value.normalized_value is not None else ""
    )
    return S1BridgeSurfaceValue(
        field_name=field_name,
        raw_value=value.raw_value,
        canonical_value=(
            _normalize_value(field_name, raw_or_final_value)
            if raw_or_final_value
            else None
        ),
        benchmark_value=value.normalized_value,
        evidence_text=evidence_text or _first_value_evidence_text(value),
        bridge_flags=_bridge_flags_from_final_value(value),
        bridge_status=bridge_status,
        source_stage="deterministic_bridge",
    )


def _bridge_flags_from_final_value(value: ExtractedValue) -> list[str]:
    return [
        flag
        for flag in value.quality_flags
        if flag == "specificity_collapsed"
        or flag.startswith("benchmark_bridge:")
        or flag.startswith("s1_clean_bridge:")
    ]


def _first_value_evidence_text(value: ExtractedValue) -> str | None:
    if not value.evidence:
        return None
    return value.evidence[0].text


def _normalize_value(field_name: str, value: str) -> str:
    if field_name == "annotated_medication":
        return canonical_medication_name(value)
    return canonical_clinical_phrase(value)


def _evidence_at(evidence_values: list[str], index: int) -> str | None:
    if index >= len(evidence_values):
        return None
    evidence = evidence_values[index].strip()
    return evidence or None


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [] if stripped.lower() in {"", "none", "null"} else [stripped]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
