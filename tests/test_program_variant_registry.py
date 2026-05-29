from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from clinical_extraction.experiments.config import ExperimentConfig, load_experiment_config
from clinical_extraction.experiments.program_variant_registry import (
    PROGRAM_VARIANT_REGISTRY,
    archived_program_variant_specs,
    current_authority_program_variant_specs,
    experiment_config_inventory,
    program_contract_allows,
    program_variant_registry_by_id,
    render_program_variant_registry_markdown,
    resolve_program_variant_spec_for_config,
)


def test_program_variant_registry_has_unique_ids():
    ids = [spec.variant_id for spec in PROGRAM_VARIANT_REGISTRY]
    assert len(ids) == len(set(ids))


def test_program_variant_registry_is_current_authority_only():
    ids = {spec.variant_id for spec in PROGRAM_VARIANT_REGISTRY}

    assert len(PROGRAM_VARIANT_REGISTRY) == 19
    assert ids == {spec.variant_id for spec in current_authority_program_variant_specs()}
    assert "gan.s0.self_consistency" not in ids
    assert "gan.s0.date_events_candidates_single_pass" not in ids
    assert all(spec.authority_class == "current_authority" for spec in PROGRAM_VARIANT_REGISTRY)


def test_archived_program_variant_specs_preserve_provenance_rows():
    archived = {spec.variant_id: spec for spec in archived_program_variant_specs()}

    assert "gan.s0.self_consistency" in archived
    assert archived["gan.s0.self_consistency"].status == "rejected_arm"
    assert "gan.s0.date_events_candidates_single_pass" in archived
    assert archived["gan.s0.date_events_candidates_single_pass"].status == "replay_provenance"
    assert all(not spec.is_current_authority for spec in archived.values())


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
        "exect.s1.e13_medication_only",
        "exect.s1.e13_medication_lifecycle_context",
        "gan.s0.explicit_reason_code_adjudicator",
        "gan.s0.special_class_target_selector",
        "gan.s0.candidate_ranking_target_selector",
        "gan.s0.support_aware_target_selector",
        "gan.s0.closed_option_target_selector",
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


def test_current_authority_program_variant_specs_exclude_replay_rows():
    active_ids = {
        spec.variant_id for spec in current_authority_program_variant_specs()
    }

    assert "gan.s0.builder_gap_v1" in active_ids
    assert "gan.s0.self_consistency" not in active_ids
    assert "gan.s0.date_events_candidates_single_pass" not in active_ids


def test_active_config_resolution_does_not_use_archived_variant_rows():
    payload = json.loads(
        Path(
            "archive/configs/"
            "gan_s0_self_consistency_sample5_cap25_gpt4_1_mini.json"
        ).read_text(encoding="utf-8")
    )

    assert resolve_program_variant_spec_for_config(payload) is None
    assert (
        resolve_program_variant_spec_for_config(payload, include_archive=True).variant_id
        == "gan.s0.self_consistency"
    )


def test_active_config_validation_does_not_accept_archived_variant_rows():
    payload = json.loads(
        Path(
            "archive/configs/"
            "gan_s0_self_consistency_sample5_cap25_gpt4_1_mini.json"
        ).read_text(encoding="utf-8")
    )

    with pytest.raises(ValidationError, match="registered program variant"):
        ExperimentConfig.model_validate(payload)


def test_registry_markdown_report_labels_archive_configs_as_provenance():
    report = render_program_variant_registry_markdown(repo_root=Path.cwd())

    assert (
        "| gan.s0.builder_gap_v1 | Gan 2026 | promoted_baseline | "
        "current_authority |"
    ) in report
    assert (
        "| exect.s5.v2b_operational | ExECTv2 | operational_baseline | "
        "current_authority |"
    ) in report
    assert (
        "| gan.s0.self_consistency | Gan 2026 | rejected_arm | docs_provenance |"
    ) in report
    assert "Active Config Count" in report
    assert "Archived Config Count" in report
    assert "ordinary config loading is active-only" in report
    assert "rows under `Archived Config Inventory` are" in report


def test_experiment_config_inventory_assigns_one_explicit_status_per_config():
    rows = experiment_config_inventory(repo_root=Path.cwd())
    paths = [row.config_path for row in rows]

    assert len(rows) == len(list(Path("configs/experiments").rglob("*.json")))
    assert len(paths) == len(set(paths))
    assert {row.authority_class for row in rows} == {"current_authority"}
    assert all(not row.config_path.startswith("archive/") for row in rows)


def test_archived_config_inventory_preserves_rejected_and_historical_rows_as_provenance():
    rows = experiment_config_inventory(repo_root=Path.cwd(), source="archive")
    paths = {row.config_path: row for row in rows}

    assert {row.authority_class for row in rows} == {"docs_provenance"}
    assert (
        paths[
            "archive/configs/gan_s0_self_consistency_sample5_cap25_gpt4_1_mini.json"
        ].status
        == "rejected_arm"
    )
    assert (
        paths[
            "archive/configs/gan_s0_date_stage_d0_baseline_det_candidates_cap25_gpt4_1_mini.json"
        ].status
        == "replay_provenance"
    )
    assert (
        paths["archive/configs/exect_s4_validation_full_qwen35b_ollama.json"].status
        == "historical_arm"
    )


def test_config_inventory_resolves_ambiguous_gan_program_surfaces():
    rows = {
        row.config_path: row
        for row in experiment_config_inventory(repo_root=Path.cwd(), source="all")
    }

    assert (
        rows[
            "configs/experiments/gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini.json"
        ].variant_id
        == "gan.s0.d1_v1_2b_schema_guard_only"
    )
    assert (
        rows[
            "archive/configs/gan_s0_self_consistency_sample5_cap25_gpt4_1_mini.json"
        ].status
        == "rejected_arm"
    )
    assert (
        rows[
            "archive/configs/"
            "gan_s0_date_stage_d0_baseline_det_candidates_cap25_gpt4_1_mini.json"
        ].status
        == "replay_provenance"
    )


def test_loadable_experiment_configs_are_covered_by_program_variant_registry():
    errors: list[str] = []
    for path in sorted(Path("configs/experiments").rglob("*.json")):
        try:
            load_experiment_config(path)
        except ValidationError as exc:
            errors.append(f"{path}: {exc}")

    assert errors == []
