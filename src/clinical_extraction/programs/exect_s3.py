"""ExECT S3 field-family DSPy program (S2 + birth/onset/cause/when-diagnosed)."""
from __future__ import annotations

import re
from collections.abc import Callable

import dspy

from clinical_extraction.datasets.exect import (
    canonical_birth_history_label,
    canonical_clinical_phrase,
    canonical_epilepsy_cause_label,
    canonical_onset_label,
    canonical_when_diagnosed_label,
    normalize_investigation_phrase,
)
from clinical_extraction.evaluation.exect import EXECT_S3_SCORER
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_DATASET,
    EXECT_S0_S1_PROMPT_VERSION,
    _as_list,
    _augment_current_prescription_medications,
    _augment_diagnosis_co_lists,
    _filter_diagnosis_for_seizure_descriptor_header,
    _normalize_diagnoses,
    _seizure_type_values_for_record,
    _values_for_family,
)
from clinical_extraction.programs.exect_s2 import (
    EXECT_S2_CLEAN_LADDER_V1_VARIANT,
    EXECT_S2_LABEL_POLICY_GUIDANCE,
    EXECT_S2_POLICY_EXAMPLES,
    EXECT_S2_PROMPT_VERSION,
    EXECT_S2_S1_FIELD_PRIORITY_GUIDANCE,
    _augment_s2_comorbidity_from_note,
    _recover_s2_annotated_medication_raw_values,
    _recover_s2_comorbidity_raw_values,
    _recover_s2_investigation_raw_values,
    _recover_s2_seizure_raw_values,
    _s2_bridge_tiers,
    _s2_values_for_family,
    canonical_comorbidity_label,
    ladder_investigation_guard_bridge_tiers,
    _normalize_investigation_surface,
)
from clinical_extraction.runs import RunMetadata
from clinical_extraction.schemas import (
    DocumentPrediction,
    ExectGoldDocument,
    ExtractedValue,
    PredictionSet,
)

