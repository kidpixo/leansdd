---
name: leansdd-session
description: 'Load this skill at the start (OPEN) or end (CLOSE) of a working session in a Lean SDD project, when .ai/ files need freshness checks, stamps, archiving, or the consistency check.'
---

# Lean SDD session (OPEN / CLOSE)

Implements the OPEN and CLOSE steps of the session contract in `AGENTS.md` using the
deterministic script, so hashes and archive moves are never hand-made. Requires
`.ai/scripts/leansdd-check.py` in the repo.

## OPEN

1. Run the consistency check:
   `python .ai/scripts/leansdd-check.py`
   Fix nothing silently; report ERRORs to the human, list WARNs.
2. For each live file you will read, skim the commits since its stamp:
   `git log --oneline <hash>..HEAD` (cap the output at ~20 lines per file).
   Reconcile anything the file describes that has changed; flag contradictions.
3. If the spec version in `AGENTS.md` differs from the one in `00_CONSTRAINTS.md`,
   stop and surface the CHANGELOG migration steps — do not migrate in this skill.
4. Restate the current state from `03_CURRENT_STATUS.md` in 1-2 lines and state
   what you will do.

## CLOSE

1. Update `03_CURRENT_STATUS.md` (move done to NEXT, update blockers).
2. Refresh all stamps with real values from git:
   `python .ai/scripts/leansdd-check.py stamp`
3. If a decision was made, use the `leansdd-adr` skill first, then continue.
4. Archive over-cap files, keeping the active tail:
   `python .ai/scripts/leansdd-check.py archive --dry-run` then without `--dry-run`.
5. Re-run `python .ai/scripts/leansdd-check.py`; fix findings or list them for the human.
6. State the next step in one line.

Never invent a commit hash. If the repo is not under git, `stamp` writes date-only
stamps, which is correct.
