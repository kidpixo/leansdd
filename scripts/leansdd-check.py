#!/usr/bin/env python3
"""Lean SDD consistency check. Stdlib only, zero LLM tokens.

Usage: python scripts/leansdd-check.py [check] [path/to/.agents ...]   (default: check .agents)
       python scripts/leansdd-check.py stamp [path/to/.agents ...]
       python scripts/leansdd-check.py next-adr [path/to/.agents]
       python scripts/leansdd-check.py archive [--dry-run] [path/to/.agents]
Check exits 1 on any ERROR; WARN never fails the run. Caps are read from the
file table in AGENTS.md (single source of truth).
"""
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

PROPOSED_DAYS = 14
STALE_COMMITS = 25
STAMP = re.compile(r"_Last updated: (\d{4}-\d{2}-\d{2})(?: @ ([0-9a-f]{7,40}))?_")
findings = []


def add(level, where, msg):
    findings.append((level, where, msg))


def git(*args, cwd):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip()


def find_agents(start):
    for d in [start, *start.parents]:
        if (d / "AGENTS.md").is_file():
            return d / "AGENTS.md"
    return None


def table_caps(agents_text):
    """Parse '| `file` | ... | N lines |' rows of the AGENTS.md file table."""
    caps = {}
    for line in agents_text.splitlines():
        m = re.match(r"^\| `([^`]+)` \|.*\| (\d+) lines \|\s*$", line)
        if m:
            caps[m.group(1)] = int(m.group(2))
    return caps


