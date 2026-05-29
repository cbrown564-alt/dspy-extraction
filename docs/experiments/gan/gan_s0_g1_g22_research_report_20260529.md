# Gan S0 G1-G22 Research Report

Status: current synthesis
Date: 2026-05-29
Scope: Gan 2026 synthetic seizure-frequency extraction, G1 through G22
Builds on: `docs/experiments/gan/gan_s0_key_axes_progress_report_20260528.md`
Related active authorities: `docs/current_research_program.md`, `docs/component_ceiling_registry.md`, `docs/planning/kanban_plan.md`, `docs/experiments/gan/README.md`

## Research Question

What has the G1-G22 Gan S0 sequence shown about decomposing seizure-frequency
extraction into independently measurable components, and what remains blocked
before another target-selection or full-validation claim is justified?

The practical question is whether the project is now failing because it cannot
find answer candidates, cannot anchor or construct exact labels, or cannot
choose the correct benchmark-facing target when the note contains competing
signals.

## Executive Summary

G1-G22 show a consistent decomposition result: the system is strong at finding
possible answers, increasingly able to construct missing quantified-rate answer
options, and still weak at selecting the correct answer under benchmark-facing
special-label and competing-signal policy.

The strongest current synthetic paper-facing baseline remains builder-gap v1
GPT, rescored in G5 at 79.9% monthly under `gan2026_paper_reproduction`
on the full validation split. D1 v1.2b remains the mechanism baseline because
it exposes the structured date/event payload while scoring 76.6% paper monthly.
Neither is a published Gan benchmark reproduction because the project does not
have Real(300) or Real(150) reporting access and is using the synthetic
validation split.

The candidate inventory is not the primary broad failure. G1 found at least one
candidate for 299/299 validation records, exact-covered 278/299 gold labels,
and reached 292/299 Purist-equivalent and 295/299 Pragmatic-equivalent
coverage. G11 later showed that the locked exact-miss challenge remains 0/21
exact, but 14/21 Purist-equivalent and 17/21 Pragmatic-equivalent. That means
some exact labels need downstream temporal anchoring and aggregation rather
than a simple broader candidate builder.

The deterministic quantified-rate constructor introduced by G21 is a real
interface improvement, but only for answer-option coverage. Standard50 exact
option coverage rises from 41/50 raw to 45/50 combined, and the G11 exact-miss
challenge rises from 0/21 raw exact to 12/21 constructed exact. G21 does not
choose the final answer and does not solve duration, unknown/no-reference,
cluster flattening, or target selection.

Every model-backed selector arm after the early G2 slice has failed its
decision gate on the locked G6 standard50 mechanism surface. G8 scored 37/50
paper monthly, G10 scored 36/50, G15 scored 31/50, and G22 scored 39/50,
while builder-gap GPT scored 41/50 and D1 v1.2b scored 40/50 on the same rows.
G22 improved over the other selector variants and used closed options
correctly, but it still failed the 43/50 preregistered lift gate and regressed
on unknown/no-reference and seizure-free-versus-quantified overlays.

The key scientific conclusion is therefore negative but useful: target
selection is not solved by adding class labels, candidate rankings, explicit
support context, or closed answer-option IDs alone. The next selector needs a
new mechanism card tied to the G19/G17/G22 row ledger, not another rerun of the
G8, G10, G15, or G22 prompt/interface shapes.

## Method And Controls

Dataset and split:

- Dataset: Gan 2026 synthetic seizure-frequency labels.
- Split: `gan_2026_fixed_v1:validation`.
- Primary gold: `check__Seizure Frequency Number.seizure_frequency_number[0]`.
- Secondary label: `reference[0]` is a difficulty signal and cross-check only,
  not benchmark gold.

Scorer policy:

- Benchmark-facing Gan comparisons use `gan2026_paper_reproduction`.
- Canonical project diagnostics use `gan_frequency_deterministic_v1`.
- Reports that compare the two must state scorer mode explicitly because the
  paper-reproduction scorer and canonical clinical scorer differ on special
  labels, `multiple`, ranges, constants, and parser acceptance.
