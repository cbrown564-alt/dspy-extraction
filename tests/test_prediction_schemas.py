import pytest
from pydantic import ValidationError

from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExtractedValue,
    PredictionSet,
)


def test_prediction_schema_serializes_evidence_normalization_and_flags():
    prediction = DocumentPrediction(
        document_id="gan_42",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        values=[
            ExtractedValue(
                field_name="seizure_frequency_number",
                raw_value="once per month",
                normalized_value="1 per 1 month",
                temporality="current",
                negation="affirmed",
                confidence=0.87,
                quality_flags=["normalized_surface_form"],
                evidence=[
                    EvidenceSpan(
                        document_id="gan_42",
                        text="She has had one seizure per month.",
                        start=12,
                        end=33,
                        section="history",
                    )
                ],
            )
        ],
        quality_flags=["schema_valid"],
        metadata={"split": "dev"},
    )

    serialized = prediction.model_dump(mode="json")

    assert serialized == {
        "document_id": "gan_42",
        "dataset": "gan_2026",
        "schema_level": "gan_frequency_s0",
        "values": [
            {
                "field_name": "seizure_frequency_number",
                "raw_value": "once per month",
                "normalized_value": "1 per 1 month",
                "evidence": [
                    {
                        "text": "She has had one seizure per month.",
                        "start": 12,
                        "end": 33,
                        "document_id": "gan_42",
                        "section": "history",
                    }
                ],
                "temporality": "current",
                "negation": "affirmed",
                "confidence": 0.87,
                "quality_flags": ["normalized_surface_form"],
                "metadata": {},
            }
        ],
        "quality_flags": ["schema_valid"],
        "metadata": {"split": "dev"},
    }


def test_prediction_set_keeps_schema_level_as_run_metadata():
    prediction_set = PredictionSet(
        dataset="exectv2",
        schema_level="S3_temporality_probe",
        predictions=[
            DocumentPrediction(
                document_id="EA0001",
                dataset="exectv2",
                schema_level="S3_temporality_probe",
            )
        ],
    )

    assert prediction_set.schema_level == "S3_temporality_probe"


def test_prediction_set_rejects_mixed_dataset_or_schema_contexts():
    with pytest.raises(ValidationError, match="dataset"):
        PredictionSet(
            dataset="gan_2026",
            schema_level="S0",
            predictions=[
                DocumentPrediction(
                    document_id="EA0001",
                    dataset="exectv2",
                    schema_level="S0",
                )
            ],
        )

    with pytest.raises(ValidationError, match="schema_level"):
        PredictionSet(
            dataset="gan_2026",
            schema_level="S0",
            predictions=[
                DocumentPrediction(
                    document_id="gan_1",
                    dataset="gan_2026",
                    schema_level="S1",
                )
            ],
        )


def test_evidence_span_validates_offsets_and_confidence_bounds():
    with pytest.raises(ValidationError, match="both start and end"):
        EvidenceSpan(text="one seizure per month", start=4)

    with pytest.raises(ValidationError, match="greater than or equal"):
        EvidenceSpan(text="one seizure per month", start=10, end=5)

    with pytest.raises(ValidationError):
        ExtractedValue(field_name="diagnosis", confidence=1.5)
