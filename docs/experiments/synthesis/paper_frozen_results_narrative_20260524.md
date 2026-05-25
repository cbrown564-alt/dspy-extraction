# Paper Frozen Results Narrative

Date: 2026-05-24  
Status: Frozen manuscript-facing results narrative  
Decision scope: Paper evidence freeze (Pathway D3); inherits metrics from D1, negative arms from D2

## Companion Artifacts

| Card | Document | Role |
| --- | --- | --- |
| D1 | [paper_frozen_operational_defaults_20260524.md](paper_frozen_operational_defaults_20260524.md) | Authoritative operational-default numbers and run IDs |
| D2 | [paper_frozen_arm_reject_table_20260524.md](paper_frozen_arm_reject_table_20260524.md) | Rejected arms with `decision_scope: arm` |
| Tables | [paper_result_table_pack_20260524.md](paper_result_table_pack_20260524.md) | Compact manuscript table pack |
| Synthesis | [core_research_questions_pipeline_review_20260524.md](core_research_questions_pipeline_review_20260524.md) | Three-axis interpretive frame |

---

## Thesis (Results Section Anchor)

On synthetic validation splits with frozen deterministic scorers, the project shows that **hybrid placement must follow task bottleneck shape**: Gan seizure-frequency extraction improves when deterministic code owns temporal candidate recall before LLM adjudication, while ExECT broad phenotyping remains primarily a benchmark-aligned LLM extraction problem with deterministic bridges and targeted post guards. Model choice is surface-dependent: GPT 4.1-mini leads on Gan monthly accuracy and ExECT S1 seizure-type policy alignment; Qwen3.6:35b transfers some surfaces but does not universalize hosted performance.

---

## Gan S0 Seizure Frequency

### Headline result (paper-frozen)

The operational Gan S0 default is **candidate-builder gap v1** with GPT 4.1-mini on `gan_2026_fixed_v1:validation` (299 records), scored with `gan_frequency_deterministic_v1`:

