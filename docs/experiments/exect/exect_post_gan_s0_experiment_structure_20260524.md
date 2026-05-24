# ExECT Post-Gan S0 Experiment Structure

Date: 2026-05-24  
Status: Planning synthesis after Gan G11-G21 candidate-builder lift  
Decision scope: experiment-structure proposal; no scorer, loader, or prompt semantics changed

## Purpose

Gan S0 improved because the experiment loop stopped treating model prompts as the first lever and instead isolated a concrete upstream bottleneck: deterministic candidate recall. This note captures that loop and defines a similar ExECT structure, first for S1, then S4, with S2/S3 held as fill-in ladder work only if the S1/S4 surfaces show real progress.

This plan follows the ExECT gold audit and current hybrid doctrine:

- ExECT local field-family scores are partial diagnostic views, not published ExECTv2 Table 1 reproduction.
- Benchmark-facing outputs must remain separate from clinically richer extraction.
- Cap-25 runs are search/ranking gates, not mechanism closure.
- Pooled micro F1 is not comparable across schema breadth; S1, S2, S3, and S4 need per-family reporting.

## What Worked In Gan G11-G21

| Step | Gan artifact | What made it useful | ExECT translation |
| --- | --- | --- | --- |
| G11 no-model audit | `gan_s0_candidate_builder_gap_audit_20260523.md` | Measured whether gold labels were present in candidates before spending model calls. Found 23/25 exact gold coverage after inspection target was understood. | Start S1/S4 with no-model gold/support audits: "can the existing bridge/candidate surface represent the gold label?" |
| G12 preregistration | `gan_s0_candidate_builder_gap_preregistration_20260523.md` | One varied factor: deterministic candidate-builder implementation. Explicit included/excluded families and no scorer changes. | Each ExECT family intervention needs one varied factor, acceptance gates, and excluded patterns before code or runs. |
| No-model validation | candidate-builder tests + audit script | Proved the implementation moved the intended substrate before running GPT. | Require fixture coverage and candidate/gold representability checks for S1 seizure/diagnosis and S4 frequency/medication. |
| G15 slice model gate | `gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md` | Same model, prompt, scorer, and records as control; candidate implementation only varied. Large slice lift justified full validation. | Use enriched ExECT residual slices for S1 and S4, but do not treat slice lift as full-validation performance. |
| G16-G18 reconciliation | preservation + verified rerun docs | Detected stale/runtime mismatch before promotion. Re-ran and verified emitted candidate metadata in full validation. | ExECT plans must include runtime metadata checks: bridge mode, candidate lists, prompt version, schema level, and scorer mode. |
| G19-G21 promotion and transfer | promotion review + Qwen prereg/inspection | Promotion was separate from inspection; Qwen transfer had separate gates and denominator caveats. | Promote ExECT defaults only after a separate review. Treat Qwen/Gemini/Claude as model-profile or transfer arms, not automatic defaults. |

The important pattern is not "add more deterministic code." It is:

1. audit the bottleneck without a model,
2. preregister one implementation change,
3. test no-model substrate movement,
4. run a controlled slice,
5. verify full-validation runtime behavior,
6. promote only after a separate review,
7. port to other models only under a separate transfer question.

## ExECT Field Ladder Reference

Current implemented field-family ladder:

