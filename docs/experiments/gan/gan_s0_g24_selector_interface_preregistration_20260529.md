# Gan S0 G24 Selector Interface Reframing Preregistration

Status: preregistered mechanism card
Date: 2026-05-29
Kanban card: G24 - Gan Selector Interface Reframing Preregistration
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Primary surface: `gan_s0_g6_standard50_v1`
Primary scorer: `gan2026_paper_reproduction` monthly-frequency match, with
repair, range, and tolerance disabled
Diagnostic scorer: `gan_frequency_deterministic_v1` canonical monthly-frequency
match
Model/provider plan: GPT-4.1-mini / OpenAI for the first cap5 and standard50
execution; Qwen3.6:35b remains blocked until the GPT standard50 row ledger
satisfies the G25 gate.

## Research Question

Can an evidence-first selector interface reduce Gan S0 target-selection errors
that persisted under closed-option ID selection, especially forced special-label
misses and constructed-option deprioritization, while preserving the fixed
scorer, loader, split, benchmark bridge, candidate-builder, G21 constructor, and
prediction-repair semantics?

## Hypothesis

Evidence-first target narration with constrained final output will outperform
closed-option ID selection alone on the G23 failure surface. The expected gain
is not generic prompt polish; it should appear in the preregistered row ledger:

- fewer forced concrete choices on G17 unknown rows where the closed option list
  is inadequate;
- better priority for G21 constructed exact options when they compete with raw
  narrower-window options;
- no new regression on G17 special-label rows that builder-gap GPT already gets
  correct;
- no loss of trace completeness compared with G22.

## Mechanism

The next program variant should be implemented as
`gan_frequency_s0_evidence_first_target_selector`, prompt version
`gan_frequency_s0_evidence_first_target_selector_v1_0`.

The model receives the same core context as G22:

- the full note text;
- raw deterministic temporal candidates;
- prediction-time constructed quantified-rate options from
  `gan.frequency.aggregation_constructor.v1`;
- option IDs, option source, label family, and evidence/support metadata.

The varied factor is the model-facing target-selection interface. Instead of
asking the model to choose an option ID first, the prompt must require:

1. evidence-first target narration before option ranking;
2. an explicit closed-option adequacy decision;
3. construction-aware priority when a G21 constructed option summarizes the
   benchmark target better than a raw narrower-window candidate;
4. selected option ID and copied final label when an adequate option exists;
5. a constrained special-label escape only when no closed option can support a
   valid Gan benchmark label.

This is a composite interface mechanism derived from G23. If it succeeds, later
ablations may separate evidence-first narration, special-label escape, and
construction-aware priority. G24 itself tests the combined interface because
G22 failed through the interaction of those constraints.

## Prediction Contract

Every prediction must expose these trace fields:

- `evidence_first_target_narration`;
- `closed_option_adequacy` with values equivalent to `adequate` or
  `inadequate`;
- `selected_option_id` when `closed_option_adequacy` is `adequate`;
- `selected_option_label`, copied exactly from the selected option;
- `construction_priority_reason` when a constructed option is present;
- `special_label_escape` when `closed_option_adequacy` is `inadequate`;
- `special_label_escape_reason`;
- `final_label`;
- `final_label_source`, one of `selected_closed_option` or
  `constrained_special_label_escape`.

When an option is adequate, the final label must be copied from the selected
option. When no option is adequate, the final label may only be one of the
explicitly allowed special-label escapes:

- `unknown`;
- `no seizure frequency reference`.

G24 does not authorize free-written quantified rates, duration repairs, cluster
flattening, or invented `unknown, <n> per cluster` labels outside the closed
option list. Unknown-cluster rows remain separate policy rows: if an adequate
unknown-cluster option exists, select it; if it does not, classify the row in
the ledger rather than repairing it after prediction.

## Fixed Controls

- Dataset loader: unchanged Gan 2026 loader.
- Split: `gan_2026_fixed_v1:validation`; G6 standard50 record IDs.
- Gold source: `seizure_frequency_number[0]`.
- Reference policy: `reference[0]` remains a secondary difficulty signal only.
- Primary scorer: `gan2026_paper_reproduction`; repair/range/tolerance disabled.
- Diagnostic scorer: canonical `gan_frequency_deterministic_v1`.
- Candidate builder: current deterministic temporal candidate substrate.
- Constructor: `gan.frequency.aggregation_constructor.v1`; no mutation of raw
  candidate records.
