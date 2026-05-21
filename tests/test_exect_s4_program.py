import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.programs.exect_s4 import (
    EXECT_S4_FIELD_FAMILIES,
    EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
    EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
    EXECT_S4_LABEL_POLICY_GUIDANCE,
    EXECT_S4_PROMPT_VERSION,
    EXECT_S4_SCHEMA_LEVEL,
    EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
    EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
    EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
    EXECT_S4_VARIANT,
    ExectS4FieldFamilyModule,
    ExectS4FrequencyPreVocabFieldFamilyModule,
    build_exect_s4_module,
    build_precomputed_seizure_frequency_candidates,
    format_note_with_precomputed_seizure_frequency_candidates,
    _recover_s4_investigation_raw_values,
    _recover_s4_medication_temporality_raw_values,
    _recover_s4_seizure_frequency_raw_values,
    _recover_s4_seizure_frequency_values,
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


def test_build_exect_s4_module_returns_frequency_pre_vocab_single_pass():
    module = build_exect_s4_module(EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT)
    assert isinstance(module, ExectS4FrequencyPreVocabFieldFamilyModule)


def test_build_exect_s4_module_returns_same_single_pass_for_temporality_post_classifier():
    module = build_exect_s4_module(EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT)
    assert isinstance(module, ExectS4FieldFamilyModule)


def test_build_exect_s4_module_returns_same_single_pass_for_mt_non_asm_guard():
    module = build_exect_s4_module(EXECT_S4_MT_GUARD_NON_ASM_VARIANT)
    assert isinstance(module, ExectS4FieldFamilyModule)


def test_build_exect_s4_module_returns_same_single_pass_for_frequency_post_merge():
    module = build_exect_s4_module(EXECT_S4_FREQUENCY_POST_MERGE_VARIANT)
    assert isinstance(module, ExectS4FieldFamilyModule)


def test_recover_s4_seizure_frequency_values_post_merge_abstains_without_note_support():
    recovered, flags = _recover_s4_seizure_frequency_values(
        ["seizure free"],
        "Current medication: lamotrigine 75mg bd.",
        program_variant=EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
    )
    assert recovered == []
    assert "s4_bridge:spurious_seizure_free_removed" in flags


def test_recover_s4_seizure_frequency_values_control_skips_post_merge():
    recovered, flags = _recover_s4_seizure_frequency_values(
        ["1 per 3 week"],
        "He has about one focal seizure every three weeks.",
        program_variant=EXECT_S4_VARIANT,
    )
    assert recovered == ["1 per 3 week"]
    assert "s4_bridge:note_anchored_frequency_merged" not in flags


def test_predict_exect_s4_temporality_post_classifier_applies_evidence_aligned_recovery():
    record = load_exect_gold_document("EA0008")
    dspy.configure(
        lm=DummyLM(
            answers=[
                {
                    "reasoning": "Post-classifier arm.",
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
                    "birth_history": [],
                    "birth_history_evidence": [],
                    "onset": [],
                    "onset_evidence": [],
                    "epilepsy_cause": [],
                    "epilepsy_cause_evidence": [],
                    "when_diagnosed": [],
                    "when_diagnosed_evidence": [],
                    "seizure_frequency": [],
                    "seizure_frequency_evidence": [],
                    "medication_temporality": ["lamotrigine|planned", "thyroxine|current"],
                    "medication_temporality_evidence": [
                        "Current medication: lamotrigine 75mg bd as detailed below to reduce",
                        "thyroxine 100mcg",
                    ],
                }
            ]
        )
    )

    prediction_set = predict_exect_s4_records(
        build_exect_s4_module(EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
    )

    temporality = [
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "medication_temporality"
    ]
    assert temporality == ["lamotrigine|current"]
    assert prediction_set.predictions[0].metadata["post_classifier"][
        "medication_temporality"
    ] == "exect.medication_temporality.post_classifier.v1"


def test_predict_exect_s4_mt_non_asm_guard_drops_non_asm_keeps_asm_status():
    record = load_exect_gold_document("EA0008")
    dspy.configure(
        lm=DummyLM(
            answers=[
                {
                    "reasoning": "G0 non-ASM guard arm.",
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
                    "birth_history": [],
                    "birth_history_evidence": [],
                    "onset": [],
                    "onset_evidence": [],
                    "epilepsy_cause": [],
                    "epilepsy_cause_evidence": [],
                    "when_diagnosed": [],
                    "when_diagnosed_evidence": [],
                    "seizure_frequency": [],
                    "seizure_frequency_evidence": [],
                    "medication_temporality": [
                        "lamotrigine|planned",
                        "thyroxine|current",
                    ],
                    "medication_temporality_evidence": [
                        "lamotrigine 75mg bd",
                        "thyroxine 100mcg",
                    ],
                }
            ]
        )
    )

    prediction_set = predict_exect_s4_records(
        build_exect_s4_module(EXECT_S4_MT_GUARD_NON_ASM_VARIANT),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
    )

    temporality = [
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "medication_temporality"
    ]
    assert temporality == ["lamotrigine|planned"]
    assert prediction_set.predictions[0].metadata["post_guard"][
        "medication_temporality"
    ] == "exect.medication_temporality.non_asm_guard.v1"


def test_build_precomputed_seizure_frequency_candidates_from_note_text():
    note = (
        "He has about one focal seizure every three weeks and the frequency has increased. "
        "He remains seizure free since 2017 on good days."
    )
    candidates = build_precomputed_seizure_frequency_candidates(note)

    assert "1 per 3 week" in candidates
    assert "frequency increased" in candidates


def test_format_note_with_precomputed_seizure_frequency_candidates_omits_other_families():
    record = load_exect_gold_document("EA0008")
    formatted = format_note_with_precomputed_seizure_frequency_candidates(record.text)

    assert "Precomputed benchmark-facing candidates" in formatted
    assert "seizure_frequency:" in formatted
    assert "annotated_medication:" not in formatted
    assert "diagnosis:" not in formatted
    assert formatted.endswith(record.text)


def test_predict_exect_s4_frequency_pre_vocab_records_candidate_metadata():
    record = load_exect_gold_document("EA0008")
    dspy.configure(
        lm=DummyLM(
            answers=[
                {
                    "reasoning": "Frequency hints only.",
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
                    "birth_history": [],
                    "birth_history_evidence": [],
                    "onset": [],
                    "onset_evidence": [],
                    "epilepsy_cause": [],
                    "epilepsy_cause_evidence": [],
                    "when_diagnosed": [],
                    "when_diagnosed_evidence": [],
                    "seizure_frequency": ["1 per 3 week"],
                    "seizure_frequency_evidence": ["one every three weeks"],
                    "medication_temporality": [],
                    "medication_temporality_evidence": [],
                }
            ]
        )
    )

    prediction_set = predict_exect_s4_records(
        build_exect_s4_module(EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
    )

    metadata = prediction_set.predictions[0].metadata
    assert metadata["program_variant"] == EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT
    assert "seizure_frequency" in metadata["precomputed_candidates"]


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