def setting(text, key):
    m = re.search(rf"^\s*[-*]?\s*{re.escape(key)}:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else None


def overrides(constraints_text):
    raw = setting(constraints_text, "Cap overrides") or ""
    out = {}
    for name, n in re.findall(r"`?([\w./-]+?)(?:\.md)?=(\d+)`?", raw):
        out[name] = int(n)
    return out


def check_caps_and_stamps(ai, root, caps, ov, in_git):
    for name, cap in caps.items():
        f = ai / name
        if not f.is_file():
            continue
        text = f.read_text()
        n = len(text.splitlines())
        limit = ov.get(name.removesuffix(".md"), cap)
        if n > limit:
            add("ERROR", name, f"{n} lines, cap is {limit}")
        if not name.endswith(".md"):
            continue
        stamps = STAMP.findall(text)
        if not stamps:
            add("ERROR", name, "missing stamp '_Last updated: YYYY-MM-DD @ <hash>_'")
            continue
        day, h = stamps[-1]
        try:
            datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            add("ERROR", name, f"bad stamp date {day}")
        if not in_git:
            continue
        if not h:
            add("ERROR", name, "stamp has no '@ <hash>' (project is under git)")
            continue
        ok, _ = git("cat-file", "-e", f"{h}^{{commit}}", cwd=root)
        if not ok:
            add("ERROR", name, f"stamp hash {h} not found in git")
            continue
        ok, cnt = git("rev-list", "--count", f"{h}..HEAD", cwd=root)
        if ok and cnt.isdigit() and int(cnt) > STALE_COMMITS:
            add("WARN", name, f"stamp is {cnt} commits behind HEAD")


def parse_index(index_text):
    rows, cols = [], []
    for line in index_text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "ADR":
            cols = [c.lower() for c in cells]
        elif cols and re.match(r"ADR-\d+", cells[0]):
            rows.append(dict(zip(cols, cells)))
    return rows


def check_decisions(ai):
    dec = ai / "decisions"
    index = dec / "index.md"
    if not index.is_file():
        return
    rows = parse_index(index.read_text())
    files = {re.match(r"(ADR-\d+)", p.name).group(1): p
             for p in dec.glob("ADR-*.md") if re.match(r"ADR-\d+", p.name)}
    by_id = {r["adr"]: r for r in rows}
    for adr in sorted(set(files) - set(by_id)):
        add("ERROR", f"decisions/{files[adr].name}", "ADR file has no row in index.md")
    for adr in sorted(set(by_id) - set(files)):
        add("ERROR", "decisions/index.md", f"{adr} has a row but no ADR file")
    for adr, row in by_id.items():
        if not row.get("scope"):
            add("ERROR", "decisions/index.md", f"{adr} has no Scope")
        if adr not in files:
            continue
        text = files[adr].read_text()
        m = re.search(r"\*\*Status:\*\*\s*(\w+)", text)
        status = m.group(1) if m else ""
        idx_status = (row.get("status", "").split() or [""])[0]
        if status != idx_status:
            add("ERROR", f"decisions/{files[adr].name}",
                f"status '{status}' differs from index '{idx_status}'")
        if status == "Active":
            v = re.search(r"## Verification\n(.*?)(?=\n## |\Z)", text, re.S)
            if not v or not re.search(r"^- \[[ x]\]\s*\S", v.group(1), re.M):
                add("ERROR", f"decisions/{files[adr].name}", "Active ADR has no Verification check")
        if status == "Proposed":
            try:
                age = (date.today() - datetime.strptime(row.get("date", ""), "%Y-%m-%d").date()).days
                if age > PROPOSED_DAYS:
                    add("WARN", f"decisions/{files[adr].name}", f"Proposed for {age} days")
            except ValueError:
                add("WARN", "decisions/index.md", f"{adr} has no valid date")


def check_spec_version(agents_text, constraints_text):
    m = re.search(r"^Spec version:\s*(\d+)", agents_text, re.M)
    theirs = setting(constraints_text or "", "Spec version")
    if not m:
        return
    if not theirs or not theirs.strip("[]").isdigit():
        add("WARN", "00_CONSTRAINTS.md", f"no Spec version (AGENTS.md is {m.group(1)}); see CHANGELOG.md")
    elif int(theirs) != int(m.group(1)):
        add("WARN", "00_CONSTRAINTS.md", f"Spec version {theirs} vs AGENTS.md {m.group(1)}; see CHANGELOG.md")


def locate(ai_path):
    """Resolve an .agents dir, its AGENTS.md, repo root, and constraints text."""
    ai = Path(ai_path).resolve()
    if not ai.is_dir():
        raise SystemExit(f"error: {ai} is not a directory")
    agents = find_agents(ai.parent)
    if not agents:
        raise SystemExit(f"error: AGENTS.md not found in any parent of {ai}")
    root = agents.parent
    cons = ai / "00_CONSTRAINTS.md"
    return ai, agents.read_text(), root, cons


def stamp_file(path, root):
    """Refresh the trailing stamp with today's date and the current HEAD hash."""
    text = path.read_text()
    m = STAMP.search(text)
    ok, h = git("rev-parse", "--short", "HEAD", cwd=root)
    new = f"_Last updated: {date.today().isoformat()} @ {h}_" if ok and h else \
          f"_Last updated: {date.today().isoformat()}_"
    if not m:
        text = text.rstrip("\n") + "\n\n" + new + "\n"
        print(f"stamped (no prior stamp): {path}")
    else:
        text = text[:m.start()] + new + text[m.end():]
        print(f"stamped: {path}")
    path.write_text(text)


def next_adr(ai):
    """Print the next free ADR number, e.g. ADR-004."""
    dec = ai / "decisions"
    nums = [int(m.group(1)) for p in dec.glob("ADR-*.md")
            if (m := re.match(r"ADR-(\d+)", p.name))]
    index = dec / "index.md"
    if index.is_file():
        nums += [int(m.group(1)) for m in re.finditer(r"\bADR-(\d+)\b", index.read_text())]
    print(f"ADR-{max(nums, default=0) + 1:03d}")


def archive_over_cap(ai, agents_text, cons_text, dry_run=False):
    """Move over-cap live files to archive/YYYY-MM-<name>.md, keeping the active tail."""
    caps = {**table_caps(agents_text), **overrides(cons_text)}
    dec_index = ai / "decisions" / "index.md"
    moved = []
    for name, cap in caps.items():
        f = ai / name
        if not f.is_file() or f == dec_index:
            continue
        text = f.read_text()
        # strip any trailing stamp: the archive keeps it, the live tail gets a fresh one
        head_text = STAMP.sub("", text).rstrip("\n")
        lines = head_text.splitlines(keepends=True)
        # reserve room for the blank line + fresh stamp, which count toward the cap
        room = max(cap - 2, 1)
        if len(lines) <= room:
            continue
        keep = lines[-room:]
        cut = lines[:-room]
        live = "".join(keep).rstrip("\n")
        stamp = f"_Last updated: {date.today().isoformat()} @ " \
                f"{git('rev-parse', '--short', 'HEAD', cwd=ai.parent)[1]}_"
        dest = ai / "archive" / f"{date.today().isoformat()}-{f.name}"
        if dry_run:
            print(f"would archive {len(cut)} lines of {name} -> {dest}")
        else:
            dest.parent.mkdir(exist_ok=True)
            header = f"# Archive of {name} (archived {date.today().isoformat()})\n\n"
            dest.write_text(header + text)  # archived copy = original, stamp included
            f.write_text(live + "\n\n" + stamp + "\n")
            print(f"archived {len(cut)} lines of {name} -> {dest}")
        moved.append(name)
    return moved


def cmd_check(argv):
    global findings
    targets = [Path(a).resolve() for a in (argv or [".agents"])]
    for ai in targets:
        if not ai.is_dir():
            add("ERROR", str(ai), "not a directory")
            continue
        agents = find_agents(ai.parent)
        if not agents:
            add("ERROR", str(ai), "AGENTS.md not found in any parent directory")
            continue
        agents_text = agents.read_text()
        root = agents.parent
        in_git = git("rev-parse", "--git-dir", cwd=root)[0]
        cons = ai / "00_CONSTRAINTS.md"
        cons_text = cons.read_text() if cons.is_file() else ""
        check_caps_and_stamps(ai, root, table_caps(agents_text), overrides(cons_text), in_git)
        check_decisions(ai)
        check_spec_version(agents_text, cons_text)
    for level, where, msg in sorted(findings):
        print(f"{level:5} {where}: {msg}")
    errors = sum(1 for f in findings if f[0] == "ERROR")
    print(f"{errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if errors else 0


def cmd_stamp(argv):
    for target in (argv or ["."]):
        ai, _, root, cons = locate(target)
        stamp_file(cons, root)  # constraints first: settings may gate the session
        for name in ("00_PHILOSOPHY.md", "01_STRUCTURE.md", "02_ROADMAP.md",
                     "03_CURRENT_STATUS.md", "decisions/index.md"):
            f = ai / name
            if f.is_file():
                stamp_file(f, root)
    return 0


def cmd_next_adr(argv):
    ai, _, _, _ = locate(argv[0] if argv else ".agents")
    next_adr(ai)
    return 0


def cmd_archive(argv):
    args = [a for a in argv if a != "--dry-run"]
    dry = "--dry-run" in argv
    ai, agents_text, root, cons = locate(args[0] if args else ".agents")
    moved = archive_over_cap(ai, agents_text,
                             cons.read_text() if cons.is_file() else "", dry_run=dry)
    if not moved:
        print("nothing over cap")
    return 0


USAGE = """usage: leansdd-check.py [check] [path/.agents ...]   consistency check (default)
       leansdd-check.py stamp [path/.agents ...]     refresh stamps (date + HEAD hash)
       leansdd-check.py next-adr [path/.agents]      print the next free ADR number
       leansdd-check.py archive [--dry-run] [path/.agents]  move over-cap lines to archive/
"""


def main(argv):
    cmd, *rest = (argv or ["check"])
    if cmd in ("check", "-c"):
        return cmd_check(rest)
    if cmd == "stamp":
        return cmd_stamp(rest)
    if cmd == "next-adr":
        return cmd_next_adr(rest)
    if cmd == "archive":
        return cmd_archive(rest)
    if cmd in ("-h", "--help", "help"):
        print(USAGE, end="")
        return 0
    # backward compatibility: a bare path (absolute, relative, or /tmp style)
    if cmd[0] in "/.~" or Path(cmd).is_dir() or Path(cmd).is_file():
        return cmd_check(argv)
    print(USAGE, end="", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
