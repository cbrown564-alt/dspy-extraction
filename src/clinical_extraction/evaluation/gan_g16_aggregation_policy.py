"""Gan G16 rate/duration aggregation policy report.

This is a no-model policy surface. It classifies where exact Gan S0 answer
options are already available, where rate/duration aggregation is required, and
where the row belongs to an upstream gate, inventory, or special-class policy
before another exact-label selector claim.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.evaluation.gan_g11_candidate_inventory_challenge import (
    DEFAULT_G11_JSON_OUTPUT,
    G11_CHALLENGE_SET_NAME,
)
from clinical_extraction.evaluation.gan_temporal_anchoring_g14 import (
    DEFAULT_G14_JSON_OUTPUT,
    G14_STANDARD50_NAME,
    _candidate_slot_match,
    _temporal_slot,
)
from clinical_extraction.gan.frequency import normalize_label

DEFAULT_G16_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g16_aggregation_policy_20260529.json"
)
DEFAULT_G16_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g16_aggregation_policy_20260529.md"
)


def aggregation_policy_class(
    *,
    gold_label: str,
    exact_candidate_coverage: bool,
    temporal_applicable: bool,
    temporal_slot_coverage: bool | None,
    purist_equivalent_coverage: bool,
    pragmatic_equivalent_coverage: bool,
    gate_caveated: bool,
) -> str:
    """Classify the next aggregation action for one Gan S0 row."""

    normalized = normalize_label(gold_label)
    if exact_candidate_coverage:
        return "closed_option_already_available"
    if normalized in {
        "unknown",
        "no seizure frequency reference",
    } or normalized.startswith("unknown,"):
        return "outside_rate_duration_aggregation_policy"
    if normalized.startswith("seizure free for "):
        return "duration_aggregation_policy_required"
    if gate_caveated:
        return "upstream_gate_caveat_before_aggregation"
    if (
        temporal_applicable
        and temporal_slot_coverage is False
        and (purist_equivalent_coverage or pragmatic_equivalent_coverage)
    ):
        return "aggregation_required_temporal_slot_missing"
    if purist_equivalent_coverage or pragmatic_equivalent_coverage:
        return "aggregation_constructor_required"
    return "candidate_inventory_gap_before_aggregation"


def build_g16_aggregation_policy_report(
    *,
    g11_json: Path = DEFAULT_G11_JSON_OUTPUT,
    g14_json: Path = DEFAULT_G14_JSON_OUTPUT,
) -> dict[str, Any]:
    """Build the G16 no-model aggregation policy report from G11 and G14."""

    g11 = json.loads(g11_json.read_text(encoding="utf-8"))
    g14 = json.loads(g14_json.read_text(encoding="utf-8"))
    g11_rows = [_g11_policy_row(row) for row in g11["rows"]]
    standard50_rows = [_g14_policy_row(row) for row in g14["rows"]]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "G16 no-model rate/duration aggregation policy",
        "kanban_card": "G16 - Gan Rate/Duration Aggregation Policy",
        "dataset": "Gan 2026 synthetic",
        "split": "gan_2026_fixed_v1:validation",
        "surfaces": {
            "g11_exact_miss_challenge": G11_CHALLENGE_SET_NAME,
            "standard50": G14_STANDARD50_NAME,
        },
        "source_artifacts": {
            "g11_candidate_inventory_challenge": g11_json.as_posix(),
            "g14_temporal_anchoring": g14_json.as_posix(),
        },
        "gold_source": "check__Seizure Frequency Number.seizure_frequency_number[0]",
        "reference_policy": (
            "reference[0] is a secondary difficulty signal, not benchmark gold"
        ),
        "fixed_controls": {
            "model_calls": "none",
            "scorer_changed": False,
            "loader_split_bridge_prompt_or_repair_changed": False,
            "candidate_builder_changed": False,
            "target_selection_changed": False,
            "prediction_repair_changed": False,
        },
        "policy": _policy(),
        "summary": {
            "g11_exact_miss_challenge": _summary(g11_rows),
            "standard50": _summary(standard50_rows),
        },
        "decision": _decision(g11_rows, standard50_rows),
        "rows": {
            "g11_exact_miss_challenge": g11_rows,
            "standard50": standard50_rows,
        },
    }


def write_g16_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_G16_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_G16_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_g16_markdown(report), encoding="utf-8")


def render_g16_markdown(report: dict[str, Any]) -> str:
    g11 = report["summary"]["g11_exact_miss_challenge"]
    standard = report["summary"]["standard50"]
    decision = report["decision"]
    lines = [
        "# Gan S0 G16 Rate/Duration Aggregation Policy",
        "",
        "Date: 2026-05-29",
        "Status: current synthesis / no-model aggregation policy",
        f"Kanban card: {report['kanban_card']}",
        f"Dataset/split: {report['dataset']} (`{report['split']}`)",
        f"G11 challenge set: `{report['surfaces']['g11_exact_miss_challenge']}`",
        f"Standard surface: `{report['surfaces']['standard50']}`",
        "Model calls: none",
        "Scorer, loader, split, bridge, prompt, model, candidate-builder, target-selection, and prediction-repair semantics: unchanged.",
        "",
        "## Summary",
        "",
        _summary_sentence("G11 exact-miss challenge", g11),
        _summary_sentence("Standard50", standard),
        "",
        "## Policy",
        "",
    ]
    for item in report["policy"]["rules"]:
        lines.append(f"- `{item['class']}`: {item['meaning']}")
    lines.extend(
        [
            "",
            "## Policy Class Counts",
            "",
            "| Surface | Policy class | Records |",
            "| --- | --- | ---: |",
        ]
    )
    for surface_key, summary in (
        ("g11_exact_miss_challenge", g11),
        ("standard50", standard),
    ):
        for klass, count in summary["policy_class_counts"].items():
            lines.append(f"| `{surface_key}` | `{klass}` | {count} |")
    lines.extend(
        [
            "",
            "## G11 Policy Rows",
            "",
            "| Record | Gold | Policy class | Exact | Slot | Purist/Pragmatic | Candidate labels |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in report["rows"]["g11_exact_miss_challenge"]:
        labels = (
            "<br>".join(f"`{label}`" for label in row["candidate_labels"]) or "`none`"
        )
        lines.append(
            f"| `{row['record_id']}` | `{row['gold_label']}` | "
            f"`{row['policy_class']}` | {_yn(row['exact_candidate_coverage'])} | "
            f"{_yn(row['temporal_slot_coverage'])} | "
            f"{_yn(row['purist_equivalent_coverage'])}/"
            f"{_yn(row['pragmatic_equivalent_coverage'])} | {labels} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Classification: **{decision['classification']}**.",
            f"- Next selector authorization: **{decision['next_selector_authorization']}**.",
            f"- Constructor decision: {decision['constructor_decision']}",
            f"- Reporting rule: {decision['reporting_rule']}",
            "",
            "## Interpretation",
            "",
            "- Rate aggregation is policy-ready only as a named mechanism: sum explicitly supported events over an explicitly supported observation window, preserve the source candidates and evidence, and report exact labels separately from category-equivalent diagnostics.",
            "- Seizure-free duration aggregation is not the same as rate aggregation; it needs a duration-specific policy before being mixed with quantified-frequency answer construction.",
            "- Unknown and no-reference rows remain outside this G16 rate/duration policy and route to G17.",
            "- G16 does not promote another exact-label selector. It defines the boundary a deterministic constructor or preregistered model mechanism must satisfy before exact closed answer options can be claimed.",
            "",
            "## Companion Artifact",
            "",
            "`docs/experiments/gan/gan_s0_g16_aggregation_policy_20260529.json` contains policy classes for the G11 exact-miss challenge and G14 standard50 surface.",
            "",
        ]
    )
    return "\n".join(lines)


def _policy() -> dict[str, Any]:
    return {
        "scope": (
            "multiple seizure-frequency mentions that may need rate or seizure-free "
            "duration aggregation before exact answer-option construction"
        ),
        "rules": [
            {
                "class": "closed_option_already_available",
                "meaning": "The current candidate surface already contains the exact gold label; aggregation is not the bottleneck for that row.",
            },
            {
                "class": "aggregation_required_temporal_slot_missing",
                "meaning": "A quantified-frequency row has category-equivalent candidates but lacks the exact event/window slot; an exact claim requires an explicit aggregation constructor or preregistered model mechanism.",
            },
            {
                "class": "aggregation_constructor_required",
                "meaning": "The row is category-equivalent but exact-incomplete; aggregation may be needed, but the existing temporal slot is not the primary recorded miss.",
            },
            {
                "class": "duration_aggregation_policy_required",
                "meaning": "The row is seizure-free duration rather than quantified rate; do not fold it into rate aggregation without a duration-specific rule.",
            },
            {
                "class": "upstream_gate_caveat_before_aggregation",
                "meaning": "G13 already misclassified the content state, so aggregation should not be blamed as the first failure stage.",
            },
            {
                "class": "outside_rate_duration_aggregation_policy",
                "meaning": "The row is an unknown/no-reference/unknown-cluster special case and routes to G17 or cluster policy, not G16 rate/duration aggregation.",
            },
            {
                "class": "candidate_inventory_gap_before_aggregation",
                "meaning": "No exact or category-equivalent candidate support exists; inventory or temporal anchoring must improve before aggregation can be evaluated.",
            },
        ],
    }


def _g11_policy_row(row: dict[str, Any]) -> dict[str, Any]:
    slot = _temporal_slot(row["gold_label"])
    slot_coverage = (
        _candidate_slot_match(slot, row["candidate_records"])
        if slot["temporal_applicable"]
        else None
    )
    policy_class = aggregation_policy_class(
        gold_label=row["gold_label"],
        exact_candidate_coverage=row["gold_exact_in_candidates"],
        temporal_applicable=slot["temporal_applicable"],
        temporal_slot_coverage=slot_coverage,
        purist_equivalent_coverage=row["gold_purist_in_candidates"],
        pragmatic_equivalent_coverage=row["gold_pragmatic_in_candidates"],
        gate_caveated=False,
    )
    return {
        "record_id": row["record_id"],
        "gold_label": row["gold_label"],
        "label_family": row["label_family"],
        "candidate_labels": row["candidate_labels"],
        "exact_candidate_coverage": row["gold_exact_in_candidates"],
        "purist_equivalent_coverage": row["gold_purist_in_candidates"],
        "pragmatic_equivalent_coverage": row["gold_pragmatic_in_candidates"],
        "temporal_applicable": slot["temporal_applicable"],
        "temporal_slot_coverage": slot_coverage,
        "gate_caveated": False,
        "policy_class": policy_class,
        "reference_label": row["reference_label"],
        "gold_evidence": row["gold_evidence"],
        "hard_strata": row["hard_strata"],
    }


def _g14_policy_row(row: dict[str, Any]) -> dict[str, Any]:
    policy_class = aggregation_policy_class(
        gold_label=row["gold_label"],
        exact_candidate_coverage=row["exact_candidate_coverage"],
        temporal_applicable=row["temporal_applicable"],
        temporal_slot_coverage=row["temporal_slot_coverage"],
        purist_equivalent_coverage=row["purist_equivalent_coverage"],
        pragmatic_equivalent_coverage=row["pragmatic_equivalent_coverage"],
        gate_caveated=row["gate_caveated"],
    )
    return {
        "record_id": row["record_id"],
        "gold_label": row["gold_label"],
        "label_family": row["label_family"],
        "candidate_labels": row["candidate_labels"],
        "exact_candidate_coverage": row["exact_candidate_coverage"],
        "purist_equivalent_coverage": row["purist_equivalent_coverage"],
        "pragmatic_equivalent_coverage": row["pragmatic_equivalent_coverage"],
        "temporal_applicable": row["temporal_applicable"],
        "temporal_slot_coverage": row["temporal_slot_coverage"],
        "gate_caveated": row["gate_caveated"],
        "policy_class": policy_class,
        "reference_label": row["reference_label"],
        "gold_evidence": row["gold_evidence"],
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(row["policy_class"] for row in rows)
    exact_blocked = [
        row
        for row in rows
        if row["policy_class"]
        in {
            "aggregation_required_temporal_slot_missing",
            "aggregation_constructor_required",
            "duration_aggregation_policy_required",
        }
    ]
    return {
        "records": len(rows),
        "policy_class_counts": dict(sorted(counts.items())),
        "exact_blocked_by_aggregation_policy": len(exact_blocked),
        "exact_blocked_record_ids": [row["record_id"] for row in exact_blocked],
    }


def _decision(
    g11_rows: list[dict[str, Any]],
    standard50_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    g11_summary = _summary(g11_rows)
    standard_summary = _summary(standard50_rows)
    blocked = (
        g11_summary["exact_blocked_by_aggregation_policy"] > 0
        or standard_summary["exact_blocked_by_aggregation_policy"] > 0
    )
    return {
        "classification": "aggregation_policy_defined_exact_constructor_blocked",
        "next_selector_authorization": (
            "blocked_until_constructor_or_preregistered_model_mechanism"
            if blocked
            else "exact_closed_options_authorized"
        ),
        "constructor_decision": (
            "Do not mutate the current candidate builder from this policy pass. "
            "A follow-up constructor must be independently fixture-tested and "
            "reported before an exact closed-answer-option claim."
        ),
        "reporting_rule": (
            "Until that constructor exists, report exact-label and monthly-frequency "
            "selector results as unsupported diagnostics when exact candidates are "
            "absent; category-equivalent coverage may be reported separately."
        ),
        "g11_exact_blocked_record_ids": g11_summary["exact_blocked_record_ids"],
        "standard50_exact_blocked_record_ids": standard_summary[
            "exact_blocked_record_ids"
        ],
    }


def _summary_sentence(label: str, summary: dict[str, Any]) -> str:
    return (
        f"{label}: **{summary['records']}** rows; "
        f"**{summary['exact_blocked_by_aggregation_policy']}** rows are blocked "
        "on aggregation or duration policy before exact closed-answer options."
    )


def _yn(value: bool | None) -> str:
    if value is None:
        return "n/a"
    return "yes" if value else "no"


__all__ = [
    "DEFAULT_G16_JSON_OUTPUT",
    "DEFAULT_G16_MARKDOWN_OUTPUT",
    "aggregation_policy_class",
    "build_g16_aggregation_policy_report",
    "render_g16_markdown",
    "write_g16_report_artifacts",
]