EXECT_S3_SCHEMA_LEVEL = "exect_s3_field_family"
EXECT_S3_VARIANT = "exect_s3_field_family_single_pass"
EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT = (
    "exect_s3_field_family_cause_bridge_k0_k1_single_pass"
)
EXECT_S3_CLEAN_LADDER_V1_VARIANT = "exect_s3_field_family_clean_ladder_v1_single_pass"
_EXECT_S3_PROGRAM_VARIANTS = frozenset(
    {
        EXECT_S3_VARIANT,
        EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
        EXECT_S3_CLEAN_LADDER_V1_VARIANT,
    }
)
EXECT_S3_V1_0_PROMPT_VERSION = "exect_s3_field_family_v1_0_label_policy"
EXECT_S3_V1_1_PROMPT_VERSION = "exect_s3_field_family_v1_1_label_policy"
EXECT_S3_PROMPT_VERSION = "exect_s3_field_family_v1_2_label_policy"
EXECT_S3_FIELD_FAMILIES = (
    "diagnosis",
    "seizure_type",
    "annotated_medication",
    "investigation",
    "comorbidity",
    "birth_history",
    "onset",
    "epilepsy_cause",
    "when_diagnosed",
)
EXECT_S3_S1_SEIZURE_PRIORITY_GUIDANCE = (
    "Nine-family pass with S1 seizure priority: extract the full audited seizure-type list "
    "with the same v4.10 / S2 v1.3 label policy before any S3 field.",
    "Do not omit, shorten, or move seizure-type labels into onset, when_diagnosed, "
    "epilepsy_cause, comorbidity, or birth_history because S3 fields are present.",
    "Do not modernize to ILAE-only labels (focal aware seizure, focal impaired awareness "
    "seizure) when the note uses legacy benchmark surfaces.",
    "Preserve plural seizure wording (generalized tonic clonic seizures, myoclonic seizures).",
    "Use altered awareness when the note says altered awareness; never impaired awareness.",
    "Do not add absence seizures unless absence is explicitly named in seizure context.",
    "Preserve convulsive wording for focal to bilateral convulsive seizures; do not replace "
    "with tonic clonic when the note uses convulsive.",
    "Do not emit bare focal when the note names focal seizure or focal seizures.",
)
EXECT_S3_S2_FIELD_PRIORITY_GUIDANCE = (
    "This is a nine-family pass: complete frozen S2 v1.3 outputs for diagnosis, seizure type, "
    "medication, investigation, and comorbidity before adding any S3 field.",
    "S2 fields are mandatory and scored first — do not shorten, skip, or replace them because "
    "birth history, onset, cause, or when-diagnosed are present.",
    "Investigation must use benchmark modality+result labels only: eeg/mri/ct + "
    "normal/abnormal/unknown (for example eeg normal, mri abnormal).",
    "Never put imaging findings, EEG descriptors, planned scans, or prose sentences in "
    "investigation (for example NOT mri brain normal, NOT eeg spike and wave activity).",
    "Apply full S2 comorbidity atomization and S1 seizure legacy surfaces before S3 fields.",
)
EXECT_S3_LABEL_POLICY_GUIDANCE = (
    *EXECT_S3_S1_SEIZURE_PRIORITY_GUIDANCE,
    *EXECT_S3_S2_FIELD_PRIORITY_GUIDANCE,
    *EXECT_S2_S1_FIELD_PRIORITY_GUIDANCE,
    *EXECT_S2_LABEL_POLICY_GUIDANCE,
    "Birth history labels are affirmed perinatal or delivery surfaces only (for example "
    "born normally, perinatal insult, late preterm birth). Do not move epilepsy diagnoses "
    "into birth history.",
    "Onset labels capture age-of-onset or first-event framing explicitly stated in the "
    "note. The audited gold surface is the condition phrase (often epilepsy or a named "
    "seizure type), not a numeric age or year alone.",
    "Epilepsy cause labels are aetiology phrases explicitly linked to epilepsy causation "
    "(for example meningitis, traumatic brain injury, perinatal insult). Prefer "
    "epilepsy_cause over comorbidity when the note frames the phrase as cause of epilepsy.",
    "When diagnosed labels capture explicit diagnosis-timing mentions (often epilepsy). "
    "Do not emit bare ages or calendar years without the audited condition phrase.",
    "Do not duplicate diagnosis labels into onset or when_diagnosed unless the note "
    "explicitly frames timing or onset for that condition phrase.",
    "When no supported S3 field value is present, return empty lists rather than guessing.",
)
EXECT_S3_POLICY_EXAMPLES = (
    *EXECT_S2_POLICY_EXAMPLES,
    {
        "case": "s3_seizure_priority_with_s3_fields",
        "note_fragment": (
            "Born normally. Seizure type: focal seizures with altered awareness. "
            "Investigations: EEG normal."
        ),
        "benchmark_output": {
            "birth_history": ["born normally"],
            "seizure_type": ["focal seizures with altered awareness"],
            "investigation": ["eeg normal"],
        },
        "policy": "Emit full seizure-type list before S3 fields; do not drop seizure for birth history.",
    },
    {
        "case": "s3_seizure_not_in_onset_slot",
        "note_fragment": "Epilepsy since age 4 with generalized tonic clonic seizures.",
        "benchmark_output": {
            "onset": ["epilepsy"],
            "seizure_type": ["generalized tonic clonic seizures"],
        },
        "policy": "Onset holds timing condition phrase; named seizure types belong in seizure_type.",
    },
    {
        "case": "s3_investigation_modality_result_not_prose",
        "note_fragment": "Investigations: MRI brain scan was normal. EEG showed generalized spike and wave.",
        "benchmark_output": {
            "investigation": ["mri normal", "eeg abnormal"],
        },
        "policy": "Map performed investigations to modality+result only; never imaging prose in investigation.",
    },
    {
        "case": "s3_s2_priority_before_birth_history",
        "note_fragment": (
            "Born normally. Investigations: EEG normal. Comorbidities: type 1 diabetes."
        ),
        "benchmark_output": {
            "birth_history": ["born normally"],
            "investigation": ["eeg normal"],
            "comorbidity": ["type 1 diabetes"],
        },
        "policy": "Emit full S2 investigation and comorbidity labels even when birth history is present.",
    },
    {
        "case": "birth_history_born_normally",
        "note_fragment": "He was born normally with no perinatal problems.",
        "benchmark_output": {"birth_history": ["born normally"]},
        "policy": "Emit affirmed birth-history CUIPhrase surfaces only.",
    },
    {
        "case": "epilepsy_cause_meningitis",
        "note_fragment": (
            "Diagnosis: symptomatic epilepsy secondary to childhood meningitis."
        ),
        "benchmark_output": {"epilepsy_cause": ["meningitis"]},
        "policy": "Prefer epilepsy_cause for causal aetiology phrasing.",
    },
    {
        "case": "onset_epilepsy_age_context",
        "note_fragment": "Epilepsy since the age of four with focal seizures.",
        "benchmark_output": {"onset": ["epilepsy"]},
        "policy": "Emit onset condition phrase; ages are not separate benchmark labels.",
    },
    {
        "case": "when_diagnosed_epilepsy",
        "note_fragment": "She was diagnosed with epilepsy at age 18.",
        "benchmark_output": {"when_diagnosed": ["epilepsy"]},
        "policy": "Emit when-diagnosed condition phrase when timing is stated.",
    },
)


