---
name: review-triage
description: "Run a tool-assisted review on a fixed target and triage every finding into confirmed, rejected, or unproven before anything enters the backlog. Use when the request is 'revisa esse commit', 'roda o review', 'checa o diff', 'esses achados são reais', or before a gate that depends on independent review. Do not use to review a moving worktree, to apply fixes automatically, or to treat a review report as proof of correctness."
license: MIT
compatibility: "Any diff-based review tool plus a local repository; the triage rules do not depend on a specific vendor."
---

# Review triage

A review tool produces hypotheses at scale. The value is in what survives validation, not in the number of comments.

## Fix the target

1. Resolve the exact commit, merge-base and head, or diff hash. Record it before running anything.
2. Confirm the change set is non-empty and matches the scope the user named.
3. Treat any later mutation as a new target: the review is stale, not partially valid.

## Run the review

- Review a commit or a diff, not a directory, when the question is about a change.
- Run long reviews in the background with a notification. A large diff takes minutes and a foreground call dies at the shell timeout.
- Prefer JSON output: it carries path, line, category, severity, and a suggested patch, and it can be counted.
- Keep the raw output as an artifact next to the summary. The summary is for humans; the JSON is for the next pass.

## Triage

Every finding gets exactly one state, recorded in a ledger. Format: [triage-ledger.md](references/triage-ledger.md).

- **confirmed** — reproduced in the current code, with the file and line, and a stated failure mode.
- **rejected** — the code does not do what the finding claims, or the behavior is intentional and documented. Record why.
- **unproven** — plausible but cannot be reproduced without a missing environment, dataset, or approval. It stays out of the backlog and is reported as a limit.

Rules:

1. Validate before fixing. A comment is a hypothesis; open the code and confirm the usage before renaming or removing a symbol.
2. Do not accept a finding because it sounds severe. A "role checked only in the client" finding is confirmed only after the server handler is read.
3. Do not reject a finding because the tool is noisy. Rejection needs a reason grounded in the code.
4. Group duplicates. Forty comments about one missing guard are one finding.

## What the tool reliably finds

- Money handled as float, rounding applied twice, splitting that loses a cent.
- Client-side authorization with no server-side revalidation.
- Secrets or credentials interpolated into a shell command, `eval`, or a log line.
- Missing scope filter on a query that touches shared data.
- Unbounded loops and allocations in a hot path.

Use that list to prioritize; do not use it to skip the ledger.

## Close the loop

1. Fix confirmed findings on a separate branch, one theme per commit.
2. Rerun the same tool on the fixed target. Stop when no confirmed finding remains, not when the comment count drops.
3. Rerun the repository gates. A review tool does not run the build.
4. Hand the fixed target to `review-gate` for the independent pass and to `completion-gate` for the claim.

## Baseline

When the repository already has an audit or a previous review document, that document is the baseline. Re-reporting a corrected finding is noise: pass the list as context and require a status per item (fixed, regressed, not verifiable).

The surface that pays is the code written after the last audit. List the commits since that date and review that range first.

## Evidence rule

A finding enters the backlog only with executable proof: a test that fails before and passes after, or a real command output. Without proof it is a marked hypothesis, even when the finding came from a strong model.
