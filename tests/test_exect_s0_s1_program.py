import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.exect import load_exect_gold_document, load_exect_gold_documents
from clinical_extraction.exect.s0_s1.metrics import (
    exect_s0_s1_field_family_micro_f1_raw_metric,
)
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
    EXECT_S0_S1_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
    EXECT_S0_S1_FIELD_FAMILIES,
    EXECT_S0_S1_LABEL_POLICY_GUIDANCE,
    EXECT_S0_S1_POLICY_EXAMPLES,
    EXECT_S0_S1_V4_11_POLICY_EXAMPLES,
    EXECT_S0_S1_V4_12_POLICY_EXAMPLES,
    EXECT_S0_S1_V4_12_PROMPT_VERSION,
    EXECT_S0_S1_V4_11_PROMPT_VERSION,
    EXECT_S0_S1_V4_10_EVIDENCE_SOFT_PROMPT_VERSION,
    EXECT_S0_S1_V4_10_EVIDENCE_STRICT_PROMPT_VERSION,
    EXECT_S0_S1_VERIFY_REPAIR_PROMPT_VERSION,
    EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
    EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT,
    EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT,
    EXECT_S0_S1_D1_PROMPT_VERSION,
    EXECT_S0_S1_L0_PROMPT_VERSION,
    EXECT_S0_S1_L1_SCHEMA_PROMPT_VERSION,
    ExectS0S1DeterministicOnlyModule,
    ExectS0S1L0MinimalSignature,
    ExectS0S1L1SchemaSignature,
    build_exect_s0_s1_field_family_signature,
    extract_d1_field_family_surfaces,
    resolve_exect_s0_s1_extraction_prompt_version,
    resolve_exect_s0_s1_label_policy,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT,
    EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT,
    EXECT_S0_S1_VARIANT,
    ExectS0S1DiagnosisRecallProbeModule,
    ExectS0S1MedicationPreVocabFieldFamilyModule,
    ExectS0S1SeizurePreVocabFieldFamilyModule,
    ExectS0S1PreVocabFieldFamilyModule,
    ExectS0S1VerifyRepairModule,
    ExectS0S1FieldFamilySignature,
    ExectS0S1FieldFamilyModule,
    ExectS1CleanLadderDiagnosisStableEnsembleModule,
    ExectS0S1SectionAwareFieldFamilyModule,
    ExectS0S1FieldFamilyPromptGraphParallelModule,
    ExectS0S1FieldFamilyPromptGraphSequentialModule,
    build_exect_s0_s1_family_specific_signature,
    stage_graph_id_for_program_variant,
    EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
    EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
    REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY,
    REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES,
    build_exect_s0_s1_module,
    build_precomputed_family_candidates,
    compile_exect_s0_s1_module,
    exect_s0_s1_field_family_micro_f1_metric,
    exect_s0_s1_run_metadata,
    format_note_with_precomputed_family_candidates,
    format_note_with_precomputed_medication_candidates,
    format_note_with_precomputed_seizure_type_candidates,
    build_precomputed_seizure_type_candidates,
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


def test_exect_s0_s1_boundary_surfaces_expose_diagnosis_specificity_collapse():
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

    surfaces = prediction_set.predictions[0].metadata["s1_boundary_surfaces"]
    assert surfaces["boundary_version"] == "exect_s1_boundary_surfaces.v1"
    assert [item["raw_value"] for item in surfaces["raw_model_outputs"]["diagnosis"]] == [
        "epilepsy",
        "juvenile-myoclonic-epilepsy",
    ]

    bridge_rows = surfaces["deterministic_bridge_values"]["diagnosis"]
    dropped_parent = next(item for item in bridge_rows if item["raw_value"] == "epilepsy")
    kept_specific = next(
        item
        for item in bridge_rows
        if item["benchmark_value"] == "juvenile myoclonic epilepsy"
    )

    assert dropped_parent["bridge_status"] == "dropped"
    assert dropped_parent["benchmark_value"] is None
    assert kept_specific["bridge_status"] == "kept"
    assert "specificity_collapsed" in kept_specific["bridge_flags"]
    assert [
        item["normalized_value"]
        for item in surfaces["final_artifact_values"]["diagnosis"]
    ] == ["juvenile myoclonic epilepsy"]


