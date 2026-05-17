from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from clinical_extraction.schemas import EvidenceSpan


class EvidenceScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    predicted_evidence_count: int
    predicted_evidence_with_offsets: int
    quote_supported: bool
    offsets_valid: bool | None
    gold_evidence_locatable: bool | None
    best_overlap_ratio: float | None
    best_iou: float | None


def score_evidence_support(
    *,
    document_text: str,
    predicted_evidence: list[EvidenceSpan],
    gold_evidence_text: str | None = None,
) -> EvidenceScore:
    """Score whether predicted evidence is grounded in the source document.

    Quote support is deliberately independent from overlap: a quote can be
    supported by document text even when no offsets are supplied, while overlap
    requires both predicted and gold evidence to be locatable as spans.
    """

    located_predictions = [
        _locate_predicted_span(document_text, span) for span in predicted_evidence
    ]
    predictions_with_offsets = [
        span
        for span in predicted_evidence
        if span.start is not None and span.end is not None
    ]
    quote_supported = bool(predicted_evidence) and all(
        located is not None for located in located_predictions
    )
    offsets_valid = _offsets_valid(document_text, predictions_with_offsets)

    gold_range = _find_text_range(document_text, gold_evidence_text)
    predicted_ranges = [located for located in located_predictions if located is not None]
    overlap_scores = [
        _overlap_scores(predicted_range, gold_range)
        for predicted_range in predicted_ranges
        if gold_range is not None
    ]
    best_overlap_ratio = max(
        (score[0] for score in overlap_scores),
        default=None,
    )
    best_iou = max(
        (score[1] for score in overlap_scores),
        default=None,
    )

    return EvidenceScore(
        predicted_evidence_count=len(predicted_evidence),
        predicted_evidence_with_offsets=len(predictions_with_offsets),
        quote_supported=quote_supported,
        offsets_valid=offsets_valid,
        gold_evidence_locatable=None if gold_evidence_text is None else gold_range is not None,
        best_overlap_ratio=best_overlap_ratio,
        best_iou=best_iou,
    )


def _locate_predicted_span(
    document_text: str,
    evidence: EvidenceSpan,
) -> tuple[int, int] | None:
    if evidence.start is not None and evidence.end is not None:
        if document_text[evidence.start : evidence.end] == evidence.text:
            return (evidence.start, evidence.end)
        return None
    return _find_text_range(document_text, evidence.text)


def _find_text_range(
    document_text: str,
    text: str | None,
) -> tuple[int, int] | None:
    if not text:
        return None
    start = document_text.find(text)
    if start == -1:
        return None
    return (start, start + len(text))


def _offsets_valid(document_text: str, evidence_spans: list[EvidenceSpan]) -> bool | None:
    if not evidence_spans:
        return None
    return all(
        document_text[span.start : span.end] == span.text
        for span in evidence_spans
        if span.start is not None and span.end is not None
    )


def _overlap_scores(
    predicted_range: tuple[int, int],
    gold_range: tuple[int, int],
) -> tuple[float, float]:
    predicted_start, predicted_end = predicted_range
    gold_start, gold_end = gold_range
    intersection = max(0, min(predicted_end, gold_end) - max(predicted_start, gold_start))
    gold_length = max(1, gold_end - gold_start)
    union = max(predicted_end, gold_end) - min(predicted_start, gold_start)
    return intersection / gold_length, intersection / union
