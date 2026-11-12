---
name: motion-design
description: "Design and implement interface motion that carries hierarchy instead of decorating it. Use when the request is 'anima isso', 'põe motion', 'faz o reveal', 'scroll horizontal', 'quero impacto ao rolar', or when a landing needs choreography, reduced-motion handling, and measured scroll behavior. Do not use for a single hover transition, for animation that hides content until JavaScript runs, or when native CSS already satisfies the approved direction."
license: MIT
compatibility: "Browser with CSS scroll-driven features and optional GSAP; both patterns are documented, neither is mandatory."
---

# Motion design

Motion is hierarchy made visible: it tells the reader where to look next and how two things relate. If it does not do one of those, remove it.

## Choose the budget first

| Need | Tool |
|---|---|
| Reveal of a block already on screen | CSS transition on `transform` and `opacity` |
| Sticky section with horizontal track | Native CSS `position: sticky` plus `scroll-snap`, vertical fallback |
| Choreography tied to scroll progress, multiple synchronized elements, pinned timelines | GSAP with `ScrollTrigger` |
| Route or page transition in an application | Framework-level transition, one shared runtime |

Rule: reach for GSAP only when the scroll choreography is genuinely complex. A simple reveal implemented in a 200-line timeline is a defect, not a feature.

## Non-negotiables

1. **Content is visible without motion.** Never ship `opacity: 0` in the stylesheet waiting for a script. Animate from a transform, or set the initial state in the animation library so a failed load leaves readable content.
2. **Respect the preference.** Wrap every non-essential effect in `prefers-reduced-motion: no-preference`. GSAP: `gsap.matchMedia()` and `revert()` on cleanup. CSS: the media query around the transition.
3. **One owner per element.** Two libraries animating the same node fight, and the loser is usually the one you debug for an hour.
4. **Clean up.** Every `ScrollTrigger` created in a component is killed on unmount. Every `matchMedia` is reverted. A leaked trigger survives navigation and animates nothing.
5. **No layout thrash.** Animate `transform` and `opacity`. Animating `height`, `top`, or `width` on scroll forces layout on every frame.

## Patterns

Copy-ready snippets and the fallback matrix: [scroll-choreography.md](references/scroll-choreography.md).

- **Line reveal with mask**: wrap each line, translate on `Y` inside an `overflow: hidden` parent, stagger by index. The mask does the work; do not animate `clip-path` and opacity on the same element.
- **Sticky horizontal**: a tall section, a `sticky` viewport-height child, and a track translated by scroll progress. Provide a vertical stack below the breakpoint and when motion is reduced. Keyboard users must still reach every card.
- **Progress-linked UI**: header density, progress rail, section index. Drive them from one scroll listener or one `ScrollTrigger`, not from five.

## Measure

1. Record the frame budget before optimizing: a timeline with more than a few dozen animated nodes needs a smoke run, not an opinion.
2. Check the three widths (390, 768, 1440) and confirm `document.documentElement.scrollWidth <= window.innerWidth`. Horizontal scroll on the page is a defect; horizontal scroll inside a track is intentional.
3. Verify reduced motion by emulating it, not by reading the code.
4. Capture key frames at start, middle, and end of each pinned sequence. A screenshot at the end proves the final state; the middle proves the choreography.
5. Re-run the measured pass through `visual-qa` before claiming the motion is done.

## Handoff

Return the chosen budget, the pattern applied, the reduced-motion behavior, the measured widths, and the screenshots. State explicitly which effects were dropped and why.
