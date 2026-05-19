"""Gan S0 Qwen error-regression slice fixture helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_SLICE_PATH = Path("data/fixtures/gan_s0_qwen_error_regression_slice.json")


def load_gan_qwen_error_regression_slice(
    path: Path = DEFAULT_SLICE_PATH,
) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not payload.get("records"):
        raise ValueError(f"{path} must define a non-empty records list.")
    return payload


def gan_qwen_error_regression_record_ids(
    path: Path = DEFAULT_SLICE_PATH,
) -> list[str]:
    payload = load_gan_qwen_error_regression_slice(path)
    return [entry["record_id"] for entry in payload["records"]]


def gan_qwen_error_regression_failure_modes(
    path: Path = DEFAULT_SLICE_PATH,
) -> dict[str, str]:
    payload = load_gan_qwen_error_regression_slice(path)
    return {
        entry["record_id"]: entry["failure_mode"]
        for entry in payload["records"]
    }
