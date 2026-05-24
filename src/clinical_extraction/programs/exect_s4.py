"""ExECT S4 field-family DSPy program (S3 + seizure frequency + Rx temporality)."""
from __future__ import annotations

import re
from collections.abc import Callable

import dspy

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
    format_medication_temporality_label,
    infer_prescription_temporality,
)
from clinical_extraction.evaluation.exect import EXECT_S4_SCORER, EXECT_S5_SCORER
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_DATASET,
    EXECT_S0_S1_PROMPT_VERSION,
    _as_list,
)
from clinical_extraction.programs.exect_s2 import (
    EXECT_S2_PROMPT_VERSION,
    _recover_s2_investigation_raw_values,
    ladder_investigation_guard_bridge_tiers,
)
from clinical_extraction.programs.exect_s3 import (
    EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
    EXECT_S3_FIELD_FAMILIES,
    EXECT_S3_LABEL_POLICY_GUIDANCE,
    EXECT_S3_POLICY_EXAMPLES,
    EXECT_S3_PROMPT_VERSION,
    EXECT_S3_VARIANT,
    _normalize_investigation_surface,
    _recover_s3_investigation_raw_values,
    _s2_field_values_from_prediction,
    _s2_values_for_family,
    _s3_field_values_from_prediction,
)
from clinical_extraction.runs import RunMetadata
from clinical_extraction.exect.primitives import (
    build_exect_frequency_pre_vocab_labels as build_precomputed_seizure_frequency_candidates,
    build_exect_frequency_pre_vocab_labels_high_precision as build_precomputed_seizure_frequency_candidates_high_precision,
    format_exect_frequency_pre_vocab_note as format_note_with_precomputed_seizure_frequency_candidates,
    format_exect_frequency_pre_vocab_note_high_precision as format_note_with_precomputed_seizure_frequency_candidates_high_precision,
    recover_exect_frequency_benchmark_values as _recover_s4_seizure_frequency_raw_values,
    recover_exect_frequency_benchmark_values_with_multi_label_retention as _recover_s4_seizure_frequency_multi_label_retention_raw_values,
    recover_exect_frequency_benchmark_values_with_post_merge as _recover_s4_seizure_frequency_post_merge_raw_values,
    recover_exect_medication_temporality_non_asm_dose_current_guard,
    recover_exect_medication_temporality_non_asm_guard,
    recover_exect_medication_temporality_with_post_classifier,
    repair_exect_frequency_surface as _repair_s4_seizure_frequency_surface,
)
from clinical_extraction.exect.slot_payload import format_exect_frequency_slot_payload_for_prompt
from clinical_extraction.schemas import (
    DocumentPrediction,
    ExectGoldDocument,
    ExtractedValue,
    PredictionSet,
)

