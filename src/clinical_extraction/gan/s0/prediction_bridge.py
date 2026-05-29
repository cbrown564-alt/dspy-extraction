"""Gan S0 prediction bridge and artifact assembly."""
from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import Any

import dspy

from clinical_extraction.gan.frequency import (
    canonicalize_leading_inequality_label,
    gan_label_policy_failure_class,
)
from clinical_extraction.gan.s0.variant_routing import (
    GAN_FREQUENCY_S0_FIELD,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_SCORER,
    GAN_FREQUENCY_S0_VARIANT,
)
from clinical_extraction.runs import RunMetadata
from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExtractedValue,
    GanRecord,
    PredictionSet,
)

_ABSTAIN_STRINGS = frozenset({"none", "null", ""})
_FINAL_LABEL_REJECT_FAILURE_CLASSES = frozenset(
    {
        "unknown_quantified_hybrid",
        "multiple_frequency_labels",
        "prose_appended_label",
        "malformed_cluster_unknown_slot",
    }
)
_NO_REFERENCE_NOTE_RE = re.compile(
    r"\b("
    r"administrative|admin|appointment|appointments|cancellation|cancelled|"
    r"triage request|urgent referral|supporting information|exam access|"
    r"access arrangements|support housing|housing needs|temporary access|"
    r"site access|building works|childcare setting|caregiver support|"
    r"non-clinical|reasonable adjustment|reasonable adjustments"
    r")\b",
    re.IGNORECASE,
)
_FREQUENCY_CONTEXT_RE = re.compile(
    r"\b("
    r"\d+\s+(?:seizures?|fits?|episodes?|events?)|"
    r"(?:one|two|three|four|five|six|seven|eight|nine|ten|multiple|several|few|many)\s+"
    r"(?:seizures?|fits?|episodes?|events?)|"
    r"per\s+(?:day|week|month|year|night|hour|fortnight|quarter)|"
    r"daily|weekly|monthly|yearly|nightly|"
    r"seizure free|seizure-free|last seizure|clusters?"
    r")\b",
    re.IGNORECASE,
)
_SHORT_SEIZURE_FREE_RE = re.compile(
    r"^seizure free for (?P<count>\d+(?:\.\d+)?) (?P<unit>week|month|year)s?$"
)
_EVERY_DAY_RANGE_RE = re.compile(r"^1 per day to 1 per (?P<end>\d+) day$")
_DAILY_COUNT_RE = re.compile(r"^(?P<count>\d+(?:\.\d+)?) per day$")
_QUOTED_SPECIAL_LABEL_RE = re.compile(
    r"^[\"'](?P<label>unknown|no seizure frequency reference)[\"']$",
    re.IGNORECASE,
)
_MATCHING_RATE_RANGE_RE = re.compile(
    r"^(?P<count>\d+(?:\.\d+)?) per (?P<first>\d+(?:\.\d+)?) "
    r"(?P<first_unit>day|week|month|year) to (?P=count) per "
    r"(?P<second>\d+(?:\.\d+)?) (?P<second_unit>day|week|month|year)$"
)
_SEIZURE_FREE_RE = re.compile(
    r"^seizure free for (?P<count>\d+(?:\.\d+)?) (?P<unit>month|year)$"
)
_YTD_NOTE_RE = re.compile(r"\b(year to date|ytd|since january)\b", re.IGNORECASE)
_FORBIDDEN_UNIT_RE = re.compile(
    r"\b(quarter|quarters|fortnight|fortnights|night|nights|hour|hours)\b",
    re.IGNORECASE,
)
_ADJECTIVE_RATE_LABELS = {
    "daily": "1 per day",
    "nightly": "1 per day",
    "weekly": "1 per week",
    "monthly": "1 per month",
    "biweekly": "1 per 2 week",
    "fortnightly": "1 per 2 week",
}
_EVIDENCE_PROMPT_FOOTER_MARKERS = (
    "Respond with the corresponding output fields",
    "[[ ## ",
    "In adhering to this structure",
)
_PER_HOUR_RATE_RE = re.compile(r"^(?P<count>\d+(?:\.\d+)?) per hour$")
_UNKNOWN_PER_HOUR_RATE_RE = re.compile(
    r"^unknown, (?P<count>\d+(?:\.\d+)?) per hours?$"
)
_MALFORMED_CLUSTER_SUFFIX_RE = re.compile(
    r"^(?P<rate>.+?) per (?P<unit>day|week|month|year), "
    r"(?P<per_cluster>.+?) per cluster$"
)
_EVIDENCE_ELLIPSIS_RE = re.compile(r"\.\.\.|…")


