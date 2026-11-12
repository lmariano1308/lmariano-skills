# Prototype first

A direction is decided by looking at a running page. Use this recipe when the design is still open.

## Layout

```text
~/prototypes/<project>-directions/
  index.html      # the three directions side by side, plus references
  t1.html
  t2.html
  t3.html
```

Keep prototypes outside the repository: they must not pollute the branch, the build, or the diff.

## index.html

- One card per direction with a real iframe at `width: 1280px`, scaled to about `0.32` with `transform-origin: top left`. The reader scrolls the real page inside the card.
- A visible "open" link per direction, so the page can be inspected full size.
- A references block naming the source site and the pattern being extracted ("hierarchy by metadata density", "1 px rule as structure"). Never "screenshot to copy".
- A single closing question with the options, for example `T1, T2, or T3?`.

## Serve and check

Serve the directory over HTTP on the loopback interface with whatever static server the machine already has; most language runtimes ship one. Record the port you used.

Then, before sending a link:

1. Confirm `200` on `index.html` and on every direction page.
2. Capture each page in a browser engine and inspect the captures.
3. Confirm no direction relies on a font that failed to load and no iframe is blank.

## Rules that keep the comparison useful

- Real typography, real palette, real motion. A direction that cannot be judged at a glance teaches nothing.
- Vary composition and theme between directions, not the type family and not the accent. Three unrelated brands cannot be compared.
- If the page sells a product that already exists, read the product's own tokens first. The directions vary layout and theme around that system.
- Never present a direction the author would not ship.
