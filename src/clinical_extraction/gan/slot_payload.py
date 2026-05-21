"""Structured slot payloads for Gan temporal-frequency candidate presentation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from clinical_extraction.gan.temporal_candidates import (
    GanTemporalFrequencyCandidate,
)

WindowSource = str
DenominatorStatus = str
TargetPriorityCue = str


@dataclass(frozen=True)
class GanTemporalFrequencySlotPayload:
    """Structured candidate slots exposed to the adjudicator."""

    candidate_label: str
    event_count_or_range: str
    event_type: str | None
    target_priority_cue: TargetPriorityCue
    window_count: str
    window_unit: str
    window_source: WindowSource
    denominator_status: DenominatorStatus
    cluster_count_or_range: str | None
    per_cluster_count_or_range: str | None
    cluster_spacing_source: str | None
    unknown_policy_cue: str | None
    supporting_quote: str
    derivation: str


SEIZURE_TYPE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\babsences?\b", re.IGNORECASE), "absence"),
    (re.compile(r"\btonic[- ]?clonic\b", re.IGNORECASE), "tonic-clonic"),
    (re.compile(r"\bmyoclonic\b", re.IGNORECASE), "myoclonic"),
    (re.compile(r"\bfocal\b", re.IGNORECASE), "focal"),
    (re.compile(r"\bdrop attacks?\b", re.IGNORECASE), "drop attack"),
    (re.compile(r"\bclusters?\b", re.IGNORECASE), "cluster"),
    (re.compile(r"\btonic seizures?\b", re.IGNORECASE), "tonic"),
    (re.compile(r"\bconvulsive\b", re.IGNORECASE), "convulsive"),
)


CLUSTER_LABEL_PATTERN = re.compile(
    r"^(?P<cluster_count>[\d to]+)\s+cluster per "
    r"(?:(?P<window_count>[\d to]+)\s+(?P<window_unit>month|week|day|year)"
    r"|(?P<implicit_window_unit>week|day|month|year))"
    r"(?:,\s*(?P<per_cluster>.+))?$",
    flags=re.IGNORECASE,
)


def enrich_candidate_to_slot_payload(
    candidate: GanTemporalFrequencyCandidate,
) -> GanTemporalFrequencySlotPayload:
    """Derive structured slot metadata from an existing temporal candidate."""

    window_source = _window_source_from_derivation(candidate.derivation)
    cluster_count, per_cluster, cluster_spacing = _cluster_slots_from_label(
        candidate.canonical_label
    )
    denominator_status = _denominator_status(
        candidate=candidate,
        window_source=window_source,
        cluster_count=cluster_count,
        per_cluster=per_cluster,
    )
    unknown_policy_cue = _unknown_policy_cue(
        candidate=candidate,
        denominator_status=denominator_status,
        cluster_spacing=cluster_spacing,
        per_cluster=per_cluster,
    )
    return GanTemporalFrequencySlotPayload(
        candidate_label=candidate.canonical_label,
        event_count_or_range=candidate.event_count,
        event_type=_event_type_from_evidence(candidate.evidence_text),
        target_priority_cue=_target_priority_cue(candidate),
        window_count=candidate.window_count,
        window_unit=candidate.window_unit,
        window_source=window_source,
        denominator_status=denominator_status,
        cluster_count_or_range=cluster_count,
        per_cluster_count_or_range=per_cluster,
        cluster_spacing_source=cluster_spacing,
        unknown_policy_cue=unknown_policy_cue,
        supporting_quote=candidate.evidence_text,
        derivation=candidate.derivation,
    )


def build_slot_payloads_from_candidates(
    candidates: list[GanTemporalFrequencyCandidate],
) -> list[GanTemporalFrequencySlotPayload]:
    return [enrich_candidate_to_slot_payload(candidate) for candidate in candidates]


def slot_payload_to_dict(payload: GanTemporalFrequencySlotPayload) -> dict[str, str | None]:
    return {
        "candidate_label": payload.candidate_label,
        "event_count_or_range": payload.event_count_or_range,
        "event_type": payload.event_type,
        "target_priority_cue": payload.target_priority_cue,
        "window_count": payload.window_count,
        "window_unit": payload.window_unit,
        "window_source": payload.window_source,
        "denominator_status": payload.denominator_status,
        "cluster_count_or_range": payload.cluster_count_or_range,
        "per_cluster_count_or_range": payload.per_cluster_count_or_range,
        "cluster_spacing_source": payload.cluster_spacing_source,
        "unknown_policy_cue": payload.unknown_policy_cue,
        "supporting_quote": payload.supporting_quote,
        "derivation": payload.derivation,
    }


def format_slot_payload_candidates_for_prompt(
    candidates: list[GanTemporalFrequencyCandidate],
    *,
    source: str = "deterministic",
) -> str:
    if not candidates:
        prefix = "deterministic"
        if source == "llm":
            prefix = "LLM-extracted"
        elif source == "hybrid":
            prefix = "Hybrid deterministic+LLM"
        return (
            f"No {prefix.lower()} temporal frequency slot payloads were extracted "
            "from this note."
        )

    if source == "llm":
        header = (
            "LLM-extracted temporal frequency slot payloads "
            "(diagnostic hints only — read slots before choosing a label):"
        )
    elif source == "hybrid":
        header = (
            "Hybrid deterministic+LLM temporal frequency slot payloads "
            "(diagnostic hints only — read slots before choosing a label):"
        )
    else:
        header = (
            "Deterministic temporal frequency slot payloads "
            "(diagnostic hints only — read slots before choosing a label):"
        )

    payloads = build_slot_payloads_from_candidates(candidates)
    rows = [
        "| # | candidate_label | event_count_or_range | event_type | "
        "target_priority_cue | window | window_source | denominator_status | "
        "cluster_count_or_range | per_cluster_count_or_range | "
        "cluster_spacing_source | unknown_policy_cue | supporting_quote |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for index, payload in enumerate(payloads, start=1):
        window = f"{payload.window_count} {payload.window_unit}".strip()
        rows.append(
            "| "
            f"{index} | {payload.candidate_label!r} | {payload.event_count_or_range} | "
            f"{payload.event_type or ''} | {payload.target_priority_cue} | {window} | "
            f"{payload.window_source} | {payload.denominator_status} | "
            f"{payload.cluster_count_or_range or ''} | "
            f"{payload.per_cluster_count_or_range or ''} | "
            f"{payload.cluster_spacing_source or ''} | "
            f"{payload.unknown_policy_cue or ''} | {payload.supporting_quote!r} |"
        )

    json_block = json.dumps(
        {"slot_payloads": [slot_payload_to_dict(payload) for payload in payloads]},
        indent=2,
    )
    return "\n".join([header, *rows, "", "Slot payload JSON:", json_block])


def _event_type_from_evidence(evidence_text: str) -> str | None:
    for pattern, label in SEIZURE_TYPE_PATTERNS:
        if pattern.search(evidence_text):
            return label
    return None


def _window_source_from_derivation(derivation: str) -> WindowSource:
    normalized = derivation.lower()
    if "two explicitly dated events" in normalized:
        return "calendar_aggregation"
    if "year-to-date" in normalized or "calendar months elapsed" in normalized:
        return "calendar_aggregation"
    if "prior month/year" in normalized or "nearly one-year" in normalized:
        return "elapsed_since_date"
    if "last recorded event" in normalized:
        return "explicit_text"
    if "calendar quarter" in normalized:
        return "explicit_text"
    if "weekly cluster cadence" in normalized:
        return "explicit_text"
    if "qualitative several-times-per-week" in normalized:
        return "explicit_text"
    return "explicit_text"


def _cluster_slots_from_label(
    canonical_label: str,
) -> tuple[str | None, str | None, str | None]:
    if "cluster" not in canonical_label.lower():
        return None, None, None

    match = CLUSTER_LABEL_PATTERN.match(canonical_label.strip())
    if match is None:
        return None, None, "vague_recurrence"

    per_cluster = match.group("per_cluster")
    cluster_spacing = "explicit_spacing"
    if per_cluster and "multiple per cluster" in per_cluster.lower():
        cluster_spacing = "vague_recurrence"
        per_cluster = "multiple"
    elif per_cluster is None and "multiple per cluster" in canonical_label.lower():
        cluster_spacing = "vague_recurrence"
        per_cluster = "multiple"
    elif per_cluster and per_cluster.lower().endswith(" per cluster"):
        per_cluster = per_cluster[: -len(" per cluster")].strip()
    return match.group("cluster_count"), per_cluster, cluster_spacing


def _denominator_status(
    *,
    candidate: GanTemporalFrequencyCandidate,
    window_source: WindowSource,
    cluster_count: str | None,
    per_cluster: str | None,
) -> DenominatorStatus:
    label = candidate.canonical_label.lower()
    if label == "unknown" or label.startswith("no seizure frequency reference"):
        return "missing_or_ambiguous"
    if cluster_count and per_cluster in {None, "multiple"}:
        return "missing_or_ambiguous"
    if window_source == "calendar_aggregation":
        return "derivable"
    if window_source == "elapsed_since_date":
        return "derivable"
    if candidate.window_count and candidate.window_unit:
        return "explicit"
    return "missing_or_ambiguous"


def _unknown_policy_cue(
    *,
    candidate: GanTemporalFrequencyCandidate,
    denominator_status: DenominatorStatus,
    cluster_spacing: str | None,
    per_cluster: str | None,
) -> str | None:
    if denominator_status == "missing_or_ambiguous":
        return "prefer_unknown_when_denominator_not_benchmark_derivable"
    if cluster_spacing == "vague_recurrence" and per_cluster == "multiple":
        return "cluster_spacing_vague_but_label_may_still_be_benchmark_valid"
    if "unknown" in candidate.canonical_label.lower():
        return "explicit_unknown_label"
    return None


def _target_priority_cue(candidate: GanTemporalFrequencyCandidate) -> TargetPriorityCue:
    evidence = candidate.evidence_text.lower()
    if "last " in evidence and "seizure" in evidence:
        return "may_be_lower_frequency_concurrent_type"
    if "tonic-clonic" in evidence or "convulsive" in evidence:
        return "may_be_lower_frequency_concurrent_type"
    if "daily" in evidence or "absence" in evidence:
        return "may_be_higher_frequency_concurrent_type"
    return "benchmark_highest_current_frequency_unknown"
