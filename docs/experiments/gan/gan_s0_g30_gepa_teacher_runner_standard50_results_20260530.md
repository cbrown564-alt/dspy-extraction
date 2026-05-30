# Gan S0 G30 GEPA Teacher-Runner Standard50 Results

Status: current synthesis / rejected arm / mechanism open
Date: 2026-05-30
Preregistration: `gan_s0_g30_gepa_teacher_runner_preregistration_20260530.md`
Smoke gate: `gan_s0_g30_gepa_teacher_runner_smoke_results_20260530.md`

## Research Question

After the hosted teacher-runner smoke gate, can GEPA over the G27/G24
evidence-first target selector use GPT-4.1-mini prediction plus GPT-5.5
reflection to clear the G25 standard50 mechanism gate without changing scorer,
loader, split, benchmark bridge, candidate-builder, constructor, prompt
version, gold policy, or prediction-repair semantics?

## Method

- Dataset and split: Gan 2026 synthetic, `gan_2026_fixed_v1:validation`.
- Evaluation surface: `gan_s0_g6_standard50_v1`.
- Gold label: `seizure_frequency_number[0]`; `reference` remains secondary.
- Program variant: `gan_frequency_s0_evidence_first_target_selector`.
- Prediction model config: `configs/models/gan_s0_gpt4_1_mini.json`.
- Reflection model config: `configs/models/gan_s0_gpt5_5_openai.json`.
- Optimizer: GEPA with `trainset_size=16`, `max_metric_calls=80`,
  `reflection_minibatch_size=4`, Pareto candidate selection, and
  `gan_s0_stage_attributed_frequency_feedback`.
- Primary scorer: `gan2026_paper_reproduction`; canonical Gan metrics remain
  diagnostic only.
- Config:
  `configs/experiments/gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_standard50.json`.
- Run:
  `gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_standard50_20260530T203349Z`.

## Optimization Behavior

GEPA exercised the larger budget and accepted reflected candidates:

| Optimization item | Value |
| --- | ---: |
| Metric-call budget | 80 |
| `gepa_state.bin` total evaluations | 80 |
| Full train/val evaluations | 3 |
| Program candidates | 3 |
| Base train/val score | 10.25/16 (64.1%) |
| Candidate 1 score | 10.65/16 (66.6%) |
| Candidate 2 score | 11.1/16 (69.4%) |
| Final instruction length | 14,639 chars / 221 lines |
| Compile duration | 403.7 seconds |
| Prediction duration | 114.8 seconds |
| Total run duration | 518.6 seconds |
| Run-level token usage | 487,720 total tokens |

This is a real optimizer-capacity signal: the reflection model was used, GEPA
found accepted candidates on the 16-record compile set, and the final candidate
improved the compile objective. The accepted instruction also expanded into a
large policy wall, which was a preregistered risk from R14 and the G30 smoke.

## Standard50 Results

The preregistered standard50 gate is 43/50 paper monthly, or a preregistered
row-ledger exception with no special-label regression. G30 did not clear it.

| Arm | Monthly | Purist | Pragmatic | Schema | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: |
| G24/G28 uncompiled evidence-first standard50 | 44/50 | 44/50 | 45/50 | 50/50 | 44/44 among present quotes |
| G30 GEPA teacher-runner standard50 | 41/50 | 42/50 | 43/50 | 50/50 | 44/44 among present quotes |

G30 missed the 43/50 gate by two records and finished three records below the
uncompiled G24/G28 standard50 result on the same locked surface. Missing
prediction evidence remained 6/50, while support among present evidence quotes
remained 44/44.

## Row Movement Versus G24

| Movement | Records | Detail |
| --- | --- | --- |
| Fixes | 2 | `gan_12679` fixed from `1 to 2 per month` to `1 per day`; `gan_6607` fixed from `no seizure frequency reference` to `unknown`. |
| Regressions | 4 | `gan_12950` regressed from `7 per 3 month` to `1 per 2 to 3 week`; `gan_13123` from `1 per year` to `unknown`; `gan_15306` from `2 to 3 per 15 month` to `seizure free for multiple month`; `gan_16041` from monthly-correct `3 per month` to `9 per 2 month`. |
| Shared misses | 5 | `gan_11380`, `gan_14485`, `gan_14881`, `gan_5974`, and `gan_9566` remained monthly misses. |
| Shared hits | 39 | No monthly-category change. |

The G17 special-label slice improved from 5/9 to 6/9 because `gan_6607` moved
to `unknown`, but G30 still missed `gan_9566`, `gan_5974`, and `gan_11380`.
That special-label improvement is not enough to offset the four standard50
regressions.

## Interpretation

G30 is rejected as tested.

The optimizer had enough capacity to exercise reflection and improve its
compile-set objective, but the accepted instruction did not generalize to the
locked standard50 mechanism slice. The result is worse than the uncompiled
G24/G28 selector and below the G25 obvious-pass gate, with no clean row-ledger
exception because the net row movement is negative.

Decision scope: arm. This does not close GEPA as a mechanism, because only one
teacher-runner position and prompt surface were tested at standard50 scale.

## Caveats

- Standard50 is a mechanism-comparison surface, not an unbiased validation
  estimate or promotion surface.
- GEPA used the trainset as valset during compilation because no separate
  valset was configured; this is acceptable for this arm-level capacity test
  but weakens generalization claims.
- Runtime `estimated_model_calls` undercounts GEPA activity because the runner
  records a simple trainset-plus-prediction estimate; use GEPA state
  `total_num_evals=80` plus token history for optimizer-capacity reporting.
- Token usage is captured at run level, not split by prediction versus
  reflection model.
- Frozen-test rows were not used for prompt wording, candidate surfaces,
  scorer changes, bridge changes, repair changes, or policy tuning.

## Decision

Do not full-validate this G30 arm. Do not run Qwen GEPA from this arm. Do not
inspect or tune from frozen-test rows. Any future GEPA work needs a new compact
or stripped-prompt mechanism card with its own standard50 gate and row ledger,
rather than scaling this policy-wall instruction.
