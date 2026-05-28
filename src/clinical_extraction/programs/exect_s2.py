"""ExECT S2 field-family DSPy program (S1 + investigations + comorbidities)."""
from __future__ import annotations

import re
from collections.abc import Callable

import dspy

from clinical_extraction.datasets.exect import (
    canonical_comorbidity_label,
    normalize_investigation_phrase,
)
from clinical_extraction.evaluation.exect import EXECT_S2_SCORER
from clinical_extraction.exect.medication_primitives import (
    recover_exect_annotated_medication_non_asm_brand_alias_guard,
)
from clinical_extraction.exect.s0_s1.constants import (
    EXECT_DATASET,
    EXECT_S0_S1_LABEL_POLICY_GUIDANCE,
    EXECT_S0_S1_PROMPT_VERSION,
)
from clinical_extraction.exect.s0_s1.prediction_artifacts import (
    _as_list,
    _augment_current_prescription_medications,
    _augment_diagnosis_co_lists,
    _evidence_at,
    _evidence_spans,
    _filter_diagnosis_for_seizure_descriptor_header,
    _normalize_diagnoses,
    _seizure_type_values_for_record,
    _values_for_family,
)
from clinical_extraction.runs import RunMetadata
from clinical_extraction.schemas import (
    DocumentPrediction,
    ExectGoldDocument,
    ExtractedValue,
    PredictionSet,
)

