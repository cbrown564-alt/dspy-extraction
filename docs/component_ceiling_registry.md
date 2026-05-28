# Component Ceiling Registry

Status: component ceiling registry
Last updated: 2026-05-28 (X1 evidence backfill)
Scope: current Gan S0 and ExECT decomposition status

This registry is the compact current map. It is not a full run registry. Use it
to decide what is active, what is historical evidence, and what must not be
repeated without a new preregistration.

The X1 backfill tables below are the row-level evidence ledger for the compact
component map. They classify each active result as an isolated ceiling,
operational stack, diagnostic result, rejected arm, or blocked benchmark claim,
and preserve the model/provider, split, scorer, config or run ID,
bridge/normalization policy, and caveat needed before a row can be promoted or
reused.

As of this backfill, no row is promoted as an isolated component ceiling.

## Gan S0

Current question: can seizure-frequency extraction be decomposed into candidate
inventory, temporal anchoring, target selection, label construction, and
unknown/no-reference policy before another broad prompt pass?

| Component | Status | Current evidence | Next action |
| --- | --- | --- | --- |
| Paper-comparison surface | blocked / benchmark-facing | Direct Gan paper comparison now requires `gan2026_paper_reproduction`; current headline rows mostly used `gan_frequency_deterministic_v1`. | Use Kanban G5 to rescore current baselines before benchmark-comparison tables. |
| Synthetic operational default | promoted baseline | Builder-gap v1 GPT: 80.6% monthly canonical validation; Qwen: 70.7%. | Keep as synthetic paper-default baseline until rescored or explicitly superseded. |
| Mechanism baseline | operational default | D1 v1.2b schema guard only: 79.9% monthly, within 0.7pp of builder-gap v1 and more decomposed. | Use for mechanism experiments. |
| Candidate inventory | coverage gate measured / mechanism open | G1 no-model report: deterministic D1/builder substrate emits candidates for 65/299 validation records, covers 61/299 exact gold labels, and covers 63/299 Purist/Pragmatic-equivalent labels; no-reference coverage is 0/11. | Use G1 strata to split target selection from label construction before adding more adjudicator or prompt variants. |
| Temporal anchoring | mechanism open | R11 D1 won; R15 showed arithmetic injection and broad relative-anchor guardrails regress. | Keep arithmetic diagnostic-only until parser is seizure-specific. |
| Scope and target selection | model-arm slice measured / mechanism open | G2 no-model report: candidate-constrained oracle supports 64/299 validation records and reaches 20.7% monthly under both scorer views. G2 model-arm slice: free adjudication 16.0% monthly, candidate-constrained 92.0%, seeded reason-code/answer-options selector surrogate 92.0% monthly and 100.0% pragmatic on the enriched 25-record slice under both paper and canonical scorer views. | Use candidate-constrained target selection as the current mechanism anchor; use seeded selector metadata for G3 policy isolation before any full-validation selector promotion. |
| Label construction and aggregation | constructor surface implemented / mechanism open | G2 deterministic constructor validates 64/65 current candidate records and leaves malformed `a pair of per 4 month` unsupported rather than scorer-repaired. The seeded selector preserves answer-option source/status/ambiguity metadata; selected options were deterministic seeds in 23/25 slice records and LLM options in 2/25. | Keep label construction separated from target selection in reports; inspect G2 differential records before adding a new explicit reason-code adjudicator. |
| Unknown vs no-reference policy | mechanism open | Canonical scorer separates them; paper reproduction collapses special classes differently. | Keep benchmark and clinical scorer modes separated in every report. |
| Evidence and schema | diagnostic only | High schema/evidence rates often coexist with wrong frequency labels. | Keep as gates and diagnostics, not proof of semantic correctness. |
| CLINES-style entity-first | rejected arm | R12 C1 caused severe context loss: GPT 20.8%, Qwen 12.0% monthly on cap-25. | Do not rerun same entity-first interface. Mechanism only reopens with preserved global context. |
| Self-consistency | rejected arm | R13 repeated sampling gave 0.0pp gain and 0% variance at temperature 0.7. | Do not spend 5x compute on Gan S0 self-consistency without a new instability hypothesis. |
| GEPA / optimizers | blocked | R14 requires compact-delta gate before Qwen GEPA. | No new Qwen GEPA until hosted compact-delta gate clears. |

