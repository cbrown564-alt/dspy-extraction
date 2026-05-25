import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.exect import load_exect_gold_document
from clinical_extraction.programs.exect_s2 import (
    EXECT_S2_CLEAN_LADDER_V1_VARIANT,
    EXECT_S2_COMORBIDITY_C0_C1_VARIANT,
    EXECT_S2_COMORBIDITY_C0_VARIANT,
    EXECT_S2_FIELD_FAMILIES,
    EXECT_S2_INV_GUARD_I0_VARIANT,
    EXECT_S2_LABEL_POLICY_GUIDANCE,
    EXECT_S2_PROMPT_VERSION,
    EXECT_S2_SCHEMA_LEVEL,
    EXECT_S2_VARIANT,
    ExectS2FieldFamilyModule,
    _augment_s2_comorbidity_from_note,
    _recover_s2_comorbidity_raw_values,
    _recover_s2_investigation_raw_values,
    _recover_s2_seizure_raw_values,
    _s2_bridge_tiers,
    predict_exect_s2_records,
)


@pytest.fixture(autouse=True)
def reset_dspy_settings():
    yield
    dspy.settings.configure(lm=None)


def test_exect_s2_module_maps_prediction_to_five_field_families():
    record = load_exect_gold_document("EA0007")
    dspy.configure(
        lm=DummyLM(
            answers=[
                {
                    "reasoning": "The note names MRI normal and diabetes.",
                    "diagnosis": [],
                    "diagnosis_evidence": [],
                    "seizure_type": [],
                    "seizure_type_evidence": [],
                    "annotated_medication": [],
                    "annotated_medication_evidence": [],
                    "investigation": ["MRI normal"],
                    "investigation_evidence": ["MRI was normal"],
                    "comorbidity": ["diabetes"],
                    "comorbidity_evidence": ["diabetes"],
                }
            ]
        )
    )

    prediction_set = predict_exect_s2_records(
        ExectS2FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    assert prediction_set.schema_level == EXECT_S2_SCHEMA_LEVEL
    assert prediction_set.metadata["program_variant"] == EXECT_S2_VARIANT
    fields = {value.field_name for value in prediction_set.predictions[0].values}
    assert fields <= set(EXECT_S2_FIELD_FAMILIES)
    assert "investigation" in fields
    assert "comorbidity" in fields


def test_exect_s2_label_policy_extends_s1_guidance():
    assert EXECT_S2_PROMPT_VERSION == "exect_s2_field_family_v1_3_label_policy"
    assert any("multi-family pass" in rule.lower() for rule in EXECT_S2_LABEL_POLICY_GUIDANCE)
    assert any("investigation" in rule.lower() for rule in EXECT_S2_LABEL_POLICY_GUIDANCE)
    assert any("comorbidity" in rule.lower() for rule in EXECT_S2_LABEL_POLICY_GUIDANCE)
    assert any("impaired awareness" in rule.lower() for rule in EXECT_S2_LABEL_POLICY_GUIDANCE)
    assert any("meningioma surgery" in rule.lower() for rule in EXECT_S2_LABEL_POLICY_GUIDANCE)
    assert any("jerk" in rule.lower() for rule in EXECT_S2_LABEL_POLICY_GUIDANCE)
    assert any("family history" in rule.lower() for rule in EXECT_S2_LABEL_POLICY_GUIDANCE)


def test_recover_s2_seizure_raw_values_restores_cap25_regression_surfaces():
    note = (
        "Seizure type and frequency: focal seizures with altered awareness every 3 weeks. "
        "She also has generalized tonic clonic seizures."
    )
    recovered, flags = _recover_s2_seizure_raw_values(
        [
            "focal seizures with impaired awareness",
            "generalized tonic clonic seizure",
            "absence seizures",
            "focal aware seizure",
        ],
        note,
    )
    assert recovered == [
        "focal seizures with altered awareness",
        "generalized tonic clonic seizures",
    ]
    assert "s2_bridge:altered_awareness_restored" in flags
    assert "s2_bridge:gtcs_plural_restored" in flags
    assert "s2_bridge:absence_without_note_support_removed" in flags
    assert "s2_bridge:ilae_surface_removed" in flags


def test_recover_s2_comorbidity_raw_values_atomizes_stroke_and_strips_modifiers():
    note = (
        "History: CVA with right hemiparesis. Prior infarct. "
        "Apart from the previous stroke, he is well. Moderate learning difficulties."
    )
    recovered, flags = _recover_s2_comorbidity_raw_values(
        ["stroke", "moderate learning difficulties", "trisomy 21", "episodic migraine"],
        note,
    )
    assert recovered == [
        "cva",
        "hemiparesis",
        "infarct",
        "stroke",
        "learning difficulties",
        "trisomy",
        "migraine",
    ]
    assert "s2_bridge:stroke_atomized" in flags
    assert "s2_bridge:learning_difficulties_modifier_stripped" in flags
    assert "s2_bridge:trisomy_specificity_restored" in flags
    assert "s2_bridge:episodic_migraine_normalized" in flags


def test_recover_s2_comorbidity_raw_values_restores_meningioma_surgery_and_drops_seizure_history():
    note = "Previous meningioma resection 3rd January 2005."
    recovered, flags = _recover_s2_comorbidity_raw_values(
        ["meningioma", "febrile seizure"],
        note,
    )
    assert recovered == ["meningioma surgery"]
    assert "s2_bridge:meningioma_surgery_restored" in flags
    assert "s2_bridge:seizure_history_comorbidity_removed" in flags


def test_recover_s2_comorbidity_raw_values_drops_seizure_context_jerk_but_keeps_follow_up_jerks():
    jme_note = (
        "Chronic seizures, absences and myoclonic jerks since teenage years, JME. "
        "Medication: levetiracetam."
    )
    recovered, flags = _recover_s2_comorbidity_raw_values(["jerk", "myoclonic jerk"], jme_note)
    assert recovered == []
    assert "s2_bridge:seizure_descriptor_jerk_removed" in flags

    follow_up_note = "Lisa continues to get jerks several times a day. She also gets tonic jerks."
    recovered, flags = _recover_s2_comorbidity_raw_values(["jerk"], follow_up_note)
    assert recovered == ["jerk"]


def test_recover_s2_comorbidity_raw_values_normalizes_meningioma_resection_and_drops_family_history():
    note = "Previous meningioma resection. Family history of epilepsy."
    recovered, flags = _recover_s2_comorbidity_raw_values(
        ["meningioma resection", "family history of epilepsy"],
        note,
    )
    assert recovered == ["meningioma surgery"]
    assert "s2_bridge:meningioma_surgery_restored" in flags
    assert "s2_bridge:seizure_history_comorbidity_removed" in flags


def test_augment_s2_comorbidity_from_note_does_not_add_jerk_from_myoclonic_cluster():
    note = "She has absences and myoclonic jerks since teenage years."
    recovered, flags = _augment_s2_comorbidity_from_note([], note)
    assert "jerk" not in recovered
    assert "s2_bridge:comorbidity_note_recall_augmented" not in flags


def test_augment_s2_comorbidity_from_note_recalls_brain_atrophy_from_premature_atrophy_wording():
    note = "MRI brain scan shows some premature atrophy and white matter hyperintensities."
    recovered, flags = _augment_s2_comorbidity_from_note(["learning difficulties"], note)
    assert "brain atrophy" in recovered
    assert "s2_bridge:comorbidity_note_recall_augmented" in flags


def test_augment_s2_comorbidity_from_note_recalls_affirmed_history_and_skips_negated_mentions():
    note = (
        "Diagnosis: symptomatic structural epilepsy secondary probably caused by early life meningitis. "
        "Investigations: MRI generalised brain atrophy. "
        "She did not have any febrile seizures, meningitis or significant head injury."
    )
    recovered, flags = _augment_s2_comorbidity_from_note(["learning difficulties"], note)
    assert "meningitis" in recovered
    assert "brain atrophy" in recovered
    assert recovered.count("meningitis") == 1
    assert "s2_bridge:comorbidity_note_recall_augmented" in flags


def test_recover_s2_investigation_raw_values_drops_unknown_without_note():
    recovered, flags = _recover_s2_investigation_raw_values(
        ["mri unknown", "eeg normal"],
        "Investigations: EEG normal.",
    )
    assert recovered == ["eeg normal"]
    assert "s2_bridge:investigation_unknown_removed" in flags


def test_recover_s2_comorbidity_c0_atomizes_traumatic_brain_injury():
    note = (
        "Past medical history: traumatic brain injury from road traffic accident. "
        "Epilepsy secondary to traumatic brain injury."
    )
    tiers = _s2_bridge_tiers(EXECT_S2_COMORBIDITY_C0_VARIANT)
    recovered, flags = _recover_s2_comorbidity_raw_values(
        ["traumatic brain injury"],
        note,
        bridge_tiers=tiers,
    )
    assert recovered == ["traumatic", "brain injury"]
    assert "s2_bridge:tbi_atomized" in flags


def test_recover_s2_comorbidity_c0_c1_normalizes_haemorrhage_spelling():
    note = "History of intracerebral haemorrhage and prior infarcts."
    tiers = _s2_bridge_tiers(EXECT_S2_COMORBIDITY_C0_C1_VARIANT)
    recovered, flags = _recover_s2_comorbidity_raw_values(
        ["intracerebral haemorrhage", "infarcts"],
        note,
        bridge_tiers=tiers,
    )
    assert "intracerebral hemorrhage" in recovered
    assert "infarct" in recovered
    assert "s2_bridge:haemorrhage_spelling_normalized" in flags
    assert "s2_bridge:infarct_plural_normalized" in flags


def test_recover_s2_comorbidity_c1_preserves_learning_disabilities():
    note = "She has mild learning disabilities."
    tiers = _s2_bridge_tiers(EXECT_S2_COMORBIDITY_C0_C1_VARIANT)
    recovered, flags = _recover_s2_comorbidity_raw_values(
        ["mild learning disabilities"],
        note,
        bridge_tiers=tiers,
    )
    assert recovered == ["learning disabilities"]
    assert "s2_bridge:learning_disabilities_modifier_stripped" in flags


def test_recover_s2_investigation_i0_drops_ecg():
    note = "Investigations: ECG normal. EEG normal."
    tiers = _s2_bridge_tiers(EXECT_S2_INV_GUARD_I0_VARIANT)
    recovered, flags = _recover_s2_investigation_raw_values(
        ["ecg normal", "eeg normal"],
        note,
        bridge_tiers=tiers,
    )
    assert recovered == ["eeg normal"]
    assert "s2_bridge:investigation_ecg_removed" in flags


def test_exect_s2_clean_ladder_variant_combines_low_risk_guards():
    tiers = _s2_bridge_tiers(EXECT_S2_CLEAN_LADDER_V1_VARIANT)

    assert "comorbidity_atomization_tbi_v1" in tiers
    assert "comorbidity_surface_plural_v1" in tiers
    assert "inv_guard_drop_ecg_v1" in tiers
    assert "annotated_medication_non_asm_brand_alias_v1" in tiers
