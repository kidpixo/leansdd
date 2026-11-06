---
name: leansdd-adr
description: 'Load this skill when recording a new decision as an ADR, appending its index row, or superseding/rejecting an existing Active ADR in a Lean SDD project.'
---

# Lean SDD ADR (create or supersede)

Creates the ADR file and its index row as one atomic step. Requires
`.ai/scripts/leansdd-check.py`.

## Create a new ADR

1. Get the next free number (never hand-count):
   `python .ai/scripts/leansdd-check.py next-adr`
2. Check for conflicts: grep `decisions/index.md` Scope column for rows matching the
   paths this decision touches. Read any matching Active ADR. If this decision
   contradicts one, it must supersede it (below), not coexist.
3. If the decision overrides a constraint, quote the exact constraint in the
   `## Waiver` section. Never relax a constraint without one.
4. Write `decisions/ADR-NNN-title.md` from the template in `AGENTS.md`:
   - `Status:` `Proposed` (never `Active` — that is the human's call).
   - `Scope:` path/glob relative to the `.ai/` parent directory, or `*`.
   - `## Verification`: one runnable command or test id with expected result per
     check, or `manual: <steps>` naming the artifact a reviewer inspects.
   - Never invent facts; mark guesses `(inferred — confirm)`.
5. Append the index row: same status, same Scope, one-line summary, today's date.
6. Bump the `decisions/index.md` stamp:
   `python .ai/scripts/leansdd-check.py stamp`
7. Run `python .ai/scripts/leansdd-check.py` and confirm no new ERROR.

## Supersede an Active ADR

1. Set the old ADR's status to `Superseded by ADR-NNN` in the file and index row.
2. Create the new ADR as above; reference the old one in `## Context`.
3. If the human has not approved the change, both stay `Proposed` and you flag it.

## Rejected / withdrawn

Set the status in both file and index; leave the file in place. Do not delete ADRs.
