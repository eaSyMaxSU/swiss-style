# Diagrams

Diagrams are flat rectangles in `#111111`, `#F4F1EA`, and `#DA291C`. No arrows, no rounded caps, no gray axes, no legend in the SVG. Words live in the HTML, flush left, in `.meta` or body type.

| File | Use |
|---|---|
| `assets/diagrams/bar.svg` | One series. The marked bar is red. Empty field on the right |
| `assets/diagrams/stack.svg` | Three left-aligned bands of different lengths |
| `assets/diagrams/timeline.svg` | A hairline and three squares. The current mark is red |
| `assets/diagrams/square.svg` | A single red square when the page needs a geometric accent |

Place the image on the page grid:

```html
<figure class="s1 w7">
  <img class="diagram" src="bar.svg" alt="">
  <figcaption class="meta mt-1">01 — Marked year in red.</figcaption>
</figure>
```

Copy the SVG into the working directory, or inline the `<svg>` and keep only the three fills. `class="diagram"` must not also be `photo`: grayscale would turn the red into gray.

Change the rectangle widths to match real values. Do not add a fifth color for a second series. If the data needs two series, use two diagrams, or encode the second series as an outlined gap of paper, not a new hue.
