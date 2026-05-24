import json
from pathlib import Path

# Paths
ROOT = Path("c:/Users/cbrow/Code/dspy-extraction")
REGISTRY_PATH = ROOT / "docs" / "experiments" / "synthesis" / "experiment_registry.json"

# Load registry
registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

# Find the index of the GPT validation row to place Qwen right after it
gpt_index = -1
for idx, exp in enumerate(registry["experiments"]):
    if exp["experiment_id"] == "gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation":
        gpt_index = idx
        gpt_exp = exp
        break

if gpt_index == -1:
    print("Error: Could not find GPT validation row in registry.")
    exit(1)

# Build the Qwen row based on the GPT row
qwen_exp = {
    "experiment_id": "gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation",
    "dataset": "gan_2026",
    "schema_complexity": "gan_s0",
    "clinical_task_family": ["frequency"],
    "model_track": "qwen35b",
    "program_architecture": gpt_exp["program_architecture"],
    "hybrid_balance_class": gpt_exp["hybrid_balance_class"],
    "deterministic_roles": gpt_exp["deterministic_roles"],
    "llm_roles": gpt_exp["llm_roles"],
    "interleaving_positions": gpt_exp["interleaving_positions"],
    "knowledge_sources": gpt_exp["knowledge_sources"],
    "control_modes": gpt_exp["control_modes"],
    "context_strategy": gpt_exp["context_strategy"],
    "evidence_strategy": gpt_exp["evidence_strategy"],
    "normalization_strategy": gpt_exp["normalization_strategy"],
    "verification_strategy": gpt_exp["verification_strategy"],
    "schema_integrity_strategy": gpt_exp["schema_integrity_strategy"],
    "example_strategy": gpt_exp["example_strategy"],
    "comparison_group": "gan_s0_candidate_builder_gap_v1_model_comparison",
    "fixed_controls": {
        "schema_level": "gan_frequency_s0",
        "scorer": "gan_frequency_deterministic_v1",
        "model_config_path": "configs/models/gan_s0_qwen35b_ollama.json",
        "split": "gan_2026_fixed_v1:validation"
    },
    "varied_factor": "model_track",
    "run_scope": "full_validation",
    "canonical_run_id": "gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z",
    "outcome": "hold",
    "decision_doc": "docs/experiments/gan/gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_inspection_20260523.md",
    "metric_caveats": [
      "Gan synthetic validation, not published benchmark reproduction.",
      "Validation of Qwen3.6:35b Ollama transferability under the candidate-builder gap v1 surface.",
      "decision_scope arm; not operational promotion."
    ],
    "artifact_paths": [
      "runs/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z"
    ],
    "headline_metric": {
      "name": "monthly_frequency_accuracy",
      "value": 0.7070707070707071,
      "secondary": {
        "purist_category_accuracy": 0.8316498316498316,
        "pragmatic_category_accuracy": 0.9057239057239057,
        "schema_valid_prediction_rate": 0.9933110367892977,
        "evidence_quote_support_rate": 0.9966329966329966,
        "prediction_seconds_per_record": 10.903010033444816 # 3260 seconds total / 299 records
      }
    },
    "prompt_versions": "gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy",
    "config_paths": "configs/experiments/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation.json",
    "notes": "decision_scope: arm. Qwen transfer validation completed; unblocked for potential promotion.",
    "comparison_groups": [
      "gan_s0_candidate_builder_gap_v1_model_comparison"
    ],
    "comparison_caveat": "Axis 3 model track comparison on full validation under builder-gap v1 surface."
}

# Check if already exists to avoid duplicates
existing_ids = [e["experiment_id"] for e in registry["experiments"]]
if qwen_exp["experiment_id"] in existing_ids:
    print(f"Warning: Experiment {qwen_exp['experiment_id']} already registered. Overwriting.")
    # remove existing
    registry["experiments"] = [e for e in registry["experiments"] if e["experiment_id"] != qwen_exp["experiment_id"]]

# Insert right after GPT validation row
registry["experiments"].insert(gpt_index + 1, qwen_exp)

# Increment row count
registry["row_count"] = len(registry["experiments"])

# Save back
REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
print(f"Successfully registered {qwen_exp['experiment_id']} in experiment_registry.json. New row count: {registry['row_count']}")
