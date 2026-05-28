# Gan S0 Seizure Frequency Residual Taxonomy Consolidation

Date: 2026-05-24  
Kanban Card: C1 - Consolidate Gan residual taxonomy  
Decision Scope: Residual taxonomy mapping for Gan S0 improvements  

---

## 1. Context and Motivation

Following the implementation of `gan_s0_candidate_builder_gap_v1` as the operational default (80.6% monthly accuracy on synthetic validation), this note consolidates forensics from the builder-gap manual audit (58 severe misses), the Qwen-35b error taxonomy, and GEPA G1/G2 failure patterns. 

By categorizing the remaining errors, we define a clear taxonomy to prevent blind optimizer iterations or prompt-tuning runs that regress on resolved defaults.

---

## 2. Core Residual Taxonomy

The residual errors in Gan S0 monthly frequency extraction are divided into four primary categories:

### A. Unknown-Overuse / Abundance
* **Description**: The model emits `unknown` when a rate or cluster window is actually derivable, or conversely, emits a specific rate/category for notes that explicitly state "frequency unclear" or contain no clinical frequency reference.
* **Semantic Boundary**:
  * **`unknown`**: Used when seizure activity *is* mentioned, but its frequency is declared as unclear, untracked, or missing numeric bounds (e.g., "Clusters of absences; frequency unclear").
  * **`no seizure frequency reference`**: Used when the note contains *zero* mention of current or historical seizure events, or when the only mentions are childhood febrile seizures or diagnostic descriptors with no frequency context (e.g., "No unprovoked seizures since childhood").
* **Key Example**: `gan_7894` ( childhood febrile seizures only, gold is `no seizure frequency reference`; models must not over-emit `unknown` here).

### B. Pragmatic Monthly Divergence
* **Description**: A divergence between the Purist category (strict mathematical conversion) and the Pragmatic category (overall clinical description).
* **Semantic Boundary**:
  * **Purist category**: The literal rate mathematical mapping (e.g., "1 per day" maps to `gte_1_per_day` / 30.0 monthly).
  * **Pragmatic category**: The clinician's contextual reading. For example, if a patient has daily absences (30/month) but only 2 tonic-clonic seizures per month, the purist reading is "30.0 monthly" (highest frequency), while a pragmatic classification might focus on the tonic-clonic rate depending on annotation policy.
* **Scoring Guardrail**: Gan primary gold is strictly `seizure_frequency_number[0]`. Scorer semantics must remain unchanged.

### C. Multi-Type and Cluster Spacing Errors
* **Description**: Failure to extract or format cluster intensity and frequency correctly.
* **Taxonomy Rules**:
  * For clusters of unknown frequency: `unknown, N per cluster` (e.g., `gan_10594` -> `unknown, 2 per cluster`).
  * If the number of events per cluster is a range: `unknown, N to M per cluster`.
  * The model must not collapse cluster templates (e.g., emitting `unknown` instead of `unknown, 3 to 4 per cluster`).

### D. Temporal Scope/Window Mismatches
* **Description**: Historical seizure rates or temporary seizure-free intervals (e.g., "seizure-free for 4 months") are normalized as the current active frequency.
* **Taxonomy Rules**:
  * "Seizure-free since [Year]" must be extracted as `seizure free since YEAR`.
  * A temporary seizure-free window (e.g. 4 months) in a patient with a baseline rate must not collapse the active rate unless they meet the gold definition of long-term freedom.

---

## 3. Preregistration Guidelines for Future Gan Arms

No new optimizer arms (GEPA G3+) or prompt policy modifications may be run without satisfying the following:

1. **Gate Control**: Any new arm must run first on the cap-25 subset, and may only proceed to full validation if cap-25 monthly accuracy is $\ge 84\%$.
2. **Key Controls**: The candidate builder gap v1 patterns in `src/clinical_extraction/gan/temporal_candidates.py` must remain frozen as the baseline.
3. **API Key Checks**: Start-time preflight checks must verify active key residency to prevent silent mock fallback during comparisons.
