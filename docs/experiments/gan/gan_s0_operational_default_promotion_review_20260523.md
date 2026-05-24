# Gan S0 Operational Default Promotion Review

Date: 2026-05-23  
Status: **Review Completed; Promotion Recommended**  
Target Arm: `gan_s0_candidate_builder_gap_v1` on GPT 4.1-mini  
Current Operational Default: F0 (`cand_prose_expanded_builders_v1` + prose F0)  
Evidence Reference: `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md`

---

## 1. Overview & Performance Delta

A formal promotion review has been conducted to determine whether the verified candidate-builder gap v1 arm (`gan_s0_candidate_builder_gap_v1`) on GPT 4.1-mini should replace the current operational default for Gan S0.

The verified full-validation rerun (`gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z`) demonstrated a massive, statistically significant performance improvement over the existing F0 default:

| Metric | Current Default (F0 GPT) | Builder-Gap v1 GPT Rerun | Delta |
| --- | ---: | ---: | ---: |
| Monthly-frequency accuracy | 68.1% | **80.6%** | **+12.5pp** |
| Purist category accuracy | — | **86.0%** | — |
| Pragmatic category accuracy | — | **88.6%** | — |
| Normalized-label exact accuracy | — | **71.2%** | — |
| Schema-valid prediction rate | 99.7% | **100.0%** | +0.3pp |
| Evidence quote support rate | 100.0% | **100.0%** | 0.0pp |

The 95% confidence interval for the monthly-frequency accuracy of the new arm is **76.3–85.3%**, completely exceeding the 68.1% default.

---

## 2. Decision Dimensions

### Cost Analysis
- **API Billing**: Both the current default and the target arm use GPT 4.1-mini. The target arm does not add LLM calls; it only expands the deterministic candidates generated locally in Python and passes them as prose in the prompt. While the expanded candidate list slightly increases prompt tokens, the difference is negligible (a few hundred tokens per record, totaling less than $0.05 across the entire 299-record validation set).
- **Compute Overhead**: The expanded deterministic builders run locally in Python using regular expressions. The local compute overhead is sub-millisecond per record and has no impact on system latency.

### Residual Error Profile
There are 58 monthly-frequency mismatches remaining under the target arm:
- `other_semantic_mismatch`: 17 cases
- `pragmatic_match_monthly_divergence`: 16 cases
- `purist_bin_boundary_within_pragmatic`: 7 cases
- `frequent_undercalled`: 7 cases
- Others (unknown-related, cluster collapses): 11 cases

Importantly, these residual errors are now dominated by model semantic reasoning and labeling policy choices rather than upstream candidate recall omissions. This confirms that the candidate-builder gap v1 successfully resolved the candidate-recall bottleneck identified in the audit.

### Prompt and Policy Surface Freezing
The prompt version is frozen at `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy`. The scorer semantics remain unchanged. Promoting this arm requires no changes to active prompts or validation schemas.

---

## 3. Recommendation

> [!IMPORTANT]
> **Promote** `gan_s0_candidate_builder_gap_v1` on GPT 4.1-mini to the **Operational Default** for the Gan S0 track.
> 
> The current default in `docs/planning/kanban_plan.md` should be updated to reflect this change. GPT 4.1-mini remains the search and reproducibility anchor, but now operates with the updated builder-gap v1 surface.
