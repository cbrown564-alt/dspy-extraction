"""ExECT S5 operational stack boundaries.

This module keeps the current S5 operational stack inspectable without changing
S4 scorer, loader, or family-program semantics.
"""
from __future__ import annotations

from collections.abc import Callable

import dspy

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
)
from clinical_extraction.exect.frequency_payload import (
    build_exect_frequency_pre_vocab_labels as build_precomputed_seizure_frequency_candidates,
    repair_exect_frequency_surface as _repair_s5_seizure_frequency_surface,
)
from clinical_extraction.exect.medication_primitives import (
    recover_exect_annotated_medication_non_asm_brand_alias_guard,
)
from clinical_extraction.exect.s0_s1.constants import EXECT_DATASET
from clinical_extraction.exect.s0_s1.prediction_artifacts import (
    _as_list,
    _augment_current_prescription_medications,
    _augment_diagnosis_co_lists,
    _evidence_at,
    _filter_diagnosis_for_seizure_descriptor_header,
    _normalize_diagnoses,
    _seizure_type_values_for_record,
    _values_for_family,
)
from clinical_extraction.programs.exect_s2 import (
    _normalize_investigation_surface,
    _recover_s2_investigation_raw_values,
    _recover_s2_seizure_raw_values,
    _s2_values_for_family,
    ladder_investigation_guard_bridge_tiers,
)
from clinical_extraction.programs.exect_s3 import _recover_s3_investigation_raw_values
from clinical_extraction.schemas import (
    DocumentPrediction,
    ExectGoldDocument,
    ExtractedValue,
)

EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT = (
    "exect_s5_am_guard_non_asm_brand_alias_v1"
)
EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT = (
    "exect_s5_frequency_pre_vocab_am_guard_non_asm_brand_alias_v1"
)
EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT = (
    "exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1"
)
EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT = (
    "exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2"
)
EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT = (
    "exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b"
)
EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT = (
    "exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_v1"
)
EXECT_S5_CORE_FIELD_FAMILIES = (
    "diagnosis",
    "seizure_type",
    "annotated_medication",
    "investigation",
    "seizure_frequency",
)
EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT = (
    "exect_s5_core_field_family_parallel_v2b"
)
EXECT_S5_STAGE_GRAPH_BY_VARIANT = {
    EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT: "g2_s5_core_family_parallel",
}
EXECT_S5_ACTIVE_VARIANTS = frozenset(
    {
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
    }
)
EXECT_S5_ARCHIVE_VARIANTS = frozenset(
    {
        EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT,
    }
)

S5_ANNOTATED_MEDICATION_GUARD_VARIANTS = frozenset(
    {
        EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT,
    }
)
S5_FREQUENCY_PRE_VOCAB_VARIANTS = frozenset(
    {
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT,
    }
)
S5_FREQUENCY_VERIFIER_VARIANTS = frozenset(
    {
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT,
    }
)


def stage_graph_id_for_s5_program_variant(program_variant: str) -> str | None:
    return EXECT_S5_STAGE_GRAPH_BY_VARIANT.get(program_variant)


def is_exect_s5_annotated_medication_guard_variant(program_variant: str) -> bool:
    return program_variant in S5_ANNOTATED_MEDICATION_GUARD_VARIANTS


def is_exect_s5_frequency_pre_vocab_variant(program_variant: str) -> bool:
    return program_variant in S5_FREQUENCY_PRE_VOCAB_VARIANTS


def is_exect_s5_frequency_verifier_variant(program_variant: str) -> bool:
    return program_variant in S5_FREQUENCY_VERIFIER_VARIANTS


def exect_s5_annotated_medication_guard_id(program_variant: str) -> str | None:
    if not is_exect_s5_annotated_medication_guard_variant(program_variant):
        return None
    if program_variant == EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT:
        return "exect.medication.am_guard_temporal_evidence.v1"
    return "exect.medication.am_guard_non_asm_brand_alias.v1"


def exect_s5_frequency_verifier_policy_id(program_variant: str) -> str | None:
    if not is_exect_s5_frequency_verifier_variant(program_variant):
        return None
    return {
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT: (
            "exect.frequency.evidence_verify_policy.v2"
        ),
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT: (
            "exect.frequency.evidence_verify_policy.v2b"
        ),
        EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT: (
            "exect.frequency.evidence_verify_policy.v2b"
        ),
    }.get(program_variant, "exect.frequency.evidence_verify_policy.v1")


