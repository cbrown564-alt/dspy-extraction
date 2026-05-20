import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.programs.exect_s4 import (
    EXECT_S4_FIELD_FAMILIES,
    EXECT_S4_LABEL_POLICY_GUIDANCE,
    EXECT_S4_PROMPT_VERSION,
    EXECT_S4_SCHEMA_LEVEL,
    EXECT_S4_VARIANT,
    ExectS4FieldFamilyModule,
    _recover_s4_investigation_raw_values,
    _recover_s4_medication_temporality_raw_values,
    _recover_s4_seizure_frequency_raw_values,
    _repair_s4_seizure_frequency_surface,
    predict_exect_s4_records,
)


@pytest.fixture(autouse=True)
def reset_dspy_settings():
    yield
    dspy.settings.configure(lm=None)


def test_exect_s4_module_maps_prediction_to_eleven_field_families():
    record = load_exect_gold_document("EA0008")
    dspy.configure(
        lm=DummyLM(
            answers=[
                {
                    "reasoning": "The note mentions frequency and current lamotrigine.",
                    "diagnosis": [],
                    "diagnosis_evidence": [],
                    "seizure_type": [],
                    "seizure_type_evidence": [],
                    "annotated_medication": ["lamotrigine"],
                    "annotated_medication_evidence": ["lamotrigine 75mg bd"],
                    "investigation": [],
                    "investigation_evidence": [],
                    "comorbidity": [],
                    "comorbidity_evidence": [],
                    "birth_history": [],
                    "birth_history_evidence": [],
                    "onset": [],
                    "onset_evidence": [],
                    "epilepsy_cause": [],
                    "epilepsy_cause_evidence": [],
                    "when_diagnosed": [],
                    "when_diagnosed_evidence": [],
                    "seizure_frequency": ["1 per 3 week", "frequency increased"],
                    "seizure_frequency_evidence": [
                        "one every three weeks",
                        "frequency has increased",
                    ],
                    "medication_temporality": ["lamotrigine|current"],
                    "medication_temporality_evidence": ["Current medication: lamotrigine"],
                }
            ]
        )
    )

    prediction_set = predict_exect_s4_records(
        ExectS4FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    assert prediction_set.schema_level == EXECT_S4_SCHEMA_LEVEL
    assert prediction_set.metadata["program_variant"] == EXECT_S4_VARIANT
    assert prediction_set.metadata["s3_prompt_anchor"] == "exect_s3_field_family_v1_2_label_policy"
    fields = {value.field_name for value in prediction_set.predictions[0].values}
    assert fields <= set(EXECT_S4_FIELD_FAMILIES)
    assert "seizure_frequency" in fields
    assert "medication_temporality" in fields


def test_exect_s4_label_policy_extends_s3_guidance():
    assert EXECT_S4_PROMPT_VERSION == "exect_s4_field_family_v1_2_label_policy"
    assert any("eleven-family" in rule.lower() for rule in EXECT_S4_LABEL_POLICY_GUIDANCE)
    assert any("seizure frequency" in rule.lower() for rule in EXECT_S4_LABEL_POLICY_GUIDANCE)
    assert any("medication|status" in rule.lower() for rule in EXECT_S4_LABEL_POLICY_GUIDANCE)
    assert any("seizure priority" in rule.lower() for rule in EXECT_S4_LABEL_POLICY_GUIDANCE)
    assert any("per 1" in rule.lower() for rule in EXECT_S4_LABEL_POLICY_GUIDANCE)
    assert any("frequency increased" in rule.lower() for rule in EXECT_S4_LABEL_POLICY_GUIDANCE)
    assert any("unknown" in rule.lower() for rule in EXECT_S4_LABEL_POLICY_GUIDANCE)


def test_recover_s4_seizure_frequency_raw_values_keeps_rates_strips_types():
    recovered, flags = _recover_s4_seizure_frequency_raw_values(
        ["1 per 3 week", "focal seizures", "frequency increased"],
        "Seizure type focal seizures. One per three weeks.",
    )
    assert recovered == ["1 per 3 week", "frequency increased"]
    assert "s4_bridge:seizure_type_removed_from_frequency" in flags


def test_recover_s4_medication_temporality_raw_values_accepts_pipe_format():
    recovered, flags = _recover_s4_medication_temporality_raw_values(
        ["lamotrigine|current"],
        "Current anti-epileptic medication: lamotrigine 75mg bd.",
    )
    assert recovered == ["lamotrigine|current"]
    assert flags == []


def test_recover_s4_medication_temporality_raw_values_rejects_bare_medication():
    recovered, flags = _recover_s4_medication_temporality_raw_values(
        ["lamotrigine"],
        "Current anti-epileptic medication: lamotrigine 75mg bd.",
    )
    assert recovered == ["lamotrigine|current"]
    assert "s4_bridge:medication_temporality_status_inferred" in flags


def test_repair_s4_seizure_frequency_surface_inserts_missing_time_period():
    repaired, flags = _repair_s4_seizure_frequency_surface("1 per month")
    assert repaired == "1 per 1 month"
    assert "s4_bridge:frequency_missing_time_period_inserted" in flags


def test_repair_s4_seizure_frequency_surface_leaves_dual_cardinal_unchanged():
    repaired, flags = _repair_s4_seizure_frequency_surface("1 per 3 week")
    assert repaired == "1 per 3 week"
    assert flags == []


def test_repair_s4_seizure_frequency_surface_collapses_seizure_free_prose():
    repaired, flags = _repair_s4_seizure_frequency_surface("seizure free for more than five years")
    assert repaired == "seizure free"
    assert "s4_bridge:seizure_free_prose_collapsed" in flags


def test_recover_s4_seizure_frequency_raw_values_repairs_near_miss_quantified():
    recovered, flags = _recover_s4_seizure_frequency_raw_values(
        ["1 per day", "1 per month", "frequency increased"],
        "One seizure per day and one per month; frequency has increased.",
    )
    assert recovered == ["1 per 1 day", "1 per 1 month", "frequency increased"]
    assert "s4_bridge:frequency_missing_time_period_inserted" in flags


def test_recover_s4_seizure_frequency_raw_values_adds_co_labels_from_note():
    recovered, flags = _recover_s4_seizure_frequency_raw_values(
        ["1 per 3 week"],
        "He has about one focal seizure every three weeks and the frequency has increased.",
    )
    assert recovered == ["1 per 3 week", "frequency increased"]
    assert "s4_bridge:frequency_co_label_augmented" in flags


def test_recover_s4_seizure_frequency_raw_values_blocks_non_audited_periods():
    recovered, flags = _recover_s4_seizure_frequency_raw_values(
        ["1 per 30 day", "1 per 3 week", "1 per previous appointment"],
        "One every three weeks.",
    )
    assert recovered == ["1 per 3 week"]
    assert "s4_bridge:non_audited_frequency_removed" in flags


def test_recover_s4_investigation_raw_values_drops_planned_scan_unknown():
    recovered, flags = _recover_s4_investigation_raw_values(
        ["mri unknown", "eeg unknown"],
        "I will arrange an MRI brain and an EEG.",
    )
    assert recovered == []
    assert "s4_bridge:investigation_unknown_removed" in flags


def test_recover_s4_investigation_raw_values_keeps_unavailable_results_unknown():
    recovered, flags = _recover_s4_investigation_raw_values(
        ["eeg unknown", "mri normal"],
        (
            "He had an MRI scan which was normal. "
            "I do not have the results of his recent EEG test."
        ),
    )
    assert recovered == ["eeg unknown", "mri normal"]
    assert flags == []
