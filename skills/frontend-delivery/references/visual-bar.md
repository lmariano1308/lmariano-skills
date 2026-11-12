# Visual bar and tokens

The reject list is not taste. Each item below was named as a defect on a real review.

## Rejected on sight

- Radial or conic decorative gradients, neon glow shadows, gradient cards, glass panels.
- Two or more accent colors competing in the same viewport.
- Weight 800 or 900 used as a shortcut for hierarchy.
- Saturated duotone palettes and stock photography in a page that claims craft.
- Emojis, decorative stars, invented statistics, decorative quotation marks.
- A generic hover lift on every card, an eight-item navigation, a split-hero skeleton.
- A simulated desktop operating system (fake window buttons, fake system bar) used as a technical portfolio metaphor.
- Redaction markers rendered as bare text where they read like a broken variable. Use a bordered badge with muted background instead.

## Token set

```css
:root {
  --bg: #f4f1ea;
  --surface: #ffffff;
  --surface-2: #ece7dc;
  --ink: #121110;
  --ink-2: #5c5750;
  --border: rgba(18, 17, 16, 0.14);
  --border-strong: rgba(18, 17, 16, 0.32);
  --accent: #c8102e;
  --ok: #1f6f43;
  --warn: #8a5a00;
  --danger: #a3170f;
  --radius: 8px;
  --radius-lg: 12px;
  --control-h: 44px;
}
```

Rules that follow from the set:

- Structure is luminance plus a 1 px border. Shadows are not structure.
- `--control-h` is a floor for interactive targets, not a suggestion.
- Every text pair must reach 4.5:1; large display text may reach 3:1. Measure, do not estimate.

## Theme switch

```html
<script>
  (function () {
    var saved = localStorage.getItem("theme");
    var dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.dataset.theme = saved || (dark ? "dark" : "light");
  })();
</script>
```

- The inline script runs before the framework mounts. Without it the first paint flashes.
- The toggle writes the same key the script reads.
- Density and font scale are separate root attributes that only redefine spacing and base font size.

## Component discipline

- One `SectionShell` owns vertical rhythm; sections do not invent their own padding.
- Buttons have three states and a disabled state, all reachable by keyboard.
- Monospace is for metrics, labels, and code. Body copy is never monospace.
- A page that sells an existing product borrows that product's scale. A poster-scale headline on a product page disconnects the page from the system it sells.
