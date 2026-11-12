# Rounding service — demonstration fixture

A single file of business logic whose installment split loses a cent. The fixture exists so the workflow demonstration in [../../docs/workflow-demo.md](../../docs/workflow-demo.md) can run the whole lifecycle against real code, offline, with no credentials.

## Contents

| Path | Role |
|---|---|
| `app/pricing.py` | The slice under change: `split_installments` uses float division and drops the remainder |
| `tests/test_pricing.py` | Seven assertions; two fail against the current implementation |
| `preview/index.html` | Static invoice card used by the measured visual pass |
| `qa/check_preview.py` | Offline visual QA: token contrast, document invariants, control height |

## Run it by hand

```sh
cd examples/rounding-service
python3 -m unittest discover -s tests -v
python3 qa/check_preview.py preview/index.html
```

The first command fails on the two sum assertions. The second passes: the preview is compliant, the defect is in the domain code.

## What the fixture deliberately omits

No database, no network, no framework, no environment variable. Everything here runs with the Python standard library, so a reader can reproduce the demonstration on any machine with `python3`.
