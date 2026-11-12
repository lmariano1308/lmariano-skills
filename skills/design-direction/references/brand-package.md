# Brand package

## Order

Name, language, symbol, measured palette, applications, code. Each step depends on the previous one; skipping a step produces a mark that has to be redone.

## Symbol

- At most three shapes. A mark that needs a paragraph to explain is an illustration.
- Build it from a small script with geometry constants at the top (center, radius, stroke, hub). Variants are parameter changes; hand-edited SVG is not reproducible.
- Check the mark at 16 px, 32 px, and 512 px before showing it. A mark that disappears at favicon size is a texture, not a symbol.
- Deliver: symbol, monochrome version, inverted version, lockup with the wordmark, and the clear-space rule.

## Wordmark

- Convert text to paths. A lockup that depends on an installed font breaks in the first PDF that leaves the machine.
- Keep the path source and the generator script next to the exported SVG so the lockup can be adjusted later.
- Optical spacing beats mathematical spacing at small sizes; check the pair at 100 percent zoom.

## Palette

- Compute contrast, never estimate it. Every text pair needs 4.5:1; display text at large sizes may reach 3:1.
- A light brand color usually fails as text on paper. Record the failure and the rule that follows from it (accent for fills, ink for text).
- Define the tokens as the product will consume them: background, surface, ink, ink-secondary, border, accent, success, warning, danger.

## Applications

- Favicon and app icon from the symbol, not from the wordmark.
- Link preview at 1200×630 with the mark, the name, and one line of positioning.
- One real surface: the hero of the product or the header of the document.

## Board

- Compose the board in HTML with the SVGs embedded, then capture at 2×. Rasterizing the SVG alone loses typography and composition.
- The board shows: symbol grid, negative space, size ladder, palette with contrast values, type specimen, and applications.

## Delivery

- Files under a dated folder, untracked until approval.
- A short README with the decisions, the files, how to regenerate, and what was explicitly not done (registration, domain).
- Apply to product code only with explicit approval; until then the artifacts stay outside the shipped tree.
