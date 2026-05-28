import json
from pathlib import Path

configs_dir = Path("configs/experiments")
gpt_files = [
    "gan_s0_date_stage_d0_baseline_det_candidates_cap25_gpt4_1_mini.json",
    "gan_s0_date_stage_d1_det_events_cap25_gpt4_1_mini.json",
    "gan_s0_date_stage_d2_llm_events_cap25_gpt4_1_mini.json",
    "gan_s0_date_stage_d3_hybrid_events_cap25_gpt4_1_mini.json",
    "gan_s0_entity_first_c0_date_events_cap25_gpt4_1_mini.json",
    "gan_s0_entity_first_c1_llm_tags_date_events_cap25_gpt4_1_mini.json",
]

for gf in gpt_files:
    gp = configs_dir / gf
    if not gp.exists():
        continue
    data = json.loads(gp.read_text(encoding="utf-8"))
    
    # Update experiment ID and model config path
    data["experiment_id"] = data["experiment_id"].replace("_gpt4_1_mini", "_qwen35b")
    data["model_config_path"] = "configs/models/gan_s0_qwen35b_ollama.json"
    
    qwen_filename = gf.replace("_gpt4_1_mini.json", "_qwen35b.json")
    qp = configs_dir / qwen_filename
    qp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Generated: {qp}")