- Benchmark bridge and normalization policy: unchanged.
- Prediction repair: none beyond selected-option label copy or the constrained
  special-label escape named above.
- Few-shot policy: none.
- Test split: unavailable for tuning and blocked from selector wording changes.

## Taxonomy And Reproducibility Fields

- Clinical task family: Gan seizure frequency.
- Component/stage: scope and benchmark target selection.
- Schema complexity: `gan_s0`.
- Program architecture: evidence-first target selector.
- Hybrid balance class: deterministic candidates and constructed options before
  LLM adjudication; LLM-constrained target selection; deterministic scoring
  after prediction.
- Interleaving positions: `pre`, `during`, `post`, `eval_only`.
- Varied factor: target-selection interface.
- Comparison group: G22 closed-option selector plus builder-gap GPT, D1 v1.2b,
  G8, G10, and G15 standard50 ledgers.
- Intended decision: whether the G24 interface merits full-validation
  expenditure under the G25 gate.
- Decision scope if run succeeds or fails: arm, not mechanism closure.

Expected execution configs, when the implementation card is pulled:

- `configs/experiments/gan_s0_g24_evidence_first_target_selector_gpt4_1_mini_cap5.json`
- `configs/experiments/gan_s0_g24_evidence_first_target_selector_gpt4_1_mini_standard50.json`

These configs are not created by this preregistration. They should be emitted
with a taxonomy block before model calls.

## Required Smoke Gate

Before standard50, run a cap5 smoke over:

| Record | Reason for inclusion |
| --- | --- |
| `gan_9566` | G17 unknown row where G22 was forced into a concrete quantified choice. |
| `gan_15997` | G21 constructed exact option that G22 selected correctly; must not regress. |
| `gan_16772` | G21 constructed exact option present but G22 selected a raw narrower-window option. |
| `gan_3246` | Exact option available but G22 flattened a cluster target to a simple rate. |
| `gan_6387` | Special-label row with an exact `unknown` option already available. |

The cap5 smoke passes only if:

- predictions exist for all five records;
- closed answer options and constructed option traces are present;
- all required G24 trace fields are present;
- final labels are copied from selected options or from the constrained
  special-label escape set;
- no free-written quantified label appears outside the option list;
- at least one constructed-option row records a construction-priority reason;
- at least one inadequate-option row uses or rejects the special-label escape
  with an explicit reason.

Cap5 metrics are traceability diagnostics only. Do not interpret cap5 accuracy
as performance evidence.

## Standard50 Run

Run the standard50 execution only after the cap5 trace gate clears.

Compare G24 against:

- builder-gap GPT;
- D1 v1.2b schema guard;
- G8 class-first selector;
- G10 candidate-ranking selector;
- G15 support-aware selector;
- G22 closed-option selector.

The standard50 report must lead with `gan2026_paper_reproduction` monthly
accuracy and report canonical `gan_frequency_deterministic_v1` as diagnostic
sensitivity. Raw exact string match remains diagnostic only.

## Row-Level Ledger Contract

The G24 report must include a before/after ledger keyed by `record_id` with:

- gold label;
- reference label as difficulty context;
- G19 failure class or `none`;
- G17 bucket when applicable;
- raw option labels;
- constructed option labels;
- G21 constructed-exact flag;
- G22 selected option and correctness;
- G24 closed-option adequacy decision;
- G24 selected option ID, source, family, and label when used;
- G24 special-label escape state and reason when used;
- G24 final label and final-label source;
- builder-gap, D1, G8, G10, G15, G22, and G24 paper-monthly correctness;
- canonical diagnostic correctness;
- improvement/regression tags against builder-gap GPT and G22;
- whether a constructed exact option was available but not selected;
- whether an escape was used on a row that had an exact closed option available.

The ledger must keep these targeted row groups separate:

