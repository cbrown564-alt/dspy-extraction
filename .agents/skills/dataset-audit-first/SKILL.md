---
name: dataset-audit-first
description: Use before touching dataset loading, gold-label representation, train/dev/test splits, benchmark reproduction, or code that interprets ExECTv2 or Gan labels. Read the local audit docs first and preserve their documented dataset quirks.
---

# Dataset Audit First

Use this skill when work depends on what the ExECTv2 or Gan datasets mean, not just where files live.

Before implementing or changing behavior:

1. Identify which dataset is affected: ExECTv2, Gan, or both.
2. Read the relevant audit before making assumptions:
   - ExECTv2: `docs/exect_gold_label_audit.md`
   - Gan: `docs/gan_2026_label_audit.md`
3. Inspect the raw data shape or manifest when needed:
   - `data/manifests/dataset_manifest.json`
   - `data/splits/exectv2_splits.json`
   - dataset files under `data/`
4. Treat the audit docs as project context, not historical commentary. If current data disagrees with an audit, investigate and document the discrepancy.

## ExECTv2 Checks

When working with ExECTv2:

- Do not infer seizure types from seizure-frequency rows unless the audit explicitly supports it.
- Preserve certainty handling; low-certainty annotations may not belong in flat gold labels.
- Preserve diagnosis specificity collapse where the current design requires it.
- Preserve medication normalization decisions, especially canonical drug names.
- Surface missing or ambiguous gold with quality flags rather than silently treating it as clean negative evidence.
- Be careful with current, historical, and planned medication status. The original data may not encode these cleanly.

## Gan Checks

When working with Gan:

- Treat `seizure_frequency_number[0]` as the gold label.
- Treat `reference` as a secondary cross-check, not gold.
- Preserve the distinction between `unknown` and `no seizure frequency reference`.
- Account for label/reference disagreements as difficulty signals, not automatic gold failures.
- Handle plural units, cluster labels, seizure-free labels, and administrative/no-clinical-content records according to the audit.
- Do not treat summarized secondary evidence as verbatim span evidence.

## Completion Criteria

Before finishing, summarize:

- which audit sections informed the change
- what dataset assumptions the code now relies on
- any unresolved ambiguity or follow-up needed