- G5, G8, G10, G15, G17, G19, and G22 all keep repair, range, and tolerance
  disabled for the paper-reproduction scorer unless explicitly noted.

Experimental controls:

- No G1-G22 synthesis claim changes scorer, loader, split, benchmark bridge, or
  gold-label semantics.
- No holdout tuning is involved.
- The G6 standard50 surface is challenge-balanced, not an unbiased validation
  sample.
- Full synthetic validation remains required before replacing an operational
  baseline.
- Real(300), Real(150), or a declared synthetic-only reporting protocol remains
  required for external Gan benchmark claims.

## Component Findings

### 1. Paper And Evaluation Surfaces

G5 created the paper-facing synthetic rescore surface. On full synthetic
validation, builder-gap v1 GPT scored 79.9% paper monthly, 85.3% Purist, and
88.0% Pragmatic. Builder-gap Qwen scored 70.2% paper monthly, and D1 v1.2b
scored 76.6% paper monthly. Canonical scores were close for builder-gap GPT and
Qwen, but D1 lost more under the paper scorer because seizure-free gold labels
were often predicted as `no seizure frequency reference`.

G6 fixed the local mechanism-comparison surface. The legacy 25-record enriched
slice became `gan_s0_g6_traceability_smoke_25`, suitable only for compatibility
and traceability. The default mechanism surface became
`gan_s0_g6_standard50_v1`, with named challenge overlays for target selection,
seizure-free versus quantified policy, unknown/no-reference policy, candidate
coverage, clusters, and temporal anchoring.

This prevents one-record or two-record changes on the old slice from being
treated as meaningful promotion evidence. On the 50-record surface, one record
is 2.0 percentage points and two records are 4.0 percentage points.

### 2. Frequency-Content Gate And Candidate Inventory

G1 showed that the deterministic candidate inventory is broad enough to support
decomposition. It emitted candidates for 299/299 validation records, exact
covered 278/299 labels, and reached 292/299 Purist-equivalent and 295/299
Pragmatic-equivalent coverage. Exact misses concentrated in quantified-rate,
seizure-free, and unknown-cluster cases.

G13 measured the isolated source-level frequency-content gate over the current
deterministic temporal candidate substrate. Overall gate accuracy was 244/299
(81.6%). Quantified-frequency recall was very high at 201/203 (99.0%), and
no-reference precision was 10/10, but unclear-frequency recall was only 10/40
(25.0%) and seizure-free recall was 23/45 (51.1%). The gate therefore creates
upstream caveats for later target-selection analysis: rows already misrouted
from unknown or seizure-free evidence into quantified-frequency presence should
not be blamed solely on selectors.

G18 closed a source-level candidate-interface defect rather than adding a
standalone report. The active runtime and G11 current rows now have 0 cases
where broad standalone abstentions such as `unknown` or
`no seizure frequency reference` are offered beside concrete frequency
candidates. The regression test
`test_temporal_candidates_drop_abstention_options_when_frequency_candidates_exist`
preserves that behavior. Older G1 rows remain provenance for the pre-pruning
surface.

### 3. Temporal Anchoring

G14 measured temporal anchoring without model calls. On standard50, exact
candidate coverage was 41/50 and temporal-slot coverage was 36/40 applicable
rows. On the `gan_s0_g6_temporal_anchoring` challenge set, exact coverage and
slot coverage were both 13/15. The two true temporal-slot misses were
`gan_16772` and `gan_16825`.

The result supports using the current temporal substrate as a diagnostic
baseline, but it does not justify expanding fragile arithmetic or broad
relative-anchor guardrails. Remaining exact misses should route to
aggregation-aware answer construction and target selection, not a broad prompt
loop.

### 4. Target Selection

