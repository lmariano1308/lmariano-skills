---
name: completion-gate
description: "Gate completion claims for research, repository understanding, investigation, hotfix, bugfix, feature, refactor, migration, spike, review, PRD, documentation, and infrastructure by matching each claim to fresh direct evidence. Use before saying work is complete, fixed, passing, verified, or ready, and invoke directly when such a claim lacks proof. Do not accept confidence, stale output, partial checks, or author, reviewer, and subagent reports as sufficient without proportional reinspection."
license: MIT
compatibility: "Uses repository-native validation and direct artifact inspection; exact commands depend on the project and no particular harness is required."
---

# Definition of done

Ask one central question: **What fresh evidence proves this exact claim?**

## Gate

1. State the claim narrowly, including intent, scope, and observable outcome.
2. Load the matching intent contract from [definitions-by-intent.md](references/definitions-by-intent.md).
3. Identify direct evidence that could disprove as well as prove the claim.
4. Run or inspect the freshest safe evidence available. Read complete results, exit status, failures, skipped coverage, and scope.
5. Separate evidence categories:
   - lint or static analysis;
   - build or compilation;
   - tests, including focused regression and relevant suite;
   - behavior verification against the original or acceptance scenario;
   - operational evidence when applicable.
6. Reinspect author, reviewer, delegated, or external reports in proportion to risk. Their summaries locate evidence; they do not replace it.
7. Compare evidence to every material requirement and state gaps without optimistic extrapolation.

Production remains read-only. If proving a claim would require a production write, restart, deployment, migration, destructive action, remote write, or code change, stop and request explicit approval. Never install dependencies to manufacture a validation path.

Redact secrets, tokens, passwords, PII, and sensitive payloads. Prefer command, scope, timestamp or freshness, exit status, counts, and sanitized observations.

## Output

```markdown
## Claim
## Evidence
| Category | Fresh evidence | Scope | Result |
## Gaps
## Verdict
```

Use one verdict:

- `pass`: fresh evidence proves the claim at the required scope;
- `conditional`: verified scope passes, but named non-blocking limits remain;
- `fail`: evidence contradicts the claim or a blocking requirement fails;
- `insufficient evidence`: required proof is absent, stale, inaccessible, or unsafe without approval.

Do not say “done,” “fixed,” “passing,” or an equivalent until the verdict supports that exact wording.
