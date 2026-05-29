"""DSPy program modules for ExECT S0/S1 field-family extraction."""
from __future__ import annotations

import dspy

from clinical_extraction.exect.s0_s1.constants import (
    EXECT_S0_S1_ACTIVE_VARIANTS,
    EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT,
    EXECT_S0_S1_CLEAN_LADDER_V1_FAMILY_SPAN_VARIANT,
    EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT,
    EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
    EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
    EXECT_S0_S1_FIELD_FAMILIES,
    EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_MEDICATION_LIFECYCLE_CONTEXT_E13_VARIANT,
    EXECT_S0_S1_MEDICATION_ONLY_E13_VARIANT,
    EXECT_S0_S1_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT,
    EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_V4_11_PROMPT_VERSION,
    EXECT_S0_S1_VARIANT,
    EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
)
from clinical_extraction.exect.s0_s1.prediction_artifacts import (
    _apply_exect_verifier_guards,
    _as_list,
    _merge_diagnosis_recall,
)
from clinical_extraction.exect.s0_s1.prompt_routing import (
    extract_d1_field_family_surfaces,
    format_note_with_precomputed_family_candidates,
    format_note_with_medication_lifecycle_context,
    format_note_with_precomputed_medication_candidates,
    format_note_with_precomputed_seizure_type_candidates,
    resolve_exect_s0_s1_extraction_prompt_version,
)
from clinical_extraction.exect.s0_s1.signatures import (
    ExectS0S1DiagnosisRecallSignature,
    ExectS0S1DiagnosisSignature,
    ExectS0S1FieldFamilySignature,
    ExectS0S1MedicationSignature,
    ExectS0S1SeizureTypeSignature,
    ExectS0S1VerifierSignature,
    build_exect_s0_s1_family_specific_signature,
    build_exect_s0_s1_field_family_signature,
)
from clinical_extraction.exect.family_spans import family_span_context
from clinical_extraction.pipeline.sectioning import select_context

EXECT_S0_S1_FAMILY_SPAN_CONTEXT_FAMILIES = (
    "diagnosis_problem",
    "seizure",
    "medication",
    "investigation",
)

class ExectS0S1DeterministicOnlyModule(dspy.Module):
    """D1 ladder rung: primitive-only substring extraction, no model calls."""

    def forward(self, note_text: str) -> dspy.Prediction:
        surfaces = extract_d1_field_family_surfaces(note_text)
        empty_evidence = [""] * len(surfaces["diagnosis"])
        empty_seizure_evidence = [""] * len(surfaces["seizure_type"])
        empty_medication_evidence = [""] * len(surfaces["annotated_medication"])
        return dspy.Prediction(
            diagnosis=surfaces["diagnosis"],
            diagnosis_evidence=empty_evidence,
            seizure_type=surfaces["seizure_type"],
            seizure_type_evidence=empty_seizure_evidence,
            annotated_medication=surfaces["annotated_medication"],
            annotated_medication_evidence=empty_medication_evidence,
        )


