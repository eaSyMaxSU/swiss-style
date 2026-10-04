---
name: swiss-style
description: "Typeset print and static pages in the Swiss International Typographic Style (瑞士国际主义 / International Typographic Style): a 12-column grid, Helvetica or Neue Haas Grotesk or Inter, weights 400 and 700 only, black, rice-white, and #DA291C. Use when the user asks for Swiss Style, 瑞士风格, a grid poster, or to make a resume, one-pager, letter, portfolio, long document, equity note, changelog, slides, or landing page (PDF, 排版, 简历, 一页纸, 信件, 作品集, 白皮书, PPT, 落地页)."
---

# Swiss Style

用瑞士国际主义风格（Swiss Style / International Typographic Style）设计。12 栏模块化网格，所有元素的边缘都对齐到网格线。字体用新怪诞无衬线体（Helvetica、Neue Haas Grotesk 或 Inter），只用常规和粗体两种字重；标题极大、正文很小，形成强烈的大小对比。文字一律左对齐、右边不齐，不要居中，也不要两端对齐。不对称构图，留出大面积空白。配色只用黑、米白和一个强调红（#DA291C），全部平涂，不要阴影、渐变、纹理和装饰插画。需要图片时用黑白照片或简单几何形。用细线分隔区块，用 01、02 这样的编号和小号的年份、地点信息点缀。

The pipeline follows the same shape as [Kami](https://github.com/tw93/Kami): lock a contract, write `content.json`, fill a template, run one deliver command. The visual system is the paragraph above. Paths below are relative to this skill. Keep the document in the working directory and call `python3 <skill>/scripts/build.py` by its full path.

**Update check.** At the start of a task, run `bash scripts/check-update.sh`. It checks once a day for a newer GitHub release, sends no document content, and stays silent when offline.

**Brand profile.** If `~/.config/swiss-style/brand.md` exists, read `references/brand-profile.md` and apply it. Precedence: the current prompt, then the profile, then the template. The profile may set a name, place, year, url, and logo. It does not change `#DA291C`.

## 1. Lock the contract

Before creating or changing an output, lock language, template, formats, page target, and the check command. Infer them, state one short line in the user's language, and continue. Ask at most once, and only when two templates both fit or a missing fact would change the deliverable.

| Task | What to do |
|---|---|
| New document | Write `content.json`, fill a template, deliver |
| Factual correction | Change copy. Leave the CSS alone |
| Visual rejection | Name the defect from the render, then change the smallest class or the copy |
| Diagram or photo | Black-and-white photo, or a geometric SVG from `references/diagrams.md` |

### Language

| User | Template |
|---|---|
| Chinese | `*.html` |
| English | `*-en.html` |
| Japanese, Korean, other | `*-en.html`, set `lang`, then look at the pages. CJK falls through the sans stack |

### Document

| User says | Document | CN | EN | Pages |
|---|---|---|---|---|
| one-pager / 方案 / 执行摘要 | one-pager | `one-pager.html` | `one-pager-en.html` | 1 |
| white paper / 白皮书 / 长文 | long-doc | `long-doc.html` | `long-doc-en.html` | 6–15 |
| letter / 信件 / 辞职信 / memo | letter | `letter.html` | `letter-en.html` | 1 |
| portfolio / 作品集 | portfolio | `portfolio.html` | `portfolio-en.html` | 3–6 |
| resume / CV / 简历 | resume | `resume.html` | `resume-en.html` | 2 |
| slides / PPT / deck / 演示 | slides | `slides.html` | `slides-en.html` | one assertion each |
| equity / 研报 / 估值 | equity-report | `equity-report.html` | `equity-report-en.html` | 2–4 |
| changelog / 更新日志 | changelog | `changelog.html` | `changelog-en.html` | as long as the versions |
| landing / 落地页 / 产品页 | landing-page | `landing-page.html` | `landing-page-en.html` | screen |

Signals: one page for an investor or an executive → one-pager. Formal correspondence → letter. Two pages of career evidence → resume. Visual cases → portfolio. A sustained argument → long-doc. One assertion per slide → slides. Thesis, catalysts, and risks → equity-report. Version facts → changelog. A browser product page → landing-page.

Slides are HTML + PDF. There is no PPTX path. A deck that can be restyled in PowerPoint will not hold this grid.

Landing pages are HTML only. The 12 columns collapse to full-width blocks below 721px. See `references/design.md`.

## 2. Sources and content

When the page names a company, product, person, date, version, price, or metric, use a primary source. If the user supplied the facts, use those and do not invent the rest. Mark a hole as `[DATA NEEDED: what]`. Never fill a hole with a guess, a stock photo, or a precise number you do not have.

Distill. Every fact lands in a template section or in the gap report.

Write `content.json` beside the HTML:

```json
{
  "type": "one-pager",
  "lang": "en",
  "brief": {
    "audience": "Who reads it",
    "job": "What the page must do",
    "template": "one-pager",
    "formats": ["html", "pdf"],
    "page_target": 1,
    "narrative": "Order of the argument",
    "acceptance_checks": ["one page", "flush left"],
    "required_facts": [],
    "required_assets": [],
    "preserve": [],
    "explicit_deviations": []
  },
  "content": {}
}
```

`type` is a file in `references/schemas/`. Read that schema, including `$comment`, before writing `content`. Validate with `python3 scripts/build.py --check-content content.json`. Strings in `content` must appear verbatim in the filled HTML. If a real field does not fit, change the schema, the template, and `references/writing.md` together. Do not drop a field to silence the checker.

## 3. What to read

| Task | Read |
|---|---|
| Fill a template | `CHEATSHEET.md`, the template, the schema |
| New document | those, plus the type's section in `references/writing.md` |
| Slides | also `references/deck-preflight.md` |
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

Formats: HTML + PDF, unless the user names one. Landing page: HTML only. Add a PNG when the user asks to share or embed.

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

- The user wants Kami, parchment, a serif, or ink blue.
- The user names another design system.
- The job is a product UI, a dashboard, or a restyle of an existing site.
- The user wants illustration, texture, or more than one accent color.