def predict_gan_records(
    module: Callable[..., Any],
    records: list[GanRecord],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = "gan_frequency_s0_v1",
    program_variant: str = GAN_FREQUENCY_S0_VARIANT,
    repair_policy: str = "none",
    progress_callback: Callable[[int, int, str], None] | None = None,
    scorer_mode: str | None = None,
) -> PredictionSet:
    """Run ``module`` on each Gan record and return a ``PredictionSet`` artifact."""
    predictions = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        predictions.append(
            _predict_record(
                module,
                record,
                program_variant=program_variant,
                repair_policy=repair_policy,
            )
        )
        if progress_callback is not None:
            progress_callback(index, total, record.record_id)
    return PredictionSet(
        dataset="gan_2026",
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        predictions=predictions,
        metadata={
            "program_variant": program_variant,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "scorer_mode": scorer_mode or GAN_FREQUENCY_S0_SCORER,
            "repair_policy": repair_policy,
        },
    )


def _is_unknown_or_abstain_label(label: str | None) -> bool:
    if label is None:
        return True
    return label.strip().lower() in _ABSTAIN_STRINGS | {"unknown"}


def looks_like_gan_s0_no_reference_note(note_text: str) -> bool:
    """Detect administrative/no-frequency Gan notes without consulting gold labels."""

    return bool(_NO_REFERENCE_NOTE_RE.search(note_text)) and not bool(
        _FREQUENCY_CONTEXT_RE.search(note_text)
    )


def _looks_like_no_reference_note(note_text: str) -> bool:
    return looks_like_gan_s0_no_reference_note(note_text)


def _seizure_free_window_in_months(label: str) -> float | None:
    normalized = _apply_canonical_surface_repairs(label.strip())
    match = _SHORT_SEIZURE_FREE_RE.match(normalized)
    if not match:
        return None
    count = float(match.group("count"))
    unit = match.group("unit").rstrip("s")
    if unit == "week":
        return count / 4.345
    if unit == "month":
        return count
    if unit == "year":
        return count * 12
    return None


def _apply_evidence_span_check_guard(
    note_text: str,
    verified: dspy.Prediction,
    *,
    initial_label: str | None,
    initial_evidence: str | None,
) -> dspy.Prediction:
    """Deterministic post-verifier guard for span-checked evidence policy arms."""
    final_label = verified.final_label
    if final_label in (None, "no seizure frequency reference"):
        return verified
    feedback = _evidence_policy_feedback(
        gold_label=final_label,
        predicted_evidence=verified.final_evidence,
        note_text=note_text,
    )
    if feedback is None:
        return verified
    if (
        isinstance(initial_evidence, str)
        and initial_evidence.strip() in note_text
        and initial_label not in (None, "no seizure frequency reference")
    ):
        return dspy.Prediction(
            final_label=initial_label,
            final_evidence=initial_evidence,
            decision="confirm",
            reason=(
                "Evidence span-check guard preserved initial prediction: "
                f"{feedback}"
            ),
        )
    return dspy.Prediction(
        final_label=None,
        final_evidence=None,
        decision="abstain",
        reason=f"Evidence span-check guard abstained: {feedback}",
    )


def apply_gan_s0_evidence_span_check_guard(
    note_text: str,
    verified: dspy.Prediction,
    *,
    initial_label: str | None,
    initial_evidence: str | None,
) -> dspy.Prediction:
    """Public Gan S0 evidence span-check stage surface."""

    return _apply_evidence_span_check_guard(
        note_text,
        verified,
        initial_label=initial_label,
        initial_evidence=initial_evidence,
    )


