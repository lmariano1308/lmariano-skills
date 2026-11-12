# Workflow demo — one request, every gate

One short case, run end to end, offline, with no credential and no network. It exists so a reader can see what the skills actually do instead of reading six procedures and taking them on faith.

The case: an invoice splits R$ 100,00 into three installments and charges R$ 99,99 in total. The defect is confirmed by a failing test, so the request is a `bugfix`, not an open investigation.

## Run it

```sh
python3 scripts/run_demo.py
```

Requirements: `python3` 3.10 or newer. Nothing else. The script copies [examples/rounding-service](../examples/rounding-service/README.md) into a fresh temporary directory, so the repository is never modified.

Add `--keep` to inspect the working copy after the run.

## Expected output

Only the workspace path and the timestamp vary between runs.

```text
workflow-demo · workspace /tmp/workflow-demo-xxxxxxxx/rounding-service
request: A soma das tres parcelas nao fecha com o total. O defeito esta confirmado pelo teste que falha. Corrija o parcelamento.

[1/7] CLASSIFY — dev-workflow
------------------------------------------------------------------------
Intent: bugfix · Skills: investigation → backend → review-gate → visual-qa → completion-gate · Mode: quick
observed state: a failing test proves the defect; approval covers the correction.

[2/7] CONTEXT — repo-context
------------------------------------------------------------------------
README.md                      26 lines
app/__init__.py                 1 lines
app/pricing.py                 25 lines
preview/index.html             76 lines
qa/check_preview.py           151 lines
tests/test_pricing.py          33 lines
symbol: split_installments · definition app/pricing.py:12
callers: tests/test_pricing.py:6 references

[3/7] IMPLEMENT — the red run first, then the fix
------------------------------------------------------------------------
command: python3 -m unittest discover -s tests -q
exit: 1 · FAILED (failures=2)
--- a/app/pricing.py
+++ b/app/pricing.py
@@ -16,8 +16,10 @@
     """
     if count <= 0:
         raise ValueError("count must be positive")
-    share = total_cents / count
-    return [int(share) for _ in range(count)]
+    share, remainder = divmod(total_cents, count)
+    installments = [share] * count
+    installments[-1] += remainder
+    return installments
 
 
 def format_brl(cents: int) -> str:
exit: 0 · OK

[4/7] REVIEW — review-gate
------------------------------------------------------------------------
target: sha256(diff) f0bf068d2337417e…
spec    : pass — the accepted criterion is asserted by a test
standards: pass
  ok  no float division on money
  ok  no rounding outside the edge
  ok  no bare except
  ok  no debug print
  ok  line length
verification: pass — OK
security : not triggered — the change touches no trust boundary, secret, or input parsing

[5/7] VISUAL QA — visual-qa (static mode)
------------------------------------------------------------------------
Visual QA (static mode) — preview/index.html
check                               measured  expected            result
contrast.ink-on-surface                18.86  >= 4.5              PASS
contrast.ink2-on-surface                7.16  >= 4.5              PASS
contrast.ink-on-bg                     16.72  >= 4.5              PASS
contrast.ink2-on-bg                     6.34  >= 4.5              PASS
contrast.button-label                   5.88  >= 4.5              PASS
document.doctype                        True  html5 doctype       PASS
document.lang                           True  present             PASS
document.viewport                       True  present             PASS
document.title                  Parcelas — serviço  non-empty           PASS
content.visible-by-default              none  none                PASS
layout.control-height                   44px  >= 44px             PASS
layout.max-width                        True  present             PASS
layout.mobile-breakpoint                True  present             PASS
blocking_failures: 0

[6/7] COMPLETION GATE — completion-gate
------------------------------------------------------------------------
category         command                                           exit  claim
focused tests    python3 -m unittest discover -s tests -q          0     behavior verified
visual (static)  python3 qa/check_preview.py                       0     tokens and invariants measured
target identity  sha256(diff)                                      -     unchanged
fresh: 2026-11-12T15:34:55Z · tests: 7 · blocking findings: 0
verdict: pass — every claim maps to a fresh command result

[7/7] INVALIDATION — a mutation stales the evidence
------------------------------------------------------------------------
reviewed target: f0bf068d2337417e…
current target : f1279499a78e3801…
verdict: fail — the worktree changed after review; rerun review and every check

workspace: /tmp/workflow-demo-xxxxxxxx/rounding-service
workspace removed (pass --keep to inspect it)
```

## What each step proves

| Step | Contract it exercises | What the output proves |
|---|---|---|
| 1 | `dev-workflow` routing | The intent is announced before work, with the chain and the mode. A confirmed defect with a failing test enters `bugfix`, not `hotfix`. |
| 2 | `repo-context` | The map is task-scoped: six files, one symbol traced from definition to callers, no repository inventory. |
| 3 | `investigation` (feedback loop) and `backend` | The loop is red before the change and green after it. The failure is observed, not assumed. |
| 4 | `review-gate` | The review is bound to `sha256(diff)`, not to a branch name. Axes are separate; security is explicitly not triggered instead of silently skipped. |
| 5 | `visual-qa` | The pass is measured and labelled `static`. Nothing rendered, so no stronger claim is made. |
| 6 | `completion-gate` | Every claim maps to a fresh command, a scope, and an exit result. The target identity is recomputed and must still match the reviewed one. |
| 7 | Lifecycle rule shared by all six skills | One byte after the gate is enough to invalidate the evidence. The gate fails instead of carrying the old result forward. |

## Files the demo touches

| Path | Role |
|---|---|
| `scripts/run_demo.py` | Orchestrates the seven steps, applies the fix with a real unified diff, computes the target identity |
| `examples/rounding-service/app/pricing.py` | The slice under change; the defect is a float division that drops the remainder |
| `examples/rounding-service/tests/test_pricing.py` | Seven assertions, two red before the fix |
| `examples/rounding-service/preview/index.html` | Page measured by the visual pass |
| `examples/rounding-service/qa/check_preview.py` | Offline visual QA: token contrast, document invariants, control height |

## Dependency and capability disclosure

This demonstration exists to be reproducible anywhere, so it deliberately uses nothing:

| Capability | Used? | Where it would be visible |
|---|---|---|
| MongoDB | no | No driver, no connection string, no collection |
| SQLite | no | No `sqlite3` import, no database file |
| Agent orchestration | no | `scripts/run_demo.py` runs a fixed sequence of local processes; there is no delegation, no subagent, no model call |
| RAG or embeddings | no | No vector store, no retrieval step |
| Claude Code or Codex | no | No external CLI is invoked; the only child processes are `python3 -m unittest` and the QA script |
| Network | no | The script only reads local files and runs local processes |

The import block is the proof for the code path: `scripts/run_demo.py:15-24` imports `argparse`, `difflib`, `hashlib`, `re`, `shutil`, `subprocess`, `sys`, `tempfile`, `datetime`, and `pathlib` — all standard library. The QA script follows the same rule: `examples/rounding-service/qa/check_preview.py:16-19`.

The claim this demo supports is exactly: *the workflow can be executed and verified offline against a real diff*. It does not claim production experience, a database integration, or an agent framework. Those are separate claims and need their own evidence.
