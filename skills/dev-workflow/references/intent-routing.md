# Intent routing

Classify the current phase, not the aspirational end state.

| Intent | Positive signals | Boundary and precedence |
|---|---|---|
| `investigation` | diagnose, explain a failure, failing test, unexpected or slow behavior | Takes precedence when a symptom is unexplained. Read-only; correction requires an approved transition. |
| `hotfix` | active severe incident, urgent contained correction, rollback pressure | Use only after enough investigation to justify a minimal reversible change; high-risk when production is involved. |
| `bugfix` | confirmed defect and requested correction | Requires a known root cause or an approved transition from investigation. |
| `feature` | new user-visible or system capability | Use `prd` when material product or technical decisions remain. |
| `refactor` | restructure while preserving observable behavior | Reject hidden feature work; fix the comparison point and preserved contracts. |
| `migration` | staged transition of data, contract, platform, or dependency | Require coexistence or cutover, rollback, and data/contract validation. |
| `spike` | timeboxed experiment to answer a decision question | Output learning and decision evidence, not production code by default. |
| `review` | assess a fixed diff, patch, branch, or exact file set | Read-only. Findings do not authorize fixes. |

## Conflict rules

1. An unexplained failure makes `investigation` the starting intent even when the prompt also says “implement” or “fix.”
2. “Review and fix” starts as `review`; propose a separate `bugfix` or `refactor` transition after findings.
3. An active incident may classify as `hotfix`, but root-cause evidence and explicit change approval still apply.
4. A refactor that changes observable behavior must be reclassified, usually as `feature` or `bugfix`.
5. A spike does not silently become a feature.

Do not activate the lead for general explanations, trivial prose edits, or tasks with no repository engineering workflow.