def _apply_constrained_verifier_guard(
    *,
    note_text: str,
    verified: dspy.Prediction,
    candidates: list[Any],
    initial_label: str | None,
    initial_evidence: str | None,
) -> dspy.Prediction:
    """Constrain verifier labels to candidates, initial label, unknown, or no-reference."""
    from clinical_extraction.gan.frequency import normalize_label
    import difflib

    final_label = verified.final_label
    decision = verified.decision or "confirm"
    reason = verified.reason or "Constrained verifier guard applied."

    unique_targets = []
    seen = set()
    possible_sources = []
    if initial_label:
        possible_sources.append(initial_label)
    for candidate in candidates:
        possible_sources.append(candidate.canonical_label)
    possible_sources.extend(["unknown", "no seizure frequency reference"])

    for label in possible_sources:
        if label and label not in seen:
            unique_targets.append(label)
            seen.add(label)

    fallback_label = initial_label if initial_label else "unknown"

    chosen_label = None
    if final_label:
        normalized_final = normalize_label(final_label)
        for target in unique_targets:
            if normalize_label(target) == normalized_final:
                chosen_label = target
                break

        if chosen_label is None:
            matches = difflib.get_close_matches(
                final_label, unique_targets, n=1, cutoff=0.5
            )
            if matches:
                chosen_label = matches[0]
                decision = "repair"
                reason = (
                    f"Out-of-bounds verifier label {final_label!r} reverted to "
                    f"closest match {chosen_label!r}."
                )
            else:
                chosen_label = fallback_label
                decision = "repair"
                reason = (
                    f"Out-of-bounds verifier label {final_label!r} fallback to "
                    f"{chosen_label!r}."
                )
    else:
        chosen_label = fallback_label
        decision = "repair"
        reason = f"Empty verifier label fallback to {chosen_label!r}."

    chosen_evidence = None
    candidate_match = None
    for candidate in candidates:
        if normalize_label(candidate.canonical_label) == normalize_label(chosen_label):
            candidate_match = candidate
            break

    if candidate_match is not None:
        chosen_evidence = candidate_match.evidence_text
    elif initial_label and normalize_label(chosen_label) == normalize_label(initial_label):
        chosen_evidence = initial_evidence
    elif (
        normalize_label(chosen_label) == normalize_label("unknown")
        and initial_label
        and normalize_label(initial_label) == normalize_label("unknown")
    ):
        chosen_evidence = initial_evidence
    else:
        chosen_evidence = None

    return dspy.Prediction(
        final_label=chosen_label,
        final_evidence=chosen_evidence,
        decision=decision,
        reason=reason,
    )


def apply_gan_s0_constrained_verifier_guard(
    *,
    note_text: str,
    verified: dspy.Prediction,
    candidates: list[Any],
    initial_label: str | None,
    initial_evidence: str | None,
) -> dspy.Prediction:
    """Public Gan S0 constrained-verifier guard stage surface."""

    return _apply_constrained_verifier_guard(
        note_text=note_text,
        verified=verified,
        candidates=candidates,
        initial_label=initial_label,
        initial_evidence=initial_evidence,
    )


def _apply_temporal_verifier_guards(
    *,
    initial_label: str | None,
    initial_evidence: str | None,
    verified: dspy.Prediction,
    candidates: list[Any],
    event_table: Any | None = None,
) -> dspy.Prediction:
    """Deterministic confirm-first and candidate-gated repair for temporal verify-repair."""
    from clinical_extraction.gan.frequency import normalize_label

    final_label = verified.final_label
    decision = verified.decision

    if not _is_unknown_or_abstain_label(initial_label):
        if decision == "repair" or (
            decision == "confirm"
            and final_label is not None
            and initial_label is not None
            and normalize_label(final_label) != normalize_label(initial_label)
        ):
            return dspy.Prediction(
                final_label=initial_label,
                final_evidence=initial_evidence,
                decision="confirm",
                reason=(
                    f"Confirm-first guard preserved initial label {initial_label!r} "
                    f"instead of verifier {decision} to {final_label!r}."
                ),
            )
        return verified

    candidate_labels = [candidate.canonical_label for candidate in candidates]
    candidate_norms = {normalize_label(label) for label in candidate_labels}

    if decision == "repair" and final_label and candidate_labels:
        if normalize_label(final_label) not in candidate_norms:
            best = candidates[0]
            return dspy.Prediction(
                final_label=best.canonical_label,
                final_evidence=best.evidence_text,
                decision="repair",
                reason=(
                    f"Candidate-gated repair replaced verifier label {final_label!r} "
                    f"with listed candidate {best.canonical_label!r}."
                ),
            )

    if decision == "repair" and final_label:
        months = _seizure_free_window_in_months(final_label)
        if months is not None and months < 6:
            return dspy.Prediction(
                final_label="unknown",
                final_evidence=initial_evidence or verified.final_evidence,
                decision="confirm",
                reason=(
                    f"Short seizure-free guard kept unknown instead of {final_label!r}."
                ),
            )

    rescued = _apply_event_table_candidate_rescue(
        initial_label=initial_label,
        verified=verified,
        candidates=candidates,
        event_table=event_table,
    )
    if rescued is not None:
        return rescued

    return verified


