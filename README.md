# Lean SDD - LSDD

Lean Spec-Driven Development (LSSD) : SDD with one `AGENTS.md`.

A context-bounded, decision-spec driven development workflow for LLM-assisted software development

This is lightweight, LLM-native project-memory convention. One file (`AGENTS.md`) defines **how an
agent should work**; a small `.ai/` folder holds the project's **current knowledge**;
significant decisions are recorded as **specs**; git is the **history**. Drop it into any
repo and an LLM can act safely without ever loading the whole project.

---

## The philosophy

The guiding principle is simple:

> The agent does not need "the project." It needs the **smallest relevant slice** of the
> project.

Knowledge is separated into four non-overlapping layers, so there is always exactly one
place to look for something:

```
AGENTS.md      operating protocol      (generic, portable, same for every project)
.ai/*.md       current project facts   (constraints, roadmap, status, philosophy)
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
| `decisions/` | What did we decide, what does it specify, and why? |
| Git | What happened historically? |

---

## The active brain: read on demand

Each artifact has a **read tier** and a **size cap**. An agent loads only what its task
needs:

- `CURRENT_STATUS` — always (the entry point).
- `CONSTRAINTS`, `ROADMAP`, `decisions/index` — for code and planning work.
- `PHILOSOPHY` — only for architecture / new patterns.
- `README` — humans only; agents skip it.
- `archive/` — never read by default; history stays in git.

This is what keeps context small: the agent reads the slice, does the task, and leaves.

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

- **OPEN** — read the status and state what you will do.
- **DO** — read any decision governing the change, implement the smallest change, verify.
- **REPORT** — summarize what changed and why.
- **CLOSE** — update the status if needed, record a new decision if one was made, archive
  anything over its cap.

The contract says **what** to do, not **how** — each agent implements it with its own
skills, hooks, or prompts, so the framework is portable across different LLMs.

---

## Decisions are specs

A decision (an **ADR**) is not just a note — it pairs the decision with the **resulting
normative specification**:

```
Context → Decision → Resulting Specification → Alternatives → Consequences → Waiver
```

The **Resulting Specification** is the contract the decision establishes: concrete, testable
statements about what the code must do. Statuses:

```
Proposed → Active → Superseded
               │
               └→ Rejected
```

`Proposed` is the human/agent boundary: an agent that hits a conflict can flag a proposed
decision for approval instead of silently deciding or stopping.

Two rules keep the framework genuinely spec-driven:

- **Never silently diverge from an active decision.** If implementation shows a decision is
  wrong, update or supersede it explicitly — never quietly reinterpret it.
- **A decision cannot silently override a constraint.** That requires an explicit `Waiver`.

The conflict hierarchy is deterministic: **Constraint > Decision > Philosophy**.

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

---

*Framework refined from an external review (ChatGPT, 2026-08).*
