import dspy
from dspy.utils import DummyLM

from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.exect.s5_stack import (
    apply_exect_s5_annotated_medication_guard,
    apply_exect_s5_frequency_verifier_guards,
    build_exect_s5_stack_metadata,
    qualitative_label_supported_by_evidence,
    stage_graph_id_for_s5_program_variant,
)
from clinical_extraction.exect.s5_modules import (
    ExectS5FrequencyPreVocabAmGuardFrequencyVerifyModule,
    ExectS5FrequencyPreVocabAmGuardFrequencyVerifyV2Module,
    ExectS5FrequencyPreVocabAmGuardFrequencyVerifyV2bModule,
    ExectS5CoreFieldFamilyParallelV2bModule,
)
from clinical_extraction.exect.s5_signatures import (
    build_exect_s5_core_family_specific_signature,
)
from clinical_extraction.exect.s5_stack import (
    EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT,
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT,
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
)
from clinical_extraction.programs.exect_s4 import (
    build_exect_s4_module,
    predict_exect_s4_records,
)
from clinical_extraction.schemas import ExtractedValue


def test_frequency_verifier_guard_blocks_added_labels_and_candidate_echo():
    guarded = apply_exect_s5_frequency_verifier_guards(
        note_text="Current seizures occur one per month.",
        initial_frequency=["1 per 1 month"],
        verified=dspy.Prediction(
            seizure_frequency=["1 per 1 month", "frequency increased"],
            seizure_frequency_evidence=[
                "Current seizures occur one per month",
                "seizure_frequency: frequency increased",
            ],
            verifier_decision="repair",
            verifier_reason="drop unsupported qualitative label",
        ),
    )

    assert guarded.seizure_frequency == ["1 per 1 month"]
    assert guarded.seizure_frequency_evidence == [
        "Current seizures occur one per month"
    ]
    assert "verifier_added_label_blocked" in guarded.frequency_verifier_flags


def test_frequency_verifier_guard_rejects_medication_control_change():
    guarded = apply_exect_s5_frequency_verifier_guards(
        note_text="We increased lamotrigine and seizure control has improved.",
        initial_frequency=["frequency decreased"],
        verified=dspy.Prediction(
            seizure_frequency=["frequency decreased"],
            seizure_frequency_evidence=[
                "increased lamotrigine and seizure control has improved"
            ],
            verifier_decision="repair",
            verifier_reason="medication control is not frequency evidence",
        ),
    )

    assert guarded.seizure_frequency == []
    assert "medication_control_not_frequency_change" in guarded.frequency_verifier_flags


def test_build_exect_s4_module_returns_frequency_verify_wrapper():
    module = build_exect_s4_module(
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT
    )

    assert isinstance(module, ExectS5FrequencyPreVocabAmGuardFrequencyVerifyModule)


def test_exect_s4_facade_reexports_s5_module_classes():
    from clinical_extraction.programs import exect_s4

    assert (
        exect_s4.ExectS5FrequencyPreVocabAmGuardFrequencyVerifyModule
        is ExectS5FrequencyPreVocabAmGuardFrequencyVerifyModule
    )
    assert (
        exect_s4.ExectS5CoreFieldFamilyParallelV2bModule
        is ExectS5CoreFieldFamilyParallelV2bModule
    )


def test_build_exect_s4_module_returns_frequency_verify_v2_wrapper():
    module = build_exect_s4_module(
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2_VARIANT
    )

    assert isinstance(module, ExectS5FrequencyPreVocabAmGuardFrequencyVerifyV2Module)


def test_build_exect_s4_module_returns_frequency_verify_v2b_wrapper():
    module = build_exect_s4_module(
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT
    )

    assert isinstance(module, ExectS5FrequencyPreVocabAmGuardFrequencyVerifyV2bModule)


def test_frequency_verifier_v2_strict_qualitative_guard_blocks_unsupported_label():
    guarded = apply_exect_s5_frequency_verifier_guards(
        note_text="Current seizures occur one per month.",
        initial_frequency=["1 per 1 month", "infrequent"],
        verified=dspy.Prediction(
            seizure_frequency=["1 per 1 month", "infrequent"],
            seizure_frequency_evidence=[
                "Current seizures occur one per month",
                "Current seizures occur one per month",
            ],
            verifier_decision="repair",
            verifier_reason="drop unsupported infrequent",
        ),
        strict_qualitative=True,
    )

    assert guarded.seizure_frequency == ["1 per 1 month"]
    assert "qualitative_without_note_support" in guarded.frequency_verifier_flags


