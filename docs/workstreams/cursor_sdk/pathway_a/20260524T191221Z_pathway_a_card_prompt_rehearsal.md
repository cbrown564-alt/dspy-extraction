# Superseded Pathway A Prompt Rehearsal Collision Notice

Date: 2026-05-24
Status: Superseded

Three prompt-only `pathway-a-card` rehearsals were launched in parallel before
`scripts/cursor_sdk_workflows.py` used microsecond-resolution run IDs. They
collided on this second-resolution filename in the machine ledger.

This file is retained so the historical ledger path resolves, but it is not a
valid card prompt. Use the regenerated prompt artifacts instead:

- `docs/workstreams/cursor_sdk/pathway_a/20260524T191244530822Z_pathway_a_card_prompt_rehearsal.md`
- `docs/workstreams/cursor_sdk/pathway_a/20260524T191244917656Z_pathway_a_card_prompt_rehearsal.md`
- `docs/workstreams/cursor_sdk/pathway_a/20260524T191245273197Z_pathway_a_card_prompt_rehearsal.md`

The run ID collision was fixed by changing `_utc_stamp()` to include
microseconds.