def _apply_event_table_candidate_rescue(
    *,
    initial_label: str | None,
    verified: dspy.Prediction,
    candidates: list[Any],
    event_table: Any | None,
) -> dspy.Prediction | None:
    """Repair confirmed-unknown when B2 event table shows no qualifying seizure-free gap."""
    if event_table is None or not _is_unknown_or_abstain_label(initial_label):
        return None
    if verified.decision != "confirm" or not _is_unknown_or_abstain_label(
        verified.final_label
    ):
        return None
    if len(candidates) != 1:
        return None
    if any(
        interval.qualifies_for_seizure_free_label
        for interval in event_table.seizure_free_intervals
    ):
        return None

    candidate = candidates[0]
    return dspy.Prediction(
        final_label=candidate.canonical_label,
        final_evidence=candidate.evidence_text,
        decision="repair",
        reason=(
            "Event-table candidate rescue repaired from confirmed unknown "
            f"to sole listed candidate {candidate.canonical_label!r} "
            "(no qualifying seizure-free interval in event table)."
        ),
    )


def _predict_record(
    module: Callable[..., Any],
    record: GanRecord,
    *,
    program_variant: str,
    repair_policy: str = "none",
) -> DocumentPrediction:
    pred = module(note_text=record.note_text)
    label: str | None = pred.seizure_frequency_number
    evidence_text: str | None = pred.evidence_text

    if isinstance(label, str) and label.strip().lower() in _ABSTAIN_STRINGS:
        label = None
    if isinstance(evidence_text, str) and evidence_text.strip().lower() in _ABSTAIN_STRINGS:
        evidence_text = None

    rejected_raw_label: str | None = None
    rejected_failure_class: str | None = None
    final_guard_flags: list[str] = []
    if label is None and _looks_like_no_reference_note(record.note_text):
        label = "no seizure frequency reference"
        evidence_text = None
        final_guard_flags.append("abstention_repaired:no_reference_policy")

    normalized_label = _normalize_predicted_label(label)
    quality_flags = ["abstained"] if label is None else []
    if label != normalized_label:
        quality_flags.append("normalized_label_repaired")
    quality_flags.extend(final_guard_flags)

    failure_class = (
        gan_label_policy_failure_class(normalized_label)
        if normalized_label is not None
        else None
    )
    if failure_class == "inequality_operator" and normalized_label is not None:
        repaired_label = canonicalize_leading_inequality_label(normalized_label)
        if repaired_label is not None:
            normalized_label = repaired_label
            failure_class = None
            if "normalized_label_repaired" not in quality_flags:
                quality_flags.append("normalized_label_repaired")

    if failure_class in _FINAL_LABEL_REJECT_FAILURE_CLASSES:
        if repair_policy == "artifact_bridge_surface_normalization_only":
            recovered_label = None
            if failure_class == "unknown_quantified_hybrid":
                recovered_label = "unknown"
            elif failure_class in ("multiple_frequency_labels", "prose_appended_label"):
                if normalized_label is not None and "," in normalized_label:
                    parts = [part.strip() for part in normalized_label.split(",")]
                    first_part = parts[0]
                    if gan_label_policy_failure_class(first_part) is None:
                        recovered_label = first_part
                if recovered_label is None:
                    recovered_label = "unknown"
            elif failure_class == "malformed_cluster_unknown_slot":
                recovered_label = "unknown"

            if recovered_label is not None:
                rejected_raw_label = label
                rejected_failure_class = failure_class
                normalized_label = recovered_label
                label = recovered_label
                failure_class = None
                if "normalized_label_repaired" not in quality_flags:
                    quality_flags.append("normalized_label_repaired")
                quality_flags.append(f"recovered_from_rejected:{rejected_failure_class}")

    if failure_class in _FINAL_LABEL_REJECT_FAILURE_CLASSES:
        rejected_raw_label = label
        rejected_failure_class = failure_class
        label = None
        normalized_label = None
        quality_flags = [
            flag for flag in quality_flags if flag != "normalized_label_repaired"
        ]
        quality_flags.extend(["abstained", f"final_label_rejected:{failure_class}"])
        evidence_text = None

    fallback_evidence_texts: list[str] = []
    if hasattr(pred, "temporal_candidate_records") and pred.temporal_candidate_records:
        for item in pred.temporal_candidate_records:
            if isinstance(item, dict):
                candidate_evidence = item.get("evidence_text")
                if isinstance(candidate_evidence, str) and candidate_evidence.strip():
                    fallback_evidence_texts.append(candidate_evidence)

    evidence_text, evidence_flags = _guard_evidence_text(
        record.note_text,
        evidence_text,
        fallback_evidence_texts=fallback_evidence_texts or None,
    )
    quality_flags.extend(evidence_flags)

    metadata: dict[str, Any] = {"program_variant": program_variant}
    if hasattr(pred, "verifier_decision"):
        metadata["verifier_decision"] = pred.verifier_decision
    if hasattr(pred, "verifier_reason"):
        metadata["verifier_reason"] = pred.verifier_reason
    if hasattr(pred, "initial_label"):
        metadata["initial_label"] = pred.initial_label
    if hasattr(pred, "initial_evidence"):
        metadata["initial_evidence"] = pred.initial_evidence
    if hasattr(pred, "temporal_candidate_labels"):
        metadata["temporal_candidate_labels"] = pred.temporal_candidate_labels
    if hasattr(pred, "temporal_candidate_records"):
        metadata["temporal_candidate_records"] = pred.temporal_candidate_records
    if hasattr(pred, "temporal_candidate_source"):
        metadata["temporal_candidate_source"] = pred.temporal_candidate_source
    if hasattr(pred, "validation_ladder_rung"):
        metadata["validation_ladder_rung"] = pred.validation_ladder_rung
    if hasattr(pred, "llm_temporal_candidate_records"):
        metadata["llm_temporal_candidate_records"] = pred.llm_temporal_candidate_records
    if hasattr(pred, "temporal_event_table_records"):
        metadata["temporal_event_table_records"] = pred.temporal_event_table_records
    if hasattr(pred, "multiple_answer_options"):
        metadata["multiple_answer_options"] = pred.multiple_answer_options
    if hasattr(pred, "rejected_multiple_answer_options"):
        metadata["rejected_multiple_answer_options"] = (
            pred.rejected_multiple_answer_options
        )
    if hasattr(pred, "selected_answer_option"):
        metadata["selected_answer_option"] = pred.selected_answer_option
    if hasattr(pred, "closed_answer_options"):
        metadata["closed_answer_options"] = pred.closed_answer_options
    if hasattr(pred, "constructed_answer_options"):
        metadata["constructed_answer_options"] = pred.constructed_answer_options
    if hasattr(pred, "selected_closed_answer_option"):
        metadata["selected_closed_answer_option"] = pred.selected_closed_answer_option
    if hasattr(pred, "closed_option_ranking"):
        metadata["closed_option_ranking"] = pred.closed_option_ranking
    if hasattr(pred, "reason_code_adjudication"):
        metadata["reason_code_adjudication"] = pred.reason_code_adjudication
    if hasattr(pred, "selected_candidate_reference"):
        metadata["selected_candidate_reference"] = pred.selected_candidate_reference
    if hasattr(pred, "label_construction_inputs"):
        metadata["label_construction_inputs"] = pred.label_construction_inputs
    if hasattr(pred, "target_semantic_class"):
        metadata["target_semantic_class"] = pred.target_semantic_class
    if hasattr(pred, "category_decision"):
        metadata["category_decision"] = pred.category_decision
    if hasattr(pred, "candidate_ranking"):
        metadata["candidate_ranking"] = pred.candidate_ranking
    if hasattr(pred, "target_selection_reason_code"):
        metadata["target_selection_reason_code"] = pred.target_selection_reason_code
    if hasattr(pred, "target_selection_error_class"):
        metadata["target_selection_error_class"] = pred.target_selection_error_class
    if hasattr(pred, "temporal_date_event_payload"):
        metadata["temporal_date_event_payload"] = pred.temporal_date_event_payload
    if hasattr(pred, "candidate_support_context"):
        metadata["candidate_support_context"] = pred.candidate_support_context
    if hasattr(pred, "react_trajectory"):
        metadata["react_trajectory"] = pred.react_trajectory
    if hasattr(pred, "react_tool_call_count"):
        metadata["react_tool_call_count"] = pred.react_tool_call_count
    if hasattr(pred, "react_error"):
        metadata["react_error"] = pred.react_error
    if hasattr(pred, "context_policy"):
        metadata["context_policy"] = pred.context_policy
    if hasattr(pred, "prompt_note_text_is_full_note"):
        metadata["prompt_note_text_is_full_note"] = pred.prompt_note_text_is_full_note
    if hasattr(pred, "prompt_note_text_char_count"):
        metadata["prompt_note_text_char_count"] = pred.prompt_note_text_char_count
    if hasattr(pred, "source_note_text_char_count"):
        metadata["source_note_text_char_count"] = pred.source_note_text_char_count
    if rejected_raw_label is not None:
        metadata["rejected_raw_label"] = rejected_raw_label
    if rejected_failure_class is not None:
        metadata["rejected_label_failure_class"] = rejected_failure_class

    value = ExtractedValue(
        field_name=GAN_FREQUENCY_S0_FIELD,
        raw_value=label,
        normalized_value=normalized_label,
        evidence=_evidence_spans(record, evidence_text),
        temporality="unknown",
        negation="unknown",
        confidence=None,
        quality_flags=quality_flags,
    )
    return DocumentPrediction(
        document_id=record.record_id,
        dataset="gan_2026",
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        values=[value],
        metadata=metadata,
    )


