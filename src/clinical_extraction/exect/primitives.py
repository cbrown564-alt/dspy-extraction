"""ExECTv2-specific taxonomy primitive helpers."""

from __future__ import annotations

import re

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
    collapse_diagnoses_to_most_specific,
    format_medication_temporality_label,
    infer_prescription_temporality,
)
from clinical_extraction.primitives import NormalizationResult, PrimitiveCandidate

EXECT_MEDICATION_RX_CANDIDATE_PRIMITIVE_ID = "exect.medication.rx_candidates.v1"
EXECT_MEDICATION_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.medication.benchmark_bridge.v1"
)
EXECT_MEDICATION_TEMPORALITY_PRIMITIVE_ID = (
    "exect.medication_temporality.post_classifier.v1"
)
EXECT_MEDICATION_TEMPORALITY_NON_ASM_GUARD_PRIMITIVE_ID = (
    "exect.medication_temporality.non_asm_guard.v1"
)
EXECT_SEIZURE_TYPE_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.seizure_type.benchmark_bridge.v1"
)
EXECT_DIAGNOSIS_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.diagnosis.benchmark_bridge.v1"
)
EXECT_FREQUENCY_RATE_CANDIDATE_PRIMITIVE_ID = "exect.frequency.rate_candidates.v1"
EXECT_FREQUENCY_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.frequency.benchmark_bridge.v1"
)

_ASM_CANONICAL_MEDICATIONS = frozenset(
    {
        "brivaracetam",
        "carbamazepine",
        "clobazam",
        "eslicarbazepine",
        "gabapentin",
        "lacosamide",
        "lamotrigine",
        "levetiracetam",
        "oxcarbazepine",
        "phenobarbital",
        "phenytoin",
        "pregabalin",
        "sodium valproate",
        "topiramate",
        "vigabatrin",
        "zonisamide",
    }
)

_SURFACE_REPAIRS = {
    "brivitiracetam": "brivaracetam",
    "eslicarbazine": "eslicarbazepine",
    "zonismaide": "zonisamide",
}

_BRAND_SURFACES = {
    "lamictal": "lamotrigine",
    "epilim": "sodium valproate",
    "epilim chrono": "sodium valproate",
    "keppra": "levetiracetam",
}

_NON_ASM_MEDICATIONS = frozenset(
    {
        "amitriptyline",
        "citalopram",
        "diazepam",
        "fluoxetine",
        "sertraline",
    }
)

_MEDICATION_SURFACES = tuple(
    sorted(
        {
            *_ASM_CANONICAL_MEDICATIONS,
            *_SURFACE_REPAIRS,
            *_SURFACE_REPAIRS.values(),
            *_BRAND_SURFACES,
            *_NON_ASM_MEDICATIONS,
        },
        key=len,
        reverse=True,
    )
)

_CURRENT_MARKERS = (
    "current medication",
    "current medications",
    "current anti-epileptic medication",
    "current anti epileptic medication",
    "currently taking",
    "currently she is taking",
    "currently he is taking",
)

_PLANNED_MARKERS = (
    "to start",
    "please start",
    "plan to start",
    "will start",
    "recommend starting",
    "grateful if you could prescribe",
    "could prescribe",
    "to change to",
)

_PREVIOUS_MARKERS = (
    "previously",
    "prior ",
    "tried ",
    "had been on",
    "had been taking",
    "stopped completely",
    "decided to stop",
    "stopped ",
)

_TAPER_OR_STOP_MARKERS = (
    "reduce and stop",
    "reduce the",
    "weaned",
    "taper",
    "stop over",
    "every week until",
)

_REJECTED_GRANULAR_SEIZURE_TYPES = frozenset(
    {
        "absences",
        "jerks",
        "occasional absences",
    }
)

_GRANULAR_SEIZURE_TYPE_COARSENING = {
    "focal aware seizure": "focal seizure",
    "focal aware seizures": "focal seizures",
    "focal impaired awareness seizure": "focal seizure",
    "focal impaired awareness seizures": "focal seizures",
    "focal seizures with impaired awareness": "focal seizures with altered awareness",
    "myoclonic jerks": "myoclonic seizures",
    "absence events": "generalized tonic clonic seizures",
}

_SEIZURE_SURFACE_REPAIRS = {
    "focal onset convulsive seizure": "focal to bilateral convulsive seizure",
    "focal onset convulsive seizures": "focal to bilateral convulsive seizures",
    "focal to bilateral seizure": "focal to bilateral convulsive seizure",
    "focal to bilateral seizures": "focal to bilateral convulsive seizures",
    "generalized tonic clonic seizures from sleep": "generalized tonic clonic seizures",
}

_FUSED_SEIZURE_TYPE_SPLITS = {
    "temporal lobe onset focal seizures": (
        "temporal lobe seizure",
        "focal seizures",
    ),
    "temporal lobe focal seizures": (
        "temporal lobe seizure",
        "focal seizures",
    ),
    "temporal onset focal seizures": (
        "temporal lobe seizure",
        "focal seizures",
    ),
    "temporal lobe seizures": (
        "temporal lobe seizure",
        "focal seizures",
    ),
    "focal seizures with secondary generalisation": (
        "focal seizures",
        "secondary generalisation",
        "generalized tonic clonic seizure",
    ),
    "focal seizures with secondary generalization": (
        "focal seizures",
        "secondary generalisation",
        "generalized tonic clonic seizure",
    ),
}

_SECONDARY_GENERALISED_SEIZURE_LABELS = frozenset(
    {
        "secondary generalised seizure",
        "secondary generalised seizures",
        "secondary generalized seizure",
        "secondary generalized seizures",
    }
)
_SECONDARY_COLLAPSED_SEIZURE_TOKEN = "secondary"
_SECONDARY_GENERALISED_SEIZURE_NOTE_RE = re.compile(
    r"\bsecondary generali[sz]ed seiz"
)

_ALLOWED_DIAGNOSIS_LABELS = frozenset(
    {
        "drug",
        "drug refractory epilepsies",
        "drug refractory epilepsy",
        "drug resistant epilepsy",
        "epilepsy",
        "epilepsy due to stroke",
        "epilepsy with generalized tonic clonic seizure alone",
        "epilepsy with generalized tonic clonic seizures alone",
        "epilepsy with generalized tonic clonic seizures on awakening",
        "epilepsy, generalized",
        "focal",
        "focal epilepsy",
        "focal onset epilepsy",
        "focal symptomatic epilepsy",
        "frontal",
        "frontal lobe epilepsy",
        "generalized epilepsy",
        "genetic generalized epilepsy",
        "intractable epilepsy",
        "jme",
        "juvenile absence epilepsy",
        "juvenile myoclonic epilepsy",
        "localisation related epilepsy",
        "occipital",
        "occipital lobe epilepsy",
        "parietal lobe epilepsy",
        "primary generalized epilepsy",
        "refractory epilepsies",
        "status epilepticus",
        "symptomatic",
        "symptomatic epilepsy",
        "symptomatic focal epilepsy",
        "symptomatic structural focal epilepsy",
        "temporal lobe epilepsy",
    }
)

_DIAGNOSIS_HEADER_RE = re.compile(r"(?im)^\s*diagnosis\s*[:\s–\-]+\s*([^\n]+)")
_DIAGNOSIS_MIN_CERTAINTY = 4
_GENERIC_EPILEPSY_CO_LIST_TRIGGERS = (
    "focal onset epilepsy",
    "primary generalized epilepsy",
    "symptomatic structural focal epilepsy",
    "focal epilepsy",
    "generalized epilepsy",
    "genetic generalized epilepsy",
)
_SPECIFICITY_COLLAPSE_DIAGNOSIS_TOKENS = ("focal", "drug", "occipital")
_SPECIFICITY_COLLAPSE_TRIGGER_DIAGNOSES = frozenset(
    {
        "drug refractory epilepsy",
        "focal epilepsy",
        "occipital lobe epilepsy",
    }
)
_ON_AWAKENING_SYNDROME_DIAGNOSIS = (
    "epilepsy with generalized tonic clonic seizures on awakening"
)
_ON_AWAKENING_SYNDROME_NOTE_RE = re.compile(
    r"epilepsy with generali[sz]ed tonic clonic seiz(?:ure|ures)\s+"
    r"(?:from sleep|on awakening)\b"
)