G2 established the target-selection opportunity: a no-model
candidate-constrained oracle could support 299/299 validation records and reach
93.3% paper monthly and 94.0% canonical monthly. On the old enriched 25-record
slice, free adjudication scored only 16.0% paper monthly, while the
candidate-constrained and seeded reason-code/answer-option arms reached 92.0%.

The later standard50 selector arms did not reproduce that promise:

| Arm | Surface | Paper monthly | Canonical monthly | Decision |
| --- | --- | ---: | ---: | --- |
| Builder-gap GPT | standard50 comparator | 41/50 | 42/50 | promoted synthetic baseline |
| D1 v1.2b | standard50 comparator | 40/50 | 42/50 | mechanism baseline |
| G8 class-first selector | standard50 | 37/50 | 36/50 | rejected arm |
| G10 candidate-ranking selector | standard50 | 36/50 | 35/50 | rejected arm |
| G15 support-aware selector | standard50 | 31/50 | 30/50 | rejected arm |
| G22 closed-option selector | standard50 | 39/50 | 39/50 | rejected arm |

G4 had already shown why traceability alone is not enough. It preserved
selected-candidate references and label-construction inputs in 25/25 records,
with no deterministic-construction mismatches, but scored only 80.0% monthly on
the old enriched slice. All five misses were target-selection failures where
the arm chose seizure-free candidates despite gold-compatible quantified
candidates.

G8, G10, G15, and G22 are therefore arm rejections, not mechanism closure. The
target-selection mechanism remains open, but future work must account for the
G22 before/after ledger and avoid rerunning the same interface shapes.

### 5. Label Construction And Aggregation

G2 separated label construction from target selection and validated 1605/1605
candidate records with 0 invalid deterministic labels. G4 also showed no
construction mismatch on its slice.

G12 then clarified that raw answer options were not exact enough for the G6
exact-miss challenge. Raw options were 0/21 exact, 14/21 Purist-equivalent, and
17/21 Pragmatic-equivalent. The constructed aggregate view at that time was
also 0/21 exact. G10 was therefore authorized only as a category-level or
candidate-ranking selector, not as an exact closed-answer selector.

G16 defined the rate/duration aggregation policy. On the 21-row exact-miss
challenge, 14 rows needed quantified-rate aggregation with missing temporal
slots, 2 needed seizure-free duration policy, 4 were candidate-inventory gaps,
and 1 was outside rate/duration policy. On standard50, 41/50 already had exact
options, 4 were quantified-rate aggregation blocks, and 5 were outside the
rate/duration policy.

G20 preregistered a deterministic, fixture-first constructor. G21 implemented
`gan.frequency.aggregation_constructor.v1`. The constructor passed its gates:
standard50 combined exact option coverage rose from 41/50 to 45/50, and the
G11 exact-miss challenge reached 12/21 constructed exact with 0 deferred or
negative-control constructions. This is answer-option coverage only.

G22 then tested closed-option selection over the raw candidates plus G21
constructed options. It selected constructed options for two rows and copied
final labels from selected options in 50/50 records, but still scored only
39/50 paper monthly. That makes selection, not construction traceability, the
active bottleneck after G21.

### 6. Unknown, No-Reference, Seizure-Free, And Special Labels

G3 tested policy probes over the old 25-record G2 reason-code selector output.
Unknown/no-reference boundary, weak-rate-to-unknown, and seizure-free conflict
rules did not improve monthly accuracy. One prediction changed
(`gan_13123`, `1 per multiple months` -> `unknown`), reducing Pragmatic accuracy
from 100.0% to 96.0% while leaving monthly and Purist accuracy unchanged.

G5 scorer-mode forensics showed that the important special-label issue is not
a simple `unknown` versus `no seizure frequency reference` string problem. In
D1, all 14 canonical-only correct records were seizure-free gold labels
predicted as `no seizure frequency reference`. The paper scorer surfaces this
as a benchmark target-semantics problem.

