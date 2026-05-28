from __future__ import annotations

from clinical_extraction.exect.medication_primitives import (
    build_exect_medication_candidate_payloads,
    exect_medication_benchmark_bridge,
    infer_exect_medication_temporality,
)
from clinical_extraction.primitives import primitive_registry_by_id


def test_exect_medication_candidates_preserve_brand_generic_and_temporality():
    note = (
        "Current medication: Lamictal 100mg BD. "
        "To start levetiracetam 250mg nocte if seizures recur."
    )

    candidates = build_exect_medication_candidate_payloads(note)

    lamictal = next(item for item in candidates if item.raw_text == "Lamictal")
    levetiracetam = next(item for item in candidates if item.raw_text == "levetiracetam")

    assert lamictal.primitive_id == "exect.medication.rx_candidates.v1"
    assert lamictal.dataset == "exect_v2"
    assert lamictal.field_family == "medication"
    assert lamictal.normalized_value == "lamotrigine"
    assert lamictal.benchmark_value == "lamictal"
    assert lamictal.metadata["temporality"] == "current"
    assert note[lamictal.start : lamictal.end] == "Lamictal"

    assert levetiracetam.normalized_value == "levetiracetam"
    assert levetiracetam.benchmark_value is None
    assert levetiracetam.metadata["temporality"] == "planned"
    assert "Planned medications are not benchmark-facing S1 current prescriptions." in (
        levetiracetam.caveats
    )


def test_exect_medication_benchmark_bridge_rejects_non_asm_and_preserves_brand_surface():
    brand = exect_medication_benchmark_bridge(
        "lamotrigine",
        note_text="Current medication: Lamictal 100mg BD",
        evidence_text="Current medication: Lamictal 100mg BD",
    )
    non_asm = exect_medication_benchmark_bridge(
        "citalopram",
        evidence_text="Current medication: citalopram 20mg daily",
    )

    assert brand.raw_value == "lamotrigine"
    assert brand.canonical_value == "lamotrigine"
    assert brand.benchmark_value == "lamictal"
    assert brand.metadata["benchmark_surface_policy"] == "brand_surface_preserved"
    assert brand.prediction_affecting
    assert not brand.scorer_only

    assert non_asm.canonical_value == "citalopram"
    assert non_asm.benchmark_value is None
    assert non_asm.metadata["is_asm"] is False
    assert non_asm.metadata["rejected_reason"] == "non_asm_medication"


def test_exect_medication_temporality_distinguishes_current_planned_previous_and_taper():
    current = infer_exect_medication_temporality(
        "Current medication: carbamazepine 200mg bd (reduce and stop over 8 weeks)."
    )
    planned = infer_exect_medication_temporality("To start levetiracetam 250mg nocte.")
    previous = infer_exect_medication_temporality("Previously tried carbamazepine.")

    assert current.canonical_value == "current"
    assert current.benchmark_value == "current_prescription"
    assert "taper_or_stop_inside_current_prescription_line" in current.metadata["cues"]

    assert planned.canonical_value == "planned"
    assert planned.benchmark_value is None
    assert planned.metadata["benchmark_s1_included"] is False

    assert previous.canonical_value == "previous"
    assert previous.benchmark_value is None
    assert previous.metadata["benchmark_s1_included"] is False


def test_exect_medication_pack_primitives_are_registered():
    registry = primitive_registry_by_id()

    assert registry["exect.medication.rx_candidates.v1"].status == "implemented"
    assert registry["exect.medication.benchmark_bridge.v1"].status == "implemented"
    assert (
        registry["exect.medication_temporality.post_classifier.v1"].status
        == "implemented"
    )
    assert (
        registry["exect.medication.am_guard_non_asm_brand_alias.v1"].status
        == "implemented"
    )


