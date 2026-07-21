---
name: investigation
description: "Investigate bugs, failing tests, regressions, slow behavior, and unexplained technical symptoms through a red-capable feedback loop, minimized reproduction, boundary evidence, and ranked falsifiable hypotheses. Use for investigation intent and before hotfix or bugfix work when root cause is not confirmed. Do not alter code for any purpose, enter implementation, or claim a fix during investigation; production remains read-only and any transition to hotfix or bugfix requires approval."
license: MIT
compatibility: "Works with repository-native tests, scripts, logs, debuggers, profilers, or user-provided evidence; inaccessible hardware and production-only symptoms use the documented read-only exception."
---

# Systematic investigation

Identify root cause or the next experiment that best separates the remaining explanations. Do not correct code under this intent.

## Establish the signal

1. Record the observed symptom, expected behavior, scope, frequency, environment, and earliest known occurrence.
2. Build the tightest viable red-capable feedback loop from existing tests and interfaces: a focused test invocation, request replay, ephemeral command, measurement, or deterministic comparison. Do not create or edit repository files under investigation intent.
3. Run the loop and confirm it detects the exact symptom. Tighten speed, determinism, and specificity.
4. Minimize the reproduction one variable at a time while preserving the signal.

If production is the only observable environment or required hardware is inaccessible, remain read-only and follow [production-read-only.md](references/production-read-only.md). Explicitly record why a local red-capable loop is unavailable; use logs, traces, metrics, captured artifacts, or an approved local simulation. Do not fabricate reproduction confidence.

## Investigate

1. Gather evidence at boundaries that discriminate between components or stages. Inspect inputs, outputs, state transitions, configuration propagation, timing, and errors without exposing sensitive values. Use [evidence-strategy.md](references/evidence-strategy.md) when the flow crosses boundaries or performance is involved.
2. Trace bad data or state backward to its origin. Compare with a working path or prior known-good state when available.
3. Generate three to five ranked, falsifiable hypotheses. For each, write a prediction and the smallest discriminating probe in [hypothesis-ledger.md](references/hypothesis-ledger.md) format.
4. Test one variable at a time. Update the ledger with observed evidence and status; do not stack speculative corrections.
5. Confirm cause only when the predicted evidence and causal mechanism both hold. A correlated change is not sufficient.

## Rule of three

After three attempted probes or correction ideas without meaningful information gain, stop. Recheck the symptom, feedback loop, hidden assumptions, boundaries, and design. Escalate a possible architectural mismatch instead of attempting a fourth variation blindly.

## Handoff

Identify a regression seam that exercises the real failure pattern when one exists. Remove ephemeral runtime instrumentation and disposable outputs. If cleanup or a regression test requires repository edits, include them in the proposed `bugfix` or `hotfix` transition rather than performing them now.

Return one of:

- confirmed root cause, causal chain, evidence, regression seam, and recommended `bugfix` or `hotfix` transition; or
- remaining ranked hypotheses and the next discriminating experiment, including access or approval needed.

Recommend the next intent and stop for approval. Never alter code during `investigation`.
