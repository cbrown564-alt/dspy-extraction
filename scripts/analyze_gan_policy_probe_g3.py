#!/usr/bin/env python3
"""G3: Gan Unknown Versus No-Reference Policy Probe.

Evaluates post-adjudication rules applied to Gan G2 predictions.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.cli import _gan_frequency_value, _prediction_label
from clinical_extraction.gan.scoring import (
    GAN_CANONICAL_SCORER,
    GAN_PAPER_REPRODUCTION_SCORER,
    score_gan_frequency_prediction,
)
from clinical_extraction.schemas import DocumentPrediction, PredictionSet


def apply_g3_policy_rules(
    prediction: DocumentPrediction,
    *,
    enable_rule_unknown_vs_noref: bool = True,
    enable_rule_weak_rate_to_unknown: bool = True,
    enable_rule_seizure_free_conflict: bool = True,
) -> str:
    """Applies G3 post-adjudication rules to adjust the predicted label."""
    val = _gan_frequency_value(prediction)
    if val is None:
        return "unknown"
    draft_label = _prediction_label(val) or "unknown"

    metadata = prediction.metadata or {}
    options = metadata.get("multiple_answer_options") or []
    rejected_options = metadata.get("rejected_multiple_answer_options") or []
    temporal_labels = metadata.get("temporal_candidate_labels") or []
    selected_opt = metadata.get("selected_answer_option") or {}

    # Rule 1: Unknown vs No-Reference
    if enable_rule_unknown_vs_noref:
        if draft_label == "unknown":
            # If there are no temporal candidates and all options are either empty or no-ref
            has_active_seizure_option = False
            for opt in options:
                lbl = opt.get("canonical_label")
                if lbl and lbl not in ("no seizure frequency reference", "unknown"):
                    has_active_seizure_option = True
                    break
            if not temporal_labels and not has_active_seizure_option:
                return "no seizure frequency reference"

        elif draft_label == "no seizure frequency reference":
            # If we claimed no-ref, but there's a strong temporal candidate or active seizure option
            has_seizure_evidence = False
            for opt in options:
                lbl = opt.get("canonical_label")
                if lbl and lbl not in ("no seizure frequency reference", "unknown"):
                    has_seizure_evidence = True
                    break
            if temporal_labels or has_seizure_evidence:
                return "unknown"

    # Rule 2: Weak/Ambiguous Rate to Unknown
    if enable_rule_weak_rate_to_unknown:
        # If predicted label is a rate (not unknown/no-ref)
        if draft_label not in ("unknown", "no seizure frequency reference") and not draft_label.startswith("seizure free"):
            # Check selected option ambiguity flags
            ambiguity_flags = selected_opt.get("ambiguity_flags") or []
            weak_flags = {
                "uncertain_frequency", "uncertain_denominator", "insufficient_data",
                "possible non-epileptic events", "possible underreporting",
                "trigger-conditioned", "conditional_frequency", "uncertain_seizure_type",
                "uncertain denominator"
            }
            has_weak_flag = any(flag in weak_flags for flag in ambiguity_flags)
            
            # Or if all available options have ambiguity flags
            all_options_ambiguous = len(options) > 0 and all(
                any(f in weak_flags for f in opt.get("ambiguity_flags", []))
                for opt in options
                if opt.get("canonical_label") not in ("no seizure frequency reference", "unknown")
            )

            if has_weak_flag or all_options_ambiguous:
                return "unknown"

    # Rule 3: Seizure-Free Conflict Resolution
    if enable_rule_seizure_free_conflict:
        # If we predicted a rate but there's a seizure-free option marked "current" or "present"
        # and no other recent breakthrough events
        if draft_label not in ("unknown", "no seizure frequency reference") and not draft_label.startswith("seizure free"):
            seizure_free_opts = [
                opt for opt in options
                if opt.get("canonical_label", "").startswith("seizure free")
            ]
            if seizure_free_opts:
                # If the selected option is a breakthrough candidate but the breakthrough was historical
                # (e.g. "seizure free for 5 months, until a seizure 3 Thursdays ago" -> wait, 3 Thursdays ago is current!)
                # Let's check if the seizure free period is the primary current status
                current_sf = [opt for opt in seizure_free_opts if opt.get("status") in ("current", "present")]
                if current_sf:
                    # Let's adjust to the seizure-free label if the rate is historical
                    # For Gan, a recent breakthrough (e.g. "3 Tuesdays ago") takes priority under target selection,
                    # but if the breakthrough is very old or unsupported, choose the seizure-free label.
                    # We can use metadata features to decide.
                    pass

    return draft_label


def run_policy_probe(
    run_dir: Path,
    *,
    enable_rule_unknown_vs_noref: bool = True,
    enable_rule_weak_rate_to_unknown: bool = True,
    enable_rule_seizure_free_conflict: bool = True,
) -> dict[str, Any]:
    prediction_set = PredictionSet.model_validate_json(
        (run_dir / "predictions.json").read_text(encoding="utf-8")
    )
    gold_by_id = {record.record_id: record for record in load_gan_records()}

    original_results = []
    probed_results = []

    for pred in prediction_set.predictions:
        record_id = pred.document_id
        if record_id not in gold_by_id:
            continue
        gold = gold_by_id[record_id]

        val = _gan_frequency_value(pred)
        if val is None:
            continue
        orig_label = _prediction_label(val) or "unknown"
        probed_label = apply_g3_policy_rules(
            pred,
            enable_rule_unknown_vs_noref=enable_rule_unknown_vs_noref,
            enable_rule_weak_rate_to_unknown=enable_rule_weak_rate_to_unknown,
            enable_rule_seizure_free_conflict=enable_rule_seizure_free_conflict,
        )

        original_results.append((gold, orig_label))
        probed_results.append((gold, probed_label))

    def evaluate_set(results: list[tuple[Any, str]]) -> dict[str, Any]:
        metrics = defaultdict(list)
        for gold, pred_label in results:
            for scorer_name in (GAN_CANONICAL_SCORER, GAN_PAPER_REPRODUCTION_SCORER):
                score = score_gan_frequency_prediction(
                    gold_label=gold.gold_label,
                    predicted_label=pred_label,
                    scorer_mode=scorer_name,
                )
                metrics[f"{scorer_name}_monthly"].append(int(score.monthly_frequency_match))
                metrics[f"{scorer_name}_purist"].append(int(score.purist_category_match))
                metrics[f"{scorer_name}_pragmatic"].append(int(score.pragmatic_category_match))
                metrics[f"{scorer_name}_exact"].append(int(score.exact_normalized_match))
        
        return {
            key: sum(val) / len(val) if val else 0.0
            for key, val in metrics.items()
        }

    orig_metrics = evaluate_set(original_results)
    probed_metrics = evaluate_set(probed_results)

    # Compute stratified confusion report
    confusion = defaultdict(lambda: defaultdict(int))
    for (gold, _), (_, probed_lbl) in zip(original_results, probed_results):
        confusion[gold.gold_label][probed_lbl] += 1

    return {
        "run_dir": str(run_dir),
        "total_records": len(original_results),
        "rules_config": {
            "enable_rule_unknown_vs_noref": enable_rule_unknown_vs_noref,
            "enable_rule_weak_rate_to_unknown": enable_rule_weak_rate_to_unknown,
            "enable_rule_seizure_free_conflict": enable_rule_seizure_free_conflict,
        },
        "original_metrics": orig_metrics,
        "probed_metrics": probed_metrics,
        "confusion_matrix": {
            gold_lbl: dict(preds)
            for gold_lbl, preds in confusion.items()
        },
        "details": [
            {
                "record_id": pred.document_id,
                "gold": gold_by_id[pred.document_id].gold_label,
                "original": orig_lbl,
                "probed": probed_lbl,
                "changed": orig_lbl != probed_lbl,
            }
            for (gold, orig_lbl), (_, probed_lbl), pred in zip(original_results, probed_results, prediction_set.predictions)
        ]
    }


def write_probe_report(
    report: dict[str, Any],
    *,
    json_output: Path,
    markdown_output: Path,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)

    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# G3 - Gan Unknown Versus No-Reference Policy Probe Report",
        "",
        f"Input Run Directory: `{report['run_dir']}`",
        f"Total Records Evaluated: {report['total_records']}",
        "",
        "## Policy Configuration",
        f"- Unknown vs No-Reference Boundary Rule: **{'Enabled' if report['rules_config']['enable_rule_unknown_vs_noref'] else 'Disabled'}**",
        f"- Weak Rate to Unknown Rule: **{'Enabled' if report['rules_config']['enable_rule_weak_rate_to_unknown'] else 'Disabled'}**",
        f"- Seizure-Free Conflict Resolution Rule: **{'Enabled' if report['rules_config']['enable_rule_seizure_free_conflict'] else 'Disabled'}**",
        "",
        "## Metrics Comparison",
        "",
        "| Scorer / Metric | Original | Probed | Delta |",
        "| --- | ---: | ---: | ---: |",
    ]

    for key in sorted(report["original_metrics"].keys()):
        orig = report["original_metrics"][key]
        probed = report["probed_metrics"][key]
        delta = probed - orig
        lines.append(f"| {key} | {orig:.1%} | {probed:.1%} | {delta * 100:+.1f}pp |")

    lines.extend([
        "",
        "## Changed Predictions Details",
        "",
        "| Record ID | Gold Label | Original Prediction | Probed Prediction |",
        "| --- | --- | --- | --- |",
    ])

    for detail in report["details"]:
        if detail["changed"]:
            lines.append(
                f"| `{detail['record_id']}` | `{detail['gold']}` | `{detail['original']}` | `{detail['probed']}` |"
            )

    lines.append("")
    markdown_output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="G3 Policy Probe Evaluator.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/experiments/gan/gan_s0_g3_policy_probe_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/experiments/gan/gan_s0_g3_policy_probe_report.md"),
    )
    parser.add_argument("--disable-rule-unknown-vs-noref", action="store_true")
    parser.add_argument("--disable-rule-weak-rate-to-unknown", action="store_true")
    parser.add_argument("--disable-rule-seizure-free-conflict", action="store_true")

    args = parser.parse_args()

    report = run_policy_probe(
        args.run_dir,
        enable_rule_unknown_vs_noref=not args.disable_rule_unknown_vs_noref,
        enable_rule_weak_rate_to_unknown=not args.disable_rule_weak_rate_to_unknown,
        enable_rule_seizure_free_conflict=not args.disable_rule_seizure_free_conflict,
    )

    write_probe_report(
        report,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
    )
    print(f"Wrote report JSON to {args.json_output}")
    print(f"Wrote report Markdown to {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
