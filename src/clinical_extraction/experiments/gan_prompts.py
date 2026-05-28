"""Prompt metadata for Gan S0 experiment runs."""

from __future__ import annotations

from typing import Any

from clinical_extraction.gan.s0.signatures import GAN_FREQUENCY_SYNTHESIS_GUIDANCE
from clinical_extraction.gan.s0.variant_routing import (
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_EXPLICIT_REASON_CODE_ADJUDICATOR_VARIANT,
    GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
    GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_SPECIAL_CLASS_TARGET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
)


def gan_prompts_data(
    *,
    program_variant: str,
    prompt_version: str,
    structured_output_strategy: str,
) -> dict[str, Any]:
    module_name = "GanFrequencyS0Module"
    predictor_name = "dspy.ChainOfThought"
    if program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT:
        module_name = "GanFrequencyS0DirectModule"
        predictor_name = "dspy.Predict"
    elif program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT:
        module_name = "GanFrequencyS0VerifyRepairModule"
        predictor_name = "dspy.Predict + dspy.Predict"
    elif program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT:
        module_name = "GanFrequencyS0TemporalCandidatesVerifyRepairModule"
        predictor_name = "dspy.Predict + deterministic temporal candidates + dspy.Predict"
    elif program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT:
        module_name = "GanFrequencyS0TemporalCandidatesSinglePassModule"
        predictor_name = "deterministic temporal candidates + dspy.Predict(adjudicate)"
    elif program_variant == GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT:
        module_name = "GanFrequencyS0LlmTemporalCandidatesSinglePassModule"
        predictor_name = "dspy.Predict(llm candidates) + dspy.Predict(adjudicate)"
    elif program_variant == GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT:
        module_name = "GanFrequencyS0HybridTemporalCandidatesSinglePassModule"
        predictor_name = (
            "deterministic + dspy.Predict(llm candidates) + dspy.Predict(adjudicate)"
        )
    elif program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT:
        module_name = "GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairModule"
        predictor_name = (
            "deterministic temporal candidates + dspy.Predict(adjudicate) + "
            "dspy.Predict(temporal verify-repair) + det guards"
        )
    elif program_variant == "gan_frequency_s0_temporal_candidates_adjudicate_det_guards":
        module_name = "GanFrequencyS0TemporalCandidatesAdjudicateDetGuardsModule"
        predictor_name = (
            "deterministic temporal candidates + dspy.Predict(adjudicate) + "
            "det plausibility guards"
        )
    elif program_variant == "gan_frequency_s0_temporal_candidates_adjudicate_det_evidence":
        module_name = "GanFrequencyS0TemporalCandidatesAdjudicateDetEvidenceModule"
        predictor_name = (
            "deterministic temporal candidates + dspy.Predict(adjudicate) + "
            "det evidence + det guards"
        )
    elif program_variant == "gan_frequency_s0_temporal_candidates_adjudicate_confirm_only":
        module_name = "GanFrequencyS0TemporalCandidatesAdjudicateConfirmOnlyModule"
        predictor_name = (
            "deterministic temporal candidates + dspy.Predict(adjudicate) + "
            "det evidence + det guards + confirm-only verifier"
        )
    elif program_variant == "gan_frequency_s0_temporal_candidates_adjudicate_verify_repair_no_guards":
        module_name = "GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairNoGuardsModule"
        predictor_name = (
            "deterministic temporal candidates + dspy.Predict(adjudicate) + "
            "det evidence + dspy.Predict(temporal verify-repair)"
        )
    elif program_variant == GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT:
        module_name = "GanFrequencyS0LlmTemporalCandidatesVerifyRepairModule"
        predictor_name = (
            "dspy.Predict(llm candidates) + dspy.Predict(adjudicate) + "
            "dspy.Predict(temporal verify-repair)"
        )
    elif program_variant == GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT:
        module_name = "GanFrequencyS0TemporalEventTableVerifyRepairModule"
        predictor_name = (
            "dspy.Predict + deterministic temporal candidates + "
            "dspy.Predict(event table) + dspy.Predict"
        )
    elif program_variant == GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT:
        module_name = "GanFrequencyS0MultipleAnswerDetSelectorModule"
        predictor_name = "dspy.Predict(answer options) + deterministic selector"
    elif program_variant == GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT:
        module_name = "GanFrequencyS0SeededMultipleAnswerDetSelectorModule"
        predictor_name = (
            "deterministic temporal candidates + dspy.Predict(answer options) + "
            "deterministic selector"
        )
    elif program_variant == GAN_FREQUENCY_S0_EXPLICIT_REASON_CODE_ADJUDICATOR_VARIANT:
        module_name = "GanFrequencyS0ExplicitReasonCodeAdjudicatorModule"
        predictor_name = (
            "deterministic temporal candidates + dspy.Predict(reason-code "
            "adjudication) + deterministic label construction"
        )
    elif program_variant == GAN_FREQUENCY_S0_SPECIAL_CLASS_TARGET_SELECTOR_VARIANT:
        module_name = "GanFrequencyS0SpecialClassTargetSelectorModule"
        predictor_name = (
            "D1 deterministic date/event payload + deterministic temporal "
            "candidates + dspy.Predict(special-class target selection) + "
            "deterministic label construction"
        )
    elif program_variant == GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT:
        module_name = "GanFrequencyS0ReactTemporalToolsModule"
        predictor_name = "dspy.ReAct + deterministic temporal tools + dspy.ChainOfThought"
    return {
        "signature": "GanFrequencyS0Signature",
        "module": module_name,
        "predictor": predictor_name,
        "program_variant": program_variant,
        "prompt_version": prompt_version,
        "synthesis_guidance": GAN_FREQUENCY_SYNTHESIS_GUIDANCE,
        "structured_output_strategy": structured_output_strategy,
    }