EXECT_S4_SCHEMA_LEVEL = "exect_s4_field_family"
EXECT_S4_L1_VARIANT = "exect_s4_field_family_single_pass"
EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT = (
    "exect_s4_field_family_cause_bridge_k0_k1_single_pass"
)
EXECT_S4_VARIANT = EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT
EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT = (
    "exect_s4_field_family_frequency_pre_vocab_single_pass"
)
EXECT_S4_FREQUENCY_PRE_VOCAB_HIGH_PRECISION_VARIANT = (
    "exect_s4_field_family_frequency_pre_vocab_high_precision_single_pass"
)
EXECT_S4_FREQUENCY_POST_MERGE_VARIANT = (
    "exect_s4_field_family_frequency_post_merge_single_pass"
)
EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT = (
    "exect_s4_field_family_frequency_structured_slots_single_pass"
)
EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_PROMPT_VERSION = (
    "exect_s4_field_family_v1_2_label_policy_structured_frequency_slots"
)
EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT = (
    "exect_s4_field_family_temporality_post_classifier_single_pass"
)
EXECT_S4_MT_GUARD_NON_ASM_VARIANT = (
    "exect_s4_field_family_mt_guard_non_asm_single_pass"
)
EXECT_S4_MT_GUARD_NON_ASM_DOSE_CURRENT_VARIANT = (
    "exect_s4_field_family_mt_guard_non_asm_dose_current_single_pass"
)
EXECT_S4_PROMPT_VERSION = "exect_s4_field_family_v1_2_label_policy"
EXECT_S4_FIELD_FAMILIES = (
    *EXECT_S3_FIELD_FAMILIES,
    "seizure_frequency",
    "medication_temporality",
)
EXECT_S4_S3_FIELD_PRIORITY_GUIDANCE = (
    "This is an eleven-family pass: complete frozen S3 v1.2 outputs for all nine S3 families "
    "before adding seizure frequency or medication temporality.",
    "S3 fields are mandatory and scored first — do not shorten, skip, or replace them because "
    "seizure frequency or medication temporality are present.",
    "Report per-family labels independently; overlapping phrases across families are expected.",
)
EXECT_S4_FREQUENCY_LABEL_POLICY_GUIDANCE = (
    "Seizure frequency labels are quantified rates, qualitative frequency changes, or "
    "seizure-free status — not seizure-type names.",
    "Quantified rates use both cardinal slots: N per N week/month/day/year "
    "(e.g. 1 per 1 month, 1 per 3 week, 0 per 5 year) — never shorten to 1 per month.",
    "When the note states a quantified rate and a frequency change, emit both labels "
    "(e.g. 1 per 3 week plus frequency increased) — do not collapse to the rate alone.",
    "Emit every supported frequency surface when the note states multiple rates or changes "
    "(quantified rate + frequency increased/decreased + infrequent can coexist).",
    "Qualitative surfaces: frequency increased, frequency decreased, infrequent, "
    "seizure free, seizure free since YEAR.",
    "Do not invent non-audited period templates (30 day, previous appointment, "
    "several per day) — use only supported benchmark surfaces.",
    "Do not put named seizure types (focal seizures, generalized tonic clonic seizures) "
    "in seizure_frequency; those belong in seizure_type.",
    "Do not emit clinical prose (seizure free for more than five years) — use benchmark "
    "surfaces only.",
)
EXECT_S4_INVESTIGATION_LABEL_POLICY_GUIDANCE = (
    "Investigation labels are performed modality+result pairs only "
    "(eeg/mri/ct + normal/abnormal/unknown).",
    "Do not emit eeg unknown or mri unknown for planned, requested, or not-yet-performed "
    "scans — abstain unless the note explicitly states an unknown result.",
    "When results are unavailable (for example do not have the results of the EEG), "
    "eeg unknown is allowed; otherwise prefer normal/abnormal or abstain.",
)
EXECT_S4_LABEL_POLICY_GUIDANCE = (
    *EXECT_S4_S3_FIELD_PRIORITY_GUIDANCE,
    *EXECT_S3_LABEL_POLICY_GUIDANCE,
    *EXECT_S4_FREQUENCY_LABEL_POLICY_GUIDANCE,
    *EXECT_S4_INVESTIGATION_LABEL_POLICY_GUIDANCE,
    "Medication temporality uses pipe format medication|status where status is current, "
    "planned, or previous.",
    "Bare medication names belong in annotated_medication only; medication_temporality "
    "must include the status after the pipe.",
    "Treat dose changes on an existing prescription (to reduce, to increase) as current, "
    "not planned.",
    "When no supported S4 field value is present, return empty lists rather than guessing.",
)
EXECT_S4_POLICY_EXAMPLES = (
    *EXECT_S3_POLICY_EXAMPLES,
    {
        "case": "s4_seizure_frequency_quantified_and_change",
        "note_fragment": (
            "He has about one focal seizure every three weeks and the frequency has increased."
        ),
        "benchmark_output": {
            "seizure_frequency": ["1 per 3 week", "frequency increased"],
        },
        "policy": "Emit quantified rate and qualitative frequency change in seizure_frequency.",
    },
    {
        "case": "s4_seizure_frequency_not_seizure_type",
        "note_fragment": "Seizure type: focal seizures. Frequency: one per month.",
        "benchmark_output": {
            "seizure_type": ["focal seizures"],
            "seizure_frequency": ["1 per 1 month"],
        },
        "policy": "Keep seizure types in seizure_type; quantified rates in seizure_frequency.",
    },
    {
        "case": "s4_medication_temporality_pipe_format",
        "note_fragment": "Current anti-epileptic medication: lamotrigine 75mg bd.",
        "benchmark_output": {
            "annotated_medication": ["lamotrigine"],
            "medication_temporality": ["lamotrigine|current"],
        },
        "policy": "Emit medication name in annotated_medication and medication|current in temporality.",
    },
    {
        "case": "s4_seizure_free_since_year",
        "note_fragment": "He has been seizure free since 2017.",
        "benchmark_output": {"seizure_frequency": ["seizure free since 2017"]},
        "policy": "Emit seizure free since YEAR when a seizure-free interval is stated.",
    },
    {
        "case": "s4_seizure_frequency_dual_cardinal_template",
        "note_fragment": "He has one seizure per day and one per month.",
        "benchmark_output": {
            "seizure_frequency": ["1 per 1 day", "1 per 1 month"],
        },
        "policy": "Always emit both cardinal slots in N per N period templates.",
    },
    {
        "case": "s4_seizure_frequency_zero_rate",
        "note_fragment": "No seizures in the past three years.",
        "benchmark_output": {"seizure_frequency": ["0 per 3 year"]},
        "policy": "Emit zero-rate quantified surfaces when a zero count over a period is stated.",
    },
    {
        "case": "s4_seizure_frequency_multi_label_block",
        "note_fragment": (
            "About one seizure per week with decreased frequency and infrequent clusters."
        ),
        "benchmark_output": {
            "seizure_frequency": ["1 per 1 week", "frequency decreased", "infrequent"],
        },
        "policy": "Retain all supported frequency labels; do not collapse to a single rate.",
    },
    {
        "case": "s4_seizure_free_benchmark_surface",
        "note_fragment": "Seizure free for more than five years.",
        "benchmark_output": {"seizure_frequency": ["seizure free"]},
        "policy": "Collapse long seizure-free prose to seizure free unless YEAR is explicit.",
    },
    {
        "case": "s4_investigation_no_unknown_for_planned_scan",
        "note_fragment": "I will arrange an MRI brain and an EEG.",
        "benchmark_output": {"investigation": []},
        "policy": "Do not emit unknown for planned scans; abstain until results are stated.",
    },
    {
        "case": "s4_investigation_unknown_when_results_unavailable",
        "note_fragment": "I do not have the results of his recent EEG test.",
        "benchmark_output": {"investigation": ["eeg unknown"]},
        "policy": "Emit eeg unknown when results are explicitly unavailable.",
    },
)

