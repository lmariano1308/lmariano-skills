---
name: dev-workflow
description: "Coordinate non-trivial repository engineering by classifying investigation, hotfix, bugfix, feature, refactor, migration, spike, or review work; announce the selected skill chain and risk mode; apply authorization gates; and require completion evidence. Use as the entry point when a task spans discovery, implementation, review, or verification. Do not use for trivial explanations or prose-only edits, and do not use it to bypass a specialized skill or approve its own high-risk work."
license: MIT
compatibility: "Portable Agent Skills package; works best in a repository with local instructions and read-only inspection capabilities. Pi may invoke it explicitly as /skill:dev-workflow."
---

# Lead developer workflow

Coordinate the workflow; do not replace the specialized skills that perform each phase.

## Start

1. Read repository and directory instructions before substantial work.
2. Identify the requested outcome, constraints, current evidence, and authorization already granted.
3. Classify the current intent using [intent-routing.md](references/intent-routing.md). Resolve conflicting verbs by observed state and uncertainty, not by the last verb in the prompt.
4. Select the smallest relevant chain using [skill-selection.md](references/skill-selection.md).
5. Select `quick`, `standard`, or `high-risk` mode from scope, reversibility, production exposure, security, data, and cross-service impact.
6. Announce exactly:

```text
Intent: <intent> · Skills: <skill chain> · Mode: <quick|standard|high-risk>
```

Do this before substantial work. Explicit Pi activation with `/skill:dev-workflow` is a documented fallback when natural activation misses; keep all following procedure harness-neutral.

## Coordinate

- Load only the selected skills and the references needed for the current phase.
- Use `repo-context` when context is weak, contradictory, cross-service, or unfamiliar. Avoid a repository-wide inventory by default.
- Apply [safety-gates.md](references/safety-gates.md) before actions. Local read-only investigation may proceed. Treat production as read-only.
- Treat stack-specific skills as optional capabilities. Follow [skill-selection.md](references/skill-selection.md) and [capability-routing.md](references/capability-routing.md); state the fallback when a preferred capability is absent. Never install dependencies during a task.
- Use the portable boundary in [cli-connectors-contract.md](references/cli-connectors-contract.md) when a capability depends on local commands or connectors.
- Label material conclusions `confirmed`, `probable`, `hypothesis`, `contradiction`, or `unknown`. Redact secrets, tokens, passwords, PII, and sensitive payloads.
- Keep lint, build, tests, and behavior verification as separate evidence categories.

## Transitions and completion

An intent transition is a recommendation. State the evidence for it, name the proposed next intent and skill chain, and stop at the approval gate. Investigation never silently becomes bugfix; review never silently becomes implementation.

Before claiming completion, load `completion-gate` and apply the relevant contract in [definitions-by-intent.md](references/definitions-by-intent.md). Ask: “What fresh evidence proves this exact claim?” Reinspect author, reviewer, or delegated reports in proportion to risk.

For meaningful risk, separate implementation from final approval. Use an independent context when supported; otherwise perform distinct passes with fresh inputs and explicitly reset prior conclusions. Subagents are optional, never required.

End with the current verdict, evidence gaps, and one recommended next intent. Do not cross its gate without approval.

## Conditional references

- Read [tracer-bullet-decomposition.md](references/tracer-bullet-decomposition.md) only when a feature, migration, or large refactor needs incremental slicing.
- Read [cli-connectors-contract.md](references/cli-connectors-contract.md) only when commands, adapters, or external capability boundaries matter.
