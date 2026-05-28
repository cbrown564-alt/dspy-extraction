"""Prediction artifact assembly and deterministic S1 bridge helpers."""
from __future__ import annotations

import re
from collections.abc import Callable
from typing import Optional

import dspy

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
    collapse_diagnoses_to_most_specific,
)
from clinical_extraction.exect.medication_primitives import (
    recover_exect_annotated_medication_non_asm_brand_alias_guard,
)
from clinical_extraction.exect.s0_s1.constants import (
    ALLOWED_DIAGNOSIS_LABELS,
    EXECT_DATASET,
    EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT,
    EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT,
    EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
    EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_VARIANT,
    EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
    REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY,
    REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES,
    _CURRENT_PRESCRIPTION_LINE_RE,
    _DIAGNOSIS_HEADER_RE,
    _DISSOCIATIVE_EPILEPTIC_FOCAL_SEIZURE_LABELS,
    _EPILEPTIC_SEIZURES_LABEL,
    _GENERIC_EPILEPSY_CO_LIST_TRIGGERS,
    _GRANULAR_SEIZURE_TYPE_COARSENING,
    _JME_COARSE_SEIZURE_LABELS,
    _JME_MYCLONIC_SEIZURE_LABELS,
    _KNOWN_PRESCRIPTION_MEDICATIONS,
    _MEDICATION_BRAND_NOTE_SURFACES,
    _MEDICATION_EVIDENCE_EXCLUSION_PHRASES,
    _MEDICATION_EVIDENCE_PREFIXES,
    _MEDICATION_PLANNED_OR_HISTORICAL_EVIDENCE_PHRASES,
    _MEDICATION_SURFACE_REPAIRS,
    _ON_AWAKENING_SYNDROME_DIAGNOSIS,
    _ON_AWAKENING_SYNDROME_NOTE_RE,
    _REJECTED_ANNOTATED_MEDICATIONS,
    _REJECTED_GRANULAR_SEIZURE_TYPES,
    _SECONDARY_COLLAPSED_SEIZURE_TOKEN,
    _SECONDARY_GENERALISED_SEIZURE_LABELS,
    _SECONDARY_GENERALISED_SEIZURE_NOTE_RE,
    _SPECIFICITY_COLLAPSE_DIAGNOSIS_TOKENS,
    _SPECIFICITY_COLLAPSE_TRIGGER_DIAGNOSES,
)
from clinical_extraction.exect.s0_s1.prompt_routing import (
    build_precomputed_family_candidates,
    build_precomputed_medication_candidates,
    build_precomputed_seizure_type_candidates,
    extract_d1_field_family_surfaces,
)
from clinical_extraction.exect.s1_boundary import build_s1_boundary_surfaces_metadata
from clinical_extraction.pipeline.sectioning import select_context
from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExectGoldDocument,
    ExtractedValue,
    PredictionSet,
)

def _apply_exect_verifier_guards(
    *,
    note_text: str,
    initial_diagnosis: list[str],
    initial_seizure_type: list[str],
    initial_annotated_medication: list[str],
    verified: dspy.Prediction,
) -> dspy.Prediction:
    """Deterministic confirm-first guards for ExECT verify-repair."""
    initial_diagnosis_keys = {
        canonical_clinical_phrase(value)
        for value in initial_diagnosis
        if value.strip()
    }
    diagnosis = []
    diagnosis_evidence = []
    for index, raw_value in enumerate(_as_list(getattr(verified, "diagnosis", []))):
        normalized = canonical_clinical_phrase(raw_value)
        if not normalized or normalized not in initial_diagnosis_keys:
            continue
        diagnosis.append(raw_value.strip())
        diagnosis_evidence.append(
            _evidence_at(_as_list(getattr(verified, "diagnosis_evidence", [])), index) or ""
        )

    initial_seizure_keys = {
        canonical_clinical_phrase(value) for value in initial_seizure_type if value.strip()
    }
    seizure_type = []
    seizure_type_evidence = []
    for index, raw_value in enumerate(_as_list(getattr(verified, "seizure_type", []))):
        normalized = canonical_clinical_phrase(raw_value)
        if normalized in _REJECTED_GRANULAR_SEIZURE_TYPES:
            continue
        if normalized and not _verified_seizure_allowed(normalized, initial_seizure_keys):
            continue
        seizure_type.append(raw_value.strip())
        seizure_type_evidence.append(
            _evidence_at(_as_list(getattr(verified, "seizure_type_evidence", [])), index) or ""
        )

    initial_medication_keys = {
        canonical_medication_name(value)
        for value in initial_annotated_medication
        if value.strip()
    }
    medication = []
    medication_evidence = []
    verified_medication = _as_list(getattr(verified, "annotated_medication", []))
    verified_medication_evidence = _as_list(
        getattr(verified, "annotated_medication_evidence", [])
    )
    for index, raw_value in enumerate(verified_medication):
        evidence_text = _evidence_at(verified_medication_evidence, index)
        if evidence_text and evidence_text not in note_text:
            continue
        if _medication_evidence_excluded(evidence_text):
            continue
        normalized = canonical_medication_name(raw_value)
        repaired = _MEDICATION_SURFACE_REPAIRS.get(normalized, normalized)
        if repaired in _REJECTED_ANNOTATED_MEDICATIONS:
            continue
        if repaired and repaired not in initial_medication_keys:
            continue
        if repaired:
            medication.append(raw_value.strip())
            medication_evidence.append(evidence_text or "")

    return dspy.Prediction(
        diagnosis=diagnosis,
        diagnosis_evidence=diagnosis_evidence,
        seizure_type=seizure_type,
        seizure_type_evidence=seizure_type_evidence,
        annotated_medication=medication,
        annotated_medication_evidence=medication_evidence,
        verifier_decision=getattr(verified, "verifier_decision", "repair"),
        verifier_reason=getattr(verified, "verifier_reason", ""),
    )


