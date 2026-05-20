"""Gan-specific taxonomy primitive helpers.

These functions adapt the existing Gan frequency utilities into the shared
primitive contracts used by taxonomy-governed experiments.
"""

from __future__ import annotations

from clinical_extraction.gan.frequency import (
    label_to_monthly_frequency,
    normalize_label,
    pragmatic_category,
    purist_category,
)
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates_from_note,
)
from clinical_extraction.primitives import (
    EvidenceSupportResult,
    NormalizationResult,
    PrimitiveCandidate,
    check_evidence_support,
)
from clinical_extraction.schemas import NormalizedValue

GAN_TEMPORAL_CANDIDATE_PRIMITIVE_ID = "gan.frequency.temporal_candidates.v1"
GAN_LABEL_POLICY_BRIDGE_PRIMITIVE_ID = "gan.frequency.label_policy_bridge.v1"
GAN_EVIDENCE_GUARD_PRIMITIVE_ID = "gan.frequency.evidence_guard.v1"


def build_gan_frequency_candidate_payloads(note_text: str) -> list[PrimitiveCandidate]:
    """Return Gan temporal candidates using the shared primitive payload contract."""

    candidates = []
    for candidate in build_temporal_frequency_candidates_from_note(note_text):
        start = note_text.find(candidate.evidence_text)
        end = start + len(candidate.evidence_text) if start >= 0 else None
        bridge = gan_frequency_label_policy_bridge(candidate.canonical_label)
        candidates.append(
            PrimitiveCandidate(
                primitive_id=GAN_TEMPORAL_CANDIDATE_PRIMITIVE_ID,
                dataset="gan_2026",
                field_family="frequency",
                raw_text=candidate.evidence_text,
                normalized_value=bridge.canonical_value,
                benchmark_value=bridge.benchmark_value,
                source_span_text=candidate.evidence_text,
                start=start if start >= 0 else None,
                end=end,
                rule_name=_rule_name_from_derivation(candidate.derivation),
                confidence=1.0,
                caveats=[
                    "Gan temporal candidates are soft hints, not gold-label replacements.",
                    (
                        "Monthly normalization is Gan-specific and must not be "
                        "reused for ExECT S4 frequency."
                    ),
                ],
                metadata={
                    "canonical_label": candidate.canonical_label,
                    "event_count": candidate.event_count,
                    "window_count": candidate.window_count,
                    "window_unit": candidate.window_unit,
                    "derivation": candidate.derivation,
                    "current_window_policy": "explicit_or_derived_observation_window",
                    **bridge.metadata,
                },
            )
        )
    return candidates


def gan_frequency_label_policy_bridge(
    label: str,
    *,
    prediction_affecting: bool = False,
) -> NormalizationResult:
    """Normalize a Gan label while preserving benchmark-facing label policy.

    By default this is scorer-only: it documents how a label maps to monthly
    frequency and Purist/Pragmatic categories without changing the prediction.
    """

    canonical = normalize_label(label)
    label_policy_class = _label_policy_class(canonical)
    clinical_caveats = _label_policy_caveats(raw_label=label, canonical_label=canonical)

    return NormalizationResult(
        primitive_id=GAN_LABEL_POLICY_BRIDGE_PRIMITIVE_ID,
        dataset="gan_2026",
        field_family="frequency",
        raw_value=label,
        canonical_value=canonical,
        benchmark_value=canonical,
        clinical_caveat=" ".join(clinical_caveats) if clinical_caveats else None,
        transformation_rule="gan_label_policy_normalization",
        prediction_affecting=prediction_affecting,
        scorer_only=not prediction_affecting,
        metadata={
            "label_policy_class": label_policy_class,
            "monthly_frequency": label_to_monthly_frequency(canonical),
            "purist_category": purist_category(canonical),
            "pragmatic_category": pragmatic_category(canonical),
            "current_window_policy": _current_window_policy(canonical),
        },
    )


