import dspy
from dspy.utils import DummyLM

from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.programs.exect_s4 import (
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
    ExectS5FrequencyPreVocabAmGuardFrequencyVerifyModule,
    _apply_exect_s5_frequency_verifier_guards,
    build_exect_s4_module,
    predict_exect_s4_records,
)


def test_frequency_verifier_guard_blocks_added_labels_and_candidate_echo():
    guarded = _apply_exect_s5_frequency_verifier_guards(
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
    guarded = _apply_exect_s5_frequency_verifier_guards(
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
    guarded = _apply_exect_s5_frequency_verifier_guards(
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
    guarded = _apply_exect_s5_frequency_verifier_guards(
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

