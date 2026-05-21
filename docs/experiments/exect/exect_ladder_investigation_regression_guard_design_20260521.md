# ExECT Ladder Investigation Regression Guard — Design

Date: 2026-05-21  
Status: Design ready for fixture tests + cap-25 prereg  
Parent: `exect_s1_s3_residual_targeted_actions_20260521.md` (P0)  
Levels: S2 (90% F1), S3 (93.1% F1 after v1.2 repair), S4 (near ceiling, 1 FP / 1 FN)  
Prior collapse: S3 v1.0 investigation format failure — **do not widen schemas without these guards**

## Question

Can lightweight **post-module investigation guards** preserve modality+result surfaces (`eeg normal`, `mri abnormal`, `eeg unknown`) and prevent out-of-scope modality leakage when comorbidity and sparse families are added to the prompt?

## No-model error taxonomy (recurring across levels)

| Bucket | Levels | Tag | Example | Mechanism |
| --- | --- | --- | --- | --- |
| Out-of-scope ECG | S2 | over-extraction | EA0016, EA0100: `ecg normal` FP | S2 policy: EEG/MRI/CT only |
| Polarity conflict | S2–S4 | scorer-surface | EA0102: `eeg abnormal` vs gold `eeg normal` | Evidence/result parsing |
| Unknown miss | S2–S4 | scorer-surface | EA0179: FN `eeg unknown` | Planned/unavailable scan wording |
| Planned scan as completed | S4 | over-extraction | v1.1 regression: `eeg unknown` on planned scans | S4 v1.2 guard restored |
| Missing-gold ECG | S2 | gold-quality-caveat | EA0100 | Exclude |

S3 v1.2 **repaired** investigation after v1.0 collapse — this family is a **regression guard**, not a primary F1 lift target on S2.

## Existing infrastructure

| Asset | Location | Status |
| --- | --- | --- |
| `exect.investigation.surface_bridge.v1` | `family_backlog.py` | planned |
| `exect.investigation.planned_scan_guard.v1` | `family_backlog.py` | planned |
| S4 investigation recovery | `exect_s4.py` `_recover_s4_investigation_raw_values` | partial — includes planned-scan cases in fixtures |
| S3 investigation recovery | `exect_s3.py` | modality+result canonicalization |
| Allowed modalities | `_INVESTIGATION_MODALITIES = ("eeg", "mri", "ct")` | S3 |

## Proposed tiers (`implementation_variant`)

| Tier | ID | Action | Expected effect |
| --- | --- | --- | --- |
| **I0** | `inv_guard_drop_ecg_v1` | Remove any investigation label with modality `ecg` | −2 FP on S2 (EA0016, EA0100) |
| **I1** | `inv_guard_planned_scan_unknown_v1` | If note matches planned/unavailable scan cues → emit `modality unknown` or drop completed polarity | Fix EA0179 FN; prevent S4-style unknown over-tag |
| **I2** | `inv_guard_polarity_from_evidence_v1` | When evidence quote contains only `normal` markers, force `normal` result (narrow regex) | EA0102 — high risk; isolate on slice |

**First grid:** L1 vs I0 vs I0+I1 on **S2** cap-25. Port winner to S3/S4 regression checklist.

### I1 planned/unavailable cues (draft)

Reuse S4 fixture policy strings from `exect_s4.py`:

- Planned: `to be arranged`, `will arrange`, `booked`, `awaiting`, `pending`
- Unavailable: `no results`, `not yet`, `report awaited`
- Output: `{modality} unknown` only when gold policy expects unknown (EA0179)

**Explicit exclusion:** Do not emit `unknown` for completed result sentences (S4 v1.1 failure mode).

## Cap-25 prereg gates

| Metric | Gate |
| --- | --- |
| Primary | `investigation` F1 vs level baseline |
| Regression | seizure_type, comorbidity, diagnosis within −2pp |
| S4 promotion | If run on S4, no investigation regression vs `…071248Z` |
| Mechanism | `decision_scope: arm` per tier |

Comparison group: `exect_ladder_investigation_guard_gpt_cap25_v1` (schema field in prereg: S2 first)

## Fixture documents

| Doc | Level | Must demonstrate |
| --- | --- | --- |
| EA0016 | S2 | I0 removes `ecg normal` |
| EA0179 | S2/S3 | I1 recovers `eeg unknown` without adding false unknowns |
| EA0102 | S2/S4 | I2 polarity — only promote if no new FPs on cap-25 |
| EA0188 | S2 | FN `eeg abnormal` with `specificity_collapsed` — gold caveat; do not train I2 |

## Open cells

- Whether I1 runs at S2 only or is shared module imported by S3/S4 recovery
- Surface bridge (`inv_guard` vs `surface_bridge`) ordering: guard first, bridge second
- Qwen investigation (stronger on S3) — separate track

## Next steps

1. Implement I0 + tests on S2 investigation recovery path.
2. Add I1 fixtures from S4 `s4_investigation_*` cases where applicable.
3. Cap-25 S2 prereg; inspection with regression table for seizure + comorbidity.
4. Add passing config as **required regression arm** in any wider-schema S3/S4 prereg template.

**Do not** mechanism-close “investigation solved” from I0 alone.
