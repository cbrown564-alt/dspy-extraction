"""Tests for dataset backends and runner dry-run behavior."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from clinical_extraction.experiments.backends import BACKENDS, get_backend
from clinical_extraction.experiments.config import load_experiment_config
from clinical_extraction.experiments.runner import (
    gepa_reflection_config,
    resolve_split_record_ids,
    run_experiment,
)
from clinical_extraction.llms import LLMProviderConfig
from clinical_extraction.paths import PROJECT_ROOT
from scripts.run_experiment import main

PROMPTS_FIXTURES = PROJECT_ROOT / "tests" / "fixtures" / "experiment_prompts"


@pytest.mark.parametrize(
    ("dataset", "backend_class"),
    [
        ("gan_2026", "GanExperimentBackend"),
        ("exect_v2", "ExectExperimentBackend"),
    ],
)
def test_backend_registry_resolves_known_datasets(dataset, backend_class):
    backend = get_backend(dataset)
    assert backend.dataset == dataset
    assert type(backend).__name__ == backend_class


def test_get_backend_preserves_unsupported_dataset_error_message():
    with pytest.raises(SystemExit, match="Unsupported dataset: 'unknown'"):
        get_backend("unknown")


def test_gan_backend_load_records_by_id_returns_record_id_index():
    backend = get_backend("gan_2026")
    records = backend.load_records_by_id()
    assert records
    first = next(iter(records.values()))
    assert first.record_id in records


def test_exect_backend_load_records_by_id_returns_document_id_index():
    backend = get_backend("exect_v2")
    records = backend.load_records_by_id()
    assert records
    first = next(iter(records.values()))
    assert first.document_id in records


@pytest.mark.parametrize(
    "config_path",
    [
        Path("configs/experiments/gan_s0_baseline_gpt4_1_mini.json"),
        Path("configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json"),
    ],
)
def test_dry_run_smoke_prints_plan_without_creating_run_directory(
    config_path: Path,
    tmp_path: Path,
    capsys,
):
    exit_code = main(
        [
            "--experiment",
            str(config_path),
            "--dry-run",
        ]
    )
    captured = capsys.readouterr().out

    assert exit_code == 0
    config = load_experiment_config(config_path)
    assert config.experiment_id in captured
    assert config.dataset in captured
    assert config.split_name in captured
    assert str(config.model_config_path) in captured
    assert "Dry run" in captured
    assert not any(tmp_path.iterdir()) if tmp_path.exists() else True


@pytest.mark.parametrize(
    "config_path",
    [
        Path("configs/experiments/gan_s0_baseline_gpt4_1_mini.json"),
        Path("configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json"),
    ],
)
def test_run_experiment_library_api_dry_run_smoke(config_path: Path, capsys):
    exit_code = run_experiment(config_path, dry_run=True)
    captured = capsys.readouterr().out

    assert exit_code == 0
    config = load_experiment_config(config_path)
    assert config.experiment_id in captured
    assert "Dry run" in captured



def test_resolve_split_record_ids_preserves_split_order_with_max_records():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_baseline_gpt4_1_mini.json")
    ).model_copy(update={"max_records": 3})
    record_ids = resolve_split_record_ids(config)
    assert len(record_ids) == 3


def test_backends_registry_contains_both_datasets():
    assert set(BACKENDS) == {"gan_2026", "exect_v2"}


def test_gan_backend_prompts_data_matches_baseline_contract():
    config = load_experiment_config(
        Path("configs/experiments/gan_s0_baseline_gpt4_1_mini.json")
    )
    prompts = get_backend("gan_2026").prompts_data(config)
    assert prompts["signature"] == "GanFrequencyS0Signature"
    assert prompts["module"] == "GanFrequencyS0Module"
    assert prompts["program_variant"] == config.program_variant


def test_exect_backend_prompts_data_matches_s1_smoke_contract():
    config = load_experiment_config(
        Path("configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json")
    )
    prompts = get_backend("exect_v2").prompts_data(config)
    assert prompts["signature"] == "ExectS0S1FieldFamilySignature"
    assert prompts["field_families"]
    assert prompts["label_policy_guidance"]


@pytest.mark.parametrize(
    ("config_path", "fixture_name"),
    [
        (
            Path("configs/experiments/gan_s0_baseline_gpt4_1_mini.json"),
            "gan_s0_baseline_gpt4_1_mini.prompts.json",
        ),
        (
            Path("configs/experiments/gan_s0_validation_ladder_v0_cap25_gpt4_1_mini.json"),
            "gan_s0_temporal_candidates_single_pass.prompts.json",
        ),
        (
            Path("configs/experiments/exect_s0_s1_smoke_gpt4_1_mini.json"),
            "exect_s0_s1_smoke_gpt4_1_mini.prompts.json",
        ),
        (
            Path("configs/experiments/exect_s4_smoke_gpt4_1_mini.json"),
            "exect_s4_smoke_gpt4_1_mini.prompts.json",
        ),
    ],
)
def test_backend_prompts_data_matches_golden_fixture(config_path: Path, fixture_name: str):
    config = load_experiment_config(config_path)
    expected = json.loads((PROMPTS_FIXTURES / fixture_name).read_text(encoding="utf-8"))
    actual = get_backend(config.dataset).prompts_data(config)
    assert actual == expected


def test_mock_runner_writes_full_artifact_layout_contract(tmp_path):
    config_path = Path("configs/experiments/gan_s0_baseline_gpt4_1_mini.json")
    config = load_experiment_config(config_path)
    run_config_path = tmp_path / "config.json"
    run_config_path.write_text(
        json.dumps(
            {
                **config.model_dump(mode="json"),
                "max_records": 1,
                "output_root": str(tmp_path / "runs"),
            }
        ),
        encoding="utf-8",
    )

    prediction_set = MagicMock()
    prediction_set.model_dump.return_value = {"predictions": [], "dataset": "gan_2026"}
    report = {
        "dataset": "gan_2026",
        "counts": {"evaluated_records": 1},
        "benchmark_metrics": {},
        "diagnostic_metrics": {},
        "errors": {"record_1": ["example"]},
    }

    with patch("clinical_extraction.experiments.runner.build_dspy_lm") as build_lm, patch(
        "clinical_extraction.experiments.gan_backend.predict_gan_records",
        return_value=prediction_set,
    ), patch(
        "clinical_extraction.experiments.gan_backend.evaluate_gan_predictions",
        return_value=report,
    ):
        build_lm.return_value = MagicMock(history=[])
        assert run_experiment(run_config_path, run_id="layout_run") == 0

    run_dir = tmp_path / "runs" / "layout_run"
    assert (run_dir / "metadata.json").is_file()
    assert (run_dir / "config.json").is_file()
    assert (run_dir / "prompts.json").is_file()
    assert (run_dir / "predictions.json").is_file()
    assert (run_dir / "metrics.json").is_file()
    assert (run_dir / "errors.json").is_file()
    assert (run_dir / "artifacts").is_dir()
    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["artifact_paths"]["compiled_state"] == "artifacts/compiled_state.json"
    assert metadata["artifact_paths"]["optimizer_artifacts"] == "artifacts/optimizer"
    assert metadata["artifact_paths"]["optimizer_logs"] == "artifacts/optimizer/logs"
    assert (run_dir / "artifacts" / "optimizer" / "logs").is_dir()

    config_payload = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    prompts_payload = json.loads((run_dir / "prompts.json").read_text(encoding="utf-8"))
    predictions_payload = json.loads(
        (run_dir / "predictions.json").read_text(encoding="utf-8")
    )
    metrics_payload = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    errors_payload = json.loads((run_dir / "errors.json").read_text(encoding="utf-8"))

    assert config_payload["experiment_id"] == config.experiment_id
    assert {"signature", "module", "predictor", "program_variant", "prompt_version"} <= set(
        prompts_payload
    )
    assert "predictions" in predictions_payload
    assert {"dataset", "counts", "benchmark_metrics", "diagnostic_metrics", "runtime"} <= set(
        metrics_payload
    )
    assert errors_payload == report["errors"]


def test_mock_runner_writes_optimizer_artifacts_when_config_has_optimizer(tmp_path):
    config_path = Path("configs/experiments/gan_s0_synthesis_bootstrap_gpt4_1_mini.json")
    config = load_experiment_config(config_path)
    run_config_path = tmp_path / "config.json"
    run_config_path.write_text(
        json.dumps(
            {
                **config.model_dump(mode="json"),
                "max_records": 1,
                "output_root": str(tmp_path / "runs"),
            }
        ),
        encoding="utf-8",
    )

    prediction_set = MagicMock()
    prediction_set.model_dump.return_value = {"predictions": [], "dataset": "gan_2026"}
    report = {
        "dataset": "gan_2026",
        "counts": {"evaluated_records": 1},
        "benchmark_metrics": {},
        "diagnostic_metrics": {},
        "errors": {},
    }
    compiled_module = MagicMock()
    compiled_module.dump_state.return_value = {"compiled": True}

    with patch("clinical_extraction.experiments.runner.build_dspy_lm") as build_lm, patch(
        "clinical_extraction.experiments.gan_backend.compile_gan_s0_module",
        return_value=compiled_module,
    ) as compile_module, patch(
        "clinical_extraction.experiments.gan_backend.predict_gan_records",
        return_value=prediction_set,
    ), patch(
        "clinical_extraction.experiments.gan_backend.evaluate_gan_predictions",
        return_value=report,
    ):
        build_lm.return_value = MagicMock(history=[])
        assert run_experiment(run_config_path, run_id="optimizer_run") == 0
        compile_module.assert_called_once()

    run_dir = tmp_path / "runs" / "optimizer_run"
    assert (run_dir / "artifacts" / "compiled_state.json").is_file()
    assert (run_dir / "artifacts" / "optimizer" / "summary.json").is_file()
    prompts_payload = json.loads((run_dir / "prompts.json").read_text(encoding="utf-8"))
    assert prompts_payload["optimizer"]["name"] == "BootstrapFewShot"


def test_gepa_reflection_config_preserves_null_temperature():
    base = LLMProviderConfig(provider="openai", model="gpt-5.5", temperature=None)

    reflection = gepa_reflection_config(base)

    assert reflection.temperature is None


def test_gepa_reflection_config_uses_high_temperature_when_supported():
    base = LLMProviderConfig(provider="openai", model="gpt-4.1-mini", temperature=0.0)

    reflection = gepa_reflection_config(base)

    assert reflection.temperature == 1.0
