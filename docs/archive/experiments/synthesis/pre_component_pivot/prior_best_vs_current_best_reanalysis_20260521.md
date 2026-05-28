# Prior Best Config vs Current Best Pipeline Reanalysis

Date: 2026-05-21  
Status: Research synthesis note; follow-up tasks added to `docs/planning/kanban_plan.md`

## Research Question

What does the older best-config pipeline report still teach us when compared
with the current strongest Gan S0 and ExECT S1/S4 pipelines?

## Motivation

`docs/experiments/synthesis/prior_best_config_pipeline_report.md` preserves an earlier view of the
best ExECTv2 and Gan 2026 conditions. Those conditions were mainly prompt,
schema, example, and guideline bundles. Since then, the project has shifted
toward taxonomy-governed hybrid pipelines: deterministic temporal candidates,
benchmark bridges, explicit stage graphs, evidence policies, and model-specific
validation tracks. The purpose of this note is to prevent older useful insights
from being lost while avoiding stale "best config" claims.

## Evidence Reviewed

Primary historical source:

- `docs/experiments/synthesis/prior_best_config_pipeline_report.md`

Current promoted or frozen anchors:

- Gan GPT temporal-candidates verify-repair full validation:
  `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z`
- Gan Qwen35b temporal-candidates verify-repair full validation:
  `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z`
- ExECT S1 GPT full validation:
  `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`
- ExECT S4 GPT full validation:
  `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`
- ExECT S4 Qwen35b full validation:
  `runs/exect_s4_validation_full_qwen35b_ollama_20260520T160914Z`

Supporting inspections:

- `docs/experiments/gan/gan_s0_gpt4_1_mini_temporal_candidates_full_validation_decision_20260520.md`
- `docs/experiments/gan/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_error_analysis.md`
- `docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md`
- `docs/experiments/exect/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md`
- `docs/experiments/exect/exect_s4_validation_full_qwen35b_ollama_inspection_20260520.md`
- `docs/experiments/synthesis/best_pipeline_benchmark_context_assessment_20260521.md`

## Comparison Summary

| Area | Prior best-config read | Current best-pipeline read | Interpretation |
| --- | ---: | ---: | --- |
| Gan exact/current frequency | v3 relaxed `0.646`; strict `0.592`; completed-doc relaxed `0.815`, timeout-confounded | Qwen temporal-candidates monthly `65.8%`, Purist `75.5%`, Pragmatic `82.6%`; GPT temporal-candidates monthly `65.1%`, Purist `76.5%`, Pragmatic `84.2%` | Current architecture is stronger and more stable operationally, especially for category metrics and evidence, but normalized-label exact remains only `52-55%`. |
| ExECT S1-like core fields | Prior full ExECT configs: Gemini diagnosis exact `0.868`, seizure type F1 `0.678`; Qwen seizure type F1 `0.639` | GPT S1 full: micro `92.3%`, diagnosis `93.8%`, seizure type `90.5%`, medication `92.8%` | Current S1 success is not a generic model improvement; the ladder shows policy plus benchmark bridges dominate the lift. |
| ExECT broad S4 | Prior ExECT frequency remained weak: Qwen `0.342`, Gemini `0.237` | GPT S4 frequency `45.7%`, Qwen S4 frequency `50.0%`; S4 pooled micro `65.5-67.5%` | Frequency has improved materially but broad ExECT remains below published-style full benchmark performance and still needs field-family-specific repair. |

## Main Findings

### 1. The Old Report Found The Right Failure Type, But Not The Full Mechanism

The prior report correctly identified label granularity and benchmark-contract
mismatch as major ExECT failure modes. The current S1 reference ladder makes
the mechanism much sharper:

- D1 deterministic floor: `58.4%` micro on cap-25.
- L0 bare LLM: `60.0%`.
- L1 schema-only LLM: `67.7%`.
- L1 plus v4.10 policy and benchmark bridges: `92.3%` full validation.

The implication is that ExECT S1 performance is mostly driven by benchmark
policy and bridge behavior, not by adding more generic reasoning or more
pipeline stages.

### 2. Gan v3 Policy Still Matters, But It Is No Longer The Whole Answer

The prior Gan v3 condition discovered a critical annotation rule: only use
seizure-free labels after at least six months of seizure freedom; otherwise
compute a rate over the described period. That rule remains part of the current
default.

The current temporal-candidates verify-repair pipeline adds a different
mechanism: deterministic temporal preconditioning followed by LLM adjudication
and repair. This gives strong evidence support and category performance near
published synthetic/real anchors, but exact label fidelity remains a residual
problem.

### 3. Current Gan May Have Traded Some Surface Fidelity For Category Robustness

The old v3 strict match was reported as `0.592`. Current normalized-label exact
is `0.554` for Qwen temporal-candidates and `0.523` for GPT temporal-candidates.
These are not guaranteed to be identical metrics, but the direction is a useful
warning: the newer architecture may be better at clinical category placement
while still failing canonical label surfaces.

That makes the most valuable next Gan test a focused Axis 3 implementation
variant: keep temporal candidates and adjudication fixed, then reintroduce the
older v3/v5-style canonical format examples and guardrails.

