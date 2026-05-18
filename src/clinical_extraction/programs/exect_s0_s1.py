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
EXECT_S0_S1_PROMPT_VERSION = "exect_s0_s1_field_family_v3_seizure_evidence_policy"
EXECT_S0_S1_FIELD_FAMILIES = (
    "diagnosis",
    "seizure_type",
    "annotated_medication",
)
EXECT_S0_S1_LABEL_POLICY_GUIDANCE = (
    "Return benchmark-facing annotation labels only; do not expand into clinically richer labels.",
    "Diagnosis labels should preserve the explicit audited diagnosis surface after deterministic "
    "canonicalization; do not force all focal, temporal-lobe, symptomatic, refractory, or syndrome "
    "phrases into a five-label diagnosis set unless the scorer has an explicit mapping.",
    "Do not output a diagnosis for a single seizure event unless the note separately states an "
    "established epilepsy diagnosis.",
    "Use the audited seizure-type surface supported by the note. Preserve plural and modifier "
    "surfaces such as focal seizures with altered awareness or occipital lobe seizures when those "
    "are the benchmark-facing labels.",
    "Split fused seizure-type surfaces into audited benchmark labels when the note combines a "
    "lobe-specific type with a broader focal seizure type; for example temporal lobe onset focal "
    "seizures should produce temporal lobe seizure and focal seizures.",
    "Do not infer seizure type from diagnosis alone, and do not add secondary generalisation as a "
    "separate current seizure type unless the note independently names it as current.",
    "Annotated medication means medications in the audited prescription annotation view only; do "
    "not include planned starts, previous trials, taper/stop instructions, or medication history "
    "mentions unless they are also prescription-style annotated medication entries.",
    "Use exact contiguous evidence quotes; omit a value rather than supplying non-contiguous or "
    "unsupported evidence.",
)
EXECT_S0_S1_POLICY_EXAMPLES = (
    {
        "case": "planned_medication_exclusion",
        "note_fragment": "Current anti-epileptic medication: lamotrigine 75mg bd. To start levetiracetam.",
        "benchmark_output": {"annotated_medication": ["lamotrigine"]},
        "policy": "Exclude planned medication starts from the benchmark-facing medication list.",
    },
    {
        "case": "previous_medication_exclusion",
        "note_fragment": "Previously tried carbamazepine. Current treatment is sodium valproate.",
        "benchmark_output": {"annotated_medication": ["sodium valproate"]},
        "policy": "Exclude historical medication mentions from the benchmark-facing medication list.",
    },
    {
        "case": "canonical_seizure_type_granularity",
        "note_fragment": "The events are temporal-lobe-onset focal seizures.",
        "benchmark_output": {"seizure_type": ["temporal lobe seizure", "focal seizures"]},
        "policy": "Split the fused rich phrase into the audited benchmark seizure-type labels.",
    },
    {
        "case": "diagnosis_label_preservation",
        "note_fragment": "Diagnosis: symptomatic structural focal epilepsy.",
        "benchmark_output": {"diagnosis": ["symptomatic structural focal epilepsy"]},
        "policy": "Preserve the audited diagnosis surface rather than forcing a five-label collapse.",
    },
    {
        "case": "plural_seizure_type_preservation",
        "note_fragment": "Seizure type and frequency: focal seizures with altered awareness every 3 weeks.",
        "benchmark_output": {"seizure_type": ["focal seizures with altered awareness"]},
        "policy": "Preserve audited plural seizure-type surfaces when that is the scorer label.",
    },
    {
        "case": "evidence_quote_contiguity",
        "note_fragment": "Seizure type: occipital lobe seizures. Previous medication: lamotrigine.",
        "benchmark_output": {
            "seizure_type": ["occipital lobe seizures"],
            "seizure_type_evidence": ["occipital lobe seizures"],
        },
        "policy": "Evidence must be an exact contiguous quote, not a stitched or ellipsis quote.",
    },
    {
        "case": "single_event_diagnosis_null",
        "note_fragment": "This was a single focal seizure. There is no established epilepsy diagnosis.",
        "benchmark_output": {"diagnosis": []},
        "policy": "Do not convert a single seizure event into an established epilepsy diagnosis.",
    },
)