G17 defined the active nine-row special-label policy slice:
`gan_6532`, `gan_9566`, `gan_5974`, `gan_6607`, `gan_6387`,
`gan_14002`, `gan_11380`, `gan_7894`, and `gan_8264`. The buckets include
unknown-cluster misrouted as concrete, unknown misrouted as concrete quantified
evidence, unknown misrouted as seizure-free evidence, unknown overcalled as
concrete despite a correct G13 gate, and seizure-free/no-reference scorer-mode
discordance. G17 found 0 deterministic repair candidates.

G22 failed specifically on this surface. Its unknown/no-reference overlay was
5/10, compared with 10/10 for builder-gap GPT and 9/10 for D1. Five G17 rows
that builder-gap GPT got right regressed under G22: `gan_9566`, `gan_5974`,
`gan_6607`, `gan_14002`, and `gan_11380`.

### 7. Evidence And Schema

Evidence and schema validity are not the current standard50 bottleneck. G4,
G8, G10, G15, and G22 all preserved important trace or option fields at high
rates, but wrong target semantics still produced wrong labels. Evidence and
schema should remain hard gates and diagnostics, not evidence that semantic
selection is solved.

## G1-G22 Card Ledger

| Card | Status | Main contribution | Claim boundary |
| --- | --- | --- | --- |
| G1 | diagnostic coverage gate | No-model candidate inventory: 299/299 records with candidates; 278/299 exact; 292/299 Purist-equivalent; 295/299 Pragmatic-equivalent. | Coverage evidence, not a model result or isolated ceiling. |
| G2 | oracle scaffold and diagnostic slice | No-model target/label split oracle reaches 93.3% paper monthly; same-slice candidate-constrained and seeded selector arms reach 92.0%. | Old enriched 25-record slice is diagnostic after G6. |
| G3 | negative policy probe | Unknown/no-reference and seizure-free conflict probes changed 1/25 record and did not improve monthly accuracy. | Does not authorize deterministic special-label repair. |
| G4 | diagnostic negative result | Explicit reason-code adjudicator preserved trace fields but fell to 80.0% monthly on old slice; five misses were target-selection failures. | Rejected as tested, not mechanism closure. |
| G5 | paper evidence and scorer forensics | Rescored baselines with `gan2026_paper_reproduction`: builder-gap GPT 79.9%, Qwen 70.2%, D1 76.6% monthly. | Synthetic-only paper-facing table; external benchmark claim blocked. |
| G6 | active evaluation protocol | Defined standard50 and challenge sets; old 25-record slice became smoke-only. | Protocol, not a performance result. |
| G7 | preregistration | Defined special-class target-selector protocol with fixed controls and G6-aligned stop rules. | Preregistration only. |
| G8 | rejected arm | Class-first target selector scored 37/50 paper monthly, below builder-gap GPT and D1. | Do not full-validate as tested. |
| G9 | routing decision | G8's 13 standard50 misses included four exact candidate-coverage misses: `gan_15997`, `gan_16772`, `gan_16825`, `gan_16335`. | Routed G11 before G10. |
| G10 | rejected arm | Candidate-ranking selector scored 36/50 paper monthly and regressed on unknown/no-reference. | Category-ranking arm rejected; exact construction still blocked. |
| G11 | coverage gate | Exact-miss challenge remained 0/21 exact, but 14/21 Purist-equivalent and 17/21 Pragmatic-equivalent; current rows differ from G1 because broad abstentions are pruned. | Not a simple candidate-builder defect. |
| G12 | answer-option decision | Raw options and constructed aggregate view were both 0/21 exact on locked exact-miss rows. | Authorized only narrowed G10 category/ranking claim. |
| G13 | isolated gate measured | Frequency-content gate accuracy 244/299; quantified recall 201/203; unclear-frequency and seizure-free recall weak. | Diagnostic baseline before selector attribution. |
| G14 | temporal component measured | Standard50 exact coverage 41/50 and temporal-slot coverage 36/40; temporal challenge 13/15 exact and slot-covered. | Do not expand broad arithmetic guardrails. |
| G15 | rejected arm | Support-aware selector scored 31/50 paper monthly despite support context in 50/50 rows. | Support metadata alone did not improve target selection. |
| G16 | aggregation policy defined | 14/21 exact-miss rows need quantified-rate aggregation; standard50 has four quantified-rate aggregation blocks. | Exact closed-option selector claims blocked until constructor or model mechanism. |
| G17 | special-label policy defined | Nine-row policy slice; 0 deterministic repair candidates. | Policy separation only, not a selector. |
| G18 | source-level cleanup complete | Current runtime has 0 rows where broad standalone abstentions are offered beside concrete frequency candidates; regression test preserves this. | No standalone report; use Kanban/test as provenance. |
| G19 | residual attribution audit | Across five arms, 65 paper-monthly misses across 29 unique rows; leading classes are aggregation blocks, unclear/special-label misrouting, seizure-free-over-quantified, and wrong quantified window. | Optimization queue, not new model evidence. |
| G20 | preregistration | Chose deterministic fixture-first quantified-rate constructor for G19/G16 aggregation rows. | Preregistration only. |
| G21 | constructor gate passed | Standard50 exact option coverage 41/50 -> 45/50; G11 0/21 -> 12/21 constructed exact; 0 negative-control constructions. | Answer-option coverage only, not selector performance. |
| G22 | rejected arm | Closed-option selector scored 39/50 paper monthly with complete option-copy traces, below 43/50 gate and builder-gap GPT 41/50. | Do not full-validate; use row ledger for next mechanism. |

