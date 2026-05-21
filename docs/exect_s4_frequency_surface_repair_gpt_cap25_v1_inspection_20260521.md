# ExECT S4 Frequency Surface Repair GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Pre-registration: `docs/exect_s4_frequency_surface_repair_gpt_cap25_v1_preregistration_20260521.md`  
decision_scope: **arm**

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S4 field-family (11 families) |
| Comparison group | `exect_s4_frequency_surface_repair_gpt_cap25_v1` |
| Research axis | 3 — post-bridge surface repair |
| stage_graph_id | `g1_l1_policy_bridges` |
| varied_factor | `implementation_variant` |
| decision_scope | arm |

## Arms

| arm_id | run_id | seizure_frequency F1 | micro F1 | evidence support | gate |
| --- | --- | ---: | ---: | ---: | --- |
| R0 | `exect_s4_frequency_surface_r0_control_cap25_gpt4_1_mini_20260521T072357Z` | **51.0%** | 69.5% | 87.9% | pass |
| R1 | `exect_s4_frequency_surface_r1_post_merge_cap25_gpt4_1_mini_20260521T072445Z` | 48.1% | 69.1% | 87.9% | fail primary |

**Void run (implementation bug):** `…T072417Z` used note-absence full abstention and is excluded from decision — 27.8% frequency F1 from clearing 13/18 non-empty docs.

Configs:

- R0: `configs/experiments/exect_s4_frequency_surface_r0_control_cap25_gpt4_1_mini.json`
- R1: `configs/experiments/exect_s4_frequency_surface_r1_post_merge_cap25_gpt4_1_mini.json`

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| R0 | hold (control) | arm | Reproduces v1.2 inline bridge band (~49–51% cap-25) |
| R1 | **reject (arm)** | arm | −2.9pp vs R0; no +3pp promotion gate |

## Primary metric read

| Metric | R0 | R1 | Δ (R1 − R0) |
| --- | ---: | ---: | ---: |
| seizure_frequency F1 | **51.0%** | 48.1% | **−2.9pp** |
| seizure_frequency recall | 52.0% | 48.0% | −4.0pp |
| seizure_frequency precision | 50.0% | 47.6% | −2.4pp |

Promotion gate requires **≥+3.0pp** — not met.

## Frozen S3 regression guard

| Family | R0 F1 | R1 F1 | Δ |
| --- | ---: | ---: | ---: |
| diagnosis | 95.2% | 95.2% | 0 |
| seizure_type | 90.9% | 90.9% | 0 |
| annotated_medication | 69.0% | 69.0% | 0 |
| investigation | 93.8% | 93.8% | 0 |
| comorbidity | 73.0% | 73.0% | 0 |
| birth_history | 50.0% | 50.0% | 0 |

No frozen S3 family regressed ≥2pp. Frequency regression is isolated to post-merge bridge behavior.

## Bridge flag read (R1)

Post-merge adds note-anchored quantified/co-label surfaces when regex finds them; spurious `seizure free` removed when note lacks cue. Net effect on cap-25: extra merged labels did not improve set-F1 — precision/recall both fell slightly vs inline-only R0.

Contrast with rejected **H2 pre-vocab** (`exect_s4_frequency_deterministic_v1`, 47.1% vs 49.1% L1): R1 post-merge is a different varied factor but same direction (arm reject). Pre-vocab anchors the LLM; post-merge only touches bridge output.

## Mechanism review

Not claimed. One implementation variant tested on cap-25; R1 reject does not close “ExECT frequency post-merge” or “note-anchored repair” mechanism classes.

## Open cells

- Prompt-policy / example-strategy changes on S4 frequency
- Narrower merge policies (quantified-only merge without qualitative note fill)
- Full validation (40) — not triggered
- Qwen port — deferred
- Frequency-heavy residual slice replay — optional diagnostic only

## Recommended next steps

1. **Do not promote** R1 `frequency_post_merge_v1_3`.
2. Keep **R0 / v1.2 inline bridge** as S4 frequency operational default on cap-25/full anchors.
3. If revisiting frequency repair, preregister a **new** `implementation_variant` (e.g. quantified-only post-merge or targeted zero-rate/dual-cardinal repair) — do not rerun this arm unchanged.

## Explicit non-claims

- No mechanism reject for post-bridge repair
- Not ExECTv2 Table 1 reproduction
- Not comparable to nine-family S1–S3 micro headlines
