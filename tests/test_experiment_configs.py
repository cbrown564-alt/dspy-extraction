import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from clinical_extraction.experiments.config import (
    ExperimentConfig,
    load_experiment_config,
)
from clinical_extraction.paths import resolve_config_path


ACTIVE_CONFIG_ROOT = Path("configs/experiments")


def read_config_payload(path: Path | str) -> dict:
    p = resolve_config_path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def test_active_experiment_configs_are_loadable_current_contracts():
    errors: list[str] = []
    config_paths = sorted(ACTIVE_CONFIG_ROOT.rglob("*.json"))

    for path in config_paths:
        try:
            load_experiment_config(path)
        except ValidationError as exc:
            errors.append(f"{path}: {exc}")
            continue

        assert not str(path).replace("\\", "/").startswith("archive/configs/")

    assert config_paths
    assert errors == []


def test_load_experiment_config_no_longer_falls_back_to_archive_by_default():
    archived_name = "gan_s0_self_consistency_sample5_cap25_gpt4_1_mini.json"
    resolved = resolve_config_path(Path("configs/experiments") / archived_name)

    assert resolved == (Path.cwd() / "configs/experiments" / archived_name)
    assert not resolved.exists()
    assert (Path("archive/configs") / archived_name).is_file()


def test_experiment_config_validation_uses_current_program_variant_registry():
    payload = read_config_payload(
        "configs/experiments/"
        "gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini.json"
    )
    payload["scorer_mode"] = "exect_field_family_deterministic_v1"

    with pytest.raises(ValidationError, match="registered program variant"):
        ExperimentConfig.model_validate(payload)


def test_experiment_config_rejects_test_reporting_without_explicit_flag():
    payload = read_config_payload(
        "configs/experiments/test_holdout/exect_s5_v2b_gpt4_test.json"
    )
    payload["report_on_test_split"] = False

    with pytest.raises(ValidationError, match="report_on_test_split=true"):
        ExperimentConfig.model_validate(payload)


def test_experiment_config_rejects_conflicting_taxonomy_and_exemption():
    payload = read_config_payload(
        "configs/experiments/"
        "gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini.json"
    )
    payload["taxonomy_exemption"] = "legacy_registry"

    with pytest.raises(ValidationError):
        ExperimentConfig.model_validate(payload)
