# Minimal Implementation

## The Rule
Build only what is needed right now. Do not add features, refactor, or introduce abstractions beyond what the current task requires.

## What This Means in Practice

- **A bug fix does not need surrounding cleanup** — fix the bug, nothing else
- **A one-shot operation does not need a helper** — inline it
- **Three similar lines is better than a premature abstraction** — extract only when the fourth case appears
- **No half-finished implementations** — if a feature isn't complete, don't merge the skeleton

## What to Avoid

- Empty methods or placeholder functions "for future extensibility"
- Factories, strategies, or adapters without an immediate need
- Generic utilities built speculatively ("we might need this later")
- Configuration options for behavior that only has one case today
- Feature flags or backward-compatibility shims when you can just change the code

## Removal

- Delete exploration artifacts — helper methods created during development that ended up unused
- Remove commented-out code immediately; version control preserves history
- Unused imports, dead branches, and orphaned models are debt — remove promptly

## Refactoring Timing

Refactor when you have a concrete problem to solve (duplication causing a bug, a feature impossible to add cleanly). Refactor in a separate PR from feature work so the diff remains reviewable.
