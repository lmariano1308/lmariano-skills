---
name: motion
description: "Design and implement interface motion that carries hierarchy instead of decorating it. Use when the request is 'anima isso', 'põe motion', 'faz o reveal', 'scroll horizontal', 'quero impacto ao rolar', or when a landing needs choreography, reduced-motion handling, and measured scroll behavior. Do not use for a single hover transition, for animation that hides content until a script runs, or when native CSS already satisfies the approved direction."
license: MIT
compatibility: "Any web target. The patterns use platform features only; a scroll or timeline runtime is optional and comes from the project, never from this skill."
---

# Motion

Motion is hierarchy made visible: it tells the reader where to look next and how two things relate. If it does not do one of those, remove it.

## Choose the budget first

| Need | Smallest sufficient approach |
|---|---|
| Reveal of a block already on screen | One CSS transition on `transform` and `opacity`, triggered by `IntersectionObserver` |
| Sticky section with a horizontal track | `position: sticky` plus a progress-driven translate, real vertical fallback below the breakpoint |
| Choreography tied to scroll progress, pinned sequences, many synchronized nodes | A timeline runtime the project already ships, or scroll-driven CSS where supported |
| Route or page transition in an application | One shared transition at the router layer, not one per page |

Rule: reach for a runtime only when the choreography is genuinely complex. A simple reveal implemented as a two-hundred-line timeline is a defect, not a feature.

## Tooling is not part of the contract

Nothing below names a library. Every rule is expressed in platform capability: animate `transform` and `opacity`, read scroll progress, observe intersection, respect a media query. Any tool that provides those can implement the pattern. Pick the one the repository already uses, record it in the evidence, and do not add a dependency to satisfy this skill.

## Non-negotiables

1. **Content is visible without motion.** Never ship `opacity: 0` in the stylesheet waiting for a script. Animate from a transform, or set the initial state inside the animation scope so a failed load leaves readable content.
2. **Respect the preference.** Wrap every non-essential effect in `prefers-reduced-motion: no-preference`. When a runtime applies the initial state, scope the effect to `matchMedia("(prefers-reduced-motion: no-preference)")` and revert that scope on cleanup.
3. **One owner per element.** Two systems animating the same node fight, and the loser is usually the one you debug for an hour.
4. **Clean up.** Every scroll trigger created in a section is destroyed on unmount. Every media scope is reverted. A leaked trigger survives navigation and animates nothing.
5. **No layout thrash.** Animate `transform` and `opacity`. Animating `height`, `top`, or `width` on scroll forces layout on every frame.

## Patterns

Copy-ready examples, including the runtime-scoped version: [scroll-choreography.md](references/scroll-choreography.md).

- **Line reveal with mask**: wrap each line, translate on `Y` inside an `overflow: hidden` parent, stagger by index. The mask does the work; do not animate `clip-path` and opacity on the same element.
- **Sticky horizontal**: a tall section, a `sticky` viewport-height child, and a track translated by scroll progress. Provide a vertical stack below the breakpoint and when motion is reduced. Keyboard users must still reach every card.
- **Progress-linked UI**: header density, progress rail, section index. Drive them from one scroll listener, not from five.

## Measure

1. Record the frame budget before optimizing: a sequence with more than a few dozen animated nodes needs a smoke run, not an opinion.
2. Check the three widths (390, 768, 1440) and confirm `document.documentElement.scrollWidth <= window.innerWidth`. Horizontal scroll on the page is a defect; horizontal scroll inside a track is intentional.
3. Verify reduced motion by emulating it, not by reading the code.
4. Capture key frames at start, middle, and end of each pinned sequence. A screenshot at the end proves the final state; the middle proves the choreography.
5. Hand the measured pass to `visual-qa` before claiming the motion is done.

## Handoff

Return the chosen budget, the pattern applied, the reduced-motion behavior, the measured widths, and the screenshots. State explicitly which effects were dropped and why.
