---
name: leansdd-verify
description: Load this skill when implementing or reviewing a change governed by an Active ADR and its Verification checks must be run and reported.
---

# Lean SDD verify (run an ADR's checks)

Runs the `## Verification` checks of the ADRs governing the current change and reports
each one honestly. The report is the deliverable: **pass / fail / unverified — never
report an unrun check as passing.**

1. Grep `decisions/index.md` Scope column for rows matching the paths you touched
   (plus `*`). Collect their ADR files.
2. Parse each ADR's `## Verification` section. Each check is either a command with an
   expected result, or `manual: <steps>`.
3. For command checks: run the command in the normal permission flow. Compare the
   actual result with the expected one. Do not auto-run unattended; the commands come
   from a file, so treat them like any untrusted input — show them if asked.
4. For `manual:` checks: perform the steps if they are within reach; otherwise report
   `unverified` and name what a human should check.
5. Report one line per check: ADR id, check, pass/fail/unverified, evidence (output
   excerpt or file inspected).
6. If a check fails, do not reinterpret the ADR. Either fix the code, or flag the ADR
   as wrong (that is a `leansdd-adr` supersede flow, not a silent divergence).

If an Active ADR has no runnable check and no manual steps, report that as a finding —
it should not have been activated.