def test_exect_annotated_medication_non_asm_brand_alias_guard():
    from clinical_extraction.exect.medication_primitives import (
        recover_exect_annotated_medication_non_asm_brand_alias_guard,
    )
    # Test spelling repair, non-ASM drop, and deduplication
    note = (
        "Current medication: Eplim Chrono 500mg BD, Simvastatin 40mg nocte, "
        "and sodium valproate."
    )
    raw_values = ["Eplim Chrono", "Simvastatin", "sodium valproate"]
    evidence_values = ["Eplim Chrono 500mg BD", "Simvastatin 40mg nocte", "sodium valproate"]

    recovered, flags = recover_exect_annotated_medication_non_asm_brand_alias_guard(
        raw_values,
        evidence_values,
        note,
    )

    # Simvastatin should be dropped (non-ASM).
    # Eplim Chrono should be repaired, but the explicit generic same-canonical
    # prediction should win because gold often uses the generic surface.
    assert recovered == ["sodium valproate"]
    assert "benchmark_bridge:medication_surface_repaired" in flags
    assert "benchmark_bridge:non_asm_medication_rejected" in flags
    assert "benchmark_bridge:medication_deduplicated" in flags


def test_exect_annotated_medication_non_asm_brand_alias_guard_eplim_repair():
    from clinical_extraction.exect.medication_primitives import (
        recover_exect_annotated_medication_non_asm_brand_alias_guard,
    )
    note = "She is taking eplim and lamotrigine."
    # Eplim should be repaired to epilim chrono.
    # lamotrigine is Generic, but the note does not contain lamictal, so it stays lamotrigine.
    raw_values = ["eplim", "lamotrigine"]
    evidence_values = ["taking eplim", "lamotrigine"]

    recovered, flags = recover_exect_annotated_medication_non_asm_brand_alias_guard(
        raw_values,
        evidence_values,
        note,
    )
    assert recovered == ["epilim chrono", "lamotrigine"]
    assert "benchmark_bridge:medication_surface_repaired" in flags


def test_exect_annotated_medication_guard_preserves_benchmark_brand_policy():
    from clinical_extraction.exect.medication_primitives import (
        recover_exect_annotated_medication_non_asm_brand_alias_guard,
    )

    recovered, _flags = recover_exect_annotated_medication_non_asm_brand_alias_guard(
        raw_values=["Epilim", "lamotrigine"],
        evidence_values=["Epilim 400 mg twice a day", "Lamictal 100mg BD"],
        note_text="Medication: Epilim 400 mg twice a day. Lamictal 100mg BD.",
    )

    assert recovered == ["sodium valproate", "lamictal"]


def test_exect_annotated_medication_temporal_evidence_guard():
    from clinical_extraction.exect.medication_primitives import (
        recover_exect_annotated_medication_temporal_evidence_guard,
    )

    # Case 1: Planned medication without any current mention in the note -> should be pruned.
    note_1 = "Plan: to start levetiracetam 500mg BD. Current: none."
    raw_values_1 = ["levetiracetam"]
    evidence_values_1 = ["to start levetiracetam"]
    recovered_1, flags_1 = recover_exect_annotated_medication_temporal_evidence_guard(
        raw_values_1,
        evidence_values_1,
        note_1,
    )
    assert recovered_1 == []
    assert "benchmark_bridge:medication_temporality_pruned" in flags_1

    # Case 2: Planned medication but there is a current mention of the same drug in the note -> should NOT be pruned.
    note_2 = "Current medication: levetiracetam 500mg bd. Plan: to start levetiracetam 1000mg bd."
    raw_values_2 = ["levetiracetam"]
    evidence_values_2 = ["to start levetiracetam 1000mg"]
    recovered_2, flags_2 = recover_exect_annotated_medication_temporal_evidence_guard(
        raw_values_2,
        evidence_values_2,
        note_2,
    )
    assert recovered_2 == ["levetiracetam"]
    assert "benchmark_bridge:medication_temporality_pruned" not in flags_2

    # Case 3: Standard spelling repair, non-ASM drop, and deduplication should still work
    note_3 = "Current medication: Eplim Chrono 500mg BD and Simvastatin 40mg nocte."
    raw_values_3 = ["Eplim Chrono", "Simvastatin"]
    evidence_values_3 = ["Eplim Chrono 500mg BD", "Simvastatin 40mg nocte"]
    recovered_3, flags_3 = recover_exect_annotated_medication_temporal_evidence_guard(
        raw_values_3,
        evidence_values_3,
        note_3,
    )
    assert recovered_3 == ["epilim chrono"]
    assert "benchmark_bridge:medication_surface_repaired" in flags_3
    assert "benchmark_bridge:non_asm_medication_rejected" in flags_3

