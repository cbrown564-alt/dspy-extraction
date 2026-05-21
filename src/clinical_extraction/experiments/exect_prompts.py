"""Prompt metadata for ExECT S0-S4 experiment runs."""

from __future__ import annotations

from typing import Any

from clinical_extraction.programs.exect_s2 import (
    EXECT_S2_FIELD_FAMILIES,
    EXECT_S2_LABEL_POLICY_GUIDANCE,
    EXECT_S2_POLICY_EXAMPLES,
    EXECT_S2_PROMPT_VERSION,
    EXECT_S2_VARIANT,
    _EXECT_S2_PROGRAM_VARIANTS,
)
from clinical_extraction.programs.exect_s3 import (
    EXECT_S3_FIELD_FAMILIES,
    EXECT_S3_LABEL_POLICY_GUIDANCE,
    EXECT_S3_POLICY_EXAMPLES,
    EXECT_S3_PROMPT_VERSION,
    EXECT_S3_VARIANT,
    _EXECT_S3_PROGRAM_VARIANTS,
)
from clinical_extraction.programs.exect_s4 import (
    EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT,
    EXECT_S4_FIELD_FAMILIES,
    EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
    EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
    EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_PROMPT_VERSION,
    EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT,
    EXECT_S4_LABEL_POLICY_GUIDANCE,
    EXECT_S4_POLICY_EXAMPLES,
    EXECT_S4_PROMPT_VERSION,
    EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
    EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
    EXECT_S4_VARIANT,
)
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
    EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
    EXECT_S0_S1_FIELD_FAMILIES,
    EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT,
    EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_VARIANT,
    EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
    resolve_exect_s0_s1_extraction_prompt_version,
    resolve_exect_s0_s1_label_policy,
)

_EXECT_S4_PROGRAM_VARIANTS = frozenset(
    {
        EXECT_S4_VARIANT,
        EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
        EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
        EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT,
        EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
        EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
        EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT,
    }
)


def _json_prompt_value(value: Any) -> Any:
    """Normalize tuple-heavy program constants to JSON-serializable lists."""
    if isinstance(value, tuple):
        return [_json_prompt_value(item) for item in value]
    if isinstance(value, list):
        return [_json_prompt_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_prompt_value(item) for key, item in value.items()}
    return value


