# Primitive-Aware Experiment Inspection Template

Date: YYYY-MM-DD  
Status: Draft | Completed  
Comparison group: `<dataset>_<schema>_<factor>_<model_track>_<scope>_v<number>`  
Pre-registration: `docs/<study>_preregistration_YYYYMMDD.md`  
Related config(s): `configs/experiments/<experiment_id>.json`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | `gan_2026` \| `exect_v2` |
| Schema complexity | `gan_s0` \| `exect_s1` … `exect_s4` |
| Clinical task family | e.g. `frequency`, `medication`, or multi-family list |
| Hybrid balance class | e.g. `L1_llm_constrained`, `H1_post_deterministic` |
| Interleaving positions | e.g. `pre`, `during`, `post`, `tool_during`, `eval_only` |
| Varied factor | e.g. `interleaving_position`, `program_architecture` |
| Intended decision | `promote` \| `freeze` \| `reject` \| `hold` \| `exploratory` \| `pending` |

## Run scope and artifacts

| Arm | Run ID | Config | Run scope |
| --- | --- | --- | --- |
| L1 / H1 / … | `runs/<run_id>` | `<config>.json` | `cap25` \| `slice` \| `full_validation` |

Fixed controls: split, schema level, program variant, model track, prompt version.

Varied factor: state exactly what differs between arms in this comparison group.

## Primitive use

List every primitive or deterministic helper that affects prediction or diagnostics.

| Primitive ID | Position | Control mode | Prediction-affecting | Notes |
| --- | --- | --- | --- | --- |
| e.g. `exect.medication.benchmark_bridge.v1` | `post` | `posthoc_correction` | yes | Applied as artifact-only bridge |

If no primitives are used, state `none` and explain why the arm is still taxonomy-valid.

## Scorer mode

| Field | Value |
| --- | --- |
| Scorer mode | e.g. `exect_field_family_deterministic_v1` |
| Benchmark-facing fields | List field families included in the primary metric |
| Scorer changed vs anchor? | `no` (default) — if yes, document why comparison remains valid |

## Normalization semantics

Describe how raw model output becomes benchmark-facing labels.

- Raw vs canonical vs benchmark-facing separation preserved? (`yes` / `no`, with examples)
- Bridge stage: `inline` \| `artifact_only` \| `scorer_only` \| `none`
- Prediction-affecting normalization rules: bullet list
- Scorer-only normalization rules: bullet list

## Evidence semantics

- Evidence strategy: e.g. `model_quote`, `model_quote_with_diagnostic_span_check`, `absent`
- Evidence affects prediction? `yes` \| `no` (default for diagnostic guards: `no`)
- Unsupported quote handling:
- Unknown vs no-reference distinctions (Gan frequency only, if applicable):

## Headline metrics

| Arm | Primary metric | Secondary metrics | Notes |
| --- | ---: | --- | --- |
| … | … | … | … |

State the primary decision metric explicitly. Pooled micro F1 is diagnostic unless the pre-registration says otherwise.

## Decisions

| Arm | Outcome | Rationale |
| --- | --- | --- |
| … | `promote` \| `freeze` \| `reject` \| `hold` | … |

## Caveats and interpretation

- Dataset audit assumptions that constrained interpretation
- Slice or cap scope limits (do not extrapolate)
- Known gold ambiguities or scorer caveats
- What remains uncertain or blocked

## Recommended next work

1. …
2. …
