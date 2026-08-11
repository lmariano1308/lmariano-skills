# Definitions by intent

Use these as claim-specific minimums; add repository or risk-specific evidence. Define readiness against the next real effect—commit, push, PR, merge, deploy, or handoff—not an artificially narrow subclaim. Where the repository defines a canonical pipeline, hook, or CI-equivalent command, that pipeline is required at the final target identity.

| Intent or artifact | Evidence required before a completion verdict |
|---|---|
| Research / repository understanding | Scope is explicit; relevant sources were inspected; map and flow cite paths, lines, or symbols; contradictions and unknowns are visible; next probes are named. |
| Investigation | Expected and observed behavior are recorded; available feedback loop was exercised; ranked hypotheses were tested; root cause is confirmed or the next discriminating experiment is specified. |
| Hotfix | Root cause or justified containment is recorded; approval exists; change is minimal and reversible; review and canonical pipeline target the final diff; rollback and operational risk are explicit; original symptom and operational behavior are freshly verified. |
| Bugfix | Root cause is corrected; a regression seam is red-capable when viable; review, focused tests, canonical pipeline, and original-symptom behavior target the final diff. |
| Feature | Scope, non-goals, acceptance criteria, contracts, and failure modes are agreed; review, canonical format, lint, static analysis, build, focused tests, relevant suite, full suite, and business behavior independently target the final diff as applicable. |
| Refactor | External behavior and comparison point are fixed; before/after evidence shows preservation; no incidental feature is included; review and canonical pipeline target the final diff. |
| Migration | Inventory, compatibility, staged rollout or cutover, rollback, data checks, security, and observability are covered; review and canonical pipeline target the final diff; no production execution occurs without approval. |
| Spike | Question, timebox, experiment, limitations, and decision are recorded; throwaway artifacts are identified; production fitness is not implied. |
| Review | Comparison point and sources are fixed; required axes are completed; findings have severity and evidence; disputes remain visible; no automatic edits occurred. |
| PRD | Material decisions are resolved or open; requirements and acceptance criteria are traceable; constraints, seams, edge cases, risks, and out-of-scope items are explicit; saving or publishing was separately approved. |
| Documentation | Intended audience and changed claims are clear; links/examples are checked; docs match executable behavior or state contradictions. |
| Infrastructure | Configuration is validated; plan or dry-run evidence exists where available; rollback, security, observability, and production approval are explicit. |

For every row, ask which fresh evidence proves the claim at the scope of its next real effect. Focused tests prove only their seam. Transport-level end-to-end evidence proves transport, not a business outcome. A reviewer summary is an input, not proof by itself.
