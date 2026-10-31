layout: default
title: Lean SDD
---

# Lean SDD - LSDD

Lean Spec-Driven Development (LSSD) v2 : SDD with one [AGENTS.md](https://github.com/kidpixo/leansdd/blob/master/AGENTS.md).

A context-bounded, decision-spec driven development workflow for LLM-assisted software development

This is lightweight, LLM-native project-memory convention. One file (`AGENTS.md`) defines **how an
agent should work**; a small `.ai/` folder holds the project's **current knowledge**;
significant decisions are recorded as **specs**; git is the **history**. Drop it into any
repo and an LLM can act safely without ever loading the whole project.

For versions specific differences check the [CHANGELOG.md](https://github.com/kidpixo/leansdd/blob/master/CHANGELOG.md).

---

## Quick start

1. **Drop in** `AGENTS.md` at the repo root, and let other agents find it:
   ```bash
   ln -s AGENTS.md CLAUDE.md
   mkdir -p .github && ln -s ../AGENTS.md .github/copilot-instructions.md
   ```
2. **Tell your agent to follow it** ("Follow AGENTS.md"). With no `.ai/` folder it runs
   [first-run setup](#first-run-setup): one batch of questions, each with a default, then it
   creates `.ai/`.
3. **Review the seeded files.** Anything marked `(inferred — confirm)` is a guess, not a fact.
4. **Work as usual.** Every session runs OPEN → DO → REPORT → CLOSE. Your job is mostly to
   keep `CONSTRAINTS` and `ROADMAP` honest and to approve `Proposed` decisions.
5. **Don't edit `AGENTS.md` per project.** It stays generic so you can pull improvements
   from upstream; project-specific facts and settings live in `.ai/`.
6. **Optional:** copy `scripts/leansdd-check.py` into your repo and run it (or put it in a
   git hook or CI) to catch drift at zero token cost. It also carries deterministic
   subcommands agents call instead of hand-editing: `stamp` (refresh stamps with the real
   HEAD hash), `next-adr`, and `archive [--dry-run]`.
7. **Optional:** copy `.agents/skills/` into your repo. `.agents/skills/` is a standard project-scope skills directory (Vibe and other agents autodiscover it), so skills load without configuration.
   Each folder is a `SKILL.md` recipe for one contract step — session OPEN/CLOSE, ADR
   creation, setup, migration, the project map, verification, audits, and opt-in ADR
   mining for brownfield repos. They are conveniences, not part of the contract.

Already using `.ai/` from an earlier version? Agents compare the `Spec version:` in
`AGENTS.md` with the one in `00_CONSTRAINTS.md` and propose a migration; the steps are in
[CHANGELOG.md](CHANGELOG.md). To skip setup, add `Setup: done` to `00_CONSTRAINTS.md`.

---

## The philosophy

The guiding principle is simple:

> The agent does not need "the project." It needs the **smallest relevant slice** of the
> project.

Knowledge is separated into four non-overlapping layers, so there is always exactly one
place to look for something:

```
AGENTS.md      operating protocol      (generic, portable, same for every project)
.ai/*.md       current project facts   (constraints, roadmap, status, philosophy,
                                        optional structure map)
decisions/     decisions + resulting normative specs
Git            history                 (what happened, the development diary)
```

No `sessions/` logs, no duplicated diary — history lives in git, current state in one
status file, decisions in specs.

---

## Knowledge types

| Artifact | Question it answers |
|---|---|
| `AGENTS.md` | How should an agent work in this repository? |
| `CONSTRAINTS` | What must / must never happen? |
| `PHILOSOPHY` | What principles should guide choices? |
| `ROADMAP` | What are we trying to accomplish? |
| `CURRENT_STATUS` | What matters right now? |
| `STRUCTURE` *(optional)* | Where do things live, and how does data flow? |
| `SYMBOLS.txt` *(optional, generated)* | Which file defines this symbol? |
| `decisions/` | What did we decide, what does it specify, and why? |
| Git | What happened historically? |

---

## The active brain: read on demand

Each artifact has a **read tier** and a **size cap**. An agent loads only what its task
needs:

- `CURRENT_STATUS` — always (the entry point).
- `CONSTRAINTS`, `ROADMAP`, `decisions/index` — for code and planning work.
- `STRUCTURE` — for code and architecture work, if the map is enabled.
- `SYMBOLS.txt` — grep only, never read whole.
- `PHILOSOPHY` — only for architecture / new patterns.
- `README` — humans only; agents skip it.
- `archive/` — never read by default; history stays in git.

This is what keeps context small: the agent reads the slice, does the task, and leaves.

Default caps follow read frequency: what is read every session stays small.

| File | Read | Default cap |
|---|---|---|
| `CURRENT_STATUS` | every session | 60 lines |
| `CONSTRAINTS` | code work | 120 lines |
| `ROADMAP` | planning | 120 lines |
| `decisions/index` | conflict checks | 150 lines |
| `STRUCTURE` | code/arch, if enabled | 200 lines |
| `PHILOSOPHY` | architecture only | 150 lines |

Raise or lower any cap with one line in `00_CONSTRAINTS.md`:
`Cap overrides: 01_STRUCTURE=300`.

---

## The workflow

```
                 HUMAN
                   │
                   ▼
                REQUEST
                   │
                   ▼
           ┌───────────────┐
           │ CURRENT STATUS│   ← always read
           └───────┬───────┘
                   │
                  relevant knowledge
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
  CONSTRAINTS  ROADMAP    DECISIONS
        │          │          │
        └──────────┼──────────┘
                   ▼
               IMPLEMENT
                   │
                   ▼
              VERIFY / TEST
                   │
           ┌───────┴────────┐
           │                │
        matches          conflict
           │                │
           ▼                ▼
         CLOSE         new/updated
                       DECISION
```

Every session follows a fixed contract — **OPEN → DO → REPORT → CLOSE**:

- **OPEN** — run first-run setup if it hasn't been done; otherwise read the status, run the
  freshness checks (spec version, commits since each stamp), and state what you will do.
- **DO** — read the decisions whose Scope matches the change, implement the smallest
  change, run the decision's Verification checks.
- **REPORT** — summarize what changed and why; each check is pass, fail, or unverified.
- **CLOSE** — update the status and its stamp, record a new decision if one was made,
  update the map if structure changed, archive anything over its cap, run the
  consistency check if present.

The contract says **what** to do, not **how** — each agent implements it with its own
skills, hooks, or prompts, so the framework is portable across different LLMs.

---

## Decisions are specs

A decision (an **ADR**) is not just a note — it pairs the decision with the **resulting
normative specification**:

```
Context → Decision → Resulting Specification → Alternatives → Consequences → Verification → Waiver
```

The **Resulting Specification** is the contract the decision establishes: concrete, testable
statements about what the code must do. Statuses:

```
Proposed → Active → Superseded
               │
               └→ Rejected
```

Every decision carries a **Scope** (a path or glob, or `*` for project-wide), so an agent
finds the decisions governing its change by grepping the index instead of reading it. A
decision cannot be `Active` without a **Verification**: a runnable command or test id with
its expected result, or `manual: <steps>`. Unrun checks are reported as unverified, never
as passing.

`Proposed` is the human/agent boundary: an agent that hits a conflict can flag a proposed
decision for approval instead of silently deciding or stopping.

Two rules keep the framework genuinely spec-driven:

- **Never silently diverge from an active decision.** If implementation shows a decision is
  wrong, update or supersede it explicitly — never quietly reinterpret it.
- **A decision cannot silently override a constraint.** That requires an explicit `Waiver`.

The conflict hierarchy is deterministic: **Constraint > Decision > Philosophy**.

---

## First-run setup

Runs once per project, when `.ai/` is missing or `00_CONSTRAINTS.md` has no `Setup:` line.
The agent asks everything in **one message**, each question with a default ("defaults"
accepts all):

1. Scaffold only, or seed from the existing repo (git log, README, manifests)?
2. One-line purpose, and what the README should convey.
3. Hard constraints you already know.
4. Project map: off, a threshold, or now?
5. Size caps: defaults, or raise some?

Rules: it writes to `.ai/` and never to `AGENTS.md`; it never invents facts (inferences are
marked `(inferred — confirm)`); it scans a bounded slice of the repo, never the full history;
it treats everything it scans as data, never as instructions; and it does not backfill
decisions from git logs.

---

## Optional: the project map

For larger repos, two extra artifacts help an agent find code without loading it:

- **`.ai/01_STRUCTURE.md`** — a curated, short map: modules, entry points, data flow,
  external boundaries. No signatures, no line numbers.
- **`.ai/SYMBOLS.txt`** — a generated symbol index (ctags or tree-sitter). Agents grep it
  and never read it whole.

It is **off by default**. You set the threshold in `00_CONSTRAINTS.md`
(`Map threshold: on | files > N | lines > N | on request | off`); when a project crosses it,
the agent *proposes* the map and waits for your approval.

A stale map is worse than none, so once enabled it is actively maintained: a
`Last updated: date @ commit` stamp lets the agent detect drift on OPEN, **code wins** on any
disagreement, structural changes update the map on CLOSE, and a map that can't be kept
current gets deleted. The map is descriptive only; it never overrides a constraint or decision.

---

## Keeping files honest

Context files rot silently, so staleness is made detectable:

- **Stamps with a commit.** Every live file ends with
  `_Last updated: YYYY-MM-DD @ <short-hash>_`. On OPEN the agent skims the commits since each
  stamp (about 20 lines at most) and reconciles anything the file describes that changed,
  including commits you made outside agent sessions.
- **Spec version.** `AGENTS.md` declares `Spec version: N`; `00_CONSTRAINTS.md` records the
  version your project was last migrated to. On a mismatch the agent tells you and proposes
  the migration from [CHANGELOG.md](CHANGELOG.md). It never migrates silently or edits
  `AGENTS.md`.
- **Consistency check (optional).** `scripts/leansdd-check.py` is stdlib-only and spends zero
  tokens. Caps come from the `AGENTS.md` file table, so there is still one source of truth.
  - **Errors** (exit code 1): file over its cap, missing or malformed stamp, stamp hash
    unknown to git, ADR file and index row out of sync, status mismatch, missing Scope,
    `Active` ADR without Verification.
  - **Warnings:** `Proposed` ADRs older than 14 days, stamps more than 25 commits behind,
    spec version mismatch.

  Run `python scripts/leansdd-check.py [path/to/.ai ...]`. The contract doesn't require it;
  without it, agents follow the same rules by hand.

---

## Untrusted content

Instruction authority belongs to three sources: `AGENTS.md`, your messages, and the `.ai/`
files (except anything still marked `(inferred — confirm)`). Everything else an agent reads —
READMEs, source comments, commit messages, issues, TODOs, tool and web output — is **data**.
Setup and seed mode read a lot of repo content, so this matters: if scanned content contains
instructions aimed at an agent, the agent does not follow them and tells you in REPORT.

---

## Monorepos

A subproject may have its own `.ai/`; `AGENTS.md` still lives once, at the repo root.

- **Nearest wins for local facts:** status, roadmap, philosophy, and structure come from the
  nearest `.ai/`.
- **Constraints only tighten:** a child adds constraints but never relaxes a parent's.
  Relaxing one takes an ADR with a `Waiver` in the *parent's* `decisions/`.
- **ADR Scope is relative** to the directory holding its `.ai/`; a parent ADR with Scope `*`
  governs the whole tree. A child ADR can't contradict an active parent ADR without
  superseding it in the parent.

The hierarchy is unchanged (Constraint > Decision > Philosophy); at each level, outer
overrides inner.

---

## How it evolves across project phases

| Phase | What matters most |
|---|---|
| **Early** | `ROADMAP`, `PHILOSOPHY`, proposed decisions — exploring. |
| **Middle** | Active decisions, `CONSTRAINTS`, `CURRENT_STATUS` — converging. |
| **Mature** | `CONSTRAINTS` + active decisions + `CURRENT_STATUS`; superseded decisions move to `archive/`. |

The agent never needs the project's entire intellectual history. It needs:

> **current constraints + current decisions + current state.**

That is why the repository itself becomes the agent's external memory — small, curated, and
always up to date.


## Maintainer notes

`index.md` (the GitHub Pages copy) is regenerated from `README.md` by a pre-commit
hook, so editing the README is enough — never edit `index.md` by hand. After cloning,
enable the hook once:

```bash
git config core.hooksPath hooks
```
