# Agent Instructions — Spec-Driven Development

Applies to all agents (this file is symlinked to `CLAUDE.md` and
`.github/copilot-instructions.md`). It defines **what** to do, not **how** —
each agent model decides its own mechanism (skills, hooks, prompts, subagents).

## Source-of-truth hierarchy (no overlap)

- **`AGENTS.md`** (this file) = the **generic, portable workflow spec** — process, file
  structure, and templates. Identical for any project, so it is self-contained for
  bootstrapping a new repo.
- **`.ai/README.md`** = the **project-specific human description** (one-liner, seed doc,
  files-at-a-glance). Humans only.
- **`.ai/*.md`** = the **filled-in per-project facts** (constraints, roadmap, status,
  decisions, philosophy).

Keep this file generic. Project-specific content never goes here — it goes in `.ai/`.

## Single source of truth

All project facts live in `.ai/`. Read them **on demand** for the task type — never load
everything.

## File table (read tier · cap)

| File | Purpose | Read by agents | Cap |
|---|---|---|---|
| `03_CURRENT_STATUS.md` | one-point current state (now/next/blocked) | **Tier 0 — always** | 80 lines |
| `00_CONSTRAINTS.md` | tech hard rules (forbidden/required) | Tier 1 — code/arch | 80 lines |
| `02_ROADMAP.md` | goals = *what*, not *how* | Tier 1 — planning/scope | 80 lines |
| `00_PHILOSOPHY.md` | design principles / rationale | Tier 2 — arch / new patterns | 80 lines |
| `README.md` | human entry, brainstorming | **Tier 3 — humans only** | no cap |
| `decisions/index.md` | decision log (agent surface) | Tier 1 — conflict/scope | 80 lines |
| `decisions/ADR-NNN-*.md` | decision deep-dive | only if index entry is not enough | git |
| `archive/` | history | **never auto-read** | git |

## Read workflow (by task type)

- **Code** → `03_CURRENT_STATUS` → `00_CONSTRAINTS` → `02_ROADMAP`. Read
  `decisions/index.md` only if a conflict or scope question arises.
- **Architecture / new module / new pattern** → additionally `00_PHILOSOPHY`.
- **Planning / scope** → `02_ROADMAP` + `03_CURRENT_STATUS`.
- **Debugging / "why"** → `03_CURRENT_STATUS` first, then grep `archive/` only if needed.
- **Q&A / explanation** → read nothing (status only if it helps).
- **Heavy initial design** → `README` (the only case agents read it).

## Size caps + archive (hard rule)

1. Every live file has a hard cap (table above).
2. Over cap → keep the **active tail** in place, move the rest to
   `archive/YYYY-MM-<name>.md`.
3. `archive/` is **outside the agent read path** — never loaded by default.
   History lives in git; do not duplicate it into agent context.
4. `_updated:` stamp on each live file is the staleness signal; bump it whenever
   the file is edited. If the stamp contradicts the code, flag it, don't guess.

## Update rules (kill churn)

- `03_CURRENT_STATUS` → current **actionable state, not session history**. Update it
  whenever the actionable state changes; the CLOSE step verifies whether an update is needed.
- `00_CONSTRAINTS` / `02_ROADMAP` / `00_PHILOSOPHY` → update **only when their
  content actually changes**. Most tasks leave them untouched.
- `README` → never touched by agents.
- `decisions/index.md` → append a row whenever a significant decision is made.

## Decisions

- Agents read `decisions/index.md` for conflict/scope checks. Each row carries a
  **summary** so you can act without opening the ADR file.
- **Do not open individual ADR files** except when the index entry is not enough
  (e.g. a waiver is in force and you need the exact quoted constraint) — or when you are
  implementing or changing the behavior an ADR governs.
- ADRs are human deep-dives. When you make a decision: create the ADR file AND
  append a summary row to the index.
- **Create an ADR only for significant decisions** — ones that change architecture,
  externally observable behavior, important algorithms, data contracts, or a project
  constraint. Do **not** create ADRs for ordinary implementation choices.
- **Never silently diverge from an active ADR.** If implementation shows an active ADR is
  wrong, do not quietly reinterpret or bypass it — update it explicitly, or create a new
  ADR that supersedes it.
- **An ADR cannot silently override a constraint** — that requires an explicit `Waiver`.
- Statuses: `Proposed` (not yet normative; flag for human approval) → `Active` →
  `Superseded`, or → `Rejected`.

## Session contract loop

- **OPEN** — read Tier-0 `03_CURRENT_STATUS` (+ Tier-1 per task type). Restate the
  current state in 1–2 lines and state what you will do.