| Level | Implemented schema / scorer | Field families currently scored | Audit / caveat |
| --- | --- | --- | --- |
| S0 | Historical/core diagnostic concept; implemented together with S1 as `exect_s0_s1_field_family` | Core diagnostic fields only, effectively the diagnostic portion of S1: `diagnosis`, `seizure_type` | In current code S0 is not a separate scorer surface; S0/S1 share the field-family implementation. |
| S1 | `exect_s0_s1_field_family` / `exect_field_family_deterministic_v1` | `diagnosis`, `seizure_type`, `annotated_medication` | Benchmark-facing labels only; medication temporality is intentionally not scored here. |
| S2 | `exect_s2_field_family` / `exect_s2_field_family_deterministic_v1` | S1 + `investigation`, `comorbidity` | Investigation uses modality+result labels; comorbidity excludes seizure-history phrases. |
| S3 | `exect_s3_field_family` / `exect_s3_field_family_deterministic_v1` | S2 + `birth_history`, `onset`, `epilepsy_cause`, `when_diagnosed` | Implemented S3 is the auditable JSON-entity phase, not the full outline list of family/social/driving/pregnancy. |
| S4 | `exect_s4_field_family` / `exect_s4_field_family_deterministic_v1` | S3 + `seizure_frequency`, `medication_temporality` | Frequency is ExECT annotation-surface scoring, not Gan monthly scoring; medication temporality is inferred from prescription span text. |
| S5 proposal | Not implemented | `diagnosis`, `seizure_type`, `annotated_medication`, `investigation`, `seizure_frequency` | Proposed below: a support-qualified, claim-ready core surface focused on the key variables with enough evidence/gold support. |

## Proposed S5: Gold-Sufficient Key Variables

S5 should not mean "more fields than S4." It should mean "the subset of clinically and research-important variables with enough gold support and scorer stability to sustain paper claims."

Proposed inclusion gates:

| Gate | Requirement |
| --- | --- |
| Gold support | At least 20 validation gold labels, or a preregistered reason to keep a sparse but clinically central field. |
| Gold source clarity | Audit identifies a reliable source column/entity and no unresolved source mismatch that changes label meaning. |
| Scorer stability | Deterministic normalization policy is documented and has regression tests. |
| Evidence support | Prediction artifacts retain quote evidence; evidence metrics are reported diagnostically. |
| Family value | Field is clinically/research meaningful for the paper, not just available in JSON. |

S5 field definition:

| Include? | Family | Reason |
| --- | --- | --- |
| Yes | `diagnosis` | High support, near-ceiling, important benchmark-facing core. |
| Yes | `seizure_type` | High support and central; residual Qwen/GPT gaps remain scientifically useful. |
| Yes | `annotated_medication` | High support; scope caveat is well understood. |
| Yes | `investigation` | Good support and stable modality+result scorer after guards. |
| Yes | `seizure_frequency` | Clinically central, enough support, and the clearest ExECT analogue to the Gan decomposition/candidate-adjudication success. |
| No for S5 | `comorbidity` | Useful but overlap/surface policy remains noisy enough to keep it outside the core research surface. |
| No for S5 | `medication_temporality` | Remains S4-only because gold is inferred from prescription spans and precision failures are prominent. |
| Defer | `birth_history`, `onset`, `epilepsy_cause`, `when_diagnosed` | Sparse support and annotation-surface instability; useful for diagnostics but weak for headline claims without a policy decision. |

## ExECT S1 Structure

S1 should be first because it is narrow, high-support, and already has a strong GPT anchor (`92.3%` micro F1 on validation). The main open problem is not broad architecture; it is whether residual errors can be made measurable enough to improve without disturbing the near-ceiling default.

### S1 Current Anchors

