from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from clinical_extraction.paths import EXECT_ROOT
from clinical_extraction.schemas import ExectGoldDocument

MIN_CERTAINTY = 4

_DIAGNOSIS_PARENT = {
    "focal epilepsy": "epilepsy",
    "generalized epilepsy": "epilepsy",
    "juvenile myoclonic epilepsy": "generalized epilepsy",
}

_MEDICATION_SYNONYMS = {
    "keppra": "levetiracetam",
    "epilim": "sodium valproate",
    "sodium valproate": "sodium valproate",
    "lamotrigine": "lamotrigine",
    "levetiracetam": "levetiracetam",
    "clobazam": "clobazam",
    "carbamazepine": "carbamazepine",
    "oxcarbazepine": "oxcarbazepine",
    "topiramate": "topiramate",
    "zonisamide": "zonisamide",
    "lacosamide": "lacosamide",
    "eslicarbazepine": "eslicarbazepine",
    "eslicarbazepine acetate": "eslicarbazepine",
    "phenytoin": "phenytoin",
    "phenobarbital": "phenobarbital",
    "gabapentin": "gabapentin",
    "pregabalin": "pregabalin",
    "vigabatrin": "vigabatrin",
}

_GOLD_NOISE_TERMS = {"seizure", "seizures"}

_INVESTIGATION_MODALITIES = ("eeg", "mri", "ct")
_INVESTIGATION_RESULTS = {"normal", "abnormal", "unknown"}

_FREQUENCY_CHANGE_LABELS = {
    "Increased": "frequency increased",
    "Decreased": "frequency decreased",
    "Infrequent": "infrequent",
}

_PLANNED_RX_PHRASES = (
    "to start",
    "plan to start",
    "will start",
    "due to start",
    "commence",
)

_PREVIOUS_RX_PHRASES = (
    "previously",
    "had been on",
    "had been taking",
    "stopped",
    "discontinued",
    "weaned",
)

_CURRENT_RX_MARKERS = (
    "current anti",
    "current-antiepileptic",
    "current medication",
)

_COMORBIDITY_EXCLUDED_PHRASES = {
    "absence",
    "absences",
    "altered awareness and consciousness",
    "cluster of seizures",
    "convulsive seizure",
    "convulsive seizures",
    "dissociative seizures",
    "febrile seizure",
    "febrile seizures",
    "jerks",
    "loss of consciousness",
    "myoclonic jerks",
    "non epileptic",
    "non epileptic attacks",
    "non epileptic psychogenic seizures",
    "photosensitivity",
    "seizure",
    "seizures",
    "transient",
    "transient loss of consciousness",
}


