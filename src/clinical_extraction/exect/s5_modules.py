"""DSPy modules for the ExECT S5 operational stack."""
from __future__ import annotations

from collections.abc import Callable

import dspy

from clinical_extraction.exect.frequency_payload import (
    build_exect_frequency_pre_vocab_labels as build_precomputed_seizure_frequency_candidates,
    format_exect_frequency_pre_vocab_note as format_note_with_precomputed_seizure_frequency_candidates,
)
from clinical_extraction.exect.s5_signatures import (
    ExectS5SeizureFrequencyVerifierSignature,
    ExectS5SeizureFrequencyVerifierV2Signature,
    build_exect_s5_core_family_specific_signature,
)
from clinical_extraction.exect.s5_stack import (
    apply_exect_s5_frequency_verifier_guards,
)
from clinical_extraction.exect.s0_s1.prediction_artifacts import _as_list

ExtractorFactory = Callable[[], dspy.Module]


def _default_s4_prompt_version() -> str:
    from clinical_extraction.programs.exect_s4 import EXECT_S4_PROMPT_VERSION

    return EXECT_S4_PROMPT_VERSION


def _default_s4_pre_vocab_extractor() -> dspy.Module:
    from clinical_extraction.programs.exect_s4 import (
        ExectS4FrequencyPreVocabFieldFamilyModule,
    )

    return ExectS4FrequencyPreVocabFieldFamilyModule()


def _default_s4_pre_vocab_v13_extractor() -> dspy.Module:
    from clinical_extraction.programs.exect_s4 import (
        ExectS4FrequencyPreVocabV13FieldFamilyModule,
    )

    return ExectS4FrequencyPreVocabV13FieldFamilyModule()


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


def _frequency_verified_prediction(
    *,
    initial: dspy.Prediction,
    guarded: dspy.Prediction,
    candidates: list[str],
    initial_frequency: list[str],
) -> dspy.Prediction:
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


class ExectS5FrequencyPreVocabAmGuardFrequencyVerifyModule(dspy.Module):
    """S5 pre-vocab extractor followed by reject-only frequency verification."""

    def __init__(
        self,
        *,
        extractor: dspy.Module | None = None,
        verifier: dspy.Module | None = None,
        extractor_factory: ExtractorFactory = _default_s4_pre_vocab_extractor,
    ) -> None:
        super().__init__()
        self.extractor = extractor or extractor_factory()
        self.verifier = verifier or ExectS5SeizureFrequencyVerifierModule()

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
        guarded = apply_exect_s5_frequency_verifier_guards(
            note_text=note_text,
            initial_frequency=initial_frequency,
            verified=verified,
        )
        return _frequency_verified_prediction(
            initial=initial,
            guarded=guarded,
            candidates=candidates,
            initial_frequency=initial_frequency,
        )


class ExectS5FrequencyPreVocabAmGuardFrequencyVerifyV2Module(dspy.Module):
    """S5 v1.3 extractor + v2 residual-tuned reject-only frequency verification."""

    def __init__(
        self,
        *,
        extractor: dspy.Module | None = None,
        verifier: dspy.Module | None = None,
        extractor_factory: ExtractorFactory = _default_s4_pre_vocab_v13_extractor,
    ) -> None:
        super().__init__()
        self.extractor = extractor or extractor_factory()
        self.verifier = verifier or ExectS5SeizureFrequencyVerifierV2Module()

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
        guarded = apply_exect_s5_frequency_verifier_guards(
            note_text=note_text,
            initial_frequency=initial_frequency,
            verified=verified,
            strict_qualitative=True,
        )
        return _frequency_verified_prediction(
            initial=initial,
            guarded=guarded,
            candidates=candidates,
            initial_frequency=initial_frequency,
        )


class ExectS5FrequencyPreVocabAmGuardFrequencyVerifyV2bModule(dspy.Module):
    """S5 v1.2 extractor + v2 verifier rules only (no v1.3 prompt, no strict qualitative guard)."""

    def __init__(
        self,
        *,
        extractor: dspy.Module | None = None,
        verifier: dspy.Module | None = None,
        extractor_factory: ExtractorFactory = _default_s4_pre_vocab_extractor,
    ) -> None:
        super().__init__()
        self.extractor = extractor or extractor_factory()
        self.verifier = verifier or ExectS5SeizureFrequencyVerifierV2Module()

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
        guarded = apply_exect_s5_frequency_verifier_guards(
            note_text=note_text,
            initial_frequency=initial_frequency,
            verified=verified,
            strict_qualitative=False,
        )
        return _frequency_verified_prediction(
            initial=initial,
            guarded=guarded,
            candidates=candidates,
            initial_frequency=initial_frequency,
        )


class ExectS5CoreFieldFamilyParallelV2bModule(dspy.Module):
    """Full-note parallel per-family S5-core extraction with v2b frequency post-stack."""

    def __init__(
        self,
        *,
        prompt_version: str | None = None,
        verifier: dspy.Module | None = None,
    ) -> None:
        super().__init__()
        resolved_prompt_version = prompt_version or _default_s4_prompt_version()
        self.extract_diagnosis = dspy.ChainOfThought(
            build_exect_s5_core_family_specific_signature(
                "diagnosis",
                resolved_prompt_version,
            )
        )
        self.extract_seizure_type = dspy.ChainOfThought(
            build_exect_s5_core_family_specific_signature(
                "seizure_type",
                resolved_prompt_version,
            )
        )
        self.extract_medication = dspy.ChainOfThought(
            build_exect_s5_core_family_specific_signature(
                "annotated_medication",
                resolved_prompt_version,
            )
        )
        self.extract_investigation = dspy.ChainOfThought(
            build_exect_s5_core_family_specific_signature(
                "investigation",
                resolved_prompt_version,
            )
        )
        self.extract_seizure_frequency = dspy.ChainOfThought(
            build_exect_s5_core_family_specific_signature(
                "seizure_frequency",
                resolved_prompt_version,
            )
        )
        self.verifier = verifier or ExectS5SeizureFrequencyVerifierV2Module()

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
        guarded = apply_exect_s5_frequency_verifier_guards(
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
