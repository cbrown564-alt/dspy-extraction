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

    diagnoses, collapsed = collapse_diagnoses_to_most_specific(_dedupe(raw_diagnoses))
    seizure_types = _dedupe(seizure_types)
    medications = _dedupe(medications)

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