## Interpretation

### Candidate search is largely adequate but not exact-complete

The evidence does not support another broad candidate-builder expansion as the
default next step. G1 and G11 show that the inventory often lands in the right
diagnostic neighborhood even when exact labels are absent. For quantified-rate
cases, G21 demonstrates that a narrow constructor can recover many exact answer
options without mutating raw candidates. Remaining exact failures are policy
specific: duration, unknown-cluster, inventory gaps, and cluster flattening need
their own mechanism cards.

### Target selection is the active bottleneck

G22 is the cleanest current proof. It fixed the interface problem by forcing
closed-option ID selection and copying final labels from selected options, but
it still failed to beat the promoted baseline. The model selected the wrong
available option on enough rows that better answer-option coverage did not
become better paper monthly performance.

### Special-label errors are semantic, not safe repair opportunities

G17 and G5 agree: seizure-free, unknown, unknown-cluster, and no-reference rows
cannot be collapsed into a binary abstention problem. They require evidence
interpretation and benchmark target semantics. The project should not add blind
post-hoc repair for these cases.

### Standard50 is useful for mechanism rejection but not baseline promotion

G8, G10, G15, and G22 are credible arm rejections because they use the same
G6 standard50 surface and fixed controls. But standard50 is challenge-balanced.
Even a selector that passes standard50 would still require full synthetic
validation before replacing builder-gap GPT or D1, and real-note or declared
synthetic-only protocol access before external benchmark claims.

## Limitations And Threats To Validity

- The report covers synthetic validation evidence only.
- Standard50 is intentionally challenge-balanced and should not be reported as
  unbiased validation performance.
- Full validation baseline values and standard50 values answer different
  questions and should not be mixed without their surfaces.
- G18 is represented by Kanban and regression-test provenance, not by a
  standalone Gan report file.
- Canonical Gan metrics are diagnostic. Benchmark-facing Gan tables should lead
  with `gan2026_paper_reproduction`.
- G21 construction coverage is not model selection performance.
- No current result establishes an isolated component ceiling for target
  selection.

## Current Research Status

