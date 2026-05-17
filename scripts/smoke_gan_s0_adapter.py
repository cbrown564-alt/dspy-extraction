from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.llms import LLMProviderConfig, build_chat_adapter
from clinical_extraction.programs.gan_frequency_s0 import (
    GanFrequencyS0Program,
    build_gan_frequency_s0_extractor,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Opt-in smoke run for the Gan S0 provider adapter contract.",
    )
    parser.add_argument("--config", required=True, help="Path to model config JSON.")
    parser.add_argument(
        "--record-id",
        help="Gan record id to run. Defaults to the first loaded record.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for the PredictionSet JSON artifact.",
    )
    args = parser.parse_args(argv)

    config = LLMProviderConfig.model_validate_json(
        Path(args.config).read_text(encoding="utf-8")
    )
    adapter = build_chat_adapter(config)
    program = GanFrequencyS0Program(
        extractor=build_gan_frequency_s0_extractor(adapter),
        model_provider=adapter.provider,
        model_name=adapter.model,
    )
    records = load_gan_records()
    if args.record_id:
        records = [record for record in records if record.record_id == args.record_id]
        if not records:
            raise SystemExit(f"No Gan record found for record id {args.record_id!r}.")
    else:
        records = records[:1]

    prediction_set = program.predict_records(records)
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
