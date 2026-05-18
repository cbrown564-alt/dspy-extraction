from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.kanban import write_visual_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Kanban visual monitoring artifacts.")
    parser.add_argument(
        "--plan",
        type=Path,
        default=Path("docs/kanban_plan.md"),
        help="Path to the Markdown Kanban plan.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/kanban"),
        help="Directory for generated JSON, Mermaid, and HTML artifacts.",
    )
    args = parser.parse_args()

    outputs = write_visual_artifacts(args.plan, args.output_dir)
    for kind, path in outputs.items():
        print(f"{kind}: {path}")


if __name__ == "__main__":
    main()
