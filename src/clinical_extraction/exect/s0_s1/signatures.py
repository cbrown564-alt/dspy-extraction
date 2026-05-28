"""DSPy signatures for ExECT S0/S1 field-family extraction."""
from __future__ import annotations

import dspy

from clinical_extraction.exect.s0_s1.constants import *  # noqa: F401,F403
from clinical_extraction.exect.s0_s1.prompt_routing import (
    resolve_exect_s0_s1_extraction_prompt_version,
    resolve_exect_s0_s1_label_policy,
)

class ExectS0S1L0MinimalSignature(dspy.Signature):
    """Extract diagnosis, seizure_type, and annotated_medication from clinical note text.

    Return label lists and parallel evidence quote lists aligned by index.
    Use empty lists when a field has no supported values in the note.
    """

    note_text: str = dspy.InputField(desc="Clinical note text")
    diagnosis: list[str] = dspy.OutputField(desc="Diagnosis labels supported by the note")
    diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Source quotes for each diagnosis label, aligned by index"
    )
    seizure_type: list[str] = dspy.OutputField(
        desc="Seizure-type labels supported by the note"
    )
    seizure_type_evidence: list[str] = dspy.OutputField(
        desc="Source quotes for each seizure-type label, aligned by index"
    )
    annotated_medication: list[str] = dspy.OutputField(
        desc="Medication labels supported by the note"
    )
    annotated_medication_evidence: list[str] = dspy.OutputField(
        desc="Source quotes for each medication label, aligned by index"
    )