def test_exect_s0_s1_bridge_does_not_infer_seizure_type_from_diagnosis():
    record = load_exect_gold_document("EA0142")
    _configure_dummy([{
        "reasoning": "Diagnosis alone is not a seizure type output.",
        "diagnosis": ["focal epilepsy"],
        "diagnosis_evidence": ["Diagnosis: focal epilepsy"],
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

    field_names = {
        value.field_name for value in prediction_set.predictions[0].values
    }
    assert "seizure_type" not in field_names
    assert "diagnosis" in field_names


def test_exect_s0_s1_prompt_policy_covers_benchmark_boundary_cases():
    policy_text = " ".join(EXECT_S0_S1_LABEL_POLICY_GUIDANCE).lower()
    signature_text = ExectS0S1FieldFamilySignature.__doc__.lower()
    example_cases = {example["case"] for example in EXECT_S0_S1_POLICY_EXAMPLES}

    assert EXECT_S0_S1_PROMPT_VERSION == "exect_s0_s1_field_family_v4_10_label_policy"
    assert "planned starts" in policy_text
    assert "previous trials" in policy_text
    assert "focal seizures with altered awareness" in policy_text
    assert "single seizure event" in policy_text
    assert "symptomatic structural focal epilepsy" in signature_text
    assert "secondary generalisation" in policy_text
    assert "focal to bilateral convulsive" in policy_text
    assert "hydrocephalus" in signature_text
    assert {
        "planned_medication_exclusion",
        "previous_medication_exclusion",
        "canonical_seizure_type_granularity",
        "diagnosis_label_preservation",
        "plural_seizure_type_preservation",
        "evidence_quote_contiguity",
        "single_event_diagnosis_null",
        "secondary_generalisation_split",
        "focal_to_bilateral_convulsive_modifier",
        "diagnosis_uncertainty_stripping",
        "cross_family_diagnosis_exclusion",
        "symptomatic_structural_focal_preservation",
        "temporal_lobe_seizures_split_pair",
        "focal_to_bilateral_annotation_surface",
        "coarse_generalized_seizure_surface",
        "on_awakening_diagnosis_phrasing",
        "from_sleep_header_to_on_awakening_diagnosis",
        "co_listed_lobe_epilepsy_diagnoses",
        "reject_granular_jme_seizure_descriptors",
        "jme_coarse_gtcs_suppresses_myoclonic",
        "jme_tonic_clonic_surface_without_generalized_prefix",
        "jme_generalized_tonic_seizures_without_clonic",
        "dissociative_epileptic_seizure_routing",
        "specificity_collapse_diagnosis_co_list",
        "specificity_collapse_secondary_seizure_surface",
        "secondary_token_co_list_with_full_phrase",
        "current_prescription_with_taper_parenthetical",
        "myoclonic_jerks_to_myoclonic_seizures",
        "non_asm_medication_exclusion",
        "empty_medication_without_prescription_list",
        "prescription_request_exclusion",
        "planned_switch_exclusion",
        "taper_stop_exclusion",
        "restart_advice_after_self_stop",
        "brand_lamictal_preservation",
        "brand_epilim_chrono_preservation",
        "generic_epilepsy_co_list_with_focal_onset",
        "focal_onset_and_focal_epilepsy_co_list",
        "generic_epilepsy_co_list_with_primary_generalized",
        "unclassified_epilepsy_header",
        "possible_tle_header_preserves_temporal_lobe_epilepsy",
    }.issubset(example_cases)


def test_exect_s0_s1_v4_11_label_policy_addendum_targets_qwen_gap_modes():
    guidance, examples = resolve_exect_s0_s1_label_policy(EXECT_S0_S1_V4_11_PROMPT_VERSION)
    guidance_text = " ".join(guidance).lower()
    example_cases = {example["case"] for example in examples}

    assert len(guidance) > len(EXECT_S0_S1_LABEL_POLICY_GUIDANCE)
    assert "plural audited benchmark surface" in guidance_text
    assert "do not emit absence seizure" in guidance_text
    assert "bare secondary alone" in guidance_text
    assert {
        "plural_gtcs_from_diagnosis_row",
        "plural_focal_to_bilateral_convulsive",
        "no_seizure_types_without_absence_myoclonic_overcall",
        "gtcs_only_no_absence_co_list",
        "secondary_generalisation_full_phrase",
        "secondary_generalized_seizures_not_bare_secondary",
        "multi_type_secondary_generalized_co_list",
    }.issubset(example_cases)
    assert len(EXECT_S0_S1_V4_11_POLICY_EXAMPLES) == 7


def test_exect_s0_s1_v4_11_signature_extends_v4_10_boundary_doc():
    v4_11_signature = build_exect_s0_s1_field_family_signature(EXECT_S0_S1_V4_11_PROMPT_VERSION)
    doc = (v4_11_signature.__doc__ or "").lower()
    assert "generalized tonic clonic seizures" in doc
    assert "secondary generalisation" in doc
    assert "do not invent absence" in doc


def test_exect_s0_s1_v4_12_label_policy_stabilizes_qwen_diagnosis_drift():
    guidance, examples = resolve_exect_s0_s1_label_policy(EXECT_S0_S1_V4_12_PROMPT_VERSION)
    guidance_text = " ".join(guidance).lower()
    example_cases = {example["case"] for example in examples}

    assert len(guidance) > len(resolve_exect_s0_s1_label_policy(EXECT_S0_S1_V4_11_PROMPT_VERSION)[0])
    assert "v4.11 seizure-type rules only inside seizure_type" in guidance_text
    assert "do not replace a generic epilepsy gold surface with focal epilepsy" in guidance_text
    assert "do not emit symptomatic structural focal epilepsy from mri lesions" in guidance_text
    assert {
        "plural_gtcs_from_diagnosis_row",
        "secondary_generalized_seizures_not_bare_secondary",
        "diagnosis_generic_epilepsy_not_focal_from_seizure_context",
        "diagnosis_no_structural_overcall_from_mri_context",
        "diagnosis_focal_onset_recall_kept",
    }.issubset(example_cases)
    assert len(EXECT_S0_S1_V4_12_POLICY_EXAMPLES) == 3


def test_exect_s0_s1_v4_12_signature_extends_v4_11_with_diagnosis_boundaries():
    v4_12_signature = build_exect_s0_s1_field_family_signature(EXECT_S0_S1_V4_12_PROMPT_VERSION)
    doc = (v4_12_signature.__doc__ or "").lower()
    assert "generalized tonic clonic seizures" in doc
    assert "do not upgrade generic epilepsy to focal epilepsy" in doc
    assert "do not infer symptomatic structural focal epilepsy" in doc


def test_exect_s0_s1_evidence_policy_signatures_keep_v4_10_label_policy():
    strict_guidance, strict_examples = resolve_exect_s0_s1_label_policy(
        EXECT_S0_S1_V4_10_EVIDENCE_STRICT_PROMPT_VERSION
    )
    soft_guidance, soft_examples = resolve_exect_s0_s1_label_policy(
        EXECT_S0_S1_V4_10_EVIDENCE_SOFT_PROMPT_VERSION
    )
    assert strict_guidance == EXECT_S0_S1_LABEL_POLICY_GUIDANCE
    assert soft_guidance == EXECT_S0_S1_LABEL_POLICY_GUIDANCE
    assert strict_examples == EXECT_S0_S1_POLICY_EXAMPLES
    assert soft_examples == EXECT_S0_S1_POLICY_EXAMPLES

    strict_doc = (
        build_exect_s0_s1_field_family_signature(
            EXECT_S0_S1_V4_10_EVIDENCE_STRICT_PROMPT_VERSION
        ).__doc__
        or ""
    ).lower()
    soft_doc = (
        build_exect_s0_s1_field_family_signature(
            EXECT_S0_S1_V4_10_EVIDENCE_SOFT_PROMPT_VERSION
        ).__doc__
        or ""
    ).lower()
    assert "evidence policy (strict" in strict_doc
    assert "evidence policy (soft diagnostic" in soft_doc


def test_resolve_exect_s0_s1_extraction_prompt_version_maps_verify_repair():
    assert (
        resolve_exect_s0_s1_extraction_prompt_version(EXECT_S0_S1_VERIFY_REPAIR_PROMPT_VERSION)
        == EXECT_S0_S1_PROMPT_VERSION
    )


def test_ladder_prompt_versions_strip_embedded_label_policy():
    for prompt_version in (
        EXECT_S0_S1_L0_PROMPT_VERSION,
        EXECT_S0_S1_L1_SCHEMA_PROMPT_VERSION,
        EXECT_S0_S1_D1_PROMPT_VERSION,
    ):
        guidance, examples = resolve_exect_s0_s1_label_policy(prompt_version)
        assert guidance == ()
        assert examples == ()


def test_ladder_l0_and_l1_signatures_are_minimal_compared_to_v4_10():
    l0_doc = (build_exect_s0_s1_field_family_signature(EXECT_S0_S1_L0_PROMPT_VERSION).__doc__ or "")
    l1_doc = (build_exect_s0_s1_field_family_signature(EXECT_S0_S1_L1_SCHEMA_PROMPT_VERSION).__doc__ or "")
    v4_doc = (ExectS0S1FieldFamilySignature.__doc__ or "")
    assert len(l0_doc) < len(v4_doc) // 2
    assert len(l1_doc) < len(v4_doc) // 2
    assert "boundary examples" not in l0_doc.lower()
    assert build_exect_s0_s1_field_family_signature(EXECT_S0_S1_L0_PROMPT_VERSION) is ExectS0S1L0MinimalSignature
    assert build_exect_s0_s1_field_family_signature(EXECT_S0_S1_L1_SCHEMA_PROMPT_VERSION) is ExectS0S1L1SchemaSignature


def test_d1_field_family_extraction_uses_note_anchored_surfaces():
    record = load_exect_gold_document("EA0008")
    surfaces = extract_d1_field_family_surfaces(record.text)
    assert "lamotrigine" in surfaces["annotated_medication"]
    module = ExectS0S1DeterministicOnlyModule()
    pred = module(note_text=record.text)
    assert list(getattr(pred, "annotated_medication", [])) == surfaces["annotated_medication"]


def test_predict_exect_records_d1_variant_skips_benchmark_bridges():
    record = load_exect_gold_document("EA0008")
    module = build_exect_s0_s1_module(
        EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
        prompt_version=EXECT_S0_S1_D1_PROMPT_VERSION,
        include_archive=True,
    )
    prediction_set = predict_exect_records(
        module,
        [record],
        model_provider="deterministic",
        model_name="d1-feasibility",
        prompt_version=EXECT_S0_S1_D1_PROMPT_VERSION,
        program_variant=EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
        repair_policy=REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES,
    )
    prediction = prediction_set.predictions[0]
    assert prediction.metadata["apply_benchmark_bridges"] is False
    assert prediction.metadata["bridge_stage"] == "none"
    assert "d1_surfaces" in prediction.metadata


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


def test_exect_s0_s1_bridge_splits_fused_secondary_generalisation_phrase():
    record = load_exect_gold_document("EA0090")
    _configure_dummy([{
        "reasoning": "The model emitted one fused secondary-generalisation phrase.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": ["focal seizures with secondary generalisation"],
        "seizure_type_evidence": ["focal seizures with secondary generalisation"],
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
        "focal seizures",
        "secondary generalisation",
        "generalized tonic clonic seizure",
    ]
    assert all(
        "benchmark_bridge:fused_seizure_type_split" in value.quality_flags
        for value in seizure_values
    )


def test_exect_s0_s1_boundary_surfaces_expose_seizure_bridge_split():
    record = load_exect_gold_document("EA0090")
    _configure_dummy([{
        "reasoning": "The model emitted one fused secondary-generalisation phrase.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": ["focal seizures with secondary generalisation"],
        "seizure_type_evidence": ["focal seizures with secondary generalisation"],
        "annotated_medication": [],
        "annotated_medication_evidence": [],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    surfaces = prediction_set.predictions[0].metadata["s1_boundary_surfaces"]
    bridge_rows = surfaces["deterministic_bridge_values"]["seizure_type"]

    assert [item["raw_value"] for item in surfaces["raw_model_outputs"]["seizure_type"]] == [
        "focal seizures with secondary generalisation"
    ]
    assert [item["benchmark_value"] for item in bridge_rows] == [
        "focal seizures",
        "secondary generalisation",
        "generalized tonic clonic seizure",
    ]
    assert all(item["bridge_status"] == "kept" for item in bridge_rows)
    assert all(
        "benchmark_bridge:fused_seizure_type_split" in item["bridge_flags"]
        for item in bridge_rows
    )


def test_exect_s0_s1_bridge_maps_focal_onset_convulsive_to_focal_to_bilateral():
    record = load_exect_gold_document("EA0098")
    _configure_dummy([{
        "reasoning": "The note header uses focal onset convulsive seizure wording.",
        "diagnosis": ["focal onset epilepsy"],
        "diagnosis_evidence": ["Focal onset epilepsy"],
        "seizure_type": ["focal onset convulsive seizure"],
        "seizure_type_evidence": ["Focal onset convulsive seizure"],
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
    assert seizure_values[0].normalized_value == "focal to bilateral convulsive seizure"
    assert "benchmark_bridge:focal_onset_to_bilateral_surface" in (
        seizure_values[0].quality_flags
    )


def test_exect_s0_s1_bridge_augment_adds_epilepsy_with_focal_onset():
    record = load_exect_gold_document("EA0098")
    _configure_dummy([{
        "reasoning": "The model omitted generic epilepsy from the diagnosis list.",
        "diagnosis": ["focal onset epilepsy"],
        "diagnosis_evidence": ["Focal onset epilepsy"],
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
    assert {value.normalized_value for value in diagnosis_values} == {
        "focal onset epilepsy",
        "epilepsy",
    }
    epilepsy_value = next(
        value for value in diagnosis_values if value.normalized_value == "epilepsy"
    )
    assert "benchmark_bridge:diagnosis_co_list_augmented" in epilepsy_value.quality_flags


def test_exect_s0_s1_bridge_augment_adds_parietal_lobe_epilepsy():
    record = load_exect_gold_document("EA0061")
    _configure_dummy([{
        "reasoning": "The model omitted parietal lobe epilepsy from the diagnosis list.",
        "diagnosis": ["focal epilepsy"],
        "diagnosis_evidence": ["focal epilepsy"],
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
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "diagnosis"
    ]
    assert diagnosis_values == ["focal epilepsy", "parietal lobe epilepsy"]


def test_exect_s0_s1_bridge_augment_adds_focal_onset_epilepsy():
    record = load_exect_gold_document("EA0045")
    _configure_dummy([{
        "reasoning": "The model kept only the header focal epilepsy label.",
        "diagnosis": ["focal epilepsy"],
        "diagnosis_evidence": ["Focal epilepsy"],
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
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "diagnosis"
    ]
    assert diagnosis_values == ["focal epilepsy", "focal onset epilepsy"]


def test_exect_s0_s1_bridge_adds_convulsive_modifier_to_focal_to_bilateral_seizures():
    record = load_exect_gold_document("EA0061")
    _configure_dummy([{
        "reasoning": "The model omitted the convulsive modifier on bilateral seizures.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": ["focal to bilateral seizures"],
        "seizure_type_evidence": ["focal to bilateral seizures"],
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
    assert seizure_values[0].normalized_value == "focal to bilateral convulsive seizures"
    assert "benchmark_bridge:seizure_type_convulsive_modifier" in (
        seizure_values[0].quality_flags
    )


def test_exect_s0_s1_bridge_strips_probable_from_diagnosis_surface():
    record = load_exect_gold_document("EA0047")
    _configure_dummy([{
        "reasoning": "The model kept the uncertainty qualifier on the diagnosis label.",
        "diagnosis": ["probable juvenile myoclonic epilepsy"],
        "diagnosis_evidence": ["probable juvenile myoclonic epilepsy"],
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
    assert diagnosis_values[0].normalized_value == "juvenile myoclonic epilepsy"
    assert "benchmark_bridge:diagnosis_uncertainty_stripped" in (
        diagnosis_values[0].quality_flags
    )


def test_exect_s0_s1_bridge_rejects_granular_absence_and_jerk_seizure_descriptors():
    record = load_exect_gold_document("EA0047")
    _configure_dummy([{
        "reasoning": "The model emitted granular jerk/absence descriptors.",
        "diagnosis": ["juvenile myoclonic epilepsy"],
        "diagnosis_evidence": ["juvenile myoclonic epilepsy"],
        "seizure_type": ["generalized seizures", "absences", "jerks"],
        "seizure_type_evidence": ["generalized seizures", "absences", "jerks"],
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
    assert [value.normalized_value for value in seizure_values] == ["generalized seizures"]


def test_exect_s0_s1_bridge_co_lists_specificity_collapse_diagnosis_tokens():
    record = load_exect_gold_document("EA0188")
    _configure_dummy([{
        "reasoning": "The model kept lobe-specific epilepsy labels but missed collapsed tokens.",
        "diagnosis": ["focal epilepsy", "occipital lobe epilepsy"],
        "diagnosis_evidence": [
            "Focal epilepsy, probable occipital lobe onset",
            "drug refractory focal (occipital lobe) epilepsy",
        ],
        "seizure_type": ["secondary generalised seizure"],
        "seizure_type_evidence": ["secondary generalised seizure"],
        "annotated_medication": ["zonisamide", "brivaracetam"],
        "annotated_medication_evidence": ["Zonismaide 100mg bd", "brivitiracetam 50mg bd"],
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
    assert {value.normalized_value for value in diagnosis_values} == {
        "focal",
        "drug",
        "occipital",
        "focal epilepsy",
        "occipital lobe epilepsy",
    }
    collapsed_tokens = {
        value.normalized_value
        for value in diagnosis_values
        if value.normalized_value in {"focal", "drug", "occipital"}
    }
    assert collapsed_tokens == {"focal", "drug", "occipital"}
    assert any(
        "benchmark_bridge:specificity_collapse_diagnosis_co_listed"
        in value.quality_flags
        for value in diagnosis_values
        if value.normalized_value in collapsed_tokens
    )


def test_exect_s0_s1_bridge_collapses_secondary_seizure_surface_for_specificity_collapse():
    record = load_exect_gold_document("EA0188")
    _configure_dummy([{
        "reasoning": "The model emitted granular focal labels and the full secondary phrase.",
        "diagnosis": ["focal epilepsy", "occipital lobe epilepsy"],
        "diagnosis_evidence": [
            "Focal epilepsy, probable occipital lobe onset",
            "drug refractory focal (occipital lobe) epilepsy",
        ],
        "seizure_type": [
            "focal seizures",
            "focal seizures with impaired awareness",
            "secondary generalised seizures",
        ],
        "seizure_type_evidence": [
            "focal seizures",
            "focal seizures with impaired awareness",
            "secondary generalised seizure",
        ],
        "annotated_medication": ["zonisamide", "brivaracetam"],
        "annotated_medication_evidence": ["Zonismaide 100mg bd", "brivitiracetam 50mg bd"],
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
    assert [value.normalized_value for value in seizure_values] == ["secondary"]
    assert "benchmark_bridge:specificity_collapse_seizure_surface" in (
        seizure_values[0].quality_flags
    )


def test_exect_s0_s1_bridge_co_lists_secondary_token_with_full_secondary_phrase():
    record = load_exect_gold_document("EA0150")
    _configure_dummy([{
        "reasoning": "The model kept the full secondary phrase but missed the collapsed token.",
        "diagnosis": ["symptomatic structural focal epilepsy"],
        "diagnosis_evidence": ["Diagnosis: symptomatic structural focal epilepsy"],
        "seizure_type": ["complex partial seizures", "secondary generalised seizures"],
        "seizure_type_evidence": [
            "complex partial seizures",
            "secondary generalised seizures",
        ],
        "annotated_medication": ["levetiracetam", "lamotrigine", "clobazam"],
        "annotated_medication_evidence": [
            "Levetiracetam 1500mg bd",
            "Lamotrigine 200mg bd",
            "Clobazam",
        ],
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
    assert {value.normalized_value for value in seizure_values} == {
        "complex partial seizures",
        "secondary generalized seizures",
        "secondary",
    }
    secondary_values = [
        value for value in seizure_values if value.normalized_value == "secondary"
    ]
    assert len(secondary_values) == 1
    assert "benchmark_bridge:secondary_token_co_listed" in secondary_values[0].quality_flags


def test_exect_s0_s1_bridge_recovers_lamotrigine_from_current_prescription_line():
    record = load_exect_gold_document("EA0008")
    _configure_dummy([{
        "reasoning": "The model omitted medication despite a current prescription list.",
        "diagnosis": ["symptomatic structural focal epilepsy"],
        "diagnosis_evidence": ["Diagnosis: symptomatic structural focal epilepsy"],
        "seizure_type": ["focal seizures with altered awareness"],
        "seizure_type_evidence": [
            "Seizure type and frequency: focal seizures with altered awareness every 3 weeks"
        ],
        "annotated_medication": [],
        "annotated_medication_evidence": [],
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
    assert medication_values[0].normalized_value == "lamotrigine"
    assert "lamotrigine" in medication_values[0].evidence[0].text.lower()
    assert "benchmark_bridge:current_prescription_medication_augmented" in (
        medication_values[0].quality_flags
    )


def test_exect_s0_s1_boundary_surfaces_expose_current_rx_augmentation():
    record = load_exect_gold_document("EA0008")
    _configure_dummy([{
        "reasoning": "The model omitted medication despite a current prescription list.",
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

    surfaces = prediction_set.predictions[0].metadata["s1_boundary_surfaces"]
    medication_rows = surfaces["deterministic_bridge_values"]["annotated_medication"]

    assert surfaces["raw_model_outputs"]["annotated_medication"] == []
    assert [item["benchmark_value"] for item in medication_rows] == ["lamotrigine"]
    assert medication_rows[0]["bridge_status"] == "augmented"
    assert "benchmark_bridge:current_prescription_medication_augmented" in (
        medication_rows[0]["bridge_flags"]
    )
    assert [
        item["normalized_value"]
        for item in surfaces["final_artifact_values"]["annotated_medication"]
    ] == ["lamotrigine"]


def test_exect_s0_s1_bridge_routes_dissociative_contrast_to_epileptic_seizures():
    record = load_exect_gold_document("EA0135")
    _configure_dummy([{
        "reasoning": (
            "The model inferred focal seizures from focal onset epilepsy rather than "
            "the epileptic-versus-dissociative seizure conclusion."
        ),
        "diagnosis": ["focal onset epilepsy"],
        "diagnosis_evidence": ["Focal onset epilepsy"],
        "seizure_type": ["focal seizures"],
        "seizure_type_evidence": ["Focal onset epilepsy"],
        "annotated_medication": ["eslicarbazepine", "levetiracetam", "clobazam"],
        "annotated_medication_evidence": [
            "Eslicarbazepine 800mg od",
            "Levetiracetam 1750mg bd",
            "Clobazam 10mg od",
        ],
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
    assert [value.normalized_value for value in seizure_values] == ["epileptic seizures"]
    assert "benchmark_bridge:dissociative_focal_seizure_suppressed" in (
        seizure_values[0].quality_flags
    )
    assert "benchmark_bridge:epileptic_seizures_surface_restored" in (
        seizure_values[0].quality_flags
    )


def test_exect_s0_s1_bridge_suppresses_myoclonic_when_jme_coarse_gtcs_present():
    record = load_exect_gold_document("EA0048")
    _configure_dummy([{
        "reasoning": "JME with tonic clonic and jerk wording.",
        "diagnosis": ["juvenile myoclonic epilepsy"],
        "diagnosis_evidence": ["juvenile myoclonic epilepsy"],
        "seizure_type": [
            "generalized tonic clonic seizures",
            "myoclonic seizures",
        ],
        "seizure_type_evidence": [
            "tonic clonic seizures",
            "myoclonic jerks",
        ],
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
    assert [value.normalized_value for value in seizure_values] == ["tonic clonic seizures"]
    assert "benchmark_bridge:jme_myoclonic_suppressed_for_coarse_label" in (
        seizure_values[0].quality_flags
    )
    assert "benchmark_bridge:jme_tonic_clonic_surface" in seizure_values[0].quality_flags


def test_exect_s0_s1_bridge_maps_generalized_tonic_seizures_for_jme_presenting_phrase():
    record = load_exect_gold_document("EA0125")
    _configure_dummy([{
        "reasoning": "JME presenting phrase uses generalised tonic seizures.",
        "diagnosis": ["jme", "juvenile myoclonic epilepsy"],
        "diagnosis_evidence": ["probably JME", "juvenile myoclonic epilepsy"],
        "seizure_type": [
            "generalized tonic clonic seizures",
            "myoclonic seizures",
        ],
        "seizure_type_evidence": [
            "generalised tonic seizures",
            "myoclonic jerks",
        ],
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
        "generalized tonic seizures"
    ]


def test_exect_s0_s1_bridge_co_lists_singular_gtcs_when_note_uses_singular():
    record = load_exect_gold_document("EA0069")
    _configure_dummy([{
        "reasoning": "Note uses singular generalised tonic clonic seizure phrasing.",
        "diagnosis": ["juvenile myoclonic epilepsy"],
        "diagnosis_evidence": ["Juvenile Myoclonic Epilepsy"],
        "seizure_type": ["generalized tonic clonic seizures", "myoclonic seizures"],
        "seizure_type_evidence": ["generalised tonic clonic seizure", "myoclonic jerks"],
        "annotated_medication": [],
        "annotated_medication_evidence": [],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    seizure_values = sorted(
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "seizure_type"
    )
    assert seizure_values == [
        "generalized tonic clonic seizure",
        "generalized tonic clonic seizures",
    ]


def test_exect_s0_s1_bridge_co_lists_epilepsy_with_primary_generalized():
    record = load_exect_gold_document("EA0131")
    _configure_dummy([{
        "reasoning": "The model omitted generic epilepsy from the diagnosis list.",
        "diagnosis": ["primary generalized epilepsy"],
        "diagnosis_evidence": ["primary generalised epilepsy"],
        "seizure_type": ["generalized tonic clonic seizures"],
        "seizure_type_evidence": ["generalised tonic clonic seizures"],
        "annotated_medication": ["sodium valproate"],
        "annotated_medication_evidence": ["sodium valproate"],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    diagnosis_values = sorted(
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "diagnosis"
    )
    assert diagnosis_values == ["epilepsy", "primary generalized epilepsy"]


def test_exect_s0_s1_bridge_co_lists_epilepsy_with_symptomatic_structural_focal():
    record = load_exect_gold_document("EA0170")
    _configure_dummy([{
        "reasoning": "The model omitted generic epilepsy from the diagnosis list.",
        "diagnosis": ["symptomatic structural focal epilepsy"],
        "diagnosis_evidence": ["Symptomatic structural focal epilepsy"],
        "seizure_type": ["complex partial seizures"],
        "seizure_type_evidence": ["complex partial seizures"],
        "annotated_medication": ["carbamazepine"],
        "annotated_medication_evidence": ["carbamazepine"],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    diagnosis_values = sorted(
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "diagnosis"
    )
    assert diagnosis_values == ["epilepsy", "symptomatic structural focal epilepsy"]


def test_exect_s0_s1_bridge_maps_unclassified_epilepsy_surface_to_epilepsy():
    record = load_exect_gold_document("EA0148")
    _configure_dummy([{
        "reasoning": "The model used unclassified epilepsy header wording.",
        "diagnosis": ["epilepsy unclassified"],
        "diagnosis_evidence": ["epilepsy unclassified"],
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
    assert diagnosis_values[0].normalized_value == "epilepsy"
    assert "benchmark_bridge:unclassified_epilepsy_surface" in diagnosis_values[0].quality_flags


def test_exect_s0_s1_bridge_recovers_epilepsy_from_unclassified_header():
    record = load_exect_gold_document("EA0148")
    _configure_dummy([{
        "reasoning": "The model returned no diagnosis labels.",
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

    diagnosis_values = [
        value
        for value in prediction_set.predictions[0].values
        if value.field_name == "diagnosis"
    ]
    assert len(diagnosis_values) == 1
    assert diagnosis_values[0].normalized_value == "epilepsy"
    assert "benchmark_bridge:diagnosis_co_list_augmented" in diagnosis_values[0].quality_flags


def test_exect_s0_s1_bridge_recovers_epilepsy_from_en_dash_unclassified_header():
    record = load_exect_gold_document("EA0173")
    _configure_dummy([{
        "reasoning": "The model returned no diagnosis labels.",
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

    diagnosis_values = [
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "diagnosis"
    ]
    assert diagnosis_values == ["epilepsy"]


def test_exect_s0_s1_bridge_preserves_temporal_lobe_epilepsy_for_possible_tle_header():
    record = load_exect_gold_document("EA0185")
    _configure_dummy([{
        "reasoning": "The header names possible TLE alongside focal seizures.",
        "diagnosis": ["temporal lobe epilepsy"],
        "diagnosis_evidence": ["possible TLE"],
        "seizure_type": ["focal seizures"],
        "seizure_type_evidence": ["Focal seizures"],
        "annotated_medication": ["carbamazepine"],
        "annotated_medication_evidence": ["Carbamazepine"],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    diagnosis_values = [
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "diagnosis"
    ]
    assert diagnosis_values == ["temporal lobe epilepsy"]


def test_exect_s0_s1_bridge_recovers_on_awakening_diagnosis_from_sleep_header():
    record = load_exect_gold_document("EA0116")
    _configure_dummy([{
        "reasoning": "The model misfiled the syndrome phrase into seizure type.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": ["generalised tonic clonic seizures from sleep"],
        "seizure_type_evidence": [
            "New diagnosis of epilepsy with generalised tonic clonic seizures from sleep"
        ],
        "annotated_medication": ["levetiracetam"],
        "annotated_medication_evidence": ["Levetiracetam 250mgs once a day"],
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
    seizure_values = [
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "seizure_type"
    ]
    assert len(diagnosis_values) == 1
    assert diagnosis_values[0].normalized_value == (
        "epilepsy with generalized tonic clonic seizures on awakening"
    )
    assert "benchmark_bridge:diagnosis_co_list_augmented" in diagnosis_values[0].quality_flags
    assert seizure_values == ["generalized tonic clonic seizures"]


def test_exect_s0_s1_bridge_maps_from_sleep_diagnosis_surface_to_on_awakening():
    record = load_exect_gold_document("EA0116")
    _configure_dummy([{
        "reasoning": "The model emitted the from-sleep syndrome surface in diagnosis.",
        "diagnosis": ["epilepsy with generalised tonic clonic seizures from sleep"],
        "diagnosis_evidence": [
            "New diagnosis of epilepsy with generalised tonic clonic seizures from sleep"
        ],
        "seizure_type": ["generalized tonic clonic seizures"],
        "seizure_type_evidence": ["generalised tonic clonic seizures"],
        "annotated_medication": ["levetiracetam"],
        "annotated_medication_evidence": ["Levetiracetam 250mgs once a day"],
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
    assert diagnosis_values[0].normalized_value == (
        "epilepsy with generalized tonic clonic seizures on awakening"
    )
    assert "benchmark_bridge:on_awakening_diagnosis_surface" in diagnosis_values[0].quality_flags


def test_exect_s0_s1_bridge_suppresses_diagnosis_when_header_lists_seizure_descriptors():
    record = load_exect_gold_document("EA0026")
    _configure_dummy([{
        "reasoning": "Diagnosis header lists seizure descriptors only.",
        "diagnosis": ["juvenile myoclonic epilepsy"],
        "diagnosis_evidence": ["possible JME"],
        "seizure_type": ["generalized tonic clonic seizures", "myoclonic seizures"],
        "seizure_type_evidence": ["generalised tonic clonic seizures", "myoclonic jerks"],
        "annotated_medication": ["topiramate"],
        "annotated_medication_evidence": ["topiramate"],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    values = prediction_set.predictions[0].values
    assert [value.field_name for value in values if value.field_name == "diagnosis"] == []
    seizure_values = [
        value.normalized_value
        for value in values
        if value.field_name == "seizure_type"
    ]
    assert seizure_values == ["generalized tonic clonic seizures"]


def test_exect_s0_s1_bridge_maps_myoclonic_jerks_to_myoclonic_seizures():
    record = load_exect_gold_document("EA0053")
    _configure_dummy([{
        "reasoning": "The model used jerk wording for the audited myoclonic seizure surface.",
        "diagnosis": ["juvenile myoclonic epilepsy"],
        "diagnosis_evidence": ["juvenile myoclonic epilepsy"],
        "seizure_type": ["myoclonic jerks"],
        "seizure_type_evidence": ["myoclonic jerks"],
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
    assert seizure_values[0].normalized_value == "myoclonic seizures"
    assert "benchmark_bridge:granular_seizure_surface_coarsened" in (
        seizure_values[0].quality_flags
    )


def test_exect_s0_s1_bridge_rejects_non_asm_medications():
    record = load_exect_gold_document("EA0053")
    _configure_dummy([{
        "reasoning": "The model included a psychotropic drug in the ASM list.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": [],
        "seizure_type_evidence": [],
        "annotated_medication": ["levetiracetam", "citalopram"],
        "annotated_medication_evidence": ["levetiracetam", "citalopram"],
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
    assert [value.normalized_value for value in medication_values] == ["levetiracetam"]


def test_exect_s0_s1_bridge_preserves_lamictal_brand_surface():
    record = load_exect_gold_document("EA0142")
    _configure_dummy([{
        "reasoning": "The note uses the Lamictal brand in the current medication list.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": [],
        "seizure_type_evidence": [],
        "annotated_medication": ["lamotrigine"],
        "annotated_medication_evidence": ["Current medication: Lamictal 100mg BD"],
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
    assert medication_values[0].normalized_value == "lamictal"
    assert "benchmark_bridge:medication_brand_surface_preserved" in (
        medication_values[0].quality_flags
    )


def test_exect_s0_s1_boundary_surfaces_expose_brand_medication_normalization():
    record = load_exect_gold_document("EA0142")
    _configure_dummy([{
        "reasoning": "The note uses the Lamictal brand in the current medication list.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": [],
        "seizure_type_evidence": [],
        "annotated_medication": ["lamotrigine"],
        "annotated_medication_evidence": ["Current medication: Lamictal 100mg BD"],
    }])

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    surfaces = prediction_set.predictions[0].metadata["s1_boundary_surfaces"]
    medication_rows = surfaces["deterministic_bridge_values"]["annotated_medication"]

    raw_medication_values = [
        item["raw_value"]
        for item in surfaces["raw_model_outputs"]["annotated_medication"]
    ]
    assert raw_medication_values == [
        "lamotrigine"
    ]
    assert medication_rows[0]["canonical_value"] == "lamotrigine"
    assert medication_rows[0]["benchmark_value"] == "lamictal"
    assert "benchmark_bridge:medication_brand_surface_preserved" in (
        medication_rows[0]["bridge_flags"]
    )
    assert surfaces["final_artifact_values"]["annotated_medication"][0][
        "normalized_value"
    ] == "lamictal"


def test_exect_s0_s1_bridge_repairs_medication_evidence_header_prefix():
    record = load_exect_gold_document("EA0142")
    _configure_dummy([{
        "reasoning": "Evidence should be repaired to the note line despite spacing drift.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": [],
        "seizure_type_evidence": [],
        "annotated_medication": ["Lamictal"],
        "annotated_medication_evidence": ["Current medication: Lamictal 100mg BD"],
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
    assert medication_values[0].evidence[0].text in record.text
    assert medication_values[0].evidence[0].start is not None
    assert "lamictal" in medication_values[0].evidence[0].text.lower()


def test_exect_s0_s1_bridge_excludes_medication_with_historical_evidence():
    record = load_exect_gold_document("EA0109")
    _configure_dummy([{
        "reasoning": "The model tagged a previously tried medication as current.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": ["temporal lobe seizure"],
        "seizure_type_evidence": ["temporal lobe seizure"],
        "annotated_medication": ["carbamazepine"],
        "annotated_medication_evidence": ["Previously tried carbamazepine"],
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


def test_exect_s0_s1_bridge_rejects_unsupported_diagnosis_labels():
    record = load_exect_gold_document("EA0109")
    _configure_dummy([{
        "reasoning": "The model incorrectly placed a seizure type in the diagnosis field.",
        "diagnosis": ["focal seizures"],
        "diagnosis_evidence": ["focal seizures"],
        "seizure_type": ["temporal lobe seizures"],
        "seizure_type_evidence": ["temporal lobe seizures"],
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
        if value.field_name == "diagnosis"
    ] == []
    seizure_values = [
        value
        for value in prediction_set.predictions[0].values
        if value.field_name == "seizure_type"
    ]
    assert [value.normalized_value for value in seizure_values] == [
        "temporal lobe seizure",
        "focal seizures",
    ]


def test_exect_s0_s1_bridge_restores_symptomatic_structural_focal_diagnosis():
    record = load_exect_gold_document("EA0059")
    _configure_dummy([{
        "reasoning": "The model dropped focal from the audited diagnosis surface.",
        "diagnosis": ["symptomatic structural epilepsy"],
        "diagnosis_evidence": ["symptomatic structural epilepsy"],
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
    assert "benchmark_bridge:symptomatic_structural_focal_restored" in (
        diagnosis_values[0].quality_flags
    )


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


def test_exect_s0_s1_family_specific_signature_includes_filtered_policy_examples():
    signature = build_exect_s0_s1_family_specific_signature("diagnosis")
    doc = signature.__doc__ or ""
    assert "Boundary examples:" in doc
    assert "diagnosis_label_preservation" in doc
    assert "planned_medication_exclusion" not in doc


def test_exect_s0_s1_prompt_graph_parallel_module_uses_full_note_context():
    record = load_exect_gold_document("EA0008")
    _configure_dummy([
        {
            "reasoning": "Diagnosis is explicit.",
            "diagnosis": ["symptomatic structural focal epilepsy"],
            "diagnosis_evidence": ["Diagnosis: symptomatic structural focal epilepsy"],
        },
        {
            "reasoning": "Seizure type is explicit.",
            "seizure_type": ["focal-seizures-with-altered-awareness"],
            "seizure_type_evidence": ["focal-seizures-with-altered-awareness"],
        },
        {
            "reasoning": "Medication is explicit.",
            "annotated_medication": ["Lamotrigine"],
            "annotated_medication_evidence": ["lamotrigine"],
        },
    ])

    predict_exect_records(
        ExectS0S1FieldFamilyPromptGraphParallelModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT,
    )

    assert (
        stage_graph_id_for_program_variant(EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT)
        == "g2_field_family_parallel"
    )
    lm_history = dspy.settings.lm.history
    assert len(lm_history) == 3
    for call in lm_history:
        prompt = call["messages"][-1]["content"]
        assert record.text in prompt
        assert "Section:" not in prompt


def test_exect_s0_s1_prompt_graph_sequential_module_chains_prior_context():
    record = load_exect_gold_document("EA0008")
    _configure_dummy([
        {
            "reasoning": "Diagnosis is explicit.",
            "diagnosis": ["symptomatic structural focal epilepsy"],
            "diagnosis_evidence": ["Diagnosis: symptomatic structural focal epilepsy"],
        },
        {
            "reasoning": "Seizure type is explicit.",
            "seizure_type": ["focal-seizures-with-altered-awareness"],
            "seizure_type_evidence": ["focal-seizures-with-altered-awareness"],
        },
        {
            "reasoning": "Medication is explicit.",
            "annotated_medication": ["Lamotrigine"],
            "annotated_medication_evidence": ["lamotrigine"],
        },
    ])

    predict_exect_records(
        ExectS0S1FieldFamilyPromptGraphSequentialModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT,
    )

    assert (
        stage_graph_id_for_program_variant(EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT)
        == "g2_field_family_prompt_graph"
    )
    seizure_prompt = dspy.settings.lm.history[1]["messages"][-1]["content"]
    medication_prompt = dspy.settings.lm.history[2]["messages"][-1]["content"]
    assert "Prior extractions from earlier prompt-graph stages:" in seizure_prompt
    assert "symptomatic structural focal epilepsy" in seizure_prompt
    assert "Prior extractions from earlier prompt-graph stages:" in medication_prompt
    assert "focal-seizures-with-altered-awareness" in medication_prompt


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
    assert examples[0].document_id == records[0].document_id
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


def test_exect_s0_s1_diagnosis_recall_probe_module_merges_recall_pass():
    record = load_exect_gold_document("EA0061")
    _configure_dummy(
        [
            {
                "reasoning": "Initial pass finds focal epilepsy only.",
                "diagnosis": ["focal epilepsy"],
                "diagnosis_evidence": ["Diagnosis: focal epilepsy"],
                "seizure_type": ["focal seizures"],
                "seizure_type_evidence": ["focal seizures"],
                "annotated_medication": ["lamotrigine"],
                "annotated_medication_evidence": ["lamotrigine 100mg bd"],
            },
            {
                "additional_diagnosis": ["parietal lobe epilepsy"],
                "additional_diagnosis_evidence": ["probable parietal onset"],
            },
        ]
    )

    prediction_set = predict_exect_records(
        ExectS0S1DiagnosisRecallProbeModule(),
        [record],
        model_provider="mock",
        model_name="dummy",
        program_variant=EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
    )
    diagnosis_values = [
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "diagnosis"
    ]

    assert "focal epilepsy" in diagnosis_values
    assert "parietal lobe epilepsy" in diagnosis_values


def test_build_exect_s0_s1_module_returns_diagnosis_recall_probe():
    module = build_exect_s0_s1_module(
        EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
        include_archive=True,
    )
    assert isinstance(module, ExectS0S1DiagnosisRecallProbeModule)


def test_exect_s0_s1_verify_repair_module_runs_extract_then_verify():
    record = load_exect_gold_document("EA0153")
    _configure_dummy(
        [
            {
                "reasoning": "Initial pass incorrectly includes planned lamotrigine.",
                "diagnosis": [],
                "diagnosis_evidence": [],
                "seizure_type": [],
                "seizure_type_evidence": [],
                "annotated_medication": ["lamotrigine"],
                "annotated_medication_evidence": [
                    "Please start lamotrigine 25mg once a day"
                ],
            },
            {
                "reasoning": "Verifier removes planned medication and confirms empty ASM list.",
                "diagnosis": [],
                "diagnosis_evidence": [],
                "seizure_type": [],
                "seizure_type_evidence": [],
                "annotated_medication": [],
                "annotated_medication_evidence": [],
                "verifier_decision": "repair",
                "verifier_reason": "Planned start is not benchmark-facing medication.",
            },
        ]
    )

    prediction_set = predict_exect_records(
        ExectS0S1VerifyRepairModule(),
        [record],
        model_provider="mock",
        model_name="dummy",
        program_variant=EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
    )

    assert prediction_set.metadata["program_variant"] == EXECT_S0_S1_VERIFY_REPAIR_VARIANT
    assert [
        value
        for value in prediction_set.predictions[0].values
        if value.field_name == "annotated_medication"
    ] == []
    assert len(dspy.settings.lm.history) == 2


def test_exect_s0_s1_verify_repair_respects_raw_no_benchmark_bridges_repair_policy():
    record = load_exect_gold_document("EA0153")
    _configure_dummy(
        [
            {
                "reasoning": "Initial pass.",
                "diagnosis": [],
                "diagnosis_evidence": [],
                "seizure_type": [],
                "seizure_type_evidence": [],
                "annotated_medication": ["lamotrigine"],
                "annotated_medication_evidence": [
                    "Please start lamotrigine 25mg once a day"
                ],
            },
            {
                "reasoning": "Verifier confirms planned medication removal.",
                "diagnosis": [],
                "diagnosis_evidence": [],
                "seizure_type": [],
                "seizure_type_evidence": [],
                "annotated_medication": [],
                "annotated_medication_evidence": [],
                "verifier_decision": "repair",
                "verifier_reason": "Planned start is not benchmark-facing medication.",
            },
        ]
    )

    prediction_set = predict_exect_records(
        ExectS0S1VerifyRepairModule(),
        [record],
        model_provider="mock",
        model_name="dummy",
        program_variant=EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
        repair_policy="raw_no_benchmark_bridges",
    )

    metadata = prediction_set.predictions[0].metadata
    assert metadata["apply_benchmark_bridges"] is False
    assert metadata["bridge_stage"] == "none"


def test_exect_s0_s1_verify_repair_guards_block_add_only_diagnosis():
    record = load_exect_gold_document("EA0061")
    _configure_dummy(
        [
            {
                "reasoning": "Initial pass finds focal epilepsy only.",
                "diagnosis": ["focal epilepsy"],
                "diagnosis_evidence": ["Diagnosis: focal epilepsy"],
                "seizure_type": ["focal seizures"],
                "seizure_type_evidence": ["focal seizures"],
                "annotated_medication": [],
                "annotated_medication_evidence": [],
            },
            {
                "reasoning": "Verifier incorrectly tries to add parietal lobe epilepsy.",
                "diagnosis": ["focal epilepsy", "parietal lobe epilepsy"],
                "diagnosis_evidence": [
                    "Diagnosis: focal epilepsy",
                    "probable parietal onset",
                ],
                "seizure_type": ["focal seizures"],
                "seizure_type_evidence": ["focal seizures"],
                "annotated_medication": [],
                "annotated_medication_evidence": [],
                "verifier_decision": "repair",
                "verifier_reason": "Attempted recall addition.",
            },
        ]
    )

    prediction_set = predict_exect_records(
        ExectS0S1VerifyRepairModule(),
        [record],
        model_provider="mock",
        model_name="dummy",
        program_variant=EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
    )
    diagnosis_values = [
        value.normalized_value
        for value in prediction_set.predictions[0].values
        if value.field_name == "diagnosis"
    ]

    assert diagnosis_values == ["focal epilepsy"]


def test_build_exect_s0_s1_module_returns_pre_vocab_single_pass():
    with pytest.raises(ValueError, match="archive-only"):
        build_exect_s0_s1_module(EXECT_S0_S1_PRE_VOCAB_VARIANT)

    module = build_exect_s0_s1_module(
        EXECT_S0_S1_PRE_VOCAB_VARIANT,
        include_archive=True,
    )
    assert isinstance(module, ExectS0S1PreVocabFieldFamilyModule)


def test_format_note_with_precomputed_family_candidates_injects_vocabularies():
    record = load_exect_gold_document("EA0008")
    formatted = format_note_with_precomputed_family_candidates(record.text)

    assert "Precomputed benchmark-facing candidates" in formatted
    assert "diagnosis:" in formatted
    assert "seizure_type:" in formatted
    assert "annotated_medication:" in formatted
    assert formatted.endswith(record.text)
    candidates = build_precomputed_family_candidates(record.text)
    assert "lamotrigine" in candidates["annotated_medication"]


def test_build_exect_s0_s1_module_returns_medication_pre_vocab_single_pass():
    module = build_exect_s0_s1_module(
        EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
        include_archive=True,
    )
    assert isinstance(module, ExectS0S1MedicationPreVocabFieldFamilyModule)


def test_format_note_with_precomputed_medication_candidates_omits_other_families():
    record = load_exect_gold_document("EA0008")
    formatted = format_note_with_precomputed_medication_candidates(record.text)

    assert "Precomputed benchmark-facing candidates" in formatted
    assert "annotated_medication:" in formatted
    assert "diagnosis:" not in formatted
    assert "seizure_type:" not in formatted
    assert formatted.endswith(record.text)


def test_build_exect_s0_s1_module_returns_seizure_pre_vocab_single_pass():
    module = build_exect_s0_s1_module(
        EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
        include_archive=True,
    )
    assert isinstance(module, ExectS0S1SeizurePreVocabFieldFamilyModule)


def test_format_note_with_precomputed_seizure_type_candidates_omits_other_families():
    record = load_exect_gold_document("EA0008")
    formatted = format_note_with_precomputed_seizure_type_candidates(record.text)

    assert "Precomputed benchmark-facing candidates" in formatted
    assert "seizure_type:" in formatted
    assert "diagnosis:" not in formatted
    assert "annotated_medication:" not in formatted
    assert formatted.endswith(record.text)
    assert "focal seizures" in build_precomputed_seizure_type_candidates()


def test_exect_s0_s1_raw_repair_policy_skips_benchmark_bridges():
    record = load_exect_gold_document("EA0090")
    dummy_answer = {
        "reasoning": "The model emitted one fused secondary-generalisation phrase.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": ["focal seizures with secondary generalisation"],
        "seizure_type_evidence": ["focal seizures with secondary generalisation"],
        "annotated_medication": [],
        "annotated_medication_evidence": [],
    }
    _configure_dummy([dummy_answer, dummy_answer])

    bridged = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )
    raw = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        repair_policy=REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES,
    )

    bridged_seizures = [
        value
        for value in bridged.predictions[0].values
        if value.field_name == "seizure_type"
    ]
    raw_seizures = [
        value for value in raw.predictions[0].values if value.field_name == "seizure_type"
    ]

    assert [value.normalized_value for value in bridged_seizures] == [
        "focal seizures",
        "secondary generalisation",
        "generalized tonic clonic seizure",
    ]
    assert len(raw_seizures) == 1
    assert raw_seizures[0].normalized_value == (
        "focal seizures with secondary generalisation"
    )
    assert not any(
        flag.startswith("benchmark_bridge:")
        for value in raw_seizures
        for flag in value.quality_flags
    )


def test_exect_s0_s1_raw_repair_policy_differs_from_inline_bridged_policy():
    record = load_exect_gold_document("EA0090")
    dummy_answer = {
        "reasoning": "The model emitted one fused secondary-generalisation phrase.",
        "diagnosis": [],
        "diagnosis_evidence": [],
        "seizure_type": ["focal seizures with secondary generalisation"],
        "seizure_type_evidence": ["focal seizures with secondary generalisation"],
        "annotated_medication": [],
        "annotated_medication_evidence": [],
    }
    _configure_dummy([dummy_answer, dummy_answer, dummy_answer])

    inline = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        repair_policy="none",
    )
    post = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        repair_policy=REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY,
    )
    raw = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        repair_policy=REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES,
    )

    def seizure_labels(prediction_set):
        return {
            value.normalized_value
            for value in prediction_set.predictions[0].values
            if value.field_name == "seizure_type"
        }

    assert seizure_labels(inline) == seizure_labels(post)
    assert seizure_labels(raw) != seizure_labels(inline)


def test_exect_s0_s1_post_bridge_repair_policy_records_bridge_stage_metadata():
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

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        repair_policy=REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY,
    )

    metadata = prediction_set.predictions[0].metadata
    assert metadata["bridge_stage"] == "post"
    assert metadata["apply_benchmark_bridges"] is True
    assert metadata["repair_policy"] == REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY
    assert prediction_set.metadata["repair_policy"] == REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY


def test_exect_s0_s1_raw_repair_policy_records_bridge_free_metadata():
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

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        repair_policy=REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES,
    )

    metadata = prediction_set.predictions[0].metadata
    assert metadata["bridge_stage"] == "none"
    assert metadata["apply_benchmark_bridges"] is False
    assert metadata["repair_policy"] == REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES
    surfaces = metadata["s1_boundary_surfaces"]
    assert surfaces["bridge_policy"]["apply_benchmark_bridges"] is False
    assert surfaces["deterministic_bridge_values"] == {
        "diagnosis": [],
        "seizure_type": [],
        "annotated_medication": [],
    }
    final_seizure_values = [
        item["normalized_value"]
        for item in surfaces["final_artifact_values"]["seizure_type"]
    ]
    assert final_seizure_values == [
        "focal seizures with altered awareness"
    ]


def test_build_exect_s0_s1_module_returns_verify_repair():
    module = build_exect_s0_s1_module(
        EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
        prompt_version=EXECT_S0_S1_VERIFY_REPAIR_PROMPT_VERSION,
        include_archive=True,
    )
    assert isinstance(module, ExectS0S1VerifyRepairModule)
    assert isinstance(module.extractor, ExectS0S1FieldFamilyModule)


def test_exect_s0_s1_field_family_micro_f1_metric_returns_1_on_exact_match():
    record = load_exect_gold_document("EA0008")
    example = dspy.Example(
        note_text=record.text,
        document_id=record.document_id,
        diagnosis=record.diagnoses,
        seizure_type=record.seizure_types,
        annotated_medication=record.current_medications,
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        diagnosis=record.diagnoses,
        seizure_type=record.seizure_types,
        annotated_medication=record.current_medications,
    )

    score = exect_s0_s1_field_family_micro_f1_metric(example, pred)

    assert score == 1.0


def test_exect_s1_clean_ladder_variant_applies_annotated_medication_guard():
    record = load_exect_gold_document("EA0008")
    _configure_dummy(
        [
            {
                "reasoning": "The model over-emits aspirin and misspells Epilim.",
                "diagnosis": [],
                "diagnosis_evidence": [],
                "seizure_type": [],
                "seizure_type_evidence": [],
                "annotated_medication": ["aspirin", "eplim chrono", "lamotrigine"],
                "annotated_medication_evidence": ["aspirin", "Epilim Chrono", "lamotrigine"],
            }
        ]
    )

    prediction_set = predict_exect_records(
        ExectS0S1FieldFamilyModule(prompt_version=EXECT_S0_S1_V4_11_PROMPT_VERSION),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        prompt_version=EXECT_S0_S1_V4_11_PROMPT_VERSION,
        program_variant=EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT,
    )

    medication_values = [
        value
        for value in prediction_set.predictions[0].values
        if value.field_name == "annotated_medication"
    ]
    normalized = [value.normalized_value for value in medication_values]
    assert "aspirin" not in normalized
    assert "epilim chrono" in normalized
    assert "lamotrigine" in normalized
    assert any(
        flag.startswith("s1_clean_bridge:")
        for value in medication_values
        for flag in value.quality_flags
    )


def test_exect_s1_clean_ladder_v2_routes_diagnosis_from_stable_policy():
    _configure_dummy(
        [
            {
                "reasoning": "v4.10 keeps generic diagnosis stable.",
                "diagnosis": ["epilepsy"],
                "diagnosis_evidence": ["Diagnosis: epilepsy"],
                "seizure_type": ["focal seizure"],
                "seizure_type_evidence": ["focal seizure"],
                "annotated_medication": ["lamotrigine"],
                "annotated_medication_evidence": ["lamotrigine"],
            },
            {
                "reasoning": "v4.11 improves seizure policy but drifts diagnosis.",
                "diagnosis": ["focal epilepsy"],
                "diagnosis_evidence": ["focal seizures"],
                "seizure_type": ["generalized tonic clonic seizures"],
                "seizure_type_evidence": ["generalized tonic clonic seizures"],
                "annotated_medication": ["lamotrigine"],
                "annotated_medication_evidence": ["lamotrigine"],
            },
        ]
    )

    pred = ExectS1CleanLadderDiagnosisStableEnsembleModule()(note_text="test note")

    assert pred.diagnosis == ["epilepsy"]
    assert pred.seizure_type == ["generalized tonic clonic seizures"]
    assert pred.annotated_medication == ["lamotrigine"]


def test_build_exect_s0_s1_module_returns_clean_ladder_v2_ensemble():
    module = build_exect_s0_s1_module(
        EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT
    )
    assert isinstance(module, ExectS1CleanLadderDiagnosisStableEnsembleModule)


def test_exect_s0_s1_field_family_micro_f1_metric_penalizes_wrong_labels():
    record = load_exect_gold_document("EA0008")
    example = dspy.Example(
        note_text=record.text,
        document_id=record.document_id,
        diagnosis=record.diagnoses,
        seizure_type=record.seizure_types,
        annotated_medication=record.current_medications,
    ).with_inputs("note_text")
    exact_pred = dspy.Prediction(
        diagnosis=record.diagnoses,
        seizure_type=record.seizure_types,
        annotated_medication=record.current_medications,
    )
    wrong_pred = dspy.Prediction(
        diagnosis=["wrong diagnosis"],
        seizure_type=["wrong seizure type"],
        annotated_medication=["wrong medication"],
    )

    exact_score = exect_s0_s1_field_family_micro_f1_metric(example, exact_pred)
    wrong_score = exect_s0_s1_field_family_micro_f1_metric(example, wrong_pred)

    assert exact_score == 1.0
    assert wrong_score < exact_score


def test_exect_s0_s1_field_family_micro_f1_raw_metric_omits_inline_bridges():
    record = load_exect_gold_documents()[0]
    example = dspy.Example(
        note_text=record.text,
        document_id=record.document_id,
        diagnosis=record.diagnoses,
        seizure_type=record.seizure_types,
        annotated_medication=record.current_medications,
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        reasoning="test",
        diagnosis=["focal"],
        diagnosis_evidence=["focal"],
        seizure_type=[],
        seizure_type_evidence=[],
        annotated_medication=[],
        annotated_medication_evidence=[],
    )

    raw_score = exect_s0_s1_field_family_micro_f1_raw_metric(example, pred)
    bridged_score = exect_s0_s1_field_family_micro_f1_metric(example, pred)

    assert raw_score <= bridged_score


def test_compile_exect_s0_s1_module_bootstrap_returns_callable_module():
    records = load_exect_gold_documents()[:3]
    answers = [
        {
            "reasoning": "Extract benchmark-facing labels.",
            "diagnosis": record.diagnoses,
            "diagnosis_evidence": record.diagnoses,
            "seizure_type": record.seizure_types,
            "seizure_type_evidence": record.seizure_types,
            "annotated_medication": record.current_medications,
            "annotated_medication_evidence": record.current_medications,
        }
        for record in records
    ] * 4
    _configure_dummy(answers)

    compiled = compile_exect_s0_s1_module(
        records,
        max_bootstrapped_demos=2,
        max_labeled_demos=0,
        max_rounds=1,
    )

    assert isinstance(compiled, ExectS0S1FieldFamilyModule)

    result = predict_exect_records(
        compiled,
        [records[0]],
        model_provider="mock",
        model_name="dummy-bootstrap",
        prompt_version=EXECT_S0_S1_PROMPT_VERSION,
    )
    assert result.dataset == "exect_v2"
    assert len(result.predictions) == 1
    assert result.metadata["program_variant"] == EXECT_S0_S1_VARIANT