def _merge_diagnosis_recall(
    *,
    initial_diagnosis: list[str],
    initial_diagnosis_evidence: list[str],
    additional_diagnosis: list[str],
    additional_diagnosis_evidence: list[str],
) -> tuple[list[str], list[str], list[str]]:
    """Merge add-only recalled diagnoses with deterministic guards."""
    merged_diagnosis = list(initial_diagnosis)
    merged_evidence = _align_evidence(initial_diagnosis, initial_diagnosis_evidence)
    seen = {
        canonical_clinical_phrase(value)
        for value in initial_diagnosis
        if value.strip()
    }
    recall_added: list[str] = []

    for index, raw_value in enumerate(additional_diagnosis):
        if not raw_value.strip():
            continue
        normalized = canonical_clinical_phrase(raw_value)
        normalized, _ = _normalize_diagnosis_surface(normalized)
        if not normalized or normalized in seen or normalized not in ALLOWED_DIAGNOSIS_LABELS:
            continue
        evidence_text = _evidence_at(additional_diagnosis_evidence, index)
        merged_diagnosis.append(raw_value.strip())
        merged_evidence.append(evidence_text or "")
        seen.add(normalized)
        recall_added.append(normalized)

    return merged_diagnosis, merged_evidence, recall_added


def merge_exect_s1_diagnosis_recall(
    *,
    initial_diagnosis: list[str],
    initial_diagnosis_evidence: list[str],
    additional_diagnosis: list[str],
    additional_diagnosis_evidence: list[str],
) -> tuple[list[str], list[str], list[str]]:
    """Public ExECT S1 diagnosis-recall merge stage surface."""

    return _merge_diagnosis_recall(
        initial_diagnosis=initial_diagnosis,
        initial_diagnosis_evidence=initial_diagnosis_evidence,
        additional_diagnosis=additional_diagnosis,
        additional_diagnosis_evidence=additional_diagnosis_evidence,
    )


def _align_evidence(values: list[str], evidence_values: list[str]) -> list[str]:
    aligned = list(evidence_values)
    while len(aligned) < len(values):
        aligned.append("")
    return aligned[: len(values)]


