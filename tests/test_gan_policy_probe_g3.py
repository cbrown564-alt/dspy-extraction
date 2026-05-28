from __future__ import annotations

from clinical_extraction.schemas import DocumentPrediction, ExtractedValue
from clinical_extraction.evaluation.gan_policy_probe_g3 import apply_g3_policy_rules


def test_rule_unknown_vs_noref_adjusts_to_noref():
    # Prediction has draft label "unknown" but no temporal candidates and no active options
    pred = DocumentPrediction(
        document_id="test_1",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        values=[
            ExtractedValue(
                field_name="seizure_frequency_number",
                raw_value="unknown",
                normalized_value="unknown",
            )
        ],
        metadata={
            "temporal_candidate_labels": [],
            "multiple_answer_options": [
                {"canonical_label": "no seizure frequency reference", "status": "absent"}
            ]
        }
    )
    result = apply_g3_policy_rules(pred)
    assert result == "no seizure frequency reference"


def test_rule_unknown_vs_noref_keeps_unknown():
    # Prediction has draft label "unknown", no options, but has a temporal candidate rate label
    pred = DocumentPrediction(
        document_id="test_2",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        values=[
            ExtractedValue(
                field_name="seizure_frequency_number",
                raw_value="unknown",
                normalized_value="unknown",
            )
        ],
        metadata={
            "temporal_candidate_labels": ["1 per month"],
            "multiple_answer_options": []
        }
    )
    result = apply_g3_policy_rules(pred)
    assert result == "unknown"


def test_rule_weak_rate_to_unknown_triggers():
    # Prediction has draft rate label but selected option has uncertainty flags
    pred = DocumentPrediction(
        document_id="test_3",
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        values=[
            ExtractedValue(
                field_name="seizure_frequency_number",
                raw_value="1 per month",
                normalized_value="1 per month",
            )
        ],
        metadata={
            "selected_answer_option": {
                "canonical_label": "1 per month",
                "ambiguity_flags": ["uncertain_denominator"]
            },
            "multiple_answer_options": [
                {
                    "canonical_label": "1 per month",
                    "ambiguity_flags": ["uncertain_denominator"]
                }
            ]
        }
    )
    result = apply_g3_policy_rules(pred)
    assert result == "unknown"
