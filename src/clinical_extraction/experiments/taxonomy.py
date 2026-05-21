from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from clinical_extraction.schemas import FrozenModel

REGISTRY_PATH = Path("docs/experiment_registry.json")

DatasetValue = Literal["gan_2026", "exect_v2"]
SchemaComplexityValue = Literal[
    "gan_s0",
    "exect_s1",
    "exect_s2",
    "exect_s3",
    "exect_s4",
]
ProgramArchitectureValue = Literal[
    "single_pass",
    "direct_single_pass",
    "verify_repair",
    "temporal_candidates_single_pass",
    "temporal_candidates_single_pass",
    "llm_temporal_candidates_single_pass",
    "hybrid_temporal_candidates_single_pass",
    "temporal_candidates_adjudicate_verify_repair",
    "temporal_candidates_adjudicate_det_guards",
    "temporal_candidates_adjudicate_det_evidence",
    "temporal_candidates_adjudicate_confirm_only",
    "temporal_candidates_adjudicate_verify_repair_no_guards",
    "temporal_candidates_adjudicate_verify_repair_span_check",
    "llm_temporal_candidates_verify_repair",
    "temporal_candidates_verify_repair",
    "temporal_event_table_verify_repair",
    "react_temporal_tools",
    "section_aware",
    "diagnosis_recall",
    "optimizer_compiled_single_pass",
]
HybridBalanceClassValue = Literal[
    "L0_llm_only",
    "L1_llm_constrained",
    "H1_post_deterministic",
    "H2_pre_deterministic",
    "H3_interleaved_tool_hybrid",
    "H4_deterministic_first_llm_adjudicates",
    "D1_deterministic_only",
]
InterleavingPositionValue = Literal[
    "pre",
    "during",
    "tool_during",
    "post",
    "eval_only",
]
VariedFactorValue = Literal[
    "program_architecture",
    "hybrid_balance_class",
    "interleaving_position",
    "knowledge_source_position",
    "model_track",
    "schema_complexity",
    "prompt_policy",
    "optimizer_strategy",
    "ladder_rung",
    "validation_ladder_rung",
    "run_scope",
    "normalization_strategy",
    "verification_strategy",
    "evidence_strategy",
    "control_mode",
    "pipeline_stage_graph",
    "stage_executor",
    "implementation_variant",
    "context_selection_policy",
    "multi_factor",
]
ContextSelectionPolicyValue = Literal[
    "full_note",
    "full_note_plus_deterministic_temporal_candidates",
    "deterministic_temporal_candidates_only",
]
StageExecutorValue = Literal[
    "det_candidates_llm_adjudicate",
    "llm_candidates_llm_adjudicate",
    "hybrid_candidates_llm_adjudicate",
    "det_candidates_llm_adjudicate_llm_vr",
    "llm_candidates_llm_adjudicate_llm_vr",
    "llm_extract_inline_bridges",
    "llm_extract_post_bridges",
    "det_all_family_hints_llm_extract",
    "det_seizure_hints_llm_extract",
    "det_medication_hints_llm_extract",
]
IntendedDecisionValue = Literal[
    "promote",
    "freeze",
    "reject",
    "hold",
    "superseded",
    "exploratory",
    "pending",
]
TaxonomyExemptionValue = Literal["legacy_registry", "exploratory_stub"]
ClinicalTaskFamilyValue = Literal[
    "frequency",
    "diagnosis",
    "seizure_type",
    "medication",
    "investigation",
    "comorbidity",
    "birth_development",
    "family_history",
    "social_history",
    "driving",
    "pregnancy",
    "multi_family",
]


class ExperimentTaxonomy(FrozenModel):
    """Minimum hybrid-design metadata required on new experiment configs."""

    dataset: DatasetValue
    schema_complexity: SchemaComplexityValue
    program_architecture: ProgramArchitectureValue
    hybrid_balance_class: list[HybridBalanceClassValue] = Field(min_length=1)
    interleaving_positions: list[InterleavingPositionValue] = Field(min_length=1)
    varied_factor: VariedFactorValue
    comparison_group: str
    intended_decision: IntendedDecisionValue
    clinical_task_family: ClinicalTaskFamilyValue | list[ClinicalTaskFamilyValue] | None = (
        None
    )
    stage_graph_id: str | None = None
    stage_executor: StageExecutorValue | None = None
    implementation_variant: str | None = None
    validation_ladder_rung: str | None = None
    context_selection_policy: ContextSelectionPolicyValue | None = None

    @model_validator(mode="after")
    def validate_taxonomy_text_fields(self) -> ExperimentTaxonomy:
        if not self.comparison_group.strip():
            raise ValueError("comparison_group must be a non-empty string.")
        return self


def load_experiment_registry(path: Path = REGISTRY_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def registry_experiment_ids(path: str = str(REGISTRY_PATH.resolve())) -> frozenset[str]:
    payload = load_experiment_registry(Path(path))
    return frozenset(row["experiment_id"] for row in payload["experiments"])


def taxonomy_covers_config(config_dataset: str, taxonomy: ExperimentTaxonomy) -> bool:
    return taxonomy.dataset == config_dataset
