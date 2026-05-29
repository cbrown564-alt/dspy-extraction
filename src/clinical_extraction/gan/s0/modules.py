"""Gan S0 DSPy program modules and variant factory."""
from __future__ import annotations

import json
from typing import Any

import dspy

from clinical_extraction.gan.s0.date_events import (
    GanDateEventPayload,
    build_deterministic_date_event_payload,
    validate_and_fallback_label,
)
from clinical_extraction.gan.s0.prediction_bridge import (
    _apply_constrained_verifier_guard,
    _apply_evidence_span_check_guard,
    _apply_temporal_verifier_guards,
    _evidence_policy_feedback,
    _normalize_predicted_label,
)
from clinical_extraction.gan.s0.signatures import (
    GAN_FREQUENCY_S0_ADJUDICATE_VR_SPAN_CHECK_PROMPT_VERSIONS,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_GENERATOR_ADDENDUM,
    GanFrequencyS0DateEventsExtractionSignature,
    GanFrequencyS0EntityTagsSignature,
    GanFrequencyS0CandidateRankingTargetSelectorSignature,
    GanFrequencyS0ExplicitReasonCodeAdjudicatorSignature,
    GanFrequencyS0LlmTemporalCandidatesSignature,
    GanFrequencyS0MultipleAnswerSignature,
    GanFrequencyS0ReactTemporalToolsSignature,
    GanFrequencyS0SeededMultipleAnswerSignature,
    GanFrequencyS0Signature,
    GanFrequencyS0SpecialClassTargetSelectorSignature,
    GanFrequencyS0TemporalEventTableAdjudicateSignature,
    GanFrequencyS0TemporalEventTableSignature,
    GanFrequencyS0TemporalEventTableVerifierSignature,
    build_gan_frequency_s0_extractor_signature,
    build_gan_frequency_s0_verifier_signature,
    resolve_gan_frequency_s0_extractor_prompt_version,
    resolve_gan_frequency_s0_verifier_prompt_version,
)
from clinical_extraction.gan.s0.variant_routing import (
    GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY,
    GAN_CONTEXT_POLICY_FULL_NOTE_PLUS_DETERMINISTIC_TEMPORAL_CANDIDATES,
    GAN_FREQUENCY_S0_CONFIRM_ONLY_VERIFIER_PROMPT_VERSION,
    GAN_FREQUENCY_S0_CANDIDATE_RANKING_TARGET_SELECTOR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_CANDIDATE_RANKING_TARGET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_DIRECT_GUARDRAILS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION,
    GAN_FREQUENCY_S0_EXPLICIT_REASON_CODE_ADJUDICATOR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_EXPLICIT_REASON_CODE_ADJUDICATOR_VARIANT,
    GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
    GAN_FREQUENCY_S0_RETRIEVAL_EMPTY_CANDIDATES_NOTE_STUB,
    GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_SPECIAL_CLASS_TARGET_SELECTOR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_SPECIAL_CLASS_TARGET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_NO_GUARDS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_VARIANT,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
    default_gan_frequency_s0_prompt_version,
)


class GanFrequencyS0Module(dspy.Module):
    """Narrow Gan seizure-frequency S0 DSPy module.

    Uses ChainOfThought so the model reasons before committing to a label.
    Compile with BootstrapFewShot or MIPROv2 + ``gan_frequency_s0_metric``
    before running on the evaluation split.
    """

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(GanFrequencyS0Signature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


class GanFrequencyS0DirectModule(dspy.Module):
    """Gan S0 module that predicts the structured fields without a reasoning output."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_DIRECT_GUARDRAILS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.extract = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


class GanFrequencyS0VerifierModule(dspy.Module):
    """Standalone verifier for Gan S0 predictions."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        signature_cls = build_gan_frequency_s0_verifier_signature(
            prompt_version,
            temporal=False,
        )
        self.verify = dspy.Predict(signature_cls)

    def forward(
        self,
        note_text: str,
        initial_label: str | None,
        initial_evidence: str | None,
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            initial_label=initial_label,
            initial_evidence=initial_evidence,
        )


class GanFrequencyS0VerifyRepairModule(dspy.Module):
    """Gan S0 module that extracts then verifies/repairs the prediction."""

    def __init__(
        self,
        extractor_variant: str = GAN_FREQUENCY_S0_DIRECT_VARIANT,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        extractor_prompt_version = resolve_gan_frequency_s0_extractor_prompt_version(
            prompt_version
        )
        self.extractor = build_gan_s0_module(
            extractor_variant,
            prompt_version=extractor_prompt_version,
            include_archive=True,
        )
        self.verifier = GanFrequencyS0VerifierModule(prompt_version=prompt_version)

    def forward(self, note_text: str) -> dspy.Prediction:
        initial = self.extractor(note_text=note_text)
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        return dspy.Prediction(
            seizure_frequency_number=verified.final_label,
            evidence_text=verified.final_evidence,
            verifier_decision=verified.decision,
            verifier_reason=verified.reason,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )


class GanFrequencyS0TemporalVerifierModule(dspy.Module):
    """Verifier that receives deterministic temporal-candidate structure."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        signature_cls = build_gan_frequency_s0_verifier_signature(
            prompt_version,
            temporal=True,
        )
        self.verify = dspy.Predict(signature_cls)

    def forward(
        self,
        note_text: str,
        initial_label: str | None,
        initial_evidence: str | None,
        temporal_candidates: str,
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            initial_label=initial_label,
            initial_evidence=initial_evidence,
            temporal_candidates=temporal_candidates,
        )


class GanFrequencyS0TemporalCandidatesVerifyRepairModule(dspy.Module):
    """Direct extraction plus temporal-candidate-aware verify/repair."""

    def __init__(
        self,
        extractor_variant: str = GAN_FREQUENCY_S0_DIRECT_VARIANT,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        extractor_prompt_version = resolve_gan_frequency_s0_extractor_prompt_version(
            prompt_version
        )
        self.extractor = build_gan_s0_module(
            extractor_variant,
            prompt_version=extractor_prompt_version,
            include_archive=True,
        )
        self.verifier = GanFrequencyS0TemporalVerifierModule(prompt_version=prompt_version)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
            temporal_candidate_to_dict,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.extractor(note_text=note_text)
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
        )
        if self.prompt_version == GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION:
            verified = _apply_evidence_span_check_guard(
                note_text,
                verified,
                initial_label=initial.seizure_frequency_number,
                initial_evidence=initial.evidence_text,
            )
        return dspy.Prediction(
            seizure_frequency_number=verified.final_label,
            evidence_text=verified.final_evidence,
            verifier_decision=verified.decision,
            verifier_reason=verified.reason,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
            temporal_candidate_labels=[c.canonical_label for c in candidates],
            temporal_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
        )


def prompt_note_text_for_context_policy(
    note_text: str,
    candidates: list[Any],
    *,
    context_policy: str,
) -> str:
    """Assemble prompt-visible note text for retrieval/context-selection arms."""

    if context_policy == GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY:
        spans: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            evidence = getattr(candidate, "evidence_text", "")
            if evidence and evidence not in seen:
                seen.add(evidence)
                spans.append(evidence)
        if spans:
            return "\n\n---\n\n".join(spans)
        return GAN_FREQUENCY_S0_RETRIEVAL_EMPTY_CANDIDATES_NOTE_STUB
    return note_text


def _prompt_note_text_for_context_policy(
    note_text: str,
    candidates: list[Any],
    *,
    context_policy: str,
) -> str:
    return prompt_note_text_for_context_policy(
        note_text,
        candidates,
        context_policy=context_policy,
    )


class GanFrequencyS0TemporalCandidatesSinglePassModule(dspy.Module):
    """Deterministic temporal candidates followed by a single LLM adjudication pass."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
        candidate_presentation: str | None = None,
        context_policy: str = (
            GAN_CONTEXT_POLICY_FULL_NOTE_PLUS_DETERMINISTIC_TEMPORAL_CANDIDATES
        ),
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.candidate_presentation = candidate_presentation
        self.context_policy = context_policy
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            TemporalCandidatePresentation,
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        presentation: TemporalCandidatePresentation = (
            self.candidate_presentation or "prose"
        )
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            presentation=presentation,
        )
        prompt_note_text = _prompt_note_text_for_context_policy(
            note_text,
            candidates,
            context_policy=self.context_policy,
        )
        result = self.adjudicate(
            note_text=prompt_note_text,
            temporal_candidates=temporal_candidates_text,
        )
        return _temporal_adjudication_prediction(
            result,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            candidate_source="deterministic",
            extra_metadata={
                "context_policy": self.context_policy,
                "prompt_note_text_is_full_note": (
                    self.context_policy
                    != GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY
                ),
                "prompt_note_text_char_count": len(prompt_note_text),
                "source_note_text_char_count": len(note_text),
            },
        )


