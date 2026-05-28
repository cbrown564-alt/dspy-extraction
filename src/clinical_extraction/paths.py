from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
EXECT_ROOT = DATA_ROOT / "ExECTv2 (2025)"
GAN_ROOT = DATA_ROOT / "Gan (2026)"
RUNS_ROOT = PROJECT_ROOT / "runs"
CONFIGS_ROOT = PROJECT_ROOT / "configs"
EXPERIMENT_CONFIGS_ROOT = CONFIGS_ROOT / "experiments"
ARCHIVE_ROOT = PROJECT_ROOT / "archive"
ARCHIVE_CONFIGS_ROOT = ARCHIVE_ROOT / "configs"
ARCHIVE_RUNS_ROOT = ARCHIVE_ROOT / "runs"


def _repo_root(root: Path | None = None) -> Path:
    return (root or PROJECT_ROOT).resolve()


def resolve_config_path(path: str | Path, *, root: Path | None = None) -> Path:
    """Resolve an experiment config from active configs or the flat archive."""

    base = _repo_root(root)
    config_path = Path(path)
    if config_path.is_absolute():
        primary = config_path
        candidates = [primary]
    else:
        primary = base / config_path
        candidates = [primary]
        if len(config_path.parts) == 1:
            candidates.append(base / "configs" / "experiments" / config_path.name)

    candidates.append(base / "archive" / "configs" / config_path.name)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return primary


def resolve_run_directory(
    path: str | Path,
    *,
    root: Path | None = None,
    runs_root: Path | None = None,
    allow_prefix_match: bool = False,
) -> Path:
    """Resolve a run directory from active runs or archived runs."""

    if runs_root is not None:
        active_runs_root = runs_root.resolve()
        base = active_runs_root.parent
    else:
        base = _repo_root(root)
        active_runs_root = base / "runs"
    archive_runs_root = base / "archive" / "runs"

    run_path = Path(path)
    if run_path.is_absolute():
        primary = run_path
    elif len(run_path.parts) == 1:
        primary = active_runs_root / run_path.name
    else:
        primary = base / run_path

    candidates = [
        primary,
        archive_runs_root / run_path.name,
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate

    if allow_prefix_match:
        for search_root in (active_runs_root, archive_runs_root):
            matches = sorted(
                candidate
                for candidate in search_root.glob(f"{run_path.name}*")
                if candidate.is_dir()
            )
            if len(matches) == 1:
                return matches[0]
            if matches:
                return matches[-1]

    return primary
