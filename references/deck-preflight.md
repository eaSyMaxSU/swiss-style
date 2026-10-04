# Deck preflight

Read this before writing slides.

- One assertion per slide. The assertion is a sentence the audience can argue with.
- The title slide carries a huge `01`, the place, the year, and a short title packed to the bottom (`.pack-end`). The field above stays empty.
- Later slides put the number in columns 1–2 and the assertion in columns 3–12, bottom-aligned with `.end`.
- Support is one line in columns 1–6, or up to four points. Each point's number occupies column 1. The words start at column 2.
- Do not center the assertion in the leftover space.
- Do not add a logo lockup, a footer URL, or a progress dot.
- Duplicate a `<section class="slide">` to add a slide. The last slide must not force a trailing blank page; the template already clears the break on the last section.
- If the assertion wraps to four lines at 44pt, cut it. Do not drop the size to an unregistered step.
