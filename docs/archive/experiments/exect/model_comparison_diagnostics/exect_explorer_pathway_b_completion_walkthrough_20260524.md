# Cross-Dataset Explorer Pathway B — Completion Walkthrough

Date: 2026-05-24  
Pathway: B — Cross-Dataset Explorer  
Status: **Complete**

## Pathway Outcome

Static Explorer views for ExECTv2 and Gan 2026 let reviewers inspect notes, gold labels, model predictions, deterministic pipeline steps, and scorer outcomes without rerunning models.

| Card | Status | Artifact |
| --- | --- | --- |
| B1. Gan data-shape audit | Completed | `exect-explorer/scripts/build_manifest_gan.py` |
| B2. Gan static catalog builder | Completed | `exect-explorer/scripts/build_model_catalog_gan.py` |
| B3. Gan Explorer UI lane | Completed | Dataset switcher in `exect-explorer/src/App.jsx` |
| B4. Shared catalog schema cleanup | Completed | `exect-explorer/scripts/catalog_shared.py`, `exect-explorer/docs/catalog_schema.md` |

## B4 Changes

### Shared catalog envelope

Both catalogs now emit:

- `artifact_class`: `explorer_model_catalog` (was dataset-specific)
- `dataset`: `exect_v2` or `gan_2026`
- `metric_labels`: dataset-appropriate display names for headline metrics

### Metric label fix (Gan)

The Model panel previously labeled Gan monthly/purist/pragmatic metrics as Micro F1 / Precision / Recall. Gan catalogs now declare:

| Slot | Gan label |
| --- | --- |
| `micro_f1` | Monthly accuracy |
| `micro_precision` | Purist category |
| `micro_recall` | Pragmatic category |

`ModelPanel.jsx` reads `catalog.metric_labels` with ExECT defaults as fallback.

### Shared pipeline step shape

ExECT and Gan builders emit identical pipeline step keys via `catalog_shared.build_pipeline_step()`. Dataset-specific mismatch logic remains in each builder.

## Validation

| Check | Result |
| --- | --- |
| `uv run python exect-explorer/scripts/build_model_catalog.py` | 10 runs written |
| `uv run python exect-explorer/scripts/build_model_catalog_gan.py` | 2 runs written |
| `uv run --extra dev pytest tests/test_explorer_catalog_schema.py` | 3/3 passed |
| `npm run build` (exect-explorer) | Success |

## Operational Usage

```bash
# Regenerate catalogs after new run artifacts
uv run python exect-explorer/scripts/build_model_catalog.py
uv run python exect-explorer/scripts/build_model_catalog_gan.py

# Dev server
cd exect-explorer && npm run dev
```

## Guardrails Preserved

- No change to source note loaders or gold semantics
- Separate catalog JSON files retained (size/rebuild isolation)
- ExECT and Gan index/manifest builders unchanged

## Files Touched

- `exect-explorer/scripts/catalog_shared.py` (new)
- `exect-explorer/scripts/build_model_catalog.py`
- `exect-explorer/scripts/build_model_catalog_gan.py`
- `exect-explorer/src/components/ModelPanel.jsx`
- `exect-explorer/docs/catalog_schema.md` (new)
- `exect-explorer/public/data/model_catalog.json` (regenerated)
- `exect-explorer/public/data/model_catalog_gan.json` (regenerated)
- `tests/test_explorer_catalog_schema.py` (new)