def test_qualitative_label_supported_by_evidence_accepts_explicit_wording():
    assert qualitative_label_supported_by_evidence(
        "infrequent",
        "She continues to have infrequent focal seizures.",
    )
    assert qualitative_label_supported_by_evidence(
        "frequency decreased",
        "seizures have improved since reducing the lamotrigine",
    )


def test_frequency_verify_wrapper_is_reject_only_and_preserves_am_guard():
    record = load_exect_gold_document("EA0008")
    dspy.configure(
        lm=DummyLM(
            answers=[
                {
                    "reasoning": "Initial S5 extraction.",
                    "diagnosis": [],
                    "diagnosis_evidence": [],
                    "seizure_type": [],
                    "seizure_type_evidence": [],
                    "annotated_medication": ["lamotrigine", "amitriptyline"],
                    "annotated_medication_evidence": [
                        "lamotrigine 75mg bd",
                        "amitriptyline",
                    ],
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
                        "every 3 weeks",
                        "seizure_frequency: frequency increased",
                    ],
                    "medication_temporality": [],
                    "medication_temporality_evidence": [],
                },
                {
                    "seizure_frequency": ["1 per 3 week", "frequency decreased"],
                    "seizure_frequency_evidence": [
                        "every 3 weeks",
                        "not in initial output",
                    ],
                    "verifier_decision": "repair",
                    "verifier_reason": "confirmed rate only",
                },
            ]
        )
    )

    prediction_set = predict_exect_s4_records(
        build_exect_s4_module(
            EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT
        ),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
        schema_level="exect_s5_core_field_family",
    )

    values = prediction_set.predictions[0].values
    by_family = {}
    for value in values:
        by_family.setdefault(value.field_name, []).append(value.normalized_value)

    assert by_family["seizure_frequency"] == ["1 per 3 week"]
    assert by_family["annotated_medication"] == ["lamotrigine"]
    assert prediction_set.predictions[0].metadata["frequency_verifier"][
        "primitive_id"
    ] == "exect.frequency.evidence_verify_policy.v1"


def test_frequency_verifier_guard_allows_seizures_improved_with_medication():
    guarded = apply_exect_s5_frequency_verifier_guards(
        note_text="I was pleased to hear that his seizures have improved since reducing the lamotrigine.",
        initial_frequency=["frequency decreased"],
        verified=dspy.Prediction(
            seizure_frequency=["frequency decreased"],
            seizure_frequency_evidence=[
                "seizures have improved since reducing the lamotrigine"
            ],
            verifier_decision="confirm",
            verifier_reason="valid frequency decrease indicator",
        ),
    )

    assert guarded.seizure_frequency == ["frequency decreased"]
    assert guarded.seizure_frequency_evidence == [
        "seizures have improved since reducing the lamotrigine"
    ]
    assert "medication_control_not_frequency_change" not in guarded.frequency_verifier_flags


def test_frequency_verifier_guard_case_insensitive_and_recovery():
    guarded = apply_exect_s5_frequency_verifier_guards(
        note_text="She thinks that she has about one a week.",
        initial_frequency=["1 per 1 week"],
        verified=dspy.Prediction(
            seizure_frequency=["1 per 1 week"],
            seizure_frequency_evidence=[
                "she thinks that she has about one a week"  # lowercased 'she'
            ],
            verifier_decision="confirm",
            verifier_reason="case insensitive match",
        ),
    )

    assert guarded.seizure_frequency == ["1 per 1 week"]
    assert guarded.seizure_frequency_evidence == [
        "She thinks that she has about one a week"  # recovered capitalized 'She'
    ]
    assert "evidence_not_in_note" not in guarded.frequency_verifier_flags


