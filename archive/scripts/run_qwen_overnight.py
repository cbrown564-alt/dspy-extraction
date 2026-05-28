import subprocess
import sys
from pathlib import Path

# Reconfigure stdout/stderr to UTF-8 to prevent encoding errors on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

log_file = Path("runs/qwen_overnight.log")
log_file.parent.mkdir(parents=True, exist_ok=True)

experiments = [
    ("run_experiment.py", "configs/experiments/gan_s0_date_stage_d0_baseline_det_candidates_cap25_qwen35b.json"),
    ("run_experiment.py", "configs/experiments/gan_s0_date_stage_d1_det_events_cap25_qwen35b.json"),
    ("run_experiment.py", "configs/experiments/gan_s0_date_stage_d2_llm_events_cap25_qwen35b.json"),
    ("run_experiment.py", "configs/experiments/gan_s0_date_stage_d3_hybrid_events_cap25_qwen35b.json"),
    ("run_experiment.py", "configs/experiments/gan_s0_entity_first_c0_date_events_cap25_qwen35b.json"),
    ("run_experiment.py", "configs/experiments/gan_s0_entity_first_c1_llm_tags_date_events_cap25_qwen35b.json"),
    ("run_experiment.py", "configs/experiments/gan_s0_self_consistency_s0_single_sample_cap25_qwen35b.json"),
    ("run_self_consistency.py", "configs/experiments/gan_s0_self_consistency_sample5_cap25_qwen35b.json"),
]

with log_file.open("w", encoding="utf-8") as f:
    for idx, (script, config_path) in enumerate(experiments, start=1):
        msg = f"\n=================== Running Qwen Experiment {idx}/{len(experiments)}: {config_path} ===================\n"
        print(msg)
        f.write(msg)
        f.flush()
        
        cmd = ["uv", "run", "python"]
        if script == "run_experiment.py":
            cmd.extend(["scripts/run_experiment.py", "--experiment", config_path])
        else:
            cmd.extend(["scripts/run_self_consistency.py", "--config", config_path])
            
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        # Stream output to stdout and log file
        for line in process.stdout:
            sys.stdout.write(line)
            f.write(line)
            f.flush()
            
        process.wait()
        if process.returncode != 0:
            err_msg = f"\nExperiment failed with return code {process.returncode}\n"
            print(err_msg)
            f.write(err_msg)
            f.flush()
            
print("\nAll Qwen overnight experiments completed.")
