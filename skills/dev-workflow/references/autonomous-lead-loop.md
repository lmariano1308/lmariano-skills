# Autonomous lead loop

Use this reference when the harness can delegate or execute several bounded tasks and the user wants the workflow to continue with low supervision. Autonomy means continuing inside an approved boundary, not inventing scope or bypassing gates.

## Operating contract

The lead owns intent, scope, sequencing, delegation, evidence, and the final verdict. Implementers own bounded changes. Reviewers inspect a fixed target and do not edit it. The lead never treats an agent report as proof without proportional reinspection.

## Loop

1. **Route** — classify intent, product track, risk mode, selected skills, and the authorization boundary. Announce the compact route line before substantial work.
2. **Map** — read applicable repository instructions and task-scoped context. Record the quality contract, dirty paths, baseline failures, and the smallest relevant surface.
3. **Packet** — produce a brief or contract packet containing goal, exclusions, dependencies, interfaces or user flow, acceptance criteria, verification commands, and unresolved questions.
4. **Gate** — obtain approval before code, material architecture or scope change, external communication, paid action, production write, migration, restart, deploy, or destructive operation.
5. **Slice** — decompose into independently verifiable waves. Parallelize only tasks with explicit boundaries and no shared mutable target. Establish a shared contract before parallel backend/frontend work.
6. **Execute** — delegate or implement one wave at a time. Keep each task's inputs, owner, allowed paths, and expected evidence explicit. Stop on a real blocker rather than fabricating progress.
7. **Check** — run repository-native format, lint, static analysis, build, focused tests, relevant suite, full suite, behavior, visual, and operational checks as applicable. Keep categories separate.
8. **Review** — capture an immutable target identity and run independent Spec, Standards, Verification, and risk-triggered Security passes. A reviewer does not fix the target.
9. **Fix** — if findings block completion, authorize a separate correction pass. Any mutation invalidates prior review and check evidence; capture the new identity and rerun the affected gates.
10. **Close** — apply `completion-gate`, state the exact permitted claim, list gaps, preserve evidence, and recommend the next intent. Do not silently transition into the next mission.

## Autonomy guardrails

The lead may read, classify, plan, delegate bounded investigation, and combine skills without micro-approval. It must stop for:

- code or configuration writes outside the approved scope;
- schema, migration, Docker, environment, dependency, secret, or infrastructure changes;
- production access beyond approved read-only inspection;
- external messages, applications, purchases, commits, pushes, PRs, deploys, restarts, or destructive commands;
- unresolved ambiguity that changes architecture, behavior, ownership, cost, or security.

## Wave report

Every completed wave should return:

```text
Wave: <id and purpose>
Owner: <agent or lead>
Paths: <exact paths or read-only scope>
Changes: <summary>
Checks: <commands, scope, exit results>
Review target: <identity or not applicable>
Open risks: <none or named risks>
Next gate: <approval, review, correction, or completion>
```

## Material transition checkpoint

When the mission changes from investigation to implementation, from planning to implementation, or from review to correction, emit:

```text
Phase: <current phase>
Target: <exact scope or identity>
Skills loaded: <current chain>
Writes since gate: <none or paths/identity>
Canonical checks: <commands and current status>
Stale evidence: <none or invalidated evidence>
Authorization: <current boundary>
```

A fresh session is preferred when the context becomes heterogeneous enough that the lead can no longer state the current target, authorization, and evidence without reconstruction.
