---
name: visual-qa
description: "Measure a web interface instead of trusting a glance: overflow, WCAG contrast, touch targets, console errors, both themes, desktop and mobile. Use when the request is 'faz o QA visual', 'testa no browser', 'olha como ficou no celular', 'valida o contraste', or before shipping a landing or an application slice. Do not use as a substitute for functional tests, or to report a defect without file, measurement, and reproduction."
license: MIT
compatibility: "Headless browser when available; the offline checks work from HTML and CSS alone."
---

# Visual QA

"The screenshot looks fine" is not a result. A visual pass produces numbers, a reproduction, and a file.

## Script first

1. Write the check once, as a script in the repository, so the next slice costs one command.
2. The script takes a URL or a file, a viewport list, and an output directory.
3. It writes a JSON result plus one screenshot per screen. JSON is the evidence; screenshots are the illustration.
4. Exit non-zero when a blocking check fails, so the gate can consume it.

The full check list, thresholds, and the offline fallback: [measured-checks.md](references/measured-checks.md).

## What to measure

| Check | Threshold | Why |
|---|---|---|
| Horizontal overflow | `scrollWidth <= innerWidth` at 390, 768, 1440 | A single wide element breaks the whole page on mobile |
| Text contrast | 4.5:1 body, 3:1 large display | Calculated from the computed pair, not from the token names |
| Touch target | at least 44×44 px below the breakpoint | Buttons that cannot be hit are broken, not small |
| Console errors | zero uncaught errors | Silent failures hide for weeks |
| Network | no 4xx or 5xx on page assets | A missing font or image is a visible defect |
| Both themes | every check runs in light and dark | The second theme is the one that ships broken |
| Focus | visible ring on the first three tabbable elements | Keyboard users are users |

## Execution

1. Serve the page, verify `200` on every route in scope.
2. Run the measured pass at each viewport and each theme.
3. Look at every screenshot after the numbers pass. Numbers catch mirrors, not ugliness.
4. Treat a delegated QA report as a declaration: rerun the script in this session before repeating its verdict.
5. Any mutation after the run invalidates it. Rerun the whole pass against the new target.

## Report

Each finding carries: severity, screen, viewport, theme, the measured value, the expected value, the file, and a one-line reproduction.

```markdown
| Severity | Screen | Viewport | Check | Measured | Expected | File |
|---|---|---|---|---|---|---|
| high | checkout | 390 | overflow | 412 > 390 | <= 390 | web/src/checkout.css:44 |
```

Finish with the counts: screens checked, viewports, themes, blocking findings, non-blocking findings. Say which screens were not reachable and why.

## Offline mode

When a browser is unavailable, run the deterministic part from the HTML and CSS: parse the custom properties, compute contrast for the declared pairs, verify the viewport meta, the language attribute, the title, and the absence of content hidden by default. State clearly that rendering was not exercised. This is a weaker claim and must be reported as such.

## Handoff

Hand blocking findings back to the slice that owns them. Do not fix visual defects under a QA intent without an approved change; QA reports, the implementation approves and implements.
