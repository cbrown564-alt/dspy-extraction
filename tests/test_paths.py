from pathlib import Path

from clinical_extraction.paths import resolve_config_path, resolve_run_directory


def test_resolve_config_path_prefers_active_config(tmp_path: Path):
    active = tmp_path / "configs" / "experiments" / "example.json"
    archived = tmp_path / "archive" / "configs" / "example.json"
    active.parent.mkdir(parents=True)
    archived.parent.mkdir(parents=True)
    active.write_text("{}", encoding="utf-8")
    archived.write_text("{}", encoding="utf-8")

    resolved = resolve_config_path(
        Path("configs/experiments/example.json"),
        root=tmp_path,
    )

    assert resolved == active


def test_resolve_config_path_falls_back_to_archive_config_by_name(tmp_path: Path):
    archived = tmp_path / "archive" / "configs" / "historical.json"
    archived.parent.mkdir(parents=True)
    archived.write_text("{}", encoding="utf-8")

    resolved = resolve_config_path(
        Path("configs/experiments/historical.json"),
        root=tmp_path,
    )

    assert resolved == archived


def test_resolve_run_directory_falls_back_to_archive_exact_match(tmp_path: Path):
    archived = tmp_path / "archive" / "runs" / "historical_run"
    archived.mkdir(parents=True)

    resolved = resolve_run_directory(
        Path("runs/historical_run"),
        root=tmp_path,
    )

    assert resolved == archived


def test_resolve_run_directory_keeps_latest_prefix_match_order(tmp_path: Path):
    first = tmp_path / "runs" / "experiment_20260520T010000Z"
    latest = tmp_path / "runs" / "experiment_20260520T020000Z"
    first.mkdir(parents=True)
    latest.mkdir(parents=True)

    resolved = resolve_run_directory(
        Path("runs/experiment"),
        root=tmp_path,
        allow_prefix_match=True,
    )

    assert resolved == latest
