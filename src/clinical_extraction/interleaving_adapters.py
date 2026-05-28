"""Interleaving adapters for taxonomy-governed primitive placement.

One primitive's core logic can be exposed at different pipeline positions
(pre, during, tool_during, post, eval_only) without duplicating the underlying
deterministic behavior.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from typing import Any, Literal, TypeAlias

from pydantic import Field

from clinical_extraction.experiments.taxonomy import InterleavingPositionValue
from clinical_extraction.experiments.taxonomy import InterleavingPositionValue as Position
from clinical_extraction.exect.medication_primitives import (
    build_exect_medication_candidate_payloads,
    exect_medication_benchmark_bridge,
)
from clinical_extraction.gan.primitives import (
    build_gan_frequency_candidate_payloads,
    check_gan_frequency_evidence_guard,
    gan_frequency_label_policy_bridge,
)
from clinical_extraction.primitives import (
    EvidenceSupportResult,
    NormalizationResult,
    PrimitiveCandidate,
    PrimitiveMetadata,
    primitive_registry_by_id,
)
from clinical_extraction.schemas import FrozenModel, NormalizedValue

CorePayload: TypeAlias = (
    list[PrimitiveCandidate] | NormalizationResult | EvidenceSupportResult
)


class InterleavingSurface(FrozenModel):
    """Base surface returned by an interleaving adapter."""

    position: InterleavingPositionValue
    primitive_id: str
    core_fingerprint: str
    reference_payload: CorePayload


class PreInjectionSurface(InterleavingSurface):
    position: Literal["pre"] = "pre"
    injected_context: str
    injected_note_text: str
    control_mode: Literal["soft_hint"] = "soft_hint"


class DuringPromptSurface(InterleavingSurface):
    position: Literal["during"] = "during"
    prompt_rules: list[str]
    control_mode: Literal["soft_hint"] = "soft_hint"


class ToolDuringSurface(InterleavingSurface):
    position: Literal["tool_during"] = "tool_during"
    tool_name: str
    tool_description: str
    execution_result: str
    control_mode: Literal["tool_affordance"] = "tool_affordance"


class PostProcessorSurface(InterleavingSurface):
    position: Literal["post"] = "post"
    input_value: NormalizedValue
    output_value: NormalizedValue
    prediction_affecting: bool = True
    control_mode: Literal["posthoc_correction"] = "posthoc_correction"
    support_status: str | None = None


class EvalOnlySurface(InterleavingSurface):
    position: Literal["eval_only"] = "eval_only"
    diagnostic_payload: NormalizationResult | EvidenceSupportResult
    prediction_affecting: bool = False
    control_mode: Literal["diagnostic_only"] = "diagnostic_only"


SurfaceValue = (
    PreInjectionSurface
    | DuringPromptSurface
    | ToolDuringSurface
    | PostProcessorSurface
    | EvalOnlySurface
)

RenderFn = Callable[["InterleavingAdapter", Position, CorePayload, dict[str, Any]], SurfaceValue]


class PrimitiveBinding(FrozenModel):
    primitive_id: str
    invoke: Any = Field(exclude=True)
    renderers: dict[InterleavingPositionValue, RenderFn] = Field(exclude=True)

    model_config = {"arbitrary_types_allowed": True}


def _candidate_fingerprint(candidates: Sequence[PrimitiveCandidate]) -> str:
    parts = tuple(
        (
            candidate.raw_text,
            str(candidate.normalized_value),
            str(candidate.benchmark_value),
        )
        for candidate in candidates
    )
    return repr(parts)


def _normalization_fingerprint(result: NormalizationResult) -> str:
    return repr(
        (
            result.raw_value,
            result.canonical_value,
            result.benchmark_value,
            result.transformation_rule,
        )
    )


def _evidence_fingerprint(result: EvidenceSupportResult) -> str:
    return repr(
        (
            result.support_status,
            result.quote,
            result.normalized_value,
            result.raw_quote_supported,
            result.normalized_interpretation_supported,
        )
    )


def fingerprint_payload(payload: CorePayload) -> str:
    if isinstance(payload, list):
        return _candidate_fingerprint(payload)
    if isinstance(payload, NormalizationResult):
        return _normalization_fingerprint(payload)
    if isinstance(payload, EvidenceSupportResult):
        return _evidence_fingerprint(payload)
    raise TypeError(f"Unsupported primitive payload type: {type(payload)!r}")


def _format_precomputed_candidate_context(
    *,
    field_label: str,
    values: Sequence[str],
    note_text: str,
) -> tuple[str, str]:
    injected_context = (
        "Precomputed benchmark-facing candidates (soft hints; emit only when note-supported):\n"
        f"{field_label}: {', '.join(values)}"
    )
    injected_note_text = "\n".join(
        [
            injected_context,
            "",
            "---",
            "",
            note_text,
        ]
    )
    return injected_context, injected_note_text


def _candidate_values(candidates: Sequence[PrimitiveCandidate]) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        value = candidate.benchmark_value or candidate.normalized_value or candidate.raw_text
        text = str(value)
        if text not in seen:
            seen.add(text)
            values.append(text)
    return values


def _render_candidate_pre(
    adapter: InterleavingAdapter,
    position: Position,
    payload: CorePayload,
    kwargs: dict[str, Any],
) -> PreInjectionSurface:
    assert isinstance(payload, list)
    note_text = str(kwargs["note_text"])
    field_label = adapter.metadata.field_families[0]
    if adapter.metadata.field_families == ["medication"]:
        field_label = "annotated_medication"
    injected_context, injected_note_text = _format_precomputed_candidate_context(
        field_label=field_label,
        values=_candidate_values(payload),
        note_text=note_text,
    )
    return PreInjectionSurface(
        primitive_id=adapter.primitive_id,
        core_fingerprint=fingerprint_payload(payload),
        reference_payload=payload,
        injected_context=injected_context,
        injected_note_text=injected_note_text,
    )


def _render_candidate_during(
    adapter: InterleavingAdapter,
    position: Position,
    payload: CorePayload,
    kwargs: dict[str, Any],
) -> DuringPromptSurface:
    assert isinstance(payload, list)
    values = _candidate_values(payload)
    field_label = adapter.metadata.field_families[0]
    if adapter.metadata.field_families == ["medication"]:
        field_label = "annotated_medication"
    prompt_rules = [
        (
            f"Use deterministic {field_label} candidates only when the note explicitly "
            "supports them."
        ),
        f"Candidate surfaces: {', '.join(values) if values else 'none found'}.",
        "Do not emit candidates that are absent, historical-only, or unsupported by note text.",
    ]
    if adapter.metadata.dataset == "gan_2026":
        prompt_rules.append(
            "Gan temporal candidates are soft hints; preserve unknown versus "
            "no seizure frequency reference distinctions."
        )
    return DuringPromptSurface(
        primitive_id=adapter.primitive_id,
        core_fingerprint=fingerprint_payload(payload),
        reference_payload=payload,
        prompt_rules=prompt_rules,
    )


def _render_candidate_tool_during(
    adapter: InterleavingAdapter,
    position: Position,
    payload: CorePayload,
    kwargs: dict[str, Any],
) -> ToolDuringSurface:
    assert isinstance(payload, list)
    tool_name = f"list_{adapter.primitive_id.replace('.', '_')}"
    serialized = [
        {
            "raw_text": candidate.raw_text,
            "normalized_value": candidate.normalized_value,
            "benchmark_value": candidate.benchmark_value,
            "rule_name": candidate.rule_name,
            "caveats": candidate.caveats,
        }
        for candidate in payload
    ]
    return ToolDuringSurface(
        primitive_id=adapter.primitive_id,
        core_fingerprint=fingerprint_payload(payload),
        reference_payload=payload,
        tool_name=tool_name,
        tool_description=adapter.metadata.output_contract,
        execution_result=json.dumps(serialized, indent=2),
    )


def _render_normalization_post(
    adapter: InterleavingAdapter,
    position: Position,
    payload: CorePayload,
    kwargs: dict[str, Any],
) -> PostProcessorSurface:
    assert isinstance(payload, NormalizationResult)
    output = payload.benchmark_value if payload.benchmark_value is not None else payload.canonical_value
    return PostProcessorSurface(
        primitive_id=adapter.primitive_id,
        core_fingerprint=fingerprint_payload(payload),
        reference_payload=payload,
        input_value=payload.raw_value,
        output_value=output,
        prediction_affecting=True,
    )


def _render_normalization_eval_only(
    adapter: InterleavingAdapter,
    position: Position,
    payload: CorePayload,
    kwargs: dict[str, Any],
) -> EvalOnlySurface:
    assert isinstance(payload, NormalizationResult)
    diagnostic = payload.model_copy(
        update={"prediction_affecting": False, "scorer_only": True}
    )
    return EvalOnlySurface(
        primitive_id=adapter.primitive_id,
        core_fingerprint=fingerprint_payload(payload),
        reference_payload=diagnostic,
        diagnostic_payload=diagnostic,
        prediction_affecting=False,
    )


def _render_evidence_post(
    adapter: InterleavingAdapter,
    position: Position,
    payload: CorePayload,
    kwargs: dict[str, Any],
) -> PostProcessorSurface:
    assert isinstance(payload, EvidenceSupportResult)
    return PostProcessorSurface(
        primitive_id=adapter.primitive_id,
        core_fingerprint=fingerprint_payload(payload),
        reference_payload=payload,
        input_value=kwargs.get("label"),
        output_value=payload.normalized_value,
        prediction_affecting=True,
        support_status=payload.support_status,
    )


def _render_evidence_eval_only(
    adapter: InterleavingAdapter,
    position: Position,
    payload: CorePayload,
    kwargs: dict[str, Any],
) -> EvalOnlySurface:
    assert isinstance(payload, EvidenceSupportResult)
    return EvalOnlySurface(
        primitive_id=adapter.primitive_id,
        core_fingerprint=fingerprint_payload(payload),
        reference_payload=payload,
        diagnostic_payload=payload,
        prediction_affecting=False,
    )


_CANDIDATE_RENDERERS: dict[InterleavingPositionValue, RenderFn] = {
    "pre": _render_candidate_pre,
    "during": _render_candidate_during,
    "tool_during": _render_candidate_tool_during,
}

_NORMALIZATION_POST_EVAL_RENDERERS: dict[InterleavingPositionValue, RenderFn] = {
    "post": _render_normalization_post,
    "eval_only": _render_normalization_eval_only,
}

_EVIDENCE_POST_EVAL_RENDERERS: dict[InterleavingPositionValue, RenderFn] = {
    "post": _render_evidence_post,
    "eval_only": _render_evidence_eval_only,
}


class InterleavingAdapter:
    """Expose one primitive at a taxonomy interleaving position."""

    def __init__(self, metadata: PrimitiveMetadata, binding: PrimitiveBinding) -> None:
        self.metadata = metadata
        self._binding = binding

    @property
    def primitive_id(self) -> str:
        return self.metadata.primitive_id

    @property
    def native_positions(self) -> list[InterleavingPositionValue]:
        return list(self.metadata.interleaving_positions)

    def supported_positions(self) -> list[InterleavingPositionValue]:
        return sorted(self._binding.renderers.keys())

    def render(self, position: InterleavingPositionValue, **kwargs: Any) -> SurfaceValue:
        renderer = self._binding.renderers.get(position)
        if renderer is None:
            raise ValueError(
                f"Primitive {self.primitive_id} does not support interleaving position "
                f"'{position}'."
            )
        payload = self._binding.invoke(position=position, **kwargs)
        surface = renderer(self, position, payload, kwargs)
        if surface.core_fingerprint != fingerprint_payload(payload):
            raise ValueError(
                f"Renderer for {self.primitive_id} at '{position}' changed core payload fingerprint."
            )
        return surface


def _invoke_gan_temporal_candidates(*, position: Position, note_text: str) -> list[PrimitiveCandidate]:
    del position
    return build_gan_frequency_candidate_payloads(note_text)


def _invoke_exect_medication_candidates(*, position: Position, note_text: str) -> list[PrimitiveCandidate]:
    del position
    return build_exect_medication_candidate_payloads(note_text)


def _invoke_exect_medication_bridge(
    *,
    position: Position,
    raw_value: str,
    note_text: str = "",
    evidence_text: str | None = None,
) -> NormalizationResult:
    return exect_medication_benchmark_bridge(
        raw_value,
        note_text=note_text,
        evidence_text=evidence_text,
        prediction_affecting=position == "post",
    )


def _invoke_gan_label_policy_bridge(*, position: Position, label: str) -> NormalizationResult:
    return gan_frequency_label_policy_bridge(
        label,
        prediction_affecting=position == "post",
    )


def _invoke_gan_evidence_guard(
    *,
    position: Position,
    note_text: str,
    evidence_text: str | None,
    label: str,
) -> EvidenceSupportResult:
    del position
    return check_gan_frequency_evidence_guard(
        note_text=note_text,
        evidence_text=evidence_text,
        label=label,
    )


PRIMITIVE_BINDINGS: dict[str, PrimitiveBinding] = {
    "gan.frequency.temporal_candidates.v1": PrimitiveBinding(
        primitive_id="gan.frequency.temporal_candidates.v1",
        invoke=_invoke_gan_temporal_candidates,
        renderers=_CANDIDATE_RENDERERS,
    ),
    "exect.medication.rx_candidates.v1": PrimitiveBinding(
        primitive_id="exect.medication.rx_candidates.v1",
        invoke=_invoke_exect_medication_candidates,
        renderers=_CANDIDATE_RENDERERS,
    ),
    "exect.medication.benchmark_bridge.v1": PrimitiveBinding(
        primitive_id="exect.medication.benchmark_bridge.v1",
        invoke=_invoke_exect_medication_bridge,
        renderers=_NORMALIZATION_POST_EVAL_RENDERERS,
    ),
    "gan.frequency.label_policy_bridge.v1": PrimitiveBinding(
        primitive_id="gan.frequency.label_policy_bridge.v1",
        invoke=_invoke_gan_label_policy_bridge,
        renderers=_NORMALIZATION_POST_EVAL_RENDERERS,
    ),
    "gan.frequency.evidence_guard.v1": PrimitiveBinding(
        primitive_id="gan.frequency.evidence_guard.v1",
        invoke=_invoke_gan_evidence_guard,
        renderers=_EVIDENCE_POST_EVAL_RENDERERS,
    ),
}


def get_interleaving_adapter(primitive_id: str) -> InterleavingAdapter:
    registry = primitive_registry_by_id()
    if primitive_id not in registry:
        raise KeyError(f"Unknown primitive_id: {primitive_id}")
    binding = PRIMITIVE_BINDINGS.get(primitive_id)
    if binding is None:
        raise KeyError(f"Primitive {primitive_id} has no interleaving binding.")
    return InterleavingAdapter(registry[primitive_id], binding)


def list_interleaving_adapters() -> list[InterleavingAdapter]:
    return [get_interleaving_adapter(primitive_id) for primitive_id in sorted(PRIMITIVE_BINDINGS)]