| Surface | Anchor |
| --- | --- |
| GPT default | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`, v4.10 + inline bridges, 92.3% micro |
| Qwen 35b default | `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z`, 79.0% micro |
| Known bridge effect | Raw L1 68.6% vs bridged 92.3% full in interleaving v2 |
| Known rejected arms | Broad/full-note pre-vocab, medication-only pre-vocab, seizure-only pre-vocab, v4.12 Qwen prompt arm |

### S1-G1: Residual Representability Audit

Question: for S1 residuals, are false negatives caused by the model not emitting a label, by bridge inability to represent the label, or by label-policy mismatch?

Controls:

- Dataset/split: `exectv2_fixed_v1:validation`
- Scorer: `exect_field_family_deterministic_v1`
- Baseline run: GPT v4.10 full plus Qwen S1 full for model-gap comparison
- No model calls

Outputs:

- Residual table by family: diagnosis, seizure_type, annotated_medication
- For each residual: gold label, prediction, evidence, bridge representability, policy boundary tag
- Candidate residual slice for model gate, analogous to Gan enriched 25-record slice

Acceptance to proceed:

- At least one family has a concrete, recurring representability or policy bottleneck affecting 5+ validation errors.
- The proposed fix can be expressed without scorer semantic changes.

Likely high-value S1 targets:

| Target | Why |
| --- | --- |
| Qwen seizure-type gap | Largest S1 model gap; prior v4.11/v4.12 prompt tradeoff shows the issue is real but not solved. |
| Diagnosis recall misses | GPT near ceiling but residual diagnosis FNs may be amenable to narrow recall pass or co-list audit. |
| Medication scope | Already high on S1; only target if residual audit finds repeated audited prescription misses rather than planned/current ambiguity. |

### S1-G2: Preregister One Narrow Intervention

Do this only after S1-G1 identifies a bottleneck. Candidate comparison groups:

| Candidate group | Primary varied factor | Decision rule |
| --- | --- | --- |
| `exect_s1_seizure_surface_repair_gpt_cap25_v1` | post bridge implementation for audited seizure surfaces only | Promote to full only if seizure_type F1 improves >=3pp on cap-25 with no diagnosis/medication regression >=2pp. |
| `exect_s1_diagnosis_recall_gpt_cap25_v1` | second diagnosis-only recall stage | Promote only if diagnosis recall improves without adding seizure-derived diagnosis FPs. |
| `exect_s1_qwen_seizure_policy_gpt_guard_cap25_v1` | prompt-policy implementation for Qwen seizure errors | GPT guardrail must pass; Qwen must clear a preregistered seizure lift without diagnosis tradeoff. |

Do not rerun:

- broad pre-vocab injection,
- the v4.12 diagnosis-stabilized Qwen arm,
- H1 post bridge metadata-only comparisons,
- full validation without a cap/slice gate.

## ExECT S4 Structure

S4 should follow S1 because it is where Gan-like disciplined bottleneck work is most likely to pay off. The current S4 GPT full anchor is `65.5%` micro with `seizure_frequency` at `45.7%` F1 and `medication_temporality` at `62.5%` F1. The S4 work should be family-specific, not a general "better S4 prompt."

### S4 Current Anchors

| Surface | Anchor |
| --- | --- |
| GPT default | `exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`, v1.2 / cause bridge default, 65.5% micro |
| Qwen 35b | `exect_s4_validation_full_qwen35b_ollama_20260520T160914Z`, 67.5% micro, divergent family profile |
| Frequency gap | GPT `seizure_frequency` 45.7% F1; Qwen 50.0% |
| Temporality gap | GPT `medication_temporality` 62.5% F1, high recall but many FPs |
| Strong guard family | `investigation` effectively stable at 96.7% GPT F1 |

### S4-G1: Frequency Gold-Template Audit

Question: can ExECT frequency gold labels be represented by deterministic note-anchored templates before model adjudication?

This is the closest ExECT analogue to Gan G11, but the target is different:

- Gan optimizes monthly-frequency equivalence.
- ExECT S4 scores annotation-facing surfaces such as `1 per 1 week`, `frequency increased`, `seizure free since 2015`, and multi-label blocks.

No-model outputs:

- gold-in-template coverage for validation frequency labels,
- missed family taxonomy: qualitative change, seizure-free, zero-rate, dual-cardinal rate, multi-label block,
- record-level candidate list and evidence quote.

Proceed only if the audit identifies a representability gap that deterministic templates can close without changing scorer semantics.

### S4-G2: Frequency Intervention Gate

Candidate varied factors:

| Candidate group | Primary varied factor | Why it differs from rejected prior work |
| --- | --- | --- |
| `exect_s4_frequency_template_repair_gpt_cap25_v1` | post-template repair / surface canonicalization | Targets exact ExECT gold surfaces after extraction, not pre-vocab prompting. |
| `exect_s4_frequency_structured_slots_gpt_cap25_v2` | structured slots for rate/change/seizure-free/co-label retention | Keeps the model output decomposed before final surface assembly. |
| `exect_s4_frequency_candidate_adjudicate_gpt_slice_v1` | candidate presentation + LLM adjudication | Tests Gan-like candidate adjudication, but candidates must be ExECT gold-template surfaces. |

Gates:

- Primary: `seizure_frequency` F1 +3pp on cap-25 or enriched slice.
- Guard: no S1/S2/S3 family regression >=2pp on the same records.
- Evidence: quote support does not materially drop.
- Full validation only after cap/slice pass.

### S4-G3: Medication / Temporality Precision Guard

Question: can obvious non-ASM and planned/previous over-extraction be reduced without repeating the broad post-classifier recall collapse?

Start with no-model and artifact-only analysis:

- separate `annotated_medication` FPs from `medication_temporality` FPs,
- tag non-ASM leakage, planned/previous over-tagging, duplicate current/planned rows, and brand/generic misses,
- inspect whether evidence spans identify the leakage reliably.

Candidate intervention:

| Candidate group | Primary varied factor | Gate |
| --- | --- | --- |
| `exect_s4_medication_scope_guard_gpt_cap25_v1` | narrow post guard for non-ASM plus unsupported planned/previous rows | Medication-temporality precision improves with recall drop <2pp; annotated_medication F1 does not regress. |

Do not rerun the previous broad `medication_temporality` post-classifier as-is.

## S2 And S3 Fill-In Policy

S2 and S3 should be filled in only when they support the S1/S4 story or a manuscript needs the middle ladder.

| Level | Fill-in trigger | Candidate work |
| --- | --- | --- |
| S2 | S4 medication/comorbidity changes risk regressing S2 families | Re-run focused S2 cap-25 guard for `investigation`, `comorbidity`, and `annotated_medication`. |
| S3 | Cause/comorbidity overlap becomes central to S4 residuals | Run a sparse-family policy decision, not broad model tuning. |
| S2/S3 model suite | Paper makes an explicit middle-ladder claim | Reopen the declined extension with exact models, per-family metrics, and denominators. |

## Immediate Next Pull

1. Create S1 residual representability audit (`S1-G1`) from current GPT/Qwen full-validation artifacts.
2. From that audit, choose exactly one S1 cap-25/slice comparison group.
3. If S1 produces a credible lift or clean negative result, run S4 frequency gold-template audit (`S4-G1`).
4. Only after S4 frequency audit, choose between post-template repair, structured slots, or candidate adjudication.
5. Define S5 as a reporting layer once S1/S4 family stability is clear.

## Reporting Template For New ExECT Runs

Every new ExECT inspection should include:

| Field | Required value |
| --- | --- |
| Dataset / split | Usually `exectv2_fixed_v1:validation`; state cap/full/slice IDs. |
| Schema level | S1, S2, S3, S4, or S5-reporting subset. |
| Comparison group | Stable ID, e.g. `exect_s1_seizure_surface_repair_gpt_cap25_v1`. |
| Research axis | Axis 1, 2, or 3 under hybrid doctrine. |
| `stage_graph_id` | Stable graph, not just program name. |
| Primary varied factor | One of `pipeline_stage_graph`, `stage_executor`, `implementation_variant`, `prompt_policy`, etc. |
| Bridge mode | `inline`, `post_module`, `none_diagnostic`, or family-specific. |
| Scorer mode | Exact scorer string and caveats. |
| Primary metric | Family-specific F1 for targeted work; pooled micro is secondary for S4. |
| Guard metrics | Frozen-family F1, schema validity, evidence quote support. |
| Decision scope | `arm` unless a mechanism review cites multiple arms/positions. |
| Open cells | Explicitly state what was not tested. |
