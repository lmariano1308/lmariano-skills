# Measured checks

## Contrast

Compute from the two colors actually in effect, not from the token names.

```python
def channel(value: float) -> float:
    value /= 255.0
    return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    raw = hex_color.lstrip("#")
    r, g, b = (int(raw[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def ratio(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)
```

- Body text: 4.5:1. Large display text (24 px, or 18.66 px bold): 3:1.
- A ratio computed from declared tokens is a static check. A ratio read from the computed style of a rendered node is the real check; prefer it when a browser is available.

## Overflow

- `document.documentElement.scrollWidth <= window.innerWidth`. One pixel over is a defect.
- Find the offender, do not guess: walk elements and report the first node whose `right` exceeds the viewport width.
- Re-check after each theme change and after opening a modal.

## Touch target

- Every interactive element is at least 44×44 CSS pixels below the mobile breakpoint.
- Adjacent targets need at least 8 px between them.
- A decorative icon inside a button is part of the target; the target is the button.

## Console and network

- Clear the console, navigate, interact, then read it. An error before the first interaction still counts.
- Collect failed responses with their URL and status. A 404 on a font file is a visible defect in the next screenshot.

## Themes

- Run every check once per theme. The theme is set on the root element, then the pass repeats.
- Persisted preference must survive reload. Check it once; do not test the whole matrix twice.

## Offline fallback

When no browser is available:

1. Parse the page and its stylesheet.
2. Extract `--` custom properties and the `background` / `color` pairs declared together.
3. Compute contrast for each pair and report the worst one.
4. Verify the viewport meta, the language attribute, a non-empty title, and that no block is hidden by default with `opacity: 0` or `visibility: hidden`.
5. Label the result `static analysis`, never `rendered`.

## Result shape

```json
{
  "target": "preview/index.html",
  "mode": "static",
  "viewports": [390, 1440],
  "checks": [
    {"id": "contrast.ink-on-bg", "measured": 15.98, "expected": ">= 4.5", "passed": true},
    {"id": "layout.viewport-meta", "measured": "present", "expected": "present", "passed": true}
  ],
  "blocking_failures": 0
}
```

The gate reads `blocking_failures`; the human reads the rows.