def test_s5_stack_components_expose_medication_guard_and_verifier_metadata():
    record = load_exect_gold_document("EA0008")
    pred = dspy.Prediction(
        annotated_medication=["lamotrigine", "amitriptyline"],
        annotated_medication_evidence=["lamotrigine 75mg bd", "amitriptyline"],
        frequency_verifier_flags=["missing_evidence"],
        frequency_verifier_decision="repair",
        frequency_verifier_reason="drop unsupported label",
    )
    initial_values = [
        ExtractedValue(field_name="annotated_medication", raw_value="amitriptyline")
    ]

    values = apply_exect_s5_annotated_medication_guard(
        values=initial_values,
        pred=pred,
        record=record,
        program_variant=EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
    )
    metadata = build_exect_s5_stack_metadata(
        pred=pred,
        note_text=record.text,
        program_variant=EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_V2B_VARIANT,
    )

    assert [
        value.normalized_value
        for value in values
        if value.field_name == "annotated_medication"
    ] == ["lamotrigine"]
    assert metadata["post_guard"]["annotated_medication"] == (
        "exect.medication.am_guard_non_asm_brand_alias.v1"
    )
    assert metadata["frequency_verifier"]["primitive_id"] == (
        "exect.frequency.evidence_verify_policy.v2b"
    )


def test_build_exect_s5_core_family_signature_includes_policy_examples():
    signature = build_exect_s5_core_family_specific_signature("seizure_frequency")
    doc = signature.__doc__ or ""
    assert "Boundary examples:" in doc
    assert "s4_seizure_frequency_dual_cardinal_template" in doc


def test_build_exect_s4_module_returns_s5_core_parallel_wrapper():
    module = build_exect_s4_module(EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT)
    assert isinstance(module, ExectS5CoreFieldFamilyParallelV2bModule)


def test_s5_core_parallel_module_uses_full_note_context_and_six_calls():
    record = load_exect_gold_document("EA0008")
    dspy.configure(
        lm=DummyLM(
            answers=[
                {
                    "reasoning": "Diagnosis explicit.",
                    "diagnosis": ["symptomatic structural focal epilepsy"],
                    "diagnosis_evidence": ["Diagnosis: symptomatic structural focal epilepsy"],
                },
                {
                    "reasoning": "Seizure type explicit.",
                    "seizure_type": ["focal-seizures-with-altered-awareness"],
                    "seizure_type_evidence": ["focal-seizures-with-altered-awareness"],
                },
                {
                    "reasoning": "Medication explicit.",
                    "annotated_medication": ["Lamotrigine"],
                    "annotated_medication_evidence": ["lamotrigine"],
                },
                {
                    "reasoning": "Investigation explicit.",
                    "investigation": ["mri abnormal"],
                    "investigation_evidence": ["MRI brain showed mesial temporal sclerosis"],
                },
                {
                    "reasoning": "Frequency explicit.",
                    "seizure_frequency": ["1 per 3 week"],
                    "seizure_frequency_evidence": ["every 3 weeks"],
                },
                {
                    "seizure_frequency": ["1 per 3 week"],
                    "seizure_frequency_evidence": ["every 3 weeks"],
                    "verifier_decision": "confirm",
                    "verifier_reason": "supported",
                },
            ]
        )
    )

    prediction_set = predict_exect_s4_records(
        build_exect_s4_module(EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT,
        schema_level="exect_s5_core_field_family",
    )

    assert (
        stage_graph_id_for_s5_program_variant(EXECT_S5_CORE_FIELD_FAMILY_PARALLEL_V2B_VARIANT)
        == "g2_s5_core_family_parallel"
    )
    assert len(dspy.settings.lm.history) == 6
    for call in dspy.settings.lm.history[:5]:
        prompt = call["messages"][-1]["content"]
        assert record.text in prompt
        assert "Prior extractions from earlier prompt-graph stages:" not in prompt

    metadata = prediction_set.predictions[0].metadata
    assert metadata["frequency_verifier"]["primitive_id"] == (
        "exect.frequency.evidence_verify_policy.v2b"
    )
    field_names = {value.field_name for value in prediction_set.predictions[0].values}
    assert field_names <= {
        "diagnosis",
        "seizure_type",
        "annotated_medication",
        "investigation",
        "seizure_frequency",
    }