def load_exect_gold_document(
    document_id: str,
    *,
    exect_root: Path = EXECT_ROOT,
) -> ExectGoldDocument:
    normalized_id = document_id.removesuffix(".txt").removesuffix(".json")
    json_path = exect_root / "Json" / f"{normalized_id}.json"
    text_path = exect_root / "Gold1-200_corrected_spelling" / f"{normalized_id}.txt"

    annotations = json.loads(json_path.read_text(encoding="utf-8"))
    text = text_path.read_text(encoding="utf-8")

    raw_diagnoses: list[str] = []
    seizure_types: list[str] = []
    medications: list[str] = []
    investigations: list[str] = []
    comorbidities: list[str] = []
    birth_histories: list[str] = []
    onsets: list[str] = []
    epilepsy_causes: list[str] = []
    when_diagnosed: list[str] = []
    seizure_frequencies: list[str] = []
    medication_temporalities: list[str] = []

    for annotation in annotations:
        entity = annotation.get("entity")
        attrs = annotation.get("attributes", {})
        if entity == "Diagnosis" and _is_affirmed_high_certainty(attrs):
            category = attrs.get("DiagCategory")
            phrase = canonical_clinical_phrase(attrs.get("CUIPhrase") or annotation.get("text", ""))
            if not phrase:
                continue
            if category == "Epilepsy":
                raw_diagnoses.append(phrase)
            elif category in {"MultipleSeizures", "SingleSeizure"}:
                seizure_types.append(phrase)
        elif entity == "Prescription":
            medication = canonical_medication_name(
                attrs.get("CUIPhrase") or attrs.get("DrugName") or annotation.get("text", "")
            )
            if medication:
                medications.append(medication)
                temporality = infer_prescription_temporality(annotation.get("text", ""))
                medication_temporalities.append(
                    format_medication_temporality_label(medication, temporality)
                )
        elif entity == "Investigations":
            investigation = canonical_investigation_label(attrs)
            if investigation:
                investigations.append(investigation)
        elif entity == "PatientHistory":
            phrase = attrs.get("CUIPhrase") or annotation.get("text", "")
            if is_comorbidity_patient_history(phrase, attrs):
                comorbidity = canonical_comorbidity_label(phrase)
                if comorbidity:
                    comorbidities.append(comorbidity)
        elif entity == "BirthHistory" and _is_affirmed_high_certainty(attrs):
            label = canonical_birth_history_label(attrs.get("CUIPhrase") or annotation.get("text", ""))
            if label:
                birth_histories.append(label)
        elif entity == "Onset" and _is_affirmed_high_certainty(attrs):
            label = canonical_onset_label(attrs.get("CUIPhrase") or annotation.get("text", ""))
            if label:
                onsets.append(label)
        elif entity == "EpilepsyCause" and _is_affirmed_high_certainty(attrs):
            label = canonical_epilepsy_cause_label(attrs.get("CUIPhrase") or annotation.get("text", ""))
            if label:
                epilepsy_causes.append(label)
        elif entity == "WhenDiagnosed" and _is_affirmed_high_certainty(attrs):
            label = canonical_when_diagnosed_label(attrs.get("CUIPhrase") or annotation.get("text", ""))
            if label:
                when_diagnosed.append(label)
        elif entity == "SeizureFrequency":
            label = canonical_seizure_frequency_label(attrs)
            if label:
                seizure_frequencies.append(label)

    diagnoses, collapsed = collapse_diagnoses_to_most_specific(_dedupe(raw_diagnoses))
    seizure_types = _dedupe(seizure_types)
    medications = _dedupe(medications)
    investigations = _dedupe(investigations)
    comorbidities = _dedupe(comorbidities)
    birth_histories = _dedupe(birth_histories)
    onsets = _dedupe(onsets)
    epilepsy_causes = _dedupe(epilepsy_causes)
    when_diagnosed = _dedupe(when_diagnosed)
    seizure_frequencies = _dedupe(seizure_frequencies)
    medication_temporalities = _dedupe(medication_temporalities)

    quality_flags = _quality_flags(
        diagnoses=diagnoses,
        seizure_types=seizure_types,
        medications=medications,
        collapsed=collapsed,
    )

    return ExectGoldDocument(
        document_id=normalized_id,
        text=text,
        raw_annotations=annotations,
        raw_diagnoses=_dedupe(raw_diagnoses),
        diagnoses=diagnoses,
        seizure_types=seizure_types,
        current_medications=medications,
        investigations=investigations,
        comorbidities=comorbidities,
        birth_histories=birth_histories,
        onsets=onsets,
        epilepsy_causes=epilepsy_causes,
        when_diagnosed=when_diagnosed,
        seizure_frequencies=seizure_frequencies,
        medication_temporalities=medication_temporalities,
        quality_flags=quality_flags,
    )


def load_exect_gold_documents(*, exect_root: Path = EXECT_ROOT) -> list[ExectGoldDocument]:
    json_dir = exect_root / "Json"
    return [
        load_exect_gold_document(path.stem, exect_root=exect_root)
        for path in sorted(json_dir.glob("EA*.json"))
    ]


def canonical_clinical_phrase(value: str | None) -> str:
    if not value:
        return ""
    value = _split_camel(value)
    value = value.replace("-", " ").replace("_", " ")
    value = re.sub(r"\s+", " ", value).strip().lower()
    value = value.replace("generalised", "generalized")
    value = value.replace("tonic chronic", "tonic clonic")
    return value


def canonical_medication_name(value: str | None) -> str:
    phrase = canonical_clinical_phrase(value)
    return _MEDICATION_SYNONYMS.get(phrase, phrase)


def canonical_investigation_label(attrs: dict[str, Any]) -> str | None:
    for modality in _INVESTIGATION_MODALITIES:
        performed_key = f"{modality.upper()}_Performed"
        results_key = f"{modality.upper()}_Results"
        if attrs.get(performed_key) == "Yes" and attrs.get(results_key):
            result = canonical_clinical_phrase(str(attrs[results_key]))
            if result in _INVESTIGATION_RESULTS:
                return f"{modality} {result}"

    phrase = canonical_clinical_phrase(attrs.get("CUIPhrase"))
    return _canonical_investigation_phrase(phrase)


def normalize_investigation_phrase(value: str | None) -> str:
    phrase = canonical_clinical_phrase(value)
    canonical = _canonical_investigation_phrase(phrase)
    return canonical or phrase