def build_exect_s5_stack_metadata(
    *,
    pred: dspy.Prediction,
    note_text: str,
    program_variant: str,
) -> dict[str, object]:
    metadata: dict[str, object] = {}
    if is_exect_s5_frequency_pre_vocab_variant(program_variant):
        metadata["precomputed_candidates"] = {
            "seizure_frequency": build_precomputed_seizure_frequency_candidates(
                note_text
            )
        }
    guard_id = exect_s5_annotated_medication_guard_id(program_variant)
    if guard_id is not None:
        metadata["post_guard"] = {"annotated_medication": guard_id}
    policy_id = exect_s5_frequency_verifier_policy_id(program_variant)
    if policy_id is not None:
        metadata["frequency_verifier"] = {
            "primitive_id": policy_id,
            "policy": "reject_only",
            "flags": _as_list(getattr(pred, "frequency_verifier_flags", [])),
            "decision": getattr(pred, "frequency_verifier_decision", None),
            "reason": getattr(pred, "frequency_verifier_reason", None),
        }
    return metadata


def apply_exect_s5_annotated_medication_guard(
    *,
    values: list[ExtractedValue],
    pred: dspy.Prediction,
    record: ExectGoldDocument,
    program_variant: str,
) -> list[ExtractedValue]:
    """Apply the S5 annotated-medication bridge as an explicit stack component."""
    if not is_exect_s5_annotated_medication_guard_variant(program_variant):
        return values

    non_medication_values = [
        value for value in values if value.field_name != "annotated_medication"
    ]
    guarded_values = _guarded_annotated_medication_values(
        pred=pred,
        record=record,
        program_variant=program_variant,
    )
    return [*non_medication_values, *guarded_values]


def _guarded_annotated_medication_values(
    *,
    pred: dspy.Prediction,
    record: ExectGoldDocument,
    program_variant: str,
) -> list[ExtractedValue]:
    pred_meds = _as_list(getattr(pred, "annotated_medication", []))
    pred_evidence = _as_list(getattr(pred, "annotated_medication_evidence", []))
    medication_raw, medication_evidence, medication_augmented = (
        _augment_current_prescription_medications(
            pred_meds,
            pred_evidence,
            record.text,
        )
    )

    if program_variant == EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT:
        from clinical_extraction.exect.medication_primitives import (
            recover_exect_annotated_medication_temporal_evidence_guard,
        )

        guarded_meds, guard_flags = recover_exect_annotated_medication_temporal_evidence_guard(
            medication_raw,
            medication_evidence,
            record.text,
        )
    else:
        guarded_meds, guard_flags = recover_exect_annotated_medication_non_asm_brand_alias_guard(
            medication_raw,
            medication_evidence,
            record.text,
        )

    guarded_values: list[ExtractedValue] = []
    for med in guarded_meds:
        canon_med = canonical_medication_name(med)
        orig_raw = med
        orig_evidence = ""
        is_augmented = False

        for idx, raw_val in enumerate(medication_raw):
            clean_raw = raw_val.strip().lower()
            if clean_raw in {"eplim", "eplim chrono", "epilim", "epilim chrono"}:
                clean_raw = "epilim chrono"
            if canonical_medication_name(clean_raw) == canon_med:
                orig_raw = raw_val
                orig_evidence = medication_evidence[idx] if idx < len(medication_evidence) else ""
                if raw_val in medication_augmented:
                    is_augmented = True
                break

        guarded_values.extend(
            _values_for_family(
                record=record,
                field_name="annotated_medication",
                raw_values=[orig_raw],
                evidence_values=[orig_evidence],
                fixed_normalized=med,
                fixed_bridge_flags=guard_flags,
                augmented_values={orig_raw} if is_augmented else set(),
            )
        )
    return guarded_values