def _build_gan_frequency_s0_llm_candidate_generator_signature() -> type[
    GanFrequencyS0LlmTemporalCandidatesSignature
]:
    doc = (GanFrequencyS0LlmTemporalCandidatesSignature.__doc__ or "") + (
        GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_GENERATOR_ADDENDUM
    )
    return type(
        "GanFrequencyS0LlmTemporalCandidatesGeneratorSignature",
        (GanFrequencyS0LlmTemporalCandidatesSignature,),
        {"__doc__": doc},
    )


class GanFrequencyS0LlmTemporalCandidatesGeneratorModule(dspy.Module):
    """Model pass that emits structured temporal frequency candidates."""

    def __init__(self) -> None:
        super().__init__()
        signature_cls = _build_gan_frequency_s0_llm_candidate_generator_signature()
        self.generate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.generate(note_text=note_text)


def _temporal_adjudication_prediction(
    result: dspy.Prediction,
    *,
    candidates: list[Any],
    temporal_candidates_text: str,
    candidate_source: str,
    llm_candidate_records: list[dict[str, str]] | None = None,
    extra_metadata: dict[str, Any] | None = None,
) -> dspy.Prediction:
    from clinical_extraction.gan.temporal_candidates import temporal_candidate_to_dict

    metadata: dict[str, Any] = {
        "seizure_frequency_number": result.seizure_frequency_number,
        "evidence_text": result.evidence_text,
        "temporal_candidates": temporal_candidates_text,
        "temporal_candidate_labels": [c.canonical_label for c in candidates],
        "temporal_candidate_records": [
            temporal_candidate_to_dict(candidate) for candidate in candidates
        ],
        "temporal_candidate_source": candidate_source,
    }
    if llm_candidate_records is not None:
        metadata["llm_temporal_candidate_records"] = llm_candidate_records
    if extra_metadata:
        metadata.update(extra_metadata)
    return dspy.Prediction(**metadata)


def _synthetic_confirm_from_adjudicate(
    *,
    initial_label: str | None,
    initial_evidence: str | None,
    reason: str,
) -> dspy.Prediction:
    return dspy.Prediction(
        final_label=initial_label,
        final_evidence=initial_evidence,
        decision="confirm",
        reason=reason,
    )


def _apply_det_evidence_grounding(
    note_text: str,
    *,
    initial_label: str | None,
    initial_evidence: str | None,
) -> dspy.Prediction:
    """Deterministic in-note evidence check before plausibility guards (ladder V3+)."""
    if initial_label in (None, "no seizure frequency reference"):
        return _synthetic_confirm_from_adjudicate(
            initial_label=initial_label,
            initial_evidence=initial_evidence,
            reason="Det evidence grounding skipped for abstain/no-reference.",
        )
    feedback = _evidence_policy_feedback(
        gold_label=initial_label,
        predicted_evidence=initial_evidence,
        note_text=note_text,
    )
    if feedback is None:
        return _synthetic_confirm_from_adjudicate(
            initial_label=initial_label,
            initial_evidence=initial_evidence,
            reason="Det evidence grounding passed.",
        )
    return dspy.Prediction(
        final_label=None,
        final_evidence=None,
        decision="abstain",
        reason=f"Det evidence grounding abstained: {feedback}",
    )


def _prediction_from_temporal_adjudicate_validation(
    *,
    initial_label: str | None,
    initial_evidence: str | None,
    verified: dspy.Prediction,
    candidates: list[Any],
    temporal_candidates_text: str,
    validation_ladder_rung: str,
) -> dspy.Prediction:
    from clinical_extraction.gan.temporal_candidates import temporal_candidate_to_dict

    return dspy.Prediction(
        seizure_frequency_number=verified.final_label,
        evidence_text=verified.final_evidence,
        verifier_decision=verified.decision,
        verifier_reason=verified.reason,
        initial_label=initial_label,
        initial_evidence=initial_evidence,
        temporal_candidates=temporal_candidates_text,
        temporal_candidate_labels=[c.canonical_label for c in candidates],
        temporal_candidate_records=[
            temporal_candidate_to_dict(candidate) for candidate in candidates
        ],
        temporal_candidate_source="deterministic",
        validation_ladder_rung=validation_ladder_rung,
    )


def _llm_temporal_candidates_from_prediction(
    note_text: str,
    prediction: dspy.Prediction,
) -> list[Any]:
    from clinical_extraction.gan.temporal_candidates import (
        parse_llm_temporal_candidates_json,
    )

    return parse_llm_temporal_candidates_json(
        prediction.temporal_candidates_json,
        note_text=note_text,
    )


class GanFrequencyS0LlmTemporalCandidatesSinglePassModule(dspy.Module):
    """LLM temporal candidates followed by a single LLM adjudication pass."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.candidate_generator = GanFrequencyS0LlmTemporalCandidatesGeneratorModule()
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            format_temporal_candidates_for_prompt,
            temporal_candidate_to_dict,
        )

        generated = self.candidate_generator(note_text=note_text)
        candidates = _llm_temporal_candidates_from_prediction(note_text, generated)
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            source="llm",
        )
        result = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        return _temporal_adjudication_prediction(
            result,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            candidate_source="llm",
            llm_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
        )


class GanFrequencyS0HybridTemporalCandidatesSinglePassModule(dspy.Module):
    """Merged deterministic+LLM temporal candidates with LLM adjudication."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.candidate_generator = GanFrequencyS0LlmTemporalCandidatesGeneratorModule()
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
            merge_temporal_frequency_candidates,
            temporal_candidate_to_dict,
        )

        deterministic_candidates = build_temporal_frequency_candidates_from_note(
            note_text
        )
        generated = self.candidate_generator(note_text=note_text)
        llm_candidates = _llm_temporal_candidates_from_prediction(note_text, generated)
        candidates = merge_temporal_frequency_candidates(
            deterministic_candidates,
            llm_candidates,
        )
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            source="hybrid",
        )
        result = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        return _temporal_adjudication_prediction(
            result,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            candidate_source="hybrid",
            llm_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in llm_candidates
            ],
        )


