"""ExECT S0/S1 field-family DSPy program."""
from __future__ import annotations

from collections.abc import Callable
from typing import Optional

import dspy

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
    collapse_diagnoses_to_most_specific,
)
from clinical_extraction.runs import RunMetadata
from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExectGoldDocument,
    ExtractedValue,
    PredictionSet,
)

EXECT_DATASET = "exect_v2"
EXECT_S0_S1_SCHEMA_LEVEL = "exect_s0_s1_field_family"
EXECT_S0_S1_VARIANT = "exect_s0_s1_field_family_single_pass"
EXECT_S0_S1_SCORER = "exect_field_family_deterministic_v1"
EXECT_S0_S1_PROMPT_VERSION = "exect_s0_s1_field_family_v1"
EXECT_S0_S1_FIELD_FAMILIES = (
    "diagnosis",
    "seizure_type",
    "annotated_medication",
)

ALLOWED_DIAGNOSIS_LABELS = frozenset(
    {
        "epilepsy",
        "focal epilepsy",
        "generalized epilepsy",
        "juvenile myoclonic epilepsy",
        "status epilepticus",
    }
)


class ExectS0S1FieldFamilySignature(dspy.Signature):
    """Extract audited ExECT S0/S1 benchmark-facing field families.

    Return only labels directly supported by the note. This is an annotation-policy
    aligned task, not a clinically rich free extraction task.

    Policy:
    - diagnosis: established epilepsy diagnoses only. Do not infer epilepsy from a
      single seizure event, and do not infer subtype from seizure-type evidence alone.
    - seizure_type: seizure-type labels independently named in the note. Do not infer
      seizure type from diagnosis alone.
    - annotated_medication: prescription-style medication mentions only. Do not emit
      current/planned/historical status as a benchmark-facing label.
    - evidence lists should align by index with the corresponding value lists and
      contain exact contiguous source quotes where possible.
    """

    note_text: str = dspy.InputField(desc="Synthetic epilepsy clinic letter text")
    diagnosis: list[str] = dspy.OutputField(
        desc=(
            "Benchmark-facing epilepsy diagnosis labels. Allowed examples include "
            "epilepsy, focal epilepsy, generalized epilepsy, juvenile myoclonic epilepsy."
        )
    )
    diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each diagnosis label, aligned by index."
    )
    seizure_type: list[str] = dspy.OutputField(
        desc=(
            "Benchmark-facing seizure-type labels explicitly named in the note. "
            "Do not infer these from diagnosis alone."
        )
    )
    seizure_type_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each seizure-type label, aligned by index."
    )
    annotated_medication: list[str] = dspy.OutputField(
        desc="Prescription-style anti-seizure medication names explicitly mentioned."
    )
    annotated_medication_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each medication label, aligned by index."
    )