def _repair_forbidden_hour_rate(label: str) -> str:
    """Convert forbidden per-hour rates to per-day before scorer validation."""
    unknown_match = _UNKNOWN_PER_HOUR_RATE_RE.match(label)
    if unknown_match is not None:
        daily = float(unknown_match.group("count")) * 24
        return f"{_format_number(daily)} per day"

    match = _PER_HOUR_RATE_RE.match(label)
    if match is None:
        return label
    daily = float(match.group("count")) * 24
    return f"{_format_number(daily)} per day"


def _repair_malformed_cluster_suffix(label: str) -> str:
    """Insert missing 'cluster' when a rate is followed by ', N per cluster'."""
    if " cluster per " in label:
        return label
    match = _MALFORMED_CLUSTER_SUFFIX_RE.match(label)
    if match is None:
        return label
    return (
        f"{match.group('rate')} cluster per {match.group('unit')}, "
        f"{match.group('per_cluster')} per cluster"
    )


def _normalize_predicted_label(label: str | None) -> str | None:
    if label is None:
        return None

    stripped = label.strip()
    if len(stripped) >= 2 and stripped[0] in '"\'' and stripped[-1] == stripped[0]:
        stripped = stripped[1:-1].strip()

    quoted_special = _QUOTED_SPECIAL_LABEL_RE.match(stripped)
    if quoted_special:
        return quoted_special.group("label").lower()

    normalized = _apply_canonical_surface_repairs(stripped)
    normalized = _repair_forbidden_hour_rate(normalized)
    normalized = _repair_malformed_cluster_suffix(normalized)

    every_day_range = _EVERY_DAY_RANGE_RE.match(normalized)
    if every_day_range:
        return f"1 per 1 to {every_day_range.group('end')} day"

    matching_rate_range = _MATCHING_RATE_RANGE_RE.match(normalized)
    if (
        matching_rate_range
        and matching_rate_range.group("first_unit")
        == matching_rate_range.group("second_unit")
    ):
        first = matching_rate_range.group("first")
        second = matching_rate_range.group("second")
        low, high = sorted((float(first), float(second)))
        return (
            f"{matching_rate_range.group('count')} per "
            f"{_format_number(low)} to {_format_number(high)} "
            f"{matching_rate_range.group('first_unit')}"
        )

    daily_count = _DAILY_COUNT_RE.match(normalized)
    if daily_count and float(daily_count.group("count")) > 33:
        return "multiple per day"

    return normalized


