# Dataset split policy

Fixed split files under `data/splits/` use three partitions with stable record IDs:

| Partition | ExECTv2 (`exectv2_fixed_v1`) | Gan 2026 (`gan_2026_fixed_v1`) | Role |
| --- | ---: | ---: | --- |
| **train** | 120 | 900 | Optimizer compile trainset only (`scripts/run_experiment.py` reads the `train` key). Not used for routine benchmark eval configs. |
| **validation** | 40 | 300 | Routine capped/full eval, error analysis, ablations. |
| **test** | 40 | 300 | Holdout; requires `report_on_test_split: true` on experiment configs. |

## Naming change (2026-05-21)

The former **`development`** partition was renamed to **`train`** in place (same IDs, same 60/20/20 ratios). Config `split_name` values such as `exectv2_fixed_v1:validation` are unchanged. Optimizer compile now resolves `exectv2_fixed_v1:train` when a config references that partition explicitly.

Legacy split JSON that still uses `development` is accepted only as a fallback when loading optimizer train IDs or validating manifests.

## Do not merge train into test

Train IDs overlap the historical optimizer pool. Enlarging **test** by absorbing train would contaminate the holdout with examples used for DSPy compile. Keep **test** at 40 (ExECT) / 300 (Gan) unless a new preregistered split version is generated end-to-end.

## Regenerating Gan splits

```bash
uv run python scripts/generate_gan_splits.py
```

Output must include `train`, `validation`, and `test` keys (see `clinical_extraction.splits.make_gan_splits`).
