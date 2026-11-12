# Direction board

## Structure

```text
prototypes/<project>-directions/
  index.html
  d1.html
  d2.html
  d3.html
  captures/          # screenshots used as evidence
```

`index.html` holds one card per direction. Each card frames the real page:

```html
<article class="direction">
  <header><h2>D1 · Prancha de obra</h2><a href="d1.html" target="_blank">abrir</a></header>
  <div class="frame"><iframe src="d1.html" width="1280" height="2400" loading="lazy"></iframe></div>
</article>
```

```css
.frame { width: 100%; aspect-ratio: 16 / 10; overflow: hidden; border: 1px solid var(--border); }
.frame iframe { transform: scale(0.32); transform-origin: top left; border: 0; }
```

- The reader scrolls the real page inside the card. A static image cannot show sticky behavior, reveal timing, or hover states.
- Below the cards, a references section names each source and the pattern being extracted.
- The page ends with the question and the options. Nothing else competes with the decision.

## What each direction must contain

- The real type family and the real palette, loaded from local files or a font CDN that is verified to answer.
- The real content, or a marked placeholder where copy does not exist. Invented copy makes a direction look finished when it is not.
- Real motion if the direction depends on it.
- One accent, one hierarchy, one obvious first action.

## Capture protocol

```sh
python3 -m http.server 8765 --bind localhost
```

1. `200` on every page.
2. Headless screenshot of each direction at 1440 and 390.
3. Look at both widths before sending the link. A direction that collapses on mobile is not a direction.
4. Keep the captures under `captures/` so the decision has evidence later.

## Grounding in an existing product

When the page sells a product that already runs:

1. Open the product and read its tokens: display face, UI face, accent in light and dark, radius, button shape, sidebar color.
2. Keep those fixed. Vary composition: poster hierarchy versus editorial grid versus application shell.
3. Never introduce a second accent because the name is still provisional.

## When the request is "more versions"

Run the generator again with a different seed or constraint set. Do not hand-draw one more variant: the point of a generator is that the next batch costs minutes, and hand-drawn variants drift toward a single taste.
