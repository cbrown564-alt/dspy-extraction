"""Append hybrid-grid cap-25 rows to docs/experiment_registry.json.

Reads latest run under runs/ per experiment_id and builds minimal registry rows.
Skips experiment_ids already present.

Usage:
    uv run python scripts/backfill_hybrid_cap25_registry.py
    uv run python scripts/backfill_hybrid_cap25_registry.py --dry-run
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / "docs" / "experiment_registry.json"
RUNS = ROOT / "runs"

GAN_GRID_ROWS: list[dict] = [
    {
        "experiment_id": "gan_s0_stage_graph_g1_direct_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g1_direct",
        "program_architecture": "direct_single_pass",
        "hybrid_balance_class": ["L1_llm_constrained"],
        "interleaving_positions": ["during"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 cap-25 A1; 44% monthly; reject vs A3 winner.",
    },
    {
        "experiment_id": "gan_s0_stage_graph_g2_extract_repair_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g2_extract_repair",
        "program_architecture": "verify_repair",
        "hybrid_balance_class": ["H1_post_deterministic"],
        "interleaving_positions": ["during", "post"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 cap-25 A2; 44% monthly; reject vs A3.",
    },
    {
        "experiment_id": "gan_s0_stage_graph_g2_candidates_adjudicate_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g2_candidates_adjudicate",
        "program_architecture": "temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 cap-25 A3 winner; 52% monthly; anchor for Axis 2/3.",
    },
    {
        "experiment_id": "gan_s0_stage_graph_g3_extract_verify_repair_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g3_extract_verify_repair",
        "program_architecture": "verify_repair",
        "hybrid_balance_class": ["H1_post_deterministic"],
        "interleaving_positions": ["during", "post"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 cap-25 A4; 44% monthly; label-duplicate of A2.",
    },
    {
        "experiment_id": "gan_s0_stage_graph_g3_candidates_extract_repair_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g3_candidates_extract_repair",
        "program_architecture": "temporal_candidates_verify_repair",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during", "post"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 cap-25 A5; 44% monthly; promoted skeleton did not win Axis 1 search.",
    },
    {
        "experiment_id": "gan_s0_stage_executor_e1_det_candidates_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "program_architecture": "temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E1; 52% monthly; det-candidate anchor confirmed.",
    },
    {
        "experiment_id": "gan_s0_stage_executor_e2_llm_candidates_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "llm_candidates_llm_adjudicate",
        "program_architecture": "llm_temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E2; 29.2% monthly; LLM JSON candidate path reject.",
    },
    {
        "experiment_id": "gan_s0_stage_executor_e3_hybrid_candidates_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "hybrid_candidates_llm_adjudicate",
        "program_architecture": "hybrid_temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E3; 41.7% monthly; hybrid merge reject vs det.",
    },
    {
        "experiment_id": "gan_s0_stage_executor_e4_det_vr_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate_llm_vr",
        "program_architecture": "temporal_candidates_adjudicate_verify_repair",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during", "post"],
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E4 diagnostic; 52% monthly; VR neutral after adjudicate.",
    },
    {
        "experiment_id": "gan_s0_stage_executor_e5_llm_vr_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "llm_candidates_llm_adjudicate_llm_vr",
        "program_architecture": "llm_temporal_candidates_verify_repair",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during", "post"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E5 diagnostic; 29.2% monthly; VR cannot rescue LLM candidates.",
    },
]

GAN_IMPL_ROWS: list[dict] = [
    {
        "experiment_id": "gan_s0_impl_i0_cand_prose_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_implementation_variant_gpt_cap25_v1",
        "varied_factor": "implementation_variant",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "implementation_variant": "cand_prose_v1",
        "program_architecture": "temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "verification_strategy": "none",
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 3 I0; 52% monthly; prose control reject vs 56% non-prose.",
    },
    {
        "experiment_id": "gan_s0_impl_i1_cand_table_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_implementation_variant_gpt_cap25_v1",
        "varied_factor": "implementation_variant",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "implementation_variant": "cand_table_v1",
        "program_architecture": "temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "verification_strategy": "none",
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 3 I1; 56% monthly; table presentation hold (tied).",
    },
    {
        "experiment_id": "gan_s0_impl_i2_cand_json_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_implementation_variant_gpt_cap25_v1",
        "varied_factor": "implementation_variant",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "implementation_variant": "cand_json_v1",
        "program_architecture": "temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "verification_strategy": "none",
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 3 I2; 56% monthly; JSON presentation hold (tied).",
    },
    {
        "experiment_id": "gan_s0_impl_i3_cand_bullets_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_implementation_variant_gpt_cap25_v1",
        "varied_factor": "implementation_variant",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "implementation_variant": "cand_bullets_v1",
        "program_architecture": "temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "verification_strategy": "none",
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 3 I3; 56% monthly; bullets presentation hold (tied).",
    },
]

GAN_LADDER_ROWS: list[dict] = [
    {
        "experiment_id": "gan_s0_validation_ladder_v0_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_validation_ladder_gpt_cap25_v1",
        "varied_factor": "validation_ladder_rung",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "validation_ladder_rung": "adjudicate_only",
        "program_architecture": "temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "verification_strategy": "none",
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. V0 adjudicate-only; 52% monthly baseline.",
    },
    {
        "experiment_id": "gan_s0_validation_ladder_v2_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_validation_ladder_gpt_cap25_v1",
        "varied_factor": "validation_ladder_rung",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "validation_ladder_rung": "det_plausibility",
        "program_architecture": "temporal_candidates_adjudicate_det_guards",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "post"],
        "verification_strategy": "deterministic_guards_only",
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. V2 det plausibility; 52% monthly null vs V0.",
    },
    {
        "experiment_id": "gan_s0_validation_ladder_v3_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_validation_ladder_gpt_cap25_v1",
        "varied_factor": "validation_ladder_rung",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "validation_ladder_rung": "det_evidence_grounding",
        "program_architecture": "temporal_candidates_adjudicate_det_evidence",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "post"],
        "verification_strategy": "deterministic_evidence_span_check",
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. V3 det evidence; 58.3% on 12 valid; 13 abstentions fail gates.",
    },
    {
        "experiment_id": "gan_s0_validation_ladder_v4_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_validation_ladder_gpt_cap25_v1",
        "varied_factor": "validation_ladder_rung",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "validation_ladder_rung": "llm_confirm_only",
        "program_architecture": "temporal_candidates_adjudicate_confirm_only",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during", "post"],
        "verification_strategy": "llm_confirm_only",
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md",
        "notes": (
            "decision_scope: arm. V4 confirm-only rerun after verifier-prompt wiring fix; "
            "null vs V3 because 13 records abstain in deterministic evidence grounding "
            "before the confirm-only verifier."
        ),
    },
    {
        "experiment_id": "gan_s0_validation_ladder_v5_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_validation_ladder_gpt_cap25_v1",
        "varied_factor": "validation_ladder_rung",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "validation_ladder_rung": "llm_verify_repair",
        "program_architecture": "temporal_candidates_adjudicate_verify_repair_no_guards",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during", "post"],
        "verification_strategy": "llm_verify_repair",
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. V5 LLM VR no guards; null vs V3; valid-count fail.",
    },
    {
        "experiment_id": "gan_s0_validation_ladder_v6_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_validation_ladder_gpt_cap25_v1",
        "varied_factor": "validation_ladder_rung",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "validation_ladder_rung": "llm_verify_repair_det_guards",
        "program_architecture": "temporal_candidates_adjudicate_verify_repair",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during", "post"],
        "verification_strategy": "llm_verify_repair",
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. V6 LLM VR + det guards; 52% monthly; neutral vs V0.",
    },
    {
        "experiment_id": "gan_s0_validation_ladder_v7_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_validation_ladder_gpt_cap25_v1",
        "varied_factor": "validation_ladder_rung",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "validation_ladder_rung": "llm_vr_det_guards_span_check",
        "program_architecture": "temporal_candidates_adjudicate_verify_repair_span_check",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during", "post"],
        "verification_strategy": "llm_verify_repair",
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_validation_ladder_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. V7 span-check after VR; 50% on 16 valid; 9 abstentions.",
    },
]

EXECT_GRID_ROWS: list[dict] = [
    {
        "experiment_id": "exect_s1_stage_graph_g1_l1_policy_bridges_cap25_gpt4_1_mini",
        "comparison_group": "exect_s1_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g1_l1_policy_bridges",
        "program_architecture": "single_pass",
        "hybrid_balance_class": ["L1_llm_constrained"],
        "interleaving_positions": ["during"],
        "clinical_task_family": ["diagnosis", "seizure_type", "medication"],
        "context_strategy": "full_note",
        "verification_strategy": "none",
        "normalization_strategy": "benchmark_policy_prompt",
        "prompt_versions": "exect_s0_s1_field_family_v4_10_label_policy",
        "outcome": "hold",
        "decision_doc": "docs/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 S1; 95.8% micro; production-shaped hold.",
    },
    {
        "experiment_id": "exect_s1_stage_graph_g1_l1_policy_no_bridges_cap25_gpt4_1_mini",
        "comparison_group": "exect_s1_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g1_l1_policy_no_bridges",
        "program_architecture": "single_pass",
        "hybrid_balance_class": ["L1_llm_constrained"],
        "interleaving_positions": ["during"],
        "clinical_task_family": ["diagnosis", "seizure_type", "medication"],
        "context_strategy": "full_note",
        "verification_strategy": "none",
        "normalization_strategy": "benchmark_policy_prompt",
        "prompt_versions": "exect_s0_s1_field_family_v4_10_label_policy",
        "outcome": "hold",
        "decision_doc": "docs/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 S2 diagnostic; 72.8% micro; bridge-free reference.",
    },
    {
        "experiment_id": "exect_s1_stage_graph_g2_extract_verify_cap25_gpt4_1_mini",
        "comparison_group": "exect_s1_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g2_extract_verify",
        "program_architecture": "verify_repair",
        "hybrid_balance_class": ["L1_llm_constrained"],
        "interleaving_positions": ["during"],
        "clinical_task_family": ["diagnosis", "seizure_type", "medication"],
        "context_strategy": "full_note",
        "verification_strategy": "verify_repair",
        "normalization_strategy": "benchmark_policy_prompt",
        "prompt_versions": "exect_s0_s1_field_family_verify_repair_v1",
        "outcome": "reject",
        "decision_doc": "docs/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 S3; 72.8% micro; verify-repair bridges-off reject.",
    },
    {
        "experiment_id": "exect_s1_stage_graph_g2_raw_post_bridge_cap25_gpt4_1_mini",
        "comparison_group": "exect_s1_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g2_raw_post_bridge",
        "program_architecture": "single_pass",
        "hybrid_balance_class": ["H1_post_deterministic"],
        "interleaving_positions": ["during", "post"],
        "clinical_task_family": ["diagnosis", "seizure_type", "medication"],
        "context_strategy": "full_note",
        "verification_strategy": "none",
        "normalization_strategy": "benchmark_policy_prompt",
        "prompt_versions": "exect_s0_s1_field_family_v4_10_label_policy",
        "outcome": "hold",
        "decision_doc": "docs/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 S4; 95.8% micro; ties S1 post-bridge hold.",
    },
    {
        "experiment_id": "exect_s1_stage_graph_g3_family_split_merge_cap25_gpt4_1_mini",
        "comparison_group": "exect_s1_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g3_family_split_merge",
        "program_architecture": "section_aware",
        "hybrid_balance_class": ["L1_llm_constrained"],
        "interleaving_positions": ["during"],
        "clinical_task_family": ["diagnosis", "seizure_type", "medication"],
        "context_strategy": "section_filtered",
        "verification_strategy": "none",
        "normalization_strategy": "benchmark_policy_prompt",
        "prompt_versions": "exect_s0_s1_field_family_v4_10_label_policy",
        "outcome": "reject",
        "decision_doc": "docs/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 S5; 83.3% micro; family-split reject.",
    },
    {
        "experiment_id": "exect_s1_stage_executor_e1_inline_bridges_cap25_gpt4_1_mini",
        "comparison_group": "exect_s1_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g1_l1_policy_bridges",
        "stage_executor": "llm_extract_inline_bridges",
        "program_architecture": "single_pass",
        "hybrid_balance_class": ["L1_llm_constrained"],
        "interleaving_positions": ["during"],
        "clinical_task_family": ["diagnosis", "seizure_type", "medication"],
        "context_strategy": "full_note",
        "verification_strategy": "none",
        "normalization_strategy": "benchmark_policy_prompt",
        "prompt_versions": "exect_s0_s1_field_family_v4_10_label_policy",
        "outcome": "hold",
        "decision_doc": "docs/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E1; 95.8% micro; inline-bridge anchor.",
    },
    {
        "experiment_id": "exect_s1_stage_executor_e2_post_bridges_cap25_gpt4_1_mini",
        "comparison_group": "exect_s1_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g1_l1_policy_bridges",
        "stage_executor": "llm_extract_post_bridges",
        "program_architecture": "single_pass",
        "hybrid_balance_class": ["H1_post_deterministic"],
        "interleaving_positions": ["during", "post"],
        "clinical_task_family": ["diagnosis", "seizure_type", "medication"],
        "context_strategy": "full_note",
        "verification_strategy": "none",
        "normalization_strategy": "benchmark_policy_prompt",
        "prompt_versions": "exect_s0_s1_field_family_v4_10_label_policy",
        "outcome": "hold",
        "decision_doc": "docs/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E2; 95.8% micro; post-bridge null vs E1.",
    },
    {
        "experiment_id": "exect_s1_stage_executor_e3_all_family_hints_cap25_gpt4_1_mini",
        "comparison_group": "exect_s1_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g1_l1_policy_bridges",
        "stage_executor": "det_all_family_hints_llm_extract",
        "program_architecture": "single_pass",
        "hybrid_balance_class": ["H2_pre_deterministic"],
        "interleaving_positions": ["pre", "during"],
        "clinical_task_family": ["diagnosis", "seizure_type", "medication"],
        "context_strategy": "candidate_injected",
        "verification_strategy": "none",
        "normalization_strategy": "list_constrained",
        "prompt_versions": "exect_s0_s1_field_family_v4_10_label_policy",
        "outcome": "reject",
        "decision_doc": "docs/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E3; 90.9% micro; all-family hints reject.",
    },
    {
        "experiment_id": "exect_s1_stage_executor_e4_seizure_hints_cap25_gpt4_1_mini",
        "comparison_group": "exect_s1_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g1_l1_policy_bridges",
        "stage_executor": "det_seizure_hints_llm_extract",
        "program_architecture": "single_pass",
        "hybrid_balance_class": ["H2_pre_deterministic"],
        "interleaving_positions": ["pre", "during"],
        "clinical_task_family": ["seizure_type"],
        "context_strategy": "candidate_injected",
        "verification_strategy": "none",
        "normalization_strategy": "list_constrained",
        "prompt_versions": "exect_s0_s1_field_family_v4_10_label_policy",
        "outcome": "reject",
        "decision_doc": "docs/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E4; 92.8% micro; seizure-only hints reject.",
    },
    {
        "experiment_id": "exect_s1_stage_executor_e5_medication_hints_cap25_gpt4_1_mini",
        "comparison_group": "exect_s1_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g1_l1_policy_bridges",
        "stage_executor": "det_medication_hints_llm_extract",
        "program_architecture": "single_pass",
        "hybrid_balance_class": ["H2_pre_deterministic"],
        "interleaving_positions": ["pre", "during"],
        "clinical_task_family": ["medication"],
        "context_strategy": "candidate_injected",
        "verification_strategy": "none",
        "normalization_strategy": "list_constrained",
        "prompt_versions": "exect_s0_s1_field_family_v4_10_label_policy",
        "outcome": "reject",
        "decision_doc": "docs/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E5; 93.3% micro; medication-only hints reject.",
    },
]

ALL_GRID_ROWS = GAN_GRID_ROWS + GAN_IMPL_ROWS + GAN_LADDER_ROWS + EXECT_GRID_ROWS


def _latest_run_dir(experiment_id: str) -> Path | None:
    matches = sorted(RUNS.glob(f"{experiment_id}_*"), reverse=True)
    return matches[0] if matches else None


def _gan_headline_from_metrics(metrics_path: Path) -> dict | None:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    bench = metrics.get("benchmark_metrics") or {}
    monthly = bench.get("monthly_frequency_accuracy")
    if monthly is None:
        return None
    diag = metrics.get("diagnostic_metrics") or {}
    return {
        "name": "monthly_frequency_accuracy",
        "value": monthly,
        "secondary": {
            "purist_category_accuracy": bench.get("purist_category_accuracy"),
            "pragmatic_category_accuracy": bench.get("pragmatic_category_accuracy"),
            "evidence_quote_support_rate": diag.get("evidence_quote_support_rate"),
            "schema_valid_prediction_rate": diag.get("schema_valid_prediction_rate"),
        },
    }


def _exect_headline_from_metrics(metrics_path: Path) -> dict | None:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    bench = metrics.get("benchmark_metrics") or {}
    micro_f1 = bench.get("micro_f1")
    if micro_f1 is None:
        return None
    diag = metrics.get("diagnostic_metrics") or {}
    field_f1 = bench.get("field_f1") or {}
    return {
        "name": "micro_f1",
        "value": micro_f1,
        "secondary": {
            "diagnosis_f1": field_f1.get("diagnosis"),
            "seizure_type_f1": field_f1.get("seizure_type"),
            "annotated_medication_f1": field_f1.get("annotated_medication"),
            "evidence_quote_support_rate": diag.get("evidence_quote_support_rate"),
        },
    }


def _build_gan_row(spec: dict) -> dict | None:
    run_dir = _latest_run_dir(spec["experiment_id"])
    if run_dir is None:
        return None
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        return None
    headline = _gan_headline_from_metrics(metrics_path)
    config_path = ROOT / "configs" / "experiments" / f"{spec['experiment_id']}.json"
    return {
        "experiment_id": spec["experiment_id"],
        "dataset": "gan_2026",
        "schema_complexity": "gan_s0",
        "clinical_task_family": ["frequency"],
        "model_track": "gpt4_1_mini",
        "program_architecture": spec["program_architecture"],
        "hybrid_balance_class": spec["hybrid_balance_class"],
        "deterministic_roles": [
            "benchmark_label_policy",
            "frequency_normalization",
            "json_schema_constraint",
            "pydantic_validation",
            "temporal_candidate_generation",
        ],
        "llm_roles": [
            "evidence_quote_generation",
            "frequency_interpretation",
        ],
        "interleaving_positions": spec["interleaving_positions"],
        "knowledge_sources": [
            "benchmark_label_policy",
            "json_schema",
            "pydantic_validation",
            "temporal_rules",
        ],
        "control_modes": ["hard_constraint", "soft_hint"],
        "context_strategy": "full_note_plus_deterministic_temporal_candidates",
        "evidence_strategy": "model_quote_required",
        "normalization_strategy": "benchmark_policy_prompt",
        "verification_strategy": spec.get(
            "verification_strategy",
            "none"
            if spec["program_architecture"] == "temporal_candidates_single_pass"
            else "llm_verify_repair",
        ),
        "schema_integrity_strategy": ["json_schema", "pydantic_validation"],
        "example_strategy": "zero_shot_or_prompt_only",
        "comparison_group": spec["comparison_group"],
        "fixed_controls": {
            "schema_level": "gan_frequency_s0",
            "scorer": "gan_frequency_deterministic_v1",
            "model_config_path": "configs/models/gan_s0_gpt4_1_mini.json",
            "split": "gan_2026_fixed_v1:validation",
        },
        "varied_factor": spec["varied_factor"],
        "run_scope": "slice",
        "canonical_run_id": run_dir.name,
        "outcome": spec["outcome"],
        "decision_doc": spec["decision_doc"],
        "metric_caveats": [
            "Cap-25 search grid under hybrid pipeline pivot; not mechanism closure.",
            f"stage_graph_id={spec.get('stage_graph_id')}; "
            f"stage_executor={spec.get('stage_executor', 'n/a')}; "
            f"implementation_variant={spec.get('implementation_variant', 'n/a')}; "
            f"validation_ladder_rung={spec.get('validation_ladder_rung', 'n/a')}.",
        ],
        "artifact_paths": [f"runs/{run_dir.name}"],
        "headline_metric": headline,
        "prompt_versions": (
            json.loads(config_path.read_text(encoding="utf-8")).get("prompt_version")
            if config_path.exists()
            else "gan_frequency_s0_temporal_candidates_single_pass_v1_1"
        ),
        "config_paths": str(config_path.relative_to(ROOT)).replace("\\", "/"),
        "notes": spec["notes"],
        "comparison_groups": [spec["comparison_group"]],
    }


def _build_exect_row(spec: dict) -> dict | None:
    run_dir = _latest_run_dir(spec["experiment_id"])
    if run_dir is None:
        return None
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        return None
    headline = _exect_headline_from_metrics(metrics_path)
    config_path = ROOT / "configs" / "experiments" / f"{spec['experiment_id']}.json"
    llm_roles = [
        "benchmark_policy_application",
        "clinical_field_extraction",
        "evidence_quote_generation",
    ]
    if spec["verification_strategy"] == "verify_repair":
        llm_roles.extend(["repair", "verification"])
    deterministic_roles = [
        "benchmark_label_policy",
        "field_family_scoring",
        "json_schema_constraint",
        "pydantic_validation",
    ]
    if spec["hybrid_balance_class"] == ["H2_pre_deterministic"]:
        deterministic_roles.append("controlled_vocabulary_filter")
    if spec["hybrid_balance_class"] == ["H1_post_deterministic"]:
        deterministic_roles.append("benchmark_bridge")
    knowledge_sources = [
        "benchmark_label_policy",
        "gold_audit_policy",
        "json_schema",
        "pydantic_validation",
    ]
    if spec["context_strategy"] == "candidate_injected":
        knowledge_sources.insert(1, "controlled_vocabulary")
    control_modes = ["hard_constraint"]
    if spec["hybrid_balance_class"] == ["H1_post_deterministic"]:
        control_modes.append("posthoc_correction")
    if spec["hybrid_balance_class"] == ["H2_pre_deterministic"]:
        control_modes.append("soft_hint")
    return {
        "experiment_id": spec["experiment_id"],
        "dataset": "exect_v2",
        "schema_complexity": "exect_s1",
        "clinical_task_family": spec["clinical_task_family"],
        "model_track": "gpt4_1_mini",
        "program_architecture": spec["program_architecture"],
        "hybrid_balance_class": spec["hybrid_balance_class"],
        "deterministic_roles": deterministic_roles,
        "llm_roles": llm_roles,
        "interleaving_positions": spec["interleaving_positions"],
        "knowledge_sources": knowledge_sources,
        "control_modes": control_modes,
        "context_strategy": spec["context_strategy"],
        "evidence_strategy": "model_quote_with_diagnostic_span_check",
        "normalization_strategy": spec["normalization_strategy"],
        "verification_strategy": spec["verification_strategy"],
        "schema_integrity_strategy": ["json_schema", "pydantic_validation"],
        "example_strategy": "manual_few_shot_or_policy_examples",
        "comparison_group": spec["comparison_group"],
        "fixed_controls": {
            "schema_level": "exect_s0_s1_field_family",
            "scorer": "exect_field_family_deterministic_v1",
            "model_config_path": "configs/models/gan_s0_gpt4_1_mini.json",
            "split": "exectv2_fixed_v1:validation",
        },
        "varied_factor": spec["varied_factor"],
        "run_scope": "cap25",
        "canonical_run_id": run_dir.name,
        "outcome": spec["outcome"],
        "decision_doc": spec["decision_doc"],
        "metric_caveats": [
            "Cap-25 search grid under hybrid pipeline pivot; not mechanism closure.",
            "These are partial ExECT S0/S1 diagnostics, not published ExECTv2 benchmark reproduction.",
            f"stage_graph_id={spec.get('stage_graph_id')}; "
            f"stage_executor={spec.get('stage_executor', 'n/a')}.",
        ],
        "artifact_paths": [f"runs/{run_dir.name}"],
        "headline_metric": headline,
        "prompt_versions": spec["prompt_versions"],
        "config_paths": str(config_path.relative_to(ROOT)).replace("\\", "/"),
        "notes": spec["notes"],
        "comparison_groups": [spec["comparison_group"]],
    }


def _build_row(spec: dict) -> dict | None:
    if spec["experiment_id"].startswith("exect_"):
        return _build_exect_row(spec)
    return _build_gan_row(spec)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(REG_PATH.read_text(encoding="utf-8"))
    existing = {row["experiment_id"] for row in data["experiments"]}
    added: list[str] = []
    missing_runs: list[str] = []

    for spec in ALL_GRID_ROWS:
        if spec["experiment_id"] in existing:
            continue
        row = _build_row(spec)
        if row is None:
            missing_runs.append(spec["experiment_id"])
            continue
        data["experiments"].append(row)
        added.append(spec["experiment_id"])

    data["row_count"] = len(data["experiments"])
    print(f"Added {len(added)} rows: {added}")
    if missing_runs:
        print(f"Skipped (no run): {missing_runs}")

    if args.dry_run:
        return
    REG_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
