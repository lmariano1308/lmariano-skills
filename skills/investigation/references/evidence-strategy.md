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

## Evidence strength

- `confirmed`: direct observation matches the predicted causal mechanism.
- `probable`: consistent evidence exists, but a decisive probe is unavailable.
- `hypothesis`: prediction has not yet been tested.
- `contradiction`: sources or observations cannot both be true under current assumptions.
- `unknown`: required evidence is absent.
