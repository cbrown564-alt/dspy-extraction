"""Public Gan S0 candidate-inventory stage surface."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import asdict
from typing import Any

from clinical_extraction.gan.frequency import (
    label_to_monthly_frequency,
    pragmatic_category,
    purist_category,
)
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates,
    temporal_candidate_to_dict,
)
from clinical_extraction.schemas import GanRecord

GAN_S0_CANDIDATE_INVENTORY_SURFACE_VERSION = "gan_s0_candidate_inventory.v1"


def build_gan_s0_candidate_inventory_surface(
    *,
    record: GanRecord,
    flags: Any | None,
) -> dict[str, Any]:
    """Characterize deterministic Gan candidates before target selection."""

    candidates = build_temporal_frequency_candidates(record)
    candidate_labels = [candidate.canonical_label for candidate in candidates]
    invalid_candidate_labels = _invalid_candidate_labels(candidate_labels)
    gold_purist = purist_category(record.gold_label)
    gold_pragmatic = pragmatic_category(record.gold_label)
    candidate_purist = _category_set(candidate_labels, purist_category)
    candidate_pragmatic = _category_set(candidate_labels, pragmatic_category)
    exact = record.gold_label in candidate_labels

    return {
        "record_id": record.record_id,
        "gold_label": record.gold_label,
        "label_family": gan_s0_label_family(record.gold_label),
        "gold_purist_category": gold_purist,
        "gold_pragmatic_category": gold_pragmatic,
        "candidate_count": len(candidates),
        "candidate_labels": candidate_labels,
        "invalid_candidate_labels": invalid_candidate_labels,
        "invalid_candidate_count": len(invalid_candidate_labels),
        "gold_exact_in_candidates": exact,
        "gold_purist_in_candidates": gold_purist in candidate_purist,
        "gold_pragmatic_in_candidates": gold_pragmatic in candidate_pragmatic,
        "hard_strata": gan_s0_hard_strata_for_record(record, flags),
        "row_ok": record.row_ok,
        "hard_case": "hard_case" in record.flags,
        "reference_label": record.reference_label,
        "gold_evidence": record.gold_evidence,
        "candidate_records": [
            temporal_candidate_to_dict(candidate) for candidate in candidates
        ],
        "multi_event_flags": asdict(flags) if flags else None,
    }


def gan_s0_label_family(label: str) -> str:
    if label == "no seizure frequency reference":
        return "no_reference"
    if label == "unknown":
        return "unknown"
    if label.startswith("unknown,"):
        return "unknown_cluster"
    if label.startswith("seizure free for "):
        return "seizure_free"
    if " cluster per " in label:
        return "cluster"
    if "multiple" in label:
        return "vague_or_multiple_rate"
    return "quantified_rate"


def gan_s0_hard_strata_for_record(
    record: GanRecord,
    flags: Any | None,
) -> list[str]:
    strata: list[str] = []
    if flags is not None:
        if flags.multi_or_highest_analysis_signal:
            strata.append("multi_highest")
        if flags.seizure_free_conflict:
            strata.append("seizure_free_conflict")
        if flags.cluster_adjudication_required:
            strata.append("cluster")
        if flags.unknown_with_event_mentions:
            strata.append("unknown_with_events")
        if flags.label_reference_disagreement:
            strata.append("label_reference_disagreement")
        if flags.gold_evidence_multispan:
            strata.append("gold_evidence_multispan")
    if record.gold_label == "no seizure frequency reference":
        strata.append("no_reference")
    if "multiple" in record.gold_label or record.gold_label.startswith("unknown,"):
        strata.append("vague_frequency")
    return sorted(set(strata))


def _category_set(
    labels: Iterable[str],
    category_fn: Callable[[str], str],
) -> set[str]:
    categories: set[str] = set()
    for label in labels:
        try:
            categories.add(category_fn(label))
        except ValueError:
            continue
    return categories


def _invalid_candidate_labels(labels: Iterable[str]) -> list[str]:
    invalid: list[str] = []
    for label in labels:
        try:
            label_to_monthly_frequency(label)
        except ValueError:
            invalid.append(label)
    return invalid


__all__ = [
    "GAN_S0_CANDIDATE_INVENTORY_SURFACE_VERSION",
    "build_gan_s0_candidate_inventory_surface",
    "gan_s0_hard_strata_for_record",
    "gan_s0_label_family",
]