def build_exect_s5_core_parallel_field_values(
    pred: dspy.Prediction,
    record: ExectGoldDocument,
    *,
    program_variant: str,
    recover_investigation_raw_values: Callable[
        [list[str], str], tuple[list[str], list[str]]
    ],
    recover_frequency_values: Callable[..., tuple[list[str], list[str]]],
) -> list[ExtractedValue]:
    values: list[ExtractedValue] = []

    diagnosis_inputs = _as_list(getattr(pred, "diagnosis", []))
    diagnosis_inputs, diagnosis_header_flags = _filter_diagnosis_for_seizure_descriptor_header(
        diagnosis_inputs,
        record.text,
    )
    diagnosis_raw, diagnosis_augmented, specificity_collapse_augmented = (
        _augment_diagnosis_co_lists(diagnosis_inputs, record.text)
    )
    diagnoses, collapsed = _normalize_diagnoses(diagnosis_raw)
    values.extend(
        _values_for_family(
            record=record,
            field_name="diagnosis",
            raw_values=diagnoses,
            evidence_values=_as_list(getattr(pred, "diagnosis_evidence", [])),
            collapsed_values=collapsed,
            augmented_values=diagnosis_augmented,
            specificity_collapse_augmented=specificity_collapse_augmented,
            extra_quality_flags=diagnosis_header_flags,
        )
    )

    seizure_raw, _ = _recover_s2_seizure_raw_values(
        _as_list(getattr(pred, "seizure_type", [])),
        record.text,
    )
    values.extend(
        _seizure_type_values_for_record(
            record=record,
            raw_values=seizure_raw,
            evidence_values=_as_list(getattr(pred, "seizure_type_evidence", [])),
        )
    )

    values.extend(
        _guarded_annotated_medication_values(
            pred=pred,
            record=record,
            program_variant=program_variant,
        )
    )

    investigation_raw, _ = _recover_s2_investigation_raw_values(
        _as_list(getattr(pred, "investigation", [])),
        record.text,
        bridge_tiers=ladder_investigation_guard_bridge_tiers(),
    )
    investigation_raw, _ = _recover_s3_investigation_raw_values(
        investigation_raw,
        record.text,
    )
    investigation_raw, _ = recover_investigation_raw_values(
        investigation_raw,
        record.text,
    )
    values.extend(
        _s2_values_for_family(
            record=record,
            field_name="investigation",
            raw_values=investigation_raw,
            evidence_values=_as_list(getattr(pred, "investigation_evidence", [])),
            normalize=_normalize_investigation_surface,
        )
    )

    frequency_raw, _ = recover_frequency_values(
        _as_list(getattr(pred, "seizure_frequency", [])),
        record.text,
        program_variant=program_variant,
    )
    values.extend(
        _s2_values_for_family(
            record=record,
            field_name="seizure_frequency",
            raw_values=frequency_raw,
            evidence_values=_as_list(getattr(pred, "seizure_frequency_evidence", [])),
            normalize=canonical_clinical_phrase,
        )
    )
    return values


def build_exect_s5_core_parallel_prediction(
    module: dspy.Module,
    record: ExectGoldDocument,
    *,
    program_variant: str,
    schema_level: str,
    recover_investigation_raw_values: Callable[
        [list[str], str], tuple[list[str], list[str]]
    ],
    recover_frequency_values: Callable[..., tuple[list[str], list[str]]],
) -> DocumentPrediction:
    pred = module(note_text=record.text)
    values = build_exect_s5_core_parallel_field_values(
        pred,
        record,
        program_variant=program_variant,
        recover_investigation_raw_values=recover_investigation_raw_values,
        recover_frequency_values=recover_frequency_values,
    )
    metadata: dict[str, object] = {
        "program_variant": program_variant,
        "stage_graph_id": stage_graph_id_for_s5_program_variant(program_variant),
    }
    metadata.update(
        build_exect_s5_stack_metadata(
            pred=pred,
            note_text=record.text,
            program_variant=program_variant,
        )
    )
    return DocumentPrediction(
        document_id=record.document_id,
        dataset=EXECT_DATASET,
        schema_level=schema_level,
        values=values,
        quality_flags=record.quality_flags,
        metadata=metadata,
    )


def verified_frequency_allowed_keys(raw_values: list[str]) -> set[str]:
    allowed: set[str] = set()
    for raw in raw_values:
        canonical = canonical_clinical_phrase(raw)
        if not canonical:
            continue
        repaired, _ = _repair_s5_seizure_frequency_surface(canonical)
        allowed.add(repaired)
    return allowed


