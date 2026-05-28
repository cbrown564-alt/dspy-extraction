# Archive Index

Status: active guidance
Last updated: 2026-05-28

The archive keeps provenance without letting old plans steer the project.

## Current Physical Archive

- `prior-context/` - inherited prompt and error-analysis context from earlier
  project phases.

## Archive Rule

Archive by decision boundary, not by age.

Move or de-authorize a doc when its active decision has been absorbed into a
newer steering doc, component registry, domain README, or paper evidence pack.
Do not delete run IDs, scorer caveats, dataset quirks, rejected arms, or holdout
warnings.

## Next Archive Candidates

See `may28_refocus_archive_plan.md` for the concrete wave plan.

These should be physically moved or given supersession banners in a follow-up
cleanup pass:

- old Gan prompt-policy, verify-repair, temporal-candidate, GEPA, retrieval,
  and targeted-example notes not listed in `experiments/gan/README.md`;
- old ExECT v4.x label-policy implementation trail except the frozen evidence
  row needed for S1 provenance;
- generated registry matrix and research atlas exports that predate the May 28
  pivot;
- stale promoted memory files that point to completed G16/F0 work;
- paper drafts and 20260524 synthesis docs superseded by the May 25 table pack
  and May 28 decomposition docs.

When moving files, leave an index entry with:

- old path;
- new path;
- status label;
- reason for archive;
- replacement active doc.
