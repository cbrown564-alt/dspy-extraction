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
from clinical_extraction.pipeline.sectioning import select_context
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
EXECT_S0_S1_SECTION_AWARE_VARIANT = "exect_s0_s1_field_family_section_aware"
EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT = "exect_s0_s1_field_family_diagnosis_recall"
EXECT_S0_S1_SCORER = "exect_field_family_deterministic_v1"
EXECT_S0_S1_PROMPT_VERSION = "exect_s0_s1_field_family_v4_2_label_policy"
EXECT_S0_S1_DIAGNOSIS_RECALL_PROMPT_VERSION = "exect_s0_s1_diagnosis_recall_v1"
EXECT_S0_S1_V3_PROMPT_VERSION = "exect_s0_s1_field_family_v3_seizure_evidence_policy"
EXECT_S0_S1_V4_PROMPT_VERSION = "exect_s0_s1_field_family_v4_label_policy"
EXECT_S0_S1_V4_1_PROMPT_VERSION = "exect_s0_s1_field_family_v4_1_label_policy"
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
    "When a note names focal seizures with secondary generalisation as one phrase, split it into "
    "focal seizures, secondary generalisation, and generalized tonic clonic seizure as separate "
    "benchmark-facing seizure-type labels.",
    "Preserve convulsive modifiers on focal to bilateral seizure labels when the audited scorer "
    "expects focal to bilateral convulsive seizure or seizures.",
    "Strip probable, possible, or similar uncertainty qualifiers from diagnosis labels when the "
    "benchmark-facing gold uses the definite audited diagnosis surface.",
    "Preserve modifier-rich audited diagnosis surfaces such as symptomatic structural focal "
    "epilepsy; do not drop focal or other audited modifiers unless specificity collapse applies.",
    "Keep seizure-type labels out of the diagnosis field and epilepsy diagnoses out of the "
    "seizure-type field; do not emit non-epilepsy conditions such as hydrocephalus as diagnosis.",
    "Only emit diagnosis labels from the audited epilepsy diagnosis vocabulary; never place "
    "seizure-type phrases, fused secondary-generalisation wording, or seizure-event descriptors "
    "in the diagnosis field.",
    "When splitting temporal-lobe-onset focal seizures, emit temporal lobe seizure and focal "
    "seizures as separate labels; do not replace them with temporal lobe seizures alone.",
    "When the note lists both focal seizures and a temporal-lobe seizure type, include both in "
    "seizure_type rather than moving focal seizures into diagnosis.",
    "For symptomatic structural focal epilepsy, keep the focal modifier; do not shorten to "
    "symptomatic structural epilepsy.",
    "When a note separately names parietal lobe epilepsy alongside focal epilepsy, include both "
    "diagnosis labels.",
    "Use epilepsy with generalized tonic clonic seizures on awakening when the note uses on "
    "awakening wording; do not substitute from sleep.",
    "Prefer audited coarse seizure-type labels such as generalized seizures or generalized tonic "
    "clonic seizures over granular event descriptors such as jerks, absences, or absence events "
    "unless the note explicitly uses the audited benchmark surface.",
    "When the benchmark-facing seizure label is focal to bilateral convulsive seizure, use that "
    "surface even if the note says focal onset convulsive seizure.",
    "Do not infer seizure type from diagnosis alone, and do not add secondary generalisation as a "
    "separate current seizure type unless the note independently names it as current.",
    "Annotated medication means anti-seizure medications in the audited prescription annotation "
    "view only; do not include psychotropic or non-ASM drugs, planned starts, previous trials, "
    "taper/stop instructions, or medication-history mentions.",
    "When the note has no prescription-style current medication list, return an empty "
    "annotated_medication list rather than inferring ASM from seizure history or past trials.",
    "Do not emit jerks, absences, or absence events as separate seizure-type labels when the "
    "benchmark-facing surface is a coarse generalized or generalized tonic clonic label.",
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
    {
        "case": "secondary_generalisation_split",
        "note_fragment": "Seizure type: focal seizures with secondary generalisation.",
        "benchmark_output": {
            "seizure_type": [
                "focal seizures",
                "secondary generalisation",
                "generalized tonic clonic seizure",
            ]
        },
        "policy": "Split fused secondary-generalisation phrases into separate benchmark seizure types.",
    },
    {
        "case": "focal_to_bilateral_convulsive_modifier",
        "note_fragment": "She has focal to bilateral seizures.",
        "benchmark_output": {"seizure_type": ["focal to bilateral convulsive seizures"]},
        "policy": "Preserve the convulsive modifier when that is the audited benchmark surface.",
    },
    {
        "case": "diagnosis_uncertainty_stripping",
        "note_fragment": "Diagnosis: probable juvenile myoclonic epilepsy.",
        "benchmark_output": {"diagnosis": ["juvenile myoclonic epilepsy"]},
        "policy": "Strip uncertainty qualifiers when the benchmark-facing label is definite.",
    },
    {
        "case": "cross_family_diagnosis_exclusion",
        "note_fragment": "Diagnosis: hydrocephalus. Seizure type: focal seizures.",
        "benchmark_output": {"diagnosis": [], "seizure_type": ["focal seizures"]},
        "policy": "Do not place non-epilepsy conditions or seizure types in the diagnosis field.",
    },
    {
        "case": "symptomatic_structural_focal_preservation",
        "note_fragment": "Diagnosis: symptomatic structural focal epilepsy.",
        "benchmark_output": {"diagnosis": ["symptomatic structural focal epilepsy"]},
        "policy": "Preserve the full audited focal diagnosis modifier rather than dropping focal.",
    },
    {
        "case": "temporal_lobe_seizures_split_pair",
        "note_fragment": "Seizure type: temporal lobe seizures with occipital lobe seizures.",
        "benchmark_output": {
            "seizure_type": [
                "temporal lobe seizure",
                "focal seizures",
                "occipital lobe seizures",
            ]
        },
        "policy": "Do not stop at temporal lobe seizures alone when focal seizures is also required.",
    },
    {
        "case": "focal_to_bilateral_annotation_surface",
        "note_fragment": "Seizure type and frequency: focal onset convulsive seizure.",
        "benchmark_output": {"seizure_type": ["focal to bilateral convulsive seizure"]},
        "policy": "Use the audited bilateral convulsive benchmark surface when that is the scorer label.",
    },
    {
        "case": "coarse_generalized_seizure_surface",
        "note_fragment": "She has absences and myoclonic jerks.",
        "benchmark_output": {"seizure_type": ["generalized seizures"]},
        "policy": "Prefer audited coarse generalized seizure labels over granular jerk/absence descriptors.",
    },
    {
        "case": "absence_events_to_gtcs_surface",
        "note_fragment": "He reports absence events.",
        "benchmark_output": {"seizure_type": ["generalized tonic clonic seizures"]},
        "policy": "Map absence-event wording to the audited generalized tonic clonic seizure surface when required.",
    },
    {
        "case": "on_awakening_diagnosis_phrasing",
        "note_fragment": "Diagnosis: epilepsy with generalized tonic clonic seizures on awakening.",
        "benchmark_output": {
            "diagnosis": ["epilepsy with generalized tonic clonic seizures on awakening"]
        },
        "policy": "Preserve on awakening wording in the audited diagnosis label.",
    },
    {
        "case": "co_listed_lobe_epilepsy_diagnoses",
        "note_fragment": "Diagnosis: focal epilepsy, probable parietal onset.",
        "benchmark_output": {"diagnosis": ["focal epilepsy", "parietal lobe epilepsy"]},
        "policy": "Emit separate lobe-specific epilepsy diagnoses when the note supports both.",
    },
    {
        "case": "reject_granular_jme_seizure_descriptors",
        "note_fragment": "She reports absences and myoclonic jerks. Seizure type: generalized tonic clonic seizures.",
        "benchmark_output": {"seizure_type": ["generalized tonic clonic seizures"]},
        "policy": "Do not add jerks or absences when the audited label is already coarse.",
    },
    {
        "case": "myoclonic_jerks_to_myoclonic_seizures",
        "note_fragment": "Seizure type: myoclonic jerks.",
        "benchmark_output": {"seizure_type": ["myoclonic seizures"]},
        "policy": "Map jerk wording to myoclonic seizures when that is the audited surface.",
    },
    {
        "case": "non_asm_medication_exclusion",
        "note_fragment": "Current medication: lamotrigine 100mg bd, citalopram 20mg od.",
        "benchmark_output": {"annotated_medication": ["lamotrigine"]},
        "policy": "Exclude non-anti-seizure medications from annotated_medication.",
    },
    {
        "case": "empty_medication_without_prescription_list",
        "note_fragment": "Seizure type: focal seizures. No current anti-epileptic medication documented.",
        "benchmark_output": {"annotated_medication": []},
        "policy": "Return empty medication when no prescription-style ASM list is present.",
    },
)

