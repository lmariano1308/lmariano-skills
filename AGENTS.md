# Repository instructions

This repository publishes a small, portable Agent Skills foundation.

## Scope

- Keep exactly the six skills declared in `ecosystem.json`.
- Keep skill procedures harness-neutral and written in technical English.
- Use only Agent Skills core frontmatter: `name`, `description`, `license`, optional `compatibility`, and portable `metadata` when justified.
- Preserve progressive disclosure: essential procedure in `SKILL.md`, task-specific detail in directly linked `references/` or `assets/` files.
- Do not add installation, publishing, commit, push, deploy, restart, migration execution, remote write, or dependency-install side effects to a skill.
- Treat production as read-only. Require explicit approval for code changes and every operational or destructive action.
- Keep secrets, tokens, passwords, PII, and sensitive payloads out of examples and reports.

## Changes

- Read this file and relevant local instructions before editing.
- Preserve unrelated work and keep changes task-scoped.
- Update `ecosystem.json` and fixtures when a skill contract changes.
- Do not add tool names from a particular agent harness to the main procedures. Compatibility notes may document invocation syntax without making it required.
- Do not copy substantial upstream passages. Adapt principles and retain attribution in `sources.lock.json` and the root `README.md`.

## Required validation

Run before claiming completion:

```sh
python3 scripts/validate.py
make test
```

Report each validation category separately. A passing linter or parser does not prove behavior.
