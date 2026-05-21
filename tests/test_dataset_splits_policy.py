import json
from pathlib import Path

import pytest

from clinical_extraction.paths import PROJECT_ROOT

SPLIT_FILES = (
    PROJECT_ROOT / "data" / "splits" / "exectv2_splits.json",
    PROJECT_ROOT / "data" / "splits" / "gan_2026_splits.json",
)


@pytest.mark.parametrize("split_file", SPLIT_FILES, ids=lambda p: p.name)
def test_fixed_split_files_use_train_not_development(split_file: Path) -> None:
    payload = json.loads(split_file.read_text(encoding="utf-8"))
    assert "development" not in payload
    assert "train" in payload
    assert payload["counts"]["train"] == len(payload["train"])
    assert set(payload["counts"]) == {"train", "validation", "test"}
