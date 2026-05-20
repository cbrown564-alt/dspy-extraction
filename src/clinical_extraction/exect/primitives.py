"""ExECTv2-specific taxonomy primitive helpers."""

from __future__ import annotations

import re

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
    collapse_diagnoses_to_most_specific,
)
from clinical_extraction.primitives import NormalizationResult, PrimitiveCandidate

EXECT_MEDICATION_RX_CANDIDATE_PRIMITIVE_ID = "exect.medication.rx_candidates.v1"
EXECT_MEDICATION_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.medication.benchmark_bridge.v1"
)
EXECT_MEDICATION_TEMPORALITY_PRIMITIVE_ID = (
    "exect.medication_temporality.post_classifier.v1"
)
EXECT_SEIZURE_TYPE_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.seizure_type.benchmark_bridge.v1"
)
EXECT_DIAGNOSIS_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.diagnosis.benchmark_bridge.v1"
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
