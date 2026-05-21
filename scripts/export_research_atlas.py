"""Generate registry-derived research evidence views.

Usage:
    uv run python scripts/export_research_atlas.py
    uv run python scripts/export_research_atlas.py --output-dir docs/research_atlas
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / "docs" / "experiments" / "synthesis" / "experiment_registry.json"
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "research_atlas"

DECISION_OUTCOMES = ("promote", "freeze", "hold", "reject", "superseded", "pending", "exploratory")
OUTCOME_PRIORITY = {
    "promote": 0,
    "freeze": 1,
    "hold": 2,
    "pending": 3,
    "exploratory": 4,
    "superseded": 5,
    "reject": 6,
    "pending_backfill": 7,
}
STUDY_TYPE_BY_FACTOR = {
    "program_architecture": "Architecture",
    "hybrid_balance_class": "Architecture",
    "interleaving_position": "Interleaving",
    "knowledge_source_position": "Interleaving",
    "prompt_policy": "Prompt policy",
    "optimizer_strategy": "Optimization",
    "model_track": "Model",
    "schema_complexity": "Schema ladder",
    "run_scope": "Scale",
    "normalization_strategy": "Normalization",
    "verification_strategy": "Verification",
    "evidence_strategy": "Evidence",
    "control_mode": "Control",
    "multi_factor": "Multi-factor",
    "pending_backfill": "Unclassified",
}
STUDY_COLUMNS = [
    "Architecture",
    "Interleaving",
    "Prompt policy",
    "Optimization",
    "Model",
    "Schema ladder",
    "Scale",
    "Verification",
    "Evidence",
]
SCHEMA_ORDER = {
    "gan_s0": 0,
    "exect_s1": 1,
    "exect_s2": 2,
    "exect_s3": 3,
    "exect_s4": 4,
    "pending_backfill": 99,
}


def _join(values: list[str] | None) -> str:
    if not values:
        return "-"
    return ", ".join(values)


def _format_metric(row: dict) -> str:
    hm = row.get("headline_metric") or {}
    name = hm.get("name")
    value = hm.get("value")
    if name is None or value is None:
        return "-"
    if isinstance(value, (int, float)) and 0 <= value <= 1:
        return f"{name}={value * 100:.1f}%"
    return f"{name}={value}"


def _curated_rows(reg: dict) -> list[dict]:
    rows = []
    for row in reg.get("experiments", []):
        group = row.get("comparison_group") or ""
        if not group or group == "pending_backfill":
            continue
        rows.append(row)
    return rows


def _best_row(rows: list[dict]) -> dict:
    def key(row: dict) -> tuple[int, int, str]:
        scope_rank = {
            "test_holdout": 0,
            "full_validation": 1,
            "cap100": 2,
            "cap25": 3,
            "slice": 4,
            "smoke": 5,
        }.get(row.get("run_scope", ""), 9)
        return (
            OUTCOME_PRIORITY.get(row.get("outcome", "pending_backfill"), 99),
            scope_rank,
            row.get("experiment_id", ""),
        )

    return sorted(rows, key=key)[0]


def _node_id(text: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]+", "_", text)
    clean = clean.strip("_")
    return clean[:48] or "node"


def _study_type(row: dict) -> str:
    factor = row.get("varied_factor") or "pending_backfill"
    return STUDY_TYPE_BY_FACTOR.get(factor, "Other")


def _decision_class(outcome: str) -> str:
    if outcome in {"promote", "freeze", "hold", "reject", "superseded", "pending", "exploratory"}:
        return outcome
    return "pending"


def render_journey_mermaid(reg: dict) -> str:
    rows = _curated_rows(reg)
    counts = Counter(row.get("dataset", "unknown") for row in rows)
    promoted_gan = sum(1 for row in rows if row.get("dataset") == "gan_2026" and row.get("outcome") == "promote")
    frozen_exect = sum(1 for row in rows if row.get("dataset") == "exect_v2" and row.get("outcome") == "freeze")
    qwen_rows = sum(1 for row in rows if row.get("model_track") == "qwen35b")
    lines = [
        "flowchart LR",
        '  foundation["Foundation: loaders, splits, scorers"]',
        f'  gan["Gan S0 architecture search ({counts.get("gan_2026", 0)} curated rows)"]',
        f'  gan_promoted["Gan temporal-candidates promoted ({promoted_gan} anchors)"]',
        '  exect_policy["ExECT S1 label-policy tuning"]',
        f'  exect_ladder["ExECT S1-S4 schema ladder frozen ({frozen_exect} anchors)"]',
        f'  qwen["Qwen local replication ({qwen_rows} curated rows)"]',
        '  primitives["Taxonomy-governed primitive probes"]',
        '  frontier["Current frontier: preregistered narrow mechanisms"]',
        "  foundation --> gan --> gan_promoted",
        "  foundation --> exect_policy --> exect_ladder --> qwen --> primitives --> frontier",
        "  gan_promoted --> primitives",
        "  classDef anchor fill:#d8f3dc,stroke:#2d6a4f,color:#081c15;",
        "  classDef hold fill:#fff3bf,stroke:#cc8f00,color:#201400;",
        "  classDef frontier fill:#dbeafe,stroke:#2563eb,color:#0f172a;",
        "  class gan_promoted,exect_ladder anchor;",
        "  class qwen hold;",
        "  class frontier frontier;",
    ]
    return "\n".join(lines) + "\n"


def render_decision_map_mermaid(reg: dict) -> str:
    rows = _curated_rows(reg)
    by_group: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_group[row["comparison_group"]].append(row)

    lines = [
        "flowchart TD",
        '  gan["Gan S0"]',
        '  exect["ExECT"]',
    ]
    class_assignments: list[tuple[str, str]] = []

    for group in sorted(by_group):
        group_rows = by_group[group]
        best = _best_row(group_rows)
        outcomes = Counter(row.get("outcome", "pending") for row in group_rows)
        outcome_summary = ", ".join(
            f"{name}:{outcomes[name]}" for name in DECISION_OUTCOMES if outcomes.get(name)
        )
        metric = _format_metric(best)
        label = f"{group}\\n{outcome_summary}\\nanchor: {metric}"
        node = _node_id(group)
        lines.append(f'  {node}["{label}"]')
        parent = "gan" if best.get("dataset") == "gan_2026" else "exect"
        lines.append(f"  {parent} --> {node}")
        class_assignments.append((node, _decision_class(best.get("outcome", "pending"))))

    lines.extend(
        [
            "  classDef promote fill:#d8f3dc,stroke:#2d6a4f,color:#081c15;",
            "  classDef freeze fill:#e0f2fe,stroke:#0369a1,color:#0c4a6e;",
            "  classDef hold fill:#fff3bf,stroke:#cc8f00,color:#201400;",
            "  classDef reject fill:#fee2e2,stroke:#b91c1c,color:#450a0a;",
            "  classDef superseded fill:#e5e7eb,stroke:#6b7280,color:#111827;",
            "  classDef exploratory fill:#f3e8ff,stroke:#7e22ce,color:#3b0764;",
            "  classDef pending fill:#f8fafc,stroke:#64748b,color:#0f172a;",
        ]
    )
    for node, klass in class_assignments:
        lines.append(f"  class {node} {klass};")
    return "\n".join(lines) + "\n"


def render_evidence_matrix(reg: dict) -> str:
    rows = _curated_rows(reg)
    buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    schemas = set()
    for row in rows:
        schema = row.get("schema_complexity") or "pending_backfill"
        study = _study_type(row)
        schemas.add(schema)
        buckets[(schema, study)].append(row)

    lines = [
        "# Evidence Matrix",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Each cell shows the strongest registered row for that schema and study type. "
        "Use this as a navigation surface, not as a claim that unlike cells are directly comparable.",
        "",
        "| Schema | " + " | ".join(STUDY_COLUMNS) + " |",
        "| --- | " + " | ".join("---" for _ in STUDY_COLUMNS) + " |",
    ]
    for schema in sorted(schemas, key=lambda s: (SCHEMA_ORDER.get(s, 50), s)):
        cells = []
        for study in STUDY_COLUMNS:
            cell_rows = buckets.get((schema, study), [])
            if not cell_rows:
                cells.append("-")
                continue
            best = _best_row(cell_rows)
            short_id = best.get("experiment_id", "").replace("_gpt4_1_mini", "").replace("_qwen35b", "")
            cells.append(
                f"`{short_id}`<br>{best.get('outcome', '-')}<br>{_format_metric(best)}"
            )
        lines.append(f"| {schema} | " + " | ".join(cells) + " |")

    lines.extend(
        [
            "",
            "## Reading Notes",
            "",
            "- Rows summarize registered local diagnostics, not published benchmark reproduction.",
            "- Prefer within-cell decision docs and comparison groups before making metric claims.",
            "- Empty cells are useful: they mark open or intentionally deferred paths.",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_atlas_index(output_dir: Path) -> str:
    return "\n".join(
        [
            "# Research Atlas",
            "",
            "- [Journey](research_atlas/journey.mmd)",
            "- [Decision map](research_atlas/decision_map.mmd)",
            "- [Evidence matrix](research_atlas/evidence_matrix.md)",
            "- [Open frontiers](research_atlas/open_frontiers.md)",
            "",
            "Generated from the experiment registry.",
            "",
        ]
    )


def _render_open_frontiers(kanban: str) -> str:
    marker = "## Recommended Next Pull"
    if marker not in kanban:
        return "# Open Frontiers\n\nNo `Recommended Next Pull` section found in the Kanban.\n"
    return "# Open Frontiers\n\n" + kanban[kanban.index(marker) :]


def write_atlas(
    reg: dict,
    output_dir_or_kanban: Path | str,
    output_dir: Path | None = None,
    index_path: Path | None = None,
) -> None:
    if output_dir is None:
        kanban = None
        output_dir = Path(output_dir_or_kanban)
    else:
        kanban = str(output_dir_or_kanban)

    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        output_dir / "journey.mmd": render_journey_mermaid(reg),
        output_dir / "decision_map.mmd": render_decision_map_mermaid(reg),
        output_dir / "evidence_matrix.md": render_evidence_matrix(reg),
    }
    if kanban is not None:
        files[output_dir / "open_frontiers.md"] = _render_open_frontiers(kanban)
    if index_path is not None:
        files[index_path] = _render_atlas_index(output_dir)
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export registry-derived research evidence views.")
    parser.add_argument("--registry", type=Path, default=REG_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    reg = json.loads(args.registry.read_text(encoding="utf-8"))
    write_atlas(reg, args.output_dir)
    print(f"Wrote research evidence views to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
