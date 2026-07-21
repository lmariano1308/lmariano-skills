# Production read-only investigation

Production observation does not authorize mutation.

When the symptom cannot be reproduced locally:

1. State why local or hardware reproduction is unavailable and what was attempted.
2. Ask for the smallest already-captured artifact that can discriminate hypotheses: redacted logs, trace, metric window, core dump, request shape, or screen recording with timestamps.
3. Correlate evidence across boundaries without retrieving unnecessary payload content.
4. If new production instrumentation appears necessary, recommend a transition out of investigation and request separate authorization for the exact mutation; do not add, enable, restart, or deploy it under this intent.
5. Treat time, sampling, retention, redaction, and observer effects as limitations.
6. Report confidence honestly. If cause is not confirmed, return the next discriminating observation rather than a correction.

Do not run production writes, restarts, deployments, migrations, destructive commands, or secret-revealing diagnostics under investigation intent.
