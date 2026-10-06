# Production

## Render

`--deliver` writes a PDF next to the HTML when it can.

1. WeasyPrint, if `import weasyprint` works.
2. Otherwise a headless Brave, Chrome, Chromium, or Edge. The script passes `--no-pdf-header-footer` so the browser does not stamp a date or a URL onto the page.

`python3 scripts/build.py --doctor` prints which of those exist. On macOS, Helvetica is the usual grotesque. Chinese falls through to PingFang SC or Noto Sans CJK. Do not vendor a random font file into the document.

If neither renderer exists, the HTML can still be `READY`, with `WARN: no pdf renderer`. Say the pages are unconfirmed.

## Page size

Slides are 13.333 × 7.5 in (about 960 × 540 pt). A `WARN` on the media box means the `@page` override did not win. Slides include a second `@page` rule for that reason. Do not "fix" it by scaling the type.

## Fonts

The stack is Inter, Neue Haas Grotesk, Helvetica Neue, Helvetica, then PingFang SC, Hiragino Sans, Noto Sans CJK, Source Han Sans. Only 400 and 700. `font-synthesis: none` stops the browser from inventing a bold or an italic.

## Checks

| Command | Does |
|---|---|
| `--check` | Templates, specimen, diagrams, palette, grid |
| `--check-content file.json` | Envelope and schema |
| `--check-content file.json filled.html` | Schema plus verbatim coverage |
| `--deliver filled.html file.json` | All of that, then the PDF |
| `--doctor` | Renderer and fonts |
| `--self-test` | Lint, specimen, deliver |

`ERROR` fails the run. `WARN` and `GAP` do not. A gap is still part of the closing message.

## Screen

Open the HTML and inspect the title slide, assertion slide, and numbered-points slide. The canvas stays 16:9, with flush-left text and empty paper. Check every PDF page for clipping, overflow, and trailing blank slides.
