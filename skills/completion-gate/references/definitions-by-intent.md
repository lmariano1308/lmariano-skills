# Definitions by intent

Use these as claim-specific minimums; add repository or risk-specific evidence.

| Intent or artifact | Evidence required before a completion verdict |
|---|---|
| Research / repository understanding | Scope is explicit; relevant sources were inspected; map and flow cite paths, lines, or symbols; contradictions and unknowns are visible; next probes are named. |
| Investigation | Expected and observed behavior are recorded; available feedback loop was exercised; ranked hypotheses were tested; root cause is confirmed or the next discriminating experiment is specified. |
| Hotfix | Root cause or justified containment is recorded; approval exists; change is minimal and reversible; rollback and operational risk are explicit; original symptom and operational behavior are freshly verified. |
| Bugfix | Root cause is corrected; a regression seam is red-capable when viable; focused and relevant suites pass; the original symptom is rechecked. |
| Feature | Scope, non-goals, acceptance criteria, contracts, and failure modes are agreed; lint, build, tests, and actual behavior are independently evidenced as applicable. |
| Refactor | External behavior and comparison point are fixed; before/after evidence shows preservation; no incidental feature is included; relevant checks pass. |
| Migration | Inventory, compatibility, staged rollout or cutover, rollback, data checks, security, and observability are covered; no production execution occurs without approval. |
| Spike | Question, timebox, experiment, limitations, and decision are recorded; throwaway artifacts are identified; production fitness is not implied. |
| Review | Comparison point and sources are fixed; required axes are completed; findings have severity and evidence; disputes remain visible; no automatic edits occurred. |
| PRD | Material decisions are resolved or open; requirements and acceptance criteria are traceable; constraints, seams, edge cases, risks, and out-of-scope items are explicit; saving or publishing was separately approved. |
| Documentation | Intended audience and changed claims are clear; links/examples are checked; docs match executable behavior or state contradictions. |
| Infrastructure | Configuration is validated; plan or dry-run evidence exists where available; rollback, security, observability, and production approval are explicit. |

For every row, ask which fresh evidence proves the exact claim. A reviewer summary is an input, not proof by itself.