def check_gan_frequency_evidence_guard(
    *,
    note_text: str,
    evidence_text: str | None,
    label: str,
) -> EvidenceSupportResult:
    """Check Gan evidence support without collapsing label-policy distinctions."""

    canonical = normalize_label(label)
    if evidence_text and "..." in evidence_text:
        return _check_elided_evidence(
            note_text=note_text,
            evidence_text=evidence_text,
            label=canonical,
        )

    result = check_evidence_support(
        document_text=note_text,
        quote=evidence_text,
        normalized_value=canonical,
        primitive_id=GAN_EVIDENCE_GUARD_PRIMITIVE_ID,
    )
    if result.support_status != "no_reference":
        return result

    caveats = list(result.caveats)
    if canonical == "no seizure frequency reference":
        caveats.append("Gan no-reference label")
        caveats.append(
            "Gan no-reference label means no seizure-frequency reference was found."
        )
    elif canonical == "unknown" or canonical.startswith("unknown,"):
        caveats.append("Gan unknown label still implies seizure-frequency context")
        caveats.append(
            "Gan unknown label still implies seizure-frequency context with unclear "
            "frequency."
        )

    return EvidenceSupportResult(
        primitive_id=result.primitive_id,
        document_text=result.document_text,
        quote=result.quote,
        normalized_value=result.normalized_value,
        interpretation_evidence_text=result.interpretation_evidence_text,
        support_status=result.support_status,
        raw_quote_supported=result.raw_quote_supported,
        normalized_interpretation_supported=result.normalized_interpretation_supported,
        start=result.start,
        end=result.end,
        caveats=caveats,
    )


def _check_elided_evidence(
    *,
    note_text: str,
    evidence_text: str,
    label: NormalizedValue,
) -> EvidenceSupportResult:
    parts = [part.strip() for part in evidence_text.split("...") if part.strip()]
    if not parts:
        return check_evidence_support(
            document_text=note_text,
            quote=evidence_text,
            normalized_value=label,
            primitive_id=GAN_EVIDENCE_GUARD_PRIMITIVE_ID,
        )

    cursor = 0
    ranges: list[tuple[int, int]] = []
    for part in parts:
        start = note_text.find(part, cursor)
        if start < 0:
            return EvidenceSupportResult(
                primitive_id=GAN_EVIDENCE_GUARD_PRIMITIVE_ID,
                document_text=note_text,
                quote=evidence_text,
                normalized_value=label,
                support_status="unsupported_quote",
                caveats=["Gan multi-span elided evidence part was not found in order."],
            )
        end = start + len(part)
        ranges.append((start, end))
        cursor = end

    first_start, first_end = ranges[0]
    return EvidenceSupportResult(
        primitive_id=GAN_EVIDENCE_GUARD_PRIMITIVE_ID,
        document_text=note_text,
        quote=evidence_text,
        normalized_value=label,
        interpretation_evidence_text=parts[0],
        support_status="normalized_interpretation",
        normalized_interpretation_supported=True,
        start=first_start,
        end=first_end,
        caveats=[
            "multi-span elided evidence",
            (
                "Gan multi-span elided evidence is supported by ordered note "
                "fragments, not one exact quote."
            ),
            (
                "Use this as an evidence guard caveat, not as proof of normalized "
                "frequency correctness."
            ),
        ],
    )


def _label_policy_class(canonical_label: str) -> str:
    if canonical_label == "unknown" or canonical_label.startswith("unknown,"):
        return "unknown_frequency"
    if canonical_label == "no seizure frequency reference":
        return "no_frequency_reference"
    if canonical_label.startswith("seizure free for "):
        return "seizure_free"
    if "cluster per" in canonical_label:
        return "cluster_rate"
    return "explicit_rate"


def _current_window_policy(canonical_label: str) -> str:
    if canonical_label in {"unknown", "no seizure frequency reference"}:
        return "not_applicable"
    if canonical_label.startswith("unknown,"):
        return "cluster_spacing_unknown"
    if canonical_label.startswith("seizure free for "):
        return "seizure_free_duration_maps_to_no_current_seizures"
    return "explicit_or_derived_observation_window"


def _label_policy_caveats(*, raw_label: str, canonical_label: str) -> list[str]:
    caveats: list[str] = []
    if raw_label != canonical_label:
        caveats.append("Surface normalized before Gan benchmark conversion.")
    if any(unit in raw_label.lower() for unit in ["months", "years", "weeks", "days"]):
        caveats.append("Plural units are normalized to the Gan singular label surface.")
    if canonical_label == "unknown":
        caveats.append("Unknown means seizures are referenced but frequency is unclear.")
    if canonical_label == "no seizure frequency reference":
        caveats.append("No-reference is distinct from unknown and maps to x=0.")
    return caveats


def _rule_name_from_derivation(derivation: str) -> str:
    return "_".join(token for token in derivation.lower().split() if token.isalnum())[
        :80
    ]