def _apply_canonical_surface_repairs(label: str) -> str:
    normalized = re.sub(r"\s+", " ", label.strip().lower())
    normalized = re.sub(
        r"^(?:<=|>=|<|>|at most|at least|up to)\s*",
        "",
        normalized,
    )
    if normalized in _ADJECTIVE_RATE_LABELS:
        return _ADJECTIVE_RATE_LABELS[normalized]

    normalized = re.sub(r"\b(few|several|many)\b", "multiple", normalized)
    normalized = re.sub(
        r"(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)",
        r"\1 to \2",
        normalized,
    )
    normalized = re.sub(
        r"(\d+(?:\.\d+)?)\s+or\s+(\d+(?:\.\d+)?)",
        r"\1 to \2",
        normalized,
    )
    normalized = re.sub(r"\bper\s+fortnight\b", "per 2 week", normalized)
    normalized = re.sub(r"\bper\s+fortnights\b", "per 2 week", normalized)
    normalized = re.sub(r"\bper\s+quarter\b", "per 3 month", normalized)
    normalized = re.sub(r"\bper\s+quarters\b", "per 3 month", normalized)
    return normalized


def _strip_outer_quotes_for_evidence(text: str) -> tuple[str, bool]:
    stripped = text.strip()
    if len(stripped) >= 2 and stripped[0] in '"\'' and stripped[-1] == stripped[0]:
        return stripped[1:-1].strip(), True
    return stripped, False


