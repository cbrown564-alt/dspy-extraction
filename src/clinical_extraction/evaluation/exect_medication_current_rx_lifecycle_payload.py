"""Audit ExECT medication current-Rx and lifecycle payload coverage."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.exect import load_exect_gold_documents
from clinical_extraction.exect.medication_payload import (
    benchmark_current_rx_values,
    build_exect_medication_payload,
    note_lifecycle_current_values,
    summarize_medication_payload_rows,
)

DEFAULT_SPLITS = Path("data/splits/exectv2_splits.json")
DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/exect/"
    "exect_medication_current_rx_lifecycle_payload_audit_20260528.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/exect/"
    "exect_medication_current_rx_lifecycle_payload_audit_20260528.md"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--split", default="validation")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    args = parser.parse_args()

    report = build_report(args.splits, args.split)
    write_json(args.json_output, report)
    write_markdown(args.markdown_output, report)
    print(
        json.dumps(
            {
                "split": report["split_name"],
                "current_rx_coverage": report["current_rx_summary"]["coverage"],
                "note_lifecycle_current_recall": report[
                    "note_lifecycle_current_summary"
                ]["coverage"],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


def build_report(splits_path: Path, split_name: str) -> dict[str, Any]:
    split_ids = _load_split_ids(splits_path, split_name)
    documents = [
        document
        for document in load_exect_gold_documents()
        if document.document_id in split_ids
    ]
    documents.sort(key=lambda document: document.document_id)
    rows = [_document_row(document) for document in documents]
    lifecycle_counts = Counter()
    aggregate = Counter()
    for row in rows:
        lifecycle_counts.update(row["payload_summary"]["lifecycle_status_counts"])
        aggregate.update(
            {
                "non_asm_rows": row["payload_summary"]["non_asm_rows"],
                "planned_rows": row["payload_summary"]["planned_rows"],
                "previous_rows": row["payload_summary"]["previous_rows"],
                "unknown_temporality_rows": row["payload_summary"][
                    "unknown_temporality_rows"
                ],
                "taper_or_stop_rows": row["payload_summary"]["taper_or_stop_rows"],
                "dose_line_rows": row["payload_summary"]["dose_line_rows"],
                "dose_only_rows": row["payload_summary"]["dose_only_rows"],
                "prescription_list_rows": row["payload_summary"][
                    "prescription_list_rows"
                ],
            }
        )
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": "exect_v2",
        "split_name": split_name,
        "split_file": splits_path.as_posix(),
        "validation_policy": (
            "No model calls; medication payload rows compared to existing "
            "load_exect_gold_documents() current_medications."
        ),
        "scorer_caveats": [
            "Prescription JSON has no native temporality column.",
            "Annotated prescriptions remain the benchmark current-Rx source.",
            "Lifecycle status is diagnostic and must not change S1 medication scoring.",
            "Validation is the component-development split; test remains holdout.",
        ],
        "current_rx_summary": _summarize_candidate_key(rows, "current_rx_values"),
        "note_lifecycle_current_summary": _summarize_candidate_key(
            rows,
            "note_lifecycle_current_values",
        ),
        "lifecycle_status_counts": dict(sorted(lifecycle_counts.items())),
        "lifecycle_case_counts": dict(sorted(aggregate.items())),
        "decision": {
            "annotated_current_rx": "headline substrate",
            "medication_lifecycle_temporality": "diagnostic/deferred",
            "rationale": (
                "The annotation-derived current-Rx payload reproduces S1 medication "
                "gold, while note-surface lifecycle rows expose planned, previous, "
                "taper, non-ASM, and dose-line cases without reliable native "
                "temporality gold."
            ),
        },
        "rows": rows,
    }


def _document_row(document: Any) -> dict[str, Any]:
    payload = build_exect_medication_payload(
        document.text,
        annotations=document.raw_annotations,
        document_id=document.document_id,
    )
    current_rx = sorted(benchmark_current_rx_values(payload))
    note_lifecycle_current = sorted(note_lifecycle_current_values(payload))
    return {
        "document_id": document.document_id,
        "gold_current_medications": sorted(document.current_medications),
        "current_rx_values": current_rx,
        "note_lifecycle_current_values": note_lifecycle_current,
        "payload_summary": summarize_medication_payload_rows(payload),
        "payload_rows": [_payload_row_to_dict(row) for row in payload],
    }


def _summarize_candidate_key(
    rows: list[dict[str, Any]],
    candidate_key: str,
) -> dict[str, Any]:
    gold_docs = [row for row in rows if row["gold_current_medications"]]
    gold_total = sum(len(row["gold_current_medications"]) for row in rows)
    candidate_total = sum(len(row[candidate_key]) for row in rows)
    matched = sum(
        len(set(row["gold_current_medications"]) & set(row[candidate_key]))
        for row in rows
    )
    full_docs = sum(
        1
        for row in gold_docs
        if set(row["gold_current_medications"]).issubset(set(row[candidate_key]))
    )
    return {
        "documents": len(rows),
        "gold_documents": len(gold_docs),
        "gold_labels": gold_total,
        "candidate_labels": candidate_total,
        "matched_gold_labels": matched,
        "missed_gold_labels": gold_total - matched,
        "coverage": _safe_divide(matched, gold_total),
        "precision": _safe_divide(matched, candidate_total),
        "full_label_documents": full_docs,
        "full_label_document_rate": _safe_divide(full_docs, len(gold_docs)),
    }


def _payload_row_to_dict(row: Any) -> dict[str, Any]:
    return {
        "source_kind": row.source_kind,
        "raw_text": row.raw_text,
        "canonical_medication": row.canonical_medication,
        "benchmark_medication": row.benchmark_medication,
        "lifecycle_status": row.lifecycle_status,
        "annotation_policy_current": row.annotation_policy_current,
        "benchmark_role": row.benchmark_role,
        "is_asm": row.is_asm,
        "prescription_list_member": row.prescription_list_member,
        "dose_line": row.dose_line,
        "taper_or_stop": row.taper_or_stop,
        "section": row.section,
        "evidence_text": row.evidence_text,
        "start": row.start,
        "end": row.end,
        "caveats": row.caveats,
        "metadata": row.metadata,
    }


def _load_split_ids(path: Path, split_name: str) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    try:
        split_values = payload[split_name]
    except KeyError as exc:
        raise ValueError(f"Split {split_name!r} not found in {path}") from exc
    return {str(value) for value in split_values}


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


def render_markdown(report: dict[str, Any]) -> str:
    current = report["current_rx_summary"]
    note_current = report["note_lifecycle_current_summary"]
    lines = [
        "# ExECT Medication Current-Rx And Lifecycle Payload Audit",
        "",
        "Date: 2026-05-28",
        "Status: current synthesis; no-model representability gate",
        "Kanban card: E3 - Medication Current-Rx And Lifecycle Payload",
        f"Dataset/split: ExECTv2 `{report['split_name']}` "
        f"({current['documents']} documents)",
        "Model/provider: none",
        "Scorer mode: no-model payload-vs-gold coverage audit; no scorer semantics changed",
        "",
        "## Summary",
        "",
        (
            "The annotation-derived current-Rx payload reproduces "
            f"**{current['matched_gold_labels']}/{current['gold_labels']}** validation "
            f"gold medication labels ({current['coverage']:.1%}) across "
            f"{current['full_label_documents']}/{current['gold_documents']} "
            "gold-bearing documents."
        ),
        "",
        (
            "The note-surface lifecycle view is useful as a diagnostic inventory, "
            "but not as a replacement current-Rx substrate: it covers "
            f"**{note_current['matched_gold_labels']}/{note_current['gold_labels']}** "
            f"gold labels ({note_current['coverage']:.1%}) with "
            f"{note_current['precision']:.1%} candidate precision."
        ),
        "",
        "## Current-Rx Comparison",
        "",
        "| Payload view | Gold coverage | Candidate precision | Full-label docs | Gold labels | Candidate labels |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        _mode_row("Annotated current-Rx payload", current),
        _mode_row("Note lifecycle current candidates", note_current),
        "",
        "## Lifecycle Inventory",
        "",
        "| Case type | Count |",
        "| --- | ---: |",
    ]
    for key, value in report["lifecycle_case_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Temporality Decision",
            "",
            "- Annotated current-Rx is the headline medication substrate for S1/S5 medication reproduction.",
            "- Lifecycle and temporality remain diagnostic/deferred because ExECT prescription JSON lacks a native temporality column.",
            "- Planned, previous, taper, dose-line, and non-ASM rows should be reported as lifecycle cases before any model-backed temporality target is promoted.",
            "",
            "## Dataset And Scorer Caveats",
            "",
            "- Gold labels use current `load_exect_gold_documents()` prescription policy.",
            "- Prescription rows are benchmark current-Rx by annotation policy, even when lifecycle cues need separate inspection.",
            "- No loader, split, scorer, or benchmark bridge semantics changed.",
            "- Validation is the component-development split; test remains holdout for residual analysis only.",
            "",
            "## Generated Companion",
            "",
            "`docs/experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.json` contains per-document payload rows and lifecycle counts.",
            "",
        ]
    )
    return "\n".join(lines)


def _mode_row(name: str, mode: dict[str, Any]) -> str:
    return (
        f"| {name} | {mode['coverage']:.1%} | {mode['precision']:.1%} | "
        f"{mode['full_label_documents']}/{mode['gold_documents']} "
        f"({mode['full_label_document_rate']:.1%}) | "
        f"{mode['gold_labels']} | {mode['candidate_labels']} |"
    )


def _safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


if __name__ == "__main__":
    main()
