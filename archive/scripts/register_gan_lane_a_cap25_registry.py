"""Register Gan S0 Lane A cap-25 runs in docs/experiments/synthesis/experiment_registry.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / "docs" / "experiments" / "synthesis" / "experiment_registry.json"

RUNS = [
    ("gan_s0_verification_direct_cap25_gpt4_1_mini", "gan_s0_verification_direct_cap25_gpt4_1_mini_20260520T233555Z", "hold"),
    ("gan_s0_verification_verify_repair_cap25_gpt4_1_mini", "gan_s0_verification_verify_repair_cap25_gpt4_1_mini_20260520T233559Z", "hold"),
    ("gan_s0_verification_temporal_verify_repair_cap25_gpt4_1_mini", "gan_s0_verification_temporal_verify_repair_cap25_gpt4_1_mini_20260520T233701Z", "hold"),
    ("gan_s0_evidence_model_quote_cap25_gpt4_1_mini", "gan_s0_evidence_model_quote_cap25_gpt4_1_mini_20260520T233707Z", "hold"),
    ("gan_s0_evidence_optional_cap25_gpt4_1_mini", "gan_s0_evidence_optional_cap25_gpt4_1_mini_20260520T233713Z", "reject"),
    ("gan_s0_evidence_span_check_cap25_gpt4_1_mini", "gan_s0_evidence_span_check_cap25_gpt4_1_mini_20260520T233837Z", "reject"),
    ("gan_s0_prompt_policy_temporal_v1_1_cap25_gpt4_1_mini", "gan_s0_prompt_policy_temporal_v1_1_cap25_gpt4_1_mini_20260520T233934Z", "hold"),
    ("gan_s0_prompt_policy_synthesis_port_cap25_gpt4_1_mini", "gan_s0_prompt_policy_synthesis_port_cap25_gpt4_1_mini_20260520T233941Z", "reject"),
    ("gan_s0_prompt_policy_guardrails_port_cap25_gpt4_1_mini", "gan_s0_prompt_policy_guardrails_port_cap25_gpt4_1_mini_20260520T234051Z", "hold"),
]

EVIDENCE_BY_EID = {
    "gan_s0_evidence_optional_cap25_gpt4_1_mini": "absent",
    "gan_s0_evidence_model_quote_cap25_gpt4_1_mini": "model_quote",
    "gan_s0_evidence_span_check_cap25_gpt4_1_mini": "model_quote_with_diagnostic_span_check",
}

VERIFICATION_BY_ARCH = {
    "direct_single_pass": "none",
    "verify_repair": "verify_repair",
    "temporal_candidates_verify_repair": "verify_repair",
}

NOTES = {
    "gan_s0_verification_direct_cap25_gpt4_1_mini": "Hold: verification-group anchor; 44% monthly on cap-25.",
    "gan_s0_verification_verify_repair_cap25_gpt4_1_mini": "Hold: null vs direct on monthly (44%); 8 label diffs.",
    "gan_s0_verification_temporal_verify_repair_cap25_gpt4_1_mini": "Hold: identical labels to direct on cap-25; null factor.",
    "gan_s0_evidence_model_quote_cap25_gpt4_1_mini": "Hold: evidence-group reference; 44% monthly.",
    "gan_s0_evidence_optional_cap25_gpt4_1_mini": "Reject: -4pp monthly vs model-quote; no evidence gain.",
    "gan_s0_evidence_span_check_cap25_gpt4_1_mini": "Reject: 7/25 abstentions; 55.6% monthly on 18 valid only.",
    "gan_s0_prompt_policy_temporal_v1_1_cap25_gpt4_1_mini": "Hold: prompt-policy reference; 44% monthly.",
    "gan_s0_prompt_policy_synthesis_port_cap25_gpt4_1_mini": "Reject: 39.1% monthly; 92% schema.",
    "gan_s0_prompt_policy_guardrails_port_cap25_gpt4_1_mini": "Hold: +4pp monthly vs v1.1 (48%); error-read before full.",
}

TEMPORAL_ROW = {
    "program_architecture": "temporal_candidates_verify_repair",
    "hybrid_balance_class": ["H2_pre_deterministic", "H4_deterministic_first_llm_adjudicates"],
    "interleaving_positions": ["pre", "during", "post"],
    "context_strategy": "candidate_injected",
    "verification_strategy": "verify_repair",
    "evidence_strategy": "model_quote",
}


def base_gan_row() -> dict:
    return {
        "dataset": "gan_2026",
        "schema_complexity": "gan_s0",
        "clinical_task_family": ["frequency"],
        "model_track": "gpt4_1_mini",
        "deterministic_roles": [
            "benchmark_label_policy",
            "evidence_span_guard",
            "json_schema_constraint",
            "pydantic_validation",
        ],
        "llm_roles": [
            "evidence_quote_generation",
            "frequency_interpretation",
            "repair",
            "verification",
        ],
        "knowledge_sources": [
            "benchmark_label_policy",
            "controlled_vocabulary",
            "gold_audit_policy",
            "json_schema",
            "pydantic_validation",
            "temporal_rules",
        ],
        "control_modes": ["hard_constraint", "posthoc_correction", "soft_hint"],
        "normalization_strategy": "list_constrained",
        "schema_integrity_strategy": ["json_schema", "pydantic_validation"],
        "example_strategy": "zero_shot_or_prompt_only",
        "fixed_controls": {
            "schema_level": "gan_frequency_s0",
            "scorer": "gan_frequency_deterministic_v1",
            "model_config_path": "configs/models/gan_s0_gpt4_1_mini.json",
            "split": "gan_2026_fixed_v1:validation",
        },
        "run_scope": "cap25",
        "decision_doc": "docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md",
        "config_paths": None,
    }


def build_row(eid: str, run_id: str, outcome: str) -> dict:
    cfg = json.loads((ROOT / "runs" / run_id / "config.json").read_text(encoding="utf-8"))
    met = json.loads((ROOT / "runs" / run_id / "metrics.json").read_text(encoding="utf-8"))
    tax = cfg["taxonomy"]
    arch = tax["program_architecture"]
    varied = tax["varied_factor"]
    comparison_group = tax["comparison_group"]

    row = base_gan_row()
    row.update(
        {
            "experiment_id": eid,
            "program_architecture": arch,
            "hybrid_balance_class": tax["hybrid_balance_class"],
            "interleaving_positions": tax["interleaving_positions"],
            "context_strategy": cfg["controls"]["context_policy"],
            "comparison_group": comparison_group,
            "varied_factor": varied,
            "canonical_run_id": run_id,
            "outcome": outcome,
            "metric_caveats": cfg["metric_caveats"]
            + [
                "Clean GPT factor-isolation group; compare only within the named comparison_group.",
                "Cap-25 runs are gate-only and systematically optimistic vs full validation.",
                "Gan primary gold is check__Seizure Frequency Number.seizure_frequency_number[0].",
                "Monthly-frequency, Purist category, and Pragmatic category metrics are benchmark-facing.",
                "Evidence metrics are diagnostic source-grounding checks.",
                "This config targets the fixed Gan synthetic validation split and must not be described as published Gan benchmark reproduction.",
            ],
            "artifact_paths": [f"runs/{run_id}"],
            "headline_metric": {
                "name": "monthly_frequency_accuracy",
                "value": met["benchmark_metrics"]["monthly_frequency_accuracy"],
                "secondary": {
                    "purist_category_accuracy": met["benchmark_metrics"]["purist_category_accuracy"],
                    "pragmatic_category_accuracy": met["benchmark_metrics"]["pragmatic_category_accuracy"],
                    "evidence_quote_support_rate": met["diagnostic_metrics"]["evidence_quote_support_rate"],
                    "schema_valid_prediction_rate": met["diagnostic_metrics"]["schema_valid_prediction_rate"],
                },
            },
            "prompt_versions": cfg["prompt_version"],
            "notes": NOTES[eid],
            "comparison_caveat": (
                f"Varied {varied} only; see docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md."
            ),
            "comparison_groups": [comparison_group],
        }
    )

    if varied == "verification_strategy":
        row["verification_strategy"] = VERIFICATION_BY_ARCH[arch]
        row["evidence_strategy"] = "model_quote"
        if arch == "direct_single_pass":
            row["llm_roles"] = ["evidence_quote_generation", "frequency_interpretation"]
    elif varied == "evidence_strategy":
        row.update(TEMPORAL_ROW)
        row["evidence_strategy"] = EVIDENCE_BY_EID[eid]
        row["deterministic_roles"] = row["deterministic_roles"] + ["temporal_candidate_generation"]
    else:
        row.update(TEMPORAL_ROW)

    return row


def main() -> None:
    reg = json.loads(REG_PATH.read_text(encoding="utf-8"))
    existing = {r["experiment_id"] for r in reg["experiments"]}
    added: list[str] = []
    for eid, run_id, outcome in RUNS:
        if eid in existing:
            print(f"skip existing {eid}")
            continue
        reg["experiments"].append(build_row(eid, run_id, outcome))
        added.append(eid)
    reg["row_count"] = len(reg["experiments"])
    reg["generated_on"] = "2026-05-21"
    REG_PATH.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    print(f"Added {len(added)} rows: {', '.join(added)}")
    print(f"row_count={reg['row_count']}")


if __name__ == "__main__":
    main()
