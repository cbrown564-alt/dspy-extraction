"""Public Gan S0 target-selection and label-construction stage surface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from clinical_extraction.gan.frequency import label_to_monthly_frequency, normalize_label
from clinical_extraction.gan.s0.candidate_inventory import (
    gan_s0_hard_strata_for_record,
    gan_s0_label_family,
)
from clinical_extraction.gan.scoring import (
    GAN_CANONICAL_SCORER,
    GAN_PAPER_REPRODUCTION_SCORER,
    score_gan_frequency_prediction,
)
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates,
    temporal_candidate_to_dict,
)
from clinical_extraction.schemas import GanRecord

GAN_S0_TARGET_SELECTION_SURFACE_VERSION = "gan_s0_target_selection.v1"


@dataclass(frozen=True)
class ConstructedGanLabel:
    """Result of deterministic label construction from a selected candidate."""

    status: str
    raw_candidate_label: str
    constructed_label: str | None
    failure_reason: str | None = None


def build_gan_s0_target_selection_surface(
    *,
    record: GanRecord,
    flags: Any | None,
) -> dict[str, Any]:
    """Characterize target selection separately from label construction."""

    candidates = [
        temporal_candidate_to_dict(candidate)
        for candidate in build_temporal_frequency_candidates(record)
    ]
    constructed = [
        construct_gan_s0_label_from_candidate_record(candidate)
        for candidate in candidates
    ]
    base = {
        "record_id": record.record_id,
        "gold_label": record.gold_label,
        "label_family": gan_s0_label_family(record.gold_label),
        "hard_strata": gan_s0_hard_strata_for_record(record, flags),
        "row_ok": record.row_ok,
        "hard_case": "hard_case" in record.flags,
        "reference_label": record.reference_label,
        "candidate_count": len(candidates),
        "candidate_labels": [candidate["canonical_label"] for candidate in candidates],
        "candidate_records": candidates,
        "constructed_candidates": [
            {
                "status": item.status,
                "raw_candidate_label": item.raw_candidate_label,
                "constructed_label": item.constructed_label,
                "failure_reason": item.failure_reason,
            }
            for item in constructed
        ],
    }
    return {
        **base,
        "candidate_constrained_oracle": select_gan_s0_candidate_constrained_oracle(
            record=record,
            constructed_candidates=constructed,
        ),
        "reason_code_selector_family_oracle": (
            select_gan_s0_reason_code_family_oracle(
                record=record,
                constructed_candidates=constructed,
            )
        ),
    }


def construct_gan_s0_label_from_candidate_record(
    candidate_record: dict[str, Any],
) -> ConstructedGanLabel:
    """Normalize and validate the label emitted by a selected candidate.

    This is intentionally narrower than scorer repair: a candidate label must
    already satisfy the audited Gan label taxonomy after existing plural and
    whitespace normalization.
    """

    raw_label = str(candidate_record.get("canonical_label") or "").strip()
    normalized = normalize_label(raw_label)
    try:
        label_to_monthly_frequency(normalized)
    except ValueError as exc:
        reason = str(exc)
        if "Unsupported Gan frequency label" not in reason:
            reason = f"Unsupported Gan frequency label: {raw_label!r} ({reason})"
        return ConstructedGanLabel(
            status="invalid_candidate_label",
            raw_candidate_label=raw_label,
            constructed_label=None,
            failure_reason=reason,
        )
    return ConstructedGanLabel(
        status="constructed",
        raw_candidate_label=raw_label,
        constructed_label=normalized,
    )


def select_gan_s0_candidate_constrained_oracle(
    *,
    record: GanRecord,
    constructed_candidates: list[ConstructedGanLabel],
) -> dict[str, Any]:
    valid = [
        item
        for item in constructed_candidates
        if item.constructed_label is not None
    ]
    if not constructed_candidates:
        return _unsupported_arm("no_candidate")
    if not valid:
        return _unsupported_arm("invalid_selected_candidate")

    scored = [
        (
            _score_priority(record.gold_label, item.constructed_label or ""),
            item,
        )
        for item in valid
    ]
    _, selected = max(scored, key=lambda pair: pair[0])
    reason_code = _selection_reason(record.gold_label, selected.constructed_label or "")
    return _supported_arm(
        constructed_label=selected.constructed_label or "",
        raw_candidate_label=selected.raw_candidate_label,
        reason_code=reason_code,
        gold_label=record.gold_label,
    )


def select_gan_s0_reason_code_family_oracle(
    *,
    record: GanRecord,
    constructed_candidates: list[ConstructedGanLabel],
) -> dict[str, Any]:
    if not constructed_candidates:
        return _unsupported_arm("no_candidate")
    valid = [
        item
        for item in constructed_candidates
        if item.constructed_label is not None
    ]
    if not valid:
        return _unsupported_arm("invalid_selected_candidate")

    gold_family = gan_s0_label_family(record.gold_label)
    for item in valid:
        constructed_label = item.constructed_label or ""
        if gan_s0_label_family(constructed_label) == gold_family:
            return _supported_arm(
                constructed_label=constructed_label,
                raw_candidate_label=item.raw_candidate_label,
                reason_code=f"select_family_{gold_family}",
                gold_label=record.gold_label,
            )
    return _unsupported_arm("no_family_match")


def _score_priority(gold_label: str, predicted_label: str) -> tuple[int, int, int, int]:
    score = score_gan_frequency_prediction(
        gold_label=gold_label,
        predicted_label=predicted_label,
    )
    return (
        int(score.exact_normalized_match),
        int(score.monthly_frequency_match),
        int(score.purist_category_match),
        int(score.pragmatic_category_match),
    )


def _selection_reason(gold_label: str, predicted_label: str) -> str:
    score = score_gan_frequency_prediction(
        gold_label=gold_label,
        predicted_label=predicted_label,
    )
    if score.exact_normalized_match:
        return "select_exact_candidate"
    if score.monthly_frequency_match:
        return "select_monthly_equivalent_candidate"
    if score.purist_category_match:
        return "select_purist_equivalent_candidate"
    if score.pragmatic_category_match:
        return "select_pragmatic_equivalent_candidate"
    return "select_best_available_candidate"


def _supported_arm(
    *,
    constructed_label: str,
    raw_candidate_label: str,
    reason_code: str,
    gold_label: str,
) -> dict[str, Any]:
    return {
        "status": "supported",
        "reason_code": reason_code,
        "raw_candidate_label": raw_candidate_label,
        "constructed_label": constructed_label,
        "scores": {
            "canonical": _score_dict(
                gold_label=gold_label,
                predicted_label=constructed_label,
                scorer_mode=GAN_CANONICAL_SCORER,
            ),
            "paper_reproduction": _score_dict(
                gold_label=gold_label,
                predicted_label=constructed_label,
                scorer_mode=GAN_PAPER_REPRODUCTION_SCORER,
            ),
        },
    }


def _unsupported_arm(reason_code: str) -> dict[str, Any]:
    return {
        "status": "unsupported",
        "reason_code": reason_code,
        "raw_candidate_label": None,
        "constructed_label": None,
        "scores": {
            "canonical": _empty_score_dict(),
            "paper_reproduction": _empty_score_dict(),
        },
    }


def _score_dict(
    *,
    gold_label: str,
    predicted_label: str,
    scorer_mode: str,
) -> dict[str, Any]:
    score = score_gan_frequency_prediction(
        gold_label=gold_label,
        predicted_label=predicted_label,
        scorer_mode=scorer_mode,
    )
    return {
        "normalized_label_match": score.exact_normalized_match,
        "monthly_frequency_match": score.monthly_frequency_match,
        "purist_category_match": score.purist_category_match,
        "pragmatic_category_match": score.pragmatic_category_match,
        "gold_monthly_frequency": score.gold_monthly_frequency,
        "predicted_monthly_frequency": score.predicted_monthly_frequency,
        "gold_purist_category": score.gold_purist_category,
        "predicted_purist_category": score.predicted_purist_category,
        "gold_pragmatic_category": score.gold_pragmatic_category,
        "predicted_pragmatic_category": score.predicted_pragmatic_category,
    }


def _empty_score_dict() -> dict[str, Any]:
    return {
        "normalized_label_match": False,
        "monthly_frequency_match": False,
        "purist_category_match": False,
        "pragmatic_category_match": False,
        "gold_monthly_frequency": None,
        "predicted_monthly_frequency": None,
        "gold_purist_category": None,
        "predicted_purist_category": None,
        "gold_pragmatic_category": None,
        "predicted_pragmatic_category": None,
    }


__all__ = [
    "GAN_S0_TARGET_SELECTION_SURFACE_VERSION",
    "ConstructedGanLabel",
    "build_gan_s0_target_selection_surface",
    "construct_gan_s0_label_from_candidate_record",
    "select_gan_s0_candidate_constrained_oracle",
    "select_gan_s0_reason_code_family_oracle",
]
