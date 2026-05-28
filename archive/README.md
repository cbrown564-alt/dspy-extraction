# Repository Archive

Status: archive / replay provenance

This directory stores experiment surfaces that are no longer part of the live
steering surface but remain needed for reproducibility, rejected-arm memory, or
historical run tracing.

## Configs

`archive/configs/` contains experiment configs that should not be treated as
active pulls. `src/clinical_extraction/paths.py` resolves a missing
`configs/experiments/<name>.json` reference to `archive/configs/<name>.json`,
so older docs, run metadata, and tests can still replay archived configs by
basename.

After C19, `configs/experiments/` is reserved for current-authority config rows
shown in `docs/experiments/synthesis/program_variant_registry.md`. Archived
configs may still match promoted, diagnostic, historical, rejected, or replay
variant rows, but the archive path makes them provenance surfaces rather than
current work.

## Scripts

`archive/scripts/` contains historical launchers, one-off generators, and
rejected-arm utilities. C19 moved these active-tree scripts here:

- `generate_qwen_configs.py`: one-off config generator.
- `register_gan_lane_a_cap25_registry.py`: old registry registration utility.
- `run_qwen_overnight.py`: historical queue launcher.
- `run_self_consistency.py`: R13 self-consistency replay utility for a rejected
  compute-allocation arm.

Do not promote archived scripts or configs back into active use without a
current Kanban card, decision doc, and validation plan.
