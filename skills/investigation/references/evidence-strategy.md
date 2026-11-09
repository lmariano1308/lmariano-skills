# Evidence strategy

Choose evidence that separates hypotheses rather than producing volume.

## Boundaries

For each relevant boundary, capture only:

- input shape, provenance, and invariant;
- output shape and invariant;
- state or configuration version;
- timing and error category;
- correlation identifier that is safe to disclose.

Prefer counts, schemas, hashes, boolean presence, and redacted samples over raw payloads. Never print secrets, tokens, passwords, PII, or sensitive bodies.

## Data and control flow

Trace the first point where actual state diverges from expected state. Work backward through definitions and callers until the source condition is identified. Compare a working path with the failing path under the same controlled input.

## Performance

Establish a repeatable baseline before interpreting cause. Prefer profilers, query plans, counters, and controlled timings over broad logging. Change one variable, repeat enough samples to distinguish signal from noise, and report measurement limits.

## Reported UI action does nothing

Use when a control does not open, save, or respond. Trace the path in order and record what is observed at each step:

1. Find the click handler by element id in the client script. Confirm it runs (a log or breakpoint on the click); a handler that never fires is a client-side binding problem.
2. Read the request the handler sends: endpoint, filter and body fields, and the success callback.
3. Confirm the route registration and its capability gates. A denied gate returns an error that the screen may never render.
4. Read the controller's error branches for the record's inputs: missing identifiers, foreign keys, or related rows. Errors that are logged but returned as empty content are the usual silent failure.
5. Read the client's success callback for unguarded access to response fields. A missing field throws inside the callback, so the screen never switches.

Compare with a record that does open. Diff the response shape and input values. The difference points at the data condition, which is usually more specific than the code path that looks suspicious.

Tool note: `search_files` takes one directory per call. A space-joined path list returns `Path not found`, so run one search per root.

## Evidence strength

- `confirmed`: direct observation matches the predicted causal mechanism.
- `probable`: consistent evidence exists, but a decisive probe is unavailable.
- `hypothesis`: prediction has not yet been tested.
- `contradiction`: sources or observations cannot both be true under current assumptions.
- `unknown`: required evidence is absent.