class ExectS3FieldFamilySignature(dspy.Signature):
    """Extract audited ExECT S3 benchmark-facing field families.

    Nine-family pass: S1 seizure-type priority, then full S2 v1.3 fields, then S3 fields.

    Seizure-type (do not skip because S3 fields are present):
    - Preserve legacy audited surfaces; no ILAE modernization; plural + altered awareness rules.
    - Keep named seizure types in seizure_type, not in onset/when_diagnosed/comorbidity.

    Investigation:
    - Output only modality+result pairs: eeg/mri/ct + normal/abnormal/unknown.
    - Do NOT output imaging prose (mri brain normal, eeg spike and wave).

    S3 fields only after diagnosis, seizure_type, medication, investigation, comorbidity.

    Boundary examples:
    - "Seizure type: focal seizures with altered awareness." ->
      seizure_type = ["focal seizures with altered awareness"]
    - "Epilepsy since age 4 with GTCS." -> onset = ["epilepsy"]; seizure_type = ["generalized tonic clonic seizures"]
    - "Investigations: MRI normal, EEG abnormal." -> investigation = ["mri normal", "eeg abnormal"]
    - "Born normally." -> birth_history = ["born normally"]
    - "Epilepsy since age 4." -> onset = ["epilepsy"] (not a separate age label)
    - "Secondary to meningitis." -> epilepsy_cause = ["meningitis"]
    - "Diagnosed with epilepsy at 18." -> when_diagnosed = ["epilepsy"]
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
        desc="Audited prescription-style anti-seizure medication names only."
    )
    annotated_medication_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each medication label, aligned by index."
    )
    investigation: list[str] = dspy.OutputField(
        desc=(
            "Performed investigation results as modality+result labels only "
            "(eeg/mri/ct + normal/abnormal/unknown). No imaging prose or planned scans."
        )
    )
    investigation_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each investigation label, aligned by index."
    )
    comorbidity: list[str] = dspy.OutputField(
        desc="Atomized non-seizure comorbid conditions explicitly named in the note."
    )
    comorbidity_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each comorbidity label, aligned by index."
    )
    birth_history: list[str] = dspy.OutputField(
        desc="Affirmed perinatal or delivery history phrases (born normally, perinatal insult)."
    )
    birth_history_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each birth-history label, aligned by index."
    )
    onset: list[str] = dspy.OutputField(
        desc="Onset condition phrases when age-of-onset or first-event timing is stated."
    )
    onset_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each onset label, aligned by index."
    )
    epilepsy_cause: list[str] = dspy.OutputField(
        desc="Aetiology phrases explicitly linked to epilepsy causation."
    )
    epilepsy_cause_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each epilepsy-cause label, aligned by index."
    )
    when_diagnosed: list[str] = dspy.OutputField(
        desc="Condition phrases when explicit diagnosis timing is stated (often epilepsy)."
    )
    when_diagnosed_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each when-diagnosed label, aligned by index."
    )


class ExectS3FieldFamilyModule(dspy.Module):
    """Single-pass ExECT S3 field-family extractor."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS3FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


