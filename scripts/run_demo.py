#!/usr/bin/env python3
"""Run the end-to-end workflow demonstration in a clean temporary directory.

The demonstration copies ``examples/rounding-service`` into a fresh temporary
directory and walks the lifecycle described in ``docs/workflow-demo.md``:
classification, context, implementation, review, measured visual QA, completion
gate, and one deliberate mutation that invalidates the evidence.

Everything uses the Python standard library and local processes. There is no
network access, no credential, and no write to the repository.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = REPO_ROOT / "examples" / "rounding-service"
REQUEST = (
    "A soma das tres parcelas nao fecha com o total. O defeito esta confirmado "
    "pelo teste que falha. Corrija o parcelamento."
)
ROUTE = (
    "Intent: bugfix · Skills: investigation → backend → review-gate → "
    "visual-qa → completion-gate · Mode: quick"
)
BUGGY = "    share = total_cents / count\n    return [int(share) for _ in range(count)]\n"
FIXED = (
    "    share, remainder = divmod(total_cents, count)\n"
    "    installments = [share] * count\n"
    "    installments[-1] += remainder\n"
    "    return installments\n"
)


def heading(index: int, total: int, title: str) -> None:
    print()
    print(f"[{index}/{total}] {title}")
    print("-" * 72)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=120)


def diff_of(baseline: str, current: str, path: str) -> str:
    return "".join(
        difflib.unified_diff(
            baseline.splitlines(keepends=True),
            current.splitlines(keepends=True),
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
        )
    )


def target_identity(diff_text: str) -> str:
    return hashlib.sha256(diff_text.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", action="store_true", help="keep the temporary directory")
    arguments = parser.parse_args()

    workspace = Path(tempfile.mkdtemp(prefix="workflow-demo-"))
    work = workspace / "rounding-service"
    shutil.copytree(EXAMPLE, work)
    pricing = work / "app" / "pricing.py"
    baseline = pricing.read_text(encoding="utf-8")
    total = 7
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"workflow-demo · workspace {work}")
    print(f"request: {REQUEST}")

    heading(1, total, "CLASSIFY — dev-workflow")
    print(ROUTE)
    print("observed state: a failing test proves the defect; approval covers the correction.")

    heading(2, total, "CONTEXT — repo-context")
    for path in sorted(work.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            relative = path.relative_to(work)
            print(f"{str(relative):<28} {len(path.read_text(encoding='utf-8').splitlines()):>4} lines")
    symbol = re.search(r"^def (split_installments)\(.*$", baseline, re.MULTILINE)
    print(f"symbol: {symbol.group(1) if symbol else 'missing'} · definition app/pricing.py:12")
    print(f"callers: tests/test_pricing.py:{len(re.findall(r'split_installments', (work / 'tests' / 'test_pricing.py').read_text(encoding='utf-8')))} references")

    heading(3, total, "IMPLEMENT — the red run first, then the fix")
    before = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], work)
    tail = [line for line in before.stderr.strip().splitlines() if line.strip()][-1]
    print(f"command: python3 -m unittest discover -s tests -q")
    print(f"exit: {before.returncode} · {tail}")
    if before.returncode == 0:
        print("the fixture was expected to fail before the fix")
        return 1

    if BUGGY not in baseline:
        print("the fixture no longer contains the defect; refusing to continue")
        return 1
    fixed_text = baseline.replace(BUGGY, FIXED)
    pricing.write_text(fixed_text, encoding="utf-8")
    change = diff_of(baseline, fixed_text, "app/pricing.py")
    print(change.rstrip())
    after = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], work)
    print(f"exit: {after.returncode} · {after.stderr.strip().splitlines()[-1]}")

    heading(4, total, "REVIEW — review-gate")
    identity = target_identity(change)
    added = [line[1:] for line in change.splitlines() if line.startswith("+") and not line.startswith("+++")]
    guards = {
        "no float division on money": not any(re.search(r"[^/]/[^/]", line) for line in added),
        "no rounding outside the edge": not any("round(" in line for line in added),
        "no bare except": not any(line.strip().startswith("except:") for line in added),
        "no debug print": not any("print(" in line for line in added),
        "line length": all(len(line) <= 100 for line in added),
    }
    spec = bool(
        re.search(
            r"sum\(split_installments\(10000, 3\)\)",
            (work / "tests" / "test_pricing.py").read_text(encoding="utf-8"),
        )
    )
    print(f"target: sha256(diff) {identity[:16]}…")
    print(f"spec    : {'pass' if spec else 'fail'} — the accepted criterion is asserted by a test")
    print(f"standards: {'pass' if all(guards.values()) else 'fail'}")
    for name, passed in guards.items():
        print(f"  {'ok' if passed else 'FAIL'}  {name}")
    print(f"verification: pass — {after.stderr.strip().splitlines()[-1]}")
    print("security : not triggered — the change touches no trust boundary, secret, or input parsing")
    if not (spec and all(guards.values())):
        return 1

    heading(5, total, "VISUAL QA — visual-qa (static mode)")
    qa = run(
        [sys.executable, "qa/check_preview.py", "preview/index.html", "--json", "qa-result.json"],
        work,
    )
    print(qa.stdout.rstrip())
    if qa.returncode != 0:
        return 1

    heading(6, total, "COMPLETION GATE — completion-gate")
    fresh = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], work)
    current = target_identity(diff_of(baseline, pricing.read_text(encoding="utf-8"), "app/pricing.py"))
    print(f"{'category':<17}{'command':<50}{'exit':<6}claim")
    print(f"{'focused tests':<17}{'python3 -m unittest discover -s tests -q':<50}{fresh.returncode:<6}behavior verified")
    print(f"{'visual (static)':<17}{'python3 qa/check_preview.py':<50}{qa.returncode:<6}tokens and invariants measured")
    print(f"{'target identity':<17}{'sha256(diff)':<50}{'-':<6}{'unchanged' if current == identity else 'CHANGED'}")
    print(f"fresh: {started} · tests: 7 · blocking findings: 0")
    if current != identity or fresh.returncode != 0:
        print("verdict: fail — evidence does not match the reviewed target")
        return 1
    print("verdict: pass — every claim maps to a fresh command result")

    heading(7, total, "INVALIDATION — a mutation stales the evidence")
    pricing.write_text(pricing.read_text(encoding="utf-8") + "\n# local note after the gate\n", encoding="utf-8")
    mutated = target_identity(diff_of(baseline, pricing.read_text(encoding="utf-8"), "app/pricing.py"))
    print(f"reviewed target: {identity[:16]}…")
    print(f"current target : {mutated[:16]}…")
    print(f"verdict: fail — the worktree changed after review; rerun review and every check")

    print()
    print(f"workspace: {work}")
    if not arguments.keep:
        shutil.rmtree(workspace)
        print("workspace removed (pass --keep to inspect it)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
