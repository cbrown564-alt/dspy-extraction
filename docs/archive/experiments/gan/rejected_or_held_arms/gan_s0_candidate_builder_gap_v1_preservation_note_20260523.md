# Gan S0 Candidate Builder Gap V1 Preservation Note

Date: 2026-05-23  
Status: Preserved and verified  
Related Kanban card: G17  
Decision scope: operational gate for rerun reproducibility

## Purpose

Preserve the recovered `gan_s0_candidate_builder_gap_v1` deterministic builder state before any further GPT full-validation spend.

## Preservation Decision

The recovered Gan candidate-builder code state is already committed in git:

| Item | Value |
| --- | --- |
| Recovery commit | `3f96b0c Restore Gan temporal candidate builders and variant mapping` |
| Current branch at check | `main` |
| Branch relation | `main...origin/main [ahead 8]` |
| Code/config/test/script diff before rerun | clean |

No stash was created because there was no uncommitted recovered builder code to preserve. The accepted rerun state is the committed code at and after `3f96b0c`, with later documentation commits not changing the Gan builder implementation.

## No-Model Validation

Commands run immediately before the verified rerun:

```powershell
uv run pytest tests/test_gan_temporal_candidates.py
uv run python scripts/audit_gan_candidate_builder_gap.py
uv run python scripts/validate_primitives.py --errors-only
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json --env-file .env --dry-run
```

Results:

| Check | Result |
| --- | --- |
| Gan temporal-candidate tests | 49 passed |
| Enriched-slice candidate-builder audit | 23/25 gold-in-candidates |
| Primitive validation | warning-only output; no blocking errors |
| Experiment dry run | 299 Gan validation records, GPT 4.1-mini config, no optimizer; exited before model calls |

The primitive warnings were pre-existing registry/catalog alignment warnings and did not affect the Gan candidate-builder rerun gate.

## Dataset And Scorer Assumptions

This preservation gate follows the Gan audit and deterministic scorer policy:

- primary gold remains `seizure_frequency_number[0]`;
- `reference[0]` remains a secondary difficulty signal;
- evidence support remains diagnostic unless an experiment explicitly makes it prediction-affecting;
- normalized-label exact remains diagnostic, while monthly-frequency, Purist, and Pragmatic category metrics are benchmark-facing for Gan S0 synthetic validation.

## Follow-Through

The verified GPT rerun was launched after these checks as:

`runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z`