class GanFrequencyS0DateEventsCandidatesSinglePassModule(dspy.Module):
    """Deterministic date/event extraction followed by a single LLM adjudication pass."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        payload = build_deterministic_date_event_payload(note_text)
        payload_json = payload.model_dump_json(indent=2)
        
        result = self.adjudicate(
            note_text=note_text,
            date_event_payload=payload_json,
        )
        final_lbl = validate_and_fallback_label(result.seizure_frequency_number)
        return dspy.Prediction(
            seizure_frequency_number=final_lbl,
            evidence_text=result.evidence_text,
            date_event_payload=payload_json,
            temporal_candidate_labels=payload.candidate_labels,
        )


class GanFrequencyS0LlmDateEventsCandidatesSinglePassModule(dspy.Module):
    """LLM date/event extraction followed by single LLM adjudication."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.extractor = dspy.ChainOfThought(GanFrequencyS0DateEventsExtractionSignature)
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        extracted = self.extractor(note_text=note_text)
        payload_json = extracted.date_event_payload_json
        
        try:
            raw = json.loads(payload_json)
            candidate_labels = raw.get("candidate_labels", [])
        except Exception:
            candidate_labels = []
            
        result = self.adjudicate(
            note_text=note_text,
            date_event_payload=payload_json,
        )
        final_lbl = validate_and_fallback_label(result.seizure_frequency_number)
        return dspy.Prediction(
            seizure_frequency_number=final_lbl,
            evidence_text=result.evidence_text,
            date_event_payload=payload_json,
            temporal_candidate_labels=candidate_labels,
        )


class GanFrequencyS0HybridDateEventsCandidatesSinglePassModule(dspy.Module):
    """Deterministic + LLM date/events merge followed by LLM adjudication."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.extractor = dspy.ChainOfThought(GanFrequencyS0DateEventsExtractionSignature)
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        det_payload = build_deterministic_date_event_payload(note_text)
        extracted = self.extractor(note_text=note_text)
        llm_payload_json = extracted.date_event_payload_json
        
        temporal_anchors = list(det_payload.temporal_anchors)
        seizure_events = list(det_payload.seizure_events)
        seizure_free_intervals = list(det_payload.seizure_free_intervals)
        cluster_events = list(det_payload.cluster_events)
        current_window_cues = list(det_payload.current_window_cues)
        candidate_labels = list(det_payload.candidate_labels)
        
        try:
            raw = json.loads(llm_payload_json)
            if isinstance(raw.get("temporal_anchors"), list):
                temporal_anchors.extend(raw["temporal_anchors"])
            if isinstance(raw.get("seizure_events"), list):
                seizure_events.extend(raw["seizure_events"])
            if isinstance(raw.get("seizure_free_intervals"), list):
                seizure_free_intervals.extend(raw["seizure_free_intervals"])
            if isinstance(raw.get("cluster_events"), list):
                cluster_events.extend(raw["cluster_events"])
            if isinstance(raw.get("current_window_cues"), list):
                current_window_cues.extend(raw["current_window_cues"])
            if isinstance(raw.get("candidate_labels"), list):
                candidate_labels.extend(raw["candidate_labels"])
        except Exception:
            pass

        def to_str(x):
            if isinstance(x, str):
                return x
            if isinstance(x, dict):
                return x.get("text") or x.get("label") or json.dumps(x)
            return str(x)

        temporal_anchors = [to_str(x) for x in temporal_anchors]
        seizure_events = [to_str(x) for x in seizure_events]
        seizure_free_intervals = [to_str(x) for x in seizure_free_intervals]
        cluster_events = [to_str(x) for x in cluster_events]
        current_window_cues = [to_str(x) for x in current_window_cues]
        candidate_labels = [to_str(x) for x in candidate_labels]
            
        merged_payload = GanDateEventPayload(
            clinic_date=det_payload.clinic_date,
            temporal_anchors=list(dict.fromkeys(temporal_anchors)),
            seizure_events=list(dict.fromkeys(seizure_events)),
            seizure_free_intervals=list(dict.fromkeys(seizure_free_intervals)),
            cluster_events=list(dict.fromkeys(cluster_events)),
            current_window_cues=list(dict.fromkeys(current_window_cues)),
            candidate_labels=list(dict.fromkeys(candidate_labels)),
            evidence_text=det_payload.evidence_text,
            stage_confidence=1.0,
        )
        payload_json = merged_payload.model_dump_json(indent=2)
        
        result = self.adjudicate(
            note_text=note_text,
            date_event_payload=payload_json,
        )
        final_lbl = validate_and_fallback_label(result.seizure_frequency_number)
        return dspy.Prediction(
            seizure_frequency_number=final_lbl,
            evidence_text=result.evidence_text,
            date_event_payload=payload_json,
            temporal_candidate_labels=merged_payload.candidate_labels,
        )


class GanFrequencyS0EntityTagsDateEventsSinglePassModule(dspy.Module):
    """LLM clinical entities/events tags -> Date/event payload -> Adjudicate."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.tagger = dspy.Predict(GanFrequencyS0EntityTagsSignature)
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        tagged = self.tagger(note_text=note_text)
        tags_json = tagged.entity_tags_json
        
        temporal_anchors = []
        seizure_events = []
        seizure_free_intervals = []
        cluster_events = []
        current_window_cues = []
        candidate_labels = []
        evidence_pieces = []
        
        try:
            raw = json.loads(tags_json)
            tags = raw.get("entity_tags", [])
            for tag in tags:
                etype = tag.get("entity_type")
                text = tag.get("text", "")
                hint = tag.get("temporality_hint", "")
                count_hint = tag.get("count_or_duration_hint")
                
                if text:
                    evidence_pieces.append(text)
                    
                display = f"{text}"
                if count_hint:
                    display += f" (count/duration: {count_hint})"
                if hint:
                    display += f" [{hint}]"
                    
                if etype == "temporal_anchor":
                    temporal_anchors.append(display)
                elif etype in ("seizure_free_status", "negation_or_absence"):
                    seizure_free_intervals.append(display)
                elif etype == "cluster":
                    cluster_events.append(display)
                elif etype in ("seizure_event", "seizure_frequency"):
                    seizure_events.append(display)
                elif etype in ("medication_change", "other_relevant_context"):
                    current_window_cues.append(display)
                
                if count_hint and etype in ("seizure_event", "seizure_frequency", "cluster"):
                    candidate_labels.append(count_hint)
        except Exception:
            pass
            
        from clinical_extraction.gan.temporal_candidates import _clinic_date
        clinic_d = _clinic_date(note_text)
        clinic_date_str = clinic_d.isoformat() if clinic_d else None
        if clinic_date_str:
            temporal_anchors.append(f"clinic_date={clinic_date_str}")
            
        payload = GanDateEventPayload(
            clinic_date=clinic_date_str,
            temporal_anchors=list(dict.fromkeys(temporal_anchors)),
            seizure_events=list(dict.fromkeys(seizure_events)),
            seizure_free_intervals=list(dict.fromkeys(seizure_free_intervals)),
            cluster_events=list(dict.fromkeys(cluster_events)),
            current_window_cues=list(dict.fromkeys(current_window_cues)),
            candidate_labels=list(dict.fromkeys(candidate_labels)),
            evidence_text=" | ".join(dict.fromkeys(evidence_pieces)) if evidence_pieces else None,
            stage_confidence=1.0,
        )
        payload_json = payload.model_dump_json(indent=2)
        
        result = self.adjudicate(
            note_text=note_text,
            date_event_payload=payload_json,
        )
        return dspy.Prediction(
            seizure_frequency_number=result.seizure_frequency_number,
            evidence_text=result.evidence_text,
            date_event_payload=payload_json,
            temporal_candidate_labels=payload.candidate_labels,
        )


