# Gan S0 Expanded Builders VR GPT Full Validation v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_preregistration_20260521.md`  
F0 anchor: `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md`  
Comparison group: `gan_s0_expanded_builders_vr_gpt_full_validation_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — expanded builders × VR stage graph |
| Comparison group | `gan_s0_expanded_builders_vr_gpt_full_validation_v1` |
| Primary varied factor | `implementation_variant` (`cand_prose_expanded_builders_vr_v1`) |
| Anchor `stage_graph_id` | `g3_candidates_extract_repair` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, full validation 299 records, `gan_frequency_s0_temporal_candidates_verify_repair` v1.1, expanded `temporal_candidates.py` builders, two LLM calls per record.

## Arms

| arm_id | implementation_variant | run_id | monthly | purist | pragmatic | norm exact | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V1 | `cand_prose_expanded_builders_vr_v1` | `gan_s0_expanded_builders_vr_full_validation_gpt4_1_mini_20260521T074513Z` | **65.8%** | 77.2% | 84.9% | 53.0% | 99.7% | 100% | 298/299 |

**External anchors:**

| Reference | run_id | monthly | Δ vs V1 |
| --- | --- | ---: | ---: |
| F0 adjudicate-only (expanded) | `gan_s0_expanded_builders_prose_full_validation_gpt4_1_mini_20260521T073432Z` | **68.1%** | **−2.3pp** |
| Pre-expansion VR operational | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` | 65.1% | **+0.7pp** |

Monthly correct: V1 **196/298** vs F0 **203/298** (−7) vs VR **194/298** (+2).

## Confirmation gates (prereg)

| Gate | Rule | Result |
| --- | --- | --- |
| Promote VR operational (arm) | V1 ≥ F0 − 1.0pp (≥ 67.1%) and ≥ VR − 1.0pp and gates pass | **Fail** — 65.8% < 67.1% |
| Hold — keep F0 as best monthly | Beats old VR with gates pass but V1 < F0 − 1.0pp | **Pass** — +0.7pp vs VR, −2.3pp vs F0; schema/evidence pass |
| Hold (inconclusive) | V1 within ±1.0pp of F0 | **Fail** — −2.3pp outside band |
| Reject VR bundle (arm) | V1 < F0 − 3.0pp (65.1%) or gate failure | **Fail** — 65.8% > 65.1%; gates pass |

**Outcome:** **hold (arm) — keep F0 adjudicate-only as best monthly full-validation arm.** Expanded builders in VR improve slightly over pre-expansion VR (+0.7pp) but **verify-repair subtracts vs single-pass F0** on this split. Do **not** promote VR bundle to operational default.

## Diagnostics

| Metric | V1 | F0 | Pre-exp VR |
| --- | ---: | ---: | ---: |
| Normalized exact | 53.0% | 56.0% | 52.3% |
| Missing evidence spans | 4 | 15 | 4 |
| Invalid predictions | 1 (`gan_338`) | 1 (`gan_338`) | 1 (`gan_338`) |
| Prediction latency | 0.19 s/rec | 0.91 s/rec | 3.73 s/rec |

Latency note: V1 wall time ~63s total suggests heavy **DSPy disk-cache reuse** from prior VR/adjudicate runs on overlapping records; treat latency as non-comparable for cost planning until a cache-cleared rerun.

## Label delta (monthly, sampled mismatch IDs)

| Pair | Recovered | Regressed | Shared misses |
| --- | ---: | ---: | ---: |
| V1 vs F0 | 12 | 12 | 8 |
| V1 vs pre-exp VR | 2 | 2 | 18 |

VR does not uniformly repair F0 regressions; paired tradeoff vs F0 (12/12) mirrors F0-vs-VR read. vs pre-exp VR, V1 is nearly a wash on sampled IDs (+2 net on full split).

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| V1 | **hold (arm)** | arm | +0.7pp vs old VR; −2.3pp vs F0; keep F0 as monthly leader |

## Mechanism review

Not applicable for mechanism closure.

Directional read:

- Expanded builders **transfer partially** to VR (+0.7pp vs frozen pre-expansion anchor) but **do not close the gap** to adjudicate-only F0.
- Consistent with cap-25 Axis 1 (A3 adjudicate beat A5 VR by +8pp on pre-expansion builders) directionally, though magnitudes differ at full scale.
- Mechanism classes **verify-repair placement (Gan)** and **det temporal candidate generation** remain **open**; this arm does not promote VR.

## Operational recommendation

- **Freeze operational default:** F0 skeleton (`g2_candidates_adjudicate` + expanded builders, single pass) for monthly-frequency leadership at **68.1%**.
- **Do not** replace frozen VR anchor `…130933Z` with V1 for benchmark comparisons without relabeling — modest +0.7pp is within noise vs pre-expansion VR and loses to F0.
- **Deprioritize** further g3 VR sweeps unless a new `implementation_variant` (repair policy, presentation) is preregistered.
- **Optional:** E4-style adjudicate-then-VR with expanded builders only if a new hypothesis doc targets the cap-25 A3/A5 gap explicitly.

## Open cells

- Adjudicate-then-VR (`temporal_candidates_adjudicate_verify_repair`) + expanded builders
- Qwen port of F0 skeleton (not V1)
- Targeted builder gaps (seizure-type priority, long-window cluster phrasing)
