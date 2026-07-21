# Tracer-bullet decomposition

Use tracer bullets when a feature, migration, or wide refactor cannot be verified safely as one change.

A tracer bullet is the smallest end-to-end slice that crosses the real boundaries and produces decision or behavior evidence. It is not a horizontal layer such as “build all models” or “finish all endpoints.”

For each slice, record:

- user or operator value;
- entry point and observable result;
- contracts crossed;
- prerequisite decisions and dependencies;
- acceptance evidence;
- rollback or removal path;
- what remains deliberately out of scope.

Order slices to retire the highest uncertainty early. For migrations, prefer expand → coexist → verify → cut over → contract, with separately approved production gates. For refactors, preserve an executable behavior baseline through every slice.

Present the decomposition for approval before implementation. Do not create tickets, publish issues, or persist the plan unless separately authorized.
