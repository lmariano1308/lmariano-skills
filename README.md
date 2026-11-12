# skills

Portable engineering skills for AI coding agents. Six of them are the portfolio set; six more support the workflow behind them. Every one of them runs in any harness and does not require any particular library.

**Resumo PT-BR:** skills portáteis para agentes de código — investigar, front-end, motion, direção de design, back-end e QA visual. Nenhuma skill exige ferramenta, framework ou harness específico; cada uma descreve a capacidade de que precisa e usa o que o projeto já tem.

## The six

| Skill | Area | What it decides |
|---|---|---|
| [`investigation`](skills/investigation/SKILL.md) | diagnóstico | Establishes a red-capable feedback loop, ranks falsifiable hypotheses, and confirms root cause without touching code |
| [`frontend`](skills/frontend/SKILL.md) | front-end | Prototypes the direction before editing, then delivers one section at a time against a measured bar |
| [`motion`](skills/motion/SKILL.md) | motion | Picks the smallest motion budget that carries hierarchy, then proves it respects reduced motion |
| [`design-direction`](skills/design-direction/SKILL.md) | design | Turns references into a live direction board, one approved direction, and a brand package with measured contrast |
| [`backend`](skills/backend/SKILL.md) | back-end | Ships one verifiable slice: contract, reversible migration, scoped store, routes, tests, evidence |
| [`visual-qa`](skills/visual-qa/SKILL.md) | visual-qa | Measures overflow, contrast, touch targets, console, and both themes instead of trusting a screenshot |

Each one states the capability it needs and leaves the tool to the repository: serving, rendering, capturing, measuring, migrating, testing. Nothing in a skill body names a product, a framework, or a harness, so the same procedure works with the stack you already have — and with whichever browser automation, animation runtime, or plugin your harness exposes.

## The supporting six

| Skill | Area | Role |
|---|---|---|
| [`dev-workflow`](skills/dev-workflow/SKILL.md) | workflow | Classifies intent, announces the chain and mode, enforces the gates |
| [`repo-context`](skills/repo-context/SKILL.md) | workflow | Task-scoped, read-only map with `path:line` evidence |
| [`prd`](skills/prd/SKILL.md) | workflow | Decision-ready requirements before code |
| [`review-gate`](skills/review-gate/SKILL.md) | review | Independent review: Spec, Standards, Verification, and risk-triggered Security |
| [`review-triage`](skills/review-triage/SKILL.md) | review | Fixed-target review with every finding triaged into confirmed, rejected, or unproven |
| [`completion-gate`](skills/completion-gate/SKILL.md) | workflow | Tests a completion claim against fresh, claim-specific evidence |

The catalog is [`ecosystem.json`](ecosystem.json): area, capabilities, and a dated evidence record per skill (project, commit or artifact, observed result). A skill without evidence is not published here.

## Try it

```sh
git clone <this repository> && cd skills
python3 scripts/run_demo.py
```

One request, seven steps, no network, no credential, about two seconds. It runs the whole lifecycle against a real diff in a temporary directory: classification, context, red test, fix, review bound to a hash, measured visual pass, completion gate, and one mutation that invalidates the evidence. Transcript and what each step proves: [docs/workflow-demo.md](docs/workflow-demo.md).

## Use it in your harness

A skill is a directory: `SKILL.md` with portable frontmatter plus optional `references/`. Anything that can read a skill directory can use it.

1. Copy `skills/<id>/` into the skills directory your harness reads, or point the harness at this repository's `skills/` folder.
2. Load `SKILL.md` when its description matches the request; load a `references/` file only when the body links to it and the task needs that depth.
3. Invocation syntax is the harness's business. `/skill:<id>`, a tool call, or a plain prompt that matches the description all work, because the description is written with the words a person uses to ask.

To install selectively: one directory or one symlink per reviewed skill, resolved target verified. See [Selective installation](#selective-installation).

## Composition

For non-trivial engineering work, start with `dev-workflow`. It emits:

```text
Intent: <intent> · Skills: <skill chain> · Mode: <quick|standard|high-risk>
```

The supported intents are `investigation`, `hotfix`, `bugfix`, `feature`, `refactor`, `migration`, `spike`, and `review`. A request such as "implement and fix the failing test" begins as investigation because the observed failure must be understood before a correction is approved. Intent transitions are recommendations, never silent state changes.

A typical bugfix with visual impact:

```text
Intent: bugfix · Skills: investigation → backend → review-gate → visual-qa → completion-gate · Mode: quick
```

Capability skills are optional in the sense that no repository is required to have them. When one is absent, continue with repository rules and native project commands, state the fallback, and never install anything during the task.

## Safety model

- Local reading and investigation may proceed without a write approval.
- Production remains read-only.
- Code changes, remote writes, restarts, deployments, migration execution, and destructive actions require explicit approval.
- No skill installs dependencies as part of a task.
- Reports redact secrets, tokens, passwords, PII, and sensitive payloads.
- Evidence labels distinguish `confirmed`, `probable`, `hypothesis`, `contradiction`, and `unknown`.
- Format, lint, static analysis, build, focused tests, relevant suite, full suite, behavior, and operational verification are independent signals.
- No completion claim rests only on an author or reviewer report.
- A mutation after a review or a check invalidates that evidence; the gate says `fail`, not `conditional`.

## Selective installation

Prefer a per-project skills directory, or a harness setting that points at selected skill directories. If symlinks are appropriate, create one link per reviewed skill and verify the resolved target before use. Never replace an existing directory, recursively link a whole upstream collection, or use an installer that deletes destinations.

```text
.agents/skills/
  investigation   -> /reviewed/path/skills/skills/investigation
  frontend        -> /reviewed/path/skills/skills/frontend
  visual-qa       -> /reviewed/path/skills/skills/visual-qa
```

Test discovery with one explicit activation and one natural-language prompt, then add and remove one capability to confirm the fallback path. Upstreams in `sources.lock.json` are attribution and comparison sources, not runtime dependencies; do not install a whole upstream collection for a first test, because overlapping descriptions obscure routing.

## Attribution

The workflows adapt principles from Matt Pocock Skills, Superpowers, and Pi's Agent Skills documentation. Exact repositories, licenses, and pinned commits are recorded in [`sources.lock.json`](sources.lock.json). The content here is an original, concise adaptation; upstream skills are not copied wholesale.

## Validation

All tooling in this repository uses only the Python standard library.

- **Structural validation** — catalog, portable frontmatter, area coverage, evidence records, links, size limits, JSON syntax, demo files, and fixture coverage. It does not execute behavioral evals.
- **Deterministic behavioral evals** — parse synthetic, non-sensitive normalized events: `meta -> work/evidence* -> claim -> output -> verdict`. Unknown, malformed, duplicate, or out-of-order events fail closed.
- **The demo** — executes the lifecycle against a real diff in a temporary directory.

```sh
python3 scripts/validate.py
make demo
make test
```

`make test` runs the demo, structural validation, and the deterministic evals. It is offline and free.

`make live-evals` is the opt-in, inference-bearing variant: it runs a real harness twice and compares the verdicts. The repository ships one harness-specific adapter for it (`evals/pi_eval.py`) as a reference implementation; the skills themselves assume no harness. Do not redirect real session payloads, secrets, or sensitive prompts into committed files.

## License

MIT. See [LICENSE](LICENSE).
