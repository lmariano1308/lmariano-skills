---
name: prd
description: "Turn product and repository context into a decision-ready PRD using one-question discovery when material decisions are missing or direct synthesis when context is sufficient. Use for features, migrations, and consequential changes that need traceable requirements, acceptance criteria, testing decisions, edge cases, and optional tracer bullets. Do not repeat an interview when decisions are already available, prescribe premature file paths or code snippets, or save, publish, ticket, or implement the artifact without approval."
license: MIT
compatibility: "Portable workflow using repository read access and conversation; issue trackers, document systems, and connectors are optional and never required."
---

# To PRD

Choose a mode before drafting.

## Discovery mode

Use Discovery when a material product, behavior, risk, metric, or constraint decision is unresolved.

1. Inventory what is known, recoverable from the repository, decided, and open.
2. Retrieve facts locally instead of asking the user to repeat them.
3. Ask one decision question at a time and wait for the answer.
4. Include a recommended answer with its reasoning and main tradeoff.
5. Follow dependent branches until the remaining open items are non-blocking or explicitly deferred.
6. Do not implement or persist an artifact during discovery.

## Synthesis mode

Use Synthesis when the conversation and inspected evidence already resolve material decisions. Do not repeat the interview. Reconcile contradictions, mark unresolved items, and draft the PRD with [prd-template.md](references/prd-template.md).

Requirements must be behavioral and durable. Avoid premature paths, symbol names, implementation snippets, and ticket-system fields. Assign stable functional requirement IDs and make acceptance criteria trace back to them.

Include personas only when different users materially change requirements. Include security, privacy, observability, or operational sections when risk makes them relevant; do not add empty ceremony.

## Review and decomposition

Check that problem evidence supports the solution, metrics map to goals, requirements cover journeys and failure modes, constraints are distinguished from decisions, and acceptance criteria are observable.

Offer tracer-bullet decomposition only when the work benefits from independently verifiable end-to-end slices. Keep it optional and draft-only.

Present the PRD for review. Do not save it, create issues or tickets, publish it, or invoke implementation without explicit approval for that separate action.
