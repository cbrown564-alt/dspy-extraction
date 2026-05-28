"""Build the E11 ExECT holdout residual-attribution report.

This is an artifact-only analysis. It reads frozen validation/test run outputs
and no-model substrate probes to attribute holdout drops without changing
scorers, loaders, splits, bridges, prompts, or predictions.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from clinical_extraction.datasets.exect import load_exect_gold_documents
from clinical_extraction.evaluation.exect_frequency_candidate_selection_probe import (
    build_report as build_frequency_selection_report,
)
from clinical_extraction.evaluation.exect_medication_current_rx_ceiling_probe import (
    build_report as build_medication_ceiling_report,
)
from clinical_extraction.evaluation.exect_s1_split_audit import summarize_s1_run
from clinical_extraction.paths import PROJECT_ROOT, resolve_run_directory

DEFAULT_SPLITS = Path("data/splits/exectv2_splits.json")
DEFAULT_OUTPUT_JSON = Path(
    "docs/experiments/exect/"
    "exect_holdout_residual_attribution_e11_20260528.json"
)
DEFAULT_OUTPUT_MARKDOWN = Path(
    "docs/experiments/exect/"
    "exect_holdout_residual_attribution_e11_20260528.md"
)
DEFAULT_E2_AUDIT = Path(
    "docs/experiments/exect/exect_s1_raw_bridge_prompt_split_audit_20260528.json"
)
DEFAULT_E3_TEST_PAYLOAD = Path(
    "docs/experiments/exect/_e11_generated_test_medication_payload.json"
)
DEFAULT_E1_TEST_PAYLOAD = Path(
    "docs/experiments/exect/_e11_generated_test_frequency_payload.json"
)

S1_GPT_VALIDATION_RUN = "exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z"
S1_GPT_TEST_RUN = "exect_s0_s1_validation_test_gpt4_1_mini_20260526T184057Z"
S1_QWEN_VALIDATION_RUN = (
    "exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_ollama_"
    "20260525T103640Z"
)
S1_QWEN_TEST_RUN = (
    "test_holdout_exect_s1_clean_ladder_v2_diagnosis_stable_full_qwen35b_"
    "ollama_20260526T184101Z"
)

S4_GPT_VALIDATION_RUN = "exect_s4_validation_full_gpt4_1_mini_20260520T071248Z"
S4_GPT_TEST_RUN = "test_holdout_exect_s4_validation_full_gpt4_1_mini_20260527T023724Z"
S5_GPT_VALIDATION_RUN = (
    "exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_"
    "gpt4_1_mini_20260524T211229Z"
)
S5_GPT_TEST_RUN = (
    "test_holdout_exect_s5_frequency_pre_vocab_am_guard_frequency_verify_"
    "v2b_full_gpt4_1_mini_20260527T055059Z"
)
S5_QWEN_VALIDATION_RUN = (
    "exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_"
    "qwen35b_ollama_20260525T072245Z"
)
S5_QWEN_TEST_RUN = (
    "test_holdout_exect_s5_frequency_pre_vocab_am_guard_frequency_verify_"
    "v2b_full_qwen35b_ollama_20260527T055854Z"
)

CORE_S1_FIELDS = ("diagnosis", "seizure_type", "annotated_medication")
S5_FIELDS = (
    "diagnosis",
    "seizure_type",
    "annotated_medication",
    "investigation",
    "seizure_frequency",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--e2-audit", type=Path, default=DEFAULT_E2_AUDIT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    args = parser.parse_args()

    report = build_report(splits_path=args.splits, e2_audit_path=args.e2_audit)
    write_json(args.json_output, report)
    write_markdown(args.markdown_output, report)
    print(
        json.dumps(
            {
                "kanban_card": report["kanban_card"],
                "gpt_s1_micro_delta": report["transfer_deltas"][
                    "s1_gpt_validation_to_test"
                ]["micro_f1_delta"],
                "gpt_s5_frequency_delta": report["transfer_deltas"][
                    "s5_gpt_validation_to_test"
                ]["field_f1_delta"]["seizure_frequency"],
                "test_frequency_payload_coverage": report["frequency_attribution"][
                    "test"
                ]["surface_summaries"]["broad_event_rate_payload"]["recall"],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


def build_report(
    *,
    splits_path: Path = DEFAULT_SPLITS,
    e2_audit_path: Path = DEFAULT_E2_AUDIT,
) -> dict[str, Any]:
    gold_text_by_id = {
        document.document_id: document.text for document in load_exect_gold_documents()
    }
    run_summaries = {
        "s1_gpt_validation": _run_metric_summary(
            S1_GPT_VALIDATION_RUN,
            label="S1 GPT validation",
            model_provider="GPT 4.1-mini / OpenAI",
            field_order=CORE_S1_FIELDS,
        ),
        "s1_gpt_test": _run_metric_summary(
            S1_GPT_TEST_RUN,
            label="S1 GPT test holdout",
            model_provider="GPT 4.1-mini / OpenAI",
            field_order=CORE_S1_FIELDS,
        ),
        "s1_qwen_validation": _run_metric_summary(
            S1_QWEN_VALIDATION_RUN,
            label="S1 Qwen validation",
            model_provider="Qwen3.6:35b / Ollama",
            field_order=CORE_S1_FIELDS,
        ),
        "s1_qwen_test": _run_metric_summary(
            S1_QWEN_TEST_RUN,
            label="S1 Qwen test holdout",
            model_provider="Qwen3.6:35b / Ollama",
            field_order=CORE_S1_FIELDS,
        ),
        "s5_gpt_validation": _run_metric_summary(
            S5_GPT_VALIDATION_RUN,
            label="S5 GPT validation",
            model_provider="GPT 4.1-mini / OpenAI",
            field_order=S5_FIELDS,
        ),
        "s5_gpt_test": _run_metric_summary(
            S5_GPT_TEST_RUN,
            label="S5 GPT test holdout",
            model_provider="GPT 4.1-mini / OpenAI",
            field_order=S5_FIELDS,
        ),
        "s5_qwen_validation": _run_metric_summary(
            S5_QWEN_VALIDATION_RUN,
            label="S5 Qwen validation",
            model_provider="Qwen3.6:35b / Ollama",
            field_order=S5_FIELDS,
        ),
        "s5_qwen_test": _run_metric_summary(
            S5_QWEN_TEST_RUN,
            label="S5 Qwen test holdout",
            model_provider="Qwen3.6:35b / Ollama",
            field_order=S5_FIELDS,
        ),
    }
    s1_residuals = {
        "s1_gpt_validation": _compact_s1_residual_summary(
            S1_GPT_VALIDATION_RUN,
            gold_text_by_id=gold_text_by_id,
        ),
        "s1_gpt_test": _compact_s1_residual_summary(
            S1_GPT_TEST_RUN,
            gold_text_by_id=gold_text_by_id,
        ),
        "s1_qwen_validation": _compact_s1_residual_summary(
            S1_QWEN_VALIDATION_RUN,
            gold_text_by_id=gold_text_by_id,
        ),
        "s1_qwen_test": _compact_s1_residual_summary(
            S1_QWEN_TEST_RUN,
            gold_text_by_id=gold_text_by_id,
        ),
    }

    frequency_validation = build_frequency_selection_report(
        splits_path=splits_path,
        split_name="validation",
        e1_payload_path=Path(
            "docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.json"
        ),
        s4_run=S4_GPT_VALIDATION_RUN,
        s5_run=S5_GPT_VALIDATION_RUN,
    )
    frequency_test = build_frequency_selection_report(
        splits_path=splits_path,
        split_name="test",
        e1_payload_path=DEFAULT_E1_TEST_PAYLOAD,
        s4_run=S4_GPT_TEST_RUN,
        s5_run=S5_GPT_TEST_RUN,
    )
    medication_test = build_medication_ceiling_report(
        splits_path=splits_path,
        split_name="test",
        e3_payload_path=DEFAULT_E3_TEST_PAYLOAD,
        s1_run=S1_GPT_TEST_RUN,
        s5_run=S5_GPT_TEST_RUN,
    )

    e2_audit = _read_json(e2_audit_path)
    transfer_deltas = {
        "s1_gpt_validation_to_test": _transfer_delta(
            run_summaries["s1_gpt_validation"],
            run_summaries["s1_gpt_test"],
        ),
        "s1_qwen_validation_to_test": _transfer_delta(
            run_summaries["s1_qwen_validation"],
            run_summaries["s1_qwen_test"],
        ),
        "s5_gpt_validation_to_test": _transfer_delta(
            run_summaries["s5_gpt_validation"],
            run_summaries["s5_gpt_test"],
        ),
        "s5_qwen_validation_to_test": _transfer_delta(
            run_summaries["s5_qwen_validation"],
            run_summaries["s5_qwen_test"],
        ),
    }

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "kanban_card": "E11 - ExECT Holdout Residual Attribution",
        "status": "current synthesis; diagnostic holdout residual analysis",
        "dataset": "exect_v2",
        "splits": ["exectv2_fixed_v1:validation", "exectv2_fixed_v1:test"],
        "model_calls": 0,
        "scorer_semantics_changed": False,
        "loader_split_bridge_prompt_changed": False,
        "run_summaries": run_summaries,
        "transfer_deltas": transfer_deltas,
        "s1_raw_bridge_prompt_context": {
            "source_artifact": e2_audit_path.as_posix(),
            "stage_deltas": e2_audit["stage_deltas"],
            "qwen_holdout_residual_classes": e2_audit["residual_comparison"][
                "qwen_clean_test_holdout"
            ],
            "caveat": (
                "Raw/bridge prompt split is available for validation and Qwen "
                "holdout artifact replay; GPT holdout raw-no-bridge replay was "
                "not newly run."
            ),
        },
        "s1_residual_attribution": s1_residuals,
        "frequency_attribution": {
            "validation": _compact_frequency_attribution(frequency_validation),
            "test": _compact_frequency_attribution(frequency_test),
            "interpretation": _frequency_interpretation(
                frequency_validation,
                frequency_test,
                run_summaries["s5_gpt_validation"],
                run_summaries["s5_gpt_test"],
            ),
        },
        "medication_attribution": _compact_medication_attribution(medication_test),
        "stack_interference": {
            "gpt_validation_s5_minus_s1": _shared_field_delta(
                run_summaries["s1_gpt_validation"],
                run_summaries["s5_gpt_validation"],
                fields=CORE_S1_FIELDS,
            ),
            "gpt_test_s5_minus_s1": _shared_field_delta(
                run_summaries["s1_gpt_test"],
                run_summaries["s5_gpt_test"],
                fields=CORE_S1_FIELDS,
            ),
            "qwen_validation_s5_minus_s1": _shared_field_delta(
                run_summaries["s1_qwen_validation"],
                run_summaries["s5_qwen_validation"],
                fields=CORE_S1_FIELDS,
            ),
            "qwen_test_s5_minus_s1": _shared_field_delta(
                run_summaries["s1_qwen_test"],
                run_summaries["s5_qwen_test"],
                fields=CORE_S1_FIELDS,
            ),
        },
        "decision": {
            "s1_drop_attribution": (
                "Diagnosis and seizure-type transfer dominate the S1 drop; "
                "medication remains stable. Residuals expand in extraction, "
                "bridge, policy, specificity, and scope classes, so S1 remains "
                "validation-aligned rather than an isolated ceiling."
            ),
            "s5_frequency_drop_attribution": (
                "S5 frequency loss is split between holdout payload "
                "representability and candidate adjudication/label construction. "
                "The broad validation payload covers 43/43 validation labels but "
                "only 31/44 holdout labels."
            ),
            "s5_medication_drop_attribution": (
                "Medication current-Rx is representable on holdout by the "
                "annotation-derived payload, but S5 loses precision and recall "
                "relative to S1 under the stacked prompt."
            ),
            "next_exect_action": (
                "Use validation-only component probes for S1 diagnosis/seizure "
                "transfer, frequency payload generalization, and medication "
                "payload routing/prompt isolation before rebuilding broad stacks."
            ),
        },
        "caveats": [
            "Holdout is used for residual attribution only, not prompt, scorer, loader, split, bridge, or repair tuning.",
            "Current ExECT project scorers are field-family diagnostic/project scorers, not CUI-aware Table 1 reproduction.",
            "Frequency labels use ExECT SeizureFrequency annotation surfaces, not Gan monthly-frequency normalization.",
            "Medication lifecycle categories remain diagnostic; annotated current-Rx is the benchmark-facing medication surface.",
            "Stack-interference attribution is inferred from stored S1-vs-S5 behavior, not from a randomized prompt-isolation run.",
        ],
    }
    return report


def _run_metric_summary(
    run_id: str,
    *,
    label: str,
    model_provider: str,
    field_order: tuple[str, ...],
) -> dict[str, Any]:
    run_dir = resolve_run_directory(run_id, include_archive=True)
    metrics = _read_json(run_dir / "metrics.json")
    config = _read_json(run_dir / "config.json")
    benchmark = metrics["benchmark_metrics"]
    return {
        "label": label,
        "run_id": run_dir.name,
        "run_dir": _repo_relative_path(run_dir),
        "model_provider": model_provider,
        "split_name": config.get("split_name"),
        "schema_level": metrics.get("schema_level"),
        "scorer_mode": metrics.get("scorer") or config.get("scorer_mode"),
        "micro_precision": benchmark.get("micro_precision"),
        "micro_recall": benchmark.get("micro_recall"),
        "micro_f1": benchmark.get("micro_f1"),
        "field_precision": _ordered_field_map(
            benchmark.get("field_precision", {}),
            field_order=field_order,
        ),
        "field_recall": _ordered_field_map(
            benchmark.get("field_recall", {}),
            field_order=field_order,
        ),
        "field_f1": _ordered_field_map(
            benchmark.get("field_f1", {}),
            field_order=field_order,
        ),
        "field_support": _ordered_field_map(
            benchmark.get("field_support", {}),
            field_order=field_order,
        ),
        "diagnostic_metrics": {
            key: metrics.get("diagnostic_metrics", {}).get(key)
            for key in (
                "evidence_quote_support_rate",
                "documents_with_gold_quality_flags",
            )
        },
        "counts": metrics.get("counts", {}),
    }


def _compact_s1_residual_summary(
    run_id: str,
    *,
    gold_text_by_id: Mapping[str, str],
    sample_limit: int = 12,
) -> dict[str, Any]:
    run_dir = resolve_run_directory(run_id, include_archive=True)
    summary = summarize_s1_run(run_dir, gold_text_by_id=gold_text_by_id)
    return {
        "run_id": summary["run_id"],
        "split_name": summary["split_name"],
        "micro_f1": summary["micro_f1"],
        "field_f1": summary["field_f1"],
        "bridge_flag_counts": summary["bridge_flag_counts"],
        "bridge_flag_names": summary["bridge_flag_names"],
        "residual_class_counts": summary["residual_class_counts"],
        "residual_sample": summary["residuals"][:sample_limit],
    }


def _compact_frequency_attribution(report: Mapping[str, Any]) -> dict[str, Any]:
    surfaces = report["surface_summaries"]
    attribution = report["error_attribution"]
    selected = {
        key: {
            item: surfaces[key][item]
            for item in ("tp", "fp", "fn", "precision", "recall", "f1", "gold_support")
        }
        for key in (
            "broad_event_rate_payload",
            "candidate_constrained_oracle",
            "s4_gpt_frequency_surface",
            "s5_gpt_frequency_surface",
        )
    }
    return {
        "split_name": report["split_name"],
        "surface_summaries": selected,
        "broad_payload_category_counts": attribution["broad_event_rate_payload"][
            "category_counts"
        ],
        "s5_frequency_category_counts": attribution["s5_gpt_frequency_surface"][
            "category_counts"
        ],
        "s5_frequency_error_docs": attribution["s5_gpt_frequency_surface"][
            "row_count"
        ],
        "s5_frequency_residual_sample": attribution["s5_gpt_frequency_surface"][
            "rows"
        ][:12],
    }


def _compact_medication_attribution(report: Mapping[str, Any]) -> dict[str, Any]:
    surfaces = report["surface_summaries"]
    residuals = report["residuals"]
    return {
        "split_name": report["split_name"],
        "surface_summaries": {
            key: {
                item: surfaces[key][item]
                for item in ("tp", "fp", "fn", "precision", "recall", "f1", "gold_support")
            }
            for key in (
                "isolated_current_rx_payload",
                "s1_gpt_surface",
                "s5_gpt_surface",
            )
        },
        "s1_medication_category_counts": residuals["s1_gpt_surface"][
            "category_counts"
        ],
        "s5_medication_category_counts": residuals["s5_gpt_surface"][
            "category_counts"
        ],
        "s5_medication_residual_sample": residuals["s5_gpt_surface"]["rows"][:12],
    }


def _frequency_interpretation(
    validation: Mapping[str, Any],
    test: Mapping[str, Any],
    s5_validation: Mapping[str, Any],
    s5_test: Mapping[str, Any],
) -> dict[str, Any]:
    val_surfaces = validation["surface_summaries"]
    test_surfaces = test["surface_summaries"]
    val_broad = val_surfaces["broad_event_rate_payload"]
    test_broad = test_surfaces["broad_event_rate_payload"]
    val_oracle = val_surfaces["candidate_constrained_oracle"]
    test_oracle = test_surfaces["candidate_constrained_oracle"]
    return {
        "broad_payload_recall_delta": test_broad["recall"] - val_broad["recall"],
        "candidate_constrained_oracle_f1_delta": test_oracle["f1"] - val_oracle["f1"],
        "s5_frequency_f1_delta": (
            s5_test["field_f1"]["seizure_frequency"]
            - s5_validation["field_f1"]["seizure_frequency"]
        ),
        "test_s5_gap_to_payload_oracle": (
            test_surfaces["s5_gpt_frequency_surface"]["f1"] - test_oracle["f1"]
        ),
    }


def _transfer_delta(
    validation: Mapping[str, Any],
    test: Mapping[str, Any],
) -> dict[str, Any]:
    fields = sorted(set(validation["field_f1"]) | set(test["field_f1"]))
    return {
        "validation_run": validation["run_id"],
        "test_run": test["run_id"],
        "micro_f1_delta": test["micro_f1"] - validation["micro_f1"],
        "field_f1_delta": {
            field: test["field_f1"].get(field, 0.0)
            - validation["field_f1"].get(field, 0.0)
            for field in fields
        },
        "field_support_delta": {
            field: test["field_support"].get(field, 0)
            - validation["field_support"].get(field, 0)
            for field in fields
        },
        "evidence_quote_support_delta": (
            test["diagnostic_metrics"]["evidence_quote_support_rate"]
            - validation["diagnostic_metrics"]["evidence_quote_support_rate"]
        ),
    }


def _shared_field_delta(
    s1_summary: Mapping[str, Any],
    s5_summary: Mapping[str, Any],
    *,
    fields: tuple[str, ...],
) -> dict[str, float]:
    return {
        field: s5_summary["field_f1"][field] - s1_summary["field_f1"][field]
        for field in fields
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# ExECT Holdout Residual Attribution",
        "",
        "Date: 2026-05-28",
        "Status: current synthesis; diagnostic holdout residual analysis",
        "Kanban card: E11 - ExECT Holdout Residual Attribution",
        "Dataset/splits: ExECTv2 `validation` and frozen `test` holdout",
        "Model/provider: GPT 4.1-mini / OpenAI and Qwen3.6:35b / Ollama stored artifacts",
        "Model calls: 0",
        "Scorer mode: existing ExECT field-family scorers only",
        "",
        "## Summary",
        "",
        (
            "E11 attributes the ExECT holdout drop without tuning on holdout. "
            "S1 transfer loss is concentrated in diagnosis and seizure-type "
            "policy/bridge/extraction residuals, while annotated medication "
            "stays stable. S5 frequency loss is a mixed payload-generalization "
            "and adjudication problem: the broad frequency payload covers "
            "43/43 validation labels but only 31/44 holdout labels."
        ),
        "",
        (
            "The medication substrate does transfer: the annotation-derived "
            "current-Rx payload still reaches 53/53 holdout labels. S5 medication "
            "loss on holdout is therefore stack behavior, not a current-Rx "
            "representability failure."
        ),
        "",
        "## Transfer Deltas",
        "",
        "| Surface | Micro F1 val | Micro F1 test | Delta | Main field deltas |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for delta_key, val_key, test_key in (
        ("s1_gpt_validation_to_test", "s1_gpt_validation", "s1_gpt_test"),
        ("s1_qwen_validation_to_test", "s1_qwen_validation", "s1_qwen_test"),
        ("s5_gpt_validation_to_test", "s5_gpt_validation", "s5_gpt_test"),
        ("s5_qwen_validation_to_test", "s5_qwen_validation", "s5_qwen_test"),
    ):
        validation = report["run_summaries"][val_key]
        test = report["run_summaries"][test_key]
        delta = report["transfer_deltas"][delta_key]
        lines.append(
            f"| {validation['label'].replace(' validation', '')} | "
            f"{_pct(validation['micro_f1'])} | {_pct(test['micro_f1'])} | "
            f"{_pp(delta['micro_f1_delta'])} | "
            f"{_field_delta_cell(delta['field_f1_delta'])} |"
        )

    lines.extend(
        [
            "",
            "## S1 Attribution",
            "",
            "| Surface | Residual classes | Bridge-flagged values |",
            "| --- | --- | --- |",
        ]
    )
    for key in (
        "s1_gpt_validation",
        "s1_gpt_test",
        "s1_qwen_validation",
        "s1_qwen_test",
    ):
        residual = report["s1_residual_attribution"][key]
        lines.append(
            f"| {report['run_summaries'][key]['label']} | "
            f"{_category_counts(residual['residual_class_counts'])} | "
            f"{_category_counts(residual['bridge_flag_counts'])} |"
        )

    e2 = report["s1_raw_bridge_prompt_context"]
    lines.extend(
        [
            "",
            (
                "The E2 split remains the causal context: full-validation S1 "
                f"bridge contribution was {_field_delta_cell(e2['stage_deltas']['bridge_full_validation'])}, "
                "so raw S1 extraction is not itself at ceiling. On holdout, GPT "
                "S1 residual rows expand from 11 validation diagnosis/seizure "
                "mismatches to 38 holdout mismatches, with extraction and bridge "
                "classes both reaching 10 rows."
            ),
            "",
            "## Frequency Attribution",
            "",
            "| Split | Broad payload recall | Oracle F1 | S5 GPT F1 | S5 error docs | S5 categories |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for split in ("validation", "test"):
        frequency = report["frequency_attribution"][split]
        surfaces = frequency["surface_summaries"]
        lines.append(
            f"| {split} | "
            f"{_pct(surfaces['broad_event_rate_payload']['recall'])} | "
            f"{_pct(surfaces['candidate_constrained_oracle']['f1'])} | "
            f"{_pct(surfaces['s5_gpt_frequency_surface']['f1'])} | "
            f"{frequency['s5_frequency_error_docs']} | "
            f"{_category_counts(frequency['s5_frequency_category_counts'])} |"
        )

    freq_interp = report["frequency_attribution"]["interpretation"]
    lines.extend(
        [
            "",
            (
                "The holdout frequency surface is not just a model-selection "
                f"failure. Broad-payload recall drops {_pp(freq_interp['broad_payload_recall_delta'])}, "
                f"and the gold-constrained oracle over that payload drops "
                f"{_pp(freq_interp['candidate_constrained_oracle_f1_delta'])}. "
                f"The remaining GPT S5 gap to the holdout oracle is "
                f"{_pp(freq_interp['test_s5_gap_to_payload_oracle'])}, which keeps "
                "candidate adjudication open after payload repair is studied on validation."
            ),
            "",
            "## Medication And Stack",
            "",
            "| Surface | Precision | Recall | F1 | TP | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    medication = report["medication_attribution"]["surface_summaries"]
    for key in (
        "isolated_current_rx_payload",
        "s1_gpt_surface",
        "s5_gpt_surface",
    ):
        surface = medication[key]
        lines.append(
            f"| {key} | {_pct(surface['precision'])} | {_pct(surface['recall'])} | "
            f"{_pct(surface['f1'])} | {surface['tp']} | {surface['fp']} | {surface['fn']} |"
        )

    lines.extend(
        [
            "",
            (
                "Shared-family stack deltas on GPT holdout are diagnosis "
                f"{_pp(report['stack_interference']['gpt_test_s5_minus_s1']['diagnosis'])}, "
                f"seizure type {_pp(report['stack_interference']['gpt_test_s5_minus_s1']['seizure_type'])}, "
                "and annotated medication "
                f"{_pp(report['stack_interference']['gpt_test_s5_minus_s1']['annotated_medication'])}. "
                "That routes the next medication mechanism toward payload routing "
                "or prompt isolation, not a broad temporality scorer change."
            ),
            "",
            "## Decision",
            "",
        ]
    )
    for value in report["decision"].values():
        lines.append(f"- {value}")

    lines.extend(
        [
            "",
            "## Reproducibility",
            "",
            f"- S1 GPT validation: `{S1_GPT_VALIDATION_RUN}`",
            f"- S1 GPT holdout: `{S1_GPT_TEST_RUN}`",
            f"- S5 GPT validation: `{S5_GPT_VALIDATION_RUN}`",
            f"- S5 GPT holdout: `{S5_GPT_TEST_RUN}`",
            f"- S1 split source: `{report['s1_raw_bridge_prompt_context']['source_artifact']}`",
            "- No model calls, scorer changes, loader changes, split changes, benchmark bridge changes, prompt changes, prediction repair, or artifact mutation were made.",
            "",
            "## Caveats",
            "",
        ]
    )
    for caveat in report["caveats"]:
        lines.append(f"- {caveat}")
    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, report: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_markdown(path: Path, report: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


def _ordered_field_map(
    values: Mapping[str, Any],
    *,
    field_order: tuple[str, ...],
) -> dict[str, Any]:
    return {field: values[field] for field in field_order if field in values}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def _pp(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:+.1f} pp"


def _field_delta_cell(deltas: Mapping[str, float]) -> str:
    return "; ".join(f"`{field}` {_pp(value)}" for field, value in deltas.items())


def _category_counts(counts: Mapping[str, int]) -> str:
    if not counts:
        return "none"
    return "; ".join(f"`{key}` {value}" for key, value in counts.items())


if __name__ == "__main__":
    main()