EXECT_S2_SCHEMA_LEVEL = "exect_s2_field_family"
EXECT_S2_VARIANT = "exect_s2_field_family_single_pass"
EXECT_S2_COMORBIDITY_C0_VARIANT = "exect_s2_field_family_comorbidity_c0_single_pass"
EXECT_S2_COMORBIDITY_C0_C1_VARIANT = (
    "exect_s2_field_family_comorbidity_c0_c1_single_pass"
)
EXECT_S2_INV_GUARD_I0_VARIANT = "exect_s2_field_family_inv_guard_i0_single_pass"
EXECT_S2_CLEAN_LADDER_V1_VARIANT = "exect_s2_field_family_clean_ladder_v1_single_pass"
INVESTIGATION_GUARD_DROP_ECG_TIER = "inv_guard_drop_ecg_v1"
_EXECT_S2_PROGRAM_VARIANTS = frozenset(
    {
        EXECT_S2_VARIANT,
        EXECT_S2_COMORBIDITY_C0_VARIANT,
        EXECT_S2_COMORBIDITY_C0_C1_VARIANT,
        EXECT_S2_INV_GUARD_I0_VARIANT,
        EXECT_S2_CLEAN_LADDER_V1_VARIANT,
    }
)
EXECT_S2_PROMPT_VERSION = "exect_s2_field_family_v1_3_label_policy"
EXECT_S2_FIELD_FAMILIES = (
    "diagnosis",
    "seizure_type",
    "annotated_medication",
    "investigation",
    "comorbidity",
)
EXECT_S2_S1_FIELD_PRIORITY_GUIDANCE = (
    "This is a multi-family pass: extract frozen S1 diagnosis, seizure-type, and medication "
    "surfaces with the same benchmark-facing label policy as v4.10 before adding "
    "investigation or comorbidity labels.",
    "Do not modernize, shorten, or ILAE-relabel S1 seizure surfaces because S2 fields are present.",
    "Preserve plural seizure wording when the note uses plural (for example generalized tonic "
    "clonic seizures, myoclonic seizures).",
    "When the note says altered awareness, use altered awareness; do not substitute impaired "
    "awareness or focal impaired awareness seizure.",
    "Do not emit focal aware seizure, focal impaired awareness seizure, or similar ILAE-only "
    "labels when the note uses legacy benchmark surfaces such as temporal lobe seizure, "
    "occipital lobe seizures, or focal seizures with altered awareness.",
    "Do not add absence seizures unless the note explicitly names absence events in the "
    "seizure-type context.",
    "When the note says focal to bilateral convulsive seizures, preserve convulsive wording; "
    "do not replace with tonic clonic.",
    "Do not emit bare focal when the note names focal seizure or focal seizures.",
    "Annotated medication is prescription-style anti-seizure medication only; do not add "
    "comorbidity drugs (for example aspirin, insulin, omeprazole) to annotated_medication.",
)
EXECT_S2_LABEL_POLICY_GUIDANCE = (
    *EXECT_S2_S1_FIELD_PRIORITY_GUIDANCE,
    *EXECT_S0_S1_LABEL_POLICY_GUIDANCE,
    "Investigation labels are benchmark-facing modality+result pairs only: eeg/mri/ct "
    "with normal, abnormal, or unknown. Emit separate labels for each performed "
    "investigation with a stated result in the note.",
    "Do not emit investigation labels with unknown unless the note explicitly states the "
    "result is unknown; do not infer planned or unperformed imaging.",
    "Preserve the audited result surface from the note (for example eeg normal stays normal).",
    "Comorbidity labels are atomized non-epilepsy, non-seizure-history conditions explicitly "
    "named in the note. Prefer separate labels for separate history phrases (for example cva, "
    "hemiparesis, infarct) rather than umbrella terms such as stroke when components are named.",
    "Use learning difficulties without mild/moderate/severity modifiers unless the note uses "
    "that exact modifier as the condition name.",
    "Use migraine not episodic migraine; use measles not childhood measles when the note "
    "names measles in patient history.",
    "Use trisomy not trisomy 21 when the audited PatientHistory surface is trisomy.",
    "When the note names meningioma resection or meningioma surgery, emit meningioma surgery "
    "not meningioma alone.",
    "When stroke components are named separately, emit stroke as its own label in addition "
    "to atomized cva, hemiparesis, or infarct when each is affirmed.",
    "Scan past history, previous, and secondary diagnosis lines for affirmed comorbidities "
    "the model omitted (for example meningitis, brain atrophy, arachnoid cyst, cortical dysplasia).",
    "Preserve plural comorbidity surfaces when the note uses plural (for example migraines).",
    "Do not emit seizure events, febrile seizures, dissociative seizures, or other "
    "seizure-history phrases as comorbidities.",
    "Do not emit jerk, jerks, or myoclonic jerks as comorbidities when they describe "
    "seizure types or epilepsy events; family history of epilepsy is not a comorbidity label.",
    "Do not duplicate epilepsy diagnoses or seizure types in the comorbidity field.",
    "When no supported investigation or comorbidity is present, return empty lists rather "
    "than guessing.",
)
EXECT_S2_POLICY_EXAMPLES = (
    {
        "case": "investigation_modality_result",
        "note_fragment": "Investigations: MRI, right parietal focal cortical dysplasia",
        "benchmark_output": {"investigation": ["mri abnormal"]},
        "policy": "Emit modality+result benchmark labels for performed investigations.",
    },
    {
        "case": "comorbidity_excludes_seizure_history",
        "note_fragment": "Comorbidities: learning disabilities. Seizure history: febrile seizures.",
        "benchmark_output": {"comorbidity": ["learning disabilities"]},
        "policy": "Exclude seizure-history phrases from comorbidity outputs.",
    },
    {
        "case": "comorbidity_diabetes_header",
        "note_fragment": "Diagnosis: epilepsy. Comorbidities: Type 1 diabetes.",
        "benchmark_output": {"comorbidity": ["type 1 diabetes"]},
        "policy": "Emit affirmed non-seizure comorbidities from diagnosis or history sections.",
    },
    {
        "case": "s2_seizure_altered_awareness_plural",
        "note_fragment": (
            "Seizure type and frequency: focal seizures with altered awareness every 3 weeks."
        ),
        "benchmark_output": {"seizure_type": ["focal seizures with altered awareness"]},
        "policy": "Preserve altered awareness and plural seizures in the S1 seizure slot.",
    },
    {
        "case": "s2_seizure_no_absence_without_note",
        "note_fragment": "Seizure type: generalized tonic clonic seizures.",
        "benchmark_output": {"seizure_type": ["generalized tonic clonic seizures"]},
        "policy": "Do not add absence seizures when the note only names GTCS.",
    },
    {
        "case": "comorbidity_stroke_atomized",
        "note_fragment": "History: CVA with right hemiparesis. MRI: prior infarct.",
        "benchmark_output": {"comorbidity": ["cva", "hemiparesis", "infarct"]},
        "policy": "Atomize stroke components when the note names them separately.",
    },
    {
        "case": "investigation_no_unknown_without_note",
        "note_fragment": "Investigations: EEG normal.",
        "benchmark_output": {"investigation": ["eeg normal"]},
        "policy": "Do not emit mri unknown or eeg unknown without explicit unknown wording.",
    },
    {
        "case": "comorbidity_meningioma_surgery",
        "note_fragment": "Previous meningioma resection 3rd January 2005.",
        "benchmark_output": {"comorbidity": ["meningioma surgery"]},
        "policy": "Emit meningioma surgery when resection or surgery is named with meningioma.",
    },
    {
        "case": "comorbidity_affirmed_history_recall",
        "note_fragment": (
            "Diagnosis: symptomatic structural epilepsy secondary probably caused by "
            "early life meningitis. Investigations: MRI generalised brain atrophy."
        ),
        "benchmark_output": {
            "comorbidity": ["meningitis", "brain atrophy"],
        },
        "policy": "Emit affirmed history phrases from diagnosis and investigation context.",
    },
    {
        "case": "comorbidity_excludes_myoclonic_jerks",
        "note_fragment": "Absences and myoclonic jerks since teenage years, JME.",
        "benchmark_output": {"comorbidity": []},
        "policy": "Do not emit jerk or jerks as comorbidities when they are seizure descriptors.",
    },
)