_REJECTED_GRANULAR_SEIZURE_TYPES = frozenset(
    {
        "absences",
        "jerks",
        "occasional absences",
    }
)

_GRANULAR_SEIZURE_TYPE_COARSENING = {
    "myoclonic jerks": "myoclonic seizures",
    "absence events": "generalized tonic clonic seizures",
}

_REJECTED_ANNOTATED_MEDICATIONS = frozenset(
    {
        "citalopram",
        "fluoxetine",
        "sertraline",
        "amitriptyline",
        "diazepam",
    }
)

_MEDICATION_SURFACE_REPAIRS = {
    "eslicarbazine": "eslicarbazepine",
}

_MEDICATION_EVIDENCE_EXCLUSION_PHRASES = (
    "previously",
    "prior ",
    "to start",
    "plan to start",
    "we plan",
    "tried ",
    "recommend starting",
    "will start",
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
      modifier forms such as focal seizures with altered awareness, focal to bilateral
      convulsive seizures, or occipital lobe seizures when those are the scorer labels.
      Split fused phrases such as temporal lobe onset focal seizures or focal seizures
      with secondary generalisation into separate audited labels. Do not infer seizure
      type from diagnosis alone.
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
    - "Seizure type: focal seizures with secondary generalisation."
      -> seizure_type = ["focal seizures", "secondary generalisation",
      "generalized tonic clonic seizure"]; split fused secondary-generalisation phrases.
    - "She has focal to bilateral seizures."
      -> seizure_type = ["focal to bilateral convulsive seizures"]; preserve convulsive
      modifiers when required by the audited surface.
    - "Diagnosis: probable juvenile myoclonic epilepsy."
      -> diagnosis = ["juvenile myoclonic epilepsy"]; strip uncertainty qualifiers for
      benchmark-facing labels.
    - "Diagnosis: hydrocephalus. Seizure type: focal seizures."
      -> diagnosis = []; seizure_type = ["focal seizures"]; keep seizure types out of
      diagnosis and omit non-epilepsy diagnoses.
    - "Seizure type: temporal lobe seizures with occipital lobe seizures."
      -> seizure_type = ["temporal lobe seizure", "focal seizures", "occipital lobe
      seizures"]; do not stop at temporal lobe seizures alone.
    - "Seizure type and frequency: focal onset convulsive seizure."
      -> seizure_type = ["focal to bilateral convulsive seizure"]; use the audited
      bilateral convulsive benchmark surface when required.
    - "Diagnosis: epilepsy with generalized tonic clonic seizures on awakening."
      -> diagnosis = ["epilepsy with generalized tonic clonic seizures on awakening"];
      preserve on awakening wording.
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


class ExectS0S1DiagnosisSignature(dspy.Signature):
    """Extract benchmark-facing ExECT diagnosis labels only."""

    note_text: str = dspy.InputField(desc="Section-aware ExECT note context for diagnosis")
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


class ExectS0S1SeizureTypeSignature(dspy.Signature):
    """Extract benchmark-facing ExECT seizure-type labels only."""

    note_text: str = dspy.InputField(desc="Section-aware ExECT note context for seizure type")
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


class ExectS0S1MedicationSignature(dspy.Signature):
    """Extract benchmark-facing ExECT annotated medications only."""

    note_text: str = dspy.InputField(desc="Section-aware ExECT note context for medication")
    annotated_medication: list[str] = dspy.OutputField(
        desc=(
            "Audited prescription-style anti-seizure medication names. Exclude planned, "
            "previous, taper/stop, and medication-history-only mentions."
        )
    )
    annotated_medication_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each medication label, aligned by index."
    )


class ExectS0S1DiagnosisRecallSignature(dspy.Signature):
    """Find additional missed benchmark-facing ExECT diagnosis labels.

    Review the note and the initial diagnosis list. Return ONLY additional
    established epilepsy diagnoses that the initial pass missed. This is an
    add-only recall pass — do not repeat labels already in initial_diagnosis.

    Recall policy:
    - Add co-listed lobe-specific or syndrome epilepsy diagnoses when the note
      explicitly names them alongside a broader epilepsy diagnosis (e.g. add
      parietal lobe epilepsy when focal epilepsy and probable parietal onset
      are both stated).
    - Add generic epilepsy when the note explicitly states established epilepsy
      but initial_diagnosis omitted it while listing only a more specific label.
    - Preserve audited diagnosis surfaces such as epilepsy with generalized
      tonic clonic seizures on awakening when that exact phrasing appears.
    - Do not infer epilepsy subtype from seizure-type evidence alone.
    - Do not add a diagnosis for a single seizure event without established
      epilepsy wording.
    - Do not add non-epilepsy conditions or seizure-type phrases.
    - Return [] when no additional benchmark-facing diagnoses are supported.
    - additional_diagnosis_evidence must be exact contiguous note quotes aligned
      by index with additional_diagnosis.
    """

    note_text: str = dspy.InputField(desc="Synthetic epilepsy clinic letter text")
    initial_diagnosis: list[str] = dspy.InputField(
        desc="Diagnosis labels already extracted in the first pass."
    )
    additional_diagnosis: list[str] = dspy.OutputField(
        desc=(
            "Additional benchmark-facing epilepsy diagnosis labels not already "
            "in initial_diagnosis. Use [] when none."
        )
    )
    additional_diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each additional diagnosis, aligned by index."
    )


