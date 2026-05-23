"""Audit Gan S0 deterministic candidate coverage on the enriched gap slice."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.frequency import (
    label_to_monthly_frequency,
    pragmatic_category,
    purist_category,
)
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates,
    temporal_candidate_to_dict,
)

DEFAULT_FIXTURE = Path("data/fixtures/gan_s0_qwen35b_20260522_pragmatic_error_slice.json")
DEFAULT_PREDICTIONS = Path(
    "runs/gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z"
    "/predictions.json"
)
DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    args = parser.parse_args()

    report = build_report(args.fixture, args.predictions)
    write_json(args.json_output, report)
    write_markdown(args.markdown_output, report)

    printable = {
        "record_count": report["summary"]["record_count"],
        "gold_in_candidates": report["summary"]["gold_in_candidates"],
        "coverage_rate": report["summary"]["coverage_rate"],
        "by_failure_family": report["summary"]["by_failure_family"],
    }
    print(json.dumps(printable, indent=2))


def build_report(fixture_path: Path, predictions_path: Path) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    predictions_payload = json.loads(predictions_path.read_text(encoding="utf-8"))
    predictions = {
        prediction["document_id"]: prediction
        for prediction in predictions_payload.get("predictions", [])
    }
    records_by_id = {record.record_id: record for record in load_gan_records()}

    rows: list[dict[str, Any]] = []
    by_family: dict[str, dict[str, int]] = defaultdict(
        lambda: {"records": 0, "gold_in_candidates": 0}
    )
    for fixture_row in fixture["records"]:
        record_id = fixture_row["record_id"]
        failure_family = fixture_row["failure_mode"]
        record = records_by_id[record_id]
        prediction = predictions.get(record_id)
        if prediction is None:
            raise ValueError(f"Missing v1.4 prediction for {record_id}")

        candidates = build_temporal_frequency_candidates(record)
        candidate_labels = sorted({candidate.canonical_label for candidate in candidates})
        gold_in_candidates = record.gold_label in candidate_labels
        predicted_label = _prediction_label(prediction)

        by_family[failure_family]["records"] += 1
        if gold_in_candidates:
            by_family[failure_family]["gold_in_candidates"] += 1

        rows.append(
            {
                "record_id": record_id,
                "failure_family": failure_family,
                "gold_label": record.gold_label,
                "gold_monthly_frequency": label_to_monthly_frequency(record.gold_label),
                "gold_purist_category": purist_category(record.gold_label),
                "gold_pragmatic_category": pragmatic_category(record.gold_label),
                "v1_4_prediction": predicted_label,
                "v1_4_monthly_match": (
                    label_to_monthly_frequency(record.gold_label)
                    == label_to_monthly_frequency(predicted_label)
                ),
                "v1_4_pragmatic_category": pragmatic_category(predicted_label),
                "gold_in_candidates": gold_in_candidates,
                "candidate_labels": candidate_labels,
                "candidate_records": [
                    temporal_candidate_to_dict(candidate) for candidate in candidates
                ],
                "gold_reference_disagreement": "hard_case" in record.flags,
                "gold_evidence": record.gold_evidence,
                "reference_label": record.reference_label,
            }
        )

    covered = sum(1 for row in rows if row["gold_in_candidates"])
    by_family_summary = {
        family: {
            **stats,
            "coverage_rate": stats["gold_in_candidates"] / stats["records"],
        }
        for family, stats in sorted(by_family.items())
    }
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "fixture": _display_path(fixture_path),
        "prediction_run": _display_path(predictions_path.parent),
        "prediction_file": _display_path(predictions_path),
        "dataset": "gan_2026",
        "split_name": fixture.get("split_name"),
        "scorer_mode": "gan_frequency_deterministic_v1",
        "summary": {
            "record_count": len(rows),
            "gold_in_candidates": covered,
            "coverage_rate": covered / len(rows) if rows else 0.0,
            "by_failure_family": by_family_summary,
        },
        "rows": rows,
    }


def _prediction_label(prediction: dict[str, Any]) -> str:
    values = prediction.get("values") or []
    for value in values:
        if value.get("field_name") == "seizure_frequency_number":
            label = value.get("normalized_value") or value.get("raw_value")
            if label:
                return str(label)
    raise ValueError(f"Prediction has no seizure_frequency_number value: {prediction!r}")


def _display_path(path: Path) -> str:
    return path.as_posix()


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    rows = report["rows"]
    uncovered = [row for row in rows if not row["gold_in_candidates"]]
    monthly_misses = [row for row in rows if not row["v1_4_monthly_match"]]

    lines = [
        "# Gan S0 Candidate Builder Gap Audit",
        "",
        "Date: 2026-05-23",
        "Status: G11 no-model inspection artifact",
        f"Fixture: `{report['fixture']}`",
        f"v1.4 prediction run: `{report['prediction_run']}`",
        "Dataset/split: Gan 2026 synthetic validation enriched 25-record slice",
        "Primary gold: `check__Seizure Frequency Number.seizure_frequency_number[0]`",
        "Scorer: `gan_frequency_deterministic_v1`",
        "",
        "## Summary",
        "",
        (
            f"Current deterministic temporal builders contain the exact gold label for "
            f"**{summary['gold_in_candidates']}/{summary['record_count']}** records "
            f"({summary['coverage_rate']:.1%}). The pre-G13 baseline was 5/25 in "
            "`docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md`."
        ),
        "",
        (
            f"The v1.4 GPT control has {len(monthly_misses)} monthly-frequency misses on "
            "the same slice. Candidate absence is therefore a concrete upstream bottleneck, "
            "especially for records where v1.4 predicted `unknown` or a nearby but wrong "
            "window label."
        ),
        "",
        "## Coverage By Failure Family",
        "",
        "| Failure family | Records | Gold in candidates | Coverage |",
        "| --- | ---: | ---: | ---: |",
    ]
    for family, stats in summary["by_failure_family"].items():
        lines.append(
            f"| `{family}` | {stats['records']} | {stats['gold_in_candidates']} | "
            f"{stats['coverage_rate']:.1%} |"
        )

    lines.extend(
        [
            "",
            "## Record-Level Audit",
            "",
            "| Record | Family | Gold | v1.4 prediction | Gold in candidates | Candidate labels |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            f"`{row['record_id']}` | "
            f"`{row['failure_family']}` | "
            f"`{row['gold_label']}` | "
            f"`{row['v1_4_prediction']}` | "
            f"{'yes' if row['gold_in_candidates'] else 'no'} | "
            f"{_labels_cell(row['candidate_labels'])} |"
        )

    lines.extend(
        [
            "",
            "## Uncovered Families",
            "",
            "| Family | Records | Candidate-builder implication |",
            "| --- | --- | --- |",
        ]
    )
    for family in sorted({row["failure_family"] for row in uncovered}):
        family_rows = [row for row in uncovered if row["failure_family"] == family]
        lines.append(
            "| "
            f"`{family}` | "
            f"{', '.join(f'`{row['record_id']}`' for row in family_rows)} | "
            f"{_family_implication(family)} |"
        )

    lines.extend(
        [
            "",
            "## Implementation Notes For G12/G13",
            "",
            "- Long-window quantified counts are the broadest uncovered surface: examples include `2 per 7 month`, `5 per 13 month`, and `6 per 7 month`.",
            "- Seizure-free records need a boundary decision before code: both uncovered examples have gold `seizure free for multiple year`, which maps to monthly 0 but is stricter than generic no-current-seizure phrasing.",
            "- Cluster spacing remains uncovered for `gan_15442`: target surface `1 cluster per 4 day, 2 per cluster`.",
            "- Frequent quantified residuals are not all cluster problems; `gan_16529` gold is a simple `1 per 5 day` rate while v1.4 over-clustered it.",
            "- Scorer semantics are unchanged: this audit only inspects whether deterministic candidates include the exact gold label.",
            "",
            "## Generated Companion",
            "",
            "`docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.json` contains candidate records, evidence snippets, reference labels, monthly frequencies, and category fields for programmatic follow-up.",
            "",
        ]
    )
    return "\n".join(lines)


def _labels_cell(labels: list[str]) -> str:
    if not labels:
        return "`none`"
    return "<br>".join(f"`{label}`" for label in labels)


def _family_implication(family: str) -> str:
    implications = {
        "cluster_frequency_over_unknown": "Add narrow cluster-spacing plus per-cluster candidate logic.",
        "frequent_quantified_over_unknown": "Audit simple high-frequency rate phrasing separately from cluster-like phrasings.",
        "infrequent_quantified_over_unknown": "Prioritize elapsed-window and recent-count aggregation builders.",
        "seizure_free_over_unknown": "Preregister seizure-free/no-current-seizure boundary rules before implementation.",
        "vague_multiple_over_unknown": "Handle vague multiple counts only when the observation window is textually anchored.",
    }
    return implications.get(family, "Inspect before implementation.")


if __name__ == "__main__":
    main()
