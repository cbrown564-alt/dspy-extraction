import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_FIELD_FAMILIES,
    EXECT_S0_S1_LABEL_POLICY_GUIDANCE,
    EXECT_S0_S1_POLICY_EXAMPLES,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_VARIANT,
    ExectS0S1FieldFamilySignature,
    ExectS0S1FieldFamilyModule,
    ExectS0S1SectionAwareFieldFamilyModule,
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


def test_exect_s0_s1_prompt_policy_covers_benchmark_boundary_cases():
    policy_text = " ".join(EXECT_S0_S1_LABEL_POLICY_GUIDANCE).lower()
    signature_text = ExectS0S1FieldFamilySignature.__doc__.lower()
    example_cases = {example["case"] for example in EXECT_S0_S1_POLICY_EXAMPLES}

    assert (
        EXECT_S0_S1_PROMPT_VERSION
        == "exect_s0_s1_field_family_v3_seizure_evidence_policy"
    )
    assert "planned starts" in policy_text
    assert "previous trials" in policy_text
    assert "focal seizures with altered awareness" in policy_text
    assert "single seizure event" in policy_text
    assert "symptomatic structural focal epilepsy" in signature_text
    assert {
        "planned_medication_exclusion",
        "previous_medication_exclusion",
        "canonical_seizure_type_granularity",
        "diagnosis_label_preservation",
        "plural_seizure_type_preservation",
        "evidence_quote_contiguity",
        "single_event_diagnosis_null",
    }.issubset(example_cases)


