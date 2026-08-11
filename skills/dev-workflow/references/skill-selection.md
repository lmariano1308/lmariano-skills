# Skill selection

Select the smallest chain that covers the current intent.

| Intent | Foundation chain | Conditional additions |
|---|---|---|
| investigation | `investigation` | `repo-context` for weak, contradictory, unfamiliar, or cross-service context |
| hotfix | `investigation` → stack capability → `review-gate` → `completion-gate` | `repo-context` when containment crosses boundaries |
| bugfix | stack capability → `review-gate` → `completion-gate` | `investigation` unless root cause is already confirmed with evidence |
| feature | `prd` when decisions remain → stack capability → `review-gate` → `completion-gate` | tracer-bullet decomposition for multi-slice delivery |
| refactor | `repo-context` → stack capability → `review-gate` → `completion-gate` | tracer bullets for wide changes |
| migration | `repo-context` → optional `prd` → stack capability → `review-gate` → `completion-gate` | tracer bullets for staged transition |
| spike | relevant capability → `completion-gate` | `repo-context` when the decision depends on existing contracts |
| review | `review-gate` → `completion-gate` | risk-based security pass only when triggered |

## Capability fallback

1. Match needs to capabilities, not a hard-coded skill name.
2. Load a preferred installed capability only after reading its description and repository rules.
3. If absent, say which capability is unavailable and continue with repository instructions and available native commands.
4. Absence never blocks read-only investigation by itself.
5. Do not install a skill, package, tool, or dependency during the task.

Do not load competing skills for the same role unless comparison is the stated goal.

The review and completion gates apply when these flows make meaningful mutations. Read-only investigation and review remain at their stated boundaries; planning-only work does not acquire an implementation gate merely because its future intent may mutate code.
