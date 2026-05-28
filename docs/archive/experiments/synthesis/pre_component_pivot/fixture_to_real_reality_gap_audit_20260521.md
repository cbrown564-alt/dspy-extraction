# Fixture-to-Real Reality-Gap Audit

Date: 2026-05-21  
Status: Literature-card audit complete  
Decision scope: research hygiene / operational guardrail  
Primary Kanban card: `Fixture-to-real reality-gap audit`

## Research Question

How much should the project trust deterministic fixtures and residual slices as evidence for clinical extraction improvement, compared with cap-25 and full-validation behavior?

## Bottom Line

Fixtures and residual queues are **contract evidence**, not performance evidence. They are useful for proving that a loader, bridge, candidate builder, normalizer, or scorer handles a known edge case. They do not by themselves justify promotion, mechanism closure, or benchmark-facing claims.

The current evidence shows a real fixture-to-validation gap:

- Gan residual fixtures can strongly predict whether a specific candidate surface is available, but full validation still exposes adjudication tradeoffs, unknown overcalls, and category regressions.
- ExECT residual fixtures are very good at naming label-policy and bridge-surface failures, but small queues are too sparse to infer broad family-level gains.
- Cap-25 runs are a better search layer than fixtures, but even cap-25 wins need full-validation confirmation when the proposed change alters scorer-facing outputs.
- Neither Gan synthetic validation nor ExECT local field-family validation should be described as published real-set benchmark reproduction.

## Source Artifacts

### Dataset Audits

| Dataset | Audit guidance used |
| --- | --- |
| Gan 2026 | `docs/datasets/gan/gan_2026_label_audit.md` — JSON synthetic labels use `seizure_frequency_number[0]` as gold; `reference` is secondary; real Excel letters are a different population and annotation scheme. |
| ExECTv2 | `docs/datasets/exect/exect_gold_label_audit.md` — current local scoring depends on audited loader choices: JSON primary source, certainty threshold, diagnosis specificity collapse, and known medication temporality limitations. |

### Fixture and Slice Artifacts

| Artifact | Scope | Purpose |
| --- | --- | --- |
| `data/fixtures/gan_s0_exact_frequency_residual_slice.json` | 30 Gan records | Hard queue from VR full-validation monthly misses. |
| `data/fixtures/gan_s0_qwen_error_regression_slice.json` | 14 Gan records | Qwen/GPT regression stress queue. |
| `data/fixtures/exect_s0_label_policy_error_regression_slice.json` | 37 ExECT records | S0/S1 recurrent label-policy failures and canonical anchors. |
| `data/fixtures/exect_s2_comorbidity_residual_slice.json` | 6 ExECT records | S2 comorbidity qualitative queue. |
| `data/fixtures/exect_s3_epilepsy_cause_residual_slice.json` | 3 ExECT records | S3 epilepsy-cause qualitative queue. |
| `data/fixtures/primitive_cases.json` | deterministic primitive cases | Contract coverage for typed primitives. |

### Validation and Inspection Artifacts

| Artifact | Relevance |
| --- | --- |
| `docs/experiments/gan/gan_s0_canonical_format_residual_slice_replay_20260521.md` | Cap-25 canonical-format +4pp was not confirmed on the 30-record hard queue. |
| `docs/experiments/gan/gan_s0_expanded_builders_residual_slice_replay_v3_20260521.md` | Builder-gap pass improved the hard queue by +13.4pp monthly, but remained slice-level evidence. |
| `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md` | Full validation confirmed expanded builders as best known monthly arm, but with paired tradeoffs and category regressions. |
| `docs/experiments/exect/exect_s2_comorbidity_residual_slice_replay_20260521.md` | 6-doc queue showed +14.0pp comorbidity F1 for C0, while cap-25 was null. |
| `docs/experiments/exect/exect_s3_epilepsy_cause_residual_slice_replay_20260521.md` | 3-doc queue was null for K0+K1 despite cap/full-validation cause gains elsewhere. |
| `docs/experiments/exect/exect_s4_epilepsy_cause_bridge_gpt_full_validation_v1_inspection_20260521.md` | Full validation confirmed K0+K1 cause lift on sparse support, but only +0.3pp pooled micro. |
| `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_full_validation_v1_inspection_20260521.md` | Full validation confirmed a cap-25 medication-temporality precision guard without moving unrelated families. |
| `docs/experiments/synthesis/best_pipeline_benchmark_context_assessment_20260521.md` | Separates local validation performance from published Gan real-set and ExECT broad benchmark claims. |