_VALID_RX_TEMPORALITIES = frozenset({"current", "planned", "previous"})
_INVESTIGATION_MODALITIES = ("eeg", "mri", "ct")
_PLANNED_INVESTIGATION_MARKERS = (
    "will arrange",
    "will request",
    "requesting",
    "due to have",
    "plan to",
    "arrange an",
    "arrange a",
    "which i will request",
)


class ExectS4FieldFamilySignature(dspy.Signature):
    """Extract audited ExECT S4 benchmark-facing field families.

    Eleven-family pass: frozen S3 v1.2 priority, then seizure frequency and Rx temporality.

    Seizure frequency (not seizure types):
    - Quantified rates: N per N week/month/day/year (both cardinal slots required)
    - Zero rates: 0 per N year/week when stated
    - Qualitative: frequency increased/decreased, infrequent, seizure free, seizure free since YEAR
    - Retain multiple frequency labels when note supports rate + change + infrequent
    - Do not emit non-audited period templates (30 day, previous appointment)

    Investigation (eleven-family pass):
    - Do not emit modality unknown for planned or requested scans
    - Emit unknown only when results are explicitly unavailable or unknown

    Medication temporality:
    - Pipe format medication|current|planned|previous
    - Bare medication names belong in annotated_medication only

    Complete all nine S3 families before S4 fields.

    Boundary examples:
    - "One seizure every three weeks." -> seizure_frequency = ["1 per 3 week"]
    - "Seizure type: focal seizures." -> seizure_type = ["focal seizures"] (not frequency)
    - "Current medication: lamotrigine." ->
      annotated_medication = ["lamotrigine"], medication_temporality = ["lamotrigine|current"]
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
            "Preserve plural and legacy audited surfaces."
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
            "(eeg/mri/ct + normal/abnormal/unknown). No unknown for planned scans."
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
        desc="Affirmed perinatal or delivery history phrases."
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
        desc="Condition phrases when explicit diagnosis timing is stated."
    )
    when_diagnosed_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each when-diagnosed label, aligned by index."
    )
    seizure_frequency: list[str] = dspy.OutputField(
        desc=(
            "Seizure frequency benchmark labels: N per N week/month/day/year quantified rates "
            "(both cardinal slots), zero rates, frequency increased/decreased, infrequent, "
            "seizure free, seizure free since YEAR — not seizure-type names; retain multi-label."
        )
    )
    seizure_frequency_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each seizure-frequency label, aligned by index."
    )
    medication_temporality: list[str] = dspy.OutputField(
        desc="Prescription temporality as medication|current|planned|previous."
    )
    medication_temporality_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each medication-temporality label, aligned by index."
    )


class ExectS4FieldFamilyModule(dspy.Module):
    """Single-pass ExECT S4 field-family extractor."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS4FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