_ILAE_SEIZURE_SURFACES = (
    "focal aware seizure",
    "focal aware seizures",
    "focal impaired awareness seizure",
    "focal impaired awareness seizures",
    "focal seizures with impaired awareness",
)


class ExectS2FieldFamilySignature(dspy.Signature):
    """Extract audited ExECT S2 benchmark-facing field families.

    Multi-family pass: apply frozen S1 v4.10 label policy for diagnosis, seizure type,
    and annotated medication first, then add investigation and comorbidity.

    S1 seizure-type priority (do not change because S2 fields are present):
    - Preserve plural audited surfaces (generalized tonic clonic seizures, myoclonic seizures).
    - Use altered awareness when the note says altered awareness; never impaired awareness.
    - Do not emit ILAE-only labels (focal aware seizure) when the note uses temporal lobe,
      occipital lobe, or altered-awareness benchmark surfaces.
    - Do not add absence seizures unless absence is explicitly named in seizure context.
    - Preserve convulsive wording for focal to bilateral convulsive seizures.
    - Medication: current prescription ASM only; exclude comorbidity drugs and planned starts.

    S2 families:
    - investigation: performed EEG/MRI/CT with stated results only (eeg normal, mri abnormal).
      Do not emit unknown unless the note says unknown.
    - comorbidity: atomized affirmed non-seizure history phrases; prefer cva/hemiparesis/infarct
      plus stroke when each is affirmed; meningioma surgery for resection; migraine not episodic
      migraine; trisomy not trisomy 21; recall affirmed history the model omitted; exclude jerk
      and family history of epilepsy unless the audited surface is a non-seizure comorbidity.

    Boundary examples:
    - "Seizure type: focal seizures with altered awareness." ->
      seizure_type = ["focal seizures with altered awareness"] (not impaired awareness).
    - "Seizure type: generalized tonic clonic seizures." ->
      seizure_type = ["generalized tonic clonic seizures"]; do not add absence seizures.
    - "History: CVA with right hemiparesis and prior infarct." ->
      comorbidity = ["cva", "hemiparesis", "infarct"] (not stroke alone).
    - "Investigations: EEG normal." -> investigation = ["eeg normal"]; no mri unknown.
    - evidence lists align by index with the corresponding value lists.
    """

    note_text: str = dspy.InputField(desc="Synthetic epilepsy clinic letter text")
    diagnosis: list[str] = dspy.OutputField(
        desc="Benchmark-facing epilepsy diagnosis labels only."
    )
    diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each diagnosis label, aligned by index."
    )
    seizure_type: list[str] = dspy.OutputField(
        desc=(
            "Benchmark-facing seizure-type labels explicitly named in the note. "
            "Preserve plural and legacy audited surfaces (altered awareness, convulsive, "
            "temporal/occipital lobe); do not ILAE-modernize or add absence without note support."
        )
    )
    seizure_type_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each seizure-type label, aligned by index."
    )
    annotated_medication: list[str] = dspy.OutputField(
        desc=(
            "Audited prescription-style anti-seizure medication names only. "
            "Exclude non-ASM comorbidity drugs and planned/previous mentions."
        )
    )
    annotated_medication_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each medication label, aligned by index."
    )
    investigation: list[str] = dspy.OutputField(
        desc=(
            "Performed investigation results as modality+result labels "
            "(eeg/mri/ct + normal/abnormal/unknown)."
        )
    )
    investigation_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each investigation label, aligned by index."
    )
    comorbidity: list[str] = dspy.OutputField(
        desc=(
            "Atomized non-seizure comorbid conditions explicitly named in the note. "
            "Prefer separate history phrases over umbrella clinical terms."
        )
    )
    comorbidity_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each comorbidity label, aligned by index."
    )


