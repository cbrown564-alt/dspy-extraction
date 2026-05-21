"""Export a paper-ready markdown matrix from docs/experiments/synthesis/experiment_registry.json.

Usage:
    uv run python scripts/export_experiment_registry_matrix.py
    uv run python scripts/export_experiment_registry_matrix.py --mode decided
    uv run python scripts/export_experiment_registry_matrix.py --output docs/custom_matrix.md
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / "docs" / "experiments" / "synthesis" / "experiment_registry.json"
DEFAULT_OUTPUT = ROOT / "docs" / "experiments" / "synthesis" / "experiment_registry_matrix_20260520.md"

DECIDED_OUTCOMES = frozenset({"promote", "freeze", "hold", "reject", "superseded"})


def _join(values: list[str] | None) -> str:
    if not values:
        return "—"
    return ", ".join(values)


def _format_metric(row: dict) -> str:
    hm = row.get("headline_metric") or {}
    name = hm.get("name")
    value = hm.get("value")
    if name is None or value is None:
        return "—"
    if isinstance(value, (int, float)) and 0 <= value <= 1:
        return f"{name}={value * 100:.1f}%"
    return f"{name}={value}"


def _sort_key(row: dict) -> tuple:
    return (
        row.get("comparison_group") or "",
        row.get("dataset") or "",
        row.get("schema_complexity") or "",
        row.get("model_track") or "",
        row.get("run_scope") or "",
        row.get("program_architecture") or "",
        _join(row.get("hybrid_balance_class")),
        row.get("experiment_id") or "",
    )


def _filter_rows(rows: list[dict], mode: str) -> list[dict]:
    if mode == "all":
        return list(rows)
    curated: list[dict] = []
    for row in rows:
        cg = row.get("comparison_group") or ""
        if cg in ("", "pending_backfill"):
            continue
        if mode == "decided":
            if row.get("outcome") not in DECIDED_OUTCOMES:
                continue
        elif mode == "curated":
            if not row.get("decision_doc"):
                continue
        else:
            raise ValueError(f"unknown mode: {mode}")
        curated.append(row)
    return curated


def _table_header() -> list[str]:
    return [
        "| Experiment | Dataset | Schema | Model | Architecture | Hybrid | "
        "Interleave | Scope | Outcome | Headline metric | Decision doc |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]


def _table_row(row: dict) -> str:
    exp_id = row.get("experiment_id", "")
    short_id = exp_id.replace("_gpt4_1_mini", "").replace("_qwen35b", "")
    doc = row.get("decision_doc") or ""
    doc_link = f"[inspection]({doc})" if doc else "—"
    return (
        f"| `{short_id}` | {row.get('dataset', '—')} | {row.get('schema_complexity', '—')} | "
        f"{row.get('model_track', '—')} | {row.get('program_architecture', '—')} | "
        f"{_join(row.get('hybrid_balance_class'))} | {_join(row.get('interleaving_positions'))} | "
        f"{row.get('run_scope', '—')} | **{row.get('outcome', '—')}** | {_format_metric(row)} | "
        f"{doc_link} |"
    )


def render_matrix(reg: dict, mode: str) -> str:
    rows = sorted(_filter_rows(reg["experiments"], mode), key=_sort_key)
    generated = date.today().isoformat()
    lines = [
        "# Experiment Registry Matrix (Paper-Ready Export)",
        "",
        f"**Generated:** {generated}  ",
        f"**Source:** `docs/experiments/synthesis/experiment_registry.json` (registry_rows={len(reg['experiments'])})  ",
        f"**Filter mode:** `{mode}`  ",
        f"**Exported rows:** {len(rows)}",
        "",
        "Grouped by `comparison_group`, then dataset, schema, model, and run scope. "
        "Compare rows only within the same comparison group and respect `metric_caveats` "
        "on each registry row.",
        "",
        "## Caveats",
        "",
    ]
    for caveat in reg.get("caveats") or []:
        lines.append(f"- {caveat}")
    lines.extend(
        [
            "- This table is for methods/results drafting; it is not published ExECTv2 Table 1 "
            "or Gan Real-set reproduction.",
            "- Regenerate after registry updates: "
            "`uv run python scripts/export_experiment_registry_matrix.py`.",
            "",
        ]
    )

    by_group: dict[str, list[dict]] = {}
    for row in rows:
        by_group.setdefault(row.get("comparison_group") or "ungrouped", []).append(row)

    for group in sorted(by_group):
        group_rows = by_group[group]
        lines.append(f"## {group}")
        lines.append("")
        lines.append(f"Rows: {len(group_rows)}")
        lines.append("")
        lines.extend(_table_header())
        for row in group_rows:
            lines.append(_table_row(row))
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export experiment registry matrix markdown.")
    parser.add_argument(
        "--mode",
        choices=("curated", "decided", "all"),
        default="curated",
        help="curated: named comparison_group + decision_doc; "
        "decided: curated outcomes only; all: every registry row.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output markdown path.",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=REG_PATH,
        help="Registry JSON path.",
    )
    args = parser.parse_args(argv)

    reg = json.loads(args.registry.read_text(encoding="utf-8"))
    markdown = render_matrix(reg, args.mode)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(f"Wrote {len(_filter_rows(reg['experiments'], args.mode))} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
