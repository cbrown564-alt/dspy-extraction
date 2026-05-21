"""Fixture tests for ExECT S3 epilepsy_cause CUIPhrase bridge (K0+K1)."""

from clinical_extraction.programs.exect_s2 import _recover_s2_comorbidity_raw_values
from clinical_extraction.programs.exect_s3 import (
    EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
    _recover_s3_epilepsy_cause_raw_values,
    _s3_bridge_tiers,
)

_K0_K1 = _s3_bridge_tiers(EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT)


def test_ec_0059_early_life_meningitis_strips_modifier():
    note = (
        "Diagnosis: symptomatic structural epilepsy secondary probably caused by "
        "early life meningitis."
    )
    recovered, flags = _recover_s3_epilepsy_cause_raw_values(
        ["early life meningitis"],
        note,
        bridge_tiers=_K0_K1,
    )
    assert recovered == ["meningitis"]
    assert "s3_bridge:cause_modifier_stripped" in flags


def test_ec_0016_cva_maps_cerebrovascular_accident():
    note = "History of cerebrovascular accident with residual hemiparesis."
    recovered, flags = _recover_s3_epilepsy_cause_raw_values(
        ["cerebrovascular accident"],
        note,
        bridge_tiers=_K0_K1,
    )
    assert recovered == ["cva"]
    assert "s3_bridge:cause_synonym_mapped" in flags


def test_ec_0170_ich_strips_modifiers_and_normalizes_spelling():
    note = (
        "Epilepsy secondary to recurrent right hemisphere intracerebral haemorrhage."
    )
    recovered, flags = _recover_s3_epilepsy_cause_raw_values(
        ["recurrent right hemisphere intracerebral haemorrhage"],
        note,
        bridge_tiers=_K0_K1,
    )
    assert recovered == ["intracerebral hemorrhage"]
    assert "s3_bridge:cause_modifier_stripped" in flags
    assert "s3_bridge:cause_spelling_normalized" in flags


def test_ec_k0_plural_strokes_to_stroke():
    note = "Epilepsy due to previous strokes."
    recovered, flags = _recover_s3_epilepsy_cause_raw_values(
        ["strokes"],
        note,
        bridge_tiers=_K0_K1,
    )
    assert recovered == ["stroke"]
    assert "s3_bridge:cause_plural_normalized" in flags


def test_epilepsy_cause_bridge_off_preserves_raw_surface():
    note = "Epilepsy secondary to early life meningitis."
    recovered, flags = _recover_s3_epilepsy_cause_raw_values(
        ["early life meningitis"],
        note,
        bridge_tiers=frozenset(),
    )
    assert recovered == ["early life meningitis"]
    assert "s3_bridge:cause_modifier_stripped" not in flags


def test_epilepsy_cause_still_drops_seizure_history_with_bridge():
    recovered, flags = _recover_s3_epilepsy_cause_raw_values(
        ["meningitis", "febrile seizures"],
        "Epilepsy secondary to meningitis.",
        bridge_tiers=_K0_K1,
    )
    assert recovered == ["meningitis"]
    assert "s3_bridge:seizure_history_cause_removed" in flags


def test_ec_overlap_keep_comorbidity_unchanged_when_cause_mapped():
    """EA0016-style: cause bridge maps CVA; comorbidity recovery is independent."""
    note = (
        "History of cerebrovascular accident with residual hemiparesis. "
        "Epilepsy secondary to cerebrovascular accident."
    )
    comorbidity_raw, _ = _recover_s2_comorbidity_raw_values(
        ["cerebrovascular accident", "hemiparesis"],
        note,
    )
    cause_raw, cause_flags = _recover_s3_epilepsy_cause_raw_values(
        ["cerebrovascular accident"],
        note,
        bridge_tiers=_K0_K1,
    )
    assert "cerebrovascular accident" in comorbidity_raw or "cva" in comorbidity_raw
    assert cause_raw == ["cva"]
    assert "s3_bridge:cause_synonym_mapped" in cause_flags