class ExectS0S1L1SchemaSignature(dspy.Signature):
    """Extract structured field families from a clinical note.

    Output JSON lists for diagnosis, seizure_type, and annotated_medication with
    parallel evidence lists. Use empty lists when the note does not support a field.
    """

    note_text: str = dspy.InputField(desc="Clinical note text")
    diagnosis: list[str] = dspy.OutputField(
        desc="Epilepsy diagnosis labels explicitly supported by the note"
    )
    diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Exact quotes supporting each diagnosis label, aligned by index"
    )
    seizure_type: list[str] = dspy.OutputField(
        desc="Seizure-type labels explicitly named in the note"
    )
    seizure_type_evidence: list[str] = dspy.OutputField(
        desc="Exact quotes supporting each seizure-type label, aligned by index"
    )
    annotated_medication: list[str] = dspy.OutputField(
        desc="Current prescription-style anti-seizure medication names in the note"
    )
    annotated_medication_evidence: list[str] = dspy.OutputField(
        desc="Exact quotes supporting each medication label, aligned by index"
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


EXECT_S0_S1_V4_11_SIGNATURE_BOUNDARY_ADDENDUM = """
    Additional v4.11 seizure-policy boundary examples:
    - "Diagnosis: generalized tonic clonic seizures. Seizure type: generalized tonic clonic seizures."
      -> seizure_type = ["generalized tonic clonic seizures"]; use plural GTCS when the audited
      diagnosis or seizure row uses the plural surface.
    - "Seizure type: focal to bilateral convulsive seizures."
      -> seizure_type = ["focal to bilateral convulsive seizures"]; preserve plural convulsive
      surfaces when required by the audited label.
    - "Diagnosis: focal epilepsy. EEG shows spike-wave activity. No seizure type documented."
      -> seizure_type = []; do not invent absence or myoclonic types from EEG alone.
    - "Seizure type: complex partial seizures with secondary generalisation."
      -> seizure_type = ["complex partial seizures", "secondary generalisation"]; use the full
      secondary generalisation phrase, not bare secondary alone.
    - "Seizure type: complex partial seizures, secondary generalized seizures."
      -> seizure_type = ["complex partial seizures", "secondary generalized seizures"]; co-list
      multiple audited current seizure types when each is named.
"""

EXECT_S0_S1_V4_12_SIGNATURE_BOUNDARY_ADDENDUM = """
    Additional v4.12 diagnosis-stability examples:
    - "Diagnosis: epilepsy. Seizure type: focal to bilateral convulsive seizure."
      -> diagnosis = ["epilepsy"]; seizure_type = ["focal to bilateral convulsive seizure"];
      do not upgrade generic epilepsy to focal epilepsy from seizure-type wording.
    - "She was diagnosed with epilepsy at age 22. MRI showed a small right amygdala hyperintensity."
      -> diagnosis = ["epilepsy"]; do not infer symptomatic structural focal epilepsy from
      structural imaging context alone.
    - "Diagnosis: focal onset epilepsy. Seizure type: epileptic seizures."
      -> diagnosis = ["focal onset epilepsy"]; keep diagnosis recall even when seizure-type
      policy also applies.
"""


EXECT_S0_S1_V4_10_EVIDENCE_STRICT_SIGNATURE_ADDENDUM = """
    Evidence policy (strict; v4.10 label policy unchanged):
    - Every emitted label requires an exact contiguous quote from note_text; omit the label if
      no exact quote exists.
    - Seizure-type evidence must come from an explicit seizure-type or diagnosis row, not EEG
      or imaging narrative alone.
    - Use the shortest exact contiguous substring that supports each label.
"""


EXECT_S0_S1_V4_10_EVIDENCE_SOFT_SIGNATURE_ADDENDUM = """
    Evidence policy (soft diagnostic; v4.10 label policy unchanged):
    - Prefer benchmark-facing labels supported by the note even when quote alignment is imperfect.
    - Provide best-effort exact quotes when possible; do not abstain from a correct label solely
      because quote extraction is difficult.
    - Evidence quality is evaluated diagnostically; extraction favors recall on audited labels.
"""


def build_exect_s0_s1_field_family_signature(
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
) -> type[ExectS0S1FieldFamilySignature]:
    """Build a field-family signature for the requested label-policy prompt version."""
    if prompt_version == EXECT_S0_S1_L0_PROMPT_VERSION:
        return ExectS0S1L0MinimalSignature
    if prompt_version == EXECT_S0_S1_L1_SCHEMA_PROMPT_VERSION:
        return ExectS0S1L1SchemaSignature
    if prompt_version == EXECT_S0_S1_D1_PROMPT_VERSION:
        return ExectS0S1L0MinimalSignature
    doc = ExectS0S1FieldFamilySignature.__doc__ or ""
    if prompt_version == EXECT_S0_S1_V4_11_PROMPT_VERSION:
        return type(
            "ExectS0S1FieldFamilyV411Signature",
            (ExectS0S1FieldFamilySignature,),
            {"__doc__": doc + EXECT_S0_S1_V4_11_SIGNATURE_BOUNDARY_ADDENDUM},
        )
    if prompt_version == EXECT_S0_S1_V4_12_PROMPT_VERSION:
        return type(
            "ExectS0S1FieldFamilyV412Signature",
            (ExectS0S1FieldFamilySignature,),
            {
                "__doc__": (
                    doc
                    + EXECT_S0_S1_V4_11_SIGNATURE_BOUNDARY_ADDENDUM
                    + EXECT_S0_S1_V4_12_SIGNATURE_BOUNDARY_ADDENDUM
                )
            },
        )
    if prompt_version == EXECT_S0_S1_V4_10_EVIDENCE_STRICT_PROMPT_VERSION:
        return type(
            "ExectS0S1FieldFamilyV410EvidenceStrictSignature",
            (ExectS0S1FieldFamilySignature,),
            {"__doc__": doc + EXECT_S0_S1_V4_10_EVIDENCE_STRICT_SIGNATURE_ADDENDUM},
        )
    if prompt_version == EXECT_S0_S1_V4_10_EVIDENCE_SOFT_PROMPT_VERSION:
        return type(
            "ExectS0S1FieldFamilyV410EvidenceSoftSignature",
            (ExectS0S1FieldFamilySignature,),
            {"__doc__": doc + EXECT_S0_S1_V4_10_EVIDENCE_SOFT_SIGNATURE_ADDENDUM},
        )
    extraction_version = resolve_exect_s0_s1_extraction_prompt_version(prompt_version)
    if extraction_version != EXECT_S0_S1_PROMPT_VERSION:
        raise ValueError(f"Unsupported ExECT S0/S1 prompt version: {prompt_version!r}")
    return ExectS0S1FieldFamilySignature


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

class ExectS0S1VerifierSignature(dspy.Signature):
    """Verify and repair benchmark-facing ExECT S0/S1 field-family extraction.

    Review the initial extraction against the note. This is a confirm-first verifier:
    preserve correct initial labels and evidence; repair only clear errors.

    Confirm-first policy:
    - When initial labels and evidence are benchmark-facing and note-supported, confirm
      unchanged. Do not add diagnoses, seizure types, or medications for recall.
    - Repair evidence quotes to the shortest exact contiguous substring of note_text.
    - Remove unsupported labels, cross-family leakage, planned/previous ASM, and granular
      seizure descriptors (jerks, absences) when coarse benchmark surfaces apply.
    - Do not add medications from prescription requests, planned starts, taper/stop
      instructions, or medication-history mentions.
    - Do not add-only co-listed diagnoses (diagnosis-recall probe was negative).
    - Prefer removing a label over inventing evidence.

    Evidence rules:
    - Evidence lists align by index with value lists.
    - Each evidence entry must be an exact contiguous quote from note_text.
    - On confirm, keep initial evidence when it already matches the note.
    """

    note_text: str = dspy.InputField(desc="Synthetic epilepsy clinic letter text")
    initial_diagnosis: list[str] = dspy.InputField(
        desc="Initial diagnosis labels from the extraction pass."
    )
    initial_diagnosis_evidence: list[str] = dspy.InputField(
        desc="Initial diagnosis evidence quotes, aligned by index."
    )
    initial_seizure_type: list[str] = dspy.InputField(
        desc="Initial seizure-type labels from the extraction pass."
    )
    initial_seizure_type_evidence: list[str] = dspy.InputField(
        desc="Initial seizure-type evidence quotes, aligned by index."
    )
    initial_annotated_medication: list[str] = dspy.InputField(
        desc="Initial annotated medication labels from the extraction pass."
    )
    initial_annotated_medication_evidence: list[str] = dspy.InputField(
        desc="Initial medication evidence quotes, aligned by index."
    )
    diagnosis: list[str] = dspy.OutputField(
        desc="Confirmed or repaired benchmark-facing diagnosis labels."
    )
    diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Exact note quotes supporting each diagnosis label, aligned by index."
    )
    seizure_type: list[str] = dspy.OutputField(
        desc="Confirmed or repaired benchmark-facing seizure-type labels."
    )
    seizure_type_evidence: list[str] = dspy.OutputField(
        desc="Exact note quotes supporting each seizure-type label, aligned by index."
    )
    annotated_medication: list[str] = dspy.OutputField(
        desc="Confirmed or repaired prescription-style ASM labels only."
    )
    annotated_medication_evidence: list[str] = dspy.OutputField(
        desc="Exact note quotes supporting each medication label, aligned by index."
    )
    verifier_decision: str = dspy.OutputField(
        desc=(
            "confirm when all initial labels are already correct; repair when at least "
            "one label or evidence quote was corrected; abstain only as a last resort"
        )
    )
    verifier_reason: str = dspy.OutputField(
        desc="Brief explanation of confirm/repair/abstain citing note spans"
    )

