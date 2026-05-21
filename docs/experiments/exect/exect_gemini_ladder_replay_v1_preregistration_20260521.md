# ExECT Gemini Ladder Replay v1 — Pre-Registration

Date: 2026-05-21  
Status: **Done** — inspection `docs/experiments/exect/exect_gemini_ladder_replay_v1_inspection_20260521.md`  
Comparison group: `exect_gemini_ladder_replay_v1`  
Kanban: `docs/planning/kanban_plan.md` (§ Next step)  
Prior context: `docs/experiments/synthesis/prior_best_vs_current_best_reanalysis_20260521.md` (§ Gemini stale champion)

## Research question

Under **today's** frozen ExECT S1/S4 field-family programs, scorers, bridge policies, and validation split, does **Gemini 3.1 Flash-Lite** remain competitive with hosted GPT 4.1-mini and local Qwen3.6:35b — or does prior Round-2 Gemini champion evidence no longer apply?

**Do not** treat stale Round-2 `full_exect_gemini_combined_examples` or Gan direct/verify-repair Gemini runs as current-architecture defaults.

## Hypothesis

Gemini may match or exceed GPT/Qwen on some ExECT families (especially label surfaces where Gemini Gan cap-25 showed monthly/Purist gains) but may trail on evidence quote support, mirroring the Gan direct pattern. Outcome is **model-comparison evidence only** (`decision_scope: arm`); it does not mechanism-close hybrid placement.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Comparison group | `exect_gemini_ladder_replay_v1` |
| Primary varied factor | `model_track` = `gemini` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

## Fixed controls (all arms)

| Control | S1 | S4 |
| --- | --- | --- |
| Split | `exectv2_fixed_v1:validation` (full, 40 records) | same |
| Scorer | `exect_field_family_deterministic_v1` | `exect_s4_field_family_deterministic_v1` |
| Prompt | `exect_s0_s1_field_family_v4_10_label_policy` | `exect_s4_field_family_v1_2_label_policy` |
| Program variant | `exect_s0_s1_field_family_single_pass` | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` |
| Repair policy | `none` | `artifact_epilepsy_cause_k0_k1_only` |
| Structured output | `provider_json_schema_with_pydantic_validation` | same |
| Model config | `configs/models/gan_s0_gemini31_flash_lite.json` | same |

## External anchors (not in-session controls)

| Schema | GPT 4.1-mini | Qwen3.6:35b | Run ID suffix |
| --- | ---: | ---: | --- |
| S1 micro F1 | **92.3%** | 79.0% | `…221944Z` / `…042117Z` |
| S4 micro F1 | **65.5%** | 67.5% | `…071248Z` / `…160914Z` |

Historical Gemini (stale — reference only):

- Gan direct full validation: 63.9% monthly (`…101710Z`) — pre–temporal-candidates, wrong task for ExECT ladder
- Gan VR cap-25: evidence +8.6pp vs direct but schema/Purist regress — **no VR scale-up**

## Arms and configs

| Step | Arm | Scope | Config |
| --- | --- | --- | --- |
| 0 | S1 smoke | 3 records | `exect_s0_s1_smoke_gemini31_flash_lite.json` |
| 0 | S4 smoke | 3 records | `exect_s4_smoke_gemini31_flash_lite.json` |
| 1 | S1 full validation | 40 records | `exect_s0_s1_validation_full_gemini31_flash_lite.json` |
| 2 | S4 full validation | 40 records | `exect_s4_validation_full_gemini31_flash_lite.json` |

Optional (not in this prereg): Gan F0 expanded builders prose port — only if paper needs a three-provider Gan table.

## Primary metrics

| Arm | Primary | Diagnostic |
| --- | --- | --- |
| S1 | Pooled micro F1 (diagnosis, seizure_type, annotated_medication) | Per-family F1, evidence quote support, schema validity |
| S4 | Pooled micro F1 (eleven families) | Per-family F1; guard families: medication_temporality, seizure_frequency, investigation, epilepsy_cause |

## Run lifecycle gates

| Gate | Rule |
| --- | --- |
| Smoke | Provider/config/runtime compatibility; standard artifacts; no performance claim |
| S1 full | Run only after S1 smoke passes; record token usage and latency |
| S4 full | Run after S1 full **or** if S1 smoke passes and S1 full is in flight; same scorer/split discipline |
| Inspection | Write inspection doc per arm before Kanban promotion/hold/reject |

## Interpretation rules

- Report as **model-comparison** evidence; same scorer and split as GPT/Qwen anchors.
- Do not mechanism-close hybrid stage placement from Gemini alone.
- Do not compare to Round-2 combined-examples ExECT configs without explicit stale-architecture caveat.
- Per-family breakdown required for S4; pooled micro alone is insufficient when family profiles diverge (see Qwen S4 read).
- Record billing/cost and evidence-support separately from label F1.

## Skills

`model-config-compatibility`, `experiment-run-lifecycle`, `dspy-experiment-design`, `dataset-audit-first`.
