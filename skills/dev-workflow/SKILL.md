---
name: dev-workflow
description: "Coordinate non-trivial repository engineering by classifying investigation, hotfix, bugfix, feature, refactor, migration, spike, or review work; announce the selected skill chain and risk mode; apply authorization gates; and require completion evidence. Use as the entry point when a task spans discovery, implementation, review, or verification. Do not use for trivial explanations or prose-only edits, and do not use it to bypass a specialized skill or approve its own high-risk work."
license: MIT
compatibility: "Portable Agent Skills package; works best in a repository with local instructions, immutable change identities, and read-only inspection capabilities."
---

# Lead developer workflow

Coordinate the workflow; do not replace the specialized skills that perform each phase.

## Start

1. Read repository and directory instructions before substantial work.
2. Identify the requested outcome, constraints, current evidence, and authorization already granted.
3. Classify the current intent using [intent-routing.md](references/intent-routing.md). Resolve conflicting verbs by observed state and uncertainty, not by the last verb in the prompt.
4. Select the smallest relevant chain using [skill-selection.md](references/skill-selection.md).
5. Select `quick`, `standard`, or `high-risk` mode from scope, reversibility, production exposure, security, data, and cross-service impact.
6. If the work is product-facing, read [product-workflows.md](references/product-workflows.md) and select the applicable track. If the work spans bounded waves or delegated roles, read [autonomous-lead-loop.md](references/autonomous-lead-loop.md).
7. Before implementation, discover the repository-native quality contract from applicable instructions, manifests and scripts, Makefiles, hooks, and CI. Record canonical format, lint, static analysis, build, focused test, relevant suite, full suite, behavior, and operational commands as independent categories. Establish a baseline when viable; distinguish pre-existing failures and dirty paths.
8. Announce exactly:

```text
Intent: <intent> · Skills: <skill chain> · Mode: <quick|standard|high-risk>
```

Do this before substantial work.

## Coordinate

- Load only the selected skills and the references needed for the current phase.
- Keep product-track decisions separate from engineering intent: a landing page, vertical SaaS, institutional site, or internal system can independently be a feature, refactor, investigation, review, or spike.
- For multi-wave work, use the autonomous lead loop as the coordination contract; autonomy continues only inside the approved target and authorization boundary.
- Use `repo-context` when context is weak, contradictory, cross-service, or unfamiliar. Avoid a repository-wide inventory by default.
- Apply [safety-gates.md](references/safety-gates.md) before actions. Local read-only investigation may proceed. Treat production as read-only.
- Treat stack-specific skills as optional capabilities. Follow [skill-selection.md](references/skill-selection.md) and [capability-routing.md](references/capability-routing.md); state the fallback when a preferred capability is absent. Never install dependencies during a task.
- Use the portable boundary in [cli-connectors-contract.md](references/cli-connectors-contract.md) when a capability depends on local commands or connectors.
- Label material conclusions `confirmed`, `probable`, `hypothesis`, `contradiction`, or `unknown`. Redact secrets, tokens, passwords, PII, and sensitive payloads.
- Keep format, lint, static analysis, build, focused tests, relevant suite, full suite, behavior, and operational verification as separate evidence categories.
- Bind reviews and check results to the exact diff or worktree identity they inspected.

## Mutation-aware lifecycle

Meaningful implementation for hotfix, bugfix, feature, migration, or refactor must pass through `review-gate` and then `completion-gate`. A review never doubles as its correction pass.

Any mutation after a review or check makes all earlier review and check evidence stale, even when the edit appears unrelated. Record the new target identity, run a separate fix pass, then rerun review and every required check against that final identity. Do not reuse a baseline result as final evidence.

## Transitions and completion

An intent transition is a recommendation. State the evidence for it, name the proposed next intent and skill chain, and stop at the approval gate. Investigation never silently becomes bugfix; review never silently becomes implementation.

When mission or intent changes materially, emit this compact checkpoint and reload the new skill chain before continuing:

```text
Phase: <current phase>
Target: <exact scope or identity>
Skills loaded: <current chain>
Writes since gate: <none or paths/identity>
Canonical checks: <commands and current status>
Stale evidence: <none or invalidated evidence>
Authorization: <read/write/operation boundary>
```

Recommend a fresh session when scope materially changes or accumulated context becomes heterogeneous.

Before claiming completion, load `completion-gate` and apply the relevant contract in [definitions-by-intent.md](references/definitions-by-intent.md). Frame readiness for the next real effect such as commit, push, PR, merge, or deploy. Ask: “What fresh evidence proves this exact claim?” Reinspect author, reviewer, or delegated reports in proportion to risk.

For meaningful risk, separate implementation from final approval. Use an independent context when supported; otherwise perform distinct passes with fresh inputs and explicitly reset prior conclusions. Subagents are optional, never required.

End with the current verdict, evidence gaps, and one recommended next intent. Do not cross its gate without approval.

## Conditional references

- Read [tracer-bullet-decomposition.md](references/tracer-bullet-decomposition.md) only when a feature, migration, or large refactor needs incremental slicing.
- Read [cli-connectors-contract.md](references/cli-connectors-contract.md) only when commands, adapters, or external capability boundaries matter.
- Read [product-workflows.md](references/product-workflows.md) for landing pages, institutional sites, vertical software, or internal systems.
- Read [autonomous-lead-loop.md](references/autonomous-lead-loop.md) when delegation, multiple waves, or low-supervision execution is part of the approved workflow.
