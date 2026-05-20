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
from clinical_extraction.evaluation.exect import EXECT_S4_SCORER
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_DATASET,
    EXECT_S0_S1_PROMPT_VERSION,
    _as_list,
)
from clinical_extraction.programs.exect_s2 import (
    EXECT_S2_PROMPT_VERSION,
    _recover_s2_investigation_raw_values,
)
from clinical_extraction.programs.exect_s3 import (
    EXECT_S3_FIELD_FAMILIES,
    EXECT_S3_LABEL_POLICY_GUIDANCE,
    EXECT_S3_POLICY_EXAMPLES,
    EXECT_S3_PROMPT_VERSION,
    _normalize_investigation_surface,
    _recover_s3_investigation_raw_values,
    _s2_field_values_from_prediction,
    _s2_values_for_family,
    _s3_field_values_from_prediction,
)
from clinical_extraction.runs import RunMetadata
from clinical_extraction.schemas import (
    DocumentPrediction,
    ExectGoldDocument,
    ExtractedValue,
    PredictionSet,
)

EXECT_S4_SCHEMA_LEVEL = "exect_s4_field_family"
EXECT_S4_VARIANT = "exect_s4_field_family_single_pass"
EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT = (
    "exect_s4_field_family_frequency_pre_vocab_single_pass"
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
_FREQUENCY_MARKERS = (
    " per ",
    "seizure free",
    "frequency increased",
    "frequency decreased",
    "infrequent",
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
    ),
    "frequency decreased": (
        "frequency decreased",
        "frequency has decreased",
        "decreased frequency",
    ),
    "infrequent": ("infrequent",),
}
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


def build_exect_s4_module(program_variant: str = EXECT_S4_VARIANT) -> dspy.Module:
    if program_variant == EXECT_S4_VARIANT:
        return ExectS4FieldFamilyModule()
    if program_variant == EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT:
        return ExectS4FrequencyPreVocabFieldFamilyModule()
    raise ValueError(f"Unsupported ExECT S4 program variant: {program_variant!r}")


