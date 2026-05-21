# ExECT Qwen S1 Seizure-Gap Error Analysis

Date: 2026-05-20  
Preregistration: `docs/exect_qwen_s1_seizure_gap_error_analysis_preregistration_20260520.md`  
Comparison group: `exect_s1_interleaving_qwen_validation_v1`  
Inspection context: `docs/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md`  
Analysis artifact: `runs/exect_qwen_s1_seizure_gap_error_read_20260520.json`  
Regenerate:

```bash
uv run python scripts/analyze_exect_qwen_s1_seizure_gap_error_read.py \
  --qwen-h1-run runs/exect_s1_interleaving_h1_post_bridge_qwen35b_ollama_20260520T210722Z \
  --gpt-h1-run runs/exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z \
  --qwen-l1-run runs/exect_s1_interleaving_l1_raw_no_bridges_qwen35b_ollama_20260520T210719Z \
  --output runs/exect_qwen_s1_seizure_gap_error_read_20260520.json
```

## Research question

Why does Qwen3.6:35b remain far below GPT 4.1-mini on ExECT S1 `seizure_type` after the same benchmark-facing post bridges?

## Fixed controls

| Control | Value |
| --- | --- |
| Dataset / split | ExECTv2 `exectv2_fixed_v1:validation` (40 records) |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` |
| Qwen H1 run | `exect_s1_interleaving_h1_post_bridge_qwen35b_ollama_20260520T210722Z` |
| GPT H1 reference | `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z` |
| Qwen L1 raw reference | `exect_s1_interleaving_l1_raw_no_bridges_qwen35b_ollama_20260520T210719Z` |

## Headline metrics

| Track | Micro F1 | Seizure F1 | Seizure mismatch docs | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen L1 raw | 66.2% | 45.5% | 23 | 31 | 24 |
| Qwen H1 post bridge | 79.0% | 55.7% | 19 | 23 | 20 |
| GPT H1 post bridge | 92.3% | 90.5% | 6 | 5 | 4 |

Bridges improve Qwen seizure F1 by **+10.2pp** (45.5% → 55.7%) but leave a **−34.8pp** gap versus GPT H1 on the same validation split. The gap is not bridge absence; it is residual seizure labeling after identical bridge application.

## Overlap

| Set | Documents |
| --- | --- |
| Qwen mismatch only | EA0016, EA0029, EA0047, EA0050, EA0069, EA0090, EA0098, EA0116, EA0124, EA0125, EA0131, EA0136, EA0150, EA0170 (14) |
| Shared mismatch | EA0072, EA0109, EA0137, EA0143, EA0174 (5) |
| GPT mismatch only | EA0179 (1) |

Most seizure failures are **Qwen-only** (14/19 mismatch documents). Shared failures are a small hard core; the model-track gap is driven by errors GPT largely avoids under the same post-bridge path.

## Qwen error taxonomy (43 scored atoms)

| Category | Count | Representative docs |
| --- | ---: | --- |
| Surface inflection (singular/plural) | 14 | EA0016, EA0029, EA0050, EA0098, EA0116, EA0125, EA0131 |
| Secondary-generalisation policy | 14 | EA0090, EA0137, EA0143, EA0150, EA0170, EA0072 |
| Missed gold label | 7 | EA0069, EA0109, EA0136, EA0143, EA0150, EA0174 |
| Unsupported overcall (absence/myoclonic) | 6 | EA0029, EA0047, EA0050, EA0124, EA0125 |
| Other model wording | 2 | EA0136, EA0174 |

GPT post-bridge atoms total **9**, with no singular/plural inflection class and only **6** absence/myoclonic/inflection-style errors combined. GPT’s residual set is dominated by secondary-policy and missed-label cases on hard documents (EA0072, EA0109, EA0137, EA0143, EA0174, EA0179).

## Findings by category

### 1. Surface inflection (14 atoms) — model wording, not bridge absence

Qwen repeatedly emits singular benchmark surfaces where gold uses plural (or the reverse), e.g.:

| Doc | Predicted FP | Gold FN |
| --- | --- | --- |
| EA0016 | `focal seizures` | `focal seizure` |
| EA0029 / EA0050 / EA0116 / EA0131 | `generalized tonic clonic seizure` | `generalized tonic clonic seizures` |
| EA0098 | `focal to bilateral convulsive seizures` | `focal to bilateral convulsive seizure` |

GPT H1 does not show this inflection cluster on the same records. The shared bridge (`exect.seizure_type.benchmark_bridge.v1`) is applied to both tracks; the difference is **raw model surface choice before/at bridge input**, not a missing bridge on GPT.

Optional low-risk follow-up: pre-register a **plural-canonicalization** post-bridge rule only if paired with regression checks on GPT (which currently does not need it).

### 2. Unsupported overcall (6 atoms) — prompt/model policy

Qwen adds seizure types absent from gold:

| Doc | Spurious predictions | Notes |
| --- | --- | --- |
| EA0047 | `absence seizures`, `myoclonic seizures` | Pure FP; no gold seizure types |
| EA0029, EA0050, EA0125 | `absence seizure(s)` alongside GTCS | Gold is GTCS-only on audited surface |
| EA0124 | `absence seizures` | No matching gold |

GPT does not reproduce this absence/myoclonic cluster on the same documents. This matches the preregistered hypothesis: **model-side over-extraction**, not deterministic preconditioning.

### 3. Secondary-generalisation policy (14 atoms) — prompt/policy, both directions

Two coupled failure modes:

**Missed secondary/generalised gold (FN):** EA0090 (`secondary generalisation`), EA0069 (`generalized tonic clonic seizures`), EA0136 (`generalized seizures`), EA0143 (`secondarily generalized seizures`, `focal`), EA0150 (`complex partial seizures`, `secondary generalized seizures`).

**Extra or collapsed secondary token (FP):** EA0137 (`secondary` vs gold `secondary generalized seizures`), EA0143 (granular focal labels + extra GTCS), EA0150 (multiple focal surfaces without gold secondary set).

These align with `docs/previous_exect_error_analysis.md`: models split or collapse secondary generalisation differently than the audited benchmark policy. GPT still errs on some shared docs, but with far fewer atoms overall.

### 4. Missed gold without a paired inflection/overcall (7 atoms)

Includes EA0109 (`temporal lobe seizures` missed by both tracks) and EA0174 (`epileptic seizures` missed by Qwen while GPT predicts a long descriptive surface). EA0174 is the main **audit-adjacent** case (`epileptic seizures` generic gold vs descriptive prediction).

### 5. Evidence unsupported

Five seizure evidence-support flags on Qwen H1 (EA0047, EA0072, EA0135, EA0185, EA0188); only EA0047 and EA0072 overlap seizure mismatch docs. Evidence gaps are secondary to label-policy errors for the seizure-gap question.

## GPT comparison on shared hard docs

| Doc | Qwen issue | GPT issue |
| --- | --- | --- |
| EA0072 | FP `secondary`; FN `focal motor seizure` | Same pattern |
| EA0109 | FN `temporal lobe seizures` | Same FN |
| EA0137 | FP `focal to bilateral convulsive seizures`; FN `secondary generalized seizures` | FP `secondary` only |
| EA0143 | Multiple FPs + FN `focal` | Narrower FP set + FN `focal` |
| EA0174 | FN `epileptic seizures` | FP long descriptive label; FN `epileptic seizures` |

Shared docs account for only **5/19** Qwen mismatch documents. Qwen adds broader wrong surfaces on EA0137 and EA0143 that GPT avoids.

## Decision gate

| Gate | Assessment |
| --- | --- |
| Prompt-policy preregistration | **Met** — absence/myoclonic overcalls and secondary-policy misses dominate Qwen-only failures; GPT avoids most inflection/overcall patterns under the same bridges |
| Narrow post-template repair | **Partial** — inflection cluster could be bridged, but GPT does not need it; risk of false positives if applied blindly |
| Synthesis pause | **Not met** — two dominant buckets (inflection + secondary) both have plausible single-factor interventions, with prompt-policy as the safer primary |
| Manual audit review | **Not primary** — only EA0174-style generic gold is audit-adjacent; `specificity_collapsed` flags on EA0029/EA0050/EA0125 explain gold coarsening but do not justify delaying model-policy work |

## Recommended next action

**Prompt-policy preregistration** for a Qwen-targeted ExECT S1 seizure slice before any new full-validation run.

Pre-register a comparison group that varies only extraction policy examples/rules, holding fixed:

- validation 40, `exect_s0_s1_field_family`, `exect_field_family_deterministic_v1`
- Qwen3.6:35b, `artifact_benchmark_bridge_only` (same bridges)
- frozen Qwen H1 anchor `…210722Z` as baseline

Policy targets (one combined prereg, not separate model runs per bullet):

1. **No separate secondary type** unless the letter names multiple current seizure types (address EA0090, EA0143, EA0150 FNs and EA0137 FP `secondary`).
2. **Use audited plural seizure surfaces** when the note’s diagnosis row uses plural forms (address inflection cluster on EA0029, EA0050, EA0116, EA0131).
3. **Do not invent absence/myoclonic types** without affirmed seizure-type evidence in the diagnosis/seizure surface (address EA0047, EA0124, EA0029, EA0050, EA0125).

**Do not** open H2 pre-vocabulary, new post bridges, or another S1 interleaving matrix without that preregistration.

**Defer** narrow plural-canonicalization bridge retune unless prompt-policy cap-25 fails and GPT regression tests are included.

## Validation

- Script: `scripts/analyze_exect_qwen_s1_seizure_gap_error_read.py`
- Artifact: `runs/exect_qwen_s1_seizure_gap_error_read_20260520.json`
- No model calls in this analysis
