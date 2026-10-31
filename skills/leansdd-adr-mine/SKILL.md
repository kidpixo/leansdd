---
name: leansdd-adr-mine
description: Load this skill when explicitly asked to propose candidate ADRs for a brownfield repo by mining git history — opt-in, human-confirmed, never run unasked.
---

# Lean SDD ADR mining (brownfield, opt-in)

Reconstructs candidate decisions from an existing repo's history. **Highest
hallucination risk in the framework**: commits suggest decisions, they do not prove
them. Everything produced here is `Proposed`, and nothing becomes `Active` without a
human writing or approving the Verification.

## Mine

1. Bounded scan only:
   - `git log --oneline -100` (never the full history)
   - merge commits and commits touching >30% of the tree (`git log --merges -20`)
   - `git tag` and milestones
   - TODO/FIXME/HACK comments in the top two directory levels
2. Look for *decision-shaped* patterns: "switch X to Y", "remove Z", "never do W"
   (reverted commits and their re-revert), repeated guard-rail fixes.
3. For each candidate, gather **evidence**: commit hashes, before/after file paths.
   No evidence, no candidate.

## Propose

For each candidate, present to the human:
- one-line decision statement, and the evidence for it
- whether the decision still holds today (check the current code)
- a draft Verification check that could prove it

Only after the human confirms a candidate, create the ADR via the `leansdd-adr`
skill, with the human's confirmed statement — not the mined guess — as the Decision.
Mark anything unconfirmed `(inferred — confirm)`.
