---
name: completion-gate
description: "Gate completion claims for research, repository understanding, investigation, hotfix, bugfix, feature, refactor, migration, spike, review, PRD, documentation, and infrastructure by matching each claim to fresh direct evidence. Use before saying work is complete, fixed, passing, verified, or ready, and invoke directly when such a claim lacks proof. Do not accept confidence, stale output, partial checks, or author, reviewer, and subagent reports as sufficient without proportional reinspection."
license: MIT
compatibility: "Uses repository-native validation and direct artifact inspection; exact commands depend on the project and no particular harness is required."
---

# Definition of done

Ask one central question: **What fresh evidence proves this exact claim?**

## Gate

1. State the claim, intent, observable outcome, and next real effect such as commit, push, PR, merge, or deploy. Do not shrink the claim below the effect the handoff enables.
2. Load the matching intent contract from [definitions-by-intent.md](references/definitions-by-intent.md).
3. Capture the final diff/worktree identity and dirty paths. Verify that review and every result target that identity; any later mutation invalidates all of them.
4. Discover the repository-native commands and run the applicable canonical hook or CI-equivalent pipeline. Do not substitute a convenient focused command for a repository contract.
5. Record each applicable category independently: format, lint, static analysis, build/compilation, focused tests, relevant suite, full suite, behavior, and operational checks. Never merge lint with static analysis or relevant with full suite. Use `not applicable` only with a concrete reason.
6. Read complete outputs, exit results, failures, timeouts, skips, and scope. Reinspect author, reviewer, delegated, or external reports in proportion to risk; summaries locate evidence but do not replace it.
7. Map each result to the claim it permits. Transport end-to-end evidence does not prove business end-to-end behavior; focused tests do not prove feature readiness.
8. Compare all material requirements to the final identity without optimistic extrapolation.

Every applicable failure, timeout, unexpected skip, or unavailable required command blocks the claim, whether or not the check is canonical. Missing required categories, stale review, stale evidence, or a changed diff are also `fail` or `insufficient evidence`, never `pass` or `conditional`. A mutation invalidates the review and every prior check or behavior category tied to the old target; rerun each required or invalidated category against the final target.

Production remains read-only. If proving a claim would require a production write, restart, deployment, migration, destructive action, remote write, or code change, stop and request explicit approval. Never install dependencies to manufacture a validation path.

Redact secrets, tokens, passwords, PII, and sensitive payloads. Prefer command, scope, timestamp or freshness, exit status, counts, and sanitized observations.

## Output

```markdown
## Claim
## Evidence
| Category | Command or observation | Scope | Freshness / target identity | Exit result | Claim permitted |
## Gaps
## Verdict
```

Use one verdict:

- `pass`: fresh evidence proves the claim at the required scope;
- `conditional`: verified scope passes and only named, genuinely non-blocking limits remain;
- `fail`: evidence contradicts the claim or a blocking requirement fails;
- `insufficient evidence`: required proof is absent, stale, inaccessible, or unsafe without approval.

Do not say “done,” “fixed,” “passing,” or an equivalent until the verdict supports that exact wording.