## Findings

### 1. Fixtures Find Real Bugs, But They Overstate Generality

The strongest fixture use is TDD-style contract protection:

- ExECT S0/S1 label-policy fixture retains known diagnosis, seizure-type, and medication temporality anchors.
- ExECT S2/S3 residual queues identify specific bridge surfaces such as TBI atomization, plural/surface mismatches, and modifier stripping.
- Gan residual queues identify exact-frequency failure mechanisms: arithmetic/window precision, unknown-vs-quantified, cluster composition, and long-denominator boundaries.

These are valid engineering artifacts. The overclaim risk appears when a fixture pass is read as evidence that the intervention will improve a split-level metric. Small queues are enriched for a narrow failure class and often exclude the regressions that appear elsewhere.

### 2. Gan Shows the Clearest Fixture-to-Full Translation, But Still With Tradeoffs

Gan expanded builders are the best example of a fixture/slice signal that survived broader validation:

| Evidence layer | Result |
| --- | --- |
| 30-record residual replay v3 | 23/30 monthly correct, +13.4pp vs v2; builder-gap targets 4/5 monthly hits. |
| Cap-50 expanded builders | 68.0% monthly. |
| Full validation F0 | 68.1% monthly, +3.0pp vs VR anchor; normalized exact 56.0%; schema 99.7%; evidence 100%. |

But the full-validation read also shows why residual evidence is insufficient:

- F0 recovered 13 sampled VR misses and regressed 13 sampled VR hits.
- Pragmatic category performance was lower than the VR anchor (81.5% vs 84.2%).
- Remaining misses shifted toward unknown abstention and seizure-type-adjacent frequency selection.

Interpretation: the builder fixtures confirmed candidate-surface coverage, not an overall mechanism closure. The intervention promoted as an **arm**, while det temporal candidate generation and verify-repair placement remain open mechanism classes.

### 3. Gan Canonical-Format Examples Exposed a Slice Mismatch

The canonical-format port looked promising on the cap-25 prefix, but the fixed hard queue did not confirm it:

| Layer | C0 | C1 | Read |
| --- | ---: | ---: | --- |
| Cap-25 prefix monthly | 52% | 56% | Search signal only. |
| 30-record residual monthly | 13.3% | 13.3% | Net null, 1 recovery vs 1 regression. |

This is a clean reality-gap warning. The cap-25 prefix and the full-validation monthly-miss queue were testing different error surfaces. The correct conclusion was **hold (arm)**, not promotion.

### 4. ExECT Sparse Queues Are Useful for Diagnosis, Not Promotion

ExECT queues are smaller and more field-family-specific than Gan queues, so the gap is even sharper.

| Case | Fixture / residual queue | Broader behavior | Read |
| --- | --- | --- | --- |
| S2 comorbidity C0 | 6-doc replay +14.0pp F1, 2 doc fixes, 0 regressions | Cap-25 grid null at 85.7% across arms | Queue found a real surface issue, but not a cap-level signal. |
| S3 cause K0+K1 | 3-doc replay null | S3 full validation +11.1pp cause F1; S4 full validation +10.6pp cause F1 | Queue did not contain the cap/full trigger surface. |
| S4 cause K0+K1 | Not fixture-only; full validation pair | Cause F1 10.5% to 21.1%, pooled micro +0.3pp | Strong for sparse family guardrail, weak as broad-system evidence. |
| S4 medication G0 | Cap/full validation, not only fixture | MT precision +11.3pp and F1 +9.5pp full; unrelated families unchanged | Stronger promotion evidence because full split confirmed cap signal. |

