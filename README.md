# rotor-site

[中文](README.zh-CN.md) | English

Personal site of rotor — https://www.rotor1996.top

A single-page portfolio + a Writing section (28 essays and counting, Chinese/English bilingual). Static HTML, no framework, no build step. Articles are written in Markdown and compiled to pages by a small Python generator.

## Structure

```
index.html            # homepage (single file, inline CSS/JS)
og.png                # share image
writing/
  gen.py              # the generator: Markdown drafts -> article pages + list page
  drafts/             # article sources, `<id>-<slug>.md` + `<id>-<slug>.en.md`
  index.html          # generated: full article list with collection filters
  <id>-<slug>.html    # generated: one page per article (bilingual, client-side toggle)
```

## Quick start (use it yourself)

```bash
git clone https://github.com/xiaojiang19960811/rotor-site.git
cd rotor-site
```

1. Write your article: `writing/drafts/29-my-topic.md` (Chinese) and
   `writing/drafts/29-my-topic.en.md` (English, or skip the `.en.md` and
   remove the toggle — the generator asserts both exist for `LIVE` ids).
2. Register it in `writing/gen.py`: add one row to `ARTS`
   `(id, slug, collection, column, zh_title, en_title, zh_summary, en_summary)`,
   add the id to `LIVE`, and its date to `DATES`.
   Collections: `infra` / `agent` / `biz` / `eng` / `solo`.
   Columns: `build` (build notes) / `garden` (knowledge garden) / `log` (lab log).
3. Build: `./build.sh` → `dist/` is ready.
4. Deploy `dist/` anywhere static:
   `npx wrangler pages deploy dist --project-name=<your-site>`
   (or drag the folder into Cloudflare Pages / Netlify).

That's the whole pipeline — no npm, no framework, just Python 3.

## How an article gets published (my own flow)

1. Write `drafts/<id>-<slug>.md` (Chinese) and `drafts/<id>-<slug>.en.md` (English).
   Keep the header line format: `> 栏目：xxx ｜ 合集：xxx ｜ 状态：初稿`.
2. Add one row to `ARTS` in `writing/gen.py`:
   `(id, slug, collection, column, zh_title, en_title, zh_summary, en_summary)`.
   Collections: `infra` / `agent` / `biz` / `eng` / `solo`.
   Columns: `build` (build notes) / `garden` (knowledge garden) / `log` (lab log).
3. Add the id to `LIVE` and its date to `DATES` in `gen.py`.
4. Run `cd writing && python3 gen.py` — it regenerates the article pages,
   the list page, and `/tmp/articles.js` (homepage data).
5. Inject `/tmp/articles.js` into `index.html` (replace the `const ARTICLES = [...];` block).
6. Deploy the static files (`index.html`, `og.png`, `writing/*.html`) to Cloudflare Pages.

The generator handles: headings, ordered/unordered lists, tables, blockquotes,
fenced code blocks, inline code, and a tiny bit of inline Markdown. Article pages
are bilingual via a client-side language toggle (content embedded as JSON).

## Writing principles

- Only write what has a traceable source. No invented stories, cases, or numbers.
- Dry, paper-like: conclusion first, definitions/arguments/evidence in sections,
  one sentence to close. No mechanical parallelism, no filler punchlines.
- Desensitize work topics: methods and tradeoffs only, no internal names or paths.

## License

Code: MIT. Articles: CC BY-NC-ND 4.0 (repost with attribution, no derivatives, non-commercial).