def predict_exect_records(
    module: dspy.Module,
    records: list[ExectGoldDocument],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    program_variant: str = EXECT_S0_S1_VARIANT,
    repair_policy: str = "none",
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> PredictionSet:
    """Run ``module`` on ExECT records and return a shared ``PredictionSet``."""
    predictions = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        predictions.append(
            _predict_record(
                module,
                record,
                prompt_version=prompt_version,
                program_variant=program_variant,
                repair_policy=repair_policy,
            )
        )
        if progress_callback is not None:
            progress_callback(index, total, record.document_id)
    return PredictionSet(
        dataset=EXECT_DATASET,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        predictions=predictions,
        metadata={
            "program_variant": program_variant,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "repair_policy": repair_policy,
            "scorer_mode": EXECT_S0_S1_SCORER,
        },
    )


def _s1_single_pass_variants() -> frozenset[str]:
    return frozenset(
        {
            EXECT_S0_S1_VARIANT,
            EXECT_S0_S1_PRE_VOCAB_VARIANT,
            EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
            EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
            EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
            EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT,
            EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT,
        }
    )


def _repair_policy_applies_benchmark_bridges(repair_policy: str) -> bool:
    """Return whether audited S1 benchmark bridges run after single-pass extraction."""
    return repair_policy != REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES


def _bridge_stage_for_repair_policy(repair_policy: str) -> str:
    if not _repair_policy_applies_benchmark_bridges(repair_policy):
        return "none"
    if repair_policy == REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY:
        return "post"
    return "inline"

def _predict_record(
    module: dspy.Module,
    record: ExectGoldDocument,
    *,
    prompt_version: str,
    program_variant: str,
    repair_policy: str = "none",
) -> DocumentPrediction:
    pred = module(note_text=record.text)

    if program_variant in _s1_single_pass_variants():
        apply_benchmark_bridges = _repair_policy_applies_benchmark_bridges(repair_policy)
        bridge_stage = _bridge_stage_for_repair_policy(repair_policy)
        values = _build_s1_field_family_values(
            record,
            pred,
            apply_benchmark_bridges=apply_benchmark_bridges,
            program_variant=program_variant,
        )
        metadata = {
            "program_variant": program_variant,
            "apply_benchmark_bridges": apply_benchmark_bridges,
            "bridge_stage": bridge_stage,
            "repair_policy": repair_policy,
            "s1_boundary_surfaces": build_s1_boundary_surfaces_metadata(
                pred=pred,
                values=values,
                prompt_version=prompt_version,
                program_variant=program_variant,
                repair_policy=repair_policy,
                apply_benchmark_bridges=apply_benchmark_bridges,
                bridge_stage=bridge_stage,
            ),
        }
        if program_variant == EXECT_S0_S1_PRE_VOCAB_VARIANT:
            metadata["precomputed_candidates"] = build_precomputed_family_candidates(
                record.text
            )
        if program_variant == EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT:
            metadata["precomputed_candidates"] = {
                "annotated_medication": build_precomputed_medication_candidates(
                    record.text
                )
            }
        if program_variant == EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT:
            metadata["precomputed_candidates"] = {
                "seizure_type": build_precomputed_seizure_type_candidates()
            }
        if program_variant == EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT:
            metadata["d1_surfaces"] = extract_d1_field_family_surfaces(record.text)
        return DocumentPrediction(
            document_id=record.document_id,
            dataset=EXECT_DATASET,
            schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
            values=values,
            quality_flags=record.quality_flags,
            metadata=metadata,
        )

    apply_benchmark_bridges = _repair_policy_applies_benchmark_bridges(repair_policy)
    bridge_stage = _bridge_stage_for_repair_policy(repair_policy)
    values: list[ExtractedValue] = []
    diagnosis_inputs = _as_list(getattr(pred, "diagnosis", []))
    diagnosis_raw = diagnosis_inputs
    diagnosis_augmented: set[str] = set()
    specificity_collapse_augmented: set[str] = set()
    diagnosis_header_flags: list[str] = []
    if apply_benchmark_bridges:
        diagnosis_inputs, diagnosis_header_flags = (
            _filter_diagnosis_for_seizure_descriptor_header(
                diagnosis_inputs,
                record.text,
            )
        )
        if program_variant == EXECT_S0_S1_VERIFY_REPAIR_VARIANT:
            diagnosis_raw = diagnosis_inputs
        else:
            diagnosis_raw, diagnosis_augmented, specificity_collapse_augmented = (
                _augment_diagnosis_co_lists(
                    diagnosis_inputs,
                    record.text,
                )
            )
    diagnoses, collapsed = _normalize_diagnoses(diagnosis_raw)
    diagnosis_evidence = _as_list(getattr(pred, "diagnosis_evidence", []))
    values.extend(
        _values_for_family(
            record=record,
            field_name="diagnosis",
            raw_values=diagnoses,
            evidence_values=diagnosis_evidence,
            collapsed_values=collapsed,
            augmented_values=diagnosis_augmented,
            specificity_collapse_augmented=specificity_collapse_augmented,
            extra_quality_flags=diagnosis_header_flags,
            apply_benchmark_bridges=apply_benchmark_bridges,
        )
    )
    values.extend(
        _values_for_family(
            record=record,
            field_name="seizure_type",
            raw_values=_as_list(getattr(pred, "seizure_type", [])),
            evidence_values=_as_list(getattr(pred, "seizure_type_evidence", [])),
            apply_benchmark_bridges=apply_benchmark_bridges,
        )
    )
    medication_raw = _as_list(getattr(pred, "annotated_medication", []))
    medication_evidence = _as_list(getattr(pred, "annotated_medication_evidence", []))
    values.extend(
        _values_for_family(
            record=record,
            field_name="annotated_medication",
            raw_values=medication_raw,
            evidence_values=medication_evidence,
            augmented_values=set(),
            apply_benchmark_bridges=apply_benchmark_bridges,
        )
    )

    return DocumentPrediction(
        document_id=record.document_id,
        dataset=EXECT_DATASET,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        values=values,
        quality_flags=record.quality_flags,
        metadata={
            "program_variant": program_variant,
            "apply_benchmark_bridges": apply_benchmark_bridges,
            "bridge_stage": bridge_stage,
            "repair_policy": repair_policy,
            "s1_boundary_surfaces": build_s1_boundary_surfaces_metadata(
                pred=pred,
                values=values,
                prompt_version=prompt_version,
                program_variant=program_variant,
                repair_policy=repair_policy,
                apply_benchmark_bridges=apply_benchmark_bridges,
                bridge_stage=bridge_stage,
            ),
        },
    )


def _build_s1_field_family_values(
    record: ExectGoldDocument,
    pred: dspy.Prediction,
    *,
    apply_benchmark_bridges: bool = True,
    program_variant: str = EXECT_S0_S1_VARIANT,
) -> list[ExtractedValue]:
    """Map a single-pass model prediction to scored S1 field-family values."""
    values: list[ExtractedValue] = []

    diagnosis_inputs = _as_list(getattr(pred, "diagnosis", []))
    diagnosis_header_flags: list[str] = []
    diagnosis_augmented: set[str] = set()
    specificity_collapse_augmented: set[str] = set()
    if apply_benchmark_bridges:
        diagnosis_inputs, diagnosis_header_flags = (
            _filter_diagnosis_for_seizure_descriptor_header(
                diagnosis_inputs,
                record.text,
            )
        )
        diagnosis_raw, diagnosis_augmented, specificity_collapse_augmented = (
            _augment_diagnosis_co_lists(
                diagnosis_inputs,
                record.text,
            )
        )
    else:
        diagnosis_raw = diagnosis_inputs

    diagnoses, collapsed = _normalize_diagnoses(diagnosis_raw)
    diagnosis_evidence = _as_list(getattr(pred, "diagnosis_evidence", []))
    values.extend(
        _values_for_family(
            record=record,
            field_name="diagnosis",
            raw_values=diagnoses,
            evidence_values=diagnosis_evidence,
            collapsed_values=collapsed,
            augmented_values=diagnosis_augmented,
            specificity_collapse_augmented=specificity_collapse_augmented,
            extra_quality_flags=diagnosis_header_flags,
            apply_benchmark_bridges=apply_benchmark_bridges,
        )
    )

    seizure_raw = _as_list(getattr(pred, "seizure_type", []))
    seizure_evidence = _as_list(getattr(pred, "seizure_type_evidence", []))
    if apply_benchmark_bridges:
        values.extend(
            _seizure_type_values_for_record(
                record=record,
                raw_values=seizure_raw,
                evidence_values=seizure_evidence,
            )
        )
    else:
        values.extend(
            _values_for_family(
                record=record,
                field_name="seizure_type",
                raw_values=seizure_raw,
                evidence_values=seizure_evidence,
                apply_benchmark_bridges=False,
            )
        )

    medication_raw = _as_list(getattr(pred, "annotated_medication", []))
    medication_evidence = _as_list(getattr(pred, "annotated_medication_evidence", []))
    medication_augmented: set[str] = set()
    if apply_benchmark_bridges:
        medication_raw, medication_evidence, medication_augmented = (
            _augment_current_prescription_medications(
                medication_raw,
                medication_evidence,
                record.text,
            )
        )
    medication_guard_flags: list[str] = []
    if apply_benchmark_bridges and program_variant in {
        EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT,
        EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT,
    }:
        medication_raw, medication_guard_flags = (
            _recover_s1_clean_annotated_medication_raw_values(
                medication_raw,
                medication_evidence,
                record.text,
            )
        )
    values.extend(
        _values_for_family(
            record=record,
            field_name="annotated_medication",
            raw_values=medication_raw,
            evidence_values=medication_evidence,
            augmented_values=medication_augmented,
            extra_quality_flags=medication_guard_flags,
            apply_benchmark_bridges=apply_benchmark_bridges,
        )
    )
    return values


def _recover_s1_clean_annotated_medication_raw_values(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Apply the promoted S5/S2 annotated-medication guard to S1 clean-ladder arms."""
    recovered, flags = recover_exect_annotated_medication_non_asm_brand_alias_guard(
        raw_values,
        evidence_values,
        note_text,
    )
    return recovered, [f"s1_clean_bridge:{flag}" for flag in flags]


def recover_exect_s1_clean_annotated_medication_raw_values(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Public ExECT S1 clean-ladder medication guard recovery surface."""

    return _recover_s1_clean_annotated_medication_raw_values(
        raw_values,
        evidence_values,
        note_text,
    )


def _family_context(note_text: str, *, target_field: str, max_sections: int) -> str:
    selected = select_context(
        note_text,
        target_field=target_field,
        max_sections=max_sections,
    )
    if not selected:
        return note_text

    formatted = []
    for span in selected:
        label = span.section or "document"
        formatted.append(f"Section: {label}\n{span.text.strip()}")
    return "\n\n".join(chunk for chunk in formatted if chunk.strip()) or note_text


def _augment_diagnosis_co_lists(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], set[str], set[str]]:
    """Add note-supported co-listed diagnoses that monolithic extraction often omits."""
    note_lower = note_text.lower()
    normalized = {
        canonical_clinical_phrase(value)
        for value in raw_values
        if value.strip()
    }
    additions: list[str] = []
    augmented: set[str] = set()

    def add(label: str) -> None:
        key = canonical_clinical_phrase(label)
        if key in normalized or key not in ALLOWED_DIAGNOSIS_LABELS:
            return
        additions.append(label)
        normalized.add(key)
        augmented.add(key)

    for trigger in _GENERIC_EPILEPSY_CO_LIST_TRIGGERS:
        if trigger in normalized and _note_has_standalone_epilepsy(note_lower):
            add("epilepsy")
            break

    if "epilepsy" not in normalized:
        header = _diagnosis_header_text(note_text)
        if header and _header_establishes_generic_epilepsy(header):
            add("epilepsy")

    if "focal epilepsy" in normalized and "focal onset epilepsy" not in normalized:
        if "focal onset epilepsy" in note_lower:
            add("focal onset epilepsy")

    if "focal onset epilepsy" in normalized and "focal epilepsy" not in normalized:
        if re.search(r"\bfocal epilepsy\b", note_lower):
            add("focal epilepsy")

    if "parietal lobe epilepsy" not in normalized and _note_supports_parietal_lobe_epilepsy(
        note_lower
    ):
        if normalized & {"focal epilepsy", "focal onset epilepsy"}:
            add("parietal lobe epilepsy")

    if _ON_AWAKENING_SYNDROME_DIAGNOSIS not in normalized and _note_supports_on_awakening_syndrome_diagnosis(
        note_lower
    ):
        add(_ON_AWAKENING_SYNDROME_DIAGNOSIS)

    collapse_additions, collapse_augmented = _augment_specificity_collapse_diagnosis_tokens(
        [*raw_values, *additions],
        note_text,
    )
    for label in collapse_additions:
        key = canonical_clinical_phrase(label)
        if key in normalized or key not in ALLOWED_DIAGNOSIS_LABELS:
            continue
        additions.append(label)
        normalized.add(key)

    return [*raw_values, *additions], augmented, collapse_augmented


def _diagnosis_header_text(note_text: str) -> str | None:
    match = _DIAGNOSIS_HEADER_RE.search(note_text)
    if not match:
        return None
    return match.group(1).strip().lower()


def _header_establishes_generic_epilepsy(header: str) -> bool:
    if re.search(r"\bunclassified epilepsy\b|\bepilepsy unclassified\b", header):
        return True
    if re.search(r"^epilepsy\b", header):
        return True
    return False


def _note_has_standalone_epilepsy(note_lower: str) -> bool:
    for match in re.finditer(r"\bepilepsy\b", note_lower):
        prefix = note_lower[max(0, match.start() - 30) : match.start()]
        if re.search(
            r"(?:focal\s+onset|focal|juvenile\s+myoclonic|lobe|structural|symptomatic|"
            r"generalized|refractory|drug)\s*$",
            prefix,
        ):
            continue
        return True
    return False


def _note_supports_parietal_lobe_epilepsy(note_lower: str) -> bool:
    return bool(
        re.search(
            r"parietal lobe epilepsy|probable parietal|parietal onset|parietal lobe",
            note_lower,
        )
    )


def _note_supports_on_awakening_syndrome_diagnosis(note_lower: str) -> bool:
    return bool(_ON_AWAKENING_SYNDROME_NOTE_RE.search(note_lower))


def _augment_specificity_collapse_diagnosis_tokens(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], set[str]]:
    note_lower = note_text.lower()
    if not _note_supports_specificity_collapse_diagnosis_co_list(note_lower):
        return [], set()

    normalized = {
        canonical_clinical_phrase(value)
        for value in raw_values
        if value.strip()
    }
    if not normalized & _SPECIFICITY_COLLAPSE_TRIGGER_DIAGNOSES:
        return [], set()

    additions: list[str] = []
    augmented: set[str] = set()
    for token in _SPECIFICITY_COLLAPSE_DIAGNOSIS_TOKENS:
        if token in normalized or token not in ALLOWED_DIAGNOSIS_LABELS:
            continue
        additions.append(token)
        normalized.add(token)
        augmented.add(token)
    return additions, augmented