- **DO** — read any ADR that governs the behavior you are implementing, then implement
  the smallest change that satisfies the request. Grep code before assuming APIs. Verify
  against the ADR's specification and run relevant tests.
- **REPORT** — summarize what changed and why; name the `.ai/` files consulted.
- **CLOSE (mandatory, every session)**:
  1. Update `03_CURRENT_STATUS` (always) — move done → NEXT, update blockers, bump `_updated`.
  2. Append to `decisions/index.md` (+ create ADR file) if a decision was made.
  3. Archive anything over its size cap.
  4. State the next step (one line).

## Bootstrap (new repository)

If `.ai/` is missing, create the skeleton before writing any code. Populate `00_CONSTRAINTS.md` and `03_CURRENT_STATUS.md` first — the minimum viable context.

```bash
mkdir -p .ai/decisions .ai/archive
touch .ai/README.md
touch .ai/00_CONSTRAINTS.md
touch .ai/00_PHILOSOPHY.md
touch .ai/02_ROADMAP.md
touch .ai/03_CURRENT_STATUS.md
touch .ai/decisions/index.md
```

No `sessions/` folder — git history is the development diary. When a live file exceeds its cap, keep the active tail and move the rest to `archive/YYYY-MM-<name>.md`.

## Templates

Use these to scaffold the `.ai/` files. Fill the placeholders with project facts.

### `00_CONSTRAINTS.md` (cap 40)
```markdown
# Constraints
Hard rules. Non-negotiable unless an ADR with a `Waiver:` field explicitly overrides one.

## Required Technologies
- Must use: [technology] — Reason: [why]

## Forbidden Technologies
- Never use: [technology] — Reason: [why]

## Forbidden Patterns
- [pattern]: [why it is forbidden]

## External Boundaries
- [e.g. read-only data dirs, no outbound calls in training loops]

_Last updated: YYYY-MM-DD_
```

### `00_PHILOSOPHY.md` (cap 40)
```markdown
# Design Philosophy
Guidance, not rules. These evolve as the project matures.

## Core Principles
- [principle]: [what it means in practice]

## Architectural Style
- [e.g. explicit over implicit, flat over nested, boring over clever]

## What We Optimise For
- [e.g. correctness of the forward operator, reproducibility]

## What We Accept as Trade-offs
- [e.g. compute-heavy dataset build to keep the training loop clean]

_Last updated: YYYY-MM-DD_
```

### `02_ROADMAP.md` (cap 40)
```markdown
# Roadmap

## Current Phase: [name]
**Goal:** [one sentence]
**Target date:** YYYY-MM-DD
### In scope
- [list]
### Out of scope
- [list]

## Upcoming Phases
- [phase]: [one-line goal]

## Completed Phases
- [phase] — completed YYYY-MM-DD

_Last updated: YYYY-MM-DD_
```

### `03_CURRENT_STATUS.md` (cap 30)
```markdown
# Current Status

## NOW
- [ ] actively in progress
- [ ] blocked — [reason]

## NEXT
- [ ] next priority
- [ ] then...

## KNOWN_ISSUES
- Bug: [desc] — Workaround: [if any] — Impact: [low/medium/high]
- Debt: [desc] — Impact: [low/medium/high]

_Last updated: YYYY-MM-DD_
```

### `decisions/index.md` (cap 80)
```markdown
# Decision Index

> Agents act on this table (Tier 1) and **do not open ADR files** unless a summary is not
> enough (e.g. a waiver in force) or you are implementing an ADR's behavior. ADRs are human
> deep-dives. Keep one row per decision; archive superseded rows.

| ADR | Title | Status | Date | Summary (what + key consequence) |
|---|---|---|---|---|
| ADR-001 | [title] | Active | YYYY-MM-DD | [one-line what + consequence] |
```

### `decisions/ADR-NNN-title.md`
```markdown
# ADR-NNN: [Title]
- **Status:** Proposed | Active | Rejected | Superseded by ADR-NNN
- **Date:** YYYY-MM-DD
- **Author:** [name or session]

## Context
[What prompted this decision?]

## Decision
[What was decided and why?]

## Resulting Specification
[Normative: what the code must now do. Concrete, testable statements — the contract this
decision establishes.]
- [must ...]
- [must ...]

## Alternatives Considered
- [A]: rejected because [reason]

## Consequences
- Positive: [what becomes easier]
- Negative: [what becomes harder]

## Verification
[Optional: tests/checks that prove the resulting specification holds.]
- [ ] [check]

## Waiver
[Only if this overrides a rule in 00_CONSTRAINTS.md. Quote the exact constraint.]
```
