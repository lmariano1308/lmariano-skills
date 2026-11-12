# Scroll choreography

## Line reveal, CSS only

```css
.reveal > span {
  display: block;
  transform: translateY(0.9em);
  transition: transform 600ms cubic-bezier(0.22, 1, 0.36, 1);
}
.reveal > span:nth-child(2) { transition-delay: 60ms; }
.reveal > span:nth-child(3) { transition-delay: 120ms; }
.reveal.is-in > span { transform: translateY(0); }
```

The class is added by one `IntersectionObserver`. Without JavaScript the text is already in place and readable.

## Line reveal, masked

```html
<h1 class="mask"><span class="line">Primeira linha</span><span class="line">Segunda linha</span></h1>
```

```css
.mask { display: grid; overflow: hidden; }
.mask .line { display: block; }
```

Animate `translateY` of `.line` from `110%` to `0`. The `overflow: hidden` parent is the mask. Do not combine the mask with a blur or a per-character split unless the direction explicitly calls for it; character splitting costs layout stability on reflow.

## Sticky horizontal track

```css
.rail { height: 320vh; }
.rail__viewport { position: sticky; top: 0; height: 100vh; display: grid; align-items: center; overflow: hidden; }
.rail__track { display: flex; gap: 24px; will-change: transform; }
@media (max-width: 900px), (prefers-reduced-motion: reduce) {
  .rail { height: auto; }
  .rail__viewport { position: static; height: auto; overflow: visible; }
  .rail__track { flex-direction: column; transform: none !important; }
}
```

Rules that make it usable:

- The track is translated by progress, computed from the section's own bounding box. One listener, one write per frame.
- Cards inside the track stay focusable in DOM order. A keyboard user tabbing through a translated track must not be scrolled somewhere unexpected.
- The fallback is a real vertical list, not a disabled section.

## GSAP with ReducedMotion

```ts
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export function sectionReveal(root: HTMLElement): () => void {
  const media = gsap.matchMedia();
  media.add("(prefers-reduced-motion: no-preference)", () => {
    const items = root.querySelectorAll<HTMLElement>("[data-reveal]");
    gsap.fromTo(items, { y: 24, opacity: 0 }, {
      y: 0, opacity: 1, duration: 0.55, ease: "power2.out", stagger: 0.07,
      scrollTrigger: { trigger: root, start: "top 75%", once: true },
    });
  });
  return () => media.revert();
}
```

- `matchMedia` scopes the timeline to the preference and `revert()` removes it. Without the cleanup the timeline survives navigation.
- When the initial state is set by the animation library, a blocked or failed script leaves content at its natural position. That is the difference between a degraded page and a blank one.
- One `ScrollTrigger` per section. A trigger per card multiplies listener cost and makes the timeline impossible to reason about.

## Frame budget

- Animate `transform` and `opacity` only. Anything that changes layout (`height`, `top`, `width`, `margin`) is a per-frame layout pass.
- Cap simultaneous animated nodes. If a sequence needs more than roughly forty, split it into staged groups.
- Never measure layout inside a scroll handler. Read once at the start of the frame, write once.
- `will-change` on a single track is fine; on every card it allocates compositor layers for nothing.
