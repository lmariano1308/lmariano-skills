# Safety gates

## May proceed without a write approval

- Read repository files, history, diffs, configuration, tests, schemas, and local logs in scope.
- Run safe local diagnostics that do not mutate durable state.
- Analyze user-provided production evidence without changing production.
- Draft a proposal in chat without persisting it.

## Require explicit approval

- Change code, configuration, tests, documentation, or generated artifacts.
- Write to a remote system or send an external message.
- Restart a service, deploy, execute a migration, change infrastructure, or alter production state.
- Delete, overwrite, reset, rotate credentials, or perform another destructive or difficult-to-recover action.
- Persist a PRD, issue, ticket, ADR, context document, or review result when persistence was not already requested.

Production is read-only even when local writes are approved; production mutation requires separate explicit authorization.

Before a gated action, state the target, intended effect, important risk, rollback or recovery path, and exact authorization requested. Approval for one action does not imply approval for later transitions.

Never install dependencies during an engineering task. Treat installation as a separate user-approved activity.

Redact secrets, tokens, passwords, PII, session identifiers, private keys, and sensitive payload bodies from commands and reports. Prefer presence, type, count, hash, or schema evidence over raw values.
