---
name: leansdd-audit
description: Load this skill when asked for a periodic Lean SDD hygiene report (audit) — not part of the regular session loop.
---

# Lean SDD audit (hygiene report)

A periodic, report-only pass. **This skill never edits `.ai/` files** — it produces a
findings list for the human, who decides what to act on.

1. Run the consistency check and include its output verbatim:
   `python scripts/leansdd-check.py`
2. Rotting proposals: list `Proposed` ADRs with their age (the script warns after
   14 days; list all of them here with dates).
3. Ghost scopes: for each Active ADR, check whether the paths in its Scope still
   exist (glob relative to the `.ai/` parent). Report scopes matching nothing.
4. Roadmap drift: compare `02_ROADMAP.md` In-scope items against
   `03_CURRENT_STATUS.md` — items done but still in scope, or in NOW but absent
   from the roadmap.
5. Dead constraints: for each hard rule in `00_CONSTRAINTS.md`, grep the codebase
   for evidence it is still relevant; report constraints with no plausible referent
   (best effort — say so, do not judge).
6. Map health (if enabled): commits since the `01_STRUCTURE.md` stamp, and whether
   `SYMBOLS.txt` is older than HEAD.
7. Present everything as a table: finding, severity (high/med/low), suggested owner
   action. End with: "no files were modified."

Stale `Proposed` ADRs are the usual top finding: propose activating, rejecting, or
superseding each one explicitly.
