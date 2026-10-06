---
name: swiss-style
description: "Creates presentations in the Swiss International Typographic Style (瑞士国际主义 / International Typographic Style): a 12-column grid, Helvetica or Neue Haas Grotesk or Inter, weights 400 and 700 only, black, rice-white, and #DA291C. Use for Swiss-style presentations, slide decks, slides, PPT, 演示文稿, or 幻灯片, delivered as HTML and PDF. Not for posters, resumes, documents, landing pages, or product UI."
---

# Swiss Style

This skill is for presentations only. Use it to create or revise slide decks, not standalone documents or websites.

用瑞士国际主义风格（Swiss Style / International Typographic Style）设计。12 栏模块化网格，所有元素的边缘都对齐到网格线。字体用新怪诞无衬线体（Helvetica、Neue Haas Grotesk 或 Inter），只用常规和粗体两种字重；标题极大、正文很小，形成强烈的大小对比。文字一律左对齐、右边不齐，不要居中，也不要两端对齐。不对称构图，留出大面积空白。配色只用黑、米白和一个强调红（#DA291C），全部平涂，不要阴影、渐变、纹理和装饰插画。需要图片时用黑白照片或简单几何形。用细线分隔区块，用 01、02 这样的编号和小号的年份、地点信息点缀。

The pipeline follows the same shape as [Kami](https://github.com/tw93/Kami): lock a contract, write `content.json`, fill a template, run one deliver command. The visual system is the paragraph above. Paths below are relative to this skill. Keep the document in the working directory and call `python3 <skill>/scripts/build.py` by its full path.

**Update check.** At the start of a task, run `bash scripts/check-update.sh`. It checks once a day for a newer GitHub release, sends no document content, and stays silent when offline.

**Brand profile.** If `~/.config/swiss-style/brand.md` exists, read `references/brand-profile.md` and apply it. Precedence: the current prompt, then the profile, then the template. The profile may set a name, place, year, url, and logo. It does not change `#DA291C`.

## 1. Lock the contract

Before creating or changing an output, lock language, template, formats, page target, and the check command. Infer them, state one short line in the user's language, and continue. Ask at most once, and only when two templates both fit or a missing fact would change the deliverable.

| Task | What to do |
|---|---|
| New presentation | Write `content.json`, fill a slide template, deliver |
| Factual correction | Change copy. Leave the CSS alone |
| Visual rejection | Name the defect from the render, then change the smallest class or the copy |
| Diagram or photo | Black-and-white photo, or a geometric SVG from `references/diagrams.md` |

### Language

| User | Template |
|---|---|
| Chinese | `slides.html` |
| English | `slides-en.html` |
| Japanese, Korean, other | `slides-en.html`, set `lang`, then look at the slides. CJK falls through the sans stack |

### Presentation

Use `slides.html` or `slides-en.html` for slides / PPT / deck / 演示文稿 / 幻灯片. Each slide carries one assertion. Lock a slide count, including the title slide, and use a 16:9 canvas (338.67mm × 190.5mm).

Slides are HTML + PDF. There is no PPTX path. If the user requires an editable PowerPoint file, explain that this skill cannot produce it.

## 2. Sources and content

When the page names a company, product, person, date, version, price, or metric, use a primary source. If the user supplied the facts, use those and do not invent the rest. Mark a hole as `[DATA NEEDED: what]`. Never fill a hole with a guess, a stock photo, or a precise number you do not have.

Distill. Every fact lands in a template section or in the gap report.

Write `content.json` beside the HTML:

```json
{
  "type": "slides",
  "lang": "en",
  "brief": {
    "audience": "Who watches it",
    "job": "What the presentation must do",
    "template": "slides",
    "formats": ["html", "pdf"],
    "page_target": 3,
    "narrative": "Order of the argument",
    "acceptance_checks": ["three slides", "one assertion per slide", "flush left"],
    "required_facts": [],
    "required_assets": [],
    "preserve": [],
    "explicit_deviations": []
  },
  "content": {}
}
```

`type` and `brief.template` must be `slides`. Read `references/schemas/slides.json`, including `$comment`, before writing `content`. The `content.slides` array includes the title slide: use the short deck title as its assertion. `brief.page_target` must equal the array length. Validate with `python3 scripts/build.py --check-content content.json`. Strings in `content` must appear verbatim in the filled HTML. If a real field does not fit, change the schema, the template, and `references/writing.md` together. Do not drop a field to silence the checker.

## 3. What to read

| Task | Read |
|---|---|
| Fill a template | `CHEATSHEET.md`, the template, the schema |
| New presentation | those, plus `references/writing.md` and `references/deck-preflight.md` |
| Diagram | `references/diagrams.md` |
| Render or font failure | `references/production.md` |
| Reviewing a draft | `references/anti-patterns.md` |
| Changing the visual system | `references/design.md` and `assets/templates/swiss.css` together |

## 4. Fill the template

Copy `assets/templates/<file>.html` and `assets/templates/swiss.css` into the working directory. Keep `href="swiss.css"`. Do not write a page from scratch. Do not add a stylesheet, a class, or an inline style for one document.

Use only the classes in `CHEATSHEET.md`. Every `s` + `w` pair must end on or before column 12. Do not nest `.g`. Text is flush left and ragged right. Do not center, justify, or right-align. Do not add a fourth color, a third weight, a shadow, a radius, a gradient, or an illustration.

A display title is 1–3 Latin words or 2–6 Chinese characters, set with `.display`. A longer title steps down to `.display.m`. Body stays 8.5pt. If the page overflows, cut copy.

Photographs use `class="photo"` and a factual alt. The stylesheet forces them to black and white. Geometry uses `.bg-ink` or `.bg-red`. Diagrams use `class="diagram"` and the SVGs in `assets/diagrams/`.

Fill the four meta tags from the document. Keep `<meta name="generator" content="Swiss Style">`.

Formats: HTML + PDF, unless the user names one. Add a PNG when the user asks to share or embed.

## 5. Deliver

```bash
python3 <skill>/scripts/build.py --deliver filled.html content.json
```

Fix every `ERROR` and run again until `READY`. `WARN` means the page count, the page size, or the PDF renderer needs a look. `GAP` is a `[DATA NEEDED]` marker you must report.

Then look at the PDF. If you can export page images, look at those too. Walk the checklist in `CHEATSHEET.md`. One failure means a sweep of the whole document for that kind of error. If you cannot see the pages, say "build verified, visuals unconfirmed".

`python3 scripts/build.py --doctor` reports WeasyPrint, a Chromium-family browser, Helvetica, and PingFang.

Closing message:

1. The path of every file you promised.
2. `READY`, the page count, and the contract.
3. Every gap and every assumption.
4. An honest visual verdict.

## Feedback

Name the defect in one sentence: grid, type size, weight, alignment, color, crowding, or a missing empty field. Change the smallest class, or cut copy. Do not shrink type to hide overflow. After two failed passes on the same element, show the current page and two labeled variants, then stop nudging.

## When not to use this skill

- The output is not a presentation: posters, resumes, one-pagers, letters, portfolios, long documents, equity notes, changelogs, and landing pages are out of scope.
- The user requires a native, editable PPTX file.
- The user wants Kami, parchment, a serif, or ink blue.
- The user names another design system.
- The job is a product UI, a dashboard, or a restyle of an existing site.
- The user wants illustration, texture, or more than one accent color.