def exect_prompts_data(
    *,
    program_variant: str,
    prompt_version: str,
    structured_output_strategy: str,
) -> dict[str, Any]:
    if program_variant in _EXECT_S4_PROGRAM_VARIANTS:
        if program_variant == EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT:
            module_name = "ExectS4FrequencyPreVocabFieldFamilyModule"
        elif program_variant == EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT:
            module_name = "ExectS4FrequencyStructuredSlotsFieldFamilyModule"
        else:
            module_name = "ExectS4FieldFamilyModule"
        return {
            "signature": "ExectS4FieldFamilySignature",
            "module": module_name,
            "predictor": "dspy.ChainOfThought",
            "program_variant": program_variant,
            "prompt_version": (
                prompt_version
                or (
                    EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_PROMPT_VERSION
                    if program_variant == EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT
                    else EXECT_S4_PROMPT_VERSION
                )
            ),
            "field_families": _json_prompt_value(EXECT_S4_FIELD_FAMILIES),
            "label_policy_guidance": _json_prompt_value(EXECT_S4_LABEL_POLICY_GUIDANCE),
            "label_policy_examples": _json_prompt_value(EXECT_S4_POLICY_EXAMPLES),
            "structured_output_strategy": structured_output_strategy,
        }
    if program_variant in _EXECT_S3_PROGRAM_VARIANTS:
        return {
            "signature": "ExectS3FieldFamilySignature",
            "module": "ExectS3FieldFamilyModule",
            "predictor": "dspy.ChainOfThought",
            "program_variant": program_variant,
            "prompt_version": prompt_version or EXECT_S3_PROMPT_VERSION,
            "field_families": _json_prompt_value(EXECT_S3_FIELD_FAMILIES),
            "label_policy_guidance": _json_prompt_value(EXECT_S3_LABEL_POLICY_GUIDANCE),
            "label_policy_examples": _json_prompt_value(EXECT_S3_POLICY_EXAMPLES),
            "structured_output_strategy": structured_output_strategy,
        }
    if program_variant in _EXECT_S2_PROGRAM_VARIANTS:
        return {
            "signature": "ExectS2FieldFamilySignature",
            "module": "ExectS2FieldFamilyModule",
            "predictor": "dspy.ChainOfThought",
            "program_variant": program_variant,
            "prompt_version": prompt_version or EXECT_S2_PROMPT_VERSION,
            "field_families": _json_prompt_value(EXECT_S2_FIELD_FAMILIES),
            "label_policy_guidance": _json_prompt_value(EXECT_S2_LABEL_POLICY_GUIDANCE),
            "label_policy_examples": _json_prompt_value(EXECT_S2_POLICY_EXAMPLES),
            "structured_output_strategy": structured_output_strategy,
        }
    if program_variant == EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT:
        module_name = "ExectS0S1DiagnosisRecallProbeModule"
        predictor_name = "dspy.ChainOfThought + dspy.Predict"
    elif program_variant == EXECT_S0_S1_VERIFY_REPAIR_VARIANT:
        module_name = "ExectS0S1VerifyRepairModule"
        predictor_name = (
            "dspy.ChainOfThought (extract) + dspy.ChainOfThought (verify/repair)"
        )
    elif program_variant == EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT:
        module_name = "ExectS0S1DeterministicOnlyModule"
        predictor_name = "deterministic_substring_match"
    elif program_variant == EXECT_S0_S1_VARIANT:
        module_name = "ExectS0S1FieldFamilyModule"
        predictor_name = "dspy.ChainOfThought"
    elif program_variant == EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT:
        module_name = "ExectS0S1FieldFamilyPromptGraphParallelModule"
        predictor_name = (
            "dspy.ChainOfThought (diagnosis) + dspy.ChainOfThought (seizure) + "
            "dspy.ChainOfThought (medication) [full note, parallel]"
        )
    elif program_variant == EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT:
        module_name = "ExectS0S1FieldFamilyPromptGraphSequentialModule"
        predictor_name = (
            "dspy.ChainOfThought (diagnosis) -> dspy.ChainOfThought (seizure) -> "
            "dspy.ChainOfThought (medication) [prior-context chain]"
        )
    elif program_variant == EXECT_S0_S1_SECTION_AWARE_VARIANT:
        module_name = "ExectS0S1SectionAwareFieldFamilyModule"
        predictor_name = (
            "dspy.ChainOfThought (diagnosis) + dspy.ChainOfThought (seizure) + "
            "dspy.ChainOfThought (medication) [section-aware]"
        )
    else:
        module_name = "ExectS0S1SectionAwareFieldFamilyModule"
        predictor_name = (
            "dspy.ChainOfThought (diagnosis) + dspy.ChainOfThought (seizure) + "
            "dspy.ChainOfThought (medication)"
        )
    resolved_prompt_version = prompt_version or EXECT_S0_S1_PROMPT_VERSION
    extraction_prompt_version = resolve_exect_s0_s1_extraction_prompt_version(
        resolved_prompt_version
    )
    label_policy_guidance, label_policy_examples = resolve_exect_s0_s1_label_policy(
        resolved_prompt_version
    )
    return {
        "signature": (
            "ExectS0S1FieldFamilySignature + ExectS0S1DiagnosisRecallSignature"
            if program_variant == EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT
            else (
                "ExectS0S1FieldFamilySignature + ExectS0S1VerifierSignature"
                if program_variant == EXECT_S0_S1_VERIFY_REPAIR_VARIANT
                else (
                    "ExectS0S1FieldFamilySignature"
                    if program_variant == EXECT_S0_S1_VARIANT
                    else (
                        "ExectS0S1DiagnosisPolicySignature + "
                        "ExectS0S1SeizureTypePolicySignature + "
                        "ExectS0S1MedicationPolicySignature"
                        if program_variant
                        in {
                            EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT,
                            EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT,
                        }
                        else "ExectS0S1DiagnosisSignature + "
                        "ExectS0S1SeizureTypeSignature + "
                        "ExectS0S1MedicationSignature"
                    )
                )
            )
        ),
        "module": module_name,
        "predictor": predictor_name,
        "program_variant": program_variant,
        "prompt_version": resolved_prompt_version,
        "extraction_prompt_version": extraction_prompt_version,
        "field_families": _json_prompt_value(EXECT_S0_S1_FIELD_FAMILIES),
        "label_policy_guidance": _json_prompt_value(label_policy_guidance),
        "label_policy_examples": _json_prompt_value(label_policy_examples),
        "structured_output_strategy": structured_output_strategy,
    }