### 4. ExECT Frequency Improved, But Gan Normalization Does Not Transfer Directly

ExECT S4 frequency improved from the prior best-config values to `45.7%` on GPT
and `50.0%` on Qwen. The residual errors are not the same as Gan's residual
errors. ExECT frequency requires:

- audited surfaces such as `1 per 1 month`;
- qualitative co-labels such as `frequency increased`, `frequency decreased`,
  `infrequent`, and `seizure free`;
- zero-rate labels such as `0 per 3 year`;
- multi-row retention when a document contains coexisting frequency facts.

Therefore, a useful ExECT follow-up should be an ExECT-specific S4 frequency
label-surface repair card, not a direct port of Gan temporal-candidate logic.

### 5. Gemini Is A Stale Champion Until Replayed Under The Current Architecture

The prior report named `full_exect_gemini_combined_examples` as the best overall
ExECT condition in the preserved Round 2 comparison. Current promoted/frozen
work has focused on GPT 4.1-mini and Qwen35b under the S-level field-family
architecture. If Gemini remains important for the paper or model-comparison
story, it needs a current S1/S4 replay rather than a comparison against stale
condition-level results.

## Next Experiments

### Gan S0 Canonical Format Port Onto Temporal-Candidates

Hypothesis: Adding the prior v3/v5 canonical format discipline to the current
temporal-candidates adjudicator can improve normalized-label exact accuracy
without reducing monthly, Purist, Pragmatic, schema, or evidence metrics.

Suggested controls:

- Dataset/split: `gan_2026_fixed_v1:validation`, cap-25 first.
- Model: GPT 4.1-mini for fast search; Qwen35b only after a cap-25 win.
- Program skeleton: current temporal-candidates adjudication / verify-repair.
- Scorer: `gan_frequency_deterministic_v1`.
- Primary metric: monthly-frequency accuracy.
- Secondary metrics: normalized-label exact, Purist, Pragmatic, schema-valid
  prediction rate, evidence quote support.

Promotion signal:

- normalized-label exact improves by at least 3 percentage points on cap-25
  without monthly/category/evidence regression; then run full validation.

### Gan S0 Exact-Frequency Residual Slice Replay

Hypothesis: The best next improvement is concentrated in exact-label residuals,
especially cluster assembly, boundary infrequent rates, and surface mismatch
cases.

Suggested controls:

- Use existing residual-slice tooling and docs:
  `docs/experiments/gan/gan_s0_residual_exact_frequency_error_analysis_20260521.md`,
  `scripts/export_gan_exact_frequency_residual_slice.py`.
- Compare current default against the canonical-format port on the same
  residual IDs.

Promotion signal:

- Reduced normalized-label and monthly mismatches on residual cases without
  over-abstention.

### ExECT S4 Frequency Surface Repair

Hypothesis: A narrow ExECT S4 frequency repair or bridge can improve
seizure-frequency F1 beyond the current `45.7-50.0%` band while leaving frozen
S3 families stable.

Suggested controls:

- Dataset/split: ExECT validation.
- Schema: S4 field-family diagnostic view.
- Baselines: GPT `...071248Z`, Qwen `...160914Z`.
- Scorer: `exect_s4_field_family_deterministic_v1`.
- Fixed fields: diagnosis, seizure type, investigation, annotated medication
  should not regress.

Promotion signal:

- seizure-frequency F1 improves by at least 3 percentage points on cap-25 or
  a predeclared frequency-heavy slice, with no material regression in
  investigation, seizure type, or medication.

### Gemini Replay Under Current S-Level Architecture

Hypothesis: The older Gemini combined-examples champion may or may not remain
competitive when evaluated under current S1/S4 field-family prompts, scorers,
and bridge policies.

Suggested controls:

- Run only if model-comparison evidence is needed.
- Replay S1 first; S4 only if S1 is informative and budget allows.
- Keep scorer, split, prompt version, and bridge policy identical to the frozen
  GPT/Qwen anchors.

Promotion signal:

- Gemini either beats GPT/Qwen on a target family or clarifies a model-specific
  failure profile worth reporting.

## Caveats

- This note does not rerun historical conditions.
- Prior Round 2 and Gan v3 metrics are taken from preserved reports; some raw
  historical run directories are not present in this checkout.
- Current Gan metrics are synthetic validation metrics, not published Real(300)
  reproduction.
- Current ExECT metrics are local field-family diagnostics, not CUI-aware
  ExECTv2 Table 1 reproduction.
- Normalized-label exact, strict match, monthly accuracy, Purist accuracy, and
  relaxed diagnostic match are related but not interchangeable.

## Recommended Kanban Updates

Add the follow-up work as near-term research cards:

1. Preregister Gan S0 canonical-format port onto temporal-candidates.
2. Implement and cap-25 test the Gan S0 canonical-format port.
3. Replay the exact-frequency residual slice against the new port.
4. Preregister ExECT S4 frequency surface repair.
5. Optionally replay Gemini under current S1/S4 architecture if model-comparison
   evidence is needed.
