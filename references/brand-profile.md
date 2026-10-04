# Brand profile

Optional file: `~/.config/swiss-style/brand.md`. A copy of the shape is `references/brand.example.md`.

Read it when it exists. Use it to fill an empty name, place, year, url, or logo. The current conversation wins over the file. The file wins over an empty placeholder.

Fields:

| Field | Effect |
|---|---|
| `name` | Author, sender, or product when the user did not give one |
| `place` | The small place line |
| `year` | The small year line |
| `url` | Contact line |
| `logo` | A local image path |

The logo, when used, is `<img class="photo">` or a flat SVG in the palette, placed in a column, flush left. Do not center it. Do not recolor the page to match a brand guide. `#DA291C` stays unless the user explicitly orders a different accent in this conversation. If they do, say so as an explicit deviation in `brief`, and do not silently spread a second color through the templates.
