"""DSPy signatures for the ExECT S5 operational stack."""
from __future__ import annotations

import dspy

from clinical_extraction.exect.s0_s1.signatures import (
    ExectS0S1DiagnosisSignature,
    ExectS0S1MedicationSignature,
    ExectS0S1SeizureTypeSignature,
)
from clinical_extraction.programs.exect_s2 import EXECT_S2_POLICY_EXAMPLES


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


def _resolve_s4_policy_examples(
    prompt_version: str | None,
) -> tuple[str, tuple[dict[str, object], ...]]:
    from clinical_extraction.programs.exect_s4 import (
        EXECT_S4_POLICY_EXAMPLES,
        EXECT_S4_PROMPT_VERSION,
        EXECT_S4_PROMPT_VERSION_V1_3,
        EXECT_S4_V1_3_POLICY_EXAMPLES,
    )

    resolved_prompt_version = prompt_version or EXECT_S4_PROMPT_VERSION
    policy_examples = (*EXECT_S4_POLICY_EXAMPLES, *EXECT_S2_POLICY_EXAMPLES)
    if resolved_prompt_version == EXECT_S4_PROMPT_VERSION_V1_3:
        policy_examples = (*policy_examples, *EXECT_S4_V1_3_POLICY_EXAMPLES)
    return resolved_prompt_version, policy_examples


def build_exect_s5_core_family_specific_signature(
    field_name: str,
    prompt_version: str | None = None,
) -> type[dspy.Signature]:
    """Build a per-family S5-core signature enriched with S4 label-policy examples."""
    if field_name not in _S5_CORE_FAMILY_POLICY_OUTPUT_KEYS:
        raise ValueError(f"Unsupported ExECT S5 core field family: {field_name!r}")

    _, policy_examples = _resolve_s4_policy_examples(prompt_version)
    base_by_field = {
        "diagnosis": ExectS0S1DiagnosisSignature,
        "seizure_type": ExectS0S1SeizureTypeSignature,
        "annotated_medication": ExectS0S1MedicationSignature,
        "investigation": ExectS5CoreInvestigationSignature,
        "seizure_frequency": ExectS5CoreSeizureFrequencySignature,
    }
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
