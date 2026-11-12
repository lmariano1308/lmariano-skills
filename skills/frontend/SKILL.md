---
name: frontend
description: "Deliver front-end work one section at a time against a live prototype and a measured visual bar. Use when the request is 'faz a seção', 'implementa o front', 'ajusta esse componente', 'monta a página', 'refaz o hero', or when an existing interface must be brought to an approved direction. Do not use for backend-only work, for a whole-page rewrite in one pass, or to commit without explicit approval."
license: MIT
compatibility: "Any repository with a way to serve a page and an engine to render it. No framework, bundler, or design tool is required."
---

# Front-end delivery

Ship visible, approved interface. Judge by looking at a running page, not by describing a diff.

## Before editing

1. Confirm working directory, git root, branch, and `git status`. Preserve unrelated local changes.
2. Read the repository instructions and the design tokens in use. A token file that already exists wins over any preference in this skill.
3. Name the unit of work: one section, one component, or one hero. It is never the whole page.
4. State the approval you already have and what would need a new one.

## Prototype before code

When the direction is not settled, build the page outside the repository first. Full recipe: [prototype-first.md](references/prototype-first.md).

1. Produce two or three directions as standalone HTML pages with real fonts, the real palette, and real motion. A wireframe or a static mockup is not a direction.
2. Serve them from one local HTTP server and check that every page answers `200` before sharing a link.
3. Capture each direction in a browser engine and look at the captures before sending the link.
4. Ask exactly one closing question with options. If none fits, ask which part of which fits.

Do not start repository edits while the direction is still open.

## Tooling is not part of the contract

No product is named in this skill. Serving, rendering, capturing, and measuring are capabilities; use whatever the machine or the repository already provides and say which one you used. A skill that requires a specific tool is a skill nobody else can run.

## Build in slices

1. One section or component per session. Never regenerate a monolithic page.
2. When the complaint is specific, patch only the flagged element. Replacing the surrounding section is the fastest route to "put it back the way it was".
3. Content stays visible by default. No `opacity: 0` waiting for a reveal, no content that only exists after JavaScript.
4. Mobile first: verify the 390 px width before the 1440 px one.
5. Copy that does not exist yet is a marked placeholder, never invented marketing text.

## Visual bar

The full reject list and the token recipe live in [visual-bar.md](references/visual-bar.md). The short version:

- One accent color. No decorative gradient, no glow, no glassmorphism, no gradient cards, no ornamental slashes.
- Structure from luminance steps and 1 px hairlines, not from shadows.
- Body weights around 550 and headings around 650. Radius 8 or 12 px, pill reserved for the primary call to action.
- Density and font scale are data attributes on the root element that redefine spacing and base font tokens only. They must never rewrite component CSS.
- Dark and light are both requirements when the product has themes: semantic tokens, a root `data-theme`, an inline anti-flash script before the framework mounts, and one persisted preference key.

## Verify in a browser

1. Build first, then open a browser. A page that does not build has nothing to review.
2. Check every served route returns `200`, then read the console for errors after each navigation and after each interaction.
3. Take screenshots at 390 and 1440, in both themes when the product has them, and look at them.
4. Treat a delegated or subagent QA report as a declaration, not a fact. Re-serve the page in this session, re-check the status codes, and re-run the DOM checks before saying it is live.
5. A local server started inside a child process dies with that process. Relaunch it in the session that will open the link.

## Deliver

Return the slice, a short list of what changed, the build result, the browser evidence, and the remaining decisions. Hand the measured pass to `visual-qa` when the slice is visually significant, and to `review-gate` before any commit.

Do not commit, push, or deploy without explicit authorization for that exact action.