class ExectS0S1FieldFamilyModule(dspy.Module):
    """Single-pass ExECT S0/S1 field-family extractor."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS0S1FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


def make_exect_s0_s1_dspy_examples(
    records: list[ExectGoldDocument],
) -> list[dspy.Example]:
    """Convert audited ExECT gold documents into DSPy examples."""
    return [
        dspy.Example(
            note_text=record.text,
            diagnosis=record.diagnoses,
            seizure_type=record.seizure_types,
            annotated_medication=record.current_medications,
        ).with_inputs("note_text")
        for record in records
    ]


def predict_exect_records(
    module: ExectS0S1FieldFamilyModule,
    records: list[ExectGoldDocument],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> PredictionSet:
    """Run ``module`` on ExECT records and return a shared ``PredictionSet``."""
    predictions = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        predictions.append(_predict_record(module, record))
        if progress_callback is not None:
            progress_callback(index, total, record.document_id)
    return PredictionSet(
        dataset=EXECT_DATASET,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        predictions=predictions,
        metadata={
            "program_variant": EXECT_S0_S1_VARIANT,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "scorer_mode": EXECT_S0_S1_SCORER,
        },
    )


def _predict_record(
    module: ExectS0S1FieldFamilyModule,
    record: ExectGoldDocument,
) -> DocumentPrediction:
    pred = module(note_text=record.text)
    values: list[ExtractedValue] = []

    diagnoses, collapsed = _normalize_diagnoses(_as_list(getattr(pred, "diagnosis", [])))
    diagnosis_evidence = _as_list(getattr(pred, "diagnosis_evidence", []))
    values.extend(
        _values_for_family(
            record=record,
            field_name="diagnosis",
            raw_values=diagnoses,
            evidence_values=diagnosis_evidence,
            collapsed_values=collapsed,
        )
    )
    values.extend(
        _values_for_family(
            record=record,
            field_name="seizure_type",
            raw_values=_as_list(getattr(pred, "seizure_type", [])),
            evidence_values=_as_list(getattr(pred, "seizure_type_evidence", [])),
        )
    )
    values.extend(
        _values_for_family(
            record=record,
            field_name="annotated_medication",
            raw_values=_as_list(getattr(pred, "annotated_medication", [])),
            evidence_values=_as_list(getattr(pred, "annotated_medication_evidence", [])),
        )
    )

    return DocumentPrediction(
        document_id=record.document_id,
        dataset=EXECT_DATASET,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        values=values,
        quality_flags=record.quality_flags,
        metadata={"program_variant": EXECT_S0_S1_VARIANT},
    )


def _normalize_diagnoses(raw_values: list[str]) -> tuple[list[str], list[str]]:
    normalized = _dedupe(
        [canonical_clinical_phrase(value) for value in raw_values if value.strip()]
    )
    kept, collapsed = collapse_diagnoses_to_most_specific(normalized)
    kept_set = set(kept)
    return [value for value in raw_values if canonical_clinical_phrase(value) in kept_set], collapsed


def _values_for_family(
    *,
    record: ExectGoldDocument,
    field_name: str,
    raw_values: list[str],
    evidence_values: list[str],
    collapsed_values: list[str] | None = None,
) -> list[ExtractedValue]:
    values: list[ExtractedValue] = []
    seen: set[str] = set()
    collapsed_values = collapsed_values or []

    for index, raw_value in enumerate(raw_values):
        normalized = _normalize_value(field_name, raw_value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        quality_flags = _quality_flags(
            field_name=field_name,
            normalized_value=normalized,
            collapsed_values=collapsed_values,
            evidence_text=_evidence_at(evidence_values, index),
        )
        values.append(
            ExtractedValue(
                field_name=field_name,
                raw_value=raw_value,
                normalized_value=normalized,
                evidence=_evidence_spans(
                    record,
                    _evidence_at(evidence_values, index),
                ),
                temporality="not_applicable",
                negation="affirmed",
                confidence=None,
                quality_flags=quality_flags,
            )
        )
    return values


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
) -> list[EvidenceSpan]:
    if not evidence_text:
        return []
    start = record.text.find(evidence_text)
    if start == -1:
        return [EvidenceSpan(text=evidence_text, document_id=record.document_id)]
    return [
        EvidenceSpan(
            text=evidence_text,
            start=start,
            end=start + len(evidence_text),
            document_id=record.document_id,
        )
    ]


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


def exect_s0_s1_run_metadata(
    run_id: str,
    split_name: str,
    model_provider: str,
    model_name: str,
    *,
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    extra: dict | None = None,
) -> RunMetadata:
    """Build run metadata for an ExECT S0/S1 field-family run."""
    return RunMetadata(
        run_id=run_id,
        dataset=EXECT_DATASET,
        split_name=split_name,
        model_provider=model_provider,
        model_name=model_name,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        program_variant=EXECT_S0_S1_VARIANT,
        scorer_mode=EXECT_S0_S1_SCORER,
        metric_caveats=[
            "These are partial ExECT S0/S1 diagnostics, not published ExECTv2 benchmark reproduction.",
            "Benchmark-facing fields are limited to diagnosis, seizure type, and annotated medications.",
            "Medication temporality is intentionally not benchmark-facing in this baseline.",
            "Evidence quote support is diagnostic and should be reported separately from label metrics.",
        ],
        metadata={
            "prompt_version": prompt_version,
            **(extra or {}),
        },
    )