def build_exect_medication_candidate_payloads(note_text: str) -> list[PrimitiveCandidate]:
    """Return note-anchored medication candidates using the shared payload contract.

    These are soft hints for narrow medication experiments. Planned and previous
    medications are surfaced for inspection but are not S1 benchmark-facing
    current prescription outputs.
    """

    candidates: list[PrimitiveCandidate] = []
    seen: set[tuple[str, int]] = set()
    for surface in _MEDICATION_SURFACES:
        for match in re.finditer(rf"\b{re.escape(surface)}\b", note_text, re.IGNORECASE):
            raw_text = note_text[match.start() : match.end()]
            key = (raw_text.lower(), match.start())
            if key in seen:
                continue
            seen.add(key)

            context = _local_context(note_text, match.start(), match.end())
            bridge = exect_medication_benchmark_bridge(
                raw_text,
                note_text=note_text,
                evidence_text=context,
            )
            temporality = infer_exect_medication_temporality(context)
            caveats = _candidate_caveats(bridge=bridge, temporality=temporality)

            candidates.append(
                PrimitiveCandidate(
                    primitive_id=EXECT_MEDICATION_RX_CANDIDATE_PRIMITIVE_ID,
                    dataset="exect_v2",
                    field_family="medication",
                    raw_text=raw_text,
                    normalized_value=bridge.canonical_value,
                    benchmark_value=(
                        bridge.benchmark_value
                        if temporality.canonical_value == "current"
                        else None
                    ),
                    source_span_text=raw_text,
                    start=match.start(),
                    end=match.end(),
                    rule_name="exect_note_anchored_medication_surface",
                    confidence=1.0,
                    caveats=caveats,
                    metadata={
                        "temporality": temporality.canonical_value,
                        "benchmark_s1_included": (
                            temporality.canonical_value == "current"
                            and bridge.benchmark_value is not None
                        ),
                        "canonical_medication": bridge.canonical_value,
                        "benchmark_surface_policy": bridge.metadata.get(
                            "benchmark_surface_policy"
                        ),
                        "context": context,
                    },
                )
            )

    return sorted(candidates, key=lambda item: (item.start or 0, str(item.raw_text)))


def exect_medication_benchmark_bridge(
    raw_value: str,
    *,
    note_text: str = "",
    evidence_text: str | None = None,
    prediction_affecting: bool = True,
) -> NormalizationResult:
    """Normalize an ExECT medication surface while preserving benchmark policy."""

    repaired = _SURFACE_REPAIRS.get(raw_value.strip().lower())
    source_value = repaired or raw_value
    canonical = canonical_medication_name(source_value)
    canonical = _BRAND_SURFACES.get(canonical, canonical)
    benchmark_value = _brand_surface_from_text(
        canonical=canonical,
        note_text=note_text,
        evidence_text=evidence_text,
    )
    if benchmark_value is None and canonical in _ASM_CANONICAL_MEDICATIONS:
        benchmark_value = canonical

    metadata: dict[str, object] = {
        "is_asm": canonical in _ASM_CANONICAL_MEDICATIONS,
        "surface_repaired": repaired is not None,
        "benchmark_surface_policy": (
            "brand_surface_preserved"
            if benchmark_value is not None and benchmark_value != canonical
            else "canonical_generic"
        ),
    }
    caveat = None
    if canonical in _NON_ASM_MEDICATIONS or canonical not in _ASM_CANONICAL_MEDICATIONS:
        benchmark_value = None
        metadata["is_asm"] = False
        metadata["rejected_reason"] = "non_asm_medication"
        caveat = "Non-ASM medications are rejected from ExECT annotated medication output."
    elif repaired is not None:
        caveat = "Medication surface spelling was repaired before benchmark alignment."

    return NormalizationResult(
        primitive_id=EXECT_MEDICATION_BENCHMARK_BRIDGE_PRIMITIVE_ID,
        dataset="exect_v2",
        field_family="medication",
        raw_value=raw_value,
        canonical_value=canonical,
        benchmark_value=benchmark_value,
        clinical_caveat=caveat,
        transformation_rule="exect_medication_benchmark_surface_alignment",
        prediction_affecting=prediction_affecting,
        scorer_only=not prediction_affecting,
        metadata=metadata,
    )


def infer_exect_medication_temporality(evidence_text: str | None) -> NormalizationResult:
    """Classify prescription temporality for benchmark-facing medication policy."""

    text = (evidence_text or "").lower()
    cues: list[str] = []
    if _has_current_prescription_marker(text):
        temporality = "current"
        benchmark_value = "current_prescription"
    elif any(marker in text for marker in _PLANNED_MARKERS):
        temporality = "planned"
        benchmark_value = None
    elif any(marker in text for marker in _PREVIOUS_MARKERS):
        temporality = "previous"
        benchmark_value = None
    else:
        temporality = "unknown"
        benchmark_value = None

    if any(marker in text for marker in _TAPER_OR_STOP_MARKERS):
        cue = (
            "taper_or_stop_inside_current_prescription_line"
            if temporality == "current"
            else "taper_or_stop"
        )
        cues.append(cue)
    if temporality != "unknown":
        cues.append(f"{temporality}_cue")

    caveat = None
    if temporality in {"planned", "previous"}:
        caveat = (
            "Medication is clinically relevant but not benchmark-facing S1 current "
            "prescription output."
        )
    elif temporality == "unknown":
        caveat = "Medication temporality is not explicit enough for S1 benchmark inclusion."

    return NormalizationResult(
        primitive_id=EXECT_MEDICATION_TEMPORALITY_PRIMITIVE_ID,
        dataset="exect_v2",
        field_family="medication",
        raw_value=evidence_text,
        canonical_value=temporality,
        benchmark_value=benchmark_value,
        clinical_caveat=caveat,
        transformation_rule="exect_medication_temporality_cue_policy",
        prediction_affecting=True,
        scorer_only=False,
        metadata={
            "benchmark_s1_included": temporality == "current",
            "cues": cues,
        },
    )


_VALID_RX_TEMPORALITIES = frozenset({"current", "planned", "previous"})


