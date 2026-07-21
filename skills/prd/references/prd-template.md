# PRD template

# <Decision-oriented title>

## Problem and evidence

Describe the observed need, current behavior, affected scope, and evidence strength. Separate confirmed facts, probable interpretations, contradictions, and unknowns.

## Goals and metrics

Define desired outcomes and how success will be measured. Include a baseline or measurement plan when relevant.

## Users and personas

Include only when user groups have materially different needs, permissions, or journeys.

## Solution

Describe the proposed behavior and important product or system decisions without premature code paths or snippets.

## User journeys and stories

Cover primary, alternate, recovery, and operator journeys as applicable.

## Functional requirements

- `FR-001`: State one testable behavior.
- `FR-002`: State the next testable behavior.

## Non-functional requirements

Cover measurable performance, reliability, availability, accessibility, compatibility, and operability needs that actually apply.

## Technical constraints and decisions

Separate imposed constraints from chosen decisions. Record tradeoffs and compatibility boundaries.

## Testing seams and decisions

Identify observable boundaries and the level at which each critical behavior or failure can be tested.

## Failure modes and edge cases

Describe invalid input, partial failure, concurrency, retry, timeout, empty state, rollback, and degradation cases that apply.

## Security, privacy, and observability

Include authorization, data minimization, redaction, auditability, metrics, logs, and traces according to risk.

## Out of scope

Name adjacent work deliberately excluded.

## Acceptance criteria

- `AC-001` → `FR-001`: Given ..., when ..., then ...; evidence: ...
- `AC-002` → `FR-002`: Given ..., when ..., then ...; evidence: ...

## Open questions

List owner, impact, and decision gate for each unresolved question.

## Optional tracer bullets

For each end-to-end slice, state value, boundaries crossed, acceptance evidence, dependencies, and rollback or removal path.
