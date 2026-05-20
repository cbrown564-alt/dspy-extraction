---
name: tdd
description: Use when implementing a behavior change with test-driven development. First write or update a failing test that captures the desired behavior, then implement the smallest change to pass it, then refactor while keeping tests green. Do not use for purely mechanical refactors or formatting-only changes.
---

# TDD

Follow this loop:

1. Understand the requested behavior.
2. Find the closest existing test file or test pattern.
3. For primitive or bridge behavior, check `data/fixtures/primitive_cases.json` and add a deterministic fixture case when the edge case should be reusable.
4. Write the smallest failing test that captures the new behavior.
5. Run only the relevant test first.
6. Confirm the failure is meaningful and caused by the missing behavior, not setup issues.
7. Implement the smallest production-code change that makes the test pass.
8. Re-run the focused test.
9. Run the broader relevant test suite.
10. For primitive registry or adapter changes, also run `uv run python scripts/validate_primitives.py --errors-only`.
11. Refactor only after tests pass.
12. Summarize:
   - test added
   - implementation changed
   - commands run
   - remaining risks