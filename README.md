# Engineering Agent Skills Foundation

A portable, skills-first foundation for evidence-driven engineering work. It routes a task by intent, loads only the capabilities needed, protects write and production boundaries, and requires fresh evidence before completion claims.

**Resumo PT-BR:** seis skills portáteis para coordenar engenharia, entender repositórios, investigar falhas, sintetizar PRDs, revisar mudanças e validar conclusão. Produção é sempre read-only; mudanças exigem aprovação explícita.

## Architecture

The foundation has one entry point and five directly invocable capabilities:

| Skill | Role |
|---|---|
| `dev-workflow` | Classify intent, announce the skill chain and mode, enforce gates, and coordinate transitions. |
| `repo-context` | Build a task-scoped, read-only map with traceable evidence. |
| `investigation` | Establish a feedback loop, test ranked hypotheses, and identify root cause without changing code. |
| `prd` | Run one-question discovery or synthesize a decision-ready PRD without publication side effects. |
| `review-gate` | Review a fixed change set across independent Spec, Standards, Verification, and risk-triggered Security axes. |
| `completion-gate` | Test a completion claim against fresh, claim-specific evidence. |

The canonical catalog is [`ecosystem.json`](ecosystem.json). Skill bodies contain the always-needed procedure; direct `references/` links contain intent tables, report formats, and templates loaded only when relevant.

## Composition

For non-trivial engineering work, start with `dev-workflow`. It emits:

```text
Intent: <intent> · Skills: <skill chain> · Mode: <quick|standard|high-risk>
```

The supported intents are `investigation`, `hotfix`, `bugfix`, `feature`, `refactor`, `migration`, `spike`, and `review`. A request such as “implement and fix the failing test” begins as investigation because the observed failure must be understood before a correction is approved. Intent transitions are recommendations, never silent state changes.

Optional stack skills are capabilities rather than hard dependencies. If a preferred capability is absent, continue with repository rules and available native project commands, state the fallback, and do not install anything during the task.

## Pi activation test

Test selective installation in a disposable or controlled project before broader use.

1. Make only these six skill directories discoverable by Pi, for example through individual safe symlinks under a trusted project’s `.agents/skills/` directory.
2. Start with explicit activation: `/skill:dev-workflow <task>`.
3. Confirm the visible intent, skill chain, and mode announcement; request read-only investigation first.
4. Repeat with the same natural-language prompt without `/skill:` and compare activation, evidence quality, and fallback reporting.
5. Add and remove one optional stack capability to verify both selection and explicit fallback.

Do not install entire upstream repositories for the first test. Their overlapping descriptions and environment-specific procedures can obscure routing results. Upstreams in `sources.lock.json` are attribution and comparison sources, not runtime dependencies.

## Selective installation

Prefer a per-project skills directory or a harness setting that points at selected skill directories. If symlinks are appropriate, create one link per reviewed skill and verify the resolved target before use. Never replace an existing directory, recursively link a whole upstream collection, or use an installer that deletes destinations.

Example layout (paths are illustrative; inspect before creating):

```text
.agents/skills/
  dev-workflow -> /reviewed/path/lmariano-skills/skills/dev-workflow
  investigation -> /reviewed/path/lmariano-skills/skills/investigation
  completion-gate -> /reviewed/path/lmariano-skills/skills/completion-gate
```

## Safety model

- Local reading and investigation may proceed without a write approval.
- Production remains read-only.
- Code changes, remote writes, restarts, deployments, migration execution, and destructive actions require explicit approval.
- No skill installs dependencies as part of a task.
- Reports redact secrets, tokens, passwords, PII, and sensitive payloads.
- Evidence labels distinguish `confirmed`, `probable`, `hypothesis`, `contradiction`, and `unknown`.
- Format, lint, static analysis, build, focused tests, relevant suite, full suite, behavior, and operational verification are independent signals.
- No completion claim rests only on an author or reviewer report.

## Attribution

The workflows adapt principles from Matt Pocock Skills, Superpowers, and Pi’s Agent Skills documentation. Exact repositories, licenses, and pinned commits are recorded in [`sources.lock.json`](sources.lock.json). The content here is an original, concise adaptation; upstream skills are not copied wholesale.

## Validation

All validation and eval tooling uses only the Python standard library. The layers prove different things:

- **Structural validation** checks the six-skill manifest, portable frontmatter, links, size limits, JSON syntax, and routing/composition fixture coverage. It does not execute behavioral evals.
- **Deterministic behavioral evals** parse synthetic, non-sensitive normalized events produced by a trusted harness or adapter. The compact lifecycle is `meta -> work/evidence* -> claim -> output -> verdict`; `meta` and `verdict` are the endpoints, lifecycle events are unique, and claim-supporting evidence must precede the claim. Global failure, authorization, mutation consistency, review independence, invalidation, and final-target timeline gates are derived by the evaluator rather than enabled by fixture invariants. An approved material transition adds the strict barrier `transition -> checkpoint -> skill_reload` before work may continue. Unknown, malformed, duplicate, or out-of-order events fail closed.
- **Live Pi evals** are opt-in and inference-bearing. They run Pi twice—natural prompt and explicit `/skill:dev-workflow`—from isolated runtime directories with discovery disabled, exactly the six catalogued skill directories, no tools, no session, a minimal authentication/config environment allowlist, and a timeout. The extractor accepts Pi's documented JSON lifecycle mirrors (`message_end`, then matching `turn_end` and `agent_end`) while rejecting conflicting copies and spoof sources. Reports contain only bounded, redacted verdict fields and summaries rather than raw model output. The safe readiness default requires both runs to agree on `claim_permitted=false` and on either `fail` or `insufficient_evidence`.

```sh
python3 scripts/validate.py
make behavioral-evals
make test
```

`make test` runs structural validation and deterministic behavioral evals. It is deterministic and free by default.

Run the live comparison explicitly only when inference cost and local Pi credentials are approved:

```sh
make live-pi-evals
```

The live runner does not expose write tools, save a session, or operate in a target repository; its report is emitted to standard output. It forwards only documented provider credential variables plus a small networking/locale allowlist, and replaces `HOME` and Pi runtime directories with temporary paths. Provider credentials therefore need to be available through supported environment variables rather than a persisted Pi auth file. Its structured verdict is still a model self-report rather than an independent semantic judge. In particular, model self-report cannot establish that a command was discovered from repository instructions or is truly canonical; only the trusted adapter's normalized deterministic events may assert that fact. Live success supplements but does not replace repository-native checks, trusted harness evidence, or human review. Do not redirect real session payloads, secrets, or sensitive prompts into committed files.
