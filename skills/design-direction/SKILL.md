---
name: design-direction
description: "Turn visual references into a live direction board, get one direction approved, and close the brand package behind it. Use when the request is 'redesenha com esses prints', 'quero ver direções', 'monta um board', 'fecha a marca', 'preciso de logo e identidade', or when the current page was rejected as generic. Do not use to re-theme a product that already owns tokens, or to deliver a static document instead of a running page."
license: MIT
compatibility: "A way to serve a page locally and an engine to look at it; vector tooling is optional and never assumed."
---

# Design direction

A direction is a decision, not a collection. Produce the smallest artifact that lets the decision be made by looking, then execute only the chosen one.

## Board first

1. Read what already exists: current site, tokens, brand files, previous rejections. A new direction that ignores the existing system creates two identities.
2. Build two or three directions as running pages, not as images. Recipe and layout: [direction-board.md](references/direction-board.md).
3. Keep them outside the product repository until one is chosen.
4. Serve them locally, verify `200`, screenshot, and look before sharing.
5. Close with one question and the options. "Which piece of which" is the correct follow-up when no direction is right.

## Grounding rules

- A page that sells an existing product borrows that product's display face, UI face, accent, radius, and button. The directions vary composition and theme, not identity.
- Assets are real captures of real work. Stock imagery and invented cases are the fastest way to look like everyone else.
- Before embedding a real site inside a page, check its frame policy. If it refuses framing, show a composed capture instead of an empty frame.
- Reject on sight: decorative gradient, glassmorphism, ornamental separators, floating generic icons, stock copy. The full list lives in `frontend` under `references/visual-bar.md`.
- Approval is per stage. Implement in the product repository only after the direction is chosen, one section at a time, with a running preview.

## Brand package

When the request is the mark itself, the order is fixed. Details and measurement recipe: [brand-package.md](references/brand-package.md).

1. Name decided. Without a name the symbol is a guess.
2. One language, taken from the product that exists, not from the mood board.
3. Symbol with at most three shapes.
4. Palette with measured contrast, not estimated.
5. Real applications: icon, link preview, hero.
6. Code last, after the board is approved.

## Measurement

- Draw the symbol from a parametric source (a small script with geometry constants). Regenerate to compare variants; never hand-edit the vector file.
- Convert the wordmark to outlines so the lockup does not depend on an installed font.
- Compute contrast for every pair before writing the board. A light brand color usually fails as text and that finding belongs in the document.
- Judge the whole composition by looking at it; keep the numbers arithmetic. When a visual critique contradicts a measurement, recompute before accepting it.
- Record what was not done (registration, domain purchase) instead of implying completeness.

## Output

Return: the board path, the chosen direction with the reason, the tokens extracted, the measured pairs, and the next slice. Keep generated brand artifacts untracked until the product owner approves applying them.
