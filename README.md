# Swiss Style

A document skill in the Swiss International Typographic Style: a 12-column grid, a grotesque sans in regular and bold, and only black, rice-white (`#F4F1EA`), and red (`#DA291C`).

It sets resumes, one-pagers, letters, portfolios, long documents, equity notes, changelogs, slide decks, and landing pages. The agent instructions are `SKILL.md`.

The document pipeline — contract, `content.json`, template, one deliver command — follows the shape of [Kami](https://github.com/tw93/Kami) by Tw93, which is MIT licensed. The grid, the templates, the stylesheet, and the checker in this repository are original.

## Use

```bash
git clone git@github.com:eaSyMaxSU/swiss-style.git
ln -s "$PWD" ~/.claude/skills/swiss-style
mkdir -p ~/.cursor/skills
ln -s "$PWD" ~/.cursor/skills/swiss-style
```

Copy a file from `assets/templates/` and `assets/templates/swiss.css` into the working directory. Fill the `{{ }}` slots. Then:

```bash
python3 scripts/build.py --deliver filled.html content.json
```

`READY` means the grid, the palette, the type steps, and the content coverage passed. PDF rendering uses WeasyPrint or a headless Chromium-family browser. `python3 scripts/build.py --doctor` shows what this machine has.

`examples/one-pager/` is a filled specimen.

## License

[MIT](LICENSE). The skill can be copied into an agent skill directory and changed. Neue Haas Grotesk and Helvetica are not included; the stylesheet names them and falls back to a grotesque that is already installed.