def _s3_bridge_tiers(program_variant: str) -> frozenset[str]:
    if program_variant in {
        EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
        EXECT_S3_CLEAN_LADDER_V1_VARIANT,
    }:
        return frozenset({"cause_synonym_plural_v1", "cause_modifier_strip_v1"})
    return frozenset()


def _s3_s2_bridge_tiers(program_variant: str) -> frozenset[str]:
    if program_variant == EXECT_S3_CLEAN_LADDER_V1_VARIANT:
        return _s2_bridge_tiers(EXECT_S2_CLEAN_LADDER_V1_VARIANT)
    return ladder_investigation_guard_bridge_tiers()


def build_exect_s3_module(program_variant: str = EXECT_S3_VARIANT) -> dspy.Module:
    if program_variant in _EXECT_S3_PROGRAM_VARIANTS:
        return ExectS3FieldFamilyModule()
    raise ValueError(f"Unsupported ExECT S3 program variant: {program_variant!r}")


def predict_exect_s3_records(
    module: dspy.Module,
    records: list[ExectGoldDocument],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = EXECT_S3_PROMPT_VERSION,
    program_variant: str = EXECT_S3_VARIANT,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> PredictionSet:
    predictions = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        predictions.append(_predict_s3_record(module, record, program_variant=program_variant))
        if progress_callback is not None:
            progress_callback(index, total, record.document_id)
    return PredictionSet(
        dataset=EXECT_DATASET,
        schema_level=EXECT_S3_SCHEMA_LEVEL,
        predictions=predictions,
        metadata={
            "program_variant": program_variant,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "scorer_mode": EXECT_S3_SCORER,
            "s2_prompt_anchor": EXECT_S2_PROMPT_VERSION,
        },
    )


def _predict_s3_record(
    module: dspy.Module,
    record: ExectGoldDocument,
    *,
    program_variant: str,
) -> DocumentPrediction:
    pred = module(note_text=record.text)
    values = _s2_field_values_from_prediction(pred, record, program_variant=program_variant)
    values.extend(_s3_field_values_from_prediction(pred, record, program_variant=program_variant))
    return DocumentPrediction(
        document_id=record.document_id,
        dataset=EXECT_DATASET,
        schema_level=EXECT_S3_SCHEMA_LEVEL,
        values=values,
        quality_flags=record.quality_flags,
        metadata={"program_variant": program_variant},
    )


def _s2_field_values_from_prediction(
    pred: dspy.Prediction,
    record: ExectGoldDocument,
    *,
    program_variant: str = EXECT_S3_VARIANT,
) -> list[ExtractedValue]:
    """Build frozen S2 field values from one model prediction (no extra LM call)."""
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
    misplaced_seizure = _seizure_phrases_from_misplaced_s3_slots(pred)
    seizure_inputs = [*_as_list(getattr(pred, "seizure_type", [])), *misplaced_seizure]
    seizure_raw, _ = _recover_s2_seizure_raw_values(seizure_inputs, record.text)
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
        bridge_tiers=_s3_s2_bridge_tiers(program_variant),
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
        bridge_tiers=_s3_s2_bridge_tiers(program_variant),
    )
    investigation_raw, _ = _recover_s3_investigation_raw_values(
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
    comorbidity_raw, _ = _recover_s2_comorbidity_raw_values(
        _as_list(getattr(pred, "comorbidity", [])),
        record.text,
        bridge_tiers=_s3_s2_bridge_tiers(program_variant),
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
    return values


def _s3_field_values_from_prediction(
    pred: dspy.Prediction,
    record: ExectGoldDocument,
    *,
    program_variant: str = EXECT_S3_VARIANT,
) -> list[ExtractedValue]:
    values: list[ExtractedValue] = []

    birth_history_raw, _ = _recover_s3_phrase_list(
        _as_list(getattr(pred, "birth_history", [])),
    )
    values.extend(
        _s2_values_for_family(
            record=record,
            field_name="birth_history",
            raw_values=birth_history_raw,
            evidence_values=_as_list(getattr(pred, "birth_history_evidence", [])),
            normalize=canonical_birth_history_label,
        )
    )

    onset_raw, _ = _recover_s3_onset_raw_values(
        _as_list(getattr(pred, "onset", [])),
        record.text,
    )
    values.extend(
        _s2_values_for_family(
            record=record,
            field_name="onset",
            raw_values=onset_raw,
            evidence_values=_as_list(getattr(pred, "onset_evidence", [])),
            normalize=canonical_onset_label,
        )
    )

    cause_raw, _ = _recover_s3_epilepsy_cause_raw_values(
        _as_list(getattr(pred, "epilepsy_cause", [])),
        record.text,
        bridge_tiers=_s3_bridge_tiers(program_variant),
    )
    values.extend(
        _s2_values_for_family(
            record=record,
            field_name="epilepsy_cause",
            raw_values=cause_raw,
            evidence_values=_as_list(getattr(pred, "epilepsy_cause_evidence", [])),
            normalize=canonical_epilepsy_cause_label,
        )
    )

    when_diagnosed_raw, _ = _recover_s3_when_diagnosed_raw_values(
        _as_list(getattr(pred, "when_diagnosed", [])),
        record.text,
    )
    values.extend(
        _s2_values_for_family(
            record=record,
            field_name="when_diagnosed",
            raw_values=when_diagnosed_raw,
            evidence_values=_as_list(getattr(pred, "when_diagnosed_evidence", [])),
            normalize=canonical_when_diagnosed_label,
        )
    )
    return values


_ONSET_TIMING_PHRASES = frozenset({"epilepsy", "epileptic seizures"})
_SEIZURE_REROUTE_MARKERS = (
    "seizure",
    "tonic clonic",
    "convulsive",
    "absence",
    "myoclonic",
    "focal aware",
    "impaired awareness",
    "altered awareness",
    "temporal lobe",
    "occipital lobe",
    "non epileptic",
)


def _seizure_phrases_from_misplaced_s3_slots(pred: dspy.Prediction) -> list[str]:
    extras: list[str] = []
    for field in ("onset", "when_diagnosed", "comorbidity"):
        for raw in _as_list(getattr(pred, field, [])):
            if not raw.strip():
                continue
            if _should_reroute_misplaced_seizure_phrase(raw):
                extras.append(raw.strip())
    return extras


def _should_reroute_misplaced_seizure_phrase(value: str) -> bool:
    canonical = canonical_clinical_phrase(value)
    if not canonical:
        return False
    if canonical in _ONSET_TIMING_PHRASES:
        return False
    return any(marker in canonical for marker in _SEIZURE_REROUTE_MARKERS)


def _recover_s3_onset_raw_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    flags: list[str] = []
    recovered: list[str] = []

    for raw in raw_values:
        if not raw.strip():
            continue
        canonical = canonical_onset_label(raw)
        if canonical in _ONSET_TIMING_PHRASES:
            recovered.append(canonical)
            continue
        if _should_reroute_misplaced_seizure_phrase(raw):
            flags.append("s3_bridge:onset_seizure_type_removed")
            continue
        recovered.append(raw.strip())

    return recovered, flags


def _recover_s3_phrase_list(raw_values: list[str]) -> tuple[list[str], list[str]]:
    recovered = [raw.strip() for raw in raw_values if raw.strip()]
    return recovered, []


_INVESTIGATION_MODALITIES = ("eeg", "mri", "ct")
_INVESTIGATION_RESULTS = frozenset({"normal", "abnormal", "unknown"})
_INVESTIGATION_ABNORMAL_MARKERS = (
    "abnormal",
    "spike",
    "polyspike",
    "slowing",
    "epileptiform",
    "dysplasia",
    "atrophy",
    "infarct",
    "lesion",
    "haemorrhage",
    "hemorrhage",
)


def _is_canonical_investigation_label(label: str) -> bool:
    tokens = label.split()
    return (
        len(tokens) == 2
        and tokens[0] in _INVESTIGATION_MODALITIES
        and tokens[1] in _INVESTIGATION_RESULTS
    )


def _canonicalize_investigation_prose(raw: str) -> str | None:
    canonical = normalize_investigation_phrase(raw)
    if _is_canonical_investigation_label(canonical):
        return canonical

    lower = canonical_clinical_phrase(raw.replace("+", " ").replace(":", " "))
    if not lower:
        return None
    if "planned" in lower and not any(
        marker in lower for marker in ("normal", "abnormal", "unknown")
    ):
        return None

    for modality in _INVESTIGATION_MODALITIES:
        if modality not in lower.split() and modality not in lower:
            continue
        if "unknown" in lower:
            return f"{modality} unknown"
        if "normal" in lower and not any(
            marker in lower for marker in _INVESTIGATION_ABNORMAL_MARKERS if marker != "normal"
        ):
            return f"{modality} normal"
        if any(marker in lower for marker in _INVESTIGATION_ABNORMAL_MARKERS):
            return f"{modality} abnormal"
    return None


def _recover_s3_investigation_raw_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for raw in raw_values:
        if not raw.strip():
            continue
        canonical = _canonicalize_investigation_prose(raw)
        if not canonical:
            flags.append("s3_bridge:investigation_prose_removed")
            continue
        if canonical in seen:
            continue
        if canonical != normalize_investigation_phrase(raw):
            flags.append("s3_bridge:investigation_modality_result_restored")
        seen.add(canonical)
        recovered.append(canonical)

    return recovered, flags


_WHEN_DIAGNOSED_EXCLUDED = frozenset(
    {
        "single focal seizure",
        "focal seizure",
        "focal seizures",
        "generalized tonic clonic seizure",
        "generalized tonic clonic seizures",
        "absence seizure",
        "absence seizures",
    }
)


def _recover_s3_when_diagnosed_raw_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    flags: list[str] = []
    recovered: list[str] = []

    for raw in raw_values:
        if not raw.strip():
            continue
        canonical = canonical_when_diagnosed_label(raw)
        if canonical in _WHEN_DIAGNOSED_EXCLUDED:
            flags.append("s3_bridge:when_diagnosed_seizure_type_removed")
            continue
        if canonical == "epilepsy" or re.search(
            r"\bepilepsy\b", note_text, re.IGNORECASE
        ):
            recovered.append(canonical if canonical else raw.strip())
            continue
        flags.append("s3_bridge:when_diagnosed_unsupported_removed")

    return recovered, flags


def _normalize_s3_epilepsy_cause_candidate(
    value: str,
    note_text: str,
    *,
    bridge_tiers: frozenset[str],
) -> tuple[str, list[str]]:
    flags: list[str] = []
    canonical = canonical_epilepsy_cause_label(value)
    if not canonical:
        return value, flags

    if "cause_synonym_plural_v1" in bridge_tiers:
        if canonical == "strokes":
            canonical = "stroke"
            flags.append("s3_bridge:cause_plural_normalized")
        if canonical in {"cerebrovascular accident", "cva"}:
            if re.search(r"\bcva\b", note_text, re.IGNORECASE):
                canonical = "cva"
            elif re.search(r"\bstroke\b", note_text, re.IGNORECASE):
                canonical = "stroke"
            else:
                canonical = "cva"
            flags.append("s3_bridge:cause_synonym_mapped")
        if "haemorrhage" in canonical and (
            re.search(r"\bhemorrhage\b", note_text, re.IGNORECASE)
            or not re.search(r"\bhaemorrhage\b", note_text, re.IGNORECASE)
        ):
            canonical = canonical.replace("haemorrhage", "hemorrhage")
            flags.append("s3_bridge:cause_spelling_normalized")

    if "cause_modifier_strip_v1" in bridge_tiers:
        if canonical == "early life meningitis":
            canonical = "meningitis"
            flags.append("s3_bridge:cause_modifier_stripped")
        ich_match = re.match(
            r"^(?:recurrent\s+)?(?:right\s+hemisphere\s+)?intracerebral haemorrhage$",
            canonical,
        )
        if ich_match:
            canonical = "intracerebral hemorrhage"
            flags.append("s3_bridge:cause_modifier_stripped")
            if "s3_bridge:cause_spelling_normalized" not in flags:
                flags.append("s3_bridge:cause_spelling_normalized")

    return canonical, flags


def _recover_s3_epilepsy_cause_raw_values(
    raw_values: list[str],
    note_text: str,
    *,
    bridge_tiers: frozenset[str] | None = None,
) -> tuple[list[str], list[str]]:
    flags: list[str] = []
    recovered: list[str] = []
    tiers = bridge_tiers or frozenset()

    for raw in raw_values:
        if not raw.strip():
            continue
        canonical = canonical_epilepsy_cause_label(raw)
        if not canonical:
            continue
        if canonical in {"seizure", "seizures", "febrile seizure", "febrile seizures"}:
            flags.append("s3_bridge:seizure_history_cause_removed")
            continue
        if tiers:
            value, bridge_flags = _normalize_s3_epilepsy_cause_candidate(
                raw.strip(),
                note_text,
                bridge_tiers=tiers,
            )
            flags.extend(bridge_flags)
            recovered.append(value)
            continue
        recovered.append(raw.strip())

    return recovered, flags


def exect_s3_run_metadata(
    run_id: str,
    split_name: str,
    model_provider: str,
    model_name: str,
    *,
    prompt_version: str = EXECT_S3_PROMPT_VERSION,
    program_variant: str = EXECT_S3_VARIANT,
    extra: dict | None = None,
) -> RunMetadata:
    return RunMetadata(
        run_id=run_id,
        dataset=EXECT_DATASET,
        split_name=split_name,
        model_provider=model_provider,
        model_name=model_name,
        schema_level=EXECT_S3_SCHEMA_LEVEL,
        program_variant=program_variant,
        scorer_mode=EXECT_S3_SCORER,
        metric_caveats=[
            "These are partial ExECT S3 diagnostics (S2 + birth/onset/cause/when-diagnosed), not published ExECTv2 Table 1 reproduction.",
            "S2 label-policy bridges from frozen v1.3 are reused for S1 and S2 families without editing exect_s2.py.",
            "S3 gold uses CUIPhrase surfaces; temporal ages and years are not benchmark labels in Phase 1.",
            "Overlapping phrases across families are scored independently; see docs/experiments/exect/exect_s3_phase1_overlap_policy.md.",
            "Evidence quote support is diagnostic and should be reported separately from label metrics.",
        ],
        metadata={
            "prompt_version": prompt_version,
            "s2_prompt_anchor": EXECT_S2_PROMPT_VERSION,
            "s1_prompt_anchor": EXECT_S0_S1_PROMPT_VERSION,
            **(extra or {}),
        },
    )
