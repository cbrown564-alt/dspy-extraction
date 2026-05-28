"""Export the E6 ExECT medication current-Rx isolated ceiling probe."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.exect import canonical_medication_name
from clinical_extraction.evaluation.exect import score_exect_document
from clinical_extraction.paths import resolve_run_directory
from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExectGoldDocument,
    ExtractedValue,
    PredictionSet,
)
from clinical_extraction.evaluation.exect_medication_current_rx_lifecycle_payload import (
    DEFAULT_JSON_OUTPUT as DEFAULT_E3_PAYLOAD,
    build_report as build_e3_report,
)

DEFAULT_SPLITS = Path("data/splits/exectv2_splits.json")
DEFAULT_OUTPUT_JSON = Path(
    "docs/experiments/exect/"
    "exect_medication_current_rx_ceiling_probe_20260528.json"
)
DEFAULT_OUTPUT_MARKDOWN = Path(
    "docs/experiments/exect/"
    "exect_medication_current_rx_ceiling_probe_20260528.md"
)
DEFAULT_S1_RUN = (
    "exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z"
)
DEFAULT_S5_RUN = (
    "exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_"
    "20260524T211229Z"
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
                "isolated_medication_f1": report["surface_summaries"][
                    "isolated_current_rx_payload"
                ]["f1"],
                "s1_medication_f1": report["surface_summaries"]["s1_gpt_surface"][
                    "f1"
                ],
                "s5_medication_f1": report["surface_summaries"]["s5_gpt_surface"][
                    "f1"
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
    e3_payload = _load_or_build_e3_payload(e3_payload_path, splits_path, split_name)
    gold_by_id = _gold_rows_from_e3_payload(e3_payload)
    isolated_predictions = _isolated_prediction_set_from_e3_payload(e3_payload)

    surfaces = {
        "isolated_current_rx_payload": {
            "label": "Isolated E3 annotation current-Rx payload",
            "classification": "isolated ceiling / no-model oracle substrate",
            "model_provider": "none",
            "run_id": None,
            "prediction_set": isolated_predictions,
        },
        "s1_gpt_surface": {
            "label": "Existing S1 GPT medication surface",
            "classification": "existing S1 operational surface",
            "model_provider": "GPT 4.1-mini / OpenAI",
            "run_id": s1_run,
            "prediction_set": _load_prediction_set(s1_run),
        },
        "s5_gpt_surface": {
            "label": "Existing S5 GPT medication surface",
            "classification": "existing stacked S5 operational surface",
            "model_provider": "GPT 4.1-mini / OpenAI",
            "run_id": s5_run,
            "prediction_set": _load_prediction_set(s5_run),
        },
    }

    summaries: dict[str, Any] = {}
    residuals: dict[str, Any] = {}
    for surface_name, surface in surfaces.items():
        summary, surface_residuals = _score_medication_surface(
            surface["prediction_set"],
            gold_by_id=gold_by_id,
            e3_rows=e3_payload["rows"],
        )
        summaries[surface_name] = {
            **summary,
            "label": surface["label"],
            "classification": surface["classification"],
            "model_provider": surface["model_provider"],
            "run_id": surface["run_id"],
        }
        residuals[surface_name] = surface_residuals

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "kanban_card": "E6 - Medication Isolated Current-Rx Ceiling Probe",
        "dataset": "exect_v2",
        "split_name": split_name,
        "split_file": splits_path.as_posix(),
        "component": "annotated_medication current-Rx",
        "scorer_mode": "medication-only slice of exect_field_family_deterministic_v1",
        "bridge_normalization_policy": (
            "canonical medication names from the current ExECT medication benchmark bridge; "
            "Prescription JSON annotations remain benchmark current-Rx."
        ),
        "lifecycle_policy": (
            "Lifecycle rows are diagnostic residual strata only and are not scored as "
            "medication F1."
        ),
        "source_artifacts": {
            "e3_payload": e3_payload_path.as_posix(),
            "s1_run": s1_run,
            "s5_run": s5_run,
        },
        "surface_summaries": summaries,
        "residuals": residuals,
        "lifecycle_diagnostics": {
            "case_counts": e3_payload["lifecycle_case_counts"],
            "status_counts": e3_payload["lifecycle_status_counts"],
        },
        "decision": {
            "current_rx_ceiling": "reached by the annotation-derived no-model payload",
            "isolated_ceiling_f1": summaries["isolated_current_rx_payload"]["f1"],
            "s1_gap": _gap_from_ceiling(summaries["s1_gpt_surface"]["f1"]),
            "s5_gap": _gap_from_ceiling(summaries["s5_gpt_surface"]["f1"]),
            "next_action": (
                "Use E7 to attribute stack interference and over-emission before changing "
                "the stacked medication prompt or bridge."
            ),
        },
        "caveats": [
            "This is a validation-split component probe; test remains holdout for residual analysis only.",
            "The isolated payload is a no-model annotation substrate, not a deployed extraction model.",
            "Lifecycle, temporality, planned, previous, taper, and dose-only rows do not enter medication F1.",
            "S1 and S5 comparison runs are archived provenance artifacts resolved by explicit opt-in.",
            "No loader, scorer, split, benchmark bridge, prompt, or model-output semantics changed.",
        ],
    }


def _load_or_build_e3_payload(
    path: Path,
    splits_path: Path,
    split_name: str,
) -> dict[str, Any]:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return build_e3_report(splits_path, split_name)


def _gold_rows_from_e3_payload(payload: dict[str, Any]) -> dict[str, ExectGoldDocument]:
    return {
        row["document_id"]: ExectGoldDocument(
            document_id=row["document_id"],
            text="",
            current_medications=[
                canonical_medication_name(value)
                for value in row["gold_current_medications"]
            ],
        )
        for row in payload["rows"]
    }


def _isolated_prediction_set_from_e3_payload(payload: dict[str, Any]) -> PredictionSet:
    predictions = []
    for row in payload["rows"]:
        values = []
        annotation_rows_by_med = _annotation_rows_by_medication(row)
        for medication in row["current_rx_values"]:
            payload_row = annotation_rows_by_med.get(medication, {})
            evidence_text = str(payload_row.get("evidence_text") or "")
            evidence = []
            if evidence_text:
                evidence.append(
                    EvidenceSpan(
                        document_id=row["document_id"],
                        text=evidence_text,
                        start=payload_row.get("start"),
                        end=payload_row.get("end"),
                        section=payload_row.get("section"),
                    )
                )
            values.append(
                ExtractedValue(
                    field_name="annotated_medication",
                    raw_value=medication,
                    normalized_value=medication,
                    evidence=evidence,
                    temporality="not_applicable",
                    negation="affirmed",
                    quality_flags=["e6:annotation_current_rx_payload"],
                    metadata={
                        "payload_id": "exect.medication.rx_candidates.v1",
                        "source_kind": "annotation_prescription",
                    },
                )
            )
        predictions.append(
            DocumentPrediction(
                document_id=row["document_id"],
                dataset="exect_v2",
                schema_level="exect_medication_current_rx_isolated",
                values=values,
                metadata={"component": "annotated_medication_current_rx"},
            )
        )
    return PredictionSet(
        dataset="exect_v2",
        schema_level="exect_medication_current_rx_isolated",
        predictions=predictions,
        metadata={
            "program_variant": "e6_annotation_current_rx_payload",
            "model_provider": "none",
        },
    )


def _annotation_rows_by_medication(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result = {}
    for payload_row in row["payload_rows"]:
        if payload_row["source_kind"] != "annotation_prescription":
            continue
        medication = payload_row["canonical_medication"]
        result.setdefault(medication, payload_row)
    return result


def _load_prediction_set(run_id: str) -> PredictionSet:
    run_dir = resolve_run_directory(run_id, include_archive=True)
    payload = json.loads((run_dir / "predictions.json").read_text(encoding="utf-8"))
    return PredictionSet.model_validate(payload)


def _score_medication_surface(
    prediction_set: PredictionSet,
    *,
    gold_by_id: dict[str, ExectGoldDocument],
    e3_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    predictions_by_id = {
        prediction.document_id: prediction for prediction in prediction_set.predictions
    }
    tp = fp = fn = 0
    row_residuals = []
    for document_id, gold in sorted(gold_by_id.items()):
        prediction = predictions_by_id.get(
            document_id,
            DocumentPrediction(
                document_id=document_id,
                dataset="exect_v2",
                schema_level=prediction_set.schema_level,
            ),
        )
        score = score_exect_document(gold=gold, prediction=prediction)
        med_score = score.field_scores["annotated_medication"]
        tp += len(med_score.true_positives)
        fp += len(med_score.false_positives)
        fn += len(med_score.false_negatives)
        if med_score.false_positives or med_score.false_negatives:
            row_residuals.append(
                {
                    "document_id": document_id,
                    "false_positives": med_score.false_positives,
                    "false_negatives": med_score.false_negatives,
                    "categories": _residual_categories(
                        document_id,
                        false_positives=med_score.false_positives,
                        false_negatives=med_score.false_negatives,
                        e3_rows=e3_rows,
                    ),
                }
            )
    summary = {
        "documents": len(gold_by_id),
        "gold_support": sum(len(gold.current_medications) for gold in gold_by_id.values()),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": _precision(tp, fp),
        "recall": _recall(tp, fn),
        "f1": _f1(tp, fp, fn),
    }
    category_counts = Counter(
        category
        for residual in row_residuals
        for category in residual["categories"]
    )
    return summary, {
        "row_count": len(row_residuals),
        "category_counts": dict(sorted(category_counts.items())),
        "rows": row_residuals,
    }


def _residual_categories(
    document_id: str,
    *,
    false_positives: list[str],
    false_negatives: list[str],
    e3_rows: list[dict[str, Any]],
) -> list[str]:
    row = next(item for item in e3_rows if item["document_id"] == document_id)
    categories = []
    for value in false_positives:
        categories.append(f"fp:{_classify_false_positive(value, row)}")
    for value in false_negatives:
        current_values = set(row["current_rx_values"])
        if value in current_values:
            categories.append("fn:annotation_current_rx_missed_by_surface")
        else:
            categories.append("fn:gold_not_in_e3_current_rx_payload")
    return sorted(categories)


def _classify_false_positive(value: str, row: dict[str, Any]) -> str:
    normalized = canonical_medication_name(value)
    payload_rows = [
        payload_row
        for payload_row in row["payload_rows"]
        if payload_row["canonical_medication"] == normalized
    ]
    if not row["gold_current_medications"]:
        return "missing_gold_or_no_current_rx_gold"
    if not payload_rows:
        return "over_emission_no_e3_payload_row"
    if any(not payload_row["is_asm"] for payload_row in payload_rows):
        return "non_asm_leakage"
    if any(payload_row["lifecycle_status"] == "planned" for payload_row in payload_rows):
        return "planned_or_future_evidence"
    if any(payload_row["lifecycle_status"] == "previous" for payload_row in payload_rows):
        return "historical_or_previous_evidence"
    if any(payload_row["taper_or_stop"] for payload_row in payload_rows):
        return "taper_or_stop_evidence"
    if any(payload_row["dose_line"] for payload_row in payload_rows):
        return "dose_line_or_unknown_temporality_evidence"
    return "over_emission_extra_current_rx_surface"


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


def render_markdown(report: dict[str, Any]) -> str:
    summaries = report["surface_summaries"]
    lines = [
        "# ExECT Medication Current-Rx Isolated Ceiling Probe",
        "",
        "Date: 2026-05-28",
        "Status: current synthesis; isolated component ceiling probe",
        "Kanban card: E6 - Medication Isolated Current-Rx Ceiling Probe",
        f"Dataset/split: ExECTv2 `{report['split_name']}` "
        f"({summaries['isolated_current_rx_payload']['documents']} documents)",
        "Model/provider: none for isolated payload; GPT 4.1-mini / OpenAI for S1/S5 comparison surfaces",
        f"Scorer mode: `{report['scorer_mode']}`",
        "",
        "## Summary",
        "",
        (
            "The E3 annotation-derived current-Rx payload reaches an isolated "
            f"medication ceiling of **{summaries['isolated_current_rx_payload']['f1']:.1%} F1** "
            f"({summaries['isolated_current_rx_payload']['tp']}/"
            f"{summaries['isolated_current_rx_payload']['gold_support']} labels)."
        ),
        "",
        (
            "Existing model surfaces remain below that ceiling: S1 GPT is "
            f"**{summaries['s1_gpt_surface']['f1']:.1%} F1** and S5 GPT is "
            f"**{summaries['s5_gpt_surface']['f1']:.1%} F1** on the same "
            "validation medication target."
        ),
        "",
        "## Medication Metrics",
        "",
        "| Surface | Precision | Recall | F1 | TP | FP | FN | Support |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key in (
        "isolated_current_rx_payload",
        "s1_gpt_surface",
        "s5_gpt_surface",
    ):
        surface = summaries[key]
        lines.append(
            f"| {surface['label']} | {_fmt_pct(surface['precision'])} | "
            f"{_fmt_pct(surface['recall'])} | {_fmt_pct(surface['f1'])} | "
            f"{surface['tp']} | {surface['fp']} | {surface['fn']} | "
            f"{surface['gold_support']} |"
        )
    lines.extend(
        [
            "",
            "## Residual Categories",
            "",
            "| Surface | Residual docs | Categories |",
            "| --- | ---: | --- |",
        ]
    )
    for key in ("s1_gpt_surface", "s5_gpt_surface"):
        residual = report["residuals"][key]
        lines.append(
            f"| {summaries[key]['label']} | {residual['row_count']} | "
            f"{_format_category_counts(residual['category_counts'])} |"
        )
    lines.extend(
        [
            "",
            "## Lifecycle Diagnostics",
            "",
            "| Case type | Count |",
            "| --- | ---: |",
        ]
    )
    for key, value in report["lifecycle_diagnostics"]["case_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Annotated current-Rx is now an isolated no-model ceiling for the benchmark-facing medication component.",
            "- S1 loss is small and mixed: two current-Rx misses plus brand/surface mismatch and missing-gold false positives.",
            "- S5 reaches full recall but loses precision through extra medication emissions, which routes naturally to E7 stack-interference attribution.",
            "- Lifecycle rows remain diagnostic only; planned, previous, taper, dose-only, and unknown-temporality rows do not enter medication F1.",
            "",
            "## Reproducibility",
            "",
            f"- E3 payload: `{report['source_artifacts']['e3_payload']}`",
            f"- S1 comparison run: `{report['source_artifacts']['s1_run']}`",
            f"- S5 comparison run: `{report['source_artifacts']['s5_run']}`",
            "- No model calls, scorer changes, loader changes, split changes, benchmark bridge changes, or prompt changes were made.",
            "",
        ]
    )
    return "\n".join(lines)


def _format_category_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return "; ".join(f"`{key}` {value}" for key, value in counts.items())


def _gap_from_ceiling(value: float | None) -> float | None:
    if value is None:
        return None
    return 1.0 - value


def _precision(tp: int, fp: int) -> float | None:
    return tp / (tp + fp) if tp + fp else None


def _recall(tp: int, fn: int) -> float | None:
    return tp / (tp + fn) if tp + fn else None


def _f1(tp: int, fp: int, fn: int) -> float | None:
    precision = _precision(tp, fp)
    recall = _recall(tp, fn)
    if precision is None and recall is None:
        return None
    if not precision or not recall:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


if __name__ == "__main__":
    main()
