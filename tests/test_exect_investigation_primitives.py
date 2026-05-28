from __future__ import annotations

from clinical_extraction.exect.investigation_primitives import (
    recover_exect_s4_investigation_benchmark_values,
)


def test_recover_exect_s4_investigation_drops_planned_scan_unknown():
    recovered, flags = recover_exect_s4_investigation_benchmark_values(
        ["mri unknown", "eeg unknown"],
        "I will arrange an MRI brain and an EEG.",
    )
    assert recovered == []
    assert "s4_bridge:investigation_unknown_removed" in flags


def test_recover_exect_s4_investigation_keeps_unavailable_results_unknown():
    recovered, flags = recover_exect_s4_investigation_benchmark_values(
        ["eeg unknown", "mri normal"],
        (
            "He had an MRI scan which was normal. "
            "I do not have the results of his recent EEG test."
        ),
    )
    assert recovered == ["eeg unknown", "mri normal"]
    assert flags == []