def apply_exect_s5_frequency_verifier_guards(
    *,
    note_text: str,
    initial_frequency: list[str],
    verified: dspy.Prediction,
    strict_qualitative: bool = False,
) -> dspy.Prediction:
    """Apply reject-only frequency verifier guards without changing scorer policy."""
    initial_keys = verified_frequency_allowed_keys(initial_frequency)
    verified_frequency = _as_list(getattr(verified, "seizure_frequency", []))
    verified_evidence = _as_list(getattr(verified, "seizure_frequency_evidence", []))
    frequency: list[str] = []
    frequency_evidence: list[str] = []
    flags: list[str] = []

    for index, raw_value in enumerate(verified_frequency):
        normalized = canonical_clinical_phrase(raw_value)
        repaired, _ = _repair_s5_seizure_frequency_surface(normalized)
        if not repaired or repaired not in initial_keys:
            flags.append("verifier_added_label_blocked")
            continue

        evidence_text = _evidence_at(verified_evidence, index) or ""
        if not evidence_text:
            flags.append("missing_evidence")
            continue
        if _evidence_looks_like_frequency_candidate_block(evidence_text):
            flags.append("candidate_block_echo")
            continue
        evidence_lower = evidence_text.lower()
        note_lower = note_text.lower()
        if evidence_lower not in note_lower:
            flags.append("evidence_not_in_note")
            continue
        idx = note_lower.find(evidence_lower)
        evidence_text = note_text[idx : idx + len(evidence_text)]
        if _frequency_change_from_medication_control(raw_value, evidence_text):
            flags.append("medication_control_not_frequency_change")
            continue
        if strict_qualitative and not qualitative_label_supported_by_evidence(
            raw_value, evidence_text
        ):
            flags.append("qualitative_without_note_support")
            continue

        frequency.append(raw_value.strip())
        frequency_evidence.append(evidence_text)

    return dspy.Prediction(
        seizure_frequency=frequency,
        seizure_frequency_evidence=frequency_evidence,
        verifier_decision=getattr(verified, "verifier_decision", "repair"),
        verifier_reason=getattr(verified, "verifier_reason", ""),
        frequency_verifier_flags=flags,
    )


def _evidence_looks_like_frequency_candidate_block(evidence_text: str) -> bool:
    lower = evidence_text.lower()
    return (
        "precomputed benchmark-facing candidates" in lower
        or lower.startswith("seizure_frequency:")
    )


def _frequency_change_from_medication_control(raw_value: str, evidence_text: str) -> bool:
    label = canonical_clinical_phrase(raw_value)
    if label not in {"frequency increased", "frequency decreased"}:
        return False
    evidence = evidence_text.lower()
    medication_markers = (
        "lamotrigine",
        "levetiracetam",
        "carbamazepine",
        "valproate",
        "medication",
        "dose",
        "treatment",
    )
    control_markers = ("control", "controlled")
    seizure_frequency_markers = ("frequency", "seizure frequency", "seizures per")
    return (
        any(marker in evidence for marker in medication_markers)
        and any(marker in evidence for marker in control_markers)
        and not any(marker in evidence for marker in seizure_frequency_markers)
    )


_QUALITATIVE_FREQUENCY_LABELS = frozenset(
    {"infrequent", "frequency same", "frequency increased", "frequency decreased"}
)
_QUALITATIVE_NOTE_MARKERS: dict[str, tuple[str, ...]] = {
    "infrequent": ("infrequent", "rarely", "occasional", "occasionally", "rare"),
    "frequency same": (
        "same frequency",
        "unchanged",
        "frequency remains",
        "stable frequency",
        "frequency is the same",
    ),
    "frequency increased": (
        "frequency increased",
        "increased frequency",
        "more frequent",
        "more often",
        "worsening",
        "worse frequency",
        "having more",
        "more generalised",
        "more generalized",
    ),
    "frequency decreased": (
        "frequency decreased",
        "decreased frequency",
        "less frequent",
        "less often",
        "improved",
        "fewer seizures",
    ),
}


def qualitative_label_supported_by_evidence(raw_value: str, evidence_text: str) -> bool:
    label = canonical_clinical_phrase(raw_value)
    if label not in _QUALITATIVE_FREQUENCY_LABELS:
        return True
    evidence = evidence_text.lower()
    return any(marker in evidence for marker in _QUALITATIVE_NOTE_MARKERS.get(label, ()))