class ExectS4FrequencyPreVocabFieldFamilyModule(dspy.Module):
    """Single-pass S4 extractor with seizure-frequency-only pre-vocabulary hints."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS4FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(
            note_text=format_note_with_precomputed_seizure_frequency_candidates(
                note_text
            )
        )


class ExectS4FrequencyPreVocabHighPrecisionFieldFamilyModule(dspy.Module):
    """Single-pass S4 extractor with seizure-frequency-only high-precision pre-vocabulary hints."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS4FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(
            note_text=format_note_with_precomputed_seizure_frequency_candidates_high_precision(
                note_text
            )
        )


class ExectS4FrequencyStructuredSlotsFieldFamilyModule(dspy.Module):
    """Single-pass S4 extractor with ExECT structured frequency slot hints."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS4FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(
            note_text=format_exect_frequency_slot_payload_for_prompt(note_text)
        )


def build_exect_s4_module(program_variant: str = EXECT_S4_VARIANT) -> dspy.Module:
    if program_variant in {
        EXECT_S4_VARIANT,
        EXECT_S4_L1_VARIANT,
        EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
        EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
        EXECT_S4_MT_GUARD_NON_ASM_DOSE_CURRENT_VARIANT,
        EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
        EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT,
    }:
        return ExectS4FieldFamilyModule()
    if program_variant == EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT:
        return ExectS4FrequencyPreVocabFieldFamilyModule()
    if program_variant == EXECT_S4_FREQUENCY_PRE_VOCAB_HIGH_PRECISION_VARIANT:
        return ExectS4FrequencyPreVocabHighPrecisionFieldFamilyModule()
    if program_variant == EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT:
        return ExectS4FrequencyStructuredSlotsFieldFamilyModule()
    raise ValueError(f"Unsupported ExECT S4 program variant: {program_variant!r}")


def _s4_epilepsy_cause_bridge_s3_variant(program_variant: str) -> str:
    if program_variant in {EXECT_S4_VARIANT, EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT}:
        return EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT
    return EXECT_S3_VARIANT


def predict_exect_s4_records(
    module: dspy.Module,
    records: list[ExectGoldDocument],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = EXECT_S4_PROMPT_VERSION,
    program_variant: str = EXECT_S4_VARIANT,
    progress_callback: Callable[[int, int, str], None] | None = None,
    schema_level: str = EXECT_S4_SCHEMA_LEVEL,
) -> PredictionSet:
    predictions = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        predictions.append(_predict_s4_record(module, record, program_variant=program_variant, schema_level=schema_level))
        if progress_callback is not None:
            progress_callback(index, total, record.document_id)
    return PredictionSet(
        dataset=EXECT_DATASET,
        schema_level=schema_level,
        predictions=predictions,
        metadata={
            "program_variant": program_variant,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "scorer_mode": EXECT_S5_SCORER if schema_level == "exect_s5_core_field_family" else EXECT_S4_SCORER,
            "s3_prompt_anchor": EXECT_S3_PROMPT_VERSION,
            "s2_prompt_anchor": EXECT_S2_PROMPT_VERSION,
        },
    )


def _predict_s4_record(
    module: dspy.Module,
    record: ExectGoldDocument,
    *,
    program_variant: str,
    schema_level: str = EXECT_S4_SCHEMA_LEVEL,
) -> DocumentPrediction:
    pred = module(note_text=record.text)
    values = _s2_field_values_from_prediction(pred, record)
    values.extend(
        _s3_field_values_from_prediction(
            pred,
            record,
            program_variant=_s4_epilepsy_cause_bridge_s3_variant(program_variant),
        )
    )
    values = _replace_s4_investigation_values(values, pred, record)
    values.extend(_s4_field_values_from_prediction(pred, record, program_variant))
    metadata: dict[str, object] = {"program_variant": program_variant}
    if program_variant == EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT:
        metadata["precomputed_candidates"] = {
            "seizure_frequency": build_precomputed_seizure_frequency_candidates(
                record.text
            )
        }
    if program_variant == EXECT_S4_FREQUENCY_PRE_VOCAB_HIGH_PRECISION_VARIANT:
        metadata["precomputed_candidates"] = {
            "seizure_frequency": build_precomputed_seizure_frequency_candidates_high_precision(
                record.text
            )
        }
    if program_variant == EXECT_S4_FREQUENCY_POST_MERGE_VARIANT:
        metadata["post_merge"] = {
            "seizure_frequency": "exect.frequency.benchmark_bridge.v1:post_merge_v1_3"
        }
    if program_variant == EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT:
        metadata["structured_frequency_slots"] = {
            "seizure_frequency": (
                "exect.frequency.benchmark_bridge.v1:multi_label_retention_v1"
            ),
            "slot_payload": "exect.frequency.structured_slots.v1",
        }
    if program_variant == EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT:
        metadata["post_classifier"] = {
            "medication_temporality": "exect.medication_temporality.post_classifier.v1"
        }
    if program_variant == EXECT_S4_MT_GUARD_NON_ASM_VARIANT:
        metadata["post_guard"] = {
            "medication_temporality": "exect.medication_temporality.non_asm_guard.v1"
        }
    if program_variant == EXECT_S4_MT_GUARD_NON_ASM_DOSE_CURRENT_VARIANT:
        metadata["post_guard"] = {
            "medication_temporality": (
                "exect.medication_temporality.non_asm_dose_current_guard.v1"
            )
        }
    if program_variant in {EXECT_S4_VARIANT, EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT}:
        metadata["post_bridge"] = {
            "epilepsy_cause": "exect.epilepsy_cause.cui_phrase_bridge.v1:k0_k1"
        }
    return DocumentPrediction(
        document_id=record.document_id,
        dataset=EXECT_DATASET,
        schema_level=schema_level,
        values=values,
        quality_flags=record.quality_flags,
        metadata=metadata,
    )


def _replace_s4_investigation_values(
    values: list[ExtractedValue],
    pred: dspy.Prediction,
    record: ExectGoldDocument,
) -> list[ExtractedValue]:
    non_investigation = [value for value in values if value.field_name != "investigation"]
    investigation_raw, _ = _recover_s2_investigation_raw_values(
        _as_list(getattr(pred, "investigation", [])),
        record.text,
        bridge_tiers=ladder_investigation_guard_bridge_tiers(),
    )
    investigation_raw, _ = _recover_s3_investigation_raw_values(
        investigation_raw,
        record.text,
    )
    investigation_raw, _ = _recover_s4_investigation_raw_values(
        investigation_raw,
        record.text,
    )
    investigation_values = _s2_values_for_family(
        record=record,
        field_name="investigation",
        raw_values=investigation_raw,
        evidence_values=_as_list(getattr(pred, "investigation_evidence", [])),
        normalize=_normalize_investigation_surface,
    )
    return [*non_investigation, *investigation_values]


def _s4_field_values_from_prediction(
    pred: dspy.Prediction,
    record: ExectGoldDocument,
    program_variant: str = EXECT_S4_VARIANT,
) -> list[ExtractedValue]:
    values: list[ExtractedValue] = []

    frequency_raw, _ = _recover_s4_seizure_frequency_values(
        _as_list(getattr(pred, "seizure_frequency", [])),
        record.text,
        program_variant=program_variant,
    )
    values.extend(
        _s2_values_for_family(
            record=record,
            field_name="seizure_frequency",
            raw_values=frequency_raw,
            evidence_values=_as_list(getattr(pred, "seizure_frequency_evidence", [])),
            normalize=canonical_clinical_phrase,
        )
    )

    temporality_predictions = _as_list(getattr(pred, "medication_temporality", []))
    temporality_evidence = _as_list(getattr(pred, "medication_temporality_evidence", []))
    if program_variant == EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT:
        temporality_raw, _ = recover_exect_medication_temporality_with_post_classifier(
            temporality_predictions,
            temporality_evidence,
            record.text,
        )
    elif program_variant == EXECT_S4_MT_GUARD_NON_ASM_VARIANT:
        temporality_raw, _ = recover_exect_medication_temporality_non_asm_guard(
            temporality_predictions,
            temporality_evidence,
            record.text,
        )
    elif program_variant == EXECT_S4_MT_GUARD_NON_ASM_DOSE_CURRENT_VARIANT:
        temporality_raw, _ = (
            recover_exect_medication_temporality_non_asm_dose_current_guard(
                temporality_predictions,
                temporality_evidence,
                record.text,
            )
        )
    else:
        temporality_raw, _ = _recover_s4_medication_temporality_raw_values(
            temporality_predictions,
            record.text,
        )
    values.extend(
        _s2_values_for_family(
            record=record,
            field_name="medication_temporality",
            raw_values=temporality_raw,
            evidence_values=_as_list(getattr(pred, "medication_temporality_evidence", [])),
            normalize=_normalize_medication_temporality_surface,
        )
    )
    return values


def _note_supports_investigation_unknown(modality: str, note_text: str) -> bool:
    note = note_text.lower()
    if f"{modality} unknown" in note or f"{modality} result unknown" in note:
        return True
    if "unknown" in note and modality in note:
        return True
    if modality == "eeg" and any(
        marker in note
        for marker in (
            "do not have the results of",
            "don't have the results of",
            "results of his recent eeg",
            "results of her recent eeg",
            "results of the recent eeg",
            "results of recent eeg",
        )
    ):
        return True
    if modality == "mri" and any(
        marker in note
        for marker in (
            "do not have the results of",
            "don't have the results of",
            "results of his recent mri",
            "results of her recent mri",
            "results of the recent mri",
            "results of recent mri",
        )
    ):
        return True
    return False


def _note_has_planned_investigation(modality: str, note_text: str) -> bool:
    note = note_text.lower()
    if modality not in note:
        return False
    return any(marker in note for marker in _PLANNED_INVESTIGATION_MARKERS)


def _recover_s4_investigation_raw_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for raw in raw_values:
        if not raw.strip():
            continue
        canonical = _normalize_investigation_surface(raw)
        if not canonical.endswith(" unknown"):
            if canonical in seen:
                continue
            seen.add(canonical)
            recovered.append(canonical)
            continue

        modality = canonical.split()[0]
        if modality not in _INVESTIGATION_MODALITIES:
            flags.append("s4_bridge:investigation_unknown_removed")
            continue
        if _note_supports_investigation_unknown(modality, note_text):
            if canonical in seen:
                continue
            seen.add(canonical)
            recovered.append(canonical)
            continue
        if _note_has_planned_investigation(modality, note_text):
            flags.append("s4_bridge:investigation_unknown_removed")
            continue
        flags.append("s4_bridge:investigation_unknown_removed")

    return recovered, flags


def _recover_s4_seizure_frequency_values(
    raw_values: list[str],
    note_text: str,
    *,
    program_variant: str = EXECT_S4_VARIANT,
) -> tuple[list[str], list[str]]:
    if program_variant == EXECT_S4_FREQUENCY_POST_MERGE_VARIANT:
        return _recover_s4_seizure_frequency_post_merge_raw_values(raw_values, note_text)
    if program_variant == EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT:
        return _recover_s4_seizure_frequency_multi_label_retention_raw_values(
            raw_values, note_text
        )
    return _recover_s4_seizure_frequency_raw_values(raw_values, note_text)


def _normalize_medication_temporality_surface(value: str) -> str:
    if "|" not in value:
        return canonical_clinical_phrase(value)
    medication, temporality = value.split("|", 1)
    return format_medication_temporality_label(
        canonical_medication_name(medication),
        canonical_clinical_phrase(temporality),
    )


def _recover_s4_medication_temporality_raw_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    flags: list[str] = []
    recovered: list[str] = []
    seen: set[str] = set()

    for raw in raw_values:
        if not raw.strip():
            continue
        if "|" in raw:
            medication, temporality = raw.split("|", 1)
            medication_name = canonical_medication_name(medication)
            status = canonical_clinical_phrase(temporality)
            if not medication_name or status not in _VALID_RX_TEMPORALITIES:
                flags.append("s4_bridge:medication_temporality_invalid_pipe")
                continue
            label = format_medication_temporality_label(medication_name, status)
        else:
            medication_name = canonical_medication_name(raw)
            if not medication_name:
                flags.append("s4_bridge:medication_temporality_unrecognized")
                continue
            status = infer_prescription_temporality(note_text)
            label = format_medication_temporality_label(medication_name, status)
            flags.append("s4_bridge:medication_temporality_status_inferred")

        if label in seen:
            continue
        seen.add(label)
        recovered.append(label)

    return recovered, flags


def exect_s4_run_metadata(
    run_id: str,
    split_name: str,
    model_provider: str,
    model_name: str,
    *,
    prompt_version: str = EXECT_S4_PROMPT_VERSION,
    program_variant: str = EXECT_S4_VARIANT,
    extra: dict | None = None,
    schema_level: str = EXECT_S4_SCHEMA_LEVEL,
) -> RunMetadata:
    return RunMetadata(
        run_id=run_id,
        dataset=EXECT_DATASET,
        split_name=split_name,
        model_provider=model_provider,
        model_name=model_name,
        schema_level=schema_level,
        program_variant=program_variant,
        scorer_mode=EXECT_S5_SCORER if schema_level == "exect_s5_core_field_family" else EXECT_S4_SCORER,
        metric_caveats=[
            "These are partial ExECT S4 diagnostics (S3 + seizure frequency + Rx temporality), not published ExECTv2 Table 1 reproduction.",
            "S3 label-policy bridges from frozen v1.2 are reused for S1–S3 families without editing exect_s3.py.",
            "Seizure-frequency gold uses SeizureFrequency JSON entities; see docs/experiments/exect/exect_s4_gold_policy.md.",
            "Medication temporality gold is inferred from Prescription span text; JSON has no temporality column.",
            "Overlapping phrases across families are scored independently; see docs/experiments/exect/exect_s3_phase1_overlap_policy.md.",
            "Pooled micro F1 across eleven families is not comparable to S3 nine-family or S2 five-family headlines.",
            "Evidence quote support is diagnostic and should be reported separately from label metrics.",
        ],
        metadata={
            "prompt_version": prompt_version,
            "s3_prompt_anchor": EXECT_S3_PROMPT_VERSION,
            "s2_prompt_anchor": EXECT_S2_PROMPT_VERSION,
            "s1_prompt_anchor": EXECT_S0_S1_PROMPT_VERSION,
            **(extra or {}),
        },
    )
