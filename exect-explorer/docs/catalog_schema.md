# Explorer Model Catalog Schema

Date: 2026-05-24  
Schema version: `2026-05-24`  
Shared by ExECT and Gan static Explorer bundles.

## Purpose

Both `model_catalog.json` (ExECT) and `model_catalog_gan.json` (Gan) follow one envelope so the Model lens can render either dataset without dataset-specific UI branches beyond metric labels.

Builders:

- `exect-explorer/scripts/build_model_catalog.py`
- `exect-explorer/scripts/build_model_catalog_gan.py`
- Shared helpers: `exect-explorer/scripts/catalog_shared.py`

## Top-Level Envelope

| Field | Type | Description |
| --- | --- | --- |
| `schema_version` | string | Catalog schema version (currently `2026-05-24`) |
| `artifact_class` | string | Always `explorer_model_catalog` |
| `dataset` | string | `exect_v2` or `gan_2026` |
| `metric_labels` | object | Display labels for the three headline metrics plus evidence |
| `generated_at_utc` | string | ISO-8601 UTC timestamp |
| `source` | object | Provenance note; optional extra keys |
| `tasks` | array | Task groupings for the Model panel selector |
| `runs` | array | Run records with metrics and per-document pipelines |

## Metric Label Mapping

ExECT uses F1-style labels (default):

| Key | Label |
| --- | --- |
| `micro_f1` | Micro F1 |
| `micro_precision` | Precision |
| `micro_recall` | Recall |
| `evidence_support` | Evidence |

Gan maps the same numeric slots to frequency hierarchy metrics:

| Key | Label | Source metric |
| --- | --- | --- |
| `micro_f1` | Monthly accuracy | `monthly_frequency_accuracy` |
| `micro_precision` | Purist category | `purist_category_accuracy` |
| `micro_recall` | Pragmatic category | `pragmatic_category_accuracy` |
| `evidence_support` | Evidence | `evidence_quote_support_rate` |

The UI reads `metric_labels` from the catalog; it does not hardcode dataset-specific names.

## Task Entry

```json
{
  "id": "S1",
  "label": "ExECT S1",
  "scope": "diagnosis, seizure type, annotated medication",
  "default_run_id": "exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z",
  "run_ids": ["..."]
}
```

## Run Entry

Shared fields across datasets:

| Field | Description |
| --- | --- |
| `task` | Task id |
| `run_id` | Experiment run directory name |
| `model_label` | Human-readable model/arm label |
| `evidence_status` | `paper_frozen` or `workspace_candidate` |
| `best` | Default run for the task |
| `run_dir` | Relative path to run artifacts |
| `schema_level` | Experiment schema level |
| `scorer_mode` | Deterministic scorer id |
| `program_variant` | DSPy program variant |
| `prompt_version` | Prompt policy version |
| `metrics` | Headline metrics block (percentages) |
| `documents` | Map of document id → pipeline trace |

## Document Pipeline Step

Each step uses the same shape for ExECT field-family and Gan frequency extraction:

```json
{
  "id": "EA0001.0.diagnosis",
  "field": "diagnosis",
  "raw_value": "...",
  "normalized_value": "...",
  "temporality": "unknown",
  "negation": "unknown",
  "quality_flags": [],
  "evidence": [{"text": "...", "start": 0, "end": 10}],
  "deterministic_step": {
    "label": "policy bridge / scorer normalization",
    "output": "...",
    "metadata": {}
  },
  "outcome": "matched"
}
```

Outcome values: `matched`, `false_positive`, `false_negative`, `miss_or_partial`, `evidence_issue`.

Dataset-specific mismatch logic stays in each builder; the emitted step shape is shared.

## Validation

`catalog_shared.validate_catalog_envelope()` checks required keys at build time.  
`tests/test_explorer_catalog_schema.py` validates both builders in CI.

## Non-Goals

- No change to source note loaders (`build_manifest*.py`) or gold semantics.
- No unified catalog file; ExECT and Gan remain separate JSON outputs for size and rebuild isolation.
