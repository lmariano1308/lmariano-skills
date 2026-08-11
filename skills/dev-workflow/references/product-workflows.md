# Product workflow tracks

Use this reference when the request creates or changes a user-facing product, a vertical SaaS, an institutional site, or an internal business system. Product class is orthogonal to engineering intent: a landing page can be a feature, refactor, review, or spike.

## Shared product packet

Before implementation, produce the smallest packet that makes the next decision explicit:

- outcome and primary user;
- problem, job, or business process;
- in-scope and explicitly out-of-scope behavior;
- information architecture or domain map;
- acceptance criteria and observable success signals;
- quality constraints: usability, visual direction, accessibility, performance, reliability, security, and operational cost;
- implementation slices and verification commands;
- open questions classified as confirmed, probable, hypothesis, contradiction, or unknown.

Do not turn an attractive interface into a product specification by assumption. If the core problem or user is unclear, route to `prd` or `spike` before implementation.

## Track: landing page

Use for a focused conversion surface, campaign, launch, or lead-generation page.

1. Clarify audience, offer, proof, objection, CTA, and conversion event.
2. Define the content hierarchy and responsive visual contract before component work.
3. Implement the smallest complete path: content, CTA, form or handoff, loading/error/success states, analytics boundary if approved.
4. Verify desktop and mobile evidence, keyboard access, contrast, semantic structure, performance, metadata, and link/form behavior.
5. Review visual hierarchy and copy against the approved brief; do not add sections merely to fill space.

## Track: institutional site

Use for a company, professional, service, or local-business site whose primary job is trust, discovery, and contact.

1. Map audiences, services, proof, location/service area, contact paths, and legal or trust information.
2. Define navigation, page hierarchy, reusable content blocks, and content ownership.
3. Implement responsive templates and the contact/conversion path before secondary polish.
4. Verify accessibility, SEO fundamentals, metadata, structured content where applicable, performance, forms, and mobile navigation.
5. Check that claims, prices, testimonials, service areas, and contact details are sourced or explicitly marked as user-supplied.

## Track: vertical software / workshop or mechanic shop

Use for operational software whose value comes from reducing friction in a repeatable business workflow.

1. Observe or elicit the real workflow: customer, vehicle or asset, service request, diagnosis, quote, approval, work order, parts, execution, status, payment, delivery, and follow-up.
2. Separate the system's source-of-truth entities from views and convenience fields. Record lifecycle states, invariants, permissions, audit needs, and failure/recovery paths.
3. Select one tracer-bullet workflow that reaches a real business outcome. Prefer a complete service-order slice over a collection of disconnected CRUD screens.
4. Make the UX operationally fast: obvious next action, low typing where safe, search and status visibility, safe undo or correction paths, responsive layout, and useful empty/loading/error states.
5. Validate stability and economics as product requirements: deterministic state transitions, idempotent actions, backups/export, observability, low infrastructure complexity, and a cost model that does not depend on unsupported usage assumptions.
6. Test the workflow with representative shop scenarios before expanding inventory, finance, integrations, or automation.

The claim "cheaper, more stable, and prettier" is not evidence. Convert it into measurable constraints and user-observable acceptance criteria.

## Track: internal business system

Use for software that supports a company's internal process, regardless of whether it is sold externally.

1. Map actors, roles, approvals, handoffs, exceptions, audit requirements, and external systems.
2. Define permissions and data ownership before UI polish. Do not infer authorization from hidden buttons alone.
3. Specify contracts, import/export, retries, reconciliation, notifications, and operational ownership.
4. Deliver a vertical slice through the critical business path, including failure handling and audit evidence.
5. Verify role boundaries, data integrity, observability, backup/recovery assumptions, and the canonical business acceptance flow.

## Product gates

A product change may proceed only when the applicable gates are visible:

- **Problem gate:** user, outcome, and scope are explicit.
- **Experience/domain gate:** visual hierarchy or domain/workflow contract is explicit.
- **Tracer gate:** the first complete slice is executable or its spike question is answered.
- **Quality gate:** technical, visual, accessibility, security, and operational checks are named.
- **Completion gate:** fresh evidence proves the exact claim at the promised scope.

If a gate is intentionally deferred, record the reason and the narrower claim that remains permitted.
