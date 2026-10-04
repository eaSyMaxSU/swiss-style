# Design

Implementation of the visual law in `SKILL.md`. Tokens live in `references/tokens.json` and `assets/templates/swiss.css`. Change them together.

## Page

| Surface | Size | Margin |
|---|---|---|
| Document | A4 | 14mm, 14mm, 16mm, 14mm |
| Slide | 338.67mm × 190.5mm | 12mm, 14mm |
| Landing | max 1180px, flush left | 28px 32px 64px |

The sheet sits flush left on screen. Type is never centered inside it. The folio is `01`, `02` in the bottom-left margin, 8pt bold. Slides have no folio; the slide carries its own number.

Content width on A4 is 182mm. Twelve columns and eleven 4mm gutters leave about 11.5mm per column.

## Vertical module

4mm, 8mm, 16mm, 28mm. Those are `.mt-1` through `.mt-4`. Hairlines are 0.4pt ink. A `.band` is a full-width hairline with 4mm of air under it.

## Composition

- Put the title in columns 1–8 or 1–9. Leave the remaining columns empty.
- Put the year and place in a right-hand column, still flush left inside that column.
- One red per kind of mark on a page: the opening index, or a rule, or one flat block. Do not paint every heading red.
- A black or red rectangle is a flat fill, edge to edge of its columns. No padding on the left, so the type above and the type inside share a column line.
- Below 721px a landing page becomes four columns and every block spans them. Print pages do not collapse.

## Type

Registered sizes are the `font_sizes` list in `tokens.json`. The checker rejects any other `font-size`.

Tracking: display Latin −0.04em, display Chinese 0, meta 0.14em, body 0. Uppercase is for `.meta` only.

Screen landing sizes, because 8.5pt is too small to read in a browser: display 104px, lead 16px, body 13px, meta 11px. Below 721px the display drops to 56px. The contrast stays large.

## Images

`img.photo` is grayscale, full column, `object-fit: cover` when a height class is set. Alt states a fact. `img.diagram` keeps its black and red fills. Wordless SVGs live in `assets/diagrams/`. Captions are `.meta` under the figure, flush left.

## Tables

A table's outer edges sit on the page grid. Cell text is flush left. Internal columns are a secondary alignment. No zebra, no tint, no right-aligned numbers.

## What the checker rejects

Shadows, gradients, radius, animation, transforms, italic, a third weight, alpha, named colors, auto margins, centering, justification, right alignment, nested `.g`, a column past 12, an unregistered font size, a color outside the three hexes, a leftover `{{ }}` in a filled file, and a string in `content.json` that never reached the page.
