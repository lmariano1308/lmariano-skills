# Harness adapters

The portable procedures live in `skills/`. These files document thin local adapters; they do not duplicate the workflow. Each adapter selects a role, model, permission boundary, and skill-loading convention for one harness.

## Adapters

- [OpenCode personal lead](opencode/personal-lead.md)
- [Kilo corporate lead](kilo/corporate-lead.md)
- [Codex personal lead](codex/personal-lead.md)
- [Pi personal lead](pi/personal-lead.md)

The adapters intentionally keep personal and corporate routing separate. They do not contain credentials, production payloads, or destructive commands.