class ExectS0S1DiagnosisRecallProbeModule(dspy.Module):
    """Monolithic extraction plus add-only diagnosis recall pass."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS0S1FieldFamilySignature)
        self.recall_diagnosis = dspy.Predict(ExectS0S1DiagnosisRecallSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        initial = self.extract(note_text=note_text)
        initial_diagnosis = _as_list(getattr(initial, "diagnosis", []))
        initial_diagnosis_evidence = _as_list(getattr(initial, "diagnosis_evidence", []))
        recall = self.recall_diagnosis(
            note_text=note_text,
            initial_diagnosis=initial_diagnosis,
        )
        merged_diagnosis, merged_diagnosis_evidence, recall_added = _merge_diagnosis_recall(
            initial_diagnosis=initial_diagnosis,
            initial_diagnosis_evidence=initial_diagnosis_evidence,
            additional_diagnosis=_as_list(getattr(recall, "additional_diagnosis", [])),
            additional_diagnosis_evidence=_as_list(
                getattr(recall, "additional_diagnosis_evidence", [])
            ),
        )
        return dspy.Prediction(
            diagnosis=merged_diagnosis,
            diagnosis_evidence=merged_diagnosis_evidence,
            seizure_type=_as_list(getattr(initial, "seizure_type", [])),
            seizure_type_evidence=_as_list(getattr(initial, "seizure_type_evidence", [])),
            annotated_medication=_as_list(getattr(initial, "annotated_medication", [])),
            annotated_medication_evidence=_as_list(
                getattr(initial, "annotated_medication_evidence", [])
            ),
            diagnosis_recall_added=recall_added,
            initial_diagnosis=initial_diagnosis,
        )


class ExectS0S1SectionAwareFieldFamilyModule(dspy.Module):
    """Section-aware ExECT S0/S1 field-family extractor."""

    def __init__(self) -> None:
        super().__init__()
        self.extract_diagnosis = dspy.ChainOfThought(ExectS0S1DiagnosisSignature)
        self.extract_seizure_type = dspy.ChainOfThought(ExectS0S1SeizureTypeSignature)
        self.extract_medication = dspy.ChainOfThought(ExectS0S1MedicationSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        diagnosis_context = _family_context(
            note_text,
            target_field="diagnosis",
            max_sections=2,
        )
        seizure_context = _family_context(
            note_text,
            target_field="seizure_type",
            max_sections=3,
        )
        medication_context = _family_context(
            note_text,
            target_field="medication",
            max_sections=2,
        )

        diagnosis = self.extract_diagnosis(note_text=diagnosis_context)
        seizure_type = self.extract_seizure_type(note_text=seizure_context)
        medication = self.extract_medication(note_text=medication_context)
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
        )


def build_exect_s0_s1_module(program_variant: str = EXECT_S0_S1_VARIANT) -> dspy.Module:
    """Build an ExECT S0/S1 module for the requested program variant."""
    if program_variant == EXECT_S0_S1_SECTION_AWARE_VARIANT:
        return ExectS0S1SectionAwareFieldFamilyModule()
    if program_variant == EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT:
        return ExectS0S1DiagnosisRecallProbeModule()
    if program_variant == EXECT_S0_S1_VARIANT:
        return ExectS0S1FieldFamilyModule()
    raise ValueError(f"Unsupported ExECT S0/S1 program variant: {program_variant!r}")


def _merge_diagnosis_recall(
    *,
    initial_diagnosis: list[str],
    initial_diagnosis_evidence: list[str],
    additional_diagnosis: list[str],
    additional_diagnosis_evidence: list[str],
) -> tuple[list[str], list[str], list[str]]:
    """Merge add-only recalled diagnoses with deterministic guards."""
    merged_diagnosis = list(initial_diagnosis)
    merged_evidence = _align_evidence(initial_diagnosis, initial_diagnosis_evidence)
    seen = {
        canonical_clinical_phrase(value)
        for value in initial_diagnosis
        if value.strip()
    }
    recall_added: list[str] = []

    for index, raw_value in enumerate(additional_diagnosis):
        if not raw_value.strip():
            continue
        normalized = canonical_clinical_phrase(raw_value)
        normalized, _ = _normalize_diagnosis_surface(normalized)
        if not normalized or normalized in seen or normalized not in ALLOWED_DIAGNOSIS_LABELS:
            continue
        evidence_text = _evidence_at(additional_diagnosis_evidence, index)
        merged_diagnosis.append(raw_value.strip())
        merged_evidence.append(evidence_text or "")
        seen.add(normalized)
        recall_added.append(normalized)

    return merged_diagnosis, merged_evidence, recall_added


def _align_evidence(values: list[str], evidence_values: list[str]) -> list[str]:
    aligned = list(evidence_values)
    while len(aligned) < len(values):
        aligned.append("")
    return aligned[: len(values)]


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
    module: dspy.Module,
    records: list[ExectGoldDocument],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    program_variant: str = EXECT_S0_S1_VARIANT,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> PredictionSet:
    """Run ``module`` on ExECT records and return a shared ``PredictionSet``."""
    predictions = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        predictions.append(_predict_record(module, record, program_variant=program_variant))
        if progress_callback is not None:
            progress_callback(index, total, record.document_id)
    return PredictionSet(
        dataset=EXECT_DATASET,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        predictions=predictions,
        metadata={
            "program_variant": program_variant,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "scorer_mode": EXECT_S0_S1_SCORER,
        },
    )


def _predict_record(
    module: dspy.Module,
    record: ExectGoldDocument,
    *,
    program_variant: str,
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
        metadata={"program_variant": program_variant},
    )


def _family_context(note_text: str, *, target_field: str, max_sections: int) -> str:
    selected = select_context(
        note_text,
        target_field=target_field,
        max_sections=max_sections,
    )
    if not selected:
        return note_text

    formatted = []
    for span in selected:
        label = span.section or "document"
        formatted.append(f"Section: {label}\n{span.text.strip()}")
    return "\n\n".join(chunk for chunk in formatted if chunk.strip()) or note_text


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
        if field_name == "annotated_medication" and _medication_evidence_excluded(evidence_text):
            continue
        for normalized, bridge_flags in _benchmark_values(field_name, raw_value):
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            evidence_spans, evidence_flags = _evidence_spans(record, evidence_text)
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
                    evidence=evidence_spans,
                    temporality="not_applicable",
                    negation="affirmed",
                    confidence=None,
                    quality_flags=[*quality_flags, *bridge_flags, *evidence_flags],
                )
            )
    return values


def _benchmark_values(field_name: str, value: str) -> list[tuple[str, list[str]]]:
    normalized = _normalize_value(field_name, value)
    bridge_flags: list[str] = []

    if field_name == "diagnosis":
        normalized, bridge_flags = _normalize_diagnosis_surface(normalized)
        if not normalized:
            return []
        if normalized not in ALLOWED_DIAGNOSIS_LABELS:
            return []
    elif field_name == "seizure_type":
        normalized, surface_flags = _normalize_seizure_type_surface(normalized)
        bridge_flags.extend(surface_flags)
        coarsened = _coarsen_granular_seizure_type(normalized)
        if coarsened is not None:
            return coarsened
        split_values = _split_fused_seizure_type(normalized)
        if split_values is not None:
            return [
                (
                    split_value,
                    [*bridge_flags, "benchmark_bridge:fused_seizure_type_split"],
                )
                for split_value in split_values
            ]
    elif field_name == "annotated_medication":
        normalized, med_flags = _normalize_annotated_medication_surface(normalized)
        if not normalized:
            return []
        bridge_flags.extend(med_flags)

    return [(normalized, bridge_flags)]


def _normalize_diagnosis_surface(normalized: str) -> tuple[str, list[str]]:
    flags: list[str] = []
    for prefix in ("probable ", "possible "):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :].strip()
            flags.append("benchmark_bridge:diagnosis_uncertainty_stripped")
            break
    if normalized == "symptomatic structural epilepsy":
        return "symptomatic structural focal epilepsy", [
            *flags,
            "benchmark_bridge:symptomatic_structural_focal_restored",
        ]
    return normalized, flags


def _normalize_seizure_type_surface(normalized: str) -> tuple[str, list[str]]:
    if normalized in {"focal to bilateral seizures", "focal to bilateral seizure"}:
        convulsive = (
            "focal to bilateral convulsive seizures"
            if normalized.endswith("seizures")
            else "focal to bilateral convulsive seizure"
        )
        return convulsive, ["benchmark_bridge:seizure_type_convulsive_modifier"]
    if normalized == "generalized tonic clonic seizures from sleep":
        return "generalized tonic clonic seizures", [
            "benchmark_bridge:seizure_temporal_modifier_stripped"
        ]
    return normalized, []


def _coarsen_granular_seizure_type(
    normalized: str,
) -> list[tuple[str, list[str]]] | None:
    if normalized in _REJECTED_GRANULAR_SEIZURE_TYPES:
        return []
    coarsened = _GRANULAR_SEIZURE_TYPE_COARSENING.get(normalized)
    if coarsened is not None:
        return [
            (
                coarsened,
                ["benchmark_bridge:granular_seizure_surface_coarsened"],
            )
        ]
    return None


def _normalize_annotated_medication_surface(
    normalized: str,
) -> tuple[str, list[str]]:
    flags: list[str] = []
    repaired = _MEDICATION_SURFACE_REPAIRS.get(normalized)
    if repaired is not None:
        normalized = repaired
        flags.append("benchmark_bridge:medication_surface_repaired")
    if normalized in _REJECTED_ANNOTATED_MEDICATIONS:
        return "", [*flags, "benchmark_bridge:non_asm_medication_rejected"]
    return normalized, flags


def _medication_evidence_excluded(evidence_text: str | None) -> bool:
    if not evidence_text:
        return False
    lower = evidence_text.lower()
    return any(phrase in lower for phrase in _MEDICATION_EVIDENCE_EXCLUSION_PHRASES)


def _split_fused_seizure_type(normalized: str) -> list[str] | None:
    if normalized in {
        "temporal lobe onset focal seizures",
        "temporal lobe focal seizures",
        "temporal onset focal seizures",
        "temporal lobe seizures",
    }:
        return ["temporal lobe seizure", "focal seizures"]
    if normalized in {
        "focal seizures with secondary generalisation",
        "focal seizures with secondary generalization",
    }:
        return [
            "focal seizures",
            "secondary generalisation",
            "generalized tonic clonic seizure",
        ]
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
) -> tuple[list[EvidenceSpan], list[str]]:
    if not evidence_text:
        return [], []
    start = record.text.find(evidence_text)
    if start != -1:
        return [
            EvidenceSpan(
                text=evidence_text,
                start=start,
                end=start + len(evidence_text),
                document_id=record.document_id,
            )
        ], []

    repaired_span = _repair_ellipsis_evidence_span(record, evidence_text)
    if repaired_span is not None:
        return [repaired_span], ["evidence_repair:ellipsis_contiguous_span"]

    return [EvidenceSpan(text=evidence_text, document_id=record.document_id)], []


def _repair_ellipsis_evidence_span(
    record: ExectGoldDocument,
    evidence_text: str,
) -> EvidenceSpan | None:
    if "..." not in evidence_text:
        return None

    fragments = [fragment.strip() for fragment in evidence_text.split("...") if fragment.strip()]
    if len(fragments) < 2:
        return None

    search_from = 0
    first_start: int | None = None
    last_end: int | None = None
    for fragment in fragments:
        start = record.text.find(fragment, search_from)
        if start == -1:
            return None
        if first_start is None:
            first_start = start
        last_end = start + len(fragment)
        search_from = last_end

    if first_start is None or last_end is None:
        return None

    repaired_text = record.text[first_start:last_end]
    if len(repaired_text) > 300 or "\n\n" in repaired_text:
        return None

    return EvidenceSpan(
        text=repaired_text,
        start=first_start,
        end=last_end,
        document_id=record.document_id,
    )


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
    program_variant: str = EXECT_S0_S1_VARIANT,
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
        program_variant=program_variant,
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
