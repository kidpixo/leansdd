---
name: leansdd-map
description: Load this skill when creating or refreshing the optional Lean SDD project map (01_STRUCTURE.md and SYMBOLS.txt), or when a structure diff on OPEN shows files moved.
---

# Lean SDD project map (01_STRUCTURE + SYMBOLS)

Only for projects where the map is enabled (`Map threshold:` in `00_CONSTRAINTS.md`).
The map is descriptive, never normative; **code wins** on any disagreement.

## Create

1. Walk the top two directory levels and entry points (main, index, app configs).
2. Draft `01_STRUCTURE.md` from the AGENTS.md template: Flow, Modules
   (path → responsibility → entry point), External Boundaries. No signatures,
   no line numbers, no invariants.
3. Generate the symbol index mechanically — never by hand, never from memory:
   `ctags -R -x --output-format=u-ctags . > .ai/SYMBOLS.txt` (or tree-sitter equivalent).
4. Commit it or gitignore it, per the project's choice; if ignored, note in
   `01_STRUCTURE.md` that it is regenerated on OPEN.

## Refresh (OPEN or after structural change)

1. `git diff --name-status <stamp-hash>..HEAD` — if files or directories were added,
   removed, or renamed, refresh the map before starting work.
2. If `SYMBOLS.txt` predates HEAD, regenerate it.
3. If the map disagrees with code, fix the map in the same session.

## Retire

If the map cannot be kept current, delete `01_STRUCTURE.md` and `SYMBOLS.txt`, and
record why in `03_CURRENT_STATUS.md`. A stale map is worse than no map.
