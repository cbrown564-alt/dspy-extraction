from types import SimpleNamespace

from clinical_extraction.exect.s1_boundary import (
    EXECT_S1_BOUNDARY_SURFACE_VERSION,
    build_s1_boundary_surfaces_metadata,
)
from clinical_extraction.exect.s0_s1.prediction_artifacts import (
    merge_exect_s1_diagnosis_recall,
    recover_exect_s1_clean_annotated_medication_raw_values,
)
from clinical_extraction.schemas import EvidenceSpan, ExtractedValue


def test_s1_boundary_surface_characterizes_raw_bridge_and_final_values():
    pred = SimpleNamespace(
        diagnosis=["epilepsy", "juvenile-myoclonic-epilepsy"],
        diagnosis_evidence=["epilepsy", "JME"],
        seizure_type=[],
        seizure_type_evidence=[],
        annotated_medication=[],
        annotated_medication_evidence=[],
    )
    values = [
        ExtractedValue(
            field_name="diagnosis",
            raw_value="juvenile-myoclonic-epilepsy",
            normalized_value="juvenile myoclonic epilepsy",
            evidence=[EvidenceSpan(text="JME")],
            quality_flags=["specificity_collapsed"],
        )
    ]

    surfaces = build_s1_boundary_surfaces_metadata(
        pred=pred,
        values=values,
        prompt_version="exect_s0_s1_field_family_v4_12",
        program_variant="exect_s0_s1_field_family_single_pass",
        repair_policy="artifact_benchmark_bridge_only",
        apply_benchmark_bridges=True,
        bridge_stage="post",
    )

    assert surfaces["boundary_version"] == EXECT_S1_BOUNDARY_SURFACE_VERSION
    assert surfaces["bridge_policy"] == {
        "apply_benchmark_bridges": True,
        "bridge_stage": "post",
        "repair_policy": "artifact_benchmark_bridge_only",
        "program_variant": "exect_s0_s1_field_family_single_pass",
    }
    assert [row["raw_value"] for row in surfaces["raw_model_outputs"]["diagnosis"]] == [
        "epilepsy",
        "juvenile-myoclonic-epilepsy",
    ]

    bridge_rows = surfaces["deterministic_bridge_values"]["diagnosis"]
    dropped_parent = next(row for row in bridge_rows if row["raw_value"] == "epilepsy")
    kept_specific = next(
        row
        for row in bridge_rows
        if row["benchmark_value"] == "juvenile myoclonic epilepsy"
    )

    assert dropped_parent["canonical_value"] == "epilepsy"
    assert dropped_parent["benchmark_value"] is None
    assert dropped_parent["bridge_status"] == "dropped"
    assert kept_specific["bridge_status"] == "kept"
    assert kept_specific["evidence_text"] == "JME"
    assert kept_specific["bridge_flags"] == ["specificity_collapsed"]
    assert [
        row["normalized_value"]
        for row in surfaces["final_artifact_values"]["diagnosis"]
    ] == ["juvenile myoclonic epilepsy"]


def test_s1_boundary_surface_records_prompt_split_and_bridge_free_state():
    pred = SimpleNamespace(
        diagnosis=[],
        diagnosis_evidence=[],
        seizure_type=["focal-seizures-with-altered-awareness"],
        seizure_type_evidence=["focal-seizures-with-altered-awareness"],
        annotated_medication=["Lamotrigine"],
        annotated_medication_evidence=["lamotrigine"],
        diagnosis_source_prompt_version="diagnosis_v1",
        seizure_medication_source_prompt_version="seizure_medication_v2",
    )
    values = [
        ExtractedValue(
            field_name="seizure_type",
            raw_value="focal-seizures-with-altered-awareness",
            normalized_value="focal seizures with altered awareness",
            evidence=[EvidenceSpan(text="focal-seizures-with-altered-awareness")],
        ),
        ExtractedValue(
            field_name="annotated_medication",
            raw_value="Lamotrigine",
            normalized_value="lamotrigine",
            evidence=[EvidenceSpan(text="lamotrigine")],
        ),
    ]

    surfaces = build_s1_boundary_surfaces_metadata(
        pred=pred,
        values=values,
        prompt_version="combined_v0",
        program_variant="exect_s0_s1_prompt_graph_parallel",
        repair_policy="raw_no_benchmark_bridges",
        apply_benchmark_bridges=False,
        bridge_stage="none",
    )

    assert surfaces["deterministic_bridge_values"] == {
        "diagnosis": [],
        "seizure_type": [],
        "annotated_medication": [],
    }
    assert surfaces["prompt_policy_effects"]["source_prompt_version_by_field"] == {
        "diagnosis": "diagnosis_v1",
        "seizure_type": "seizure_medication_v2",
        "annotated_medication": "seizure_medication_v2",
    }
    assert surfaces["prompt_policy_effects"]["notes"] == ["field_prompt_policy_split"]
    assert surfaces["prompt_policy_effects"]["raw_output_count_by_field"] == {
        "diagnosis": 0,
        "seizure_type": 1,
        "annotated_medication": 1,
    }
    assert [
        row["normalized_value"]
        for row in surfaces["final_artifact_values"]["seizure_type"]
    ] == ["focal seizures with altered awareness"]


def test_s1_diagnosis_recall_surface_adds_only_allowed_new_labels():
    merged, evidence, added = merge_exect_s1_diagnosis_recall(
        initial_diagnosis=["focal epilepsy"],
        initial_diagnosis_evidence=["Diagnosis: focal epilepsy"],
        additional_diagnosis=["parietal lobe epilepsy", "focal epilepsy", "hydrocephalus"],
        additional_diagnosis_evidence=[
            "probable parietal onset",
            "Diagnosis: focal epilepsy",
            "Diagnosis: hydrocephalus",
        ],
    )

    assert merged == ["focal epilepsy", "parietal lobe epilepsy"]
    assert evidence == ["Diagnosis: focal epilepsy", "probable parietal onset"]
    assert added == ["parietal lobe epilepsy"]


def test_s1_clean_medication_surface_reuses_promoted_guard():
    recovered, flags = recover_exect_s1_clean_annotated_medication_raw_values(
        ["aspirin", "eplim chrono", "lamotrigine"],
        ["aspirin", "Epilim Chrono", "lamotrigine"],
        "Current medication: Epilim Chrono and lamotrigine. Aspirin for migraine.",
    )

    assert recovered == ["epilim chrono", "lamotrigine"]
    assert "s1_clean_bridge:benchmark_bridge:non_asm_medication_rejected" in flags