def _canonical_investigation_phrase(phrase: str | None) -> str | None:
    if not phrase:
        return None

    tokens = phrase.split()
    if len(tokens) == 2:
        left, right = tokens
        if left in _INVESTIGATION_MODALITIES and right in _INVESTIGATION_RESULTS:
            return f"{left} {right}"
        if right in _INVESTIGATION_MODALITIES and left in _INVESTIGATION_RESULTS:
            return f"{right} {left}"

    if phrase in _INVESTIGATION_MODALITIES:
        return None

    return None


def is_comorbidity_patient_history(phrase: str | None, attrs: dict[str, Any]) -> bool:
    if not _is_affirmed_high_certainty(attrs):
        return False
    canonical = canonical_comorbidity_label(phrase)
    if not canonical:
        return False
    if canonical in _COMORBIDITY_EXCLUDED_PHRASES:
        return False
    if canonical.startswith(("seizure", "convulsive", "non epileptic")):
        return False
    return True


def canonical_comorbidity_label(value: str | None) -> str:
    return canonical_clinical_phrase(value)


def canonical_birth_history_label(value: str | None) -> str:
    return canonical_clinical_phrase(value)


def canonical_onset_label(value: str | None) -> str:
    return canonical_clinical_phrase(value)


def canonical_epilepsy_cause_label(value: str | None) -> str:
    return canonical_clinical_phrase(value)


def canonical_when_diagnosed_label(value: str | None) -> str:
    return canonical_clinical_phrase(value)


def canonical_seizure_frequency_label(attrs: dict[str, Any]) -> str | None:
    phrase = canonical_clinical_phrase(attrs.get("CUIPhrase"))
    number_of_seizures = attrs.get("NumberOfSeizures")
    frequency_change = attrs.get("FrequencyChange")

    if phrase == "seizure free" or (
        number_of_seizures == "0" and phrase in {"seizure free", "seizure", "seizures"}
    ):
        year = attrs.get("YearDate")
        if year:
            return f"seizure free since {year}"
        return "seizure free"

    if number_of_seizures == "0" and attrs.get("YearDate"):
        return f"seizure free since {attrs['YearDate']}"

    if frequency_change:
        return _FREQUENCY_CHANGE_LABELS.get(
            frequency_change,
            f"frequency {canonical_clinical_phrase(frequency_change)}",
        )

    number_of_time_periods = attrs.get("NumberOfTimePeriods")
    time_period = attrs.get("TimePeriod")
    if number_of_time_periods and time_period:
        count = number_of_seizures or "1"
        return f"{count} per {number_of_time_periods} {canonical_clinical_phrase(time_period)}"

    return None


def infer_prescription_temporality(span_text: str) -> str:
    lower = span_text.lower()
    if any(marker in lower for marker in _CURRENT_RX_MARKERS):
        return "current"
    if any(phrase in lower for phrase in _PREVIOUS_RX_PHRASES):
        return "previous"
    if any(phrase in lower for phrase in _PLANNED_RX_PHRASES):
        return "planned"
    return "current"


def format_medication_temporality_label(medication: str, temporality: str) -> str:
    return f"{medication}|{temporality}"


def collapse_diagnoses_to_most_specific(diagnoses: list[str]) -> tuple[list[str], list[str]]:
    diagnosis_set = set(diagnoses)
    collapsed: list[str] = []

    for diagnosis in diagnoses:
        if any(_has_descendant_in_set(diagnosis, other, diagnosis_set) for other in diagnosis_set):
            collapsed.append(diagnosis)

    return [d for d in diagnoses if d not in set(collapsed)], collapsed


def _has_descendant_in_set(parent: str, candidate: str, diagnosis_set: set[str]) -> bool:
    if parent == candidate:
        return False
    current = candidate
    while current in _DIAGNOSIS_PARENT:
        current = _DIAGNOSIS_PARENT[current]
        if current == parent and candidate in diagnosis_set:
            return True
    return False


def _is_affirmed_high_certainty(attrs: dict[str, Any]) -> bool:
    try:
        certainty = int(attrs.get("Certainty", 0))
    except (TypeError, ValueError):
        certainty = 0
    return attrs.get("Negation") == "Affirmed" and certainty >= MIN_CERTAINTY


def _quality_flags(
    *,
    diagnoses: list[str],
    seizure_types: list[str],
    medications: list[str],
    collapsed: list[str],
) -> list[str]:
    flags: list[str] = []
    if not diagnoses and not seizure_types and not medications:
        flags.append("missing_gold")
    if any(term in _GOLD_NOISE_TERMS for term in seizure_types):
        flags.append("gold_noise")
    if collapsed:
        flags.append("specificity_collapsed")
    return flags


def _split_camel(value: str) -> str:
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result