def _ellipsis_segments(text: str) -> list[str]:
    return [
        segment.strip()
        for segment in _EVIDENCE_ELLIPSIS_RE.split(text)
        if segment.strip()
    ]


def _longest_locatable_in_note(note_text: str, candidate: str) -> str | None:
    if not candidate:
        return None
    if candidate in note_text:
        return candidate
    prefix = candidate
    while prefix and prefix not in note_text:
        prefix = prefix[:-1].rstrip()
    return prefix or None


def _guard_evidence_text(
    note_text: str,
    evidence_text: str | None,
    *,
    fallback_evidence_texts: Iterable[str] | None = None,
) -> tuple[str | None, list[str]]:
    if not evidence_text:
        return None, []

    flags: list[str] = []
    cleaned = evidence_text.strip()

    for marker in _EVIDENCE_PROMPT_FOOTER_MARKERS:
        marker_index = cleaned.find(marker)
        if marker_index != -1:
            cleaned = cleaned[:marker_index].rstrip()
            if "evidence_repaired:prompt_footer_stripped" not in flags:
                flags.append("evidence_repaired:prompt_footer_stripped")

    unquoted, had_outer_quotes = _strip_outer_quotes_for_evidence(cleaned)
    if had_outer_quotes:
        flags.append("evidence_repaired:outer_quotes_stripped")
        cleaned = unquoted

    if cleaned in note_text:
        return cleaned, flags

    locate_candidates: list[tuple[str, str]] = [("primary", cleaned)]
    for segment in _ellipsis_segments(cleaned):
        locate_candidates.append(("ellipsis", segment))
    for fallback in fallback_evidence_texts or []:
        fallback_text = fallback.strip()
        if fallback_text:
            locate_candidates.append(("temporal_candidate", fallback_text))

    best: str | None = None
    best_source: str | None = None
    for source, candidate in locate_candidates:
        located = _longest_locatable_in_note(note_text, candidate)
        if located and (best is None or len(located) > len(best)):
            best = located
            best_source = source

    if not best:
        return cleaned, flags

    if best_source == "ellipsis":
        flags.append("evidence_repaired:ellipsis_segment_selected")
    elif best_source == "temporal_candidate":
        flags.append("evidence_repaired:temporal_candidate_fallback")
    elif best_source == "primary" and best != cleaned:
        flags.append("evidence_repaired:truncated_to_note_span")

    return best, flags


def guard_gan_s0_evidence_text(
    note_text: str,
    evidence_text: str | None,
    *,
    fallback_evidence_texts: Iterable[str] | None = None,
) -> tuple[str | None, list[str]]:
    """Public Gan S0 evidence quote normalization stage surface."""

    return _guard_evidence_text(
        note_text,
        evidence_text,
        fallback_evidence_texts=fallback_evidence_texts,
    )


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(value)


def _evidence_spans(
    record: GanRecord, evidence_text: str | None
) -> list[EvidenceSpan]:
    if not evidence_text:
        return []
    start = record.note_text.find(evidence_text)
    if start == -1:
        return [EvidenceSpan(text=evidence_text, document_id=record.record_id)]
    return [
        EvidenceSpan(
            text=evidence_text,
            start=start,
            end=start + len(evidence_text),
            document_id=record.record_id,
        )
    ]


