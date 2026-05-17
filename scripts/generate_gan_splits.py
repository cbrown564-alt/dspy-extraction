from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.paths import PROJECT_ROOT
from clinical_extraction.splits import make_gan_splits


def main() -> None:
    splits = make_gan_splits(load_gan_records())
    output_path = PROJECT_ROOT / "data" / "splits" / "gan_2026_splits.json"
    output_path.write_text(json.dumps(splits, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
