---
name: repo-context
description: "Build a task-scoped, read-only model of an unfamiliar, weakly documented, contradictory, or cross-service repository area by tracing symbols, contracts, flows, tests, configuration, schemas, and documentation with path-and-line evidence. Use before decisions when repository context is insufficient. Do not use for automatic whole-repository inventories, do not treat executable code as unquestionable business truth, and do not persist context documents, ADRs, or instruction files without approval."
license: MIT
compatibility: "Requires read access to the relevant repository and a way to search files and symbols; no indexer or connector is required."
---

# Repository understanding

Build only the model needed for the current task. Remain read-only.

## Procedure

1. Read the nearest applicable repository instructions first, including `AGENTS.md`, `CLAUDE.md`, contribution rules, and directory-specific variants.
2. State the task boundary: entry symptom or request, likely modules, excluded areas, and questions the map must answer.
3. Locate the smallest relevant set of manifests, executable entry points, contracts, tests, configs, schemas, and documentation.
4. Trace important symbols from definition to usages and callers/callees. Follow data and control flow across boundaries; cite `path:line` and symbol names.
5. Compare sources. Executable code proves current mechanics, not automatically intended business behavior. Tests prove encoded expectations; docs and schemas may express a different contract.
6. Label every material conclusion:
   - `confirmed`: directly supported by inspected evidence;
   - `probable`: multiple signals agree, but a decisive check is missing;
   - `hypothesis`: falsifiable explanation awaiting a probe;
   - `contradiction`: authoritative-looking sources disagree;
   - `unknown`: evidence is missing or inaccessible.
7. Redact secrets, tokens, passwords, PII, and sensitive payloads. Record structure or presence instead of values.
8. Stop when the task questions can be answered or the next probe is clear. Do not expand into an automatic inventory.

## Output

Use this shape:

```markdown
## Scope
## Map
## Flow
## Evidence
| Status | Claim | Evidence | Relevance |
## Contradictions
## Unknowns
## Next probes
```

Make every evidence entry traceable to a path and line, or to a named symbol when line stability is poor. Distinguish facts retrieved from repository evidence from user decisions still required.

Do not create `CONTEXT.md`, an ADR, repository instructions, or another persistent summary automatically. If persistence would materially help, explain the benefit and ask first.