def _evidence_policy_ok(
    *,
    gold_label: str,
    predicted_evidence: str | None,
    note_text: str,
) -> bool:
    return (
        _evidence_policy_feedback(
            gold_label=gold_label,
            predicted_evidence=predicted_evidence,
            note_text=note_text,
        )
        is None
    )


def _evidence_policy_feedback(
    *,
    gold_label: str,
    predicted_evidence: str | None,
    note_text: str,
) -> str | None:
    if gold_label == "no seizure frequency reference":
        if isinstance(predicted_evidence, str) and predicted_evidence.strip():
            return (
                "[evidence-support] No-reference labels should not include "
                "supporting frequency evidence."
            )
        return None

    if not _requires_evidence_support(gold_label):
        return None

    if not isinstance(predicted_evidence, str) or not predicted_evidence.strip():
        return (
            "[evidence-support] The prediction must include an exact contiguous "
            "source quote as evidence."
        )
    if predicted_evidence.strip() not in note_text:
        return (
            "[evidence-support][unsupported-quote] The evidence_text is not an "
            "exact contiguous quote from the note."
        )
    return None


def _requires_evidence_support(gold_label: str) -> bool:
    return gold_label != "no seizure frequency reference"


def _looks_like_cluster_failure(label: str) -> bool:
    normalized = label.strip().lower()
    return "cluster" in normalized and " per cluster" not in normalized


def _forbidden_unit(label: str) -> str | None:
    match = _FORBIDDEN_UNIT_RE.search(label)
    if match is None:
        return None
    return match.group(1).lower()


def _is_short_seizure_free_label(label: str) -> bool:
    match = _SEIZURE_FREE_RE.match(label)
    if match is None:
        return False
    count = float(match.group("count"))
    months = count * 12 if match.group("unit") == "year" else count
    return months < 6


def _has_temporal_window_mismatch(
    note_text: str,
    *,
    gold_label: str,
    predicted_label: str,
) -> bool:
    if not _YTD_NOTE_RE.search(note_text):
        return False
    if gold_label == predicted_label:
        return False
    return " per " in gold_label and " per " in predicted_label


def gan_frequency_s0_run_metadata(
    run_id: str,
    split_name: str,
    model_provider: str,
    model_name: str,
    *,
    prompt_version: str = "gan_frequency_s0_v1",
    program_variant: str = GAN_FREQUENCY_S0_VARIANT,
    extra: dict | None = None,
) -> RunMetadata:
    """Build a ``RunMetadata`` for a Gan S0 run."""
    return RunMetadata(
        run_id=run_id,
        dataset="gan_2026",
        split_name=split_name,
        model_provider=model_provider,
        model_name=model_name,
        schema_level=GAN_FREQUENCY_S0_SCHEMA_LEVEL,
        program_variant=program_variant,
        scorer_mode=GAN_FREQUENCY_S0_SCORER,
        metric_caveats=[
            "Monthly-frequency, Purist category, and Pragmatic category metrics are benchmark-facing.",
            "Raw exact, normalized-label exact, schema validity, abstention, and evidence support are diagnostic.",
            "Provider adapters target this narrow Gan S0 contract before broader DSPy modules.",
        ],
        metadata={
            "prompt_version": prompt_version,
            **(extra or {}),
        },
    )


__all__ = [
    "_apply_canonical_surface_repairs",
    "_apply_constrained_verifier_guard",
    "_apply_evidence_span_check_guard",
    "_apply_event_table_candidate_rescue",
    "_apply_temporal_verifier_guards",
    "_evidence_policy_feedback",
    "_evidence_policy_ok",
    "_evidence_spans",
    "_forbidden_unit",
    "_guard_evidence_text",
    "_has_temporal_window_mismatch",
    "_is_short_seizure_free_label",
    "_is_unknown_or_abstain_label",
    "_looks_like_cluster_failure",
    "_looks_like_no_reference_note",
    "_normalize_predicted_label",
    "_predict_record",
    "_requires_evidence_support",
    "apply_gan_s0_constrained_verifier_guard",
    "apply_gan_s0_evidence_span_check_guard",
    "gan_frequency_s0_run_metadata",
    "guard_gan_s0_evidence_text",
    "looks_like_gan_s0_no_reference_note",
    "predict_gan_records",
]