class GanFrequencyS0TemporalCandidatesAdjudicateDetGuardsModule(dspy.Module):
    """Adjudicate then deterministic plausibility guards only (validation ladder V2)."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _synthetic_confirm_from_adjudicate(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            reason="Synthetic confirm for det-plausibility rung (no LLM verifier).",
        )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
        )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung="det_plausibility",
        )


class GanFrequencyS0TemporalCandidatesAdjudicateDetEvidenceModule(dspy.Module):
    """Adjudicate, deterministic evidence grounding, then plausibility guards (V3)."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_det_evidence_grounding(
            note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        if verified.decision != "abstain":
            verified = _apply_temporal_verifier_guards(
                initial_label=initial.seizure_frequency_number,
                initial_evidence=initial.evidence_text,
                verified=verified,
                candidates=candidates,
            )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung="det_evidence_grounding",
        )


class GanFrequencyS0TemporalCandidatesAdjudicateConfirmOnlyModule(dspy.Module):
    """V3 stack plus LLM verifier restricted to confirm-only (V4)."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_CONFIRM_ONLY_VERIFIER_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        adjudicate_prompt = resolve_gan_frequency_s0_extractor_prompt_version(
            prompt_version
        )
        signature_cls = build_gan_frequency_s0_extractor_signature(adjudicate_prompt)
        self.adjudicate = dspy.Predict(signature_cls)
        verifier_prompt = resolve_gan_frequency_s0_verifier_prompt_version(prompt_version)
        self.verifier = GanFrequencyS0TemporalVerifierModule(
            prompt_version=verifier_prompt
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_det_evidence_grounding(
            note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        if verified.decision == "abstain":
            return _prediction_from_temporal_adjudicate_validation(
                initial_label=initial.seizure_frequency_number,
                initial_evidence=initial.evidence_text,
                verified=verified,
                candidates=candidates,
                temporal_candidates_text=temporal_candidates_text,
                validation_ladder_rung="llm_confirm_only",
            )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
        )
        verified = self.verifier(
            note_text=note_text,
            initial_label=verified.final_label,
            initial_evidence=verified.final_evidence,
            temporal_candidates=temporal_candidates_text,
        )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung="llm_confirm_only",
        )


class GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairNoGuardsModule(dspy.Module):
    """Det evidence grounding plus full LLM verify-repair without post-VR guards (V5)."""

    def __init__(
        self,
        *,
        prompt_version: str = (
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_PROMPT_VERSION
        ),
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        adjudicate_prompt = resolve_gan_frequency_s0_extractor_prompt_version(
            prompt_version
        )
        signature_cls = build_gan_frequency_s0_extractor_signature(adjudicate_prompt)
        self.adjudicate = dspy.Predict(signature_cls)
        verifier_prompt = resolve_gan_frequency_s0_verifier_prompt_version(prompt_version)
        self.verifier = GanFrequencyS0TemporalVerifierModule(
            prompt_version=verifier_prompt
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_det_evidence_grounding(
            note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        if verified.decision == "abstain":
            return _prediction_from_temporal_adjudicate_validation(
                initial_label=initial.seizure_frequency_number,
                initial_evidence=initial.evidence_text,
                verified=verified,
                candidates=candidates,
                temporal_candidates_text=temporal_candidates_text,
                validation_ladder_rung="llm_verify_repair",
            )
        verified = self.verifier(
            note_text=note_text,
            initial_label=verified.final_label,
            initial_evidence=verified.final_evidence,
            temporal_candidates=temporal_candidates_text,
        )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung="llm_verify_repair",
        )


class GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairModule(dspy.Module):
    """Deterministic candidates, LLM adjudicate, then temporal verify-repair."""

    def __init__(
        self,
        *,
        prompt_version: str = (
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_PROMPT_VERSION
        ),
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)
        verifier_prompt = resolve_gan_frequency_s0_verifier_prompt_version(prompt_version)
        self.verifier = GanFrequencyS0TemporalVerifierModule(
            prompt_version=verifier_prompt
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
        )
        if self.prompt_version in GAN_FREQUENCY_S0_ADJUDICATE_VR_SPAN_CHECK_PROMPT_VERSIONS:
            verified = _apply_evidence_span_check_guard(
                note_text,
                verified,
                initial_label=initial.seizure_frequency_number,
                initial_evidence=initial.evidence_text,
            )
        ladder_rung = (
            "llm_vr_det_guards_span_check"
            if self.prompt_version in GAN_FREQUENCY_S0_ADJUDICATE_VR_SPAN_CHECK_PROMPT_VERSIONS
            else "llm_verify_repair_det_guards"
        )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung=ladder_rung,
        )


class GanFrequencyS0TemporalCandidatesAdjudicateConstrainedVerifierModule(dspy.Module):
    """Deterministic candidates, LLM adjudicate, then constrained verify-repair."""

    def __init__(
        self,
        *,
        prompt_version: str = (
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_PROMPT_VERSION
        ),
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        extractor_prompt_version = resolve_gan_frequency_s0_extractor_prompt_version(prompt_version)
        signature_cls = build_gan_frequency_s0_extractor_signature(extractor_prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)
        verifier_prompt = resolve_gan_frequency_s0_verifier_prompt_version(prompt_version)
        self.verifier = GanFrequencyS0TemporalVerifierModule(
            prompt_version=verifier_prompt
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_constrained_verifier_guard(
            note_text=note_text,
            verified=verified,
            candidates=candidates,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung="constrained_verifier",
        )


class GanFrequencyS0LlmTemporalCandidatesVerifyRepairModule(dspy.Module):
    """LLM candidates, LLM adjudicate, then temporal verify-repair."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.candidate_generator = GanFrequencyS0LlmTemporalCandidatesGeneratorModule()
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)
        self.verifier = GanFrequencyS0TemporalVerifierModule(
            prompt_version=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            format_temporal_candidates_for_prompt,
            temporal_candidate_to_dict,
        )

        generated = self.candidate_generator(note_text=note_text)
        candidates = _llm_temporal_candidates_from_prediction(note_text, generated)
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            source="llm",
        )
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
        )
        return dspy.Prediction(
            seizure_frequency_number=verified.final_label,
            evidence_text=verified.final_evidence,
            verifier_decision=verified.decision,
            verifier_reason=verified.reason,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
            temporal_candidate_labels=[c.canonical_label for c in candidates],
            temporal_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
            temporal_candidate_source="llm",
            llm_temporal_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
        )