ALLOWED_DIAGNOSIS_LABELS = frozenset(
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


class ExectS0S1FieldFamilySignature(dspy.Signature):
    """Extract audited ExECT S0/S1 benchmark-facing field families.

    Return only labels directly supported by the note. This is an annotation-policy
    aligned task, not a clinically rich free extraction task.

    Policy:
    - diagnosis: established epilepsy diagnoses only. Preserve the explicit audited
      diagnosis surface after deterministic canonicalization; do not force every focal,
      temporal-lobe, symptomatic, refractory, or syndrome phrase into a five-label set
      unless the scorer has an explicit mapping. Do not infer epilepsy from a single
      seizure event, and do not infer subtype from seizure-type evidence alone.
    - seizure_type: seizure-type labels independently named in the note. Use the
      audited benchmark-facing surface supported by the note, preserving plural and
      modifier forms such as focal seizures with altered awareness or occipital lobe
      seizures when those are the scorer labels. Do not infer seizure type from
      diagnosis alone. Secondary generalisation is not a separate current seizure type
      unless independently named as current.
    - annotated_medication: audited prescription-style medication mentions only. Do
      not include planned starts, previous trials, taper/stop instructions, or medication
      history mentions in the benchmark-facing medication list.
    - evidence lists should align by index with the corresponding value lists and
      contain exact contiguous source quotes where possible.

    Boundary examples:
    - "Current anti-epileptic medication: lamotrigine 75mg bd. To start levetiracetam."
      -> annotated_medication = ["lamotrigine"]; exclude the planned levetiracetam start.
    - "Previously tried carbamazepine. Current treatment is sodium valproate."
      -> annotated_medication = ["sodium valproate"]; exclude previous carbamazepine.
    - "The events are temporal-lobe-onset focal seizures."
      -> seizure_type = ["temporal lobe seizure", "focal seizures"]; split the fused
      rich phrase into audited benchmark labels.
    - "Diagnosis: symptomatic structural focal epilepsy."
      -> diagnosis = ["symptomatic structural focal epilepsy"]; preserve the audited label.
    - "Seizure type and frequency: focal seizures with altered awareness every 3 weeks."
      -> seizure_type = ["focal seizures with altered awareness"]; preserve plural wording.
    - "Seizure type: occipital lobe seizures. Previous medication: lamotrigine."
      -> seizure_type_evidence = ["occipital lobe seizures"]; use exact contiguous quotes.
    - "This was a single focal seizure. There is no established epilepsy diagnosis."
      -> diagnosis = []; do not convert a single event into established epilepsy.
    """

    note_text: str = dspy.InputField(desc="Synthetic epilepsy clinic letter text")
    diagnosis: list[str] = dspy.OutputField(
        desc=(
            "Benchmark-facing epilepsy diagnosis labels only. Preserve the explicit audited "
            "diagnosis surface after deterministic canonicalization; use [] for single "
            "seizure events without established epilepsy."
        )
    )
    diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each diagnosis label, aligned by index."
    )
    seizure_type: list[str] = dspy.OutputField(
        desc=(
            "Benchmark-facing seizure-type labels explicitly named in the note. "
            "Preserve audited plural and modifier surfaces when supported; do not infer "
            "these from diagnosis alone."
        )
    )
    seizure_type_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each seizure-type label, aligned by index."
    )
    annotated_medication: list[str] = dspy.OutputField(
        desc=(
            "Audited prescription-style anti-seizure medication names. Exclude planned, "
            "previous, taper/stop, and medication-history-only mentions."
        )
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
        evidence_text = _evidence_at(evidence_values, index)
        for normalized, bridge_flags in _benchmark_values(field_name, raw_value):
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            quality_flags = _quality_flags(
                field_name=field_name,
                normalized_value=normalized,
                collapsed_values=collapsed_values,
                evidence_text=evidence_text,
            )
            values.append(
                ExtractedValue(
                    field_name=field_name,
                    raw_value=raw_value,
                    normalized_value=normalized,
                    evidence=_evidence_spans(record, evidence_text),
                    temporality="not_applicable",
                    negation="affirmed",
                    confidence=None,
                    quality_flags=[*quality_flags, *bridge_flags],
                )
            )
    return values


def _benchmark_values(field_name: str, value: str) -> list[tuple[str, list[str]]]:
    normalized = _normalize_value(field_name, value)
    if field_name == "seizure_type":
        split_values = _split_fused_seizure_type(normalized)
        if split_values is not None:
            return [
                (split_value, ["benchmark_bridge:fused_seizure_type_split"])
                for split_value in split_values
            ]
    return [(normalized, [])]


def _split_fused_seizure_type(normalized: str) -> list[str] | None:
    if normalized in {
        "temporal lobe onset focal seizures",
        "temporal lobe focal seizures",
        "temporal onset focal seizures",
    }:
        return ["temporal lobe seizure", "focal seizures"]
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