class ExectS2FieldFamilyModule(dspy.Module):
    """Single-pass ExECT S2 field-family extractor."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS2FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


def ladder_investigation_guard_bridge_tiers() -> frozenset[str]:
    """I0 ECG drop guard — default on S3/S4 investigation recovery (regression guard)."""
    return frozenset({INVESTIGATION_GUARD_DROP_ECG_TIER})


def _s2_bridge_tiers(program_variant: str) -> frozenset[str]:
    tiers: set[str] = set()
    if program_variant in {
        EXECT_S2_COMORBIDITY_C0_VARIANT,
        EXECT_S2_COMORBIDITY_C0_C1_VARIANT,
    }:
        tiers.add("comorbidity_atomization_tbi_v1")
    if program_variant == EXECT_S2_COMORBIDITY_C0_C1_VARIANT:
        tiers.add("comorbidity_surface_plural_v1")
    if program_variant == EXECT_S2_INV_GUARD_I0_VARIANT:
        tiers.add(INVESTIGATION_GUARD_DROP_ECG_TIER)
    if program_variant == EXECT_S2_CLEAN_LADDER_V1_VARIANT:
        tiers.update(
            {
                "comorbidity_atomization_tbi_v1",
                "comorbidity_surface_plural_v1",
                INVESTIGATION_GUARD_DROP_ECG_TIER,
                "annotated_medication_non_asm_brand_alias_v1",
            }
        )
    return frozenset(tiers)


def build_exect_s2_module(program_variant: str = EXECT_S2_VARIANT) -> dspy.Module:
    if program_variant in _EXECT_S2_PROGRAM_VARIANTS:
        return ExectS2FieldFamilyModule()
    raise ValueError(f"Unsupported ExECT S2 program variant: {program_variant!r}")


def predict_exect_s2_records(
    module: dspy.Module,
    records: list[ExectGoldDocument],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = EXECT_S2_PROMPT_VERSION,
    program_variant: str = EXECT_S2_VARIANT,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> PredictionSet:
    predictions = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        predictions.append(_predict_s2_record(module, record, program_variant=program_variant))
        if progress_callback is not None:
            progress_callback(index, total, record.document_id)
    return PredictionSet(
        dataset=EXECT_DATASET,
        schema_level=EXECT_S2_SCHEMA_LEVEL,
        predictions=predictions,
        metadata={
            "program_variant": program_variant,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "scorer_mode": EXECT_S2_SCORER,
        },
    )


def _predict_s2_record(
    module: dspy.Module,
    record: ExectGoldDocument,
    *,
    program_variant: str,
) -> DocumentPrediction:
    pred = module(note_text=record.text)
    values: list[ExtractedValue] = []

    diagnosis_inputs = _as_list(getattr(pred, "diagnosis", []))
    diagnosis_inputs, diagnosis_header_flags = _filter_diagnosis_for_seizure_descriptor_header(
        diagnosis_inputs,
        record.text,
    )
    diagnosis_raw, diagnosis_augmented, specificity_collapse_augmented = _augment_diagnosis_co_lists(
        diagnosis_inputs,
        record.text,
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
    medication_raw, medication_evidence, medication_augmented = _augment_current_prescription_medications(
        _as_list(getattr(pred, "annotated_medication", [])),
        _as_list(getattr(pred, "annotated_medication_evidence", [])),
        record.text,
    )
    medication_raw, medication_guard_flags = _recover_s2_annotated_medication_raw_values(
        medication_raw,
        medication_evidence,
        record.text,
        bridge_tiers=_s2_bridge_tiers(program_variant),
    )
    values.extend(
        _values_for_family(
            record=record,
            field_name="annotated_medication",
            raw_values=medication_raw,
            evidence_values=medication_evidence,
            augmented_values=medication_augmented,
            extra_quality_flags=medication_guard_flags,
        )
    )
    investigation_raw, _ = _recover_s2_investigation_raw_values(
        _as_list(getattr(pred, "investigation", [])),
        record.text,
        bridge_tiers=_s2_bridge_tiers(program_variant),
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
    comorbidity_raw, _ = _recover_s2_comorbidity_raw_values(
        _as_list(getattr(pred, "comorbidity", [])),
        record.text,
        bridge_tiers=_s2_bridge_tiers(program_variant),
    )
    comorbidity_raw, _ = _augment_s2_comorbidity_from_note(comorbidity_raw, record.text)
    values.extend(
        _s2_values_for_family(
            record=record,
            field_name="comorbidity",
            raw_values=comorbidity_raw,
            evidence_values=_as_list(getattr(pred, "comorbidity_evidence", [])),
            normalize=canonical_comorbidity_label,
        )
    )

    return DocumentPrediction(
        document_id=record.document_id,
        dataset=EXECT_DATASET,
        schema_level=EXECT_S2_SCHEMA_LEVEL,
        values=values,
        quality_flags=record.quality_flags,
        metadata={"program_variant": program_variant},
    )


def _s2_values_for_family(
    *,
    record: ExectGoldDocument,
    field_name: str,
    raw_values: list[str],
    evidence_values: list[str],
    normalize: Callable[[str], str],
) -> list[ExtractedValue]:
    values: list[ExtractedValue] = []
    seen: set[str] = set()

    for index, raw_value in enumerate(raw_values):
        if not raw_value.strip():
            continue
        normalized = normalize(raw_value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        evidence_text = _evidence_at(evidence_values, index)
        evidence_spans, evidence_flags = _evidence_spans(record, evidence_text)
        values.append(
            ExtractedValue(
                field_name=field_name,
                raw_value=raw_value.strip(),
                normalized_value=normalized,
                evidence=evidence_spans,
                quality_flags=evidence_flags,
            )
        )
    return values


def _recover_s2_annotated_medication_raw_values(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
    *,
    bridge_tiers: frozenset[str] | None = None,
) -> tuple[list[str], list[str]]:
    tiers = bridge_tiers or frozenset()
    if "annotated_medication_non_asm_brand_alias_v1" not in tiers:
        return raw_values, []
    recovered, flags = recover_exect_annotated_medication_non_asm_brand_alias_guard(
        raw_values,
        evidence_values,
        note_text,
    )
    return recovered, [f"s2_bridge:{flag}" for flag in flags]


def _normalize_investigation_surface(value: str) -> str:
    return normalize_investigation_phrase(value)


def _recover_s2_seizure_raw_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    flags: list[str] = []
    note = note_text.lower()
    note_has_absence = bool(re.search(r"\babsences?\b", note_text, re.IGNORECASE))
    recovered: list[str] = []

    for raw in raw_values:
        if not raw.strip():
            continue
        value = raw.strip()
        lower = value.lower()

        if not note_has_absence and re.search(r"\babsences?\b", value, re.IGNORECASE):
            flags.append("s2_bridge:absence_without_note_support_removed")
            continue

        if "impaired awareness" in lower and "altered awareness" in note:
            value = re.sub(
                r"impaired\s+awareness",
                "altered awareness",
                value,
                flags=re.IGNORECASE,
            )
            flags.append("s2_bridge:altered_awareness_restored")
            lower = value.lower()

        if any(surface in lower for surface in _ILAE_SEIZURE_SURFACES):
            if not any(surface in note for surface in _ILAE_SEIZURE_SURFACES):
                legacy_markers = (
                    "altered awareness",
                    "temporal lobe",
                    "occipital lobe",
                    "convulsive",
                )
                if any(marker in note for marker in legacy_markers):
                    flags.append("s2_bridge:ilae_surface_removed")
                    continue

        if "tonic clonic" in lower and "focal to bilateral" in lower and "convulsive" in note:
            value = re.sub(r"tonic[- ]clonic", "convulsive", value, flags=re.IGNORECASE)
            flags.append("s2_bridge:convulsive_modifier_restored")

        if lower.rstrip(".") in {
            "generalized tonic clonic seizure",
            "generalised tonic clonic seizure",
        } and re.search(
            r"generali[sz]ed tonic clonic seizures",
            note_text,
            re.IGNORECASE,
        ):
            value = "generalized tonic clonic seizures"
            flags.append("s2_bridge:gtcs_plural_restored")

        if lower == "myoclonic seizure" and re.search(
            r"\bmyoclonic seizures\b",
            note_text,
            re.IGNORECASE,
        ):
            value = "myoclonic seizures"
            flags.append("s2_bridge:myoclonic_plural_restored")

        if lower == "focal":
            if re.search(r"\bfocal seizures\b", note_text, re.IGNORECASE):
                value = "focal seizures"
                flags.append("s2_bridge:focal_specificity_restored")
            elif re.search(r"\bfocal seizure\b", note_text, re.IGNORECASE):
                value = "focal seizure"
                flags.append("s2_bridge:focal_specificity_restored")

        recovered.append(value)

    return recovered, flags


_COMORBIDITY_SEIZURE_HISTORY_SURFACES = {
    "febrile seizure",
    "febrile seizures",
    "seizure",
    "seizures",
    "convulsive seizure",
    "convulsive seizures",
    "jerks",
    "myoclonic jerks",
    "family history of epilepsy",
}

_COMORBIDITY_NOTE_RECALL_PATTERNS: tuple[tuple[str, str], ...] = (
    ("meningitis", r"\bmeningitis\b"),
    ("brain atrophy", r"\b(?:brain atrophy|generalised brain atrophy|premature atrophy)\b"),
    ("arachnoid cyst", r"\barachnoid cyst\b"),
    ("cortical dysplasia", r"\bcortical dysplasia\b"),
    ("measles", r"\bmeasles\b"),
    ("migraines", r"\bmigraines\b"),
    ("migraine", r"\bmigraine\b"),
)


def _recover_s2_comorbidity_raw_values(
    raw_values: list[str],
    note_text: str,
    *,
    bridge_tiers: frozenset[str] | None = None,
) -> tuple[list[str], list[str]]:
    flags: list[str] = []
    note = note_text.lower()
    recovered: list[str] = []
    tiers = bridge_tiers or frozenset()

    for raw in raw_values:
        if not raw.strip():
            continue
        value, value_flags = _normalize_s2_comorbidity_candidate(raw.strip(), note_text)
        flags.extend(value_flags)
        canonical = canonical_comorbidity_label(value)

        if "comorbidity_surface_plural_v1" in tiers:
            value, plural_flags = _apply_comorbidity_surface_plural_bridge(
                value,
                canonical,
                note_text,
            )
            flags.extend(plural_flags)
            canonical = canonical_comorbidity_label(value)

        if canonical in _COMORBIDITY_SEIZURE_HISTORY_SURFACES:
            flags.append("s2_bridge:seizure_history_comorbidity_removed")
            continue

        if canonical in {"jerk", "myoclonic jerk"} and not _is_benchmark_comorbidity_jerk(
            note_text
        ):
            flags.append("s2_bridge:seizure_descriptor_jerk_removed")
            continue

        if re.match(r"^(mild|moderate|severe)\s+learning disabilit", canonical):
            value = "learning disabilities"
            flags.append("s2_bridge:learning_disabilities_modifier_stripped")
        elif re.match(r"^(mild|moderate|severe)\s+learning difficult", canonical):
            value = "learning difficulties"
            flags.append("s2_bridge:learning_difficulties_modifier_stripped")

        if "comorbidity_atomization_tbi_v1" in tiers and canonical in {
            "traumatic brain injury",
            "tbi",
        }:
            atoms: list[str] = []
            if re.search(r"\btraumatic\b", note_text, re.IGNORECASE):
                atoms.append("traumatic")
            if re.search(
                r"\b(?:brain injury|head injury|tbi)\b",
                note_text,
                re.IGNORECASE,
            ):
                atoms.append("brain injury")
            if atoms:
                recovered.extend(atoms)
                flags.append("s2_bridge:tbi_atomized")
                continue

        if canonical == "stroke":
            atoms: list[str] = []
            if re.search(r"\bcva\b|cerebrovascular", note_text, re.IGNORECASE):
                atoms.append("cva")
            if "hemiparesis" in note:
                atoms.append("hemiparesis")
            if "infarct" in note:
                atoms.append("infarct")
            if atoms:
                recovered.extend(atoms)
                if re.search(r"\bstroke\b", note_text, re.IGNORECASE):
                    recovered.append("stroke")
                flags.append("s2_bridge:stroke_atomized")
                continue

        if canonical == "migraine" and re.search(r"\bmigraines\b", note_text, re.IGNORECASE):
            value = "migraines"
            flags.append("s2_bridge:migraine_plural_restored")

        recovered.append(value)

    return recovered, flags


def _normalize_s2_comorbidity_candidate(
    value: str,
    note_text: str,
) -> tuple[str, list[str]]:
    flags: list[str] = []
    canonical = canonical_comorbidity_label(value)

    if canonical in {"meningioma resection", "meningioma"} and re.search(
        r"\bmeningioma\b.{0,40}\b(?:resection|surgery)\b|\b(?:resection|surgery)\b.{0,40}\bmeningioma\b",
        note_text,
        re.IGNORECASE,
    ):
        return "meningioma surgery", ["s2_bridge:meningioma_surgery_restored"]

    if canonical in {"episodic migraine", "episodic migraines"}:
        return "migraine", ["s2_bridge:episodic_migraine_normalized"]

    if canonical == "childhood measles":
        return "measles", ["s2_bridge:childhood_measles_normalized"]

    if canonical == "trisomy 21":
        return "trisomy", ["s2_bridge:trisomy_specificity_restored"]

    return value, flags


def _apply_comorbidity_surface_plural_bridge(
    value: str,
    canonical: str,
    note_text: str,
) -> tuple[str, list[str]]:
    flags: list[str] = []
    if "haemorrhage" in canonical:
        value = canonical.replace("haemorrhage", "hemorrhage")
        flags.append("s2_bridge:haemorrhage_spelling_normalized")
    if canonical == "infarcts":
        value = "infarct"
        flags.append("s2_bridge:infarct_plural_normalized")
    return value, flags


def _is_benchmark_comorbidity_jerk(note_text: str) -> bool:
    """True when jerk is an audited non-seizure comorbidity surface (rare)."""
    if re.search(
        r"\b(?:get|gets|got|continue(?:s)?\s+to\s+get)\s+jerks\b",
        note_text,
        re.IGNORECASE,
    ):
        return True
    return False


def _is_seizure_descriptor_jerk_context(note_text: str) -> bool:
    note = note_text.lower()
    if re.search(r"\bmyoclonic\s+jerks?\b", note):
        return True
    if re.search(r"\babsences?\s+and\s+jerks?\b", note):
        return True
    if re.search(r"\bjme\b", note) and re.search(r"\bjerks?\b", note):
        return True
    if re.search(r"\bseizure type\b", note) and re.search(r"\bjerks?\b", note):
        return True
    if re.search(r"\bmyoclonic\s+jerks?\s+weekly\b", note):
        return True
    return False


def _affirmed_comorbidity_mention_in_note(note_text: str, pattern: str) -> bool:
    for match in re.finditer(pattern, note_text, re.IGNORECASE):
        window = note_text[max(0, match.start() - 96) : match.start()].lower()
        if re.search(
            r"\b(?:did not|does not|do not|denies|denied|no |without |negative for|ruled out|not have any|not had any)\b",
            window,
        ):
            continue
        return True
    return False


def _augment_s2_comorbidity_from_note(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    flags: list[str] = []
    normalized = {
        canonical_comorbidity_label(value)
        for value in raw_values
        if value.strip()
    }
    additions: list[str] = []

    for label, pattern in _COMORBIDITY_NOTE_RECALL_PATTERNS:
        if label in normalized:
            continue
        if not _affirmed_comorbidity_mention_in_note(note_text, pattern):
            continue
        if label == "migraine" and "migraines" in normalized:
            continue
        if label == "migraines" and "migraine" in normalized:
            additions.append("migraines")
            normalized.add("migraines")
            flags.append("s2_bridge:comorbidity_note_recall_augmented")
            continue
        additions.append(label)
        normalized.add(label)
        flags.append("s2_bridge:comorbidity_note_recall_augmented")

    if (
        re.search(
            r"\bmeningioma\b.{0,40}\b(?:resection|surgery)\b|\b(?:resection|surgery)\b.{0,40}\bmeningioma\b",
            note_text,
            re.IGNORECASE,
        )
        and "meningioma surgery" not in normalized
        and "meningioma" not in normalized
    ):
        additions.append("meningioma surgery")
        normalized.add("meningioma surgery")
        flags.append("s2_bridge:comorbidity_note_recall_augmented")

    stroke_components = {"cva", "hemiparesis", "infarct"}
    if (
        stroke_components & normalized
        and "stroke" not in normalized
        and _affirmed_comorbidity_mention_in_note(note_text, r"\bstroke\b")
    ):
        additions.append("stroke")
        normalized.add("stroke")
        flags.append("s2_bridge:comorbidity_note_recall_augmented")

    if (
        "jerk" not in normalized
        and _is_benchmark_comorbidity_jerk(note_text)
        and not _is_seizure_descriptor_jerk_context(note_text)
    ):
        additions.append("jerk")
        normalized.add("jerk")
        flags.append("s2_bridge:comorbidity_note_recall_augmented")

    return [*raw_values, *additions], flags


def _recover_s2_investigation_raw_values(
    raw_values: list[str],
    note_text: str,
    *,
    bridge_tiers: frozenset[str] | None = None,
) -> tuple[list[str], list[str]]:
    flags: list[str] = []
    note = note_text.lower()
    recovered: list[str] = []
    tiers = bridge_tiers or frozenset()

    for raw in raw_values:
        if not raw.strip():
            continue
        normalized = normalize_investigation_phrase(raw)
        if INVESTIGATION_GUARD_DROP_ECG_TIER in tiers:
            modality = normalized.split()[0] if normalized else raw.strip().split()[0].lower()
            if modality == "ecg":
                flags.append("s2_bridge:investigation_ecg_removed")
                continue
        if normalized.endswith(" unknown"):
            modality = normalized.split()[0]
            if (
                f"{modality} unknown" not in note
                and f"{modality} result unknown" not in note
                and "unknown" not in note
            ):
                flags.append("s2_bridge:investigation_unknown_removed")
                continue
        recovered.append(raw.strip())

    return recovered, flags


def exect_s2_run_metadata(
    run_id: str,
    split_name: str,
    model_provider: str,
    model_name: str,
    *,
    prompt_version: str = EXECT_S2_PROMPT_VERSION,
    program_variant: str = EXECT_S2_VARIANT,
    extra: dict | None = None,
) -> RunMetadata:
    return RunMetadata(
        run_id=run_id,
        dataset=EXECT_DATASET,
        split_name=split_name,
        model_provider=model_provider,
        model_name=model_name,
        schema_level=EXECT_S2_SCHEMA_LEVEL,
        program_variant=program_variant,
        scorer_mode=EXECT_S2_SCORER,
        metric_caveats=[
            "These are partial ExECT S2 diagnostics (S1 + investigation + comorbidity), not published ExECTv2 Table 1 reproduction.",
            "Investigation labels use modality+result strings; comorbidities exclude seizure-history PatientHistory phrases.",
            "S1 label-policy bridges from frozen v4.10 are reused for diagnosis, seizure type, and medication.",
            "Evidence quote support is diagnostic and should be reported separately from label metrics.",
        ],
        metadata={
            "prompt_version": prompt_version,
            "s1_prompt_anchor": EXECT_S0_S1_PROMPT_VERSION,
            **(extra or {}),
        },
    )
