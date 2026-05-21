# Gan S0 Expanded Builders Prose GPT Cap-50 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_cap50_v1_preregistration_20260521.md`  
Builder expansion: `docs/experiments/gan/gan_s0_residual_candidate_builder_expansion_20260521.md`  
Comparison group: `gan_s0_expanded_builders_prose_gpt_cap50_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — deterministic candidate surface (confirmatory re-run) |
| Comparison group | `gan_s0_expanded_builders_prose_gpt_cap50_v1` |
| Primary varied factor | `implementation_variant` (`cand_prose_expanded_builders_v1`) |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation` first 50 IDs, prose presentation (`cand_prose_v1` formatter), adjudication v1.1, scorer `gan_frequency_deterministic_v1`, expanded `temporal_candidates.py` builders (post-2026-05-21).

## Arms

| arm_id | implementation_variant | run_id | monthly | purist | pragmatic | norm exact | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B0 | `cand_prose_expanded_builders_v1` | `gan_s0_expanded_builders_prose_cap50_gpt4_1_mini_20260521T072655Z` | **68.0%** | 74.0% | 84.0% | 60.0% | 100% | 100% | 50 |

**Historical baseline (pre-expansion prose, same 50 IDs):**

| Reference | run_id | monthly |
| --- | --- | ---: |
| I0 cap-50 prose | `gan_s0_impl_i0_cand_prose_cap50_gpt4_1_mini_20260521T021111Z` | 62.0% |

**Monthly delta (B0 − baseline):** **+6.0pp** (34/50 vs 31/50 correct).

Cap-25 prefix (records 1–25): B0 **56.0%** (14/25) vs baseline **52.0%** (13/25); **+4.0pp** on prefix.

## Confirmation gates (prereg)

| Gate | Rule | Result |
| --- | --- | --- |
| Confirm | B0 monthly ≥ baseline + **3.0pp**, gates pass | **Pass** — 68.0% vs 62.0% (+6.0pp) |
| Schema | ≥ 95% | **Pass** — 100% |
| Evidence | ≥ 96% | **Pass** — 100% |
| Full validation | Not from cap-50 alone | **Not triggered** |

**Confirmation outcome:** **confirm (arm)** — expanded builders improve monthly accuracy on the 50-record validation prefix vs pre-expansion prose cap-50.

## Label delta vs baseline

| Category | Count | Record IDs |
| --- | ---: | --- |
| Monthly recovered (wrong → right) | **3** | `gan_10993`, `gan_15923`, `gan_16251` |
| Monthly regressed (right → wrong) | **0** | — |
| Net monthly misses | **−3** | 19 → 16 |

Recovered IDs align with builder-expansion targets (calendar/window aggregation: `gan_15923` `8 per 2 month`, `gan_16251` `14 per 4 month`; cluster spacing: `gan_10993`).

Persistent misses (16) still include seizure-type selection (`gan_12679`), unknown abstention (`gan_12438`, `gan_14792`, `gan_14881`, `gan_4702`, `gan_4709`), and arithmetic compression on long denominators — consistent with residual manual read open cells.

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| B0 | confirm (arm) | arm | +6pp vs pre-expansion cap-50; unlocks considering expanded builders as default det surface |

## Mechanism review

Not applicable for mechanism closure.

Directional read:

- Expanded deterministic candidate surface **directionally helps** on the Lane-A 50-record draw; effect is not limited to the 30-record hard queue (residual v2 was 63.3% on 30).
- Single implementation variant (`cand_prose_expanded_builders_v1`); mechanism class **det temporal candidate generation (Gan)** stays **open** until a second builder policy or LLM-candidate arm agrees.
- Slot-payload presentation remains **deprioritized** after residual v2; prose + expanded builders is the default follow-up skeleton.

## Operational recommendation

- **Treat expanded builders as the working default** for new Gan S0 cap-25/50 runs on `g2_candidates_adjudicate` + det candidates (code already deployed).
- **Do not** mechanism-close det-candidate generation or promote to full 299-record validation from cap-50 alone.
- **Optional next:** cap-50 table + expanded builders only if operational readability needs tie-break; else full-validation prereg for prose + expanded builders.

## Open cells

- Full 299-record validation
- Table/JSON presentation + expanded builders
- Qwen port of expanded-builder skeleton
- Remaining builder gaps (long-window cluster phrasing, concurrent seizure-type priority)
- LLM temporal candidates (Phase 3 E2 still open)