def recover_exect_medication_temporality_with_post_classifier(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Recover S4 medication-temporality labels with evidence-aligned post classification."""

    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for index, raw in enumerate(raw_values):
        if not raw.strip():
            continue
        evidence = (
            evidence_values[index].strip()
            if index < len(evidence_values) and evidence_values[index]
            else ""
        )
        model_status: str | None = None
        if "|" in raw:
            medication_part, status_part = raw.split("|", 1)
            medication_name = canonical_medication_name(medication_part)
            model_status = canonical_clinical_phrase(status_part)
            context = evidence or note_text
        else:
            medication_name = canonical_medication_name(raw)
            context = evidence or note_text

        if not medication_name:
            flags.append("s4_bridge:medication_temporality_unrecognized")
            continue
        if (
            medication_name in _NON_ASM_MEDICATIONS
            or medication_name not in _ASM_CANONICAL_MEDICATIONS
        ):
            flags.append("s4_bridge:medication_temporality_non_asm_removed")
            continue

        classification = infer_exect_medication_temporality(context)
        status = classification.canonical_value
        if status not in _VALID_RX_TEMPORALITIES:
            if status == "unknown":
                flags.append("s4_bridge:medication_temporality_unknown_removed")
            else:
                flags.append("s4_bridge:medication_temporality_invalid_status_removed")
            continue
        if (
            model_status in _VALID_RX_TEMPORALITIES
            and model_status != status
        ):
            flags.append("s4_bridge:medication_temporality_status_reclassified")

        label = format_medication_temporality_label(medication_name, status)
        if label in seen:
            continue
        seen.add(label)
        recovered.append(label)

    return recovered, flags


def recover_exect_medication_temporality_non_asm_guard(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Drop non-ASM medication-temporality labels; keep model-assigned ASM status."""

    del evidence_values  # G0 does not reclassify from evidence (unlike H1 post-classifier).

    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for raw in raw_values:
        if not raw.strip():
            continue
        if "|" in raw:
            medication_part, status_part = raw.split("|", 1)
            medication_name = canonical_medication_name(medication_part)
            status = canonical_clinical_phrase(status_part)
            if not medication_name:
                flags.append("s4_bridge:medication_temporality_unrecognized")
                continue
            if (
                medication_name in _NON_ASM_MEDICATIONS
                or medication_name not in _ASM_CANONICAL_MEDICATIONS
            ):
                flags.append("s4_bridge:medication_temporality_non_asm_removed")
                continue
            if status not in _VALID_RX_TEMPORALITIES:
                flags.append("s4_bridge:medication_temporality_invalid_status_removed")
                continue
            label = format_medication_temporality_label(medication_name, status)
        else:
            medication_name = canonical_medication_name(raw)
            if not medication_name:
                flags.append("s4_bridge:medication_temporality_unrecognized")
                continue
            if (
                medication_name in _NON_ASM_MEDICATIONS
                or medication_name not in _ASM_CANONICAL_MEDICATIONS
            ):
                flags.append("s4_bridge:medication_temporality_non_asm_removed")
                continue
            status = infer_prescription_temporality(note_text)
            label = format_medication_temporality_label(medication_name, status)
            flags.append("s4_bridge:medication_temporality_status_inferred")

        if label in seen:
            continue
        seen.add(label)
        recovered.append(label)

    return recovered, flags


def exect_seizure_type_benchmark_bridge(
    raw_value: str,
    *,
    note_text: str = "",
    prediction_affecting: bool = True,
) -> list[NormalizationResult]:
    """Map seizure-type surfaces to audited ExECT benchmark labels.

    This is a bridge primitive, not a gold loader. It intentionally does not
    use MarkupSeizureFrequency spans as seizure-type evidence.
    """

    canonical = _canonical_seizure_type_surface(raw_value)
    if not canonical or canonical in _REJECTED_GRANULAR_SEIZURE_TYPES:
        return []

    repaired = _SEIZURE_SURFACE_REPAIRS.get(canonical)
    split_values = _FUSED_SEIZURE_TYPE_SPLITS.get(repaired or canonical)
    if split_values is not None:
        return [
            _seizure_type_normalization_result(
                raw_value=raw_value,
                canonical_value=canonical,
                benchmark_value=split_value,
                rule="exect_seizure_type_fused_phrase_split",
                prediction_affecting=prediction_affecting,
                metadata={
                    "bridge_flags": ["benchmark_bridge:fused_seizure_type_split"],
                    "split_index": index,
                    "source_policy": "diagnosis_json_seizure_type_surface",
                },
            )
            for index, split_value in enumerate(split_values)
        ]

    coarsened = _GRANULAR_SEIZURE_TYPE_COARSENING.get(repaired or canonical)
    if coarsened is not None:
        return [
            _seizure_type_normalization_result(
                raw_value=raw_value,
                canonical_value=canonical,
                benchmark_value=coarsened,
                rule="exect_seizure_type_granularity_coarsening",
                prediction_affecting=prediction_affecting,
                metadata={
                    "bridge_flags": [
                        "benchmark_bridge:granular_seizure_surface_coarsened"
                    ],
                    "source_policy": "diagnosis_json_seizure_type_surface",
                },
            )
        ]

    if repaired is not None:
        return [
            _seizure_type_normalization_result(
                raw_value=raw_value,
                canonical_value=canonical,
                benchmark_value=repaired,
                rule="exect_seizure_type_surface_repair",
                prediction_affecting=prediction_affecting,
                metadata={
                    "bridge_flags": [_seizure_repair_flag(canonical)],
                    "source_policy": "diagnosis_json_seizure_type_surface",
                },
            )
        ]

    results = [
        _seizure_type_normalization_result(
            raw_value=raw_value,
            canonical_value=canonical,
            benchmark_value=canonical,
            rule="exect_seizure_type_identity_surface",
            prediction_affecting=prediction_affecting,
            metadata={
                "bridge_flags": [],
                "source_policy": "diagnosis_json_seizure_type_surface",
            },
        )
    ]
    if _should_co_list_secondary_token(canonical, note_text):
        results.append(
            _seizure_type_normalization_result(
                raw_value=raw_value,
                canonical_value=canonical,
                benchmark_value=_SECONDARY_COLLAPSED_SEIZURE_TOKEN,
                rule="exect_seizure_type_secondary_token_co_list",
                prediction_affecting=prediction_affecting,
                metadata={
                    "bridge_flags": ["benchmark_bridge:secondary_token_co_listed"],
                    "source_policy": "diagnosis_json_seizure_type_surface",
                },
            )
        )
    return results


def exect_diagnosis_annotation_policy(attrs: dict[str, object]) -> NormalizationResult:
    """Represent audited ExECT diagnosis-row inclusion policy."""

    category = str(attrs.get("DiagCategory") or attrs.get("diag_category") or "")
    negation = str(attrs.get("Negation") or attrs.get("negation") or "")
    try:
        certainty = int(attrs.get("Certainty") or attrs.get("certainty") or 0)
    except (TypeError, ValueError):
        certainty = 0
    included = (
        category == "Epilepsy"
        and negation == "Affirmed"
        and certainty >= _DIAGNOSIS_MIN_CERTAINTY
    )
    rejected_reasons: list[str] = []
    if category != "Epilepsy":
        rejected_reasons.append("non_epilepsy_diag_category")
    if negation != "Affirmed":
        rejected_reasons.append("non_affirmed_diagnosis")
    if certainty < _DIAGNOSIS_MIN_CERTAINTY:
        rejected_reasons.append("below_certainty_threshold")

    return NormalizationResult(
        primitive_id=EXECT_DIAGNOSIS_BENCHMARK_BRIDGE_PRIMITIVE_ID,
        dataset="exect_v2",
        field_family="diagnosis",
        raw_value=attrs.get("CUIPhrase") or attrs.get("text"),
        canonical_value=canonical_clinical_phrase(
            str(attrs.get("CUIPhrase") or attrs.get("text") or "")
        ),
        benchmark_value="benchmark_included" if included else None,
        clinical_caveat=(
            None
            if included
            else "Diagnosis row is excluded from the audited S0/S1 diagnosis view."
        ),
        transformation_rule="exect_diagnosis_annotation_inclusion_policy",
        prediction_affecting=False,
        scorer_only=True,
        metadata={
            "diag_category": category,
            "negation": negation,
            "certainty": certainty,
            "min_certainty": _DIAGNOSIS_MIN_CERTAINTY,
            "benchmark_included": included,
            "rejected_reasons": rejected_reasons,
        },
    )


def exect_diagnosis_benchmark_bridge(
    raw_values: str | list[str] | tuple[str, ...] | None,
    *,
    note_text: str = "",
    prediction_affecting: bool = True,
) -> list[NormalizationResult]:
    """Map diagnosis predictions to audited ExECT benchmark-facing labels.

    The bridge preserves ExECT diagnosis policy boundaries: no diagnosis from
    seizure-descriptor-only headers, no subtype inference from seizure evidence,
    certainty qualifiers stripped only as benchmark surface repair, and parent
    diagnoses collapsed when a more specific descendant is already present.
    """

    values = _diagnosis_raw_values(raw_values)
    if values and _diagnosis_header_lists_seizure_descriptors_only(note_text):
        return []

    values, co_listed, specificity_co_listed = _augment_diagnosis_values(
        values,
        note_text,
    )
    normalized_inputs: list[tuple[str, str, list[str]]] = []
    for raw_value in values:
        canonical, flags = _normalize_diagnosis_surface(raw_value)
        if not canonical or canonical not in _ALLOWED_DIAGNOSIS_LABELS:
            continue
        normalized_inputs.append((raw_value, canonical, flags))

    kept, collapsed = collapse_diagnoses_to_most_specific(
        _dedupe([canonical for _, canonical, _ in normalized_inputs])
    )
    kept_set = set(kept)
    collapsed_set = set(collapsed)

    results: list[NormalizationResult] = []
    seen: set[str] = set()
    for raw_value, canonical, flags in normalized_inputs:
        if canonical not in kept_set or canonical in seen:
            continue
        seen.add(canonical)
        result_flags = list(flags)
        if collapsed:
            result_flags.append("specificity_collapsed")
        if canonical in co_listed:
            result_flags.append("benchmark_bridge:diagnosis_co_list_augmented")
        if canonical in specificity_co_listed:
            result_flags.append(
                "benchmark_bridge:specificity_collapse_diagnosis_co_listed"
            )

        results.append(
            NormalizationResult(
                primitive_id=EXECT_DIAGNOSIS_BENCHMARK_BRIDGE_PRIMITIVE_ID,
                dataset="exect_v2",
                field_family="diagnosis",
                raw_value=raw_value,
                canonical_value=canonical_clinical_phrase(raw_value),
                benchmark_value=canonical,
                clinical_caveat=_diagnosis_caveat(
                    canonical=canonical,
                    collapsed=collapsed_set,
                    flags=result_flags,
                ),
                transformation_rule="exect_diagnosis_benchmark_policy_bridge",
                prediction_affecting=prediction_affecting,
                scorer_only=not prediction_affecting,
                metadata={
                    "bridge_flags": result_flags,
                    "collapsed_parent_diagnoses": collapsed,
                    "co_list_augmented": canonical in co_listed,
                    "specificity_collapse_augmented": (
                        canonical in specificity_co_listed
                    ),
                    "source_policy": "diagnosis_json_epilepsy_surface",
                },
            )
        )
    return results


def _candidate_caveats(
    *,
    bridge: NormalizationResult,
    temporality: NormalizationResult,
) -> list[str]:
    caveats = [
        "ExECT medication candidates are soft hints, not gold-label replacements."
    ]
    if bridge.clinical_caveat:
        caveats.append(bridge.clinical_caveat)
    if temporality.canonical_value == "planned":
        caveats.append(
            "Planned medications are not benchmark-facing S1 current prescriptions."
        )
    elif temporality.canonical_value == "previous":
        caveats.append(
            "Previous medications are not benchmark-facing S1 current prescriptions."
        )
    elif temporality.canonical_value == "unknown":
        caveats.append(
            "Unknown medication temporality is diagnostic until a task policy includes it."
        )
    return caveats


def _diagnosis_raw_values(
    raw_values: str | list[str] | tuple[str, ...] | None,
) -> list[str]:
    if raw_values is None:
        return []
    if isinstance(raw_values, str):
        return [raw_values] if raw_values.strip() else []
    return [value for value in raw_values if value and value.strip()]


def _normalize_diagnosis_surface(raw_value: str) -> tuple[str, list[str]]:
    normalized = canonical_clinical_phrase(raw_value)
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


def _augment_diagnosis_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], set[str], set[str]]:
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
        if key in normalized or key not in _ALLOWED_DIAGNOSIS_LABELS:
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

    if (
        _ON_AWAKENING_SYNDROME_DIAGNOSIS not in normalized
        and _note_supports_on_awakening_syndrome_diagnosis(note_lower)
    ):
        add(_ON_AWAKENING_SYNDROME_DIAGNOSIS)

    collapse_additions, collapse_augmented = (
        _augment_specificity_collapse_diagnosis_tokens(
            [*raw_values, *additions],
            note_text,
        )
    )
    for label in collapse_additions:
        key = canonical_clinical_phrase(label)
        if key in normalized or key not in _ALLOWED_DIAGNOSIS_LABELS:
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
        if token in normalized or token not in _ALLOWED_DIAGNOSIS_LABELS:
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
    return bool(
        re.search(
            r"\b(?:single focal seizure|focal seizure|focal seizures|gtcs|generalized tonic clonic|"
            r"generalised tonic clonic|myoclonic jerks|absences)\b",
            header,
        )
    )