def predict_exect_s4_records(
    module: dspy.Module,
    records: list[ExectGoldDocument],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = EXECT_S4_PROMPT_VERSION,
    program_variant: str = EXECT_S4_VARIANT,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> PredictionSet:
    predictions = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        predictions.append(_predict_s4_record(module, record, program_variant=program_variant))
        if progress_callback is not None:
            progress_callback(index, total, record.document_id)
    return PredictionSet(
        dataset=EXECT_DATASET,
        schema_level=EXECT_S4_SCHEMA_LEVEL,
        predictions=predictions,
        metadata={
            "program_variant": program_variant,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "scorer_mode": EXECT_S4_SCORER,
            "s3_prompt_anchor": EXECT_S3_PROMPT_VERSION,
            "s2_prompt_anchor": EXECT_S2_PROMPT_VERSION,
        },
    )


def _predict_s4_record(
    module: dspy.Module,
    record: ExectGoldDocument,
    *,
    program_variant: str,
) -> DocumentPrediction:
    pred = module(note_text=record.text)
    values = _s2_field_values_from_prediction(pred, record)
    values.extend(_s3_field_values_from_prediction(pred, record))
    values = _replace_s4_investigation_values(values, pred, record)
    values.extend(_s4_field_values_from_prediction(pred, record))
    metadata: dict[str, object] = {"program_variant": program_variant}
    if program_variant == EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT:
        metadata["precomputed_candidates"] = {
            "seizure_frequency": build_precomputed_seizure_frequency_candidates(
                record.text
            )
        }
    return DocumentPrediction(
        document_id=record.document_id,
        dataset=EXECT_DATASET,
        schema_level=EXECT_S4_SCHEMA_LEVEL,
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
) -> list[ExtractedValue]:
    values: list[ExtractedValue] = []

    frequency_raw, _ = _recover_s4_seizure_frequency_raw_values(
        _as_list(getattr(pred, "seizure_frequency", [])),
        record.text,
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

    temporality_raw, _ = _recover_s4_medication_temporality_raw_values(
        _as_list(getattr(pred, "medication_temporality", [])),
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


def _is_non_audited_frequency_surface(canonical: str) -> bool:
    return any(pattern.search(canonical) for pattern in _NON_AUDITED_FREQUENCY_RES)


def _is_quantified_frequency_label(canonical: str) -> bool:
    return bool(_QUANTIFIED_FREQUENCY_RE.match(canonical))


def _augment_s4_seizure_frequency_co_labels(
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


def _repair_s4_seizure_frequency_surface(canonical: str) -> tuple[str, list[str]]:
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

    since_year = re.match(r"seizure free since (\d{4})$", canonical)
    if since_year:
        return repaired, flags

    if canonical.startswith("seizure free") and canonical != "seizure free":
        return "seizure free", [*flags, "s4_bridge:seizure_free_prose_collapsed"]

    return repaired, flags


def _recover_s4_seizure_frequency_raw_values(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
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
        repaired, repair_flags = _repair_s4_seizure_frequency_surface(canonical)
        flags.extend(repair_flags)
        canonical = repaired
        if _is_non_audited_frequency_surface(canonical):
            flags.append("s4_bridge:non_audited_frequency_removed")
            continue
        if not _looks_like_seizure_frequency_label(canonical):
            flags.append("s4_bridge:unsupported_frequency_removed")
            continue
        if canonical in seen:
            continue
        seen.add(canonical)
        recovered.append(canonical)

    recovered, co_label_flags = _augment_s4_seizure_frequency_co_labels(recovered, note_text)
    flags.extend(co_label_flags)
    return recovered, flags


_COUNT_WORDS = {
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
}
_PERIOD_UNIT = r"weeks?|months?|days?|years?"
_QUANTIFIED_FREQUENCY_NOTE_RE = re.compile(
    rf"\b(?P<count>one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
    rf"(?:seizures?\s+)?(?:every|per)\s+(?P<period_count>\d+\s+)?"
    rf"(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)
_ZERO_RATE_FREQUENCY_NOTE_RE = re.compile(
    rf"\b(?:no|zero|0)\s+seizures?\s+per\s+(?P<period_count>\d+)\s+"
    rf"(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)
_SEIZURE_EVERY_N_PERIOD_RE = re.compile(
    rf"seizures?\s+every\s+"
    rf"(?P<period_count>one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
    rf"(?P<period>{_PERIOD_UNIT})\b",
    flags=re.IGNORECASE,
)


def _normalize_period_unit(period: str) -> str:
    return period.lower().rstrip("s")
_SEIZURE_FREE_SINCE_RE = re.compile(
    r"seizure[- ]free since (\d{4})",
    flags=re.IGNORECASE,
)


def _accept_precomputed_seizure_frequency_candidate(label: str) -> str | None:
    canonical = canonical_clinical_phrase(label)
    if not canonical or _looks_like_seizure_type_not_frequency(canonical):
        return None
    repaired, _ = _repair_s4_seizure_frequency_surface(canonical)
    if _is_non_audited_frequency_surface(repaired):
        return None
    if not _looks_like_seizure_frequency_label(repaired):
        return None
    return repaired


def build_precomputed_seizure_frequency_candidates(note_text: str) -> list[str]:
    """Build note-anchored ExECT seizure-frequency candidates for narrow H2 probes."""
    from clinical_extraction.gan.temporal_candidates import (
        build_temporal_frequency_candidates_from_note,
    )

    candidates: set[str] = set()
    note_lower = note_text.lower()

    for label, cues in _FREQUENCY_CO_LABEL_CUES.items():
        if any(cue in note_lower for cue in cues):
            accepted = _accept_precomputed_seizure_frequency_candidate(label)
            if accepted:
                candidates.add(accepted)

    if "seizure free" in note_lower:
        since_match = _SEIZURE_FREE_SINCE_RE.search(note_text)
        if since_match:
            accepted = _accept_precomputed_seizure_frequency_candidate(
                f"seizure free since {since_match.group(1)}"
            )
        else:
            accepted = _accept_precomputed_seizure_frequency_candidate("seizure free")
        if accepted:
            candidates.add(accepted)

    for match in _QUANTIFIED_FREQUENCY_NOTE_RE.finditer(note_text):
        count_token = match.group("count").lower()
        count = _COUNT_WORDS.get(count_token, count_token)
        period_count = (match.group("period_count") or "1 ").strip().split()[0]
        period = _normalize_period_unit(match.group("period"))
        accepted = _accept_precomputed_seizure_frequency_candidate(
            f"{count} per {period_count} {period}"
        )
        if accepted:
            candidates.add(accepted)

    for match in _ZERO_RATE_FREQUENCY_NOTE_RE.finditer(note_text):
        period_count = match.group("period_count")
        period = _normalize_period_unit(match.group("period"))
        accepted = _accept_precomputed_seizure_frequency_candidate(
            f"0 per {period_count} {period}"
        )
        if accepted:
            candidates.add(accepted)

    for match in _SEIZURE_EVERY_N_PERIOD_RE.finditer(note_text):
        period_token = match.group("period_count").lower()
        period_count = _COUNT_WORDS.get(period_token, period_token)
        period = _normalize_period_unit(match.group("period"))
        accepted = _accept_precomputed_seizure_frequency_candidate(
            f"1 per {period_count} {period}"
        )
        if accepted:
            candidates.add(accepted)

    for temporal_candidate in build_temporal_frequency_candidates_from_note(note_text):
        accepted = _accept_precomputed_seizure_frequency_candidate(
            temporal_candidate.canonical_label
        )
        if accepted:
            candidates.add(accepted)

    return sorted(candidates)


def format_note_with_precomputed_seizure_frequency_candidates(note_text: str) -> str:
    """Inject seizure-frequency-only audited candidates before the clinical note."""
    frequency_candidates = build_precomputed_seizure_frequency_candidates(note_text)
    lines = [
        "Precomputed benchmark-facing candidates (soft hints; emit only when note-supported):",
        f"seizure_frequency: {', '.join(frequency_candidates)}",
        "",
        "---",
        "",
        note_text,
    ]
    return "\n".join(lines)


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
) -> RunMetadata:
    return RunMetadata(
        run_id=run_id,
        dataset=EXECT_DATASET,
        split_name=split_name,
        model_provider=model_provider,
        model_name=model_name,
        schema_level=EXECT_S4_SCHEMA_LEVEL,
        program_variant=program_variant,
        scorer_mode=EXECT_S4_SCORER,
        metric_caveats=[
            "These are partial ExECT S4 diagnostics (S3 + seizure frequency + Rx temporality), not published ExECTv2 Table 1 reproduction.",
            "S3 label-policy bridges from frozen v1.2 are reused for S1–S3 families without editing exect_s3.py.",
            "Seizure-frequency gold uses SeizureFrequency JSON entities; see docs/exect_s4_gold_policy.md.",
            "Medication temporality gold is inferred from Prescription span text; JSON has no temporality column.",
            "Overlapping phrases across families are scored independently; see docs/exect_s3_phase1_overlap_policy.md.",
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
