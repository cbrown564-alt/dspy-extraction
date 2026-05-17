"""Opt-in smoke run for the Gan S0 DSPy program contract against a real provider.

Usage:
    uv run python scripts/smoke_gan_s0_adapter.py \\
        --config configs/models/gan_s0_gpt4_1_mini.json \\
        --env-file .env
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import dspy

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.llms import LLMProviderConfig, build_dspy_lm
from clinical_extraction.programs.gan_frequency_s0 import (
    GanFrequencyS0Module,
    predict_gan_records,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Opt-in smoke run for the Gan S0 DSPy program against a real provider.",
    )
    parser.add_argument("--config", required=True, help="Path to model config JSON.")
    parser.add_argument("--record-id", help="Gan record ID to run. Defaults to first record.")
    parser.add_argument("--output", type=Path, help="Optional path for PredictionSet JSON.")
    parser.add_argument("--env-file", type=Path, help="Load API keys from .env file.")
    args = parser.parse_args(argv)

    if args.env_file:
        import os
        for line in args.env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("\"'")
            if key and key not in os.environ:
                os.environ[key] = value

    model_config = LLMProviderConfig.model_validate_json(
        Path(args.config).read_text(encoding="utf-8")
    )
    lm = build_dspy_lm(model_config)
    dspy.configure(lm=lm)

    module = GanFrequencyS0Module()
    records = load_gan_records()
    if args.record_id:
        records = [r for r in records if r.record_id == args.record_id]
        if not records:
            raise SystemExit(f"No Gan record found for record ID {args.record_id!r}.")
    else:
        records = records[:1]

    prediction_set = predict_gan_records(
        module,
        records,
        model_provider=model_config.provider,
        model_name=model_config.model,
    )
    payload = prediction_set.model_dump(mode="json")

    if args.output:
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
