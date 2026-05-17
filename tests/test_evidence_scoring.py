from clinical_extraction.evaluation.evidence import score_evidence_support
from clinical_extraction.schemas import EvidenceSpan


def test_evidence_score_supports_quotes_without_offsets():
    document_text = "History: she has had one seizure per month since March."
    gold = "one seizure per month"
    score = score_evidence_support(
        document_text=document_text,
        gold_evidence_text=gold,
        predicted_evidence=[EvidenceSpan(text=gold)],
    )

    assert score.predicted_evidence_count == 1
    assert score.predicted_evidence_with_offsets == 0
    assert score.quote_supported is True
    assert score.offsets_valid is None
    assert score.gold_evidence_locatable is True
    assert score.best_overlap_ratio == 1.0
    assert score.best_iou == 1.0


def test_evidence_score_rejects_offsets_that_do_not_match_text():
    document_text = "History: she has had one seizure per month since March."
    score = score_evidence_support(
        document_text=document_text,
        gold_evidence_text="one seizure per month",
        predicted_evidence=[
            EvidenceSpan(text="one seizure per month", start=0, end=21)
        ],
    )

    assert score.quote_supported is False
    assert score.predicted_evidence_with_offsets == 1
    assert score.offsets_valid is False
    assert score.best_overlap_ratio is None
    assert score.best_iou is None


def test_evidence_score_exposes_unlocatable_gold_evidence():
    document_text = "History: seizures were discussed, but no clear rate was recorded."
    score = score_evidence_support(
        document_text=document_text,
        gold_evidence_text="one seizure per month",
        predicted_evidence=[EvidenceSpan(text="seizures were discussed")],
    )

    assert score.quote_supported is True
    assert score.gold_evidence_locatable is False
    assert score.best_overlap_ratio is None
    assert score.best_iou is None