def _note_supports_specificity_collapse_diagnosis_co_list(note_lower: str) -> bool:
    return bool(
        re.search(r"drug[- ]?refractory\s+focal", note_lower)
        or re.search(
            r"focal epilepsy.{0,80}probable occipital|probable occipital.{0,80}focal epilepsy",
            note_lower,
        )
        or re.search(r"occipital lobe\)?\s*epilepsy", note_lower)
    )


def _augment_current_prescription_medications(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str], set[str]]:
    normalized = {
        canonical_medication_name(value)
        for value in raw_values
        if value.strip()
    }
    additions: list[str] = []
    augmented_evidence: list[str] = list(evidence_values)
    augmented: set[str] = set()

    for medication, evidence_line in _current_prescription_entries(note_text):
        if medication in normalized:
            continue
        additions.append(medication)
        augmented_evidence.append(evidence_line)
        normalized.add(medication)
        augmented.add(medication)

    return [*raw_values, *additions], augmented_evidence, augmented


def _current_prescription_entries(note_text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for match in _CURRENT_PRESCRIPTION_LINE_RE.finditer(note_text):
        line = match.group(0).strip()
        segment = match.group(1).strip()
        segment = re.split(r"\n\s*to start\b", segment, maxsplit=1, flags=re.IGNORECASE)[0]
        for medication in _medications_in_prescription_segment(segment):
            if medication in seen:
                continue
            seen.add(medication)
            entries.append((medication, line))
    return entries


def _medications_in_prescription_segment(segment: str) -> list[str]:
    segment_lower = segment.lower()
    found: list[str] = []
    for medication in _KNOWN_PRESCRIPTION_MEDICATIONS:
        if re.search(rf"\b{re.escape(medication)}\b", segment_lower):
            found.append(medication)
    return found


def _evidence_from_current_prescription_line(evidence_text: str) -> bool:
    lower = evidence_text.lower().strip()
    return any(lower.startswith(prefix) for prefix in _MEDICATION_EVIDENCE_PREFIXES)


def _normalize_diagnoses(raw_values: list[str]) -> tuple[list[str], list[str]]:
    normalized = _dedupe(
        [canonical_clinical_phrase(value) for value in raw_values if value.strip()]
    )
    kept, collapsed = collapse_diagnoses_to_most_specific(normalized)
    kept_set = set(kept)
    return [value for value in raw_values if canonical_clinical_phrase(value) in kept_set], collapsed


def _filter_diagnosis_for_seizure_descriptor_header(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Drop diagnosis outputs when the header only lists seizure-type descriptors."""
    if not raw_values:
        return raw_values, []
    if not _diagnosis_header_lists_seizure_descriptors_only(note_text):
        return raw_values, []
    return [], ["benchmark_bridge:diagnosis_seizure_descriptor_header_suppressed"]


def _diagnosis_header_lists_seizure_descriptors_only(note_text: str) -> bool:
    header = _diagnosis_header_text(note_text)
    if not header:
        return False
    if re.search(r"\b(?:epilepsy|juvenile myoclonic epilepsy|juvenile myoclonic)\b", header):
        return False
    if re.search(r"\b(?:tle|temporal lobe epilepsy)\b", header):
        return False
    if re.search(r"\b(?:probably|probable)\s+jme\s+presenting\b", header):
        return False
    if re.search(r"\bjme\b", header) and not re.search(
        r"\b(?:possible|probably|probable)\s+jme\b",
        header,
    ):
        return False
    seizure_markers = (
        "seizure",
        "jerks",
        "tonic",
        "myoclonic",
        "absence",
        "gtcs",
    )
    return any(marker in header for marker in seizure_markers)


def _seizure_type_values_for_record(
    *,
    record: ExectGoldDocument,
    raw_values: list[str],
    evidence_values: list[str],
) -> list[ExtractedValue]:
    expanded: list[tuple[str, str | None, str, list[str]]] = []
    for index, raw_value in enumerate(raw_values):
        evidence_text = _evidence_at(evidence_values, index)
        for normalized, bridge_flags in _benchmark_values(
            "seizure_type",
            raw_value,
            note_text=record.text,
            evidence_text=evidence_text,
        ):
            expanded.append((raw_value, evidence_text, normalized, bridge_flags))

    normalized_labels = _dedupe([item[2] for item in expanded])
    adjusted_labels, jme_flags = _apply_jme_coarse_seizure_policy(
        normalized_labels,
        record.text,
    )
    adjusted_labels, dissociative_flags = _apply_dissociative_epileptic_seizure_policy(
        adjusted_labels,
        record.text,
    )
    adjusted_labels, collapse_flags = _apply_specificity_collapse_seizure_policy(
        adjusted_labels,
        record.text,
    )
    if collapse_flags:
        co_list_flags: list[str] = []
    else:
        adjusted_labels, co_list_flags = _apply_secondary_token_co_list_policy(
            adjusted_labels,
            record.text,
        )
    policy_flags = [*jme_flags, *dissociative_flags, *collapse_flags, *co_list_flags]
    label_to_source = {
        normalized: (raw_value, evidence_text, bridge_flags)
        for raw_value, evidence_text, normalized, bridge_flags in expanded
    }

    values: list[ExtractedValue] = []
    seen: set[str] = set()
    for normalized in adjusted_labels:
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        _raw_value, evidence_text, bridge_flags = _source_for_adjusted_seizure_label(
            normalized,
            label_to_source,
        )
        values.extend(
            _values_for_family(
                record=record,
                field_name="seizure_type",
                raw_values=[_raw_value],
                evidence_values=[evidence_text or ""],
                fixed_normalized=normalized,
                fixed_bridge_flags=bridge_flags,
                extra_quality_flags=[*bridge_flags, *policy_flags],
            )
        )
    return values


def _source_for_adjusted_seizure_label(
    normalized: str,
    label_to_source: dict[str, tuple[str, str | None, list[str]]],
) -> tuple[str, str | None, list[str]]:
    if normalized in label_to_source:
        return label_to_source[normalized]
    for coarse in (
        "generalized tonic clonic seizures",
        "generalized tonic clonic seizure",
    ):
        if coarse not in label_to_source:
            continue
        raw_value, evidence_text, bridge_flags = label_to_source[coarse]
        if normalized == "tonic clonic seizures":
            return "tonic clonic seizures", evidence_text, [
                *bridge_flags,
                "benchmark_bridge:jme_tonic_clonic_surface",
            ]
        if normalized == "generalized tonic seizures":
            return "generalized tonic seizures", evidence_text, [
                *bridge_flags,
                "benchmark_bridge:jme_generalized_tonic_surface",
            ]
    return normalized, None, []


def _apply_jme_coarse_seizure_policy(
    labels: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    if not labels or not _note_has_jme_context(note_text.lower()):
        return labels, []

    flags: list[str] = []
    adjusted = list(labels)

    preferred = _jme_preferred_coarse_seizure_surface(note_text.lower())
    if preferred is not None:
        remapped: list[str] = []
        for label in adjusted:
            if label in {
                "generalized tonic clonic seizures",
                "generalized tonic clonic seizure",
            }:
                if preferred == "tonic clonic seizures":
                    remapped.append("tonic clonic seizures")
                    flags.append("benchmark_bridge:jme_tonic_clonic_surface")
                    continue
                if preferred == "generalized tonic seizures":
                    remapped.append("generalized tonic seizures")
                    flags.append("benchmark_bridge:jme_generalized_tonic_surface")
                    continue
            remapped.append(label)
        adjusted = _dedupe(remapped)

    if any(label in _JME_COARSE_SEIZURE_LABELS for label in adjusted) and any(
        label in _JME_MYCLONIC_SEIZURE_LABELS for label in adjusted
    ):
        adjusted = [
            label for label in adjusted if label not in _JME_MYCLONIC_SEIZURE_LABELS
        ]
        flags.append("benchmark_bridge:jme_myoclonic_suppressed_for_coarse_label")

    if (
        "generalized tonic clonic seizures" in adjusted
        and "generalized tonic clonic seizure" not in adjusted
        and re.search(r"generali[sz]ed tonic clonic seizure\b", note_text.lower())
    ):
        adjusted.append("generalized tonic clonic seizure")
        flags.append("benchmark_bridge:jme_gtcs_singular_co_listed")

    return _dedupe(adjusted), flags


def _apply_specificity_collapse_seizure_policy(
    labels: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    note_lower = note_text.lower()
    if not _note_supports_specificity_collapse_diagnosis_co_list(note_lower):
        return labels, []
    if not _SECONDARY_GENERALISED_SEIZURE_NOTE_RE.search(note_lower):
        return labels, []

    return [_SECONDARY_COLLAPSED_SEIZURE_TOKEN], [
        "benchmark_bridge:specificity_collapse_seizure_surface"
    ]


def _apply_secondary_token_co_list_policy(
    labels: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    if _SECONDARY_COLLAPSED_SEIZURE_TOKEN in labels:
        return labels, []
    if not _SECONDARY_GENERALISED_SEIZURE_NOTE_RE.search(note_text.lower()):
        return labels, []
    if not any(label in _SECONDARY_GENERALISED_SEIZURE_LABELS for label in labels):
        return labels, []

    return [*labels, _SECONDARY_COLLAPSED_SEIZURE_TOKEN], [
        "benchmark_bridge:secondary_token_co_listed"
    ]


def _note_has_jme_context(note_lower: str) -> bool:
    return bool(
        re.search(r"\bjme\b", note_lower)
        or "juvenile myoclonic epilepsy" in note_lower
        or "juvenile myoclonic" in note_lower
    )


def _jme_preferred_coarse_seizure_surface(note_lower: str) -> str | None:
    if re.search(r"generali[sz]ed tonic clonic", note_lower):
        return None
    if re.search(r"generali[sz]ed tonic seizures?\b", note_lower):
        return "generalized tonic seizures"
    if re.search(r"\btonic clonic seizures?\b", note_lower):
        return "tonic clonic seizures"
    return None


def _apply_dissociative_epileptic_seizure_policy(
    labels: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    note_lower = note_text.lower()
    if not _note_has_dissociative_epileptic_seizure_contrast(note_lower):
        return labels, []
    if not _note_supports_epileptic_seizures_conclusion(note_lower):
        return labels, []

    flags: list[str] = []
    adjusted = list(labels)

    if not re.search(r"\bfocal seizures?\b", note_lower):
        without_focal = [
            label
            for label in adjusted
            if label not in _DISSOCIATIVE_EPILEPTIC_FOCAL_SEIZURE_LABELS
        ]
        if len(without_focal) != len(adjusted):
            adjusted = without_focal
            flags.append("benchmark_bridge:dissociative_focal_seizure_suppressed")

    if _EPILEPTIC_SEIZURES_LABEL not in adjusted:
        adjusted.append(_EPILEPTIC_SEIZURES_LABEL)
        flags.append("benchmark_bridge:epileptic_seizures_surface_restored")

    return _dedupe(adjusted), flags


def _note_has_dissociative_epileptic_seizure_contrast(note_lower: str) -> bool:
    if "dissociative" not in note_lower:
        return False
    return bool(
        re.search(r"epileptic\s+or\s+dissociative|dissociative\s+or\s+epileptic", note_lower)
        or re.search(r"non[- ]epileptic", note_lower)
    )


def _note_supports_epileptic_seizures_conclusion(note_lower: str) -> bool:
    return bool(
        re.search(
            r"(?:sound|seem|appear)s?\s+like\s+epileptic\s+seizures?",
            note_lower,
        )
        or re.search(
            r"on\s+balance\s+these\s+(?:do\s+)?(?:sound|are)\s+like\s+epileptic",
            note_lower,
        )
        or re.search(
            r"(?:think|believe)\s+(?:these|this|they)\s+(?:are|represent)\s+epileptic\s+seizures?",
            note_lower,
        )
    )


def _values_for_family(
    *,
    record: ExectGoldDocument,
    field_name: str,
    raw_values: list[str],
    evidence_values: list[str],
    collapsed_values: list[str] | None = None,
    augmented_values: set[str] | None = None,
    specificity_collapse_augmented: set[str] | None = None,
    extra_quality_flags: list[str] | None = None,
    fixed_normalized: str | None = None,
    fixed_bridge_flags: list[str] | None = None,
    apply_benchmark_bridges: bool = True,
) -> list[ExtractedValue]:
    values: list[ExtractedValue] = []
    seen: set[str] = set()
    collapsed_values = collapsed_values or []
    augmented_values = augmented_values or set()
    specificity_collapse_augmented = specificity_collapse_augmented or set()
    extra_quality_flags = extra_quality_flags or []

    for index, raw_value in enumerate(raw_values):
        evidence_text = _evidence_at(evidence_values, index)
        if field_name == "annotated_medication":
            if _medication_evidence_excluded(evidence_text):
                continue
            evidence_text = _repair_medication_evidence_quote(record, evidence_text)
        benchmark_pairs: list[tuple[str, list[str]]]
        if fixed_normalized is not None:
            benchmark_pairs = [(fixed_normalized, list(fixed_bridge_flags or []))]
        elif apply_benchmark_bridges:
            benchmark_pairs = list(
                _benchmark_values(
                    field_name,
                    raw_value,
                    note_text=record.text,
                    evidence_text=evidence_text,
                )
            )
        else:
            normalized = _normalize_value(field_name, raw_value)
            if not normalized:
                continue
            benchmark_pairs = [(normalized, [])]
        for normalized, bridge_flags in benchmark_pairs:
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            evidence_spans, evidence_flags = _evidence_spans(record, evidence_text)
            quality_flags = _quality_flags(
                field_name=field_name,
                normalized_value=normalized,
                collapsed_values=collapsed_values,
                evidence_text=evidence_text,
            )
            co_list_flags: list[str] = []
            if field_name == "diagnosis" and normalized in augmented_values:
                co_list_flags.append("benchmark_bridge:diagnosis_co_list_augmented")
            if field_name == "diagnosis" and normalized in specificity_collapse_augmented:
                co_list_flags.append(
                    "benchmark_bridge:specificity_collapse_diagnosis_co_listed"
                )
            if field_name == "annotated_medication" and normalized in augmented_values:
                co_list_flags.append(
                    "benchmark_bridge:current_prescription_medication_augmented"
                )
            values.append(
                ExtractedValue(
                    field_name=field_name,
                    raw_value=raw_value,
                    normalized_value=normalized,
                    evidence=evidence_spans,
                    temporality="not_applicable",
                    negation="affirmed",
                    confidence=None,
                    quality_flags=[
                        *quality_flags,
                        *bridge_flags,
                        *co_list_flags,
                        *extra_quality_flags,
                        *evidence_flags,
                    ],
                )
            )
    return values


def _benchmark_values(
    field_name: str,
    value: str,
    *,
    note_text: str = "",
    evidence_text: str | None = None,
) -> list[tuple[str, list[str]]]:
    normalized = _normalize_value(field_name, value)
    bridge_flags: list[str] = []

    if field_name == "diagnosis":
        normalized, bridge_flags = _normalize_diagnosis_surface(normalized)
        if not normalized:
            return []
        if normalized not in ALLOWED_DIAGNOSIS_LABELS:
            return []
    elif field_name == "seizure_type":
        normalized, surface_flags = _normalize_seizure_type_surface(
            normalized,
            note_text=note_text,
        )
        bridge_flags.extend(surface_flags)
        coarsened = _coarsen_granular_seizure_type(normalized)
        if coarsened is not None:
            return coarsened
        split_values = _split_fused_seizure_type(normalized)
        if split_values is not None:
            return [
                (
                    split_value,
                    [*bridge_flags, "benchmark_bridge:fused_seizure_type_split"],
                )
                for split_value in split_values
            ]
    elif field_name == "annotated_medication":
        normalized, med_flags = _normalize_annotated_medication_surface(
            normalized,
            note_text=note_text,
            evidence_text=evidence_text,
        )
        if not normalized:
            return []
        bridge_flags.extend(med_flags)

    return [(normalized, bridge_flags)]


def _normalize_diagnosis_surface(normalized: str) -> tuple[str, list[str]]:
    flags: list[str] = []
    for prefix in ("probable ", "possible "):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :].strip()
            flags.append("benchmark_bridge:diagnosis_uncertainty_stripped")
            break
    if normalized in {"epilepsy unclassified", "unclassified epilepsy"}:
        return "epilepsy", [*flags, "benchmark_bridge:unclassified_epilepsy_surface"]
    if normalized == "symptomatic structural epilepsy":
        return "symptomatic structural focal epilepsy", [
            *flags,
            "benchmark_bridge:symptomatic_structural_focal_restored",
        ]
    if normalized == "epilepsy with generalized tonic clonic seizures from sleep":
        return _ON_AWAKENING_SYNDROME_DIAGNOSIS, [
            *flags,
            "benchmark_bridge:on_awakening_diagnosis_surface",
        ]
    return normalized, flags


def _normalize_seizure_type_surface(
    normalized: str,
    *,
    note_text: str = "",
) -> tuple[str, list[str]]:
    if normalized in {
        "focal onset convulsive seizure",
        "focal onset convulsive seizures",
    }:
        bilateral = (
            "focal to bilateral convulsive seizures"
            if normalized.endswith("seizures")
            else "focal to bilateral convulsive seizure"
        )
        return bilateral, ["benchmark_bridge:focal_onset_to_bilateral_surface"]
    if normalized in {"focal to bilateral seizures", "focal to bilateral seizure"}:
        convulsive = (
            "focal to bilateral convulsive seizures"
            if normalized.endswith("seizures")
            else "focal to bilateral convulsive seizure"
        )
        return convulsive, ["benchmark_bridge:seizure_type_convulsive_modifier"]
    if normalized == "generalized tonic clonic seizures from sleep":
        return "generalized tonic clonic seizures", [
            "benchmark_bridge:seizure_temporal_modifier_stripped"
        ]
    return normalized, []


def _coarsen_granular_seizure_type(
    normalized: str,
) -> list[tuple[str, list[str]]] | None:
    if normalized in _REJECTED_GRANULAR_SEIZURE_TYPES:
        return []
    coarsened = _GRANULAR_SEIZURE_TYPE_COARSENING.get(normalized)
    if coarsened is not None:
        return [
            (
                coarsened,
                ["benchmark_bridge:granular_seizure_surface_coarsened"],
            )
        ]
    return None


def _normalize_annotated_medication_surface(
    normalized: str,
    *,
    note_text: str = "",
    evidence_text: str | None = None,
) -> tuple[str, list[str]]:
    flags: list[str] = []
    repaired = _MEDICATION_SURFACE_REPAIRS.get(normalized)
    if repaired is not None:
        normalized = repaired
        flags.append("benchmark_bridge:medication_surface_repaired")
    brand_surface, brand_flags = _medication_brand_surface_from_note(
        normalized,
        note_text=note_text,
        evidence_text=evidence_text,
    )
    if brand_surface is not None:
        normalized = brand_surface
        flags.extend(brand_flags)
    if normalized in _REJECTED_ANNOTATED_MEDICATIONS:
        return "", [*flags, "benchmark_bridge:non_asm_medication_rejected"]
    return normalized, flags


def _medication_brand_surface_from_note(
    normalized: str,
    *,
    note_text: str,
    evidence_text: str | None,
) -> tuple[str | None, list[str]]:
    if not note_text:
        return None, []
    note_lower = note_text.lower()
    search_text = " ".join(
        part
        for part in (note_lower, (evidence_text or "").lower())
        if part
    )
    for generic, brand_marker, brand_surface in _MEDICATION_BRAND_NOTE_SURFACES:
        if normalized != generic:
            continue
        if brand_marker in search_text:
            return brand_surface, ["benchmark_bridge:medication_brand_surface_preserved"]
    return None, []


def _repair_medication_evidence_quote(
    record: ExectGoldDocument,
    evidence_text: str | None,
) -> str | None:
    if not evidence_text:
        return None
    if evidence_text in record.text:
        return evidence_text

    stripped = _strip_medication_evidence_prefix(evidence_text)
    if stripped and stripped in record.text:
        return stripped

    normalized = evidence_text.replace("\t", " ")
    if normalized in record.text:
        return normalized

    collapsed = re.sub(r"\s+", " ", evidence_text).strip()
    if collapsed in record.text:
        return collapsed

    ellipsis_span = _repair_ellipsis_evidence_span(record, evidence_text)
    if ellipsis_span is not None:
        return ellipsis_span.text

    note_lower = record.text.lower()
    for fragment in _medication_evidence_fragments(evidence_text):
        start = note_lower.find(fragment)
        if start == -1:
            continue
        return record.text[start : start + len(fragment)]

    return evidence_text


def _strip_medication_evidence_prefix(evidence_text: str) -> str:
    lower = evidence_text.lower().strip()
    for prefix in _MEDICATION_EVIDENCE_PREFIXES:
        if lower.startswith(prefix):
            return evidence_text[len(prefix) :].strip()
    return evidence_text


def _medication_evidence_fragments(evidence_text: str) -> list[str]:
    fragments: list[str] = []
    for token in re.split(r"[^a-zA-Z0-9]+", evidence_text):
        token = token.strip().lower()
        if len(token) >= 8:
            fragments.append(token)
    return sorted(fragments, key=len, reverse=True)


def _verified_seizure_allowed(normalized: str, initial_keys: set[str]) -> bool:
    if normalized in initial_keys:
        return True
    for initial_key in initial_keys:
        coarsened = _coarsen_granular_seizure_type(initial_key)
        if coarsened and any(value for value, _ in coarsened) == normalized:
            return True
    return False


def _medication_evidence_excluded(evidence_text: str | None) -> bool:
    if not evidence_text:
        return False
    lower = evidence_text.lower()
    if _evidence_from_current_prescription_line(lower):
        return any(
            phrase in lower
            for phrase in _MEDICATION_PLANNED_OR_HISTORICAL_EVIDENCE_PHRASES
        )
    return any(phrase in lower for phrase in _MEDICATION_EVIDENCE_EXCLUSION_PHRASES)


def _split_fused_seizure_type(normalized: str) -> list[str] | None:
    if normalized in {
        "temporal lobe onset focal seizures",
        "temporal lobe focal seizures",
        "temporal onset focal seizures",
        "temporal lobe seizures",
    }:
        return ["temporal lobe seizure", "focal seizures"]
    if normalized in {
        "focal seizures with secondary generalisation",
        "focal seizures with secondary generalization",
    }:
        return [
            "focal seizures",
            "secondary generalisation",
            "generalized tonic clonic seizure",
        ]
    return None


def _normalize_value(field_name: str, value: str) -> str:
    if field_name == "annotated_medication":
        return canonical_medication_name(value)
    return canonical_clinical_phrase(value)


def _quality_flags(
    *,
    field_name: str,
    normalized_value: str,
    collapsed_values: list[str],
    evidence_text: str | None,
) -> list[str]:
    flags: list[str] = []
    if field_name == "diagnosis" and normalized_value not in ALLOWED_DIAGNOSIS_LABELS:
        flags.append("unsupported_label")
    if field_name == "diagnosis" and collapsed_values:
        flags.append("specificity_collapsed")
    if not evidence_text:
        flags.append("missing_evidence")
    return flags


def _evidence_at(evidence_values: list[str], index: int) -> str | None:
    if index >= len(evidence_values):
        return None
    evidence = evidence_values[index].strip()
    return evidence or None


def _evidence_spans(
    record: ExectGoldDocument,
    evidence_text: str | None,
) -> tuple[list[EvidenceSpan], list[str]]:
    if not evidence_text:
        return [], []
    start = record.text.find(evidence_text)
    if start != -1:
        return [
            EvidenceSpan(
                text=evidence_text,
                start=start,
                end=start + len(evidence_text),
                document_id=record.document_id,
            )
        ], []

    repaired_span = _repair_ellipsis_evidence_span(record, evidence_text)
    if repaired_span is not None:
        return [repaired_span], ["evidence_repair:ellipsis_contiguous_span"]

    return [EvidenceSpan(text=evidence_text, document_id=record.document_id)], []


def _repair_ellipsis_evidence_span(
    record: ExectGoldDocument,
    evidence_text: str,
) -> EvidenceSpan | None:
    if "..." not in evidence_text:
        return None

    fragments = [fragment.strip() for fragment in evidence_text.split("...") if fragment.strip()]
    if len(fragments) < 2:
        return None

    search_from = 0
    first_start: int | None = None
    last_end: int | None = None
    for fragment in fragments:
        start = record.text.find(fragment, search_from)
        if start == -1:
            return None
        if first_start is None:
            first_start = start
        last_end = start + len(fragment)
        search_from = last_end

    if first_start is None or last_end is None:
        return None

    repaired_text = record.text[first_start:last_end]
    if len(repaired_text) > 300 or "\n\n" in repaired_text:
        return None

    return EvidenceSpan(
        text=repaired_text,
        start=first_start,
        end=last_end,
        document_id=record.document_id,
    )


def _as_list(value: Optional[object]) -> list[str]:
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

