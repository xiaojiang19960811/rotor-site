# rotor-site

[中文](README.zh-CN.md) | English

个人站 rotor — https://www.rotor1996.top

A single-page portfolio + a Writing section (28 essays and counting, Chinese/English bilingual). Static HTML, no framework, no build step. Articles are written in Markdown and compiled to pages by a small Python generator.

## 快速上手（拿去直接用）

```bash
git clone https://github.com/xiaojiang19960811/rotor-site.git
cd rotor-site
```

1. 写文章：`writing/drafts/29-my-topic.md`（中文）+ `writing/drafts/29-my-topic.en.md`（英文；不想做双语就删掉英文切换，生成器要求 `LIVE` 的文章中英成对）。
2. 在 `writing/gen.py` 注册：在 `ARTS` 加一行
   `(id, slug, 合集, 栏目, 中文标题, 英文标题, 中文一句话, 英文一句话)`，
   把 id 加入 `LIVE`，日期加入 `DATES`。
   合集：`infra` / `agent` / `biz` / `eng` / `solo`；
   栏目：`build`（建造复盘）/ `garden`（知识花园）/ `log`（实验日志）。
3. 构建：`./build.sh` → 得到 `dist/`。
4. 把 `dist/` 部署到任何静态托管：
   `npx wrangler pages deploy dist --project-name=<你的站点名>`
   （或直接拖进 Cloudflare Pages / Netlify）。

整个管线就是这样——不用 npm，不用框架，只要 Python 3。

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

## How an article gets published

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