def _diagnosis_caveat(
    *,
    canonical: str,
    collapsed: set[str],
    flags: list[str],
) -> str | None:
    if canonical in collapsed:
        return "Generic parent diagnosis was removed by audited specificity collapse."
    if "benchmark_bridge:diagnosis_co_list_augmented" in flags:
        return "Diagnosis label was added only when note text explicitly supported co-listing."
    if "benchmark_bridge:diagnosis_uncertainty_stripped" in flags:
        return "Uncertainty qualifier was stripped for benchmark-facing surface alignment."
    return None


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _seizure_type_normalization_result(
    *,
    raw_value: str,
    canonical_value: str,
    benchmark_value: str,
    rule: str,
    prediction_affecting: bool,
    metadata: dict[str, object],
) -> NormalizationResult:
    caveat = None
    if canonical_value != benchmark_value:
        caveat = (
            "ExECT seizure-type bridge maps clinically richer or fused wording to "
            "the audited benchmark-facing surface."
        )
    return NormalizationResult(
        primitive_id=EXECT_SEIZURE_TYPE_BENCHMARK_BRIDGE_PRIMITIVE_ID,
        dataset="exect_v2",
        field_family="seizure_type",
        raw_value=raw_value,
        canonical_value=canonical_value,
        benchmark_value=benchmark_value,
        clinical_caveat=caveat,
        transformation_rule=rule,
        prediction_affecting=prediction_affecting,
        scorer_only=not prediction_affecting,
        metadata=metadata,
    )


def _canonical_seizure_type_surface(raw_value: str) -> str:
    return canonical_clinical_phrase(raw_value)


def _seizure_repair_flag(canonical: str) -> str:
    if canonical.startswith("focal onset convulsive"):
        return "benchmark_bridge:focal_onset_to_bilateral_surface"
    if canonical.startswith("focal to bilateral"):
        return "benchmark_bridge:seizure_type_convulsive_modifier"
    if canonical == "generalized tonic clonic seizures from sleep":
        return "benchmark_bridge:seizure_temporal_modifier_stripped"
    return "benchmark_bridge:seizure_type_surface_repaired"


def _should_co_list_secondary_token(canonical: str, note_text: str) -> bool:
    if canonical == _SECONDARY_COLLAPSED_SEIZURE_TOKEN:
        return False
    if canonical not in _SECONDARY_GENERALISED_SEIZURE_LABELS:
        return False
    return bool(_SECONDARY_GENERALISED_SEIZURE_NOTE_RE.search(note_text.lower()))


def _brand_surface_from_text(
    *,
    canonical: str,
    note_text: str,
    evidence_text: str | None,
) -> str | None:
    search_text = " ".join(
        part.lower() for part in (note_text, evidence_text or "") if part
    )
    for brand_surface, brand_canonical in _BRAND_SURFACES.items():
        if brand_canonical == canonical and brand_surface in search_text:
            return brand_surface
    return None


def _local_context(note_text: str, start: int, end: int) -> str:
    line_start = note_text.rfind("\n", 0, start) + 1
    line_end = note_text.find("\n", end)
    if line_end == -1:
        line_end = len(note_text)
    previous_sentence = note_text.rfind(". ", 0, start)
    sentence_start = max(
        line_start,
        previous_sentence + 2 if previous_sentence != -1 else line_start,
    )
    sentence_end = note_text.find(". ", end)
    if sentence_end == -1:
        sentence_end = line_end
    else:
        sentence_end = min(sentence_end + 1, line_end)
    return note_text[sentence_start:sentence_end].strip()


