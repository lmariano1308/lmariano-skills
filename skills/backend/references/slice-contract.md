# Slice contract

Copy this into the repository under `docs/contracts/` and fill it before implementation.

```markdown
# Slice <n> — <capability>

Source: <plan or decision that authorized this slice>.

## 1. Behavior

One paragraph in the user's terms. What becomes possible, for whom, and what stays out.

## 2. Schema

Migration: `<number>_<name>`.

- `up`: <statements in prose>.
- `down`: <what is removed>. Destructive only for data this slice created: <yes|no>.
- Validation: `up → down → up` on a local database, result: <observed>.

## 3. Routes

| Method | Path | Role | Body | Response | Errors |
|---|---|---|---|---|---|
| GET | /api/<resource> | owner | — | `{items:[…]}` | 401, 403 |

## 4. Invariants

- <scope filter on every query>
- <numbering through the transactional counter>
- <public surface excludes cost, margin, tax identifier>

## 5. Acceptance criteria

1. <observable behavior, no code reading required>.
2. <observable failure mode>.

## 6. Out of scope

- <explicitly not delivered>
```

## Gate checklist

Record the command and the result for each row. Use `not applicable` only with a reason.

| Category | Command | Result |
|---|---|---|
| format | | |
| lint / static analysis | | |
| build | | |
| focused tests | | |
| relevant suite | | |
| client build | | |
| end-to-end script | | |
| migration up/down/up | | |

## Review questions

- Can every query be traced to a scope filter?
- Does the `down` migration leave the database usable?
- Is any permission enforced only in the client?
- Does the public surface leak a cost, a margin, or a tax identifier?
- Does the acceptance criterion fail if the feature is removed?