class ExectS0S1FieldFamilyModule(dspy.Module):
    """Single-pass ExECT S0/S1 field-family extractor."""

    def __init__(
        self,
        *,
        prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        signature_cls = build_exect_s0_s1_field_family_signature(prompt_version)
        self.extract = dspy.ChainOfThought(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


class ExectS0S1FamilySpanFieldFamilyModule(dspy.Module):
    """Single-pass S1 extractor over E4 typed family-span context."""

    def __init__(
        self,
        *,
        prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        signature_cls = build_exect_s0_s1_field_family_signature(prompt_version)
        self.extract = dspy.ChainOfThought(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        span_context = family_span_context(
            note_text,
            families=EXECT_S0_S1_FAMILY_SPAN_CONTEXT_FAMILIES,
        )
        return self.extract(note_text=span_context or note_text)


class ExectS0S1PreVocabFieldFamilyModule(dspy.Module):
    """Single-pass extractor with audited pre-vocabulary candidate hints."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS0S1FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(
            note_text=format_note_with_precomputed_family_candidates(note_text)
        )


class ExectS0S1MedicationPreVocabFieldFamilyModule(dspy.Module):
    """Single-pass extractor with medication-only pre-vocabulary candidate hints."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS0S1FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(
            note_text=format_note_with_precomputed_medication_candidates(note_text)
        )


class ExectS0S1MedicationOnlyE13Module(dspy.Module):
    """E13 AM-only comparator: extract annotated medication and leave other S1 fields empty."""

    def __init__(
        self,
        *,
        prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.extract_medication = dspy.ChainOfThought(
            build_exect_s0_s1_family_specific_signature(
                "annotated_medication",
                prompt_version,
            )
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        medication = self.extract_medication(note_text=note_text)
        return dspy.Prediction(
            diagnosis=[],
            diagnosis_evidence=[],
            seizure_type=[],
            seizure_type_evidence=[],
            annotated_medication=_as_list(
                getattr(medication, "annotated_medication", [])
            ),
            annotated_medication_evidence=_as_list(
                getattr(medication, "annotated_medication_evidence", [])
            ),
        )


class ExectS0S1MedicationLifecycleContextE13Module(ExectS0S1MedicationOnlyE13Module):
    """E13 AM+MT arm: add diagnostic lifecycle rows to the medication prompt context."""

    def forward(self, note_text: str) -> dspy.Prediction:
        return super().forward(
            format_note_with_medication_lifecycle_context(note_text)
        )


class ExectS0S1SeizurePreVocabFieldFamilyModule(dspy.Module):
    """Single-pass extractor with seizure-type-only pre-vocabulary candidate hints."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS0S1FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(
            note_text=format_note_with_precomputed_seizure_type_candidates(note_text)
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

class ExectS0S1VerifierModule(dspy.Module):
    """Confirm-first verifier for ExECT S0/S1 field-family extraction."""

    def __init__(self) -> None:
        super().__init__()
        self.verify = dspy.Predict(ExectS0S1VerifierSignature)

    def forward(
        self,
        note_text: str,
        *,
        initial_diagnosis: list[str],
        initial_diagnosis_evidence: list[str],
        initial_seizure_type: list[str],
        initial_seizure_type_evidence: list[str],
        initial_annotated_medication: list[str],
        initial_annotated_medication_evidence: list[str],
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            initial_diagnosis=initial_diagnosis,
            initial_diagnosis_evidence=initial_diagnosis_evidence,
            initial_seizure_type=initial_seizure_type,
            initial_seizure_type_evidence=initial_seizure_type_evidence,
            initial_annotated_medication=initial_annotated_medication,
            initial_annotated_medication_evidence=initial_annotated_medication_evidence,
        )


class ExectS0S1VerifyRepairModule(dspy.Module):
    """v4.10 extraction plus confirm-first verify/repair pass."""

    def __init__(
        self,
        *,
        extraction_prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.extractor = ExectS0S1FieldFamilyModule(
            prompt_version=extraction_prompt_version
        )
        self.verifier = ExectS0S1VerifierModule()

    def forward(self, note_text: str) -> dspy.Prediction:
        initial = self.extractor(note_text=note_text)
        initial_diagnosis = _as_list(getattr(initial, "diagnosis", []))
        initial_diagnosis_evidence = _as_list(getattr(initial, "diagnosis_evidence", []))
        initial_seizure_type = _as_list(getattr(initial, "seizure_type", []))
        initial_seizure_type_evidence = _as_list(getattr(initial, "seizure_type_evidence", []))
        initial_medication = _as_list(getattr(initial, "annotated_medication", []))
        initial_medication_evidence = _as_list(
            getattr(initial, "annotated_medication_evidence", [])
        )
        verified = self.verifier(
            note_text=note_text,
            initial_diagnosis=initial_diagnosis,
            initial_diagnosis_evidence=initial_diagnosis_evidence,
            initial_seizure_type=initial_seizure_type,
            initial_seizure_type_evidence=initial_seizure_type_evidence,
            initial_annotated_medication=initial_medication,
            initial_annotated_medication_evidence=initial_medication_evidence,
        )
        guarded = _apply_exect_verifier_guards(
            note_text=note_text,
            initial_diagnosis=initial_diagnosis,
            initial_seizure_type=initial_seizure_type,
            initial_annotated_medication=initial_medication,
            verified=verified,
        )
        return dspy.Prediction(
            diagnosis=_as_list(getattr(guarded, "diagnosis", [])),
            diagnosis_evidence=_as_list(getattr(guarded, "diagnosis_evidence", [])),
            seizure_type=_as_list(getattr(guarded, "seizure_type", [])),
            seizure_type_evidence=_as_list(getattr(guarded, "seizure_type_evidence", [])),
            annotated_medication=_as_list(getattr(guarded, "annotated_medication", [])),
            annotated_medication_evidence=_as_list(
                getattr(guarded, "annotated_medication_evidence", [])
            ),
            verifier_decision=getattr(guarded, "verifier_decision", None),
            verifier_reason=getattr(guarded, "verifier_reason", None),
            initial_diagnosis=initial_diagnosis,
            initial_seizure_type=initial_seizure_type,
            initial_annotated_medication=initial_medication,
        )


class ExectS1CleanLadderDiagnosisStableEnsembleModule(dspy.Module):
    """Two-pass S1 arm: stable v4.10 diagnosis + v4.11 seizure/medication policy."""

    def __init__(self) -> None:
        super().__init__()
        self.extract_stable_diagnosis = ExectS0S1FieldFamilyModule(
            prompt_version=EXECT_S0_S1_PROMPT_VERSION
        )
        self.extract_seizure_policy = ExectS0S1FieldFamilyModule(
            prompt_version=EXECT_S0_S1_V4_11_PROMPT_VERSION
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        stable = self.extract_stable_diagnosis(note_text=note_text)
        seizure_policy = self.extract_seizure_policy(note_text=note_text)
        return dspy.Prediction(
            diagnosis=_as_list(getattr(stable, "diagnosis", [])),
            diagnosis_evidence=_as_list(getattr(stable, "diagnosis_evidence", [])),
            seizure_type=_as_list(getattr(seizure_policy, "seizure_type", [])),
            seizure_type_evidence=_as_list(
                getattr(seizure_policy, "seizure_type_evidence", [])
            ),
            annotated_medication=_as_list(
                getattr(seizure_policy, "annotated_medication", [])
            ),
            annotated_medication_evidence=_as_list(
                getattr(seizure_policy, "annotated_medication_evidence", [])
            ),
            diagnosis_source_prompt_version=EXECT_S0_S1_PROMPT_VERSION,
            seizure_medication_source_prompt_version=EXECT_S0_S1_V4_11_PROMPT_VERSION,
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

def _format_prior_extractions_context(
    *,
    note_text: str,
    prior: dict[str, list[str]],
    target_field: str,
) -> str:
    lines = [note_text, "", "Prior extractions from earlier prompt-graph stages:"]
    for field_name in EXECT_S0_S1_FIELD_FAMILIES:
        if field_name == target_field:
            continue
        values = prior.get(field_name, [])
        rendered = ", ".join(f'"{value}"' for value in values) if values else "(none)"
        lines.append(f"- {field_name}: [{rendered}]")
    return "\n".join(lines)


class ExectS0S1FieldFamilyPromptGraphParallelModule(dspy.Module):
    """Full-note per-family extraction with v4_10 label-policy examples per stage."""

    def __init__(
        self,
        *,
        prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.extract_diagnosis = dspy.ChainOfThought(
            build_exect_s0_s1_family_specific_signature("diagnosis", prompt_version)
        )
        self.extract_seizure_type = dspy.ChainOfThought(
            build_exect_s0_s1_family_specific_signature("seizure_type", prompt_version)
        )
        self.extract_medication = dspy.ChainOfThought(
            build_exect_s0_s1_family_specific_signature(
                "annotated_medication",
                prompt_version,
            )
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        diagnosis = self.extract_diagnosis(note_text=note_text)
        seizure_type = self.extract_seizure_type(note_text=note_text)
        medication = self.extract_medication(note_text=note_text)
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


class ExectS0S1FieldFamilyPromptGraphSequentialModule(dspy.Module):
    """Sequential prompt graph: diagnosis -> seizure -> medication with prior context."""

    def __init__(
        self,
        *,
        prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.extract_diagnosis = dspy.ChainOfThought(
            build_exect_s0_s1_family_specific_signature("diagnosis", prompt_version)
        )
        self.extract_seizure_type = dspy.ChainOfThought(
            build_exect_s0_s1_family_specific_signature("seizure_type", prompt_version)
        )
        self.extract_medication = dspy.ChainOfThought(
            build_exect_s0_s1_family_specific_signature(
                "annotated_medication",
                prompt_version,
            )
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        diagnosis = self.extract_diagnosis(note_text=note_text)
        diagnosis_values = _as_list(getattr(diagnosis, "diagnosis", []))
        seizure_context = _format_prior_extractions_context(
            note_text=note_text,
            prior={"diagnosis": diagnosis_values},
            target_field="seizure_type",
        )
        seizure_type = self.extract_seizure_type(note_text=seizure_context)
        seizure_values = _as_list(getattr(seizure_type, "seizure_type", []))
        medication_context = _format_prior_extractions_context(
            note_text=note_text,
            prior={
                "diagnosis": diagnosis_values,
                "seizure_type": seizure_values,
            },
            target_field="annotated_medication",
        )
        medication = self.extract_medication(note_text=medication_context)
        return dspy.Prediction(
            diagnosis=diagnosis_values,
            diagnosis_evidence=_as_list(getattr(diagnosis, "diagnosis_evidence", [])),
            seizure_type=seizure_values,
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


def build_exect_s0_s1_module(
    program_variant: str = EXECT_S0_S1_VARIANT,
    *,
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    include_archive: bool = False,
) -> dspy.Module:
    """Build an ExECT S0/S1 module for the requested program variant."""
    if not include_archive and program_variant not in EXECT_S0_S1_ACTIVE_VARIANTS:
        raise ValueError(
            f"ExECT S0/S1 program variant {program_variant!r} is archive-only; "
            "pass include_archive=True for explicit provenance replay."
        )
    if program_variant == EXECT_S0_S1_SECTION_AWARE_VARIANT:
        return ExectS0S1SectionAwareFieldFamilyModule()
    if program_variant == EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT:
        return ExectS0S1FieldFamilyPromptGraphParallelModule(
            prompt_version=prompt_version
        )
    if program_variant == EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT:
        return ExectS0S1FieldFamilyPromptGraphSequentialModule(
            prompt_version=prompt_version
        )
    if program_variant == EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT:
        return ExectS0S1DiagnosisRecallProbeModule()
    if program_variant == EXECT_S0_S1_VERIFY_REPAIR_VARIANT:
        extraction_prompt_version = resolve_exect_s0_s1_extraction_prompt_version(
            prompt_version
        )
        return ExectS0S1VerifyRepairModule(
            extraction_prompt_version=extraction_prompt_version
        )
    if program_variant == EXECT_S0_S1_PRE_VOCAB_VARIANT:
        return ExectS0S1PreVocabFieldFamilyModule()
    if program_variant == EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT:
        return ExectS0S1MedicationPreVocabFieldFamilyModule()
    if program_variant == EXECT_S0_S1_MEDICATION_ONLY_E13_VARIANT:
        return ExectS0S1MedicationOnlyE13Module(prompt_version=prompt_version)
    if program_variant == EXECT_S0_S1_MEDICATION_LIFECYCLE_CONTEXT_E13_VARIANT:
        return ExectS0S1MedicationLifecycleContextE13Module(
            prompt_version=prompt_version
        )
    if program_variant == EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT:
        return ExectS0S1SeizurePreVocabFieldFamilyModule()
    if program_variant == EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT:
        return ExectS0S1DeterministicOnlyModule()
    if program_variant == EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT:
        return ExectS1CleanLadderDiagnosisStableEnsembleModule()
    if program_variant == EXECT_S0_S1_CLEAN_LADDER_V1_FAMILY_SPAN_VARIANT:
        return ExectS0S1FamilySpanFieldFamilyModule(prompt_version=prompt_version)
    if program_variant in {EXECT_S0_S1_VARIANT, EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT}:
        return ExectS0S1FieldFamilyModule(prompt_version=prompt_version)
    raise ValueError(f"Unsupported ExECT S0/S1 program variant: {program_variant!r}")


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


