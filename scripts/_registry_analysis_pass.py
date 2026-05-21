"""One-off registry analysis for taxonomy synthesis pass."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / "docs" / "experiments" / "synthesis" / "experiment_registry.json"


def hybrid_key(row: dict) -> str:
    return ",".join(sorted(row.get("hybrid_balance_class") or []))


def main() -> None:
    reg = json.loads(REG_PATH.read_text(encoding="utf-8"))
    rows = reg["experiments"]

    groups: dict[tuple, list[str]] = defaultdict(list)
    for row in rows:
        key = (
            row["dataset"],
            row["schema_complexity"],
            row["model_track"],
            row["program_architecture"],
            hybrid_key(row),
            row["outcome"],
        )
        groups[key].append(row["experiment_id"])

    print("=== REGISTRY SUMMARY ===")
    print(f"Total rows: {len(rows)}")
    print(f"Unique dimension tuples: {len(groups)}")
    print()

    by_outcome: dict[str, int] = defaultdict(int)
    by_dataset_outcome: dict[tuple, int] = defaultdict(int)
    for row in rows:
        by_outcome[row["outcome"]] += 1
        by_dataset_outcome[(row["dataset"], row["outcome"])] += 1

    print("By outcome:", dict(sorted(by_outcome.items())))
    print("By dataset x outcome:")
    for key, count in sorted(by_dataset_outcome.items()):
        print(f"  {key}: {count}")
    print()

    print("Top dimension tuples (count >= 2):")
    for key, ids in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        if len(ids) < 2:
            continue
        ds, schema, model, arch, hybrid, outcome = key
        print(f"  n={len(ids)} | {ds} | {schema} | {model} | {arch} | {hybrid} | {outcome}")

    for cg in (
        "gan_s0_architecture_gpt_validation_v1",
        "gan_s0_architecture_qwen_validation_v1",
    ):
        print(f"\n=== {cg} ===")
        matched = []
        for row in rows:
            cgs = row.get("comparison_groups") or []
            if row.get("comparison_group") == cg or cg in cgs:
                matched.append(row)
        for row in sorted(matched, key=lambda r: (r["program_architecture"], r["outcome"])):
            hm = row.get("headline_metric") or {}
            print(f"  {row['experiment_id']}")
            print(
                f"    arch={row['program_architecture']} "
                f"hybrid={row.get('hybrid_balance_class')} "
                f"outcome={row['outcome']}"
            )
            print(f"    metric={hm.get('name')}={hm.get('value')}")

    print("\n=== ExECT GPT S1-S4 freeze (full_validation) ===")
    for row in rows:
        if (
            row["dataset"] == "exect_v2"
            and row["model_track"] == "gpt4_1_mini"
            and row["schema_complexity"] in ("exect_s1", "exect_s2", "exect_s3", "exect_s4")
            and row.get("run_scope") == "full_validation"
            and row["outcome"] in ("freeze", "hold", "promote")
        ):
            hm = row.get("headline_metric") or {}
            print(
                f"  {row['experiment_id']} schema={row['schema_complexity']} "
                f"outcome={row['outcome']} {hm.get('name')}={hm.get('value')}"
            )

    print("\n=== ExECT Qwen S1-S3 hold (full_validation) ===")
    for row in rows:
        if (
            row["dataset"] == "exect_v2"
            and row["model_track"] == "qwen35b"
            and row["schema_complexity"] in ("exect_s1", "exect_s2", "exect_s3")
            and row.get("run_scope") == "full_validation"
            and row["outcome"] in ("freeze", "hold", "promote")
        ):
            hm = row.get("headline_metric") or {}
            print(
                f"  {row['experiment_id']} schema={row['schema_complexity']} "
                f"outcome={row['outcome']} {hm.get('name')}={hm.get('value')}"
            )

    print("\n=== ReAct H3 probe ===")
    for row in rows:
        if "react_temporal_tools" in row["experiment_id"]:
            subset = {
                k: row[k]
                for k in (
                    "experiment_id",
                    "outcome",
                    "comparison_group",
                    "hybrid_balance_class",
                    "canonical_run_id",
                    "headline_metric",
                )
                if k in row
            }
            print(json.dumps(subset, indent=2))

    print("\n=== pending_backfill in named comparison groups ===")
    for row in rows:
        cg = row.get("comparison_group", "")
        if cg != "pending_backfill" and row.get("varied_factor") == "pending_backfill":
            print(f"  {row['experiment_id']} -> {cg}")


if __name__ == "__main__":
    main()
