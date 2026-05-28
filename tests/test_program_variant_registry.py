from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from clinical_extraction.experiments.config import ExperimentConfig, load_experiment_config
from clinical_extraction.experiments.program_variant_registry import (
    PROGRAM_VARIANT_REGISTRY,
    active_program_variant_specs,
    program_contract_allows,
    program_variant_registry_by_id,
    render_program_variant_registry_markdown,
)


def test_program_variant_registry_has_unique_ids():
    ids = [spec.variant_id for spec in PROGRAM_VARIANT_REGISTRY]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize(
    "variant_id",
    [
        "gan.s0.builder_gap_v1",
        "gan.s0.d1_v1_2b_schema_guard_only",
        "exect.s1.clean_ladder_v2_diagnosis_stable",
        "exect.s2.clean_ladder_v1",
        "exect.s3.clean_ladder_v1",
        "exect.s4.operational_k0_k1",
        "exect.s5.v2b_operational",
    ],
)
def test_registry_includes_c2_promoted_and_diagnostic_surfaces(variant_id: str):
    registry = program_variant_registry_by_id()
    spec = registry[variant_id]

    assert spec.status in {
        "promoted_baseline",
        "mechanism_baseline",
        "diagnostic_baseline",
        "operational_baseline",
    }
    assert spec.decision_doc is not None
    assert spec.config_examples


def test_registry_contract_accepts_gan_paper_reproduction_and_canonical_scorers():
    assert program_contract_allows(
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        program_variant="gan_frequency_s0_date_events_candidates_single_pass",
        scorer_mode="gan_frequency_deterministic_v1",
    )
    assert program_contract_allows(
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        program_variant="gan_frequency_s0_date_events_candidates_single_pass",
        scorer_mode="gan2026_paper_reproduction",
    )


def test_experiment_config_validation_uses_program_variant_registry():
    payload = json.loads(
        Path(
            "configs/experiments/"
            "gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini.json"
        ).read_text(encoding="utf-8")
    )
    payload["scorer_mode"] = "exect_field_family_deterministic_v1"

    with pytest.raises(ValidationError, match="registered program variant"):
        ExperimentConfig.model_validate(payload)


def test_active_program_variant_specs_default_to_non_historical_rows():
    active_ids = {spec.variant_id for spec in active_program_variant_specs()}

    assert "gan.s0.builder_gap_v1" in active_ids
    assert "gan.s0.self_consistency" not in active_ids


def test_registry_markdown_report_groups_status_and_config_counts():
    report = render_program_variant_registry_markdown(repo_root=Path.cwd())

    assert "| gan.s0.builder_gap_v1 | Gan 2026 | promoted_baseline |" in report
    assert "| exect.s5.v2b_operational | ExECTv2 | operational_baseline |" in report
    assert "Config Count" in report


def test_current_experiment_configs_are_covered_by_program_variant_registry():
    errors: list[str] = []
    for path in sorted(Path("configs/experiments").rglob("*.json")):
        try:
            load_experiment_config(path)
        except ValidationError as exc:
            errors.append(f"{path}: {exc}")

    assert errors == []
