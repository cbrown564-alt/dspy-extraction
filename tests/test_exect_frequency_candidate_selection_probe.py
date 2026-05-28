from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clinical_extraction.evaluation.exect_frequency_candidate_selection_probe import (
    DEFAULT_E1_PAYLOAD,
    DEFAULT_S4_RUN,
    DEFAULT_S5_RUN,
    build_report,
)


def test_e10_frequency_candidate_selection_probe_separates_payload_from_adjudication():
    report = build_report(
        splits_path=Path("data/splits/exectv2_splits.json"),
        split_name="validation",
        e1_payload_path=DEFAULT_E1_PAYLOAD,
        s4_run=DEFAULT_S4_RUN,
        s5_run=DEFAULT_S5_RUN,
    )

    surfaces = report["surface_summaries"]
    broad = surfaces["broad_event_rate_payload"]
    oracle = surfaces["candidate_constrained_oracle"]
    s5 = surfaces["s5_gpt_frequency_surface"]

    assert report["kanban_card"] == "E10 - ExECT Frequency Candidate Selection Split"
    assert broad["classification"] == "diagnostic coverage substrate"
    assert broad["tp"] == 43
    assert broad["fp"] == 151
    assert broad["fn"] == 0
    assert broad["recall"] == 1.0
    assert broad["precision"] < 0.25

    assert oracle["classification"] == "oracle upper bound / not deployable"
    assert oracle["tp"] == 43
    assert oracle["fp"] == 0
    assert oracle["fn"] == 0
    assert oracle["f1"] == 1.0

    assert s5["classification"] == "existing stacked operational surface"
    assert s5["run_id"] == DEFAULT_S5_RUN
    assert round(s5["f1"], 3) == 0.739
    assert s5["fn"] > 0
    assert s5["fp"] > 0

    assert report["extra_candidate_strata"]["broad_event_rate_payload"]
    assert report["error_attribution"]["s5_gpt_frequency_surface"]["category_counts"]
