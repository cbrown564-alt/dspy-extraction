import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_FIELD_FAMILIES,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_VARIANT,
    ExectS0S1FieldFamilyModule,
    exect_s0_s1_run_metadata,
    make_exect_s0_s1_dspy_examples,
    predict_exect_records,
)


@pytest.fixture(autouse=True)
def reset_dspy_settings():
    yield
    dspy.settings.configure(lm=None)


def _configure_dummy(answers: list[dict]) -> None:
    dspy.configure(lm=DummyLM(answers=answers))


def test_exect_s0_s1_module_maps_dspy_prediction_to_prediction_set():
    record = load_exect_gold_document("EA0008")
    _configure_dummy([{
        "reasoning": "The note explicitly names diagnosis, seizure type, and medication.",
        "diagnosis": ["focal epilepsy"],
        "diagnosis_evidence": ["epilepsy"],
        "seizure_type": ["focal-seizures-with-altered-awareness"],
        "seizure_type_evidence": ["focal-seizures-with-altered-awareness"],
        "annotated_medication": ["Lamotrigine"],
        "annotated_medication_evidence": ["lamotrigine"],
    }])

    module = ExectS0S1FieldFamilyModule()
    prediction_set = predict_exect_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    assert prediction_set.dataset == "exect_v2"
    assert prediction_set.schema_level == EXECT_S0_S1_SCHEMA_LEVEL
    assert prediction_set.metadata["program_variant"] == EXECT_S0_S1_VARIANT
    assert prediction_set.metadata["model_provider"] == "mock"

    values_by_field = {value.field_name: value for value in prediction_set.predictions[0].values}
    assert set(values_by_field) == set(EXECT_S0_S1_FIELD_FAMILIES)
    assert values_by_field["diagnosis"].normalized_value == "focal epilepsy"
    assert values_by_field["seizure_type"].normalized_value == (
        "focal seizures with altered awareness"
    )
    assert values_by_field["annotated_medication"].normalized_value == "lamotrigine"
    assert values_by_field["annotated_medication"].evidence[0].text == "lamotrigine"


def test_exect_s0_s1_module_records_empty_lists_without_abstention_value():
    record = load_exect_gold_document("EA0016")
    _configure_dummy([{
        "reasoning": "Only a seizure type is explicitly annotated.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": ["focal seizure"],
        "seizure_type_evidence": ["focal seizure"],
        "annotated_medication": [],
        "annotated_medication_evidence": [],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    values = prediction_set.predictions[0].values
    assert [value.field_name for value in values] == ["seizure_type"]
    assert values[0].raw_value == "focal seizure"
    assert values[0].normalized_value == "focal seizure"


def test_exect_s0_s1_bridge_collapses_diagnosis_specificity():
    record = load_exect_gold_document("EA0029")
    _configure_dummy([{
        "reasoning": "The note states JME; parent epilepsy should not be duplicated.",
        "diagnosis": ["epilepsy", "juvenile-myoclonic-epilepsy"],
        "diagnosis_evidence": ["epilepsy", "JME"],
        "seizure_type": [],
        "seizure_type_evidence": [],
        "annotated_medication": [],
        "annotated_medication_evidence": [],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    values = prediction_set.predictions[0].values
    assert len(values) == 1
    assert values[0].field_name == "diagnosis"
    assert values[0].raw_value == "juvenile-myoclonic-epilepsy"
    assert values[0].normalized_value == "juvenile myoclonic epilepsy"
    assert "specificity_collapsed" in values[0].quality_flags


def test_exect_s0_s1_bridge_does_not_infer_seizure_type_from_diagnosis():
    record = load_exect_gold_document("EA0008")
    _configure_dummy([{
        "reasoning": "Diagnosis alone is not a seizure type output.",
        "diagnosis": ["focal epilepsy"],
        "diagnosis_evidence": ["epilepsy"],
        "seizure_type": [],
        "seizure_type_evidence": [],
        "annotated_medication": [],
        "annotated_medication_evidence": [],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    assert [value.field_name for value in prediction_set.predictions[0].values] == [
        "diagnosis"
    ]


def test_make_exect_s0_s1_dspy_examples_sets_note_text_input_and_gold_outputs():
    records = [load_exect_gold_document("EA0008"), load_exect_gold_document("EA0016")]

    examples = make_exect_s0_s1_dspy_examples(records)

    assert len(examples) == 2
    assert examples[0].note_text == records[0].text
    assert examples[0].diagnosis == records[0].diagnoses
    assert examples[0].seizure_type == records[0].seizure_types
    assert examples[0].annotated_medication == records[0].current_medications
    assert "note_text" in examples[0].inputs()


def test_exect_s0_s1_run_metadata_builds_correct_artifact_contract():
    metadata = exect_s0_s1_run_metadata(
        run_id="exect_s0_s1_dspy_test",
        split_name="exectv2_fixed_v1:validation",
        model_provider="mock",
        model_name="dummy",
    )

    assert metadata.dataset == "exect_v2"
    assert metadata.split_name == "exectv2_fixed_v1:validation"
    assert metadata.model_provider == "mock"
    assert metadata.model_name == "dummy"
    assert metadata.schema_level == EXECT_S0_S1_SCHEMA_LEVEL
    assert metadata.program_variant == EXECT_S0_S1_VARIANT
    assert metadata.scorer_mode == EXECT_S0_S1_SCORER
    assert "partial ExECT" in " ".join(metadata.metric_caveats)