### Gan S0 Evidence Detail Backfill

| Evidence row | Classification | Dataset / split | Model / provider | Config, run, or artifact | Scorer and bridge / normalization policy | Caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Builder-gap v1 GPT | promoted baseline / synthetic operational default | Gan 2026 synthetic; `gan_2026_fixed_v1:validation`; 299 evaluated | GPT 4.1-mini / OpenAI | Config `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json`; run `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | `gan_frequency_deterministic_v1`; prompt `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy`; Gan gold is `seizure_frequency_number[0]`; `reference[0]` is diagnostic only | 80.6% monthly is a synthetic-validation canonical diagnostic row, not Real(300) reporting; rescore with `gan2026_paper_reproduction` before benchmark-comparison tables. |
| Builder-gap v1 Qwen transfer | accepted local transfer under promoted surface | Gan 2026 synthetic; `gan_2026_fixed_v1:validation`; 299 predicted, 297 valid scored | Qwen3.6:35b / Ollama | Config `configs/experiments/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation.json`; run `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` | Same builder-gap prompt and `gan_frequency_deterministic_v1`; evidence support and schema validity remain diagnostics | 70.7% monthly trails GPT by 9.9pp; accepted as local-transfer evidence, not hosted parity or a new default. |
| D1 v1.2b schema guard only | mechanism baseline / operational D1 surface | Gan 2026 synthetic; `gan_2026_fixed_v1:validation`; 299 records | GPT 4.1-mini / OpenAI | Config `configs/experiments/gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini.json`; run `gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z` | `gan_frequency_deterministic_v1`; prompt `gan_frequency_s0_date_events_candidates_v1_2b_schema_guard_only`; schema repair keeps invalid hybrid labels out, arithmetic and broad relative-anchor guardrails excluded | 79.9% monthly is within 0.7pp of builder-gap GPT and more decomposed; use for mechanism experiments, not as a paper-comparison replacement. |
| Paper-comparison surface | blocked benchmark claim | Gan paper direct comparison requires Real(300)/Real(150) or an explicit synthetic-only caveat | none | Policy docs only: `policies/deterministic_scorer_semantics.md`, `policies/published_benchmark_metrics.md` | Direct comparison must lead with `gan2026_paper_reproduction` and report repair/range/tolerance options; canonical `gan_frequency_deterministic_v1` stays diagnostic | Current promoted rows used canonical synthetic-validation metrics, so external Gan benchmark claims remain blocked. |
| G1 candidate inventory | diagnostic coverage gate / mechanism open | Gan 2026 synthetic; `gan_2026_fixed_v1:validation`; 299 records | none | Artifact `experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.json` | No-model candidate-vs-gold coverage; exact coverage plus Purist/Pragmatic-equivalent coverage are diagnostic; no scorer semantics changed | Deterministic D1/builder substrate emits candidates for 65/299 records and exact-covers 61/299 labels; no-reference coverage is 0/11, so this is not an isolated ceiling. |
| G2 target/label no-model split | oracle scaffold / mechanism open | Gan 2026 synthetic; `gan_2026_fixed_v1:validation`; 299 records | none | Artifact `experiments/gan/gan_s0_target_label_split_g2_report_20260528.json` | Reports both `gan2026_paper_reproduction` and canonical views; deterministic constructor validates selected candidate labels without scorer-repairing malformed candidates | Candidate-constrained oracle supports only 64/299 records and reaches 20.7% monthly; useful for decomposition, not a deployable model surface. |
| G2 model-arm comparison | diagnostic model slice / mechanism open | Gan 2026 synthetic; enriched 25-record validation slice | GPT 4.1-mini / OpenAI | Configs `archive/configs/gan_s0_g2_free_adjudication_gpt4_1_mini_slice.json`, `configs/experiments/gan_s0_g2_candidate_constrained_gpt4_1_mini_slice.json`, `archive/configs/gan_s0_g2_reason_code_selector_gpt4_1_mini_slice.json`; runs `gan_s0_g2_free_adjudication_gpt4_1_mini_slice_20260528T155000Z`, `gan_s0_g2_candidate_constrained_gpt4_1_mini_slice_20260528T155000Z`, `gan_s0_g2_reason_code_selector_gpt4_1_mini_slice_20260528T155000Z` | Both paper reproduction and canonical scorer views; seeded selector preserves answer-option source/status/ambiguity metadata | Candidate-constrained and seeded-selector arms reached 92.0% monthly on the enriched slice, but slice metrics are diagnostic and must not stand in for full-validation promotion. |
| R12 CLINES-style entity-first | rejected arm | Gan 2026 synthetic; cap-25 validation slice | GPT 4.1-mini / OpenAI and Qwen3.6:35b / Ollama | Runs `gan_s0_entity_first_c1_llm_tags_date_events_cap25_gpt4_1_mini_20260527T235513Z` and `gan_s0_entity_first_c1_llm_tags_date_events_cap25_qwen35b_20260528T003538Z` | Gan deterministic cap-slice metrics under the date/events comparison policy | Severe context loss regressed GPT to 20.8% and Qwen to 12.0%; rejects the tested interface, not all entity-aware decomposition. |
| R13 self-consistency | rejected arm | Gan 2026 synthetic; cap-25 validation slice | GPT 4.1-mini / OpenAI and Qwen3.6:35b / Ollama, temperature 0.7 | Runs `gan_s0_self_consistency_sample5_cap25_gpt4_1_mini_20260528T000203Z` and `gan_s0_self_consistency_sample5_cap25_qwen35b_20260528T010925Z` | Gan deterministic cap-slice metrics; five samples compared against single-sample controls | 0.0pp gain and no variance at 5x compute; reopen only with a new instability hypothesis. |
| R14 GEPA / optimizer gate | blocked optimizer claim | Gan 2026 synthetic; historical GEPA artifacts reviewed | Qwen3.6:35b / Ollama gate design | Artifact `experiments/gan/gan_s0_r14_gepa_failure_postmortem_qwen_gate_design_20260528.md` | Optimizer objectives remain separate from benchmark scorers; no new benchmark claim made | Qwen GEPA stays blocked until compact-delta, latency, and no-overlap gate criteria are satisfied. |

Primary current docs:

- `experiments/gan/gan_s0_pipeline_decomposition_deep_dive_20260528.md`
- `experiments/gan/gan_s0_candidate_inventory_coverage_report_20260528.md`
- `experiments/gan/gan_s0_target_label_split_g2_report_20260528.md`
- `experiments/gan/gan_s0_g2_model_arm_comparison_20260528.md`
- `experiments/gan/gan_s0_r11_temporal_date_stage_decision_20260528.md`
- `experiments/gan/gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md`
- `experiments/gan/gan_s0_r13_self_consistency_variance_probe_decision_20260528.md`
- `experiments/gan/gan_s0_r15_d1_guardrail_ablation_decision_20260528.md`
- `datasets/gan/gan_2026_label_audit.md`
- `policies/deterministic_scorer_semantics.md`

## ExECT

Current question: what are the isolated family ceilings and what interference
appears when optimized components are stacked?

| Component | Status | Current evidence | Next action |
| --- | --- | --- | --- |
| Clean ladder S1-S4 | diagnostic baseline | Shows schema breadth pressure, but not component ceilings. | Treat as unoptimized complexity stress test. |
| S5 core surface | promoted baseline | GPT v2b 85.8% micro / 73.9% frequency F1; Qwen 85.4% / 71.4% on validation. | Keep as current stacked baseline, not proof of optimal decomposition. |
| Holdout transfer | active risk | S1 GPT 92.3 -> 77.8 micro; S5 GPT frequency 73.9 -> 47.1 F1. | Route residual/causal attribution through Kanban E11 before any tuning; do not tune from holdout. |
| Frequency event/rate payload | coverage gate passed / adjudication open | E1 audit covers 43/43 validation gold labels, including quantified, qualitative, seizure-free, zero-rate, type-associated, temporal-scope, and multi-label cases; broad payload precision is only 22.2% with 151 extra candidates. | Split candidate selection/adjudication from label construction before model-backed stack work. |
| S1 raw/bridge/prompt split | mechanism open | E2 split audit exists; validation strength depends heavily on benchmark bridges, while holdout diagnosis/seizure-type remain weak. | Use the completed split to design isolated diagnosis/seizure-type ceilings and pairwise interaction tests; report raw, bridge, and prompt effects separately. |
| Medication current-Rx | isolated ceiling / no-model oracle substrate | E6 annotation-derived current-Rx payload reaches 100.0% medication F1 on validation (47 TP / 0 FP / 0 FN). Existing S1 GPT medication is 92.8% F1; S5 GPT is 88.7% F1 with full recall and lower precision. | Use E7 to attribute stacked medication over-emission before changing prompts or bridges; keep note-surface lifecycle candidates diagnostic. |
| Medication lifecycle / temporality | clinical-diagnostic / deferred | E5 keeps lifecycle/temporality out of benchmark-facing medication F1. E3 lifecycle inventory exposes planned (11), previous (9), taper/stop (8), dose-line (131), dose-only/unknown (60), non-ASM (4), and unknown-temporality (116) rows; note-surface current candidates cover only 22/47 medication gold labels. Prescription JSON still lacks native temporality. | Use lifecycle categories for diagnostic residual and stack-interference attribution only; require a new follow-up card before model-backed temporality scoring. |
| Family-span payload | coverage gate passed / prompt mechanism open | E4 `exect.sections.family_spans.v1` covers validation gold evidence for diagnosis, seizure, medication, investigation, and frequency at 100%, history/background at 95.5%, and a cap-25 S1+investigation span context covers 116/116 gold annotations using 88.8% of full-note characters. False-family spans remain measurable. | Preregister a full-note versus family-span prompt comparison before promotion. |
| Investigation | likely near ceiling, unproven | High and stable in broad stacks and holdout, but isolated ceiling is not measured. | Confirm through Kanban E12 before calling solved. |
| Comorbidity / sparse S3 families | mechanism open | Weak and support-sensitive; broad ladder does not isolate causes. | Require support counts and family contract before new tuning. |
| Per-family parallel S5 | rejected arm | One parallel implementation regressed; it does not reject family-first decomposition. | Do not rerun same interface; reopen only with component substrates. |
| CUI-aware Table 1 reproduction | blocked | Current scorers are project field-family scorers, not full published benchmark reproduction. | Build CUI-aware all-family scorer before external ExECT comparison. |

### ExECT Evidence Detail Backfill

| Evidence row | Classification | Dataset / split | Model / provider | Config, run, or artifact | Scorer and bridge / normalization policy | Caveat |
| --- | --- | --- | --- | --- | --- | --- |
| S5 v2b GPT core stack | promoted baseline / operational stack | ExECTv2; `exectv2_fixed_v1:validation`; 40 documents | GPT 4.1-mini / OpenAI | Config `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini.json`; run `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` | `exect_s5_core_field_family_deterministic_v1`; prompt / bridge policy `exect_s4_field_family_v1_2_label_policy`; S5 includes diagnosis, seizure type, annotated medication, investigation, and seizure frequency; medication temporality omitted | 85.8% micro and 73.9% frequency F1 is the current stacked baseline, not an isolated component ceiling or ExECT Table 1 reproduction. |
| S5 v2b Qwen transfer | accepted local transfer under operational stack | ExECTv2; `exectv2_fixed_v1:validation`; 40 documents | Qwen3.6:35b / Ollama | Config `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama.json`; run `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z` | Same S5 v2b stack and `exect_s5_core_field_family_deterministic_v1` | 85.4% micro and 71.4% frequency F1 is near-parity transfer evidence, not a Qwen lead or deployment-readiness claim. |
| Clean S1-S4 ladder | diagnostic baseline | ExECTv2; `exectv2_fixed_v1:validation`; 40 documents per full-validation rung | GPT 4.1-mini / OpenAI and Qwen3.6:35b / Ollama | Current-authority configs are listed in `experiments/synthesis/program_variant_registry.md`; headline runs summarized in `experiments/synthesis/paper_result_table_pack_20260525.md` | `exect_field_family_deterministic_v1`, `exect_s2_field_family_deterministic_v1`, `exect_s3_field_family_deterministic_v1`, and `exect_s4_field_family_deterministic_v1`; bridge policies vary by rung | Useful schema-breadth stress test; pooled micro changes mix field-family composition with task difficulty and do not establish isolated ceilings. |
| Holdout transfer | active risk / diagnostic holdout | ExECTv2; `exectv2_fixed_v1:test`; 40 documents | GPT 4.1-mini / OpenAI and Qwen3.6:35b / Ollama | Runs include `exect_s0_s1_validation_test_gpt4_1_mini_20260526T184057Z`, `test_holdout_exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260527T055059Z`, and `test_holdout_exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260527T055854Z` | Same rung-specific field-family scorers as validation; no prompt or scorer tuning from holdout | Transfer drops are residual-analysis triggers only; holdout must not be used to tune prompts, bridges, or scorer policy. |
| Frequency event/rate payload | diagnostic coverage gate / adjudication open | ExECTv2; `exectv2_fixed_v1:validation`; 40 documents | none | Artifact `experiments/exect/exect_frequency_event_rate_payload_audit_20260528.json` | No-model candidate-vs-gold coverage audit over current `load_exect_gold_documents()` frequency policy; no scorer semantics changed | Broad payload covers 43/43 validation frequency gold labels but emits 151 extra candidates with 22.2% precision, so selection/adjudication remains open. |
| S1 raw/bridge/prompt split | diagnostic causal split / mechanism open | ExECTv2; validation cap-25, full validation, and pre-existing test holdout surfaces | none; stored artifact replay only | Artifact `experiments/exect/exect_s1_raw_bridge_prompt_split_audit_20260528.md` | `exect_field_family_deterministic_v1`; raw extraction compared against artifact benchmark-bridge-only and clean-ladder policy surfaces | S1 full-validation GPT is near ceiling only after bridges; raw extraction and transfer remain unsolved, so this is not a diagnosis/seizure-type ceiling claim. |
| Medication current-Rx payload | diagnostic coverage gate / superseded by E6 ceiling probe | ExECTv2; `exectv2_fixed_v1:validation`; 40 documents | none | Artifact `experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.json` | No-model payload-vs-gold audit over current prescription policy; annotated current-Rx uses benchmark prescription annotations | Annotated current-Rx payload reproduces 47/47 validation medication gold labels; E6 now records the isolated current-Rx ceiling comparison against S1/S5 medication surfaces. |
| E6 medication current-Rx ceiling | isolated ceiling / no-model oracle substrate | ExECTv2; `exectv2_fixed_v1:validation`; 40 documents | none for isolated payload; GPT 4.1-mini / OpenAI for S1/S5 comparison surfaces | Artifact `experiments/exect/exect_medication_current_rx_ceiling_probe_20260528.json`; S1 run `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`; S5 run `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` | Medication-only slice of `exect_field_family_deterministic_v1`; canonical medication normalization; lifecycle rows diagnostic only | Isolated payload reaches 100.0% F1 (47/47). This is an annotation-derived no-model ceiling substrate, not a deployed model extractor. S5 recall is 100.0% but precision drops to 79.7%, routing over-emission to E7. |
| Medication lifecycle / temporality | clinical-diagnostic / deferred | ExECTv2; `exectv2_fixed_v1:validation`; 40 documents | none | E3 payload artifact `experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.json`; E5 decision `experiments/exect/exect_medication_lifecycle_target_policy_decision_20260528.md` | Lifecycle rows are note-surface diagnostics; prescription JSON has no native temporality column; current medication F1 remains annotated current-Rx only | Do not make lifecycle a benchmark-facing metric without a new preregistered target policy and explicit scorer/gold-proxy design. |
| Family-span payload | diagnostic coverage gate / prompt mechanism open | ExECTv2; `exectv2_fixed_v1:validation`; 40 documents; cap-25 prompt-substrate slice | none | Artifact `experiments/exect/exect_family_span_payload_audit_20260528.json` | No-model span-vs-gold evidence coverage audit; `exect.sections.family_spans.v1`; no scorer semantics changed | Covers core-family validation evidence, but section filtering is not promoted until a full-note versus family-span prompt comparison preserves recall and shows benefit. |
| Investigation broad-stack surface | likely near ceiling / unproven diagnostic | ExECTv2 validation and holdout broad-stack reports | GPT 4.1-mini / OpenAI and Qwen3.6:35b / Ollama | S2-S5 rows in `experiments/synthesis/paper_result_table_pack_20260525.md` and `experiments/synthesis/test_holdout_evaluation_report_20260527.md` | Investigation scored by S2/S4/S5 field-family scorers using modality+result strings | High broad-stack F1 is suggestive but not isolated; confirm with an isolated family component before calling solved. |
| Per-family parallel S5 | rejected arm | ExECTv2; cap-25 validation slice | GPT 4.1-mini / OpenAI | Run `exect_s5_core_field_family_parallel_v2b_cap25_gpt4_1_mini_20260524T212052Z` | `exect_s5_core_field_family_deterministic_v1`; same v2b core families | Rejected as tested because cap-25 micro regressed; does not reject family-first decomposition with better substrates. |
| CUI-aware Table 1 reproduction | blocked benchmark claim | ExECTv2 published benchmark scope | none | Policy docs only: `policies/published_benchmark_metrics.md`, `datasets/exect/exect_gold_label_audit.md` | Requires CUI-aware, feature-aware all-family scorer across published Table 1 families | Current project field-family scorers are partial diagnostic/project scorers, so external ExECT benchmark claims remain blocked. |

Primary current docs:

- `experiments/exect/exect_task_deep_review_20260528.md`
- `experiments/exect/exect_frequency_event_rate_payload_audit_20260528.md`
- `experiments/exect/exect_medication_current_rx_lifecycle_payload_audit_20260528.md`
- `experiments/exect/exect_family_span_payload_audit_20260528.md`
- `experiments/synthesis/test_holdout_evaluation_report_20260527.md`
- `experiments/synthesis/paper_result_table_pack_20260525.md`
- `datasets/exect/exect_gold_label_audit.md`
- `policies/deterministic_scorer_semantics.md`
- `policies/published_benchmark_metrics.md`

## Registry Rules

- A component without an isolated ceiling is `mechanism open`, not solved.
- A failed config is a `rejected arm` unless a mechanism review explicitly closes
  the class.
- A promoted stacked baseline is allowed to be useful and still not be the
  research target.
- Holdout metrics can trigger analysis but must not drive tuning.
- The detail backfill is a provenance layer. It does not promote any new
  isolated ceiling unless the compact component row says so explicitly.
