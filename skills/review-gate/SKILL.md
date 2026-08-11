---
name: review-gate
description: "Review a fixed comparison point or exact file set through separate Spec compliance, Repository standards and engineering quality, Verification sufficiency, and risk-triggered Security passes. Use for patches, branches, work-in-progress changes, or completion reviews that need evidence-backed findings. Do not review an unfixed moving target, merge axes into vague approval, alter code automatically, or add a security pass when risk does not justify it."
license: MIT
compatibility: "Supports independent contexts when the harness provides them; otherwise use separate sequential passes with fresh source inputs and explicitly reset assumptions."
---

# Independent review

Review the evidence; do not modify the change.

## Fix the review target

1. Resolve exact base/head identities, a merge-base and head, an exact diff hash, a supplied patch hash, or an exact file set with content identities.
2. Record that immutable target and verify that the change set is available and non-empty. A branch name or moving worktree alone is not an identity.
3. Locate the originating requirement, PRD, acceptance criteria, or user-approved scope. If unavailable, mark the Spec axis limited rather than inventing intent.
4. Read repository and directory standards that apply to the changed files.

Any mutation after target capture makes this review stale. Stop, record the new identity, and require a complete re-review; do not append an informal check of only the last edit.

## Run separate passes

Meaningful changes should use a reviewer with independent context when supported. Subagents are optional. Otherwise perform sequential passes, reload the fixed inputs for each, explicitly set aside prior conclusions, and report same-context review as a limitation.

1. **Spec compliance** — identify missing, partial, incorrect, or unrequested behavior against cited requirements.
2. **Repository standards / engineering quality** — identify violations of documented rules and concrete correctness, maintainability, concurrency, compatibility, or contract risks. Repository rules override generic preferences.
3. **Verification sufficiency** — map each material claim and changed behavior to fresh lint, build, test, and behavior evidence. Treat these as distinct categories; report missing regression seams and unexercised controls.
4. **Security** — run only when the change touches trust boundaries, authentication or authorization, secrets, untrusted input, sensitive data, dependency or supply-chain risk, network exposure, destructive operations, or production privileges.

## Findings

Report findings first, ordered by severity within each axis. Use:

```text
Severity: critical | high | medium | low
Axis: Spec | Standards | Verification | Security
Evidence: path:line or path:symbol
Violated requirement/rule: <citation or explicit expectation>
Impact: <observable failure or risk>
Suggestion: <smallest direction, not an automatic edit>
Blocks completion: yes | no
```

Do not report stylistic preference as a hard violation. If no finding exists for an axis, say which sources and change set were checked.

The author may contest a finding with repository, runtime, test, or specification evidence. Re-evaluate and record the disposition; never silently discard or weaken a finding. Preserve unresolved disagreements and their completion impact.

End with the fixed point, coverage limitations, finding counts per axis, and blockers. Do not edit code or transition to implementation without explicit approval.

The reviewer makes no edits. Corrections occur in a separately authorized fix pass, which creates a new target identity and requires re-review before completion.
