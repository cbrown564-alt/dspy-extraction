# Test/Holdout Reporting Protocol

**Date:** 2026-05-25  
**Scope:** Project-wide methodology rules for evaluating the held-out test split.

---

## 1. Core Mandate

The test/holdout split represents the final, unbiased generalization check of the clinical extraction systems. Once a configuration is run on the test split, **no iterative tuning, prompt engineering, schema changes, or hyperparameter selection is allowed** based on the results.

## 2. Policy Guardrails

1. **Configuration Freeze:**
   - Any config run on the test split must match a corresponding validation config that has already been analyzed and frozen.
   - The only properties modified are:
     - `split_name` (e.g. `exectv2_fixed_v1:test` or `gan_2026_fixed_v1:test`)
     - `report_on_test_split` (`true`)
     - `experiment_id` and output pathways (prefixed with `test_` or `validation_test_`)
2. **One-Shot Evaluation:**
   - A test run is a one-shot operation. Rerunning a test configuration is only permitted if a technical infrastructure error occurs (e.g., local model API timeout, GPU out-of-memory crash). It is never allowed for model-behavior or performance-tuning reasons.
3. **No Validation Overlap:**
   - Test metrics must be documented in separate tables in the manuscript to ensure they are not confused with validation/dev set tuning performance.

## 3. Overnight Execution Protocol

1. **Resource Isolation:**
   - Local model (Ollama / Qwen) executions must run sequentially. No parallel local executions are allowed on the same GPU to prevent OOMs or latency degradation.
2. **Prioritization Gate:**
   - `R1.1` (the schema-validity patch for Qwen exact-policy on Gan validation) must complete first.
   - The overnight test queue executes sequentially thereafter.
