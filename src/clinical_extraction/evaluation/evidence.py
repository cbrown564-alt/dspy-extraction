from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from clinical_extraction.schemas import EvidenceSpan


class EvidenceScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    predicted_evidence_count: int
    predicted_evidence_with_offsets: int
    quote_supported: bool
    offsets_valid: bool | None


def score_evidence_support(
    *,
    document_text: str,
    predicted_evidence: list[EvidenceSpan],
) -> EvidenceScore:
    """Score whether predicted evidence is grounded in the source document.

    Gan evidence annotations are not treated as gold spans here because they can
    be paraphrased or summarized. Support means the predicted quote itself is
    deterministically locatable in the source document.
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

    return EvidenceScore(
        predicted_evidence_count=len(predicted_evidence),
        predicted_evidence_with_offsets=len(predictions_with_offsets),
        quote_supported=quote_supported,
        offsets_valid=offsets_valid,
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

