# Swiss Style · Cheatsheet

Scan this before filling a template. The law is the first paragraph of `SKILL.md`. Measures live in `references/design.md`.

## Palette

| Role | Hex | Use |
|---|---|---|
| Ink | `#111111` | Text, rules, flat black blocks |
| Paper | `#F4F1EA` | Page, and type on a black or red block |
| Red | `#DA291C` | One accent: an index, a rule, or a flat block |

No other hex. No gray. No transparency.

## Type

Grotesque only: Inter, Neue Haas Grotesk, Helvetica Neue, Helvetica. Weights 400 and 700. No italic.

| Class | Size | Weight | Use |
|---|---|---|---|
| `.display` | 76pt | 700 | Deck title, 1–3 words |
| `h1`, `.display.m` | 44pt | 700 | Slide assertion |
| `.index-xl` | 88pt | 700 | Slide number |
| `.figure` | 36pt | 700 | Metric or chapter number |
| `.heading`, `h2` | 14pt | 700 | Section title |
| `.lead` | 11pt | 400 | Opening sentence |
| `.index` | 11pt | 700 | 01, 02 |
| body | 8.5pt | 400 | Reading text |
| `.meta` | 7.5pt | 400 | Year, place, source |

Do not invent a size between these.

Chinese display titles do not use negative tracking. Body tracking stays 0.

## Grid

12 columns. Gutter 4mm. Slide size 338.67mm × 190.5mm (16:9), margins 12mm vertically and 14mm horizontally.

| Class | Meaning |
|---|---|
| `.slide` | The slide grid. Never nest grids. Never put `s` or `w` on it |
| `.g` | A standalone grid. Never nest it inside a slide or another grid |
| `.s1`–`.s12` | Start column |
| `.w1`–`.w12` | Span. `start + span - 1` must be ≤ 12 |
| `.mt-1` … `.mt-4` | 4 / 8 / 16 / 28mm above |
| `.band` | Full-width hairline, then 4mm |
| `.rule` | Hairline inside a cell. A full rule is `s1 w12 rule` |
| `.end` | Sit on the bottom of the row |
| `.spacer`, `.spacer-l` | 16mm / 40mm of empty paper |
| `.pack-end` | Pack a slide's rows to the bottom |
| `.bg-ink`, `.bg-red` | Flat rectangle |
| `.h-s` … `.h-xl` | 24 / 48 / 80 / 110mm |
| `.photo` | Black-and-white photograph, full column width |
| `.diagram` | Geometric SVG, not grayed |

A block in columns 1–7 with 8–12 empty is the usual asymmetry. Do not mirror the whole page.

## Checklist

- Every box, rule, and image starts and ends on a column line
- Text is flush left, ragged right
- One empty field remains
- Red is `#DA291C` and nothing else is
- Numbers read 01, 02. Year and place are `.meta`
- No shadow, radius, gradient, texture, icon, or illustration
- Body was not shrunk to fix an overflow