def test_exect_s0_s1_policy_fixture_excludes_planned_and_previous_medications():
    record = load_exect_gold_document("EA0018")
    _configure_dummy([{
        "reasoning": (
            "The benchmark-facing policy excludes planned and previously tried "
            "medications, leaving no audited prescription-style medication output."
        ),
        "diagnosis": [],
        "diagnosis_evidence": [],
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

    assert [
        value
        for value in prediction_set.predictions[0].values
        if value.field_name == "annotated_medication"
    ] == []


def test_exect_s0_s1_policy_fixture_uses_canonical_seizure_type_surface():
    record = load_exect_gold_document("EA0018")
    _configure_dummy([{
        "reasoning": "Richer temporal-lobe-onset wording is mapped to the benchmark surface.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": ["temporal lobe seizure"],
        "seizure_type_evidence": ["temporal lobe"],
        "annotated_medication": [],
        "annotated_medication_evidence": [],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    seizure_values = [
        value
        for value in prediction_set.predictions[0].values
        if value.field_name == "seizure_type"
    ]
    assert len(seizure_values) == 1
    assert seizure_values[0].raw_value == "temporal lobe seizure"
    assert seizure_values[0].normalized_value == "temporal lobe seizure"


def test_exect_s0_s1_bridge_splits_fused_temporal_lobe_onset_focal_seizures():
    record = load_exect_gold_document("EA0018")
    _configure_dummy([{
        "reasoning": "The model emitted a fused clinical surface for two audited labels.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": ["temporal lobe onset focal seizures"],
        "seizure_type_evidence": ["temporal lobe onset focal seizures"],
        "annotated_medication": [],
        "annotated_medication_evidence": [],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    seizure_values = [
        value
        for value in prediction_set.predictions[0].values
        if value.field_name == "seizure_type"
    ]
    assert [value.normalized_value for value in seizure_values] == [
        "temporal lobe seizure",
        "focal seizures",
    ]
    assert all(
        value.raw_value == "temporal lobe onset focal seizures"
        for value in seizure_values
    )
    assert all(
        "benchmark_bridge:fused_seizure_type_split" in value.quality_flags
        for value in seizure_values
    )


def test_exect_s0_s1_bridge_repairs_ellipsis_evidence_to_contiguous_quote():
    record = load_exect_gold_document("EA0018")
    _configure_dummy([{
        "reasoning": "The model stitched the medication evidence with an ellipsis.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": [],
        "seizure_type_evidence": [],
        "annotated_medication": ["levetiracetam"],
        "annotated_medication_evidence": [
            "Currently she is taking ... levetiracetam 1000 mg twice today"
        ],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    medication_values = [
        value
        for value in prediction_set.predictions[0].values
        if value.field_name == "annotated_medication"
    ]
    assert len(medication_values) == 1
    assert medication_values[0].evidence[0].text == (
        "Currently she is taking sodium valproate 500 mg twice a day and "
        "levetiracetam 1000 mg twice today"
    )
    assert medication_values[0].evidence[0].start == 537
    assert medication_values[0].evidence[0].end == 634
    assert "evidence_repair:ellipsis_contiguous_span" in medication_values[0].quality_flags


def test_exect_s0_s1_section_aware_module_routes_family_specific_contexts():
    record = load_exect_gold_document("EA0008")
    _configure_dummy([
        {
            "reasoning": "Diagnosis section states the established diagnosis.",
            "diagnosis": ["symptomatic structural focal epilepsy"],
            "diagnosis_evidence": ["Diagnosis: symptomatic structural focal epilepsy"],
        },
        {
            "reasoning": "Seizure section states the active seizure type.",
            "seizure_type": ["focal-seizures-with-altered-awareness"],
            "seizure_type_evidence": ["focal-seizures-with-altered-awareness"],
        },
        {
            "reasoning": "Medication section states the current medication.",
            "annotated_medication": ["Lamotrigine"],
            "annotated_medication_evidence": ["lamotrigine"],
        },
    ])

    prediction_set = predict_exect_records(
        ExectS0S1SectionAwareFieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=EXECT_S0_S1_SECTION_AWARE_VARIANT,
    )

    assert prediction_set.metadata["program_variant"] == EXECT_S0_S1_SECTION_AWARE_VARIANT
    assert prediction_set.predictions[0].metadata["program_variant"] == (
        EXECT_S0_S1_SECTION_AWARE_VARIANT
    )

    values_by_field = {value.field_name: value for value in prediction_set.predictions[0].values}
    assert set(values_by_field) == set(EXECT_S0_S1_FIELD_FAMILIES)
    assert values_by_field["diagnosis"].normalized_value == (
        "symptomatic structural focal epilepsy"
    )
    assert values_by_field["seizure_type"].normalized_value == (
        "focal seizures with altered awareness"
    )
    assert values_by_field["annotated_medication"].normalized_value == "lamotrigine"

    lm_history = dspy.settings.lm.history
    assert len(lm_history) == 3

    diagnosis_prompt = lm_history[0]["messages"][-1]["content"].lower()
    seizure_prompt = lm_history[1]["messages"][-1]["content"].lower()
    medication_prompt = lm_history[2]["messages"][-1]["content"].lower()

    assert "section: diagnosis" in diagnosis_prompt
    assert "diagnosis:" in diagnosis_prompt
    assert "section:" in seizure_prompt
    assert "seizure" in seizure_prompt
    assert "seizure type and frequency" in seizure_prompt
    assert "section:" in medication_prompt
    assert "medication" in medication_prompt
    assert "current anti-epileptic medication" in medication_prompt


def test_exect_s0_s1_policy_fixture_preserves_audited_diagnosis_label():
    record = load_exect_gold_document("EA0008")
    _configure_dummy([{
        "reasoning": "The modifier-rich diagnosis is preserved as the audited label.",
        "diagnosis": ["symptomatic structural focal epilepsy"],
        "diagnosis_evidence": ["Diagnosis: symptomatic structural focal epilepsy"],
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

    diagnosis_values = [
        value
        for value in prediction_set.predictions[0].values
        if value.field_name == "diagnosis"
    ]
    assert len(diagnosis_values) == 1
    assert diagnosis_values[0].normalized_value == "symptomatic structural focal epilepsy"
    assert "unsupported_label" not in diagnosis_values[0].quality_flags


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


def test_exect_s0_s1_run_metadata_can_record_section_aware_variant():
    metadata = exect_s0_s1_run_metadata(
        run_id="exect_s0_s1_section_aware_test",
        split_name="exectv2_fixed_v1:validation",
        model_provider="mock",
        model_name="dummy",
        program_variant=EXECT_S0_S1_SECTION_AWARE_VARIANT,
    )

    assert metadata.program_variant == EXECT_S0_S1_SECTION_AWARE_VARIANT
