"""Export the E7 ExECT medication stack-interference probe."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.exect import canonical_medication_name
from clinical_extraction.evaluation.exect_medication_current_rx_ceiling_probe import (
    DEFAULT_E3_PAYLOAD,
    DEFAULT_S1_RUN,
    DEFAULT_S5_RUN,
    DEFAULT_SPLITS,
    _load_prediction_set,
    build_report as build_ceiling_report,
)
from clinical_extraction.schemas import DocumentPrediction, PredictionSet

DEFAULT_OUTPUT_JSON = Path(
    "docs/experiments/exect/"
    "exect_medication_stack_interference_probe_20260528.json"
)
DEFAULT_OUTPUT_MARKDOWN = Path(
    "docs/experiments/exect/"
    "exect_medication_stack_interference_probe_20260528.md"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--split", default="validation")
    parser.add_argument("--e3-payload", type=Path, default=DEFAULT_E3_PAYLOAD)
    parser.add_argument("--s1-run", default=DEFAULT_S1_RUN)
    parser.add_argument("--s5-run", default=DEFAULT_S5_RUN)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    args = parser.parse_args()

    report = build_report(
        splits_path=args.splits,
        split_name=args.split,
        e3_payload_path=args.e3_payload,
        s1_run=args.s1_run,
        s5_run=args.s5_run,
    )
    write_json(args.json_output, report)
    write_markdown(args.markdown_output, report)
    print(
        json.dumps(
            {
                "split": report["split_name"],
                "s5_false_positives": report["stack_delta_summary"][
                    "s5_false_positives"
                ],
                "s5_only_false_positives": report["stack_delta_summary"][
                    "s5_only_false_positives"
                ],
                "s5_recovered_s1_false_negatives": report["stack_delta_summary"][
                    "s5_recovered_s1_false_negatives"
                ],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


def build_report(
    *,
    splits_path: Path,
    split_name: str,
    e3_payload_path: Path,
    s1_run: str,
    s5_run: str,
) -> dict[str, Any]:
    ceiling_report = build_ceiling_report(
        splits_path=splits_path,
        split_name=split_name,
        e3_payload_path=e3_payload_path,
        s1_run=s1_run,
        s5_run=s5_run,
    )
    e3_payload = json.loads(e3_payload_path.read_text(encoding="utf-8"))
    s1_predictions = _load_prediction_set(s1_run)
    s5_predictions = _load_prediction_set(s5_run)

    interference_rows = _build_interference_rows(
        ceiling_report=ceiling_report,
        e3_rows=e3_payload["rows"],
        s1_predictions=s1_predictions,
        s5_predictions=s5_predictions,
    )
    category_counts = Counter(row["primary_category"] for row in interference_rows)
    s5_only_rows = [row for row in interference_rows if row["stack_delta"] == "s5_only_fp"]
    shared_rows = [
        row for row in interference_rows if row["stack_delta"] == "shared_s1_s5_fp"
    ]
    recovered = _s5_recovered_s1_false_negatives(ceiling_report)

    s1_summary = ceiling_report["surface_summaries"]["s1_gpt_surface"]
    s5_summary = ceiling_report["surface_summaries"]["s5_gpt_surface"]

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "kanban_card": "E7 - Medication Stack-Interference Probe",
        "dataset": "exect_v2",
        "split_name": split_name,
        "split_file": splits_path.as_posix(),
        "component": "annotated_medication current-Rx stack interference",
        "model_provider": "GPT 4.1-mini / OpenAI for S1/S5 comparison surfaces",
        "scorer_mode": "medication-only slice of exect_field_family_deterministic_v1",
        "lifecycle_policy": (
            "Lifecycle rows are diagnostic attribution strata only; they do not "
            "change benchmark-facing medication F1."
        ),
        "source_artifacts": {
            "e3_payload": e3_payload_path.as_posix(),
            "e6_ceiling_probe": (
                "docs/experiments/exect/"
                "exect_medication_current_rx_ceiling_probe_20260528.json"
            ),
            "s1_run": s1_run,
            "s5_run": s5_run,
        },
        "surface_summaries": {
            "s1_gpt_surface": s1_summary,
            "s5_gpt_surface": s5_summary,
        },
        "stack_delta_summary": {
            "s1_false_positives": s1_summary["fp"],
            "s5_false_positives": s5_summary["fp"],
            "s5_only_false_positives": len(s5_only_rows),
            "shared_s1_s5_false_positives": len(shared_rows),
            "s5_recovered_s1_false_negatives": len(recovered),
            "s1_medication_f1": s1_summary["f1"],
            "s5_medication_f1": s5_summary["f1"],
            "s5_precision_loss_vs_s1": s1_summary["precision"] - s5_summary["precision"],
            "s5_recall_gain_vs_s1": s5_summary["recall"] - s1_summary["recall"],
        },
        "interference_category_counts": dict(sorted(category_counts.items())),
        "interference_rows": interference_rows,
        "recovered_s1_false_negatives": recovered,
        "decision": {
            "dominant_failure": (
                "S5 preserves and recovers current-Rx recall, but broad-stack "
                "context adds eight S5-only medication false positives."
            ),
            "next_mechanism": (
                "payload routing or prompt isolation before a broader medication "
                "temporality guard"
            ),
            "am_guard_status": (
                "The current non-ASM/brand guard is useful but insufficient for "
                "planned, historical, other-medication, and annotation-policy "
                "leakage."
            ),
        },
        "caveats": [
            "This is a validation-split no-model/artifact replay analysis.",
            "S1 and S5 comparison runs are archived provenance artifacts resolved by explicit opt-in.",
            "Cross-family prompt interference is inferred from S1-vs-S5 differential behavior, not from a randomized prompt isolation run.",
            "No loader, scorer, split, benchmark bridge, prompt, model-output, or run artifact semantics changed.",
        ],
    }


def _build_interference_rows(
    *,
    ceiling_report: dict[str, Any],
    e3_rows: list[dict[str, Any]],
    s1_predictions: PredictionSet,
    s5_predictions: PredictionSet,
) -> list[dict[str, Any]]:
    s1_fp_by_doc = _residual_value_sets(
        ceiling_report["residuals"]["s1_gpt_surface"]["rows"],
        "false_positives",
    )
    s5_fp_rows = ceiling_report["residuals"]["s5_gpt_surface"]["rows"]
    e3_by_doc = {row["document_id"]: row for row in e3_rows}
    s1_by_doc = _prediction_by_doc(s1_predictions)
    s5_by_doc = _prediction_by_doc(s5_predictions)

    rows: list[dict[str, Any]] = []
    for residual in s5_fp_rows:
        document_id = residual["document_id"]
        e3_row = e3_by_doc[document_id]
        for value in residual["false_positives"]:
            normalized = canonical_medication_name(value)
            s5_value = _prediction_value_for_medication(
                s5_by_doc.get(document_id), normalized
            )
            s1_value = _prediction_value_for_medication(
                s1_by_doc.get(document_id), normalized
            )
            payload_rows = _payload_rows_for_medication(e3_row, normalized)
            category = _primary_interference_category(
                normalized=normalized,
                e3_row=e3_row,
                payload_rows=payload_rows,
                predicted_evidence=_evidence_texts(s5_value),
            )
            stack_delta = (
                "shared_s1_s5_fp"
                if normalized in s1_fp_by_doc.get(document_id, set())
                else "s5_only_fp"
            )
            rows.append(
                {
                    "document_id": document_id,
                    "medication": normalized,
                    "stack_delta": stack_delta,
                    "primary_category": category,
                    "s1_predicted": s1_value is not None,
                    "s5_predicted": s5_value is not None,
                    "s5_evidence": _evidence_texts(s5_value),
                    "e3_payload_matches": [
                        _compact_payload_row(payload_row) for payload_row in payload_rows
                    ],
                    "gold_current_medications": e3_row["gold_current_medications"],
                }
            )
    return rows


def _residual_value_sets(
    rows: list[dict[str, Any]],
    key: str,
) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for row in rows:
        result[row["document_id"]] = {
            canonical_medication_name(value) for value in row[key]
        }
    return result


def _s5_recovered_s1_false_negatives(
    ceiling_report: dict[str, Any],
) -> list[dict[str, str]]:
    s1_fn_by_doc = _residual_value_sets(
        ceiling_report["residuals"]["s1_gpt_surface"]["rows"],
        "false_negatives",
    )
    s5_fn_by_doc = _residual_value_sets(
        ceiling_report["residuals"]["s5_gpt_surface"]["rows"],
        "false_negatives",
    )
    recovered = []
    for document_id, s1_fns in sorted(s1_fn_by_doc.items()):
        for medication in sorted(s1_fns - s5_fn_by_doc.get(document_id, set())):
            recovered.append({"document_id": document_id, "medication": medication})
    return recovered


def _prediction_by_doc(prediction_set: PredictionSet) -> dict[str, DocumentPrediction]:
    return {
        prediction.document_id: prediction for prediction in prediction_set.predictions
    }


def _prediction_value_for_medication(
    prediction: DocumentPrediction | None,
    medication: str,
) -> Any | None:
    if prediction is None:
        return None
    for value in prediction.values:
        if value.field_name != "annotated_medication":
            continue
        normalized = canonical_medication_name(
            value.normalized_value or value.raw_value
        )
        if normalized == medication:
            return value
    return None


def _payload_rows_for_medication(
    e3_row: dict[str, Any],
    medication: str,
) -> list[dict[str, Any]]:
    return [
        payload_row
        for payload_row in e3_row["payload_rows"]
        if payload_row["canonical_medication"] == medication
    ]


def _primary_interference_category(
    *,
    normalized: str,
    e3_row: dict[str, Any],
    payload_rows: list[dict[str, Any]],
    predicted_evidence: list[str],
) -> str:
    evidence_blob = " ".join(
        [*(row.get("evidence_text") or "" for row in payload_rows), *predicted_evidence]
    ).lower()
    if _has_planned_or_future_cue(payload_rows, evidence_blob):
        return "planned_or_future_evidence"
    if _has_historical_or_switched_cue(payload_rows, evidence_blob):
        return "historical_failed_or_switched_evidence"
    if _has_other_medication_cue(payload_rows, evidence_blob):
        return "other_medication_or_non_current_section"
    if normalized not in {
        canonical_medication_name(value)
        for value in e3_row["gold_current_medications"]
    }:
        return "missing_gold_or_annotation_policy"
    if any(row.get("dose_only") for row in payload_rows):
        return "dose_only_or_dose_line_leakage"
    return "over_emission_extra_current_rx_surface"


def _has_planned_or_future_cue(
    payload_rows: list[dict[str, Any]],
    evidence_blob: str,
) -> bool:
    if any(row["lifecycle_status"] == "planned" for row in payload_rows):
        return True
    markers = (
        "to start",
        "suggest starting",
        "suggest maybe",
        "would therefore suggest starting",
        "in the future",
        "future we can consider",
    )
    return any(marker in evidence_blob for marker in markers)


def _has_historical_or_switched_cue(
    payload_rows: list[dict[str, Any]],
    evidence_blob: str,
) -> bool:
    if any(row["lifecycle_status"] == "previous" for row in payload_rows):
        return True
    markers = (
        "old notes",
        "wasn\u2019t effective",
        "wasn't effective",
        "changed from",
        "switch from",
        "switched from",
        "not well controlled on",
        "initially",
    )
    return any(marker in evidence_blob for marker in markers)


def _has_other_medication_cue(
    payload_rows: list[dict[str, Any]],
    evidence_blob: str,
) -> bool:
    if "other medication" in evidence_blob:
        return True
    return any(
        row.get("section") in {"investigations", "comorbidity"}
        and not row.get("prescription_list_member")
        for row in payload_rows
    )


def _compact_payload_row(payload_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_kind": payload_row["source_kind"],
        "raw_text": payload_row["raw_text"],
        "lifecycle_status": payload_row["lifecycle_status"],
        "benchmark_role": payload_row["benchmark_role"],
        "is_asm": payload_row["is_asm"],
        "prescription_list_member": payload_row["prescription_list_member"],
        "dose_line": payload_row["dose_line"],
        "taper_or_stop": payload_row["taper_or_stop"],
        "section": payload_row["section"],
        "evidence_text": payload_row["evidence_text"],
    }


def _evidence_texts(value: Any | None) -> list[str]:
    if value is None:
        return []
    return [span.text for span in value.evidence if span.text]


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


def render_markdown(report: dict[str, Any]) -> str:
    s1 = report["surface_summaries"]["s1_gpt_surface"]
    s5 = report["surface_summaries"]["s5_gpt_surface"]
    delta = report["stack_delta_summary"]
    lines = [
        "# ExECT Medication Stack-Interference Probe",
        "",
        "Date: 2026-05-28",
        "Status: current synthesis; diagnostic stack-interference attribution",
        "Kanban card: E7 - Medication Stack-Interference Probe",
        f"Dataset/split: ExECTv2 `{report['split_name']}` ({s5['documents']} documents)",
        "Model/provider: GPT 4.1-mini / OpenAI for S1/S5 comparison surfaces",
        f"Scorer mode: `{report['scorer_mode']}`",
        "",
        "## Summary",
        "",
        (
            "S5 medication loss is a precision/interference problem, not a "
            f"current-Rx coverage problem. S1 scores **{s1['f1']:.1%} F1** "
            f"({s1['tp']} TP / {s1['fp']} FP / {s1['fn']} FN), while S5 scores "
            f"**{s5['f1']:.1%} F1** ({s5['tp']} TP / {s5['fp']} FP / {s5['fn']} FN)."
        ),
        "",
        (
            f"S5 adds **{delta['s5_only_false_positives']}** false positives that "
            "S1 avoided, while recovering the two S1 false negatives. The current "
            "AM guard fixed the earlier non-ASM/brand failure mode enough to reach "
            "full recall, but it does not isolate current-Rx medication from plan, "
            "history, other-medication, or annotation-policy contexts."
        ),
        "",
        "## S1 Versus S5 Delta",
        "",
        "| Surface | Precision | Recall | F1 | TP | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| S1 GPT medication surface | {s1['precision']:.1%} | {s1['recall']:.1%} | "
            f"{s1['f1']:.1%} | {s1['tp']} | {s1['fp']} | {s1['fn']} |"
        ),
        (
            f"| S5 GPT medication surface | {s5['precision']:.1%} | {s5['recall']:.1%} | "
            f"{s5['f1']:.1%} | {s5['tp']} | {s5['fp']} | {s5['fn']} |"
        ),
        "",
        "| Delta item | Count |",
        "| --- | ---: |",
        f"| S5-only false positives | {delta['s5_only_false_positives']} |",
        f"| Shared S1/S5 false positives | {delta['shared_s1_s5_false_positives']} |",
        f"| S5 recovered S1 false negatives | {delta['s5_recovered_s1_false_negatives']} |",
        "",
        "## Attribution Categories",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]
    for category, count in report["interference_category_counts"].items():
        lines.append(f"| `{category}` | {count} |")

    lines.extend(
        [
            "",
            "## Row-Level Interference",
            "",
            "| Document | Medication | Delta | Category | Evidence cue |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["interference_rows"]:
        cue = _markdown_evidence_cue(row)
        lines.append(
            f"| `{row['document_id']}` | `{row['medication']}` | "
            f"`{row['stack_delta']}` | `{row['primary_category']}` | {cue} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Over-emission is the right headline: S5 has 12 medication false positives and no false negatives.",
            "- The S5-only errors are consistent with broad-stack context pulling plan/history/other-medication evidence into the narrow annotated-medication slot.",
            "- A broader temporality guard is not the immediate next step; first test payload routing or prompt isolation so medication sees a current-Rx substrate before family stacking.",
            "- Lifecycle categories remain diagnostic only under E5; no medication scorer semantics changed.",
            "",
            "## Reproducibility",
            "",
            f"- E3 payload: `{report['source_artifacts']['e3_payload']}`",
            f"- E6 ceiling probe: `{report['source_artifacts']['e6_ceiling_probe']}`",
            f"- S1 comparison run: `{report['source_artifacts']['s1_run']}`",
            f"- S5 comparison run: `{report['source_artifacts']['s5_run']}`",
            "- No model calls, scorer changes, loader changes, split changes, benchmark bridge changes, prompt changes, or artifact mutations were made.",
            "",
        ]
    )
    return "\n".join(lines)


def _markdown_evidence_cue(row: dict[str, Any]) -> str:
    if row["s5_evidence"]:
        return _escape_table_text(row["s5_evidence"][0])
    if row["e3_payload_matches"]:
        return _escape_table_text(row["e3_payload_matches"][0]["evidence_text"])
    return "n/a"


def _escape_table_text(value: str) -> str:
    value = " ".join(value.split())
    if len(value) > 110:
        value = f"{value[:107]}..."
    return value.replace("|", "\\|")


if __name__ == "__main__":
    main()