| Row group | Record IDs | Required interpretation |
| --- | --- | --- |
| G17 special-label slice | `gan_6532`, `gan_9566`, `gan_5974`, `gan_6607`, `gan_6387`, `gan_14002`, `gan_11380`, `gan_7894`, `gan_8264` | Do not collapse into a binary `unknown` vs no-reference score. Report unclear-frequency, unknown-cluster, seizure-free/no-reference discordance, and concrete overcall buckets separately. |
| G22 forced unknown misses | `gan_9566`, `gan_5974`, `gan_6607`, `gan_14002`, `gan_11380` | Primary special-label escape target. These must improve or remain explicitly explained for a near-baseline exception. |
| G21 standard50 constructed rows | `gan_15997`, `gan_16772`, `gan_16825`, `gan_16335` | Preserve G22 successes on `gan_15997` and `gan_16335`; test construction-aware priority on `gan_16772` and `gan_16825`. |
| G22 exact-available wrong choices | `gan_3246`, `gan_10398`, `gan_12679`, `gan_16041`, `gan_16772`, `gan_16825` | Main target-selection and option-priority surface. |
| Scorer-mode caveats | `gan_7894`, `gan_8264` | Report paper and canonical views separately; do not repair predictions after the fact. |

## G25 Run-Scope Gate

Standard50 remains a mechanism surface, not a promotion surface. Apply the G25
gate before any full-validation, Qwen, or frozen-test spend:

1. Trace completeness is required before metrics are interpreted.
2. If G24 reaches at least 43/50 paper monthly on standard50 and has clean
   targeted overlays, authorize a full-validation GPT run.
3. If G24 scores 39-42/50, authorize full validation only if the preregistered
   ledger shows a clean mechanism gain: more targeted fixes than regressions on
   the G17/G21/G22/G23 rows, no new G17 special-label regression against
   builder-gap GPT, and no unaccounted schema/evidence failures.
4. If G24 scores below 39/50, block ordinary full validation. G24 does not
   preregister a generalization exception for a below-39/50 result.
5. Do not run Qwen until the GPT standard50 ledger satisfies the G25 gate and a
   model-effect hypothesis is written.
6. Do not inspect frozen test until after a full-validation result is frozen;
   test rows are residual-analysis evidence only and must not change prompt
   wording, candidate policy, scorer policy, or repair policy.

## Stop Rules

Reject the G24 arm as tested if any of the following occurs:

- cap5 trace fields are incomplete;
- final labels include unapproved free-written quantified labels;
- standard50 repeats the G22 special-label forced-choice regression pattern;
- the arm regresses more G17 rows than it fixes;
- the arm uses special-label escape on rows with adequate exact closed options
  without an explicit row-level justification;
- standard50 is below 39/50 and no preregistered generalization exception exists.

Classify any rejection as a rejected arm, not closure of Gan S0 target
selection.

## Non-Goals

G24 does not:

- change scorer semantics;
- change splits, loaders, or gold-label policy;
- change the deterministic temporal candidate builder;
- change `gan.frequency.aggregation_constructor.v1`;
- add duration aggregation, cluster flattening, or unknown-cluster construction;
- tune from frozen test rows;
- authorize Qwen replication or full-validation/test residual checks by itself.

## Source Artifacts

- `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.md`
- `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.json`
- `docs/experiments/gan/gan_s0_g17_unknown_no_reference_policy_20260529.md`
- `docs/experiments/gan/gan_s0_g17_unknown_no_reference_policy_20260529.json`
- `docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.md`
- `docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.json`
- `docs/experiments/gan/gan_s0_g22_closed_option_target_selector_preregistration_20260529.md`
- `docs/experiments/gan/gan_s0_g22_closed_option_target_selector_report_20260529.md`
- `docs/experiments/gan/gan_s0_g22_closed_option_target_selector_report_20260529.json`
- `docs/experiments/gan/gan_s0_g23_selector_failure_mechanism_audit_20260529.md`
- `docs/experiments/gan/gan_s0_g25_selector_generalization_audit_20260529.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
- `docs/taxonomy/taxonomy_primitive_catalog.md`

## Decision

G24 is complete as a preregistration card. It authorizes the next implementation
and execution card to build the evidence-first GPT-4.1-mini cap5 and standard50
selector arm under the fixed controls above.

It does not authorize full validation, Qwen replication, or frozen-test residual
inspection until the standard50 run satisfies the G25 gate.