Interpretation: ExECT fixtures should be treated as failure-mode labels and regression guards. Because support is sparse, promotion should require cap/full validation unless the change is purely non-scorer-facing contract cleanup.

### 5. Published Benchmark Reality Is a Separate Layer

The project still has two external-validity blockers:

- **Gan:** Local runs use `gan_2026_fixed_v1:validation` from the synthetic JSON subset. The published Real(300)/Real(150) setting uses real KCH letters and different annotation surfaces. The Gan audit explicitly says the real Excel letters and synthetic JSON corpus are not directly comparable.
- **ExECT:** Local S1/S4 results use repo-defined normalized field-family scorers. Published ExECT values are all-annotation, CUI/feature-aware per-item/per-letter metrics. The broad S4 local result is closer in spirit than S1, but it is not a published benchmark reproduction.

Therefore, this audit supports the language in `best_pipeline_benchmark_context_assessment_20260521.md`: current Gan is plausibly near category-level synthetic-validation competitiveness; current ExECT broad S4 remains below published broad-system performance; neither is a final real-set claim.

## Recommended Guardrail

Use the following evidence ladder for future fixture-derived work:

| Evidence type | Supports | Does not support |
| --- | --- | --- |
| Unit fixture / primitive case | Contract correctness, parser/bridge behavior, regression protection | Metric promotion, mechanism closure, benchmark claim |
| Residual qualitative queue | Failure-mode diagnosis, prereg justification, targeted regression check | Split-level expected gain |
| Cap-25 / cap-50 search | Arm ranking, proceed/reject/hold under fixed controls | Mechanism closure, external validity |
| Full validation | Operational promotion or freeze for that model/split/scorer | Published benchmark reproduction unless benchmark setting matches |
| Published real-set / CUI-aware reproduction | Benchmark-facing claim | Generalization to other clinical systems without additional validation |

Operational rule:

1. A fixture-only change may merge when it is a contract fix and scorer semantics are unchanged.
2. A scorer-facing or output-changing bridge may proceed from fixtures to cap-25, but should not promote from fixtures alone.
3. A cap-25 win needs full validation when support is sparse, when the change can regress other families, or when the claim is operational default.
4. Any claim involving Gan Real(300)/Real(150) or published ExECT all-family performance remains blocked until those benchmark conditions are actually reproduced.

## Failure-Mode Taxonomy Update

Use these tags in future inspections and fixture metadata:

| Tag | Meaning |
| --- | --- |
| `fixture_contract_only` | Pass/fail proves implementation behavior only. |
| `residual_enriched_queue` | Slice is enriched for known failures and not prevalence-representative. |
| `cap_prefix_signal` | Cap run is search evidence only. |
| `full_split_confirmed` | Full validation confirmed the direction under fixed controls. |
| `full_split_tradeoff` | Full validation confirmed gains but exposed paired regressions or family/category tradeoffs. |
| `external_validity_blocked` | Published real-set or CUI-aware benchmark condition is not yet available. |
| `annotation_policy_gap` | Failure may reflect benchmark annotation policy rather than clinical truth. |

## Kanban Decision

Mark the literature card **Done** with this interpretation:

- Fixture evidence is required for contract safety.
- Fixture evidence is insufficient for promotion except for strictly local, non-scorer-facing fixes.
- Residual queues should feed preregistration and error taxonomy, not replace cap/full validation.
- Real-set benchmark claims remain blocked by Gan real-letter access and ExECT CUI/all-family scorer alignment.

## Remaining Risk

The audit is documentation-only. It did not run new model calls or recompute artifact metrics. It relies on existing inspection docs and fixture manifests dated 2026-05-19 through 2026-05-21. If later runs change operational defaults, this audit should be refreshed by adding a short appendix rather than rewriting the guardrail.