def _has_current_prescription_marker(text: str) -> bool:
    return any(marker in text for marker in _CURRENT_MARKERS) or bool(
        re.search(r"^medications?\s*[:\s-]", text)
    )


_FREQUENCY_MARKERS = (
    " per ",
    "seizure free",
    "frequency increased",
    "frequency decreased",
    "infrequent",
    "frequency same",
)
_NEAR_MISS_QUANTIFIED_FREQUENCY = re.compile(
    r"^(?P<count>\d+) per (?P<period>week|month|day|year)$"
)
_FREQUENCY_CHANGE_SYNONYMS = {
    "increased frequency": "frequency increased",
    "frequency has increased": "frequency increased",
    "decreased frequency": "frequency decreased",
    "frequency has decreased": "frequency decreased",
}
_SEIZURE_TYPE_FREQUENCY_CONFUSION = (
    "seizure",
    "seizures",
    "tonic clonic",
    "convulsive",
    "absence",
    "myoclonic",
    "focal aware",
    "impaired awareness",
    "altered awareness",
    "temporal lobe",
    "occipital lobe",
)
_QUANTIFIED_FREQUENCY_RE = re.compile(
    r"^(?:\d+|several) per (?:\d+ )?(?:week|month|day|year)$"
)
_NON_AUDITED_FREQUENCY_RES = (
    re.compile(r" per 30 day$"),
    re.compile(r"previous appointment"),
    re.compile(r"^several per"),
    re.compile(r" per \d+ \d+ week$"),
)
_FREQUENCY_CO_LABEL_CUES = {
    "frequency increased": (
        "frequency increased",
        "frequency has increased",
        "increased frequency",
        "seizures have returned",
        "seizures returned",
        "seizures have worsened",
        "seizures worsened",
        "returned seizures",
        "having more",
        "getting more",
        "more seizures",
        "another seizure",
        "had another seizure",
        "seizures returning",
        "increasing seizures",
        "seizures increasing",
        "seizures have increased",
        "seizures have been worse",
        "seizures worse",
        "more frequent",
        "worse in the last year",
    ),
    "frequency decreased": (
        "frequency decreased",
        "frequency has decreased",
        "decreased frequency",
        "seizures have improved",
        "seizures improved",
        "epilepsy has improved",
        "epilepsy improved",
        "seizures have reduced",
        "seizures reduced",
        "improved seizures",
    ),
    "infrequent": (
        "infrequent",
        "occasional",
        "occasionally",
        "rare",
        "rarely",
        "well controlled",
        "controlled",
        "reasonably controlled",
    ),
    "frequency same": (
        "frequency same",
        "remains the same",
        "remain the same",
        "no change",
        "remain well controlled",
        "remains well controlled",
        "remain controlled",
        "remains controlled",
        "continue to get",
        "continues to get",
        "continue to have",
        "continues to have",
        "not really helped",
        "hasn't really helped",
        "haven't really helped",
        "stable",
        "remain stable",
        "remains stable",
        "stable frequency",
        "seizures remain",
        "well controlled",
        "controlled",
    ),
}
_COUNT_WORDS = {
    "once": "1",
    "twice": "2",
    "thrice": "3",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "several": "3",
}
_PERIOD_UNIT = r"weeks?|months?|days?|years?"
_QUANTIFIED_FREQUENCY_EX_RE = re.compile(
    rf"\b(?P<count>once|twice|thrice|one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)\s+"
    rf"(?:(?:[a-zA-Z-]+)\s+){{0,3}}?(?:seizures?|convulsions|episodes|events)?\s*(?:times?\s+)?(?:every|per|a|over|in|during|within|for)(?:\s+the\s+(?:last|past))?\s+"
    rf"(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)
_IMPLICIT_QUANTIFIED_FREQUENCY_RE = re.compile(
    rf"\b(?:every|per|a|over|in|during|within|for)(?:\s+the\s+(?:last|past))?\s+(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*"
    rf"(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)
_ADVERB_FREQUENCY_RE = re.compile(
    rf"\b(?P<count>once|twice|thrice|one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*"
    rf"(?:times?\s+)?(?P<adverb>daily|weekly|monthly|yearly|annually)\b",
    flags=re.IGNORECASE,
)
_ZERO_RATE_WINDOW_RE = re.compile(
    rf"\b(?:no|zero|0|not had|not happen|not happened)\s+(?:[a-zA-Z-]+\s+){{0,5}}?(?:seizures?|convulsions|episodes|events)?\s*"
    rf"(?:now\s+)?(?:for|in|over|since|per|every|a)\s+(?:the\s+last|the\s+past|at\s+least|more\s+than|over)?\s*"
    rf"(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)
_ZERO_RATE_FREE_RE = re.compile(
    rf"\bseizure[- ]free\s+(?:for|in|over)\s+(?:the\s+last|the\s+past|at\s+least|more\s+than|over)?\s*"
    rf"(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)
_SEIZURE_FREE_CURRENT_RE = re.compile(
    rf"\b(?:no|zero|0|not had|not happen|not happened)\s+(?:[a-zA-Z-]+\s+){{0,3}}?(?:seizures?|convulsions|episodes|events)\b",
    flags=re.IGNORECASE,
)
_AGO_ZERO_RATE_RE = re.compile(
    rf"\b(?:(?:last|most recent)\s*(?:one|seizure|event|episode|convulsion|seizures|convulsions|episodes|events)?|(?:her|his|the)?\s*(?:seizure|event|episode|convulsion|seizures|convulsions|episodes|events))\s*(?:of\s+these\s+)?(?:was|happened|occurred|occur|ocured|occurd|happend)?\s*(?:around|about|at\s+least|more\s+than|greater\s+than|over)?\s*"
    rf"(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)\s+(?P<period>{_PERIOD_UNIT})\s+ago\b",
    flags=re.IGNORECASE,
)
_SEIZURE_FREE_SINCE_YEAR_RE = re.compile(
    rf"\b(?:seizure[- ]free|free of seizures)\s+since\s+"
    rf"(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sept|oct|nov|dec)?\s*"
    rf"(?P<year>\d{{4}})\b",
    flags=re.IGNORECASE,
)
_LAST_EVENT_YEAR_RE = re.compile(
    rf"\blast\s+(?:seizure|event|episode|convulsion)\s+(?:was\s+)?(?:in\s+)?"
    rf"(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sept|oct|nov|dec)?\s*"
    rf"(?P<year>\d{{4}})\b",
    flags=re.IGNORECASE,
)
_LAST_SEIZURE_DATE_RE = re.compile(
    rf"\blast\s+(?:seizure|event|episode|convulsion|seizures|convulsions|episodes|events)\s+(?:was\s+)?(?:on\s+the\s+|on\s+|in\s+)?(?:\d{{1,2}}(?:st|nd|rd|th)?\s+)?(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sept|oct|nov|dec)\b",
    flags=re.IGNORECASE,
)
_BREAKTHROUGH_AFTER_PERIOD_RE = re.compile(
    rf"\b(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|several|\d+)?\s*(?P<period>{_PERIOD_UNIT})\s+(?:without\s+having|without|free of|no)\s+seizures?\s+(?:[a-zA-Z-]+\s+){{0,10}}?(?P<event>cluster|seizure|episode|event|convulsion|convulsions)\b",
    flags=re.IGNORECASE,
)
_AUDITED_QUALITATIVE_FREQUENCY_LABELS = frozenset(
    {
        "frequency increased",
        "frequency decreased",
        "infrequent",
        "seizure free",
        "frequency same",
    }
)
_ADVERB_TO_PERIOD = {
    "daily": "day",
    "weekly": "week",
    "monthly": "month",
    "yearly": "year",
    "annually": "year",
}


def build_exect_frequency_candidate_payloads(note_text: str) -> list[PrimitiveCandidate]:
    """Return note-anchored ExECT seizure-frequency candidates as shared payloads."""

    payloads: list[PrimitiveCandidate] = []
    for label in _build_exect_frequency_label_set(note_text):
        span = _frequency_label_span(note_text, label)
        payloads.append(
            PrimitiveCandidate(
                primitive_id=EXECT_FREQUENCY_RATE_CANDIDATE_PRIMITIVE_ID,
                dataset="exect_v2",
                field_family="frequency",
                raw_text=span or label,
                normalized_value=label,
                benchmark_value=label,
                source_span_text=span or label,
                start=note_text.find(span) if span and span in note_text else None,
                end=(
                    note_text.find(span) + len(span)
                    if span and span in note_text
                    else None
                ),
                rule_name=_frequency_candidate_rule_name(label, note_text),
                confidence=1.0,
                caveats=[
                    "ExECT seizure-frequency candidates are soft hints for narrow S4 probes.",
                    "Gan monthly normalization and label-policy classes do not transfer to ExECT.",
                    "MarkupSeizureFrequency templates remain the benchmark-facing gold surface.",
                ],
                metadata={
                    "candidate_source": _frequency_candidate_source(label, note_text),
                    "gan_temporal_filtered": _frequency_candidate_source(label, note_text)
                    == "gan_temporal_filtered",
                },
            )
        )
    return payloads


def build_exect_frequency_pre_vocab_labels(note_text: str) -> list[str]:
    """Build sorted benchmark-facing seizure-frequency labels for H2 pre-vocab probes."""

    return sorted(_build_exect_frequency_label_set(note_text))


def format_exect_frequency_pre_vocab_note(note_text: str) -> str:
    """Inject seizure-frequency-only audited candidates before the clinical note."""

    frequency_candidates = build_exect_frequency_pre_vocab_labels(note_text)
    lines = [
        "Precomputed benchmark-facing candidates (soft hints; emit only when note-supported):",
        f"seizure_frequency: {', '.join(frequency_candidates)}",
        "",
        "---",
        "",
        note_text,
    ]
    return "\n".join(lines)


def repair_exect_frequency_surface(canonical: str) -> tuple[str, list[str]]:
    """Repair near-miss quantified rates and qualitative frequency-change synonyms."""

    flags: list[str] = []
    repaired = canonical

    synonym = _FREQUENCY_CHANGE_SYNONYMS.get(canonical)
    if synonym:
        return synonym, ["s4_bridge:frequency_change_synonym"]

    near_miss = _NEAR_MISS_QUANTIFIED_FREQUENCY.match(canonical)
    if near_miss:
        repaired = (
            f"{near_miss.group('count')} per 1 {near_miss.group('period')}"
        )
        flags.append("s4_bridge:frequency_missing_time_period_inserted")

    if canonical.startswith("seizure free") and canonical != "seizure free":
        if re.match(r"seizure free since \d{4}$", canonical):
            return canonical, flags
        return "seizure free", [*flags, "s4_bridge:seizure_free_prose_collapsed"]

    return repaired, flags


def note_has_exect_frequency_support(note_text: str) -> bool:
    """Return True when note text supports at least one audited frequency template."""

    return bool(_build_exect_frequency_label_set(note_text))


def recover_exect_frequency_benchmark_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Recover benchmark-facing seizure-frequency labels from model outputs."""

    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for raw in raw_values:
        if not raw.strip():
            continue
        canonical = canonical_clinical_phrase(raw)
        if not canonical:
            continue
        if _looks_like_seizure_type_not_frequency(raw):
            flags.append("s4_bridge:seizure_type_removed_from_frequency")
            continue
        repaired, repair_flags = repair_exect_frequency_surface(canonical)
        flags.extend(repair_flags)
        canonical = repaired
        if _is_non_audited_frequency_surface(canonical):
            flags.append("s4_bridge:non_audited_frequency_removed")
            continue
        if not _is_audited_exect_frequency_template(canonical):
            flags.append("s4_bridge:unsupported_frequency_removed")
            continue
        if canonical in seen:
            continue
        seen.add(canonical)
        recovered.append(canonical)

    recovered, co_label_flags = _augment_exect_frequency_co_labels(recovered, note_text)
    flags.extend(co_label_flags)
    return recovered, flags


def recover_exect_frequency_benchmark_values_with_post_merge(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Recover frequency labels with v1.2 bridge plus post-merge note anchoring."""

    recovered, flags = recover_exect_frequency_benchmark_values(raw_values, note_text)
    note_anchored = _build_exect_frequency_label_set(note_text)

    seen = set(recovered)
    for label in sorted(note_anchored):
        if label in seen:
            continue
        recovered.append(label)
        seen.add(label)
        flags.append("s4_bridge:note_anchored_frequency_merged")

    note_lower = note_text.lower()
    filtered: list[str] = []
    for label in recovered:
        if label == "seizure free" and "seizure free" not in note_lower:
            flags.append("s4_bridge:spurious_seizure_free_removed")
            continue
        if label.startswith("seizure free since ") and not _SEIZURE_FREE_SINCE_YEAR_RE.search(
            note_text
        ):
            flags.append("s4_bridge:spurious_seizure_free_removed")
            continue
        filtered.append(label)

    return filtered, flags


def recover_exect_frequency_benchmark_values_with_multi_label_retention(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Recover frequency labels with widened co-labels and partial multi-label slot fill.

    Differs from post-merge: fills missing note-anchored labels only when the model
    emitted at least one supported frequency label (partial block retention), and
    augments qualitative co-labels when the note supports change cues even without a
    quantified rate in model output.
    """

    recovered, flags = recover_exect_frequency_benchmark_values(raw_values, note_text)
    recovered, co_flags = _augment_exect_frequency_co_labels_multi_label(
        recovered,
        note_text,
    )
    flags.extend(co_flags)

    if recovered:
        note_anchored = _build_exect_frequency_label_set(note_text)
        seen = set(recovered)
        for label in sorted(note_anchored):
            if label in seen:
                continue
            recovered.append(label)
            seen.add(label)
            flags.append("s4_bridge:multi_label_slot_filled")

    note_lower = note_text.lower()
    filtered: list[str] = []
    for label in recovered:
        if label == "seizure free" and "seizure free" not in note_lower:
            flags.append("s4_bridge:spurious_seizure_free_removed")
            continue
        if label.startswith("seizure free since ") and not _SEIZURE_FREE_SINCE_YEAR_RE.search(
            note_text
        ):
            flags.append("s4_bridge:spurious_seizure_free_removed")
            continue
        filtered.append(label)

    return filtered, flags


def exect_frequency_benchmark_bridge(
    raw_values: list[str],
    *,
    note_text: str = "",
    prediction_affecting: bool = True,
) -> list[NormalizationResult]:
    """Map seizure-frequency predictions to audited ExECT benchmark templates."""

    recovered, flags = recover_exect_frequency_benchmark_values(raw_values, note_text)
    if not recovered:
        return [
            NormalizationResult(
                primitive_id=EXECT_FREQUENCY_BENCHMARK_BRIDGE_PRIMITIVE_ID,
                dataset="exect_v2",
                field_family="frequency",
                raw_value=None,
                canonical_value=None,
                benchmark_value=None,
                clinical_caveat=(
                    "ExECT seizure frequency abstains when no audited benchmark template "
                    "survives bridge policy."
                ),
                transformation_rule="exect_frequency_abstention",
                prediction_affecting=prediction_affecting,
                scorer_only=not prediction_affecting,
                metadata={
                    "bridge_flags": flags,
                    "abstention": True,
                    "no_reference_policy": "empty_list_not_gan_no_reference",
                },
            )
        ]

    return [
        _exect_frequency_normalization_result(
            raw_value=label,
            benchmark_value=label,
            bridge_flags=flags,
            prediction_affecting=prediction_affecting,
        )
        for label in recovered
    ]


def filter_gan_temporal_candidate_for_exect(canonical_label: str) -> str | None:
    """Accept Gan temporal hints only when they map to audited ExECT frequency templates."""

    return _accept_exect_frequency_candidate_label(canonical_label)


def _build_exect_frequency_label_set(note_text: str) -> set[str]:
    from clinical_extraction.gan.temporal_candidates import (
        build_temporal_frequency_candidates_from_note,
    )

    candidates: set[str] = set()
    note_lower = note_text.lower()

    # 1. Qualitative cues (including the new "frequency same" category)
    for label, cues in _FREQUENCY_CO_LABEL_CUES.items():
        if any(cue in note_lower for cue in cues):
            accepted = _accept_exect_frequency_candidate_label(label)
            if accepted:
                candidates.add(accepted)

    # 2. Seizure free since year with alternative phrasings
    for match in _SEIZURE_FREE_SINCE_YEAR_RE.finditer(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            f"seizure free since {match.group('year')}"
        )
        if accepted:
            candidates.add(accepted)

    for match in _LAST_EVENT_YEAR_RE.finditer(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            f"seizure free since {match.group('year')}"
        )
        if accepted:
            candidates.add(accepted)

    # 3. Seizure-free word boundary and negation/return guards
    # We only add "seizure free" if it's explicitly mentioned (with boundary)
    # or if current seizure-free status is matched, AND there's no mention of seizures returning.
    seizures_returned = (
        "seizures have returned" in note_lower
        or "seizures returned" in note_lower
        or "returned seizures" in note_lower
        or "seizures recurred" in note_lower
        or "seizures recur" in note_lower
        or "seizures have worsened" in note_lower
        or "seizures worsened" in note_lower
        or "seizures are worse" in note_lower
        or "seizures have been worse" in note_lower
        or "worse in the last" in note_lower
        or "worse recently" in note_lower
    )
    
    if not seizures_returned:
        if re.search(r"\bseizure[- ]free\b", note_lower):
            accepted = _accept_exect_frequency_candidate_label("seizure free")
            if accepted:
                candidates.add(accepted)
        elif _SEIZURE_FREE_CURRENT_RE.search(note_text):
            accepted = _accept_exect_frequency_candidate_label("seizure free")
            if accepted:
                candidates.add(accepted)

    # Helper function to parse period_count with list options for several
    def get_period_count_options(raw_count_str: str | None) -> list[str]:
        if not raw_count_str:
            return ["1"]
        clean = raw_count_str.strip().lower()
        if not clean:
            return ["1"]
        clean_first = clean.split()[0]
        if clean_first == "several":
            return ["2", "3"]
        return [_COUNT_WORDS.get(clean_first, clean_first)]

    def get_count_options(raw_count_str: str | None) -> list[str]:
        if not raw_count_str:
            return ["1"]
        clean = raw_count_str.strip().lower()
        if clean == "several":
            return ["2", "3"]
        return [_COUNT_WORDS.get(clean, clean)]

    # 4. Standard and Extended Quantified Rates
    for match in _QUANTIFIED_FREQUENCY_EX_RE.finditer(note_text):
        counts = get_count_options(match.group("count"))
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for count in counts:
            for period_count in period_counts:
                accepted = _accept_exect_frequency_candidate_label(
                    f"{count} per {period_count} {period}"
                )
                if accepted:
                    candidates.add(accepted)

    # 5. Implicit Quantified Rates
    for match in _IMPLICIT_QUANTIFIED_FREQUENCY_RE.finditer(note_text):
        # Prevent matching standard quantified rate twice if it was already matched
        # (check if a count word precedes the match)
        start_idx = match.start()
        preceding_text = note_text[max(0, start_idx - 15) : start_idx].strip().lower()
        # if preceding text ends with any count word or digit, skip this to avoid duplication
        preceding_words = preceding_text.split()
        if preceding_words:
            last_word = preceding_words[-1].strip("-,.(): ")
            if last_word in _COUNT_WORDS or last_word.isdigit():
                continue
        
        counts = ["1"]
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for count in counts:
            for period_count in period_counts:
                accepted = _accept_exect_frequency_candidate_label(
                    f"{count} per {period_count} {period}"
                )
                if accepted:
                    candidates.add(accepted)

    # 6. Section-List Adverbial Rates
    for match in _ADVERB_FREQUENCY_RE.finditer(note_text):
        counts = get_count_options(match.group("count"))
        adverb = match.group("adverb").lower()
        period = _ADVERB_TO_PERIOD.get(adverb, "week")
        for count in counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"{count} per 1 {period}"
            )
            if accepted:
                candidates.add(accepted)

    # 7. Zero-Rate Windows
    for match in _ZERO_RATE_WINDOW_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"0 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)
            if not seizures_returned:
                accepted_sf = _accept_exect_frequency_candidate_label("seizure free")
                if accepted_sf:
                    candidates.add(accepted_sf)

    for match in _ZERO_RATE_FREE_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"0 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)
            if not seizures_returned:
                accepted_sf = _accept_exect_frequency_candidate_label("seizure free")
                if accepted_sf:
                    candidates.add(accepted_sf)

    for match in _AGO_ZERO_RATE_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"0 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)
            if not seizures_returned:
                accepted_sf = _accept_exect_frequency_candidate_label("seizure free")
                if accepted_sf:
                    candidates.add(accepted_sf)

    # 7b. Last Seizure Date to Seizure Free
    if not seizures_returned:
        for match in _LAST_SEIZURE_DATE_RE.finditer(note_text):
            accepted = _accept_exect_frequency_candidate_label("seizure free")
            if accepted:
                candidates.add(accepted)

    # 7c. Breakthrough after period
    for match in _BREAKTHROUGH_AFTER_PERIOD_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            accepted = _accept_exect_frequency_candidate_label(
                f"1 per {period_count} {period}"
            )
            if accepted:
                candidates.add(accepted)

    # 8. Legacy temporal candidates
    for temporal_candidate in build_temporal_frequency_candidates_from_note(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            temporal_candidate.canonical_label
        )
        if accepted:
            candidates.add(accepted)

    return candidates

    # 8. Legacy temporal candidates
    for temporal_candidate in build_temporal_frequency_candidates_from_note(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            temporal_candidate.canonical_label
        )
        if accepted:
            candidates.add(accepted)

    return candidates


def _accept_exect_frequency_candidate_label(label: str) -> str | None:
    canonical = canonical_clinical_phrase(label)
    if not canonical or _looks_like_seizure_type_not_frequency(canonical):
        return None
    repaired, _ = repair_exect_frequency_surface(canonical)
    if _is_non_audited_frequency_surface(repaired):
        return None
    if not _is_audited_exect_frequency_template(repaired):
        return None
    return repaired


def _is_audited_exect_frequency_template(canonical: str) -> bool:
    if canonical in _AUDITED_QUALITATIVE_FREQUENCY_LABELS:
        return True
    if re.match(r"seizure free since \d{4}$", canonical):
        return True
    return bool(_QUANTIFIED_FREQUENCY_RE.match(canonical))


def _is_non_audited_frequency_surface(canonical: str) -> bool:
    return any(pattern.search(canonical) for pattern in _NON_AUDITED_FREQUENCY_RES)


def _is_quantified_frequency_label(canonical: str) -> bool:
    return bool(_QUANTIFIED_FREQUENCY_RE.match(canonical))


def _augment_exect_frequency_co_labels(
    recovered: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    if not any(_is_quantified_frequency_label(label) for label in recovered):
        return recovered, []

    note = note_text.lower()
    flags: list[str] = []
    augmented = list(recovered)
    seen = set(recovered)

    for label, cues in _FREQUENCY_CO_LABEL_CUES.items():
        if label in seen:
            continue
        if any(cue in note for cue in cues):
            augmented.append(label)
            seen.add(label)
            flags.append("s4_bridge:frequency_co_label_augmented")

    return augmented, flags


def _augment_exect_frequency_co_labels_multi_label(
    recovered: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Augment qualitative co-labels when note cues exist and model engaged frequency."""

    if not recovered:
        return recovered, []

    note = note_text.lower()
    note_anchored = _build_exect_frequency_label_set(note_text)
    note_has_rate_block = any(
        _is_quantified_frequency_label(label) or label.startswith("0 per")
        for label in note_anchored
    )
    model_has_rate = any(
        _is_quantified_frequency_label(label) or label.startswith("0 per")
        for label in recovered
    )
    if not (note_has_rate_block or model_has_rate):
        return _augment_exect_frequency_co_labels(recovered, note_text)

    flags: list[str] = []
    augmented = list(recovered)
    seen = set(recovered)

    for label, cues in _FREQUENCY_CO_LABEL_CUES.items():
        if label in seen:
            continue
        if any(cue in note for cue in cues):
            augmented.append(label)
            seen.add(label)
            flags.append("s4_bridge:frequency_co_label_multi_label_retained")

    return augmented, flags


def _looks_like_seizure_frequency_label(value: str) -> bool:
    canonical = canonical_clinical_phrase(value)
    if not canonical:
        return False
    return any(marker in canonical for marker in _FREQUENCY_MARKERS)


def _looks_like_seizure_type_not_frequency(value: str) -> bool:
    canonical = canonical_clinical_phrase(value)
    if not canonical:
        return False
    if _looks_like_seizure_frequency_label(canonical):
        return False
    return any(marker in canonical for marker in _SEIZURE_TYPE_FREQUENCY_CONFUSION)


def _normalize_period_unit(period: str) -> str:
    return period.lower().rstrip("s")


def _frequency_label_span(note_text: str, label: str) -> str | None:
    # 1. First check qualitative cues
    if label in _FREQUENCY_CO_LABEL_CUES:
        for cue in _FREQUENCY_CO_LABEL_CUES[label]:
            index = note_text.lower().find(cue)
            if index >= 0:
                return note_text[index : index + len(cue)]
                
    # 2. Check year since / last event matches
    for match in _SEIZURE_FREE_SINCE_YEAR_RE.finditer(note_text):
        if f"seizure free since {match.group('year')}" == label:
            return match.group(0)
            
    for match in _LAST_EVENT_YEAR_RE.finditer(note_text):
        if f"seizure free since {match.group('year')}" == label:
            return match.group(0)
            
    # 3. Check current seizure free
    if label == "seizure free":
        # check seizure[- ]free
        match = re.search(r"\bseizure[- ]free\b", note_text, re.IGNORECASE)
        if match:
            return match.group(0)
        match = _SEIZURE_FREE_CURRENT_RE.search(note_text)
        if match:
            return match.group(0)

    # Helper function to parse count & period_count with list options for several
    def get_period_count_options(raw_count_str: str | None) -> list[str]:
        if not raw_count_str:
            return ["1"]
        clean = raw_count_str.strip().lower()
        if not clean:
            return ["1"]
        clean_first = clean.split()[0]
        if clean_first == "several":
            return ["2", "3"]
        return [_COUNT_WORDS.get(clean_first, clean_first)]

    def get_count_options(raw_count_str: str | None) -> list[str]:
        if not raw_count_str:
            return ["1"]
        clean = raw_count_str.strip().lower()
        if clean == "several":
            return ["2", "3"]
        return [_COUNT_WORDS.get(clean, clean)]

    # 4. Standard and Extended Quantified Rates
    for match in _QUANTIFIED_FREQUENCY_EX_RE.finditer(note_text):
        counts = get_count_options(match.group("count"))
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for count in counts:
            for period_count in period_counts:
                if f"{count} per {period_count} {period}" == label:
                    return match.group(0)

    # 5. Implicit Quantified Rates
    for match in _IMPLICIT_QUANTIFIED_FREQUENCY_RE.finditer(note_text):
        count = "1"
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            if f"{count} per {period_count} {period}" == label:
                return match.group(0)

    # 6. Section-List Adverbial Rates
    for match in _ADVERB_FREQUENCY_RE.finditer(note_text):
        counts = get_count_options(match.group("count"))
        adverb = match.group("adverb").lower()
        period = _ADVERB_TO_PERIOD.get(adverb, "week")
        for count in counts:
            if f"{count} per 1 {period}" == label:
                return match.group(0)

    # 7. Zero-Rate Windows
    for match in _ZERO_RATE_WINDOW_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            if f"0 per {period_count} {period}" == label:
                return match.group(0)

    for match in _ZERO_RATE_FREE_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            if f"0 per {period_count} {period}" == label:
                return match.group(0)

    for match in _AGO_ZERO_RATE_RE.finditer(note_text):
        period_counts = get_period_count_options(match.group("period_count"))
        period = _normalize_period_unit(match.group("period"))
        for period_count in period_counts:
            if f"0 per {period_count} {period}" == label:
                return match.group(0)

    return None


def _frequency_candidate_rule_name(label: str, note_text: str) -> str:
    source = _frequency_candidate_source(label, note_text)
    if source == "gan_temporal_filtered":
        return "gan_temporal_to_exect_template"
    if source == "qualitative_change_cue":
        return "qualitative_frequency_change_cue"
    if label.startswith("seizure free"):
        return "seizure_free_surface"
    if label.startswith("0 per "):
        return "zero_rate_surface"
    return "quantified_rate_surface"


def _frequency_candidate_source(label: str, note_text: str) -> str:
    from clinical_extraction.gan.temporal_candidates import (
        build_temporal_frequency_candidates_from_note,
    )

    note_lower = note_text.lower()
    if label in _FREQUENCY_CO_LABEL_CUES and any(
        cue in note_lower for cue in _FREQUENCY_CO_LABEL_CUES[label]
    ):
        return "qualitative_change_cue"
    if label.startswith("seizure free") and "seizure free" in note_lower:
        return "seizure_free_surface"
    for temporal_candidate in build_temporal_frequency_candidates_from_note(note_text):
        accepted = _accept_exect_frequency_candidate_label(
            temporal_candidate.canonical_label
        )
        if accepted == label:
            return "gan_temporal_filtered"
    return "note_regex_quantified"


def _exect_frequency_normalization_result(
    *,
    raw_value: str,
    benchmark_value: str,
    bridge_flags: list[str],
    prediction_affecting: bool,
) -> NormalizationResult:
    caveat = None
    if "s4_bridge:seizure_free_prose_collapsed" in bridge_flags:
        caveat = (
            "Clinical prose may state seizure-free duration; benchmark gold may use "
            "quantified zero-rate templates instead."
        )
    elif "s4_bridge:frequency_co_label_augmented" in bridge_flags:
        caveat = (
            "Qualitative change labels are added only when note text contains explicit "
            "frequency-change cues alongside a quantified rate."
        )
    return NormalizationResult(
        primitive_id=EXECT_FREQUENCY_BENCHMARK_BRIDGE_PRIMITIVE_ID,
        dataset="exect_v2",
        field_family="frequency",
        raw_value=raw_value,
        canonical_value=benchmark_value,
        benchmark_value=benchmark_value,
        clinical_caveat=caveat,
        transformation_rule="exect_frequency_benchmark_recovery",
        prediction_affecting=prediction_affecting,
        scorer_only=not prediction_affecting,
        metadata={
            "bridge_flags": bridge_flags,
            "source_policy": "markup_seizure_frequency_templates",
            "gan_monthly_policy_excluded": True,
        },
    )
