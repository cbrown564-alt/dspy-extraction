"""Gan S0 target-selection versus label-construction split reporting.

This module is diagnostic infrastructure for G2. It does not change Gan loader
or scorer semantics; it asks what the current candidate substrate can support
when target selection and exact label emission are treated as separate stages.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_candidate_inventory import (
    DEFAULT_GAN_JSON,
    DEFAULT_SPLIT_FILE,
    DEFAULT_SPLIT_NAME,
)
from clinical_extraction.evaluation.gan_multi_event_flags import (
    GanMultiEventFlags,
    build_flags_for_raw_records,
)
from clinical_extraction.evaluation.gan_run_analysis import load_split_ids
from clinical_extraction.gan.s0.target_selection import (
    ConstructedGanLabel,
    build_gan_s0_target_selection_surface,
    construct_gan_s0_label_from_candidate_record,
    select_gan_s0_candidate_constrained_oracle,
    select_gan_s0_reason_code_family_oracle,
)
from clinical_extraction.gan.scoring import (
    GAN_CANONICAL_SCORER,
    GAN_PAPER_REPRODUCTION_SCORER,
)
from clinical_extraction.schemas import GanRecord

DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_target_label_split_g2_report_20260528.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_target_label_split_g2_report_20260528.md"
)


construct_label_from_candidate_record = construct_gan_s0_label_from_candidate_record


def build_gan_target_label_split_report(
    *,
    records: list[GanRecord] | None = None,
    record_ids: list[str] | None = None,
    flags_by_id: dict[str, GanMultiEventFlags] | None = None,
    split_name: str = DEFAULT_SPLIT_NAME,
    candidate_source: str = "deterministic_temporal_candidates_current_d1_builder",
) -> dict[str, Any]:
    """Build the G2 no-model target-selection/label-construction report."""

    source_records = records if records is not None else load_gan_records()
    records_by_id = {record.record_id: record for record in source_records}
    ordered_ids = record_ids if record_ids is not None else list(records_by_id)
    rows = [
        _split_row(
            record=records_by_id[record_id],
            flags=flags_by_id.get(record_id) if flags_by_id else None,
        )
        for record_id in ordered_ids
    ]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": "gan_2026",
        "split_name": split_name,
        "candidate_source": candidate_source,
        "gold_source": "check__Seizure Frequency Number.seizure_frequency_number[0]",
        "reference_policy": (
            "reference[0] is retained only as a difficulty signal; "
            "seizure_frequency_number[0] is the gold label"
        ),
        "scorer_semantics": (
            "No scorer semantics changed. Arm summaries report "
            f"{GAN_PAPER_REPRODUCTION_SCORER} for paper-facing comparison and "
            f"{GAN_CANONICAL_SCORER} as a diagnostic clinical/project view."
        ),
        "ablation_plan": _ablation_plan(),
        "summary": _summarize_rows(rows),
        "rows": rows,
    }


def build_report_from_files(
    *,
    gan_json: Path = DEFAULT_GAN_JSON,
    split_file: Path = DEFAULT_SPLIT_FILE,
    split_name: str = DEFAULT_SPLIT_NAME,
) -> dict[str, Any]:
    raw_records = json.loads(gan_json.read_text(encoding="utf-8"))
    flags = build_flags_for_raw_records(raw_records)
    flags_by_id = {flag.record_id: flag for flag in flags}
    records = load_gan_records(gan_json)
    record_ids = load_split_ids(split_file, split_name)
    return build_gan_target_label_split_report(
        records=records,
        record_ids=record_ids,
        flags_by_id=flags_by_id,
        split_name=split_name,
    )


def write_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_target_label_split_markdown(report), encoding="utf-8")


def _split_row(
    *,
    record: GanRecord,
    flags: GanMultiEventFlags | None,
) -> dict[str, Any]:
    return build_gan_s0_target_selection_surface(record=record, flags=flags)


def _candidate_constrained_oracle(
    *,
    record: GanRecord,
    constructed_candidates: list[ConstructedGanLabel],
) -> dict[str, Any]:
    return select_gan_s0_candidate_constrained_oracle(
        record=record,
        constructed_candidates=constructed_candidates,
    )


def _reason_code_family_oracle(
    *,
    record: GanRecord,
    constructed_candidates: list[ConstructedGanLabel],
) -> dict[str, Any]:
    return select_gan_s0_reason_code_family_oracle(
        record=record,
        constructed_candidates=constructed_candidates,
    )


def _summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "records": len(rows),
        "arms": {
            "candidate_constrained_oracle": _arm_summary(
                rows,
                "candidate_constrained_oracle",
            ),
            "reason_code_selector_family_oracle": _arm_summary(
                rows,
                "reason_code_selector_family_oracle",
            ),
        },
        "deterministic_label_constructor": _constructor_summary(rows),
        "by_label_family": _bucketed_arm_summary(rows, "label_family"),
        "by_hard_stratum": _hard_stratum_arm_summary(rows),
    }


def _arm_summary(rows: list[dict[str, Any]], arm_key: str) -> dict[str, Any]:
    total = len(rows)
    supported = [row for row in rows if row[arm_key]["status"] == "supported"]
    summary = {
        "records": total,
        "supported_predictions": len(supported),
        "unsupported_records": total - len(supported),
        "unsupported_reason_counts": _reason_counts(
            row[arm_key]["reason_code"]
            for row in rows
            if row[arm_key]["status"] != "supported"
        ),
        "selection_reason_counts": _reason_counts(
            row[arm_key]["reason_code"] for row in supported
        ),
    }
    summary["canonical"] = _score_summary(rows, arm_key, "canonical")
    summary["paper_reproduction"] = _score_summary(
        rows,
        arm_key,
        "paper_reproduction",
    )
    return summary


def _score_summary(
    rows: list[dict[str, Any]],
    arm_key: str,
    score_key: str,
) -> dict[str, Any]:
    total = len(rows)
    scores = [row[arm_key]["scores"][score_key] for row in rows]
    return {
        "normalized_label_accuracy": _match_rate(
            scores,
            "normalized_label_match",
            total,
        ),
        "monthly_frequency_accuracy": _match_rate(
            scores,
            "monthly_frequency_match",
            total,
        ),
        "purist_category_accuracy": _match_rate(
            scores,
            "purist_category_match",
            total,
        ),
        "pragmatic_category_accuracy": _match_rate(
            scores,
            "pragmatic_category_match",
            total,
        ),
    }


def _constructor_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_total = sum(row["candidate_count"] for row in rows)
    constructed = 0
    invalid = 0
    invalid_labels: dict[str, int] = defaultdict(int)
    for row in rows:
        for candidate in row["constructed_candidates"]:
            if candidate["status"] == "constructed":
                constructed += 1
            else:
                invalid += 1
                invalid_labels[candidate["raw_candidate_label"]] += 1
    return {
        "records": len(rows),
        "candidate_records": candidate_total,
        "constructed_candidates": constructed,
        "invalid_candidates": invalid,
        "invalid_candidate_labels": dict(sorted(invalid_labels.items())),
    }


def _bucketed_arm_summary(
    rows: list[dict[str, Any]],
    key: str,
) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row[key])].append(row)
    return {
        bucket: {
            "candidate_constrained_oracle": _arm_summary(
                bucket_rows,
                "candidate_constrained_oracle",
            ),
            "reason_code_selector_family_oracle": _arm_summary(
                bucket_rows,
                "reason_code_selector_family_oracle",
            ),
        }
        for bucket, bucket_rows in sorted(buckets.items())
    }


def _hard_stratum_arm_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for stratum in row["hard_strata"]:
            buckets[stratum].append(row)
    return {
        bucket: {
            "candidate_constrained_oracle": _arm_summary(
                bucket_rows,
                "candidate_constrained_oracle",
            ),
            "reason_code_selector_family_oracle": _arm_summary(
                bucket_rows,
                "reason_code_selector_family_oracle",
            ),
        }
        for bucket, bucket_rows in sorted(buckets.items())
    }


def _match_rate(scores: list[dict[str, Any]], key: str, total: int) -> float | None:
    if total == 0:
        return None
    return sum(1 for score in scores if score[key]) / total


def _reason_counts(reasons: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for reason in reasons:
        counts[reason] += 1
    return dict(sorted(counts.items()))


def _ablation_plan() -> list[dict[str, str]]:
    return [
        {
            "arm": "free_adjudication",
            "selector": "LLM reads the note and emits the final Gan label directly",
            "label_constructor": "LLM final-label text",
            "status": "planned_model_arm",
        },
        {
            "arm": "candidate_constrained_adjudication",
            "selector": "LLM selects one candidate or explicit fallback policy",
            "label_constructor": "deterministic constructor emits selected candidate label",
            "status": "implemented_no_model_oracle; model arm pending",
        },
        {
            "arm": "reason_code_selector",
            "selector": "LLM selects reason code/family and candidate target",
            "label_constructor": "deterministic constructor emits label from selected target",
            "status": "implemented_family_oracle; slot-level model arm pending",
        },
        {
            "arm": "deterministic_label_constructor",
            "selector": "provided selected candidate",
            "label_constructor": "normalization plus audited Gan taxonomy validation only",
            "status": "implemented_candidate_validation_surface",
        },
    ]


def render_target_label_split_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    constrained = summary["arms"]["candidate_constrained_oracle"]
    family = summary["arms"]["reason_code_selector_family_oracle"]
    constructor = summary["deterministic_label_constructor"]
    lines = [
        "# Gan S0 Target Selection And Label Construction Split",
        "",
        "Date: 2026-05-28",
        "Status: G2 ablation plan plus no-model split implementation",
        f"Dataset/split: Gan 2026 synthetic validation split (`{report['split_name']}`)",
        f"Candidate source: `{report['candidate_source']}`",
        f"Gold source: `{report['gold_source']}`",
        "Scorer semantics: unchanged; paper reproduction and canonical views are both reported.",
        "",
        "## Summary",
        "",
        (
            "Candidate-constrained oracle reaches "
            f"**{_pct(constrained['paper_reproduction']['monthly_frequency_accuracy'])}** "
            "monthly accuracy under `gan2026_paper_reproduction` and "
            f"**{_pct(constrained['canonical']['monthly_frequency_accuracy'])}** "
            "under the canonical diagnostic scorer."
        ),
        (
            "The deterministic label constructor handled "
            f"**{constructor['constructed_candidates']}/{constructor['candidate_records']}** "
            "candidate records; invalid candidate labels remain unsupported rather than repaired."
        ),
        "",
        "## Ablation Plan",
        "",
        "| Arm | Selector | Label constructor | Status |",
        "| --- | --- | --- | --- |",
    ]
    for arm in report["ablation_plan"]:
        lines.append(
            f"| `{arm['arm']}` | {arm['selector']} | "
            f"{arm['label_constructor']} | `{arm['status']}` |"
        )

    lines.extend(
        [
            "",
            "## No-Model Split Report",
            "",
            "| Arm | Supported | Canonical monthly | Canonical pragmatic | Paper monthly | Paper pragmatic |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
            _arm_table_row("candidate_constrained_oracle", constrained),
            _arm_table_row("reason_code_selector_family_oracle", family),
            "",
            "## Constructor Diagnostics",
            "",
            "| Candidate records | Constructed | Invalid |",
            "| ---: | ---: | ---: |",
            (
                f"| {constructor['candidate_records']} | "
                f"{constructor['constructed_candidates']} | "
                f"{constructor['invalid_candidates']} |"
            ),
            "",
            "## Label-Family View",
            "",
            "| Family | Records | Candidate-constrained paper monthly | Reason-code paper monthly |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for family_name, payload in summary["by_label_family"].items():
        constrained_family = payload["candidate_constrained_oracle"]
        reason_family = payload["reason_code_selector_family_oracle"]
        lines.append(
            f"| `{family_name}` | {constrained_family['records']} | "
            f"{_pct(constrained_family['paper_reproduction']['monthly_frequency_accuracy'])} | "
            f"{_pct(reason_family['paper_reproduction']['monthly_frequency_accuracy'])} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This report is a no-model decomposition scaffold, not a completed model comparison.",
            "- `free_adjudication` remains the control model arm; the implemented rows here quantify what the current G1 substrate can support if selection were perfect.",
            "- Invalid candidate surfaces are not repaired here; scorer repair remains explicit and scorer-only.",
            "- `reference[0]` is not used as gold. It is retained only through hard-case flags.",
            "",
            "## Companion Artifact",
            "",
            "`docs/experiments/gan/gan_s0_target_label_split_g2_report_20260528.json` contains all record-level selected-candidate, construction, scorer, and strata fields.",
            "",
        ]
    )
    return "\n".join(lines)


def _arm_table_row(name: str, payload: dict[str, Any]) -> str:
    return (
        f"| `{name}` | {payload['supported_predictions']}/{payload['records']} | "
        f"{_pct(payload['canonical']['monthly_frequency_accuracy'])} | "
        f"{_pct(payload['canonical']['pragmatic_category_accuracy'])} | "
        f"{_pct(payload['paper_reproduction']['monthly_frequency_accuracy'])} | "
        f"{_pct(payload['paper_reproduction']['pragmatic_category_accuracy'])} |"
    )


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1%}"
