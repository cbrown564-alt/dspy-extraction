import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.programs.exect_s3 import (
    EXECT_S3_CLEAN_LADDER_V1_VARIANT,
    EXECT_S3_FIELD_FAMILIES,
    EXECT_S3_LABEL_POLICY_GUIDANCE,
    EXECT_S3_PROMPT_VERSION,
    EXECT_S3_SCHEMA_LEVEL,
    EXECT_S3_VARIANT,
    ExectS3FieldFamilyModule,
    _recover_s3_epilepsy_cause_raw_values,
    _recover_s3_investigation_raw_values,
    _recover_s3_onset_raw_values,
    _recover_s3_when_diagnosed_raw_values,
    _seizure_phrases_from_misplaced_s3_slots,
    predict_exect_s3_records,
)


@pytest.fixture(autouse=True)
def reset_dspy_settings():
    yield
    dspy.settings.configure(lm=None)


def test_exect_s3_module_maps_prediction_to_nine_field_families():
    record = load_exect_gold_document("EA0062")
    dspy.configure(
        lm=DummyLM(
            answers=[
                {
                    "reasoning": "The note mentions born normally.",
                    "diagnosis": [],
                    "diagnosis_evidence": [],
                    "seizure_type": [],
                    "seizure_type_evidence": [],
                    "annotated_medication": [],
                    "annotated_medication_evidence": [],
                    "investigation": [],
                    "investigation_evidence": [],
                    "comorbidity": [],
                    "comorbidity_evidence": [],
                    "birth_history": ["born normally"],
                    "birth_history_evidence": ["born normally"],
                    "onset": [],
                    "onset_evidence": [],
                    "epilepsy_cause": [],
                    "epilepsy_cause_evidence": [],
                    "when_diagnosed": [],
                    "when_diagnosed_evidence": [],
                }
            ]
        )
    )

    prediction_set = predict_exect_s3_records(
        ExectS3FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    assert prediction_set.schema_level == EXECT_S3_SCHEMA_LEVEL
    assert prediction_set.metadata["program_variant"] == EXECT_S3_VARIANT
    assert prediction_set.metadata["s2_prompt_anchor"] == "exect_s2_field_family_v1_3_label_policy"
    fields = {value.field_name for value in prediction_set.predictions[0].values}
    assert fields <= set(EXECT_S3_FIELD_FAMILIES)
    assert "birth_history" in fields


def test_exect_s3_label_policy_extends_s2_guidance():
    assert EXECT_S3_PROMPT_VERSION == "exect_s3_field_family_v1_2_label_policy"
    assert any("seizure priority" in rule.lower() for rule in EXECT_S3_LABEL_POLICY_GUIDANCE)
    assert any("nine-family" in rule.lower() for rule in EXECT_S3_LABEL_POLICY_GUIDANCE)
    assert any("modality+result" in rule.lower() for rule in EXECT_S3_LABEL_POLICY_GUIDANCE)
    assert any("mri brain normal" in rule.lower() for rule in EXECT_S3_LABEL_POLICY_GUIDANCE)
    assert any("birth history" in rule.lower() for rule in EXECT_S3_LABEL_POLICY_GUIDANCE)
    assert any("epilepsy cause" in rule.lower() for rule in EXECT_S3_LABEL_POLICY_GUIDANCE)
    assert any("when diagnosed" in rule.lower() for rule in EXECT_S3_LABEL_POLICY_GUIDANCE)
    assert any("investigation" in rule.lower() for rule in EXECT_S3_LABEL_POLICY_GUIDANCE)


def test_recover_s3_investigation_raw_values_maps_prose_to_modality_result():
    recovered, flags = _recover_s3_investigation_raw_values(
        ["mri brain normal", "eeg generalized spike and wave", "mri planned"],
        "Investigations: MRI brain normal. EEG showed spike and wave. MRI planned next month.",
    )
    assert recovered == ["mri normal", "eeg abnormal"]
    assert "s3_bridge:investigation_modality_result_restored" in flags
    assert "s3_bridge:investigation_prose_removed" in flags


def test_recover_s3_onset_raw_values_keeps_epilepsy_strips_seizure_types():
    recovered, flags = _recover_s3_onset_raw_values(
        ["epilepsy", "generalized tonic clonic seizures"],
        "Epilepsy since age 4 with generalized tonic clonic seizures.",
    )
    assert recovered == ["epilepsy"]
    assert "s3_bridge:onset_seizure_type_removed" in flags


def test_seizure_phrases_from_misplaced_s3_slots_reroutes_onset_seizure_types():
    pred = dspy.Prediction(
        onset=["generalized tonic clonic seizures"],
        when_diagnosed=[],
        comorbidity=[],
    )
    assert _seizure_phrases_from_misplaced_s3_slots(pred) == [
        "generalized tonic clonic seizures"
    ]


def test_recover_s3_when_diagnosed_raw_values_drops_seizure_type_labels():
    recovered, flags = _recover_s3_when_diagnosed_raw_values(
        ["single focal seizure", "epilepsy"],
        "Diagnosis: epilepsy. She was diagnosed in childhood.",
    )
    assert recovered == ["epilepsy"]
    assert "s3_bridge:when_diagnosed_seizure_type_removed" in flags


def test_recover_s3_epilepsy_cause_raw_values_drops_seizure_history():
    recovered, flags = _recover_s3_epilepsy_cause_raw_values(
        ["meningitis", "febrile seizures"],
        "Epilepsy secondary to meningitis.",
    )
    assert recovered == ["meningitis"]
    assert "s3_bridge:seizure_history_cause_removed" in flags


def test_s3_s2_field_values_apply_i0_investigation_guard():
    from clinical_extraction.programs.exect_s3 import _s2_field_values_from_prediction

    record = load_exect_gold_document("EA0016")
    pred = dspy.Prediction(
        diagnosis=[],
        diagnosis_evidence=[],
        seizure_type=[],
        seizure_type_evidence=[],
        annotated_medication=[],
        annotated_medication_evidence=[],
        investigation=["ecg normal", "ct abnormal"],
        investigation_evidence=["ECG normal", "CT abnormal"],
        comorbidity=[],
        comorbidity_evidence=[],
    )
    values = _s2_field_values_from_prediction(pred, record)
    investigation = [
        value.normalized_value
        for value in values
        if value.field_name == "investigation"
    ]
    assert investigation == ["ct abnormal"]
    assert "ecg normal" not in investigation


def test_s3_clean_ladder_applies_s2_medication_guard_to_inherited_fields():
    from clinical_extraction.programs.exect_s3 import _s2_field_values_from_prediction

    record = load_exect_gold_document("EA0007")
    pred = dspy.Prediction(
        diagnosis=[],
        diagnosis_evidence=[],
        seizure_type=[],
        seizure_type_evidence=[],
        annotated_medication=["lamotrigine", "aspirin"],
        annotated_medication_evidence=["lamotrigine", "aspirin"],
        investigation=[],
        investigation_evidence=[],
        comorbidity=[],
        comorbidity_evidence=[],
    )
    values = _s2_field_values_from_prediction(
        pred,
        record,
        program_variant=EXECT_S3_CLEAN_LADDER_V1_VARIANT,
    )
    medication = [
        value.normalized_value
        for value in values
        if value.field_name == "annotated_medication"
    ]

    assert "lamotrigine" in medication
    assert "aspirin" not in medication