| Metric | Value | Run ID |
| --- | ---: | --- |
| Monthly accuracy | **80.6%** | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` |
| Purist category | 86.0% | same |
| Pragmatic category | 88.6% | same |
| Schema validity | 100.0% | same |
| Evidence support | 100.0% | same |

**Interpretation:** Deterministic temporal candidate builders that close documented recall gaps before LLM adjudication moved GPT monthly accuracy from the mid-60s (verify-repair and temporal-candidates eras) to 80.6%. The residual error map is now semantic adjudication and builder coverage, not missing temporal windows.

**Required caveats:** Synthetic validation only; not Gan Real(300)/Real(150) reproduction. Primary gold is `seizure_frequency_number[0]`; `reference[0]` is diagnostic. Monthly accuracy is the primary benchmark-facing metric; pragmatic category (88.6%) is supporting with an 8.0pp gap largely attributable to pragmatic-monthly divergence sub-patterns documented in Pathway C3.

### Local model transfer

Qwen3.6:35b on the same builder-gap surface scored **70.7%** monthly (297/299 valid-scored), **90.6%** pragmatic, run `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z`. This clears the preregistered local transfer gate but trails GPT by ~9.9pp monthly — a transfer success, not parity.

### Negative results (arm scope)

Pathway C closed prompt-only and optimizer arms without changing the operational default:

- **Unknown-overuse guard v1.5** collapsed to 16.0% monthly on cap-25 (Rule 1 over-extraction; no-candidate records inert).
- **Multi-stage GEPA G1/G2** regressed −16.0pp and −28.0pp monthly vs cap-25 G0 control.

These rejections support the claim that Gan S0 gains came from deterministic candidate infrastructure, not broad prompt addenda or optimizer substitution. See D2 Tier 1 and Tier 3.

---

## ExECT Schema Ladder (S1–S4)

GPT 4.1-mini full-validation micro F1 on the fixed 40-record ExECTv2 validation split shows **schema breadth pressure**:

| Level | Micro F1 | Notable family caveats |
| --- | ---: | --- |
| S1 | 92.3% | Diagnosis 93.8%, seizure type 90.5%, medication 92.8% |
| S2 | 80.9% | Comorbidity 69.3% |
| S3 | 72.1% | Sparse added families weak |
| S4 | 65.5% | Seizure frequency 45.7%, medication temporality 62.5% |

This is **not** a calibrated learning curve — each rung adds field families. The paper-safe claim is that broad multi-family extraction under benchmark policy is feasible on core S1 families but degrades as sparse and temporal families enter scope.

### Qwen replication pattern

Qwen matches or slightly exceeds GPT pooled micro on S2–S4 (+0.1 to +2.0pp) but **lags S1 by 13.3pp**, driven by seizure-type granularity (55.7% vs GPT 90.5%). Local deployment is viable on some frozen surfaces; fine-grained seizure typing still favors the hosted model on S1.

### Negative decomposition evidence

Section/family splitting, verify-repair second stages, static pre-vocabulary lists, and BootstrapFewShot optimizers failed arm gates on ExECT S1/S4 probes (D2 Tier 4). The winning S1 shape remains single broad extraction with inline benchmark bridges — not section-aware decomposition or optimizer substitution.

---

## ExECT S5 Core Surface

S5 scores five families on the same 40-record validation split: diagnosis, seizure type, annotated medication, investigation, and seizure frequency. Medication temporality is excluded (no native temporality column in prescription gold).

### Paper-frozen baseline (D1)

Program `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b`, run `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z`:

| Family | F1 |
| --- | ---: |
| Pooled micro | **85.8%** |
| Diagnosis | 90.0% |
| Seizure type | 84.0% |
| Annotated medication | **88.7%** |
| Investigation | 96.7% |
| Seizure frequency | **73.9%** |

Stack: high-recall pre-vocab frequency candidates → S5 extraction (v1.2 field-family prompt) → reject-only v2 frequency verifier (rules 7–9 temporal/scope + retained A3 rules 1–6) → AM guard (`am_guard_non_asm_brand_alias.v1`). Promoted 2026-05-24 per [exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md](../exect/exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md).

**Superseded anchors:**

| Run | Program | Micro | Freq F1 | Notes |
| --- | --- | ---: | ---: | --- |
| `...frequency_verify_full..._20260524T195813Z` | v1 verifier + A3 | 85.5% | 72.3% | Prior D1 default |
| `...am_guard_full..._20260524T182142Z` | AM guard only | 81.4% | 60.2% | Pre-verifier anchor |

### S5 negative arms (recent)

- **Combined v2** (v1.3 extractor + strict qualitative guard + v2 verifier) rejected at cap-25: recall −16.0pp; factor isolation → v2b isolates v2 verifier rules as the promotable gain.
- **High-precision candidate pruning** rejected: recall −12.0pp on cap-25 without precision gain — keep high-recall candidates.
- **Temporal medication guard (A4)** rejected: 100% precision but −20.7pp recall on cap-25 — brand/non-ASM guard stays promoted; temporal pruning deferred.

Seizure frequency remains the active S5 bottleneck despite verifier gains: residual errors are precision-dominated qualitative false positives. Full-validation recall is 79.1% (unchanged vs v1 promotion); high-recall candidate injection is retained pre-verifier.

---

## Cross-Dataset Comparison (Methods-Results Bridge)

| Dimension | Gan S0 | ExECT S1/S4/S5 |
| --- | --- | --- |
| Primary bottleneck | Temporal candidate recall → semantic adjudication | Benchmark policy alignment + sparse/temporal families |
| Best deterministic placement | **Pre-LLM** candidate builders | **Post-LLM** benchmark bridges; selective post guards |
| Best LLM role | Adjudicate among injected candidates | Broad extraction with policy during pass |
| Rejected default moves | Prompt-only unknown repair; GEPA policy walls | Section split; static pre-vocab; broad verify-repair |
| Model transfer | Qwen −9.9pp monthly vs GPT on builder-gap | Qwen competitive S2–S4; weak S1 seizure typing |

This supports the hybrid-pipeline pivot thesis: identical doctrine (decompose, place determinism deliberately, test one factor at a time) yields **different winning graphs** because datasets encode different failure modes.

---

## Claim Readiness Matrix

| Claim | Status | Manuscript discipline |
| --- | --- | --- |
| Builder-gap v1 is best internal Gan S0 surface on synthetic validation | **Supported** | Cite split, scorer, run ID; deny Real benchmark parity |
| Deterministic pre-candidates materially improve Gan vs mid-60s era | **Supported** | Historical anchors in paper_result_table_pack Table 2 |
| ExECT S1 GPT v4_10 + bridges is frozen narrow-family anchor | **Supported** | Not CUI-aware Table 1 reproduction |
| Schema breadth increases difficulty S1→S4 | **Supported with caveat** | Field-family scope changes each rung |
| Qwen transfers Gan builder-gap; not hosted parity | **Supported** | Report 297 valid-scored denominator |
| Qwen viable on some ExECT surfaces, not universal | **Supported** | Emphasize S1 seizure-type gap |
| S5 paper-frozen stack (v2b verifier) | **Supported** | D1 operational default; cite v2b promotion review + run ID |
| S5 frequency verifier reaches 73.9% F1 full validation | **Supported** | Paper-frozen 2026-05-24; +1.6pp vs superseded v1; not Gan monthly metric |
| S5 medication guard repairs annotated_medication F1 | **Supported** | Component of promoted D1 stack; temporality still open |
| High-precision freq candidates or temporal med guard should be defaults | **Rejected (arm)** | D2 Tier 1 |
| Project beats published ExECT/Gan benchmarks | **Unsupported / blocked** | Real data + CUI-aware scorer gates |
| DSPy optimizers replace hand-designed policy | **Rejected as tested** | Arm-level; mechanism class open |

---

## Suggested Manuscript Structure

### Results — Gan

1. Operational default table (D1 §1 or paper_result_table_pack Table 1).
2. Architecture history paragraph (mid-60s → 80.6% narrative; Table 2).
3. Residual taxonomy summary (Pathway C1/C3): semantic mismatch, pragmatic-monthly divergence.
4. Negative results paragraph citing D2 Tier 1 Gan rows.

### Results — ExECT

1. Schema ladder table (D1 §2 or Table 3).
2. Qwen replication table (D1 §3 or Table 4) with S1 caveat.
3. S5 subsection: promoted v2b verifier stack (85.8% micro, 73.9% freq) + residual frequency errors + superseded v1 (72.3%) and AM-guard-only (60.2%) anchors as historical comparison.
4. Negative decomposition paragraph citing D2 Tier 4.

### Discussion hooks

- Task-dependent hybrid placement (pre vs post determinism).
- Arm-vs-mechanism discipline as methodological contribution.
- Synthetic validation ceiling and blocked benchmark reproduction.
- Local model deployment tradeoffs (privacy vs policy-alignment tasks).

---

## Remaining Risks Before Submission

1. **S5 frequency residual iteration:** Verifier stack is paper-frozen at 73.9% F1 (v2b); combined v2 rejected; further gains need preregistered arms (not candidate narrowing).
2. **Registry staleness:** Verify headline rows against `metrics.json` at copy-edit time (noted in paper_synthesis_update).
3. **Cap-25 optimism:** ExECT cap-25 systematically optimistic (~+3.5pp vs full on S1); never mix scopes in one table without annotation.
4. **Evidence support:** Diagnostic grounding metric, not human evidence quality.
5. **No test/holdout spend:** D4 protocol not activated; all numbers are validation split only.
