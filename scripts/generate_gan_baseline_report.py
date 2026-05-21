from __future__ import annotations

import json

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_baseline import (
    build_gan_deterministic_baseline_report,
)
from clinical_extraction.paths import PROJECT_ROOT


def main() -> None:
    report = build_gan_deterministic_baseline_report(load_gan_records())
    output_path = PROJECT_ROOT / "docs" / "datasets" / "gan" / "gan_deterministic_normalization_baseline.json"
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
