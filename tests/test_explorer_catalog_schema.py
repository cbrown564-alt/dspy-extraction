from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "exect-explorer" / "scripts"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


catalog_shared = _load_module("catalog_shared", SCRIPTS / "catalog_shared.py")
build_exect = _load_module("build_model_catalog", SCRIPTS / "build_model_catalog.py")
build_gan = _load_module("build_model_catalog_gan", SCRIPTS / "build_model_catalog_gan.py")


def test_exect_catalog_matches_shared_envelope():
    catalog = build_exect.build_exect_catalog()
    catalog_shared.validate_catalog_envelope(catalog)
    assert catalog["dataset"] == "exect_v2"
    assert catalog["artifact_class"] == "explorer_model_catalog"
    assert catalog["metric_labels"]["micro_f1"] == "Micro F1"
    assert len(catalog["tasks"]) == 5
    assert len(catalog["runs"]) == 10


def test_gan_catalog_matches_shared_envelope():
    catalog = build_gan.build_gan_catalog()
    catalog_shared.validate_catalog_envelope(catalog)
    assert catalog["dataset"] == "gan_2026"
    assert catalog["artifact_class"] == "explorer_model_catalog"
    assert catalog["metric_labels"]["micro_f1"] == "Monthly accuracy"
    assert len(catalog["tasks"]) == 1
    assert len(catalog["runs"]) == 2


def test_pipeline_step_shape_is_shared():
    exect_catalog = build_exect.build_exect_catalog()
    gan_catalog = build_gan.build_gan_catalog()
    exect_step = next(iter(exect_catalog["runs"][0]["documents"].values()))["pipeline"][0]
    gan_step = next(iter(gan_catalog["runs"][0]["documents"].values()))["pipeline"][0]
    assert set(exect_step) == set(gan_step)
    assert set(exect_step["deterministic_step"]) == {"label", "output", "metadata"}
