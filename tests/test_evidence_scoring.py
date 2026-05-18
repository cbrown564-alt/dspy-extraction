from clinical_extraction.evaluation.evidence import score_evidence_support
from clinical_extraction.schemas import EvidenceSpan


def test_evidence_score_supports_quotes_without_offsets():
    document_text = "History: she has had one seizure per month since March."
    score = score_evidence_support(
        document_text=document_text,
        predicted_evidence=[EvidenceSpan(text="one seizure per month")],
    )

    assert score.predicted_evidence_count == 1
    assert score.predicted_evidence_with_offsets == 0
    assert score.quote_supported is True
    assert score.offsets_valid is None


def test_evidence_score_rejects_offsets_that_do_not_match_text():
    document_text = "History: she has had one seizure per month since March."
    score = score_evidence_support(
        document_text=document_text,
        predicted_evidence=[
            EvidenceSpan(text="one seizure per month", start=0, end=21)
        ],
    )

    assert score.quote_supported is False
    assert score.predicted_evidence_with_offsets == 1
    assert score.offsets_valid is False


def test_evidence_score_ignores_paraphrased_gold_evidence_concepts():
    document_text = "History: she reports one seizure per month since March."
    score = score_evidence_support(
        document_text=document_text,
        predicted_evidence=[EvidenceSpan(text="one seizure per month")],
    )

    assert score.quote_supported is True
