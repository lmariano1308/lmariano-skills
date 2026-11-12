# Triage ledger

One row per finding. The ledger is the deliverable of the triage, not the tool output.

```markdown
# Review triage — <target identity>

Target: <commit or diff hash>
Tool: <name and version>
Raw output: <path>

| # | Location | Category | Severity | State | Evidence | Action |
|---|---|---|---|---|---|---|
| 1 | `internal/db/finance.go:88` | bug | high | confirmed | split returns 3333+3333+3333 for 10000/3; test asserts sum | fix in `fix/money-split` |
| 2 | `web/src/settings.tsx:37` | security | high | confirmed | handler `GET /api/profile` returns 200 for role `viewer` | enforce server role |
| 3 | `scripts/verify.sh:46` | security | high | rejected | `eval` receives a constant literal, not environment input | none |
| 4 | `internal/httpapi/export.go:120` | bug | medium | unproven | needs a dataset above 10k rows | request fixture |
```

## States

- `confirmed` — reproduced here. The evidence cell says how, in one line.
- `rejected` — the code does not behave as claimed, or the behavior is intended and documented.
- `unproven` — plausible, blocked by a missing environment, dataset, credential, or approval. Stays out of the backlog; is listed as a limit.

## Counts to report

- total findings, and the count per state;
- confirmed by severity;
- rejected, grouped by the reason they were rejected;
- unproven, with what would unblock each one.

A report that only carries the total is a tool log, not a triage.

## Fix loop

```sh
# 1. fix on a branch, one theme per commit
# 2. rerun the same tool against the fixed target
# 3. rerun the repository gates
```

Stop when no confirmed finding remains. Comment count is not the stopping criterion: a rerun usually surfaces a second layer of related defects, and each one needs the same validation.

## Reporting to the author

- Order by severity inside each category, then by file.
- Quote the exact line and the failure mode, never the raw model text.
- Say what was not reviewed: generated files, vendored code, migrations already applied.
- A security finding names the exposure class: a secret value needs rotation; a topology fact needs redaction. They are not the same ticket.
