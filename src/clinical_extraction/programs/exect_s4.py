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
    _evidence_at,
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
from clinical_extraction.exect.frequency_payload import (
    build_exect_frequency_pre_vocab_labels as build_precomputed_seizure_frequency_candidates,
    build_exect_frequency_pre_vocab_labels_high_precision as build_precomputed_seizure_frequency_candidates_high_precision,
    format_exect_frequency_pre_vocab_note as format_note_with_precomputed_seizure_frequency_candidates,
    format_exect_frequency_pre_vocab_note_high_precision as format_note_with_precomputed_seizure_frequency_candidates_high_precision,
    recover_exect_frequency_benchmark_values as _recover_s4_seizure_frequency_raw_values,
    recover_exect_frequency_benchmark_values_with_multi_label_retention as _recover_s4_seizure_frequency_multi_label_retention_raw_values,
    recover_exect_frequency_benchmark_values_with_post_merge as _recover_s4_seizure_frequency_post_merge_raw_values,
    repair_exect_frequency_surface as _repair_s4_seizure_frequency_surface,
)
from clinical_extraction.exect.primitives import (
    recover_exect_medication_temporality_non_asm_dose_current_guard,
    recover_exect_medication_temporality_non_asm_guard,
    recover_exect_medication_temporality_with_post_classifier,
    recover_exect_annotated_medication_non_asm_brand_alias_guard,
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
EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT = (
    "exect_s5_am_guard_non_asm_brand_alias_v1"
)
EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT = (
    "exect_s5_frequency_pre_vocab_am_guard_non_asm_brand_alias_v1"
)
EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT = (
    "exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1"
)
EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT = (
    "exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2"
)
EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT = (
    "exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b"
)
EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT = (
    "exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_v1"
)
EXECT_S5_CORE_FIELD_FAMILIES = (
    "diagnosis",
    "seizure_type",
    "annotated_medication",
    "investigation",
    "seizure_frequency",
)
EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT = (
    "exect_s5_core_field_family_parallel_v2b"
)
EXECT_S5_STAGE_GRAPH_BY_VARIANT = {
    EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT: "g2_s5_core_family_parallel",
}
EXECT_S4_PROMPT_VERSION = "exect_s4_field_family_v1_2_label_policy"
EXECT_S4_PROMPT_VERSION_V1_3 = "exect_s4_field_family_v1_3_qualitative_evidence_gate"
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
    "A patient can experience temporary seizure freedom in the past but have increased "
    "frequency currently. Extract BOTH (e.g. seizure free + frequency increased or 4 per 3 week) "
    "if the note mentions both.",
)
EXECT_S4_FREQUENCY_QUALITATIVE_EVIDENCE_GATE_GUIDANCE = (
    "Qualitative labels (infrequent, frequency same, frequency increased, frequency decreased) "
    "require explicit supporting wording in the clinical note — precomputed candidate hints alone "
    "are insufficient.",
    "Do not emit a qualitative label whose sole rationale is presence in the injected candidate "
    "line; evidence quotes must come from the note body below the --- separator.",
    "Medication control, rescue-medication use, or seizure-type descriptions do not justify "
    "qualitative frequency labels unless frequency change is explicitly stated.",
    "Prefer abstaining over weak qualitative inference; do not invent frequency labels in "
    "gold-empty notes.",
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
EXECT_S4_V1_3_POLICY_EXAMPLES = (
    {
        "case": "s4_qual_no_infrequent_without_wording",
        "note_fragment": (
            "He has about one focal seizure every three weeks and the frequency has increased."
        ),
        "benchmark_output": {
            "seizure_frequency": ["1 per 3 week", "frequency increased"],
        },
        "policy": "Do not add infrequent without explicit infrequent/rare wording in the note.",
    },
    {
        "case": "s4_qual_med_control_not_freq_decreased",
        "note_fragment": "Seizures are well controlled on current lamotrigine dose.",
        "benchmark_output": {"seizure_frequency": []},
        "policy": "Medication-control language alone does not justify frequency decreased.",
    },
    {
        "case": "s4_qual_infrequent_when_stated",
        "note_fragment": "She continues to have infrequent focal seizures.",
        "benchmark_output": {"seizure_frequency": ["infrequent"]},
        "policy": "Emit infrequent when the note explicitly uses infrequent or equivalent wording.",
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


def resolve_exect_s4_frequency_label_policy(
    prompt_version: str,
) -> tuple[tuple[str, ...], tuple[dict[str, object], ...]]:
    """Return frequency label-policy guidance and examples for the requested prompt version."""
    if prompt_version == EXECT_S4_PROMPT_VERSION_V1_3:
        guidance = (
            *EXECT_S4_FREQUENCY_LABEL_POLICY_GUIDANCE,
            *EXECT_S4_FREQUENCY_QUALITATIVE_EVIDENCE_GATE_GUIDANCE,
        )
        return guidance, (*EXECT_S4_POLICY_EXAMPLES, *EXECT_S4_V1_3_POLICY_EXAMPLES)
    return EXECT_S4_FREQUENCY_LABEL_POLICY_GUIDANCE, EXECT_S4_POLICY_EXAMPLES


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


class ExectS4FieldFamilyV13Signature(ExectS4FieldFamilySignature):
    """Extract audited ExECT S4 benchmark-facing field families (v1.3 qualitative evidence gate).

    Same eleven-family pass as v1.2, plus qualitative evidence-gate rules for seizure frequency:
    - Emit infrequent, frequency same, frequency increased, or frequency decreased only when
      the note contains explicit supporting wording; candidate hints alone are insufficient.
    - Do not cite the injected candidate block as evidence; quotes must come from the note body.
    - Medication-control or seizure-type wording does not justify qualitative frequency labels
      unless frequency change is explicitly stated.
    - Prefer abstaining over weak qualitative inference.
    """


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


class ExectS4FrequencyPreVocabV13FieldFamilyModule(dspy.Module):
    """Single-pass S4 extractor with v1.3 qualitative evidence gate and pre-vocab hints."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS4FieldFamilyV13Signature)

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


class ExectS5SeizureFrequencyVerifierSignature(dspy.Signature):
    """Verify ExECT S5 seizure-frequency labels against note evidence.

    This verifier is confirm-first and reject-only. It may keep or drop initial
    seizure_frequency labels, but it must not add labels, repair false negatives,
    change benchmark surfaces, or reinterpret gold policy.

    Evidence must be an exact quote from the clinical note, not from the injected
    precomputed-candidate block.

    Verification Policy Rules:
    1. Synonyms of Seizure Freedom: Phrases indicating no seizures since an event or review
       (e.g., "no further seizures", "seizure free since last review", "remains clear") are
       valid and sufficient support for the "seizure free" label. Do not reject them.
    2. Zero-rate Intervals: Statements specifying the timing of the last seizure (e.g.,
       "last event was 3 weeks ago", "last seizure in April") support a zero-rate label
       (e.g., "0 per 3 week" or "0 per 1 month"). Do not reject zero-rate labels due to
       boundary interpretation.
    3. Diagnostic Modifiers: A patient's current status (e.g., "seizure free") can coexist
       with a general diagnostic history (e.g., "infrequent focal seizures"). Confirm the
       current status label if supported by the note text, even if a diagnostic category
       seems to conflict.
    4. Seizure Free Since Year: A statement specifying that the last seizure occurred in a
       given year (e.g., "last event September 2019", "last seizure in 2017") directly
       supports the label "seizure free since YEAR". Do not reject it.
    5. Frequency Changes: "frequency increased" and "frequency decreased" are valid benchmark
       qualitative change labels. If the note mentions seizures happening "more frequently",
       "worse", "less frequently", or "improved", confirm these labels even if they appear in
       the context of treatment adjustments or diagnostic summaries.
    6. Coexisting Labels: ExECT gold annotations routinely allow multiple qualitative and
       quantified labels to coexist (e.g., "infrequent" and "seizure free" can both be confirmed
       if both are supported by phrases in the note). Do not drop one label just because you
       think another label is "more accurate" or "contradicts" it logically.
    """

    note_text: str = dspy.InputField(desc="Clinical note text without candidate block")
    candidate_labels: list[str] = dspy.InputField(
        desc="Precomputed frequency candidates used as soft hints by the extractor."
    )
    initial_seizure_frequency: list[str] = dspy.InputField(
        desc="Initial seizure_frequency labels from the extraction pass."
    )
    initial_seizure_frequency_evidence: list[str] = dspy.InputField(
        desc="Initial evidence quotes, aligned by index."
    )
    seizure_frequency: list[str] = dspy.OutputField(
        desc="Confirmed subset of initial seizure_frequency labels; add no labels."
    )
    seizure_frequency_evidence: list[str] = dspy.OutputField(
        desc=(
            "Exact, verbatim note quotes supporting each confirmed label, aligned by index. "
            "Do NOT paraphrase, summarize, or alter capitalization/punctuation. "
            "Each evidence element MUST exist as an exact case-sensitive or case-insensitive substring within note_text."
        )
    )
    verifier_decision: str = dspy.OutputField(
        desc="confirm when all initial labels are supported; repair when any are dropped."
    )
    verifier_reason: str = dspy.OutputField(
        desc="Brief evidence-based explanation for dropped labels."
    )


class ExectS5SeizureFrequencyVerifierV2Signature(dspy.Signature):
    """Verify ExECT S5 seizure-frequency labels (v2 residual-tuned policy).

    Confirm-first reject-only verifier extending v1 A3 rules with residual-driven policies
    for qualitative evidence and temporal/current scope (A1 categories 1 and 3).

    Verification Policy Rules:
    1. Synonyms of Seizure Freedom: Phrases indicating no seizures since an event or review
       (e.g., "no further seizures", "seizure free since last review", "remains clear") are
       valid and sufficient support for the "seizure free" label. Do not reject them.
    2. Zero-rate Intervals: Statements specifying the timing of the last seizure (e.g.,
       "last event was 3 weeks ago", "last seizure in April") support a zero-rate label
       (e.g., "0 per 3 week" or "0 per 1 month"). Do not reject zero-rate labels due to
       boundary interpretation.
    3. Diagnostic Modifiers: A patient's current status (e.g., "seizure free") can coexist
       with a general diagnostic history (e.g., "infrequent focal seizures"). Confirm the
       current status label if supported by the note text, even if a diagnostic category
       seems to conflict.
    4. Seizure Free Since Year: A statement specifying that the last seizure occurred in a
       given year (e.g., "last event September 2019", "last seizure in 2017") directly
       supports the label "seizure free since YEAR". Do not reject it.
    5. Frequency Changes: "frequency increased" and "frequency decreased" are valid benchmark
       qualitative change labels. If the note mentions seizures happening "more frequently",
       "worse", "less frequently", or "improved", confirm these labels even if they appear in
       the context of treatment adjustments or diagnostic summaries.
    6. Coexisting Labels: ExECT gold annotations routinely allow multiple qualitative and
       quantified labels to coexist (e.g., "infrequent" and "seizure free" can both be confirmed
       if both are supported by phrases in the note). Do not drop one label just because you
       think another label is "more accurate" or "contradicts" it logically.
    7. Historical vs Current Scope: When the note states both a historical quantified rate and a
       current status (e.g., current weekly seizures plus a past historical rate), reject historical
       quantified rates that are not supported as current benchmark-facing labels. Limited past
       seizure-free intervals (e.g., "up to five weeks seizure free") do not support generic
       "seizure free" when the note also states current ongoing seizures.
    8. Qualitative Evidence Requirement: Reject infrequent, frequency same, frequency increased,
       and frequency decreased unless the confirming evidence quote contains explicit
       frequency-change or qualitative wording from the note — not medication-control-only or
       seizure-type-only context.
    9. Unsupported Quantified Inference: Reject quantified rates inferred only from vague temporal
       anchors (e.g., "most recent seizure September 2019" alone) when the note supports only
       qualitative change or seizure-free-since-year labels.
    """

    note_text: str = dspy.InputField(desc="Clinical note text without candidate block")
    candidate_labels: list[str] = dspy.InputField(
        desc="Precomputed frequency candidates used as soft hints by the extractor."
    )
    initial_seizure_frequency: list[str] = dspy.InputField(
        desc="Initial seizure_frequency labels from the extraction pass."
    )
    initial_seizure_frequency_evidence: list[str] = dspy.InputField(
        desc="Initial evidence quotes, aligned by index."
    )
    seizure_frequency: list[str] = dspy.OutputField(
        desc="Confirmed subset of initial seizure_frequency labels; add no labels."
    )
    seizure_frequency_evidence: list[str] = dspy.OutputField(
        desc=(
            "Exact, verbatim note quotes supporting each confirmed label, aligned by index. "
            "Do NOT paraphrase, summarize, or alter capitalization/punctuation. "
            "Each evidence element MUST exist as an exact case-sensitive or case-insensitive substring within note_text."
        )
    )
    verifier_decision: str = dspy.OutputField(
        desc="confirm when all initial labels are supported; repair when any are dropped."
    )
    verifier_reason: str = dspy.OutputField(
        desc="Brief evidence-based explanation for dropped labels."
    )


class ExectS5SeizureFrequencyVerifierModule(dspy.Module):
    """Confirm-first reject-only verifier for ExECT S5 seizure frequency."""

    def __init__(self) -> None:
        super().__init__()
        self.verify = dspy.Predict(ExectS5SeizureFrequencyVerifierSignature)

    def forward(
        self,
        note_text: str,
        *,
        candidate_labels: list[str],
        initial_seizure_frequency: list[str],
        initial_seizure_frequency_evidence: list[str],
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            candidate_labels=candidate_labels,
            initial_seizure_frequency=initial_seizure_frequency,
            initial_seizure_frequency_evidence=initial_seizure_frequency_evidence,
        )


class ExectS5SeizureFrequencyVerifierV2Module(dspy.Module):
    """Confirm-first reject-only verifier with v2 residual-tuned policy."""

    def __init__(self) -> None:
        super().__init__()
        self.verify = dspy.Predict(ExectS5SeizureFrequencyVerifierV2Signature)

    def forward(
        self,
        note_text: str,
        *,
        candidate_labels: list[str],
        initial_seizure_frequency: list[str],
        initial_seizure_frequency_evidence: list[str],
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            candidate_labels=candidate_labels,
            initial_seizure_frequency=initial_seizure_frequency,
            initial_seizure_frequency_evidence=initial_seizure_frequency_evidence,
        )


class ExectS5FrequencyPreVocabAmGuardFrequencyVerifyModule(dspy.Module):
    """S5 pre-vocab extractor followed by reject-only frequency verification."""

    def __init__(self) -> None:
        super().__init__()
        self.extractor = ExectS4FrequencyPreVocabFieldFamilyModule()
        self.verifier = ExectS5SeizureFrequencyVerifierModule()

    def forward(self, note_text: str) -> dspy.Prediction:
        initial = self.extractor(note_text=note_text)
        initial_frequency = _as_list(getattr(initial, "seizure_frequency", []))
        initial_frequency_evidence = _as_list(
            getattr(initial, "seizure_frequency_evidence", [])
        )
        candidates = build_precomputed_seizure_frequency_candidates(note_text)
        verified = self.verifier(
            note_text=note_text,
            candidate_labels=candidates,
            initial_seizure_frequency=initial_frequency,
            initial_seizure_frequency_evidence=initial_frequency_evidence,
        )
        guarded = _apply_exect_s5_frequency_verifier_guards(
            note_text=note_text,
            initial_frequency=initial_frequency,
            verified=verified,
        )
        return dspy.Prediction(
            diagnosis=_as_list(getattr(initial, "diagnosis", [])),
            diagnosis_evidence=_as_list(getattr(initial, "diagnosis_evidence", [])),
            seizure_type=_as_list(getattr(initial, "seizure_type", [])),
            seizure_type_evidence=_as_list(getattr(initial, "seizure_type_evidence", [])),
            annotated_medication=_as_list(getattr(initial, "annotated_medication", [])),
            annotated_medication_evidence=_as_list(
                getattr(initial, "annotated_medication_evidence", [])
            ),
            investigation=_as_list(getattr(initial, "investigation", [])),
            investigation_evidence=_as_list(getattr(initial, "investigation_evidence", [])),
            comorbidity=_as_list(getattr(initial, "comorbidity", [])),
            comorbidity_evidence=_as_list(getattr(initial, "comorbidity_evidence", [])),
            birth_history=_as_list(getattr(initial, "birth_history", [])),
            birth_history_evidence=_as_list(getattr(initial, "birth_history_evidence", [])),
            onset=_as_list(getattr(initial, "onset", [])),
            onset_evidence=_as_list(getattr(initial, "onset_evidence", [])),
            epilepsy_cause=_as_list(getattr(initial, "epilepsy_cause", [])),
            epilepsy_cause_evidence=_as_list(getattr(initial, "epilepsy_cause_evidence", [])),
            when_diagnosed=_as_list(getattr(initial, "when_diagnosed", [])),
            when_diagnosed_evidence=_as_list(getattr(initial, "when_diagnosed_evidence", [])),
            seizure_frequency=_as_list(getattr(guarded, "seizure_frequency", [])),
            seizure_frequency_evidence=_as_list(
                getattr(guarded, "seizure_frequency_evidence", [])
            ),
            medication_temporality=_as_list(getattr(initial, "medication_temporality", [])),
            medication_temporality_evidence=_as_list(
                getattr(initial, "medication_temporality_evidence", [])
            ),
            frequency_verifier_flags=_as_list(
                getattr(guarded, "frequency_verifier_flags", [])
            ),
            frequency_verifier_decision=getattr(guarded, "verifier_decision", None),
            frequency_verifier_reason=getattr(guarded, "verifier_reason", None),
            initial_seizure_frequency=initial_frequency,
            precomputed_seizure_frequency_candidates=candidates,
        )


class ExectS5FrequencyPreVocabAmGuardFrequencyVerifyV2Module(dspy.Module):
    """S5 v1.3 extractor + v2 residual-tuned reject-only frequency verification."""

    def __init__(self) -> None:
        super().__init__()
        self.extractor = ExectS4FrequencyPreVocabV13FieldFamilyModule()
        self.verifier = ExectS5SeizureFrequencyVerifierV2Module()

    def forward(self, note_text: str) -> dspy.Prediction:
        initial = self.extractor(note_text=note_text)
        initial_frequency = _as_list(getattr(initial, "seizure_frequency", []))
        initial_frequency_evidence = _as_list(
            getattr(initial, "seizure_frequency_evidence", [])
        )
        candidates = build_precomputed_seizure_frequency_candidates(note_text)
        verified = self.verifier(
            note_text=note_text,
            candidate_labels=candidates,
            initial_seizure_frequency=initial_frequency,
            initial_seizure_frequency_evidence=initial_frequency_evidence,
        )
        guarded = _apply_exect_s5_frequency_verifier_guards(
            note_text=note_text,
            initial_frequency=initial_frequency,
            verified=verified,
            strict_qualitative=True,
        )
        return dspy.Prediction(
            diagnosis=_as_list(getattr(initial, "diagnosis", [])),
            diagnosis_evidence=_as_list(getattr(initial, "diagnosis_evidence", [])),
            seizure_type=_as_list(getattr(initial, "seizure_type", [])),
            seizure_type_evidence=_as_list(getattr(initial, "seizure_type_evidence", [])),
            annotated_medication=_as_list(getattr(initial, "annotated_medication", [])),
            annotated_medication_evidence=_as_list(
                getattr(initial, "annotated_medication_evidence", [])
            ),
            investigation=_as_list(getattr(initial, "investigation", [])),
            investigation_evidence=_as_list(getattr(initial, "investigation_evidence", [])),
            comorbidity=_as_list(getattr(initial, "comorbidity", [])),
            comorbidity_evidence=_as_list(getattr(initial, "comorbidity_evidence", [])),
            birth_history=_as_list(getattr(initial, "birth_history", [])),
            birth_history_evidence=_as_list(getattr(initial, "birth_history_evidence", [])),
            onset=_as_list(getattr(initial, "onset", [])),
            onset_evidence=_as_list(getattr(initial, "onset_evidence", [])),
            epilepsy_cause=_as_list(getattr(initial, "epilepsy_cause", [])),
            epilepsy_cause_evidence=_as_list(getattr(initial, "epilepsy_cause_evidence", [])),
            when_diagnosed=_as_list(getattr(initial, "when_diagnosed", [])),
            when_diagnosed_evidence=_as_list(getattr(initial, "when_diagnosed_evidence", [])),
            seizure_frequency=_as_list(getattr(guarded, "seizure_frequency", [])),
            seizure_frequency_evidence=_as_list(
                getattr(guarded, "seizure_frequency_evidence", [])
            ),
            medication_temporality=_as_list(getattr(initial, "medication_temporality", [])),
            medication_temporality_evidence=_as_list(
                getattr(initial, "medication_temporality_evidence", [])
            ),
            frequency_verifier_flags=_as_list(
                getattr(guarded, "frequency_verifier_flags", [])
            ),
            frequency_verifier_decision=getattr(guarded, "verifier_decision", None),
            frequency_verifier_reason=getattr(guarded, "verifier_reason", None),
            initial_seizure_frequency=initial_frequency,
            precomputed_seizure_frequency_candidates=candidates,
        )


class ExectS5FrequencyPreVocabAmGuardFrequencyVerifyV2bModule(dspy.Module):
    """S5 v1.2 extractor + v2 verifier rules only (no v1.3 prompt, no strict qualitative guard)."""

    def __init__(self) -> None:
        super().__init__()
        self.extractor = ExectS4FrequencyPreVocabFieldFamilyModule()
        self.verifier = ExectS5SeizureFrequencyVerifierV2Module()

    def forward(self, note_text: str) -> dspy.Prediction:
        initial = self.extractor(note_text=note_text)
        initial_frequency = _as_list(getattr(initial, "seizure_frequency", []))
        initial_frequency_evidence = _as_list(
            getattr(initial, "seizure_frequency_evidence", [])
        )
        candidates = build_precomputed_seizure_frequency_candidates(note_text)
        verified = self.verifier(
            note_text=note_text,
            candidate_labels=candidates,
            initial_seizure_frequency=initial_frequency,
            initial_seizure_frequency_evidence=initial_frequency_evidence,
        )
        guarded = _apply_exect_s5_frequency_verifier_guards(
            note_text=note_text,
            initial_frequency=initial_frequency,
            verified=verified,
            strict_qualitative=False,
        )
        return dspy.Prediction(
            diagnosis=_as_list(getattr(initial, "diagnosis", [])),
            diagnosis_evidence=_as_list(getattr(initial, "diagnosis_evidence", [])),
            seizure_type=_as_list(getattr(initial, "seizure_type", [])),
            seizure_type_evidence=_as_list(getattr(initial, "seizure_type_evidence", [])),
            annotated_medication=_as_list(getattr(initial, "annotated_medication", [])),
            annotated_medication_evidence=_as_list(
                getattr(initial, "annotated_medication_evidence", [])
            ),
            investigation=_as_list(getattr(initial, "investigation", [])),
            investigation_evidence=_as_list(getattr(initial, "investigation_evidence", [])),
            comorbidity=_as_list(getattr(initial, "comorbidity", [])),
            comorbidity_evidence=_as_list(getattr(initial, "comorbidity_evidence", [])),
            birth_history=_as_list(getattr(initial, "birth_history", [])),
            birth_history_evidence=_as_list(getattr(initial, "birth_history_evidence", [])),
            onset=_as_list(getattr(initial, "onset", [])),
            onset_evidence=_as_list(getattr(initial, "onset_evidence", [])),
            epilepsy_cause=_as_list(getattr(initial, "epilepsy_cause", [])),
            epilepsy_cause_evidence=_as_list(getattr(initial, "epilepsy_cause_evidence", [])),
            when_diagnosed=_as_list(getattr(initial, "when_diagnosed", [])),
            when_diagnosed_evidence=_as_list(getattr(initial, "when_diagnosed_evidence", [])),
            seizure_frequency=_as_list(getattr(guarded, "seizure_frequency", [])),
            seizure_frequency_evidence=_as_list(
                getattr(guarded, "seizure_frequency_evidence", [])
            ),
            medication_temporality=_as_list(getattr(initial, "medication_temporality", [])),
            medication_temporality_evidence=_as_list(
                getattr(initial, "medication_temporality_evidence", [])
            ),
            frequency_verifier_flags=_as_list(
                getattr(guarded, "frequency_verifier_flags", [])
            ),
            frequency_verifier_decision=getattr(guarded, "verifier_decision", None),
            frequency_verifier_reason=getattr(guarded, "verifier_reason", None),
            initial_seizure_frequency=initial_frequency,
            precomputed_seizure_frequency_candidates=candidates,
        )


_S5_CORE_FAMILY_POLICY_OUTPUT_KEYS = {
    "diagnosis": frozenset({"diagnosis"}),
    "seizure_type": frozenset({"seizure_type"}),
    "annotated_medication": frozenset({"annotated_medication"}),
    "investigation": frozenset({"investigation"}),
    "seizure_frequency": frozenset({"seizure_frequency"}),
}


def _s5_core_policy_examples_for_family(
    examples: tuple[dict[str, object], ...],
    field_name: str,
) -> tuple[dict[str, object], ...]:
    keys = _S5_CORE_FAMILY_POLICY_OUTPUT_KEYS[field_name]
    return tuple(
        example
        for example in examples
        if any(key in example.get("benchmark_output", {}) for key in keys)
    )


def _format_s5_core_family_policy_examples_block(
    examples: tuple[dict[str, object], ...],
) -> str:
    if not examples:
        return ""
    lines = ["", "Boundary examples:"]
    for example in examples:
        case = example.get("case", "example")
        fragment = example.get("note_fragment", "")
        output = example.get("benchmark_output", {})
        policy = example.get("policy", "")
        lines.append(f'- {case}: "{fragment}" -> {output}. {policy}')
    return "\n".join(lines)


class ExectS5CoreInvestigationSignature(dspy.Signature):
    """Extract benchmark-facing ExECT investigation labels only."""

    note_text: str = dspy.InputField(desc="Full clinical note text for investigation extraction")
    investigation: list[str] = dspy.OutputField(
        desc=(
            "Performed investigation results as modality+result labels "
            "(e.g. eeg normal, mri abnormal). Do not emit unknown for planned scans."
        )
    )
    investigation_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each investigation label, aligned by index."
    )


class ExectS5CoreSeizureFrequencySignature(dspy.Signature):
    """Extract benchmark-facing ExECT seizure frequency labels only."""

    note_text: str = dspy.InputField(
        desc="Clinical note text, optionally with injected pre-vocabulary frequency candidates"
    )
    seizure_frequency: list[str] = dspy.OutputField(
        desc=(
            "Seizure frequency benchmark labels: N per N week/month/day/year quantified rates, "
            "zero rates, frequency increased/decreased, infrequent, seizure free, "
            "seizure free since YEAR — not seizure-type names."
        )
    )
    seizure_frequency_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each seizure-frequency label, aligned by index."
    )


def build_exect_s5_core_family_specific_signature(
    field_name: str,
    prompt_version: str = EXECT_S4_PROMPT_VERSION,
) -> type[dspy.Signature]:
    """Build a per-family S5-core signature enriched with v1.2 label-policy examples."""
    from clinical_extraction.programs.exect_s0_s1 import (
        ExectS0S1DiagnosisSignature,
        ExectS0S1MedicationSignature,
        ExectS0S1SeizureTypeSignature,
    )
    from clinical_extraction.programs.exect_s2 import EXECT_S2_POLICY_EXAMPLES

    if field_name not in _S5_CORE_FAMILY_POLICY_OUTPUT_KEYS:
        raise ValueError(f"Unsupported ExECT S5 core field family: {field_name!r}")

    base_by_field = {
        "diagnosis": ExectS0S1DiagnosisSignature,
        "seizure_type": ExectS0S1SeizureTypeSignature,
        "annotated_medication": ExectS0S1MedicationSignature,
        "investigation": ExectS5CoreInvestigationSignature,
        "seizure_frequency": ExectS5CoreSeizureFrequencySignature,
    }
    policy_examples = (*EXECT_S4_POLICY_EXAMPLES, *EXECT_S2_POLICY_EXAMPLES)
    if prompt_version == EXECT_S4_PROMPT_VERSION_V1_3:
        policy_examples = (*policy_examples, *EXECT_S4_V1_3_POLICY_EXAMPLES)
    family_examples = _s5_core_policy_examples_for_family(policy_examples, field_name)
    base_signature = base_by_field[field_name]
    doc = (base_signature.__doc__ or "") + _format_s5_core_family_policy_examples_block(
        family_examples
    )
    suffix = {
        "diagnosis": "Diagnosis",
        "seizure_type": "SeizureType",
        "annotated_medication": "Medication",
        "investigation": "Investigation",
        "seizure_frequency": "SeizureFrequency",
    }[field_name]
    class_name = f"ExectS5Core{suffix}PolicySignature"
    return type(class_name, (base_signature,), {"__doc__": doc})


class ExectS5CoreFieldFamilyParallelV2bModule(dspy.Module):
    """Full-note parallel per-family S5-core extraction with v2b frequency post-stack."""

    def __init__(
        self,
        *,
        prompt_version: str = EXECT_S4_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.extract_diagnosis = dspy.ChainOfThought(
            build_exect_s5_core_family_specific_signature("diagnosis", prompt_version)
        )
        self.extract_seizure_type = dspy.ChainOfThought(
            build_exect_s5_core_family_specific_signature("seizure_type", prompt_version)
        )
        self.extract_medication = dspy.ChainOfThought(
            build_exect_s5_core_family_specific_signature(
                "annotated_medication",
                prompt_version,
            )
        )
        self.extract_investigation = dspy.ChainOfThought(
            build_exect_s5_core_family_specific_signature("investigation", prompt_version)
        )
        self.extract_seizure_frequency = dspy.ChainOfThought(
            build_exect_s5_core_family_specific_signature(
                "seizure_frequency",
                prompt_version,
            )
        )
        self.verifier = ExectS5SeizureFrequencyVerifierV2Module()

    def forward(self, note_text: str) -> dspy.Prediction:
        diagnosis = self.extract_diagnosis(note_text=note_text)
        seizure_type = self.extract_seizure_type(note_text=note_text)
        medication = self.extract_medication(note_text=note_text)
        investigation = self.extract_investigation(note_text=note_text)
        frequency_note = format_note_with_precomputed_seizure_frequency_candidates(note_text)
        frequency = self.extract_seizure_frequency(note_text=frequency_note)
        initial_frequency = _as_list(getattr(frequency, "seizure_frequency", []))
        initial_frequency_evidence = _as_list(
            getattr(frequency, "seizure_frequency_evidence", [])
        )
        candidates = build_precomputed_seizure_frequency_candidates(note_text)
        verified = self.verifier(
            note_text=note_text,
            candidate_labels=candidates,
            initial_seizure_frequency=initial_frequency,
            initial_seizure_frequency_evidence=initial_frequency_evidence,
        )
        guarded = _apply_exect_s5_frequency_verifier_guards(
            note_text=note_text,
            initial_frequency=initial_frequency,
            verified=verified,
            strict_qualitative=False,
        )
        return dspy.Prediction(
            diagnosis=_as_list(getattr(diagnosis, "diagnosis", [])),
            diagnosis_evidence=_as_list(getattr(diagnosis, "diagnosis_evidence", [])),
            seizure_type=_as_list(getattr(seizure_type, "seizure_type", [])),
            seizure_type_evidence=_as_list(
                getattr(seizure_type, "seizure_type_evidence", [])
            ),
            annotated_medication=_as_list(
                getattr(medication, "annotated_medication", [])
            ),
            annotated_medication_evidence=_as_list(
                getattr(medication, "annotated_medication_evidence", [])
            ),
            investigation=_as_list(getattr(investigation, "investigation", [])),
            investigation_evidence=_as_list(
                getattr(investigation, "investigation_evidence", [])
            ),
            seizure_frequency=_as_list(getattr(guarded, "seizure_frequency", [])),
            seizure_frequency_evidence=_as_list(
                getattr(guarded, "seizure_frequency_evidence", [])
            ),
            frequency_verifier_flags=_as_list(
                getattr(guarded, "frequency_verifier_flags", [])
            ),
            frequency_verifier_decision=getattr(guarded, "verifier_decision", None),
            frequency_verifier_reason=getattr(guarded, "verifier_reason", None),
            initial_seizure_frequency=initial_frequency,
            precomputed_seizure_frequency_candidates=candidates,
        )


def stage_graph_id_for_s5_program_variant(program_variant: str) -> str | None:
    return EXECT_S5_STAGE_GRAPH_BY_VARIANT.get(program_variant)


def build_exect_s4_module(program_variant: str = EXECT_S4_VARIANT) -> dspy.Module:
    if program_variant in {
        EXECT_S4_VARIANT,
        EXECT_S4_L1_VARIANT,
        EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
        EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
        EXECT_S4_MT_GUARD_NON_ASM_DOSE_CURRENT_VARIANT,
        EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
        EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT,
        EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT,
    }:
        return ExectS4FieldFamilyModule()
    if program_variant in {
        EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
    }:
        return ExectS4FrequencyPreVocabFieldFamilyModule()
    if program_variant in {
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
    }:
        return ExectS5FrequencyPreVocabAmGuardFrequencyVerifyModule()
    if program_variant == EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT:
        return ExectS5FrequencyPreVocabAmGuardFrequencyVerifyV2Module()
    if program_variant == EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT:
        return ExectS5FrequencyPreVocabAmGuardFrequencyVerifyV2bModule()
    if program_variant == EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT:
        return ExectS5CoreFieldFamilyParallelV2bModule()
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


def _build_s5_core_parallel_field_values(
    pred: dspy.Prediction,
    record: ExectGoldDocument,
    *,
    program_variant: str,
) -> list[ExtractedValue]:
    from clinical_extraction.programs.exect_s0_s1 import (
        _augment_current_prescription_medications,
        _augment_diagnosis_co_lists,
        _filter_diagnosis_for_seizure_descriptor_header,
        _normalize_diagnoses,
        _seizure_type_values_for_record,
        _values_for_family,
    )
    from clinical_extraction.programs.exect_s2 import (
        _normalize_investigation_surface,
        _recover_s2_investigation_raw_values,
        _recover_s2_seizure_raw_values,
        _s2_values_for_family,
    )
    from clinical_extraction.programs.exect_s3 import _recover_s3_investigation_raw_values

    values: list[ExtractedValue] = []

    diagnosis_inputs = _as_list(getattr(pred, "diagnosis", []))
    diagnosis_inputs, diagnosis_header_flags = _filter_diagnosis_for_seizure_descriptor_header(
        diagnosis_inputs,
        record.text,
    )
    diagnosis_raw, diagnosis_augmented, specificity_collapse_augmented = (
        _augment_diagnosis_co_lists(diagnosis_inputs, record.text)
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

    pred_meds = _as_list(getattr(pred, "annotated_medication", []))
    pred_evidence = _as_list(getattr(pred, "annotated_medication_evidence", []))
    medication_raw, medication_evidence, medication_augmented = (
        _augment_current_prescription_medications(
            pred_meds,
            pred_evidence,
            record.text,
        )
    )
    guarded_meds, guard_flags = recover_exect_annotated_medication_non_asm_brand_alias_guard(
        medication_raw,
        medication_evidence,
        record.text,
    )
    for med in guarded_meds:
        canon_med = canonical_medication_name(med)
        orig_raw = med
        orig_evidence = ""
        is_augmented = False
        for idx, raw_val in enumerate(medication_raw):
            clean_raw = raw_val.strip().lower()
            if clean_raw in {"eplim", "eplim chrono", "epilim", "epilim chrono"}:
                clean_raw = "epilim chrono"
            if canonical_medication_name(clean_raw) == canon_med:
                orig_raw = raw_val
                orig_evidence = medication_evidence[idx] if idx < len(medication_evidence) else ""
                if raw_val in medication_augmented:
                    is_augmented = True
                break
        augmented_set = {orig_raw} if is_augmented else set()
        values.extend(
            _values_for_family(
                record=record,
                field_name="annotated_medication",
                raw_values=[orig_raw],
                evidence_values=[orig_evidence],
                fixed_normalized=med,
                fixed_bridge_flags=guard_flags,
                augmented_values=augmented_set,
            )
        )

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
    values.extend(
        _s2_values_for_family(
            record=record,
            field_name="investigation",
            raw_values=investigation_raw,
            evidence_values=_as_list(getattr(pred, "investigation_evidence", [])),
            normalize=_normalize_investigation_surface,
        )
    )

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
    return values


def _predict_s5_core_parallel_record(
    module: dspy.Module,
    record: ExectGoldDocument,
    *,
    program_variant: str,
    schema_level: str,
) -> DocumentPrediction:
    pred = module(note_text=record.text)
    values = _build_s5_core_parallel_field_values(
        pred,
        record,
        program_variant=program_variant,
    )
    metadata: dict[str, object] = {
        "program_variant": program_variant,
        "stage_graph_id": stage_graph_id_for_s5_program_variant(program_variant),
        "precomputed_candidates": {
            "seizure_frequency": build_precomputed_seizure_frequency_candidates(record.text)
        },
        "post_guard": {
            "annotated_medication": "exect.medication.am_guard_non_asm_brand_alias.v1"
        },
        "frequency_verifier": {
            "primitive_id": "exect.frequency.evidence_verify_policy.v2b",
            "policy": "reject_only",
            "flags": _as_list(getattr(pred, "frequency_verifier_flags", [])),
            "decision": getattr(pred, "frequency_verifier_decision", None),
            "reason": getattr(pred, "frequency_verifier_reason", None),
        },
    }
    return DocumentPrediction(
        document_id=record.document_id,
        dataset=EXECT_DATASET,
        schema_level=schema_level,
        values=values,
        quality_flags=record.quality_flags,
        metadata=metadata,
    )


def _predict_s4_record(
    module: dspy.Module,
    record: ExectGoldDocument,
    *,
    program_variant: str,
    schema_level: str = EXECT_S4_SCHEMA_LEVEL,
) -> DocumentPrediction:
    if program_variant == EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT:
        return _predict_s5_core_parallel_record(
            module,
            record,
            program_variant=program_variant,
            schema_level=schema_level,
        )
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

    # Apply medication precision guard for the designated S5 variants
    if program_variant in {
        EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
    }:
        from clinical_extraction.programs.exect_s0_s1 import (
            _augment_current_prescription_medications,
            _values_for_family,
        )
        # Filter out existing un-guarded medications
        values = [val for val in values if val.field_name != "annotated_medication"]

        pred_meds = _as_list(getattr(pred, "annotated_medication", []))
        pred_evidence = _as_list(getattr(pred, "annotated_medication_evidence", []))

        medication_raw, medication_evidence, medication_augmented = (
            _augment_current_prescription_medications(
                pred_meds,
                pred_evidence,
                record.text,
            )
        )

        if program_variant == EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT:
            from clinical_extraction.exect.primitives import (
                recover_exect_annotated_medication_temporal_evidence_guard,
            )
            guarded_meds, guard_flags = recover_exect_annotated_medication_temporal_evidence_guard(
                medication_raw,
                medication_evidence,
                record.text,
            )
        else:
            guarded_meds, guard_flags = recover_exect_annotated_medication_non_asm_brand_alias_guard(
                medication_raw,
                medication_evidence,
                record.text,
            )

        guarded_values = []
        for med in guarded_meds:
            # Map canonical name back to original raw surface and evidence
            canon_med = canonical_medication_name(med)
            orig_raw = med
            orig_evidence = ""
            is_augmented = False

            for idx, raw_val in enumerate(medication_raw):
                clean_raw = raw_val.strip().lower()
                if clean_raw in {"eplim", "eplim chrono", "epilim", "epilim chrono"}:
                    clean_raw = "epilim chrono"
                if canonical_medication_name(clean_raw) == canon_med:
                    orig_raw = raw_val
                    orig_evidence = medication_evidence[idx] if idx < len(medication_evidence) else ""
                    if raw_val in medication_augmented:
                        is_augmented = True
                    break

            augmented_set = {orig_raw} if is_augmented else set()

            guarded_values.extend(
                _values_for_family(
                    record=record,
                    field_name="annotated_medication",
                    raw_values=[orig_raw],
                    evidence_values=[orig_evidence],
                    fixed_normalized=med,
                    fixed_bridge_flags=guard_flags,
                    augmented_values=augmented_set,
                )
            )
        values.extend(guarded_values)

    metadata: dict[str, object] = {"program_variant": program_variant}
    if program_variant in {
        EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
    }:
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
    if program_variant in {
        EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
    }:
        if program_variant == EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT:
            metadata["post_guard"] = {
                "annotated_medication": "exect.medication.am_guard_temporal_evidence.v1"
            }
        else:
            metadata["post_guard"] = {
                "annotated_medication": "exect.medication.am_guard_non_asm_brand_alias.v1"
            }
    if program_variant in {
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
    }:
        policy_id = {
            EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT: (
                "exect.frequency.evidence_verify_policy.v2"
            ),
            EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT: (
                "exect.frequency.evidence_verify_policy.v2b"
            ),
        }.get(program_variant, "exect.frequency.evidence_verify_policy.v1")
        metadata["frequency_verifier"] = {
            "primitive_id": policy_id,
            "policy": "reject_only",
            "flags": _as_list(getattr(pred, "frequency_verifier_flags", [])),
            "decision": getattr(pred, "frequency_verifier_decision", None),
            "reason": getattr(pred, "frequency_verifier_reason", None),
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
    recovered, flags = _recover_s4_seizure_frequency_raw_values(raw_values, note_text)
    if program_variant not in {
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_TEMPORAL_FREQUENCY_VERIFY_VARIANT,
    }:
        return recovered, flags

    allowed = _verified_frequency_allowed_keys(raw_values)
    filtered = [label for label in recovered if label in allowed]
    if len(filtered) != len(recovered):
        flags.append("s5_frequency_verifier:co_label_augmentation_blocked")
    return filtered, flags


def _verified_frequency_allowed_keys(raw_values: list[str]) -> set[str]:
    allowed: set[str] = set()
    for raw in raw_values:
        canonical = canonical_clinical_phrase(raw)
        if not canonical:
            continue
        repaired, _ = _repair_s4_seizure_frequency_surface(canonical)
        allowed.add(repaired)
    return allowed


def _apply_exect_s5_frequency_verifier_guards(
    *,
    note_text: str,
    initial_frequency: list[str],
    verified: dspy.Prediction,
    strict_qualitative: bool = False,
) -> dspy.Prediction:
    """Apply reject-only frequency verifier guards without changing scorer policy."""
    initial_keys = _verified_frequency_allowed_keys(initial_frequency)
    verified_frequency = _as_list(getattr(verified, "seizure_frequency", []))
    verified_evidence = _as_list(getattr(verified, "seizure_frequency_evidence", []))
    frequency: list[str] = []
    frequency_evidence: list[str] = []
    flags: list[str] = []

    for index, raw_value in enumerate(verified_frequency):
        normalized = canonical_clinical_phrase(raw_value)
        repaired, _ = _repair_s4_seizure_frequency_surface(normalized)
        if not repaired or repaired not in initial_keys:
            flags.append("verifier_added_label_blocked")
            continue

        evidence_text = _evidence_at(verified_evidence, index) or ""
        if not evidence_text:
            flags.append("missing_evidence")
            continue
        if _evidence_looks_like_frequency_candidate_block(evidence_text):
            flags.append("candidate_block_echo")
            continue
        evidence_lower = evidence_text.lower()
        note_lower = note_text.lower()
        if evidence_lower not in note_lower:
            flags.append("evidence_not_in_note")
            continue
        # Recover exact-cased substring from the note to prevent any downstream case-sensitivity issues
        idx = note_lower.find(evidence_lower)
        evidence_text = note_text[idx : idx + len(evidence_text)]
        if _frequency_change_from_medication_control(raw_value, evidence_text):
            flags.append("medication_control_not_frequency_change")
            continue
        if strict_qualitative and not _qualitative_label_supported_by_evidence(
            raw_value, evidence_text
        ):
            flags.append("qualitative_without_note_support")
            continue

        frequency.append(raw_value.strip())
        frequency_evidence.append(evidence_text)

    return dspy.Prediction(
        seizure_frequency=frequency,
        seizure_frequency_evidence=frequency_evidence,
        verifier_decision=getattr(verified, "verifier_decision", "repair"),
        verifier_reason=getattr(verified, "verifier_reason", ""),
        frequency_verifier_flags=flags,
    )


def _evidence_looks_like_frequency_candidate_block(evidence_text: str) -> bool:
    lower = evidence_text.lower()
    return (
        "precomputed benchmark-facing candidates" in lower
        or lower.startswith("seizure_frequency:")
    )


def _frequency_change_from_medication_control(raw_value: str, evidence_text: str) -> bool:
    label = canonical_clinical_phrase(raw_value)
    if label not in {"frequency increased", "frequency decreased"}:
        return False
    evidence = evidence_text.lower()
    medication_markers = (
        "lamotrigine",
        "levetiracetam",
        "carbamazepine",
        "valproate",
        "medication",
        "dose",
        "treatment",
    )
    control_markers = ("control", "controlled")
    seizure_frequency_markers = ("frequency", "seizure frequency", "seizures per")
    return (
        any(marker in evidence for marker in medication_markers)
        and any(marker in evidence for marker in control_markers)
        and not any(marker in evidence for marker in seizure_frequency_markers)
    )


_QUALITATIVE_FREQUENCY_LABELS = frozenset(
    {"infrequent", "frequency same", "frequency increased", "frequency decreased"}
)
_QUALITATIVE_NOTE_MARKERS: dict[str, tuple[str, ...]] = {
    "infrequent": ("infrequent", "rarely", "occasional", "occasionally", "rare"),
    "frequency same": (
        "same frequency",
        "unchanged",
        "frequency remains",
        "stable frequency",
        "frequency is the same",
    ),
    "frequency increased": (
        "frequency increased",
        "increased frequency",
        "more frequent",
        "more often",
        "worsening",
        "worse frequency",
        "having more",
        "more generalised",
        "more generalized",
    ),
    "frequency decreased": (
        "frequency decreased",
        "decreased frequency",
        "less frequent",
        "less often",
        "improved",
        "fewer seizures",
    ),
}


def _qualitative_label_supported_by_evidence(raw_value: str, evidence_text: str) -> bool:
    label = canonical_clinical_phrase(raw_value)
    if label not in _QUALITATIVE_FREQUENCY_LABELS:
        return True
    evidence = evidence_text.lower()
    return any(marker in evidence for marker in _QUALITATIVE_NOTE_MARKERS.get(label, ()))


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
