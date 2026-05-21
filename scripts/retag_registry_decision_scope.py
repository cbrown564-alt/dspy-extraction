"""Add decision_scope to curated high-value registry rows (Phase 1 inventory pass).

Curated = non-pending comparison_group + decision_doc present.
Only updates rows whose notes do not already contain decision_scope.

Usage:
    uv run python scripts/retag_registry_decision_scope.py
    uv run python scripts/retag_registry_decision_scope.py --dry-run
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / "docs" / "experiment_registry.json"

# Explicit operational anchors (hold/freeze/promote defaults for runs).
OPERATIONAL_IDS = frozenset(
    {
        "exect_s0_s1_validation_full_gpt4_1_mini",
        "exect_s2_validation_full_gpt4_1_mini",
        "exect_s3_validation_full_gpt4_1_mini",
        "exect_s4_validation_full_gpt4_1_mini",
        "exect_s1_full_ladder_l1_policy_full",
        "exect_s1_optimizer_baseline_cap25",
        "exect_s1_prompt_policy_v4_10_cap25",
        "exect_s1_evidence_standard_cap25",
        "exect_s1_interleaving_l1_baseline_medication_slice",
        "exect_s1_interleaving_l1_baseline_seizure_slice",
        "exect_s4_frequency_l1_baseline_cap25",
        "exect_s4_temporality_l1_baseline_cap25",
        "exect_s4_temporality_l1_baseline_full",
        "gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails",
        "gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails",
    }
)


def _scope_for(row: dict) -> str | None:
    eid = row.get("experiment_id") or ""
    outcome = row.get("outcome") or ""
    cg = row.get("comparison_group") or ""

    if cg in ("", "pending_backfill"):
        return None
    decision_doc = row.get("decision_doc") or ""
    if not decision_doc or decision_doc == "pending_backfill":
        return None

    if eid in OPERATIONAL_IDS:
        return "operational"

    if outcome in ("promote", "freeze"):
        return "operational"
    if outcome in ("reject", "hold", "superseded", "pending"):
        return "arm"
    if outcome == "exploratory":
        # Curated diagnostic / comparison arms — not operational defaults.
        return "arm"

    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(REG_PATH.read_text(encoding="utf-8"))
    updated: list[str] = []
    skipped = 0
    still_missing: list[str] = []

    for row in data["experiments"]:
        notes = row.get("notes") or ""
        if "decision_scope:" in notes:
            skipped += 1
            continue

        scope = _scope_for(row)
        if not scope:
            eid = row.get("experiment_id") or ""
            cg = row.get("comparison_group") or ""
            dd = row.get("decision_doc") or ""
            if cg not in ("", "pending_backfill") and dd and dd != "pending_backfill":
                still_missing.append(eid)
            continue

        prefix = f"decision_scope: {scope}. "
        row["notes"] = prefix + notes if notes else prefix.rstrip()
        updated.append(row["experiment_id"])

    if args.dry_run:
        print(f"Would update {len(updated)} rows:")
        for eid in updated:
            print(f"  {eid}")
        print(f"\nStill missing scope (manual review): {len(still_missing)}")
        for eid in still_missing:
            print(f"  {eid}")
        return

    REG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {len(updated)} rows")
    print(f"Already tagged: {skipped}")
    if still_missing:
        print(f"Still missing (manual review): {len(still_missing)}")
        for eid in still_missing:
            print(f"  {eid}")


if __name__ == "__main__":
    main()