_FAMILY_POLICY_OUTPUT_KEYS = {
    "diagnosis": frozenset({"diagnosis"}),
    "seizure_type": frozenset({"seizure_type", "seizure_type_evidence"}),
    "annotated_medication": frozenset({"annotated_medication", "annotated_medication_evidence"}),
}

_FAMILY_SIGNATURE_BY_FIELD = {
    "diagnosis": ExectS0S1DiagnosisSignature,
    "seizure_type": ExectS0S1SeizureTypeSignature,
    "annotated_medication": ExectS0S1MedicationSignature,
}


def _policy_examples_for_family(
    examples: tuple[dict[str, object], ...],
    field_name: str,
) -> tuple[dict[str, object], ...]:
    keys = _FAMILY_POLICY_OUTPUT_KEYS[field_name]
    return tuple(
        example
        for example in examples
        if any(key in example.get("benchmark_output", {}) for key in keys)
    )


def _format_family_policy_examples_block(
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


def build_exect_s0_s1_family_specific_signature(
    field_name: str,
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
) -> type[dspy.Signature]:
    """Build a per-family signature enriched with v4_10 label-policy examples."""
    if field_name not in _FAMILY_SIGNATURE_BY_FIELD:
        raise ValueError(f"Unsupported ExECT S0/S1 field family: {field_name!r}")
    _, policy_examples = resolve_exect_s0_s1_label_policy(prompt_version)
    base_signature = _FAMILY_SIGNATURE_BY_FIELD[field_name]
    family_examples = _policy_examples_for_family(policy_examples, field_name)
    doc = (base_signature.__doc__ or "") + _format_family_policy_examples_block(
        family_examples
    )
    suffix = {
        "diagnosis": "Diagnosis",
        "seizure_type": "SeizureType",
        "annotated_medication": "Medication",
    }[field_name]
    class_name = f"ExectS0S1{suffix}PolicySignature"
    return type(class_name, (base_signature,), {"__doc__": doc})

