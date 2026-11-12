# Engineering Agent Skills Foundation

A portable, skills-first foundation for evidence-driven engineering work. It routes a task by intent, loads only the capabilities needed, protects write and production boundaries, and requires fresh evidence before completion claims.

**Resumo PT-BR:** doze skills portáteis — seis de fluxo e seis de capacidade — para coordenar engenharia, entender repositórios, investigar falhas, sintetizar PRDs, entregar front-end, motion, design, back-end, revisar mudanças e validar conclusão com QA visual medido. Produção é sempre read-only; mudanças exigem aprovação explícita.

Every declared skill carries a dated evidence record in [`ecosystem.json`](ecosystem.json): the project where it ran, the commit or artifact, and the observed result. A skill without evidence is not published here.

## Try it

```sh
git clone <this repository> && cd lmariano-skills
python3 scripts/run_demo.py
```

One request, seven steps, no network, no credential, about two seconds. Full transcript and what each step proves: [docs/workflow-demo.md](docs/workflow-demo.md).

## Architecture

The foundation has one entry point, six flow skills, and six capability skills. `dev-workflow` classifies the request and selects the smallest chain.

| Skill | Area | Role |
|---|---|---|
| `dev-workflow` | workflow | Classify intent, announce the skill chain and mode, enforce gates, coordinate transitions |
| `repo-context` | workflow | Build a task-scoped, read-only map with traceable evidence |
| `investigation` | workflow | Establish a feedback loop, test ranked hypotheses, identify root cause without changing code |
| `prd` | workflow | One-question discovery or direct synthesis of a decision-ready PRD |
| `completion-gate` | workflow | Test a completion claim against fresh, claim-specific evidence |
| `frontend-delivery` | front-end | Prototype first, deliver one section at a time, verify in a real browser |
| `motion-design` | motion | Choose the motion budget, choreograph scroll, respect reduced motion, measure scroll behavior |
| `design-direction` | design | Direction board from references, one approved direction, brand package with measured palette |
| `backend-delivery` | back-end | One verifiable slice: contract, reversible migration, scoped store, routes, tests, evidence |
| `review-gate` | review | Independent review across Spec, Standards, Verification, and risk-triggered Security |
| `review-triage` | review | Tool-assisted review on a fixed target, every finding triaged into confirmed, rejected, or unproven |
| `visual-qa` | visual-qa | Measured checks: overflow, contrast, touch targets, console, both themes, desktop and mobile |

The canonical catalog is [`ecosystem.json`](ecosystem.json). Skill bodies contain the always-needed procedure; direct `references/` links contain tables, recipes, and templates loaded only when relevant.

## Composition

For non-trivial engineering work, start with `dev-workflow`. It emits:

```text
Intent: <intent> · Skills: <skill chain> · Mode: <quick|standard|high-risk>
```

The supported intents are `investigation`, `hotfix`, `bugfix`, `feature`, `refactor`, `migration`, `spike`, and `review`. A request such as "implement and fix the failing test" begins as investigation because the observed failure must be understood before a correction is approved. Intent transitions are recommendations, never silent state changes.

A typical bugfix with visual impact:

```text
Intent: bugfix · Skills: investigation → backend-delivery → review-gate → visual-qa → completion-gate · Mode: quick
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

Prefer a per-project skills directory or a harness setting that points at selected skill directories. If symlinks are appropriate, create one link per reviewed skill and verify the resolved target before use. Never replace an existing directory, recursively link a whole upstream collection, or use an installer that deletes destinations.

Example layout (paths are illustrative; inspect before creating):

```text
.agents/skills/
  dev-workflow -> /reviewed/path/lmariano-skills/skills/dev-workflow
  investigation -> /reviewed/path/lmariano-skills/skills/investigation
  completion-gate -> /reviewed/path/lmariano-skills/skills/completion-gate
```

## Pi activation test

Test selective installation in a disposable or controlled project before broader use.

1. Make only the skills under review discoverable by Pi, for example through individual safe symlinks under a trusted project's `.agents/skills/` directory.
2. Start with explicit activation: `/skill:dev-workflow <task>`.
3. Confirm the visible intent, skill chain, and mode announcement; request read-only investigation first.
4. Repeat with the same natural-language prompt without `/skill:` and compare activation, evidence quality, and fallback reporting.
5. Add and remove one optional stack capability to verify both selection and explicit fallback.

Do not install entire upstream repositories for the first test. Their overlapping descriptions and environment-specific procedures can obscure routing results. Upstreams in `sources.lock.json` are attribution and comparison sources, not runtime dependencies.

## Attribution

The workflows adapt principles from Matt Pocock Skills, Superpowers, and Pi's Agent Skills documentation. Exact repositories, licenses, and pinned commits are recorded in [`sources.lock.json`](sources.lock.json). The content here is an original, concise adaptation; upstream skills are not copied wholesale.

## Validation

All validation, evaluation, and demonstration tooling uses only the Python standard library. The layers prove different things:

- **Structural validation** checks the catalog, portable frontmatter, area coverage, evidence records, links, size limits, JSON syntax, demo files, and routing/composition fixture coverage. It does not execute behavioral evals.
- **Deterministic behavioral evals** parse synthetic, non-sensitive normalized events produced by a trusted harness or adapter. The compact lifecycle is `meta -> work/evidence* -> claim -> output -> verdict`; `meta` and `verdict` are the endpoints, lifecycle events are unique, and claim-supporting evidence must precede the claim. Global failure, authorization, mutation consistency, review independence, invalidation, and final-target timeline gates are derived by the evaluator rather than enabled by fixture invariants. An approved material transition adds the strict barrier `transition -> checkpoint -> skill_reload` before work may continue. Unknown, malformed, duplicate, or out-of-order events fail closed.
- **The workflow demo** executes the lifecycle against a real diff in a temporary directory: red test, fix, review bound to a diff hash, measured visual pass, completion gate, and one deliberate mutation that invalidates the evidence.
- **Live Pi evals** are opt-in and inference-bearing. They run Pi twice — natural prompt and explicit `/skill:dev-workflow` — from isolated runtime directories with discovery disabled, exactly the declared skill directories, no tools, no session, a minimal authentication/config environment allowlist, and a timeout. The extractor accepts Pi's documented JSON lifecycle mirrors (`message_end`, then matching `turn_end` and `agent_end`) while rejecting conflicting copies and spoof sources. Reports contain only bounded, redacted verdict fields and summaries rather than raw model output. The safe readiness default requires both runs to agree on `claim_permitted=false` and on either `fail` or `insufficient_evidence`.

```sh
python3 scripts/validate.py
make demo
make test
```

`make test` runs the demo, structural validation, and deterministic behavioral evals. It is deterministic and free by default.

Run the live comparison explicitly only when inference cost and local Pi credentials are approved:

```sh
make live-pi-evals
```

The live runner does not expose write tools, save a session, or operate in a target repository; its report is emitted to standard output. It forwards only documented provider credential variables plus a small networking/locale allowlist, and replaces `HOME` and Pi runtime directories with temporary paths. Provider credentials therefore need to be available through supported environment variables rather than a persisted Pi auth file. Its structured verdict is still a model self-report rather than an independent semantic judge. In particular, model self-report cannot establish that a command was discovered from repository instructions or is truly canonical; only the trusted adapter's normalized deterministic events may assert that fact. Live success supplements but does not replace repository-native checks, trusted harness evidence, or human review. Do not redirect real session payloads, secrets, or sensitive prompts into committed files.

## License

MIT. See [LICENSE](LICENSE).
