---
name: leansdd-migrate
description: 'Load this skill when the Spec version in 00_CONSTRAINTS.md is lower than the one declared in AGENTS.md and a Lean SDD migration has been approved by the human.'
---

# Lean SDD migration

Applies a spec-version migration after human approval. Never runs silently: the
mismatch must already have been surfaced in an OPEN step.

1. Read the migration notes for every version between the project's
   (`00_CONSTRAINTS.md` → `Spec version:`) and the target (top of `AGENTS.md`) in
   `CHANGELOG.md`.
2. Present the concrete steps to the human and get approval.
3. Apply the steps exactly as written in the CHANGELOG. Do not improvise extra
   changes while in the neighborhood.
4. Update `Spec version:` in `00_CONSTRAINTS.md` to the target version.
5. Stamp everything: `python .ai/scripts/leansdd-check.py stamp`
6. Run `python .ai/scripts/leansdd-check.py`; resolve findings.
7. Summarize what changed per version; note anything the human must still do by hand.

If this file's `AGENTS.md` is *older* than the project's recorded version, do not
migrate: flag that `AGENTS.md` is outdated and change nothing.
