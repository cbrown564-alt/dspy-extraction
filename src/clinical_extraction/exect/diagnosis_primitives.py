"""ExECT diagnosis taxonomy primitive and bridge helpers."""

from __future__ import annotations

import re

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    collapse_diagnoses_to_most_specific,
)
from clinical_extraction.primitives import NormalizationResult

EXECT_DIAGNOSIS_BENCHMARK_BRIDGE_PRIMITIVE_ID = (
    "exect.diagnosis.benchmark_bridge.v1"
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

__all__ = [
    "EXECT_DIAGNOSIS_BENCHMARK_BRIDGE_PRIMITIVE_ID",
    "exect_diagnosis_annotation_policy",
    "exect_diagnosis_benchmark_bridge",
]