class GanFrequencyS0TemporalEventTableExtractorModule(dspy.Module):
    """Model pass that emits a structured temporal event table."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.Predict(GanFrequencyS0TemporalEventTableSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


class GanFrequencyS0TemporalEventTableVerifierModule(dspy.Module):
    """Verifier that receives deterministic candidates and an event table."""

    def __init__(self) -> None:
        super().__init__()
        self.verify = dspy.Predict(GanFrequencyS0TemporalEventTableVerifierSignature)

    def forward(
        self,
        note_text: str,
        initial_label: str | None,
        initial_evidence: str | None,
        temporal_candidates: str,
        temporal_event_table: str,
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            initial_label=initial_label,
            initial_evidence=initial_evidence,
            temporal_candidates=temporal_candidates,
            temporal_event_table=temporal_event_table,
        )


class GanFrequencyS0TemporalEventTableVerifyRepairModule(dspy.Module):
    """Direct extraction, model event table, then temporal verify/repair."""

    def __init__(self, extractor_variant: str = GAN_FREQUENCY_S0_DIRECT_VARIANT) -> None:
        super().__init__()
        self.extractor = build_gan_s0_module(extractor_variant, include_archive=True)
        self.event_table_extractor = GanFrequencyS0TemporalEventTableExtractorModule()
        self.verifier = GanFrequencyS0TemporalEventTableVerifierModule()

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
            temporal_candidate_to_dict,
        )
        from clinical_extraction.gan.temporal_events import (
            format_temporal_event_table_for_prompt,
            parse_temporal_event_table_json,
            temporal_event_table_to_dict,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.extractor(note_text=note_text)
        event_table_raw = self.event_table_extractor(note_text=note_text)
        event_table = parse_temporal_event_table_json(
            event_table_raw.event_table_json,
            note_text=note_text,
        )
        temporal_event_table_text = format_temporal_event_table_for_prompt(event_table)
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
            temporal_event_table=temporal_event_table_text,
        )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            event_table=event_table,
        )
        return dspy.Prediction(
            seizure_frequency_number=verified.final_label,
            evidence_text=verified.final_evidence,
            verifier_decision=verified.decision,
            verifier_reason=verified.reason,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
            temporal_candidate_labels=[c.canonical_label for c in candidates],
            temporal_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
            temporal_event_table=temporal_event_table_text,
            temporal_event_table_records=temporal_event_table_to_dict(event_table),
        )


class GanFrequencyS0TemporalEventTableSinglePassModule(dspy.Module):
    """Model event table followed by one final LLM adjudication pass."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.event_table_extractor = GanFrequencyS0TemporalEventTableExtractorModule()
        self.adjudicate = dspy.Predict(GanFrequencyS0TemporalEventTableAdjudicateSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_events import (
            format_temporal_event_table_for_prompt,
            parse_temporal_event_table_json,
            temporal_event_table_to_dict,
        )

        event_table_raw = self.event_table_extractor(note_text=note_text)
        event_table = parse_temporal_event_table_json(
            event_table_raw.event_table_json,
            note_text=note_text,
        )
        temporal_event_table_text = format_temporal_event_table_for_prompt(event_table)
        result = self.adjudicate(
            note_text=note_text,
            temporal_event_table=temporal_event_table_text,
        )
        return dspy.Prediction(
            seizure_frequency_number=result.seizure_frequency_number,
            evidence_text=result.evidence_text,
            temporal_event_table=temporal_event_table_text,
            temporal_event_table_records=temporal_event_table_to_dict(event_table),
            temporal_candidate_source="llm_event_table",
            prompt_version=self.prompt_version,
        )


def _multiple_answer_option_to_dict(option: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "canonical_label": option["canonical_label"],
        "evidence_text": option.get("evidence_text"),
        "status": option.get("status", ""),
        "ambiguity_flags": list(option.get("ambiguity_flags", [])),
        "rationale": option.get("rationale", ""),
    }
    if "source" in option:
        payload["source"] = option["source"]
    if "rejection_reason" in option:
        payload["rejection_reason"] = option["rejection_reason"]
    return payload


def _raw_multiple_answer_option_to_dict(
    row: dict[str, Any],
    *,
    rejection_reason: str,
) -> dict[str, Any]:
    flags_raw = row.get("ambiguity_flags") or []
    if isinstance(flags_raw, str):
        flags = [flags_raw]
    elif isinstance(flags_raw, list):
        flags = [str(flag) for flag in flags_raw if str(flag).strip()]
    else:
        flags = []
    return {
        "canonical_label": row.get("canonical_label"),
        "evidence_text": row.get("evidence_text"),
        "status": row.get("status"),
        "ambiguity_flags": flags,
        "rationale": row.get("rationale"),
        "source": row.get("source", "llm_answer_option"),
        "rejection_reason": rejection_reason,
    }


def _parse_multiple_answer_options_json(
    payload: str | dict[str, Any] | None,
    *,
    note_text: str,
) -> list[dict[str, Any]]:
    parsed, _rejected = _parse_multiple_answer_options_json_with_rejections(
        payload,
        note_text=note_text,
    )
    return parsed


def _parse_multiple_answer_options_json_with_rejections(
    payload: str | dict[str, Any] | None,
    *,
    note_text: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if payload is None:
        return [], []
    if isinstance(payload, str):
        stripped = payload.strip()
        if not stripped or stripped.lower() in {"none", "null"}:
            return [], []
        try:
            raw = json.loads(stripped)
        except json.JSONDecodeError:
            return [], [
                {
                    "canonical_label": None,
                    "evidence_text": None,
                    "status": None,
                    "ambiguity_flags": [],
                    "rationale": payload,
                    "source": "llm_answer_option",
                    "rejection_reason": "invalid_json",
                }
            ]
    else:
        raw = payload

    if isinstance(raw, list):
        rows = raw
    elif isinstance(raw, dict):
        rows = raw.get("answer_options") or raw.get("candidates") or []
    else:
        return [], []
    if not isinstance(rows, list):
        return [], []

    parsed: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen: set[tuple[str, str | None]] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        label_raw = row.get("canonical_label")
        if not isinstance(label_raw, str) or not label_raw.strip():
            rejected.append(
                _raw_multiple_answer_option_to_dict(
                    row,
                    rejection_reason="missing_canonical_label",
                )
            )
            continue
        label = _normalize_predicted_label(label_raw)
        if not label:
            rejected.append(
                _raw_multiple_answer_option_to_dict(
                    row,
                    rejection_reason="empty_normalized_label",
                )
            )
            continue
        evidence = row.get("evidence_text")
        evidence_text = evidence.strip() if isinstance(evidence, str) else None
        if label != "no seizure frequency reference" and (
            not evidence_text or evidence_text not in note_text
        ):
            rejected.append(
                _raw_multiple_answer_option_to_dict(
                    row,
                    rejection_reason="unsupported_or_missing_evidence",
                )
            )
            continue
        try:
            _multiple_answer_label_class(label)
        except ValueError:
            rejected.append(
                _raw_multiple_answer_option_to_dict(
                    row,
                    rejection_reason="noncanonical_label",
                )
            )
            continue
        flags_raw = row.get("ambiguity_flags") or []
        if isinstance(flags_raw, str):
            flags = [flags_raw]
        elif isinstance(flags_raw, list):
            flags = [str(flag) for flag in flags_raw if str(flag).strip()]
        else:
            flags = []
        status = str(row.get("status") or "").strip().lower()
        option = {
            "canonical_label": label,
            "evidence_text": evidence_text,
            "status": status,
            "ambiguity_flags": flags,
            "rationale": str(row.get("rationale") or ""),
            "source": str(row.get("source") or "llm_answer_option"),
        }
        key = (label, evidence_text)
        if key in seen:
            rejected.append(
                _raw_multiple_answer_option_to_dict(
                    row,
                    rejection_reason="duplicate_label_evidence",
                )
            )
            continue
        seen.add(key)
        parsed.append(option)
    return parsed, rejected


def _multiple_answer_label_class(label: str) -> str:
    from clinical_extraction.gan.frequency import label_to_monthly_frequency

    normalized = label.strip().lower()
    if normalized == "no seizure frequency reference":
        return "no_reference"
    if normalized == "unknown" or normalized.startswith("unknown,"):
        return "unknown"
    if normalized.startswith("seizure free for "):
        label_to_monthly_frequency(normalized)
        return "seizure_free"
    label_to_monthly_frequency(normalized)
    return "quantified"


def _multiple_answer_selector_score(option: dict[str, Any]) -> tuple[int, float, str]:
    from clinical_extraction.gan.frequency import label_to_monthly_frequency

    label = option["canonical_label"]
    label_class = _multiple_answer_label_class(label)
    flags = {str(flag).lower() for flag in option.get("ambiguity_flags", [])}
    status = str(option.get("status") or "").lower()

    if label_class == "quantified":
        rank = 400
        if status == "historical" or "historical_only" in flags:
            rank -= 150
        if {"denominator_missing", "trigger_conditioned", "pattern_only"} & flags:
            rank -= 120
        return (rank, label_to_monthly_frequency(label), label)
    if label_class == "seizure_free":
        rank = 350
        if status == "historical" or "historical_only" in flags:
            rank -= 150
        return (rank, 0.0, label)
    if label_class == "unknown":
        rank = 300
        if {"denominator_missing", "trigger_conditioned", "pattern_only"} & flags:
            rank += 25
        return (rank, 0.0, label)
    return (100, 0.0, label)


def select_gan_multiple_answer_option(
    options: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Select one answer option with a deterministic Gan-policy hierarchy."""

    if not options:
        return None
    return max(options, key=_multiple_answer_selector_score)


def _coerce_candidate_index(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return int(stripped)
    return None


def _parse_reason_code_adjudication_json(payload: str | dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {"rejection_reason": "missing_adjudication_json"}
    if isinstance(payload, str):
        stripped = payload.strip()
        if not stripped or stripped.lower() in {"none", "null"}:
            return {"rejection_reason": "empty_adjudication_json"}
        try:
            raw = json.loads(stripped)
        except json.JSONDecodeError:
            return {
                "rejection_reason": "invalid_json",
                "raw_adjudication": payload,
            }
    else:
        raw = payload

    if not isinstance(raw, dict):
        return {"rejection_reason": "adjudication_not_object"}

    inputs = raw.get("label_construction_inputs") or {}
    if not isinstance(inputs, dict):
        inputs = {"raw": inputs}
    ranking = raw.get("candidate_ranking") or []
    if not isinstance(ranking, list):
        ranking = []
    ranking = [
        candidate_index
        for candidate_index in (_coerce_candidate_index(value) for value in ranking)
        if candidate_index is not None
    ]

    return {
        "target_semantic_class": str(
            raw.get("target_semantic_class") or "missing_target_semantic_class"
        ).strip(),
        "category_decision": str(
            raw.get("category_decision") or raw.get("target_semantic_class") or "missing_category_decision"
        ).strip(),
        "candidate_ranking": ranking,
        "reason_code": str(raw.get("reason_code") or "missing_reason_code").strip(),
        "selected_candidate_index": _coerce_candidate_index(
            raw.get("selected_candidate_index")
        ),
        "selected_candidate_label": raw.get("selected_candidate_label"),
        "selected_evidence_text": raw.get("selected_evidence_text"),
        "label_construction_inputs": inputs,
        "final_benchmark_label": raw.get("final_benchmark_label"),
        "final_evidence_text": raw.get("final_evidence_text"),
        "error_class": str(raw.get("error_class") or "none").strip(),
    }


def _candidate_label_construction_inputs(candidate: Any) -> dict[str, Any]:
    return {
        "event_count": candidate.event_count,
        "window_count": candidate.window_count,
        "window_unit": candidate.window_unit,
    }


def _selected_candidate_reference(
    *,
    candidate: Any,
    candidate_index: int,
    constructed_label: str | None,
    construction_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    from clinical_extraction.gan.temporal_candidates import temporal_candidate_to_dict

    return {
        "candidate_index": candidate_index,
        **temporal_candidate_to_dict(candidate),
        "construction_status": construction_status,
        "constructed_label": constructed_label,
        "failure_reason": failure_reason,
    }


def _prediction_from_reason_code_adjudication(
    *,
    adjudication: dict[str, Any],
    candidates: list[Any],
    temporal_candidates_text: str,
    temporal_candidate_source: str = "explicit_reason_code_adjudicator",
) -> dspy.Prediction:
    from clinical_extraction.gan.s0.target_selection import (
        construct_gan_s0_label_from_candidate_record,
    )
    from clinical_extraction.gan.temporal_candidates import temporal_candidate_to_dict

    candidate_records = [temporal_candidate_to_dict(candidate) for candidate in candidates]
    reason_code = str(adjudication.get("reason_code") or "missing_reason_code")
    selected_index = adjudication.get("selected_candidate_index")
    selected_reference: dict[str, Any] | None = None
    label_inputs = adjudication.get("label_construction_inputs") or {}
    rejection_reason = adjudication.get("rejection_reason")

    if isinstance(selected_index, int) and 1 <= selected_index <= len(candidates):
        candidate = candidates[selected_index - 1]
        constructed = construct_gan_s0_label_from_candidate_record(
            temporal_candidate_to_dict(candidate)
        )
        selected_reference = _selected_candidate_reference(
            candidate=candidate,
            candidate_index=selected_index,
            constructed_label=constructed.constructed_label,
            construction_status=constructed.status,
            failure_reason=constructed.failure_reason,
        )
        if not label_inputs:
            label_inputs = _candidate_label_construction_inputs(candidate)
        if constructed.constructed_label is not None:
            model_final = adjudication.get("final_benchmark_label")
            if (
                isinstance(model_final, str)
                and _normalize_predicted_label(model_final) != constructed.constructed_label
            ):
                adjudication = {
                    **adjudication,
                    "model_final_label_mismatch": {
                        "model_final_benchmark_label": model_final,
                        "constructed_label": constructed.constructed_label,
                    },
                }
            return dspy.Prediction(
                seizure_frequency_number=constructed.constructed_label,
                evidence_text=candidate.evidence_text,
                temporal_candidates=temporal_candidates_text,
                temporal_candidate_labels=[c.canonical_label for c in candidates],
                temporal_candidate_records=candidate_records,
                reason_code_adjudication=adjudication,
                selected_candidate_reference=selected_reference,
                label_construction_inputs=label_inputs,
                target_semantic_class=adjudication.get("target_semantic_class"),
                category_decision=adjudication.get("category_decision"),
                candidate_ranking=adjudication.get("candidate_ranking") or [],
                target_selection_reason_code=reason_code,
                target_selection_error_class=adjudication.get("error_class") or "none",
                temporal_candidate_source=temporal_candidate_source,
                verifier_decision="reason_code_candidate_select",
                verifier_reason=(
                    "Constructed final label from explicit selected candidate "
                    f"{selected_index} with reason code {reason_code}."
                ),
            )
        rejection_reason = constructed.failure_reason or "invalid_selected_candidate"

    fallback_label = _normalize_predicted_label(adjudication.get("final_benchmark_label"))
    fallback_evidence = adjudication.get("final_evidence_text")
    if fallback_label is not None:
        try:
            _multiple_answer_label_class(fallback_label)
        except ValueError:
            fallback_label = None

    if fallback_label is None:
        fallback = select_gan_multiple_answer_option(
            _temporal_candidates_to_multiple_answer_options(candidates)
        )
        if fallback is not None:
            fallback_label = fallback["canonical_label"]
            fallback_evidence = fallback.get("evidence_text")
            reason_code = f"{reason_code}:deterministic_candidate_fallback"
        else:
            fallback_label = "unknown"
            fallback_evidence = None
            reason_code = f"{reason_code}:unknown_fallback"

    adjudication = {
        **adjudication,
        "rejection_reason": rejection_reason or "no_valid_selected_candidate",
    }
    return dspy.Prediction(
        seizure_frequency_number=fallback_label,
        evidence_text=fallback_evidence if isinstance(fallback_evidence, str) else None,
        temporal_candidates=temporal_candidates_text,
        temporal_candidate_labels=[c.canonical_label for c in candidates],
        temporal_candidate_records=candidate_records,
        reason_code_adjudication=adjudication,
        selected_candidate_reference=selected_reference,
        label_construction_inputs=label_inputs,
        target_semantic_class=adjudication.get("target_semantic_class"),
        category_decision=adjudication.get("category_decision"),
        candidate_ranking=adjudication.get("candidate_ranking") or [],
        target_selection_reason_code=reason_code,
        target_selection_error_class=adjudication.get("error_class") or "policy",
        temporal_candidate_source=temporal_candidate_source,
        verifier_decision="reason_code_fallback",
        verifier_reason=(
            "Explicit reason-code adjudication did not provide a valid selected "
            "candidate; used deterministic fallback while preserving rejection metadata."
        ),
    )


def _temporal_candidates_to_multiple_answer_options(
    candidates: list[Any],
) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for candidate in candidates:
        label = _normalize_predicted_label(candidate.canonical_label)
        if not label:
            continue
        try:
            _multiple_answer_label_class(label)
        except ValueError:
            continue
        options.append(
            {
                "canonical_label": label,
                "evidence_text": candidate.evidence_text,
                "status": "current",
                "ambiguity_flags": [],
                "rationale": (
                    "Seeded from deterministic temporal candidate "
                    f"{candidate.derivation}."
                ),
                "source": "deterministic_temporal_candidate",
            }
        )
    return options


class GanFrequencyS0MultipleAnswerGeneratorModule(dspy.Module):
    """Model pass that proposes canonical answer options for deterministic selection."""

    def __init__(self) -> None:
        super().__init__()
        self.generate = dspy.Predict(GanFrequencyS0MultipleAnswerSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.generate(note_text=note_text)


class GanFrequencyS0SeededMultipleAnswerGeneratorModule(dspy.Module):
    """Model pass that proposes answer options after seeing deterministic seeds."""

    def __init__(self) -> None:
        super().__init__()
        self.generate = dspy.Predict(GanFrequencyS0SeededMultipleAnswerSignature)

    def forward(self, note_text: str, temporal_candidates: str) -> dspy.Prediction:
        return self.generate(
            note_text=note_text,
            temporal_candidates=temporal_candidates,
        )


class GanFrequencyS0MultipleAnswerDetSelectorModule(dspy.Module):
    """LLM multiple-answer proposer followed by deterministic Gan-policy selector."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.generator = GanFrequencyS0MultipleAnswerGeneratorModule()

    def forward(self, note_text: str) -> dspy.Prediction:
        generated = self.generator(note_text=note_text)
        options = _parse_multiple_answer_options_json(
            generated.answer_options_json,
            note_text=note_text,
        )
        selected = select_gan_multiple_answer_option(options)
        if selected is None:
            return dspy.Prediction(
                seizure_frequency_number="unknown",
                evidence_text=None,
                multiple_answer_options=[],
                selected_answer_option=None,
                temporal_candidate_source="llm_multiple_answer_det_selector",
                verifier_decision="abstain",
                verifier_reason=(
                    "Deterministic selector found no valid note-supported answer options."
                ),
                prompt_version=self.prompt_version,
            )
        return dspy.Prediction(
            seizure_frequency_number=selected["canonical_label"],
            evidence_text=selected.get("evidence_text"),
            multiple_answer_options=[
                _multiple_answer_option_to_dict(option) for option in options
            ],
            selected_answer_option=_multiple_answer_option_to_dict(selected),
            temporal_candidate_source="llm_multiple_answer_det_selector",
            verifier_decision="deterministic_select",
            verifier_reason=(
                "Selected by deterministic Gan policy hierarchy over explicit "
                "canonical answer options."
            ),
            prompt_version=self.prompt_version,
        )


class GanFrequencyS0SeededMultipleAnswerDetSelectorModule(dspy.Module):
    """Deterministic temporal seeds plus LLM options followed by deterministic selection."""

    def __init__(
        self,
        *,
        prompt_version: str = (
            GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_PROMPT_VERSION
        ),
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.generator = GanFrequencyS0SeededMultipleAnswerGeneratorModule()

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
            temporal_candidate_to_dict,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        generated = self.generator(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        llm_options, rejected_options = (
            _parse_multiple_answer_options_json_with_rejections(
                generated.answer_options_json,
                note_text=note_text,
            )
        )
        seeded_options = _temporal_candidates_to_multiple_answer_options(candidates)
        options = seeded_options + llm_options
        selected = select_gan_multiple_answer_option(options)
        if selected is None:
            return dspy.Prediction(
                seizure_frequency_number="unknown",
                evidence_text=None,
                temporal_candidates=temporal_candidates_text,
                temporal_candidate_labels=[c.canonical_label for c in candidates],
                temporal_candidate_records=[
                    temporal_candidate_to_dict(candidate) for candidate in candidates
                ],
                multiple_answer_options=[],
                rejected_multiple_answer_options=rejected_options,
                selected_answer_option=None,
                temporal_candidate_source="seeded_hybrid_multiple_answer_det_selector",
                verifier_decision="abstain",
                verifier_reason=(
                    "Deterministic selector found no valid seeded or LLM answer options."
                ),
                prompt_version=self.prompt_version,
            )
        return dspy.Prediction(
            seizure_frequency_number=selected["canonical_label"],
            evidence_text=selected.get("evidence_text"),
            temporal_candidates=temporal_candidates_text,
            temporal_candidate_labels=[c.canonical_label for c in candidates],
            temporal_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
            multiple_answer_options=[
                _multiple_answer_option_to_dict(option) for option in options
            ],
            rejected_multiple_answer_options=rejected_options,
            selected_answer_option=_multiple_answer_option_to_dict(selected),
            temporal_candidate_source="seeded_hybrid_multiple_answer_det_selector",
            verifier_decision="deterministic_select",
            verifier_reason=(
                "Selected by deterministic Gan policy hierarchy over deterministic "
                "temporal seeds plus valid LLM answer options."
            ),
            prompt_version=self.prompt_version,
        )


class GanFrequencyS0ExplicitReasonCodeAdjudicatorModule(dspy.Module):
    """LLM reason-code target selector with deterministic label construction."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_EXPLICIT_REASON_CODE_ADJUDICATOR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.adjudicate = dspy.Predict(GanFrequencyS0ExplicitReasonCodeAdjudicatorSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            presentation="table",
        )
        generated = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        adjudication = _parse_reason_code_adjudication_json(
            generated.adjudication_json
        )
        prediction = _prediction_from_reason_code_adjudication(
            adjudication=adjudication,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
        )
        prediction.prompt_version = self.prompt_version
        return prediction


def _format_date_event_payload_for_prompt(payload: GanDateEventPayload) -> str:
    return json.dumps(payload.model_dump(), indent=2, sort_keys=True)


class GanFrequencyS0SpecialClassTargetSelectorModule(dspy.Module):
    """G7 selector over D1 date/event payloads and indexed candidates."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_SPECIAL_CLASS_TARGET_SELECTOR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.adjudicate = dspy.Predict(GanFrequencyS0SpecialClassTargetSelectorSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        date_event_payload = build_deterministic_date_event_payload(note_text)
        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            presentation="table",
        )
        generated = self.adjudicate(
            note_text=note_text,
            date_event_payload=_format_date_event_payload_for_prompt(
                date_event_payload
            ),
            temporal_candidates=temporal_candidates_text,
        )
        adjudication = _parse_reason_code_adjudication_json(
            generated.adjudication_json
        )
        prediction = _prediction_from_reason_code_adjudication(
            adjudication=adjudication,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            temporal_candidate_source="special_class_target_selector",
        )
        prediction.temporal_date_event_payload = date_event_payload.model_dump()
        prediction.prompt_version = self.prompt_version
        return prediction


class GanFrequencyS0CandidateRankingTargetSelectorModule(dspy.Module):
    """G10 selector that ranks indexed deterministic candidates directly."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_CANDIDATE_RANKING_TARGET_SELECTOR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.adjudicate = dspy.Predict(
            GanFrequencyS0CandidateRankingTargetSelectorSignature
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            presentation="table",
        )
        generated = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        adjudication = _parse_reason_code_adjudication_json(
            generated.adjudication_json
        )
        prediction = _prediction_from_reason_code_adjudication(
            adjudication=adjudication,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            temporal_candidate_source="candidate_ranking_target_selector",
        )
        prediction.prompt_version = self.prompt_version
        return prediction


class GanFrequencyS0ReactTemporalToolsModule(dspy.Module):
    """Bounded ReAct probe with deterministic temporal helper tools."""

    def __init__(
        self,
        *,
        max_iters: int | None = None,
    ) -> None:
        from clinical_extraction.gan.react_tools import (
            GAN_REACT_TEMPORAL_MAX_ITERS,
            GAN_REACT_TEMPORAL_TOOLS,
        )

        super().__init__()
        self.max_iters = max_iters or GAN_REACT_TEMPORAL_MAX_ITERS
        self.react = dspy.ReAct(
            GanFrequencyS0ReactTemporalToolsSignature,
            tools=GAN_REACT_TEMPORAL_TOOLS,
            max_iters=self.max_iters,
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.react_tools import (
            count_react_tool_calls,
            serialize_react_trajectory,
        )

        try:
            result = self.react(note_text=note_text)
        except Exception as exc:
            return dspy.Prediction(
                seizure_frequency_number="unknown",
                evidence_text=None,
                react_trajectory={},
                react_tool_call_count=0,
                react_error=f"{type(exc).__name__}: {exc}",
            )

        trajectory = getattr(result, "trajectory", {}) or {}
        return dspy.Prediction(
            seizure_frequency_number=result.seizure_frequency_number,
            evidence_text=result.evidence_text,
            react_trajectory=serialize_react_trajectory(trajectory),
            react_tool_call_count=count_react_tool_calls(trajectory),
        )


def build_gan_s0_module(
    program_variant: str,
    *,
    prompt_version: str | None = None,
    candidate_presentation: str | None = None,
    context_policy: str | None = None,
    include_archive: bool = False,
) -> (
    GanFrequencyS0Module
    | GanFrequencyS0DirectModule
    | GanFrequencyS0VerifyRepairModule
    | GanFrequencyS0TemporalCandidatesVerifyRepairModule
    | GanFrequencyS0TemporalCandidatesSinglePassModule
    | GanFrequencyS0TemporalEventTableVerifyRepairModule
    | GanFrequencyS0TemporalEventTableSinglePassModule
    | GanFrequencyS0MultipleAnswerDetSelectorModule
    | GanFrequencyS0SeededMultipleAnswerDetSelectorModule
    | GanFrequencyS0ExplicitReasonCodeAdjudicatorModule
    | GanFrequencyS0SpecialClassTargetSelectorModule
    | GanFrequencyS0CandidateRankingTargetSelectorModule
    | GanFrequencyS0ReactTemporalToolsModule
):
    active_variants = {
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
        GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
        GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
        GAN_FREQUENCY_S0_EXPLICIT_REASON_CODE_ADJUDICATOR_VARIANT,
        GAN_FREQUENCY_S0_SPECIAL_CLASS_TARGET_SELECTOR_VARIANT,
        GAN_FREQUENCY_S0_CANDIDATE_RANKING_TARGET_SELECTOR_VARIANT,
    }
    if not include_archive and program_variant not in active_variants:
        raise ValueError(
            f"Gan S0 program variant {program_variant!r} is archive-only; "
            "pass include_archive=True for explicit provenance replay."
        )
    resolved_prompt_version = prompt_version or default_gan_frequency_s0_prompt_version(
        program_variant
    )
    if program_variant == GAN_FREQUENCY_S0_VARIANT:
        return GanFrequencyS0Module()
    if program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT:
        return GanFrequencyS0DirectModule(prompt_version=resolved_prompt_version)
    if program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT:
        return GanFrequencyS0VerifyRepairModule(prompt_version=resolved_prompt_version)
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT:
        return GanFrequencyS0TemporalCandidatesVerifyRepairModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT:
        resolved_context_policy = (
            context_policy
            or GAN_CONTEXT_POLICY_FULL_NOTE_PLUS_DETERMINISTIC_TEMPORAL_CANDIDATES
        )
        return GanFrequencyS0TemporalCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version,
            candidate_presentation=candidate_presentation,
            context_policy=resolved_context_policy,
        )
    if program_variant == GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT:
        return GanFrequencyS0LlmTemporalCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT:
        return GanFrequencyS0DateEventsCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT:
        return GanFrequencyS0LlmDateEventsCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT:
        return GanFrequencyS0HybridDateEventsCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_VARIANT:
        return GanFrequencyS0EntityTagsDateEventsSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT:
        return GanFrequencyS0HybridTemporalCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT:
        return GanFrequencyS0TemporalCandidatesAdjudicateDetGuardsModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT:
        return GanFrequencyS0TemporalCandidatesAdjudicateDetEvidenceModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT:
        return GanFrequencyS0TemporalCandidatesAdjudicateConfirmOnlyModule(
            prompt_version=resolved_prompt_version
        )
    if (
        program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_NO_GUARDS_VARIANT
    ):
        return GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairNoGuardsModule(
            prompt_version=resolved_prompt_version
        )
    if (
        program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT
    ):
        return GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairModule(
            prompt_version=resolved_prompt_version
        )
    if (
        program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT
    ):
        return GanFrequencyS0TemporalCandidatesAdjudicateConstrainedVerifierModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT:
        return GanFrequencyS0LlmTemporalCandidatesVerifyRepairModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT:
        return GanFrequencyS0TemporalEventTableVerifyRepairModule()
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT:
        return GanFrequencyS0TemporalEventTableSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT:
        return GanFrequencyS0MultipleAnswerDetSelectorModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT:
        return GanFrequencyS0SeededMultipleAnswerDetSelectorModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_EXPLICIT_REASON_CODE_ADJUDICATOR_VARIANT:
        return GanFrequencyS0ExplicitReasonCodeAdjudicatorModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_SPECIAL_CLASS_TARGET_SELECTOR_VARIANT:
        return GanFrequencyS0SpecialClassTargetSelectorModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_CANDIDATE_RANKING_TARGET_SELECTOR_VARIANT:
        return GanFrequencyS0CandidateRankingTargetSelectorModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT:
        return GanFrequencyS0ReactTemporalToolsModule()
    raise ValueError(f"Unsupported Gan S0 program variant: {program_variant!r}")
