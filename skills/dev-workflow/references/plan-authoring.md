# Writing an implementation plan someone else can execute

A plan is executable when a competent engineer who has never seen the repository
can follow it without guessing. Guessing is the failure mode: any unnamed file,
any "add validation here", any "test it works" pushes the work back onto the
reader.

Write the plan in the repository workspace (`.hermes/plans/<timestamp>-<slug>.md`
when the runtime specifies a path, use that exact path instead).

## Anatomy, in this order

1. **Goal** — one sentence, one outcome.
2. **Current context / assumptions** — split hard: *verified facts* (each with the
   file/command that proves it) vs *premissas* that would change the plan if
   false. Add a "where things live" tree so the reader is not hunting.
3. **Verified signatures** — a table of every external symbol the plan calls,
   with its real signature and any inversion of the naive assumption.
4. **Architecture / proposed approach** — 2–3 sentences plus one diagram. Explain
   *why* this shape, not what the boxes are.
5. **Transversal conventions** — the rules that every task inherits (id
   encoding, error shape, pagination, ordering, auth scoping, log hygiene,
   commit format). Stating them once removes them from 60 task bodies.
6. **Phases → tasks**, each task 2–5 minutes of focused work.
7. **Tests / validation** — the TDD cycle per task plus the gate command per
   phase.
8. **Risks, tradeoffs, open questions** — with the blocked phase named for each
   question.

## Rule: verify every symbol before it enters the plan

Never write a function call into a plan from memory. Grep the definition and
copy the signature:

```bash
grep -rnE "^func (New|Start|Stop|Init)" pkg/ libs/ | head -20
grep -n "func (s \*Server) Stop" pkg/health/server.go
grep -nE "^func \(db \*Database\)" libs/connections/postgres/postgres.go
```

Then put the result in the *Verified signatures* table. This catches the class
of error that makes a plan unusable: wrong receiver name, wrong return arity,
`Context` or not, pointer vs value.

Two things to check beyond the signature:

- **Defaults that invert your safety story.** Read the guard you are wrapping.
  A shared DB helper whose write guard reads `EnvBool("WRITE_ENABLED", true)` is
  off unless you set it, and if its blocked `Exec` returns `(zero, nil)` the
  failure is silent — a plan that promises "read-only by default" is then false.
  Say the env var explicitly in the task that wires it.
- **Helper coverage.** If the only guarded method exists for single-row queries,
  say so; multi-row calls need the raw pool and a "never write here" note.

## Rule: every verification is a command plus its expected output

Not "confirm it works". The literal command and the literal line that proves it:

```bash
curl -s 'http://localhost:3010/api/clients?limit=2' -D- | head -12
# HTTP/1.1 200 OK / X-Correlation-Id: <uuid> / "total":4,"hasNext":true
```

When the expected output is a nonzero exit or an error, show that too — a
400 response body is the evidence that the validation path is wired.

## Rule: TDD per task, one commit per task

Each task body is: write the failing test → run it and *see* the failure (paste
the expected failure line) → implement minimally → run it and see PASS (paste the
count) → `gofmt -l .` empty → commit with a Conventional Commit message.

If a task's verification needs a database, service, or fixture that does not
exist, the plan gets a task to create it **first**, not a note saying "assumes a
DB". A disposable fixture (compose file + seed SQL) is cheaper than a plan full
of mocks and it is what makes the SQL actually testable.

## Rule: the plan must reach a demonstrable point early

Order phases so the first vertical slice produces something the user can look
at end to end (UI → endpoint → real database). Name that point explicitly ("end
of phase N = first demonstrable delivery") so the user knows when feedback is
possible. Everything after it is additive.

## Rule: record divergence instead of silently fixing it

When the legacy code is wrong (a filter that silently drops rows, a misspelled
column, an inconsistent join), the plan states the old behavior, the new
behavior, and the test that pins the new one. Never normalize a quirk in a task
body without saying so — the reviewer will read it as a regression.

## Rule: missing input is a stated open question, not a gap

If a referenced handoff, spec, or decision document does not exist, say it in the
open questions with what was reconstructed instead of pretending the input was
read. Each open question names the phrase it blocks, so the user can answer the
three that matter and start executing today.

## Rule: proposed paths and packages must obey the repo's local conventions

Read `AGENTS.md` / `CLAUDE.md` / `.cursorrules` **before naming any file**, and
copy the conventions the plan must satisfy into the *Transversal conventions*
section. A plan whose architecture is right but whose paths contradict the repo
is rejected on mechanics, and the reviewer stops trusting the rest of it.

Check every proposed path and import against the local rules:

- **File naming and case.** If the repo mandates a casing scheme (kebab-case),
  no proposed path may use another one, and none may repeat the folder name the
  way a dot-suffix convention would (`repositories/client.go`, not
  `client-repository.go`).
- **Existing shared packages.** Before inventing a package, grep the shared tree
  for the concept (`pkg/errors`, `pkg/config`, `pkg/validation`). If it exists,
  the task says "extend <that package>"; a parallel package is a defect even
  when it looks cleaner.
- **Sanctioned access points.** If env access is centralized, no task may call
  the raw reader (`os.Getenv`) in new code — the flag belongs in the config
  loader. Write the config field in the task, not the direct call.
- **Infrastructure boundary.** Do not add a datastore to an existing compose
  file when the repo treats that as off-limits; put the test fixture in its own
  file and say it is separate.

Each of these is a one-line check while planning and a multi-hour correction
once an implementer follows the wrong path.

## Authoring mechanics

- **Long plan files: never round-trip.** `read_file` truncates near 100K
  characters. Reading the plan back with `read_file` and rewriting it with
  `write_file` silently destroys the tail. Use `patch` for edits, or read the
  whole file inside code (`open(path).read()`) and assert `len(content)` after
  writing.
- **Self-check structure after any rewrite**: fence count must be even, the
  heading outline must list every phase/task in order with no gap, and no
  `123|` line-number prefixes leaked from a read.

```bash
wc -c .hermes/plans/<file>.md; grep -c '^### ' .hermes/plans/<file>.md
grep -c '```' .hermes/plans/<file>.md      # must be even
```

- **Branch base**: state the branch the repo is currently on and the command to
  branch from the default branch, so the implementer does not stack the work on
  someone else's in-flight branch.