| Component | Current status | Evidence |
| --- | --- | --- |
| Paper-comparison surface | synthetic paper-scorer surface available; external benchmark claim blocked | G5 |
| Evaluation protocol | active operational decision protocol | G6 |
| Frequency-content gate | measured diagnostic baseline; mechanism open | G13 |
| Candidate inventory | coverage gate measured; mechanism open | G1, G11, G18 |
| Temporal anchoring | diagnostic component measured; mechanism open | G14 |
| Target selection | mechanism open; multiple rejected prompt/interface arms | G2, G4, G8, G10, G15, G22 |
| Label construction and aggregation | quantified-rate constructor implemented; mechanism open | G12, G16, G20, G21 |
| Unknown/no-reference and special labels | policy defined; mechanism open | G3, G5, G17, G22 |
| Evidence and schema | diagnostic gates | G4, G8, G10, G15, G22 |

## Next Experiments

1. Write a new Gan selector mechanism card before any model call. It must cite
   a specific G19/G17/G22 failure class, preserve scorer/loader/split/bridge/
   candidate-builder/constructor/prediction-repair semantics, and include a
   before/after ledger for the affected rows.
2. Do not rerun the G8, G10, G15, or G22 prompt/interface shapes. They are
   rejected arms under fixed G6 controls.
3. For special labels, start from the nine-row G17 ledger and separate
   unknown, unknown-cluster, unclear-frequency-over-concrete, seizure-free, and
   no-reference scorer-mode discordance before reporting aggregate gains.
4. For construction, keep G21 as quantified-rate-only. Open separate policy
   cards for seizure-free duration aggregation, cluster flattening, or
   unknown-cluster handling before adding those transformations.
5. Any future selector that passes standard50 should then run full synthetic
   validation under `gan2026_paper_reproduction`, with canonical metrics
   reported only as diagnostics.

## Source Artifacts Used

- `docs/README.md`
- `docs/current_research_program.md`
- `docs/component_ceiling_registry.md`
- `docs/planning/kanban_plan.md`
- `docs/experiments/gan/README.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md`
- `docs/experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.md`
- `docs/experiments/gan/gan_s0_target_label_split_g2_report_20260528.md`
- `docs/experiments/gan/gan_s0_g2_model_arm_comparison_20260528.md`
- `docs/experiments/gan/gan_s0_g3_policy_probe_report.md`
- `docs/experiments/gan/gan_s0_g4_explicit_reason_code_adjudicator_report_20260528.md`
- `docs/experiments/gan/gan_s0_g5_paper_scorer_rescore_pack_20260528.md`
- `docs/experiments/gan/gan_s0_g5_scorer_mode_forensics_for_g4_20260528.md`
- `docs/experiments/gan/gan_s0_g6_evaluation_slice_standard_decision_20260528.md`
- `docs/experiments/gan/gan_s0_g7_special_class_target_selector_preregistration_20260528.md`
- `docs/experiments/gan/gan_s0_g8_special_class_target_selector_report_20260529.md`
- `docs/experiments/gan/gan_s0_g9_exact_miss_failure_inspection_20260529.md`
- `docs/experiments/gan/gan_s0_g10_candidate_ranking_target_selector_report_20260529.md`
- `docs/experiments/gan/gan_s0_g11_candidate_inventory_challenge_set_pass_20260529.md`
- `docs/experiments/gan/gan_s0_g12_answer_option_surface_20260529.md`
- `docs/experiments/gan/gan_s0_g13_frequency_content_gate_report_20260529.md`
- `docs/experiments/gan/gan_s0_g14_temporal_anchoring_report_20260529.md`
- `docs/experiments/gan/gan_s0_g15_support_aware_target_selector_report_20260529.md`
- `docs/experiments/gan/gan_s0_g16_aggregation_policy_20260529.md`
- `docs/experiments/gan/gan_s0_g17_unknown_no_reference_policy_20260529.md`
- `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.md`
- `docs/experiments/gan/gan_s0_g20_aggregation_constructor_preregistration_20260529.md`
- `docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.md`
- `docs/experiments/gan/gan_s0_g22_closed_option_target_selector_preregistration_20260529.md`
- `docs/experiments/gan/gan_s0_g22_closed_option_target_selector_report_20260529.md`
- `tests/test_gan_temporal_candidates.py`
