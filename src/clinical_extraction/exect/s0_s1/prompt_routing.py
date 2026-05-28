"""Prompt-version, repair-policy, and candidate-routing helpers for ExECT S0/S1."""
from __future__ import annotations

import re

from clinical_extraction.exect.s0_s1.constants import *  # noqa: F401,F403

def resolve_exect_s0_s1_extraction_prompt_version(
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
) -> str:
    """Map experiment prompt versions to the single-pass extraction policy version."""
    if prompt_version in {
        EXECT_S0_S1_L0_PROMPT_VERSION,
        EXECT_S0_S1_L1_SCHEMA_PROMPT_VERSION,
        EXECT_S0_S1_D1_PROMPT_VERSION,
    }:
        return prompt_version
    if prompt_version == EXECT_S0_S1_VERIFY_REPAIR_PROMPT_VERSION:
        return EXECT_S0_S1_PROMPT_VERSION
    return prompt_version


def resolve_exect_s0_s1_label_policy(
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
) -> tuple[tuple[str, ...], tuple[dict[str, object], ...]]:
    """Return label-policy guidance and examples for the requested prompt version."""
    if prompt_version in {
        EXECT_S0_S1_L0_PROMPT_VERSION,
        EXECT_S0_S1_L1_SCHEMA_PROMPT_VERSION,
        EXECT_S0_S1_D1_PROMPT_VERSION,
    }:
        return (), ()
    if prompt_version == EXECT_S0_S1_V4_11_PROMPT_VERSION:
        return (
            (*EXECT_S0_S1_LABEL_POLICY_GUIDANCE, *EXECT_S0_S1_V4_11_LABEL_POLICY_ADDENDUM),
            (*EXECT_S0_S1_POLICY_EXAMPLES, *EXECT_S0_S1_V4_11_POLICY_EXAMPLES),
        )
    if prompt_version == EXECT_S0_S1_V4_12_PROMPT_VERSION:
        return (
            (
                *EXECT_S0_S1_LABEL_POLICY_GUIDANCE,
                *EXECT_S0_S1_V4_11_LABEL_POLICY_ADDENDUM,
                *EXECT_S0_S1_V4_12_LABEL_POLICY_ADDENDUM,
            ),
            (
                *EXECT_S0_S1_POLICY_EXAMPLES,
                *EXECT_S0_S1_V4_11_POLICY_EXAMPLES,
                *EXECT_S0_S1_V4_12_POLICY_EXAMPLES,
            ),
        )
    if prompt_version in {
        EXECT_S0_S1_PROMPT_VERSION,
        EXECT_S0_S1_V4_10_EVIDENCE_STRICT_PROMPT_VERSION,
        EXECT_S0_S1_V4_10_EVIDENCE_SOFT_PROMPT_VERSION,
        EXECT_S0_S1_VERIFY_REPAIR_PROMPT_VERSION,
    }:
        return EXECT_S0_S1_LABEL_POLICY_GUIDANCE, EXECT_S0_S1_POLICY_EXAMPLES
    raise ValueError(f"Unsupported ExECT S0/S1 prompt version: {prompt_version!r}")
def _match_longest_substring_labels(
    note_lower: str,
    labels: tuple[str, ...] | frozenset[str],
) -> list[str]:
    """Return note-anchored labels using longest-first word-boundary matching."""
    matched: list[str] = []
    for label in sorted(labels, key=len, reverse=True):
        if not label.strip():
            continue
        pattern = rf"\b{re.escape(label)}\b"
        if re.search(pattern, note_lower):
            matched.append(label)
    return list(dict.fromkeys(matched))


def extract_d1_field_family_surfaces(note_text: str) -> dict[str, list[str]]:
    """Feasibility-bound extraction without an LLM (ladder rung D1)."""
    note_lower = note_text.lower()
    return {
        "diagnosis": _match_longest_substring_labels(
            note_lower,
            ALLOWED_DIAGNOSIS_LABELS,
        ),
        "seizure_type": _match_longest_substring_labels(
            note_lower,
            _PRE_VOCAB_SEIZURE_TYPE_SURFACES,
        ),
        "annotated_medication": build_precomputed_medication_candidates(note_text),
    }


def _s1_single_pass_variants() -> frozenset[str]:
    return frozenset(
        {
            EXECT_S0_S1_VARIANT,
            EXECT_S0_S1_PRE_VOCAB_VARIANT,
            EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
            EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
            EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
            EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT,
            EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT,
        }
    )


def _repair_policy_applies_benchmark_bridges(repair_policy: str) -> bool:
    """Return whether audited S1 benchmark bridges run after single-pass extraction."""
    return repair_policy != REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES


def _bridge_stage_for_repair_policy(repair_policy: str) -> str:
    if not _repair_policy_applies_benchmark_bridges(repair_policy):
        return "none"
    if repair_policy == REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY:
        return "post"
    return "inline"

def build_precomputed_medication_candidates(note_text: str) -> list[str]:
    """Build note-anchored prescription medication candidates for narrow H2 probes."""
    note_lower = note_text.lower()
    return sorted(
        {
            medication
            for medication in _KNOWN_PRESCRIPTION_MEDICATIONS
            if re.search(rf"\b{re.escape(medication)}\b", note_lower)
        }
    )


def build_precomputed_family_candidates(note_text: str) -> dict[str, list[str]]:
    """Build note-aware audited candidate lists for H2 pre-vocabulary injection."""
    return {
        "diagnosis": sorted(ALLOWED_DIAGNOSIS_LABELS),
        "seizure_type": sorted(_PRE_VOCAB_SEIZURE_TYPE_SURFACES),
        "annotated_medication": build_precomputed_medication_candidates(note_text),
    }


def format_note_with_precomputed_medication_candidates(note_text: str) -> str:
    """Inject medication-only audited candidates before the clinical note."""
    medication_candidates = build_precomputed_medication_candidates(note_text)
    lines = [
        "Precomputed benchmark-facing candidates (soft hints; emit only when note-supported):",
        f"annotated_medication: {', '.join(medication_candidates)}",
        "",
        "---",
        "",
        note_text,
    ]
    return "\n".join(lines)


def build_precomputed_seizure_type_candidates() -> list[str]:
    """Build static audited seizure-type surfaces for narrow H2 pre-vocab probes."""
    return sorted(_PRE_VOCAB_SEIZURE_TYPE_SURFACES)


def format_note_with_precomputed_seizure_type_candidates(note_text: str) -> str:
    """Inject seizure-type-only audited candidates before the clinical note."""
    seizure_candidates = build_precomputed_seizure_type_candidates()
    lines = [
        "Precomputed benchmark-facing candidates (soft hints; emit only when note-supported):",
        f"seizure_type: {', '.join(seizure_candidates)}",
        "",
        "---",
        "",
        note_text,
    ]
    return "\n".join(lines)


def format_note_with_precomputed_family_candidates(note_text: str) -> str:
    """Inject audited candidate vocabularies before the clinical note."""
    candidates = build_precomputed_family_candidates(note_text)
    lines = [
        "Precomputed benchmark-facing candidates (soft hints; emit only when note-supported):",
        f"diagnosis: {', '.join(candidates['diagnosis'])}",
        f"seizure_type: {', '.join(candidates['seizure_type'])}",
        f"annotated_medication: {', '.join(candidates['annotated_medication'])}",
        "",
        "---",
        "",
        note_text,
    ]
    return "\n".join(lines)
def stage_graph_id_for_program_variant(program_variant: str) -> str | None:
    return EXECT_S0_S1_STAGE_GRAPH_BY_VARIANT.get(program_variant)
