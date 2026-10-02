# rotor-site

[English](README.md) | 中文

个人站 rotor — https://www.rotor1996.top

单页作品集 + Writing 栏目（28 篇文章且持续增加，中英双语）。纯静态 HTML，无框架、无构建步骤。文章用 Markdown 写，由一个 Python 小脚本编译成页面。

## 目录结构

```
index.html            # 首页（单文件，CSS/JS 内联）
og.png                # 分享图
writing/
  gen.py              # 生成器：Markdown 草稿 -> 文章页 + 列表页
  drafts/             # 文章原稿，`<id>-<slug>.md` + `<id>-<slug>.en.md`
  index.html          # 生成的：文章列表页（含合集筛选）
  <id>-<slug>.html    # 生成的：每篇文章一个页面（双语，客户端切换）
```

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

## 我自己的发布流程

1. 写 `drafts/<id>-<slug>.md`（中文）+ `drafts/<id>-<slug>.en.md`（英文）。
   头部元信息行保持格式：`> 栏目：xxx ｜ 合集：xxx ｜ 状态：初稿`。
2. 在 `writing/gen.py` 的 `ARTS` 里加一行。
3. 把 id 加入 `LIVE`，日期加入 `DATES`。
4. 跑 `cd writing && python3 gen.py`——重新生成文章页、列表页和 `/tmp/articles.js`（首页用的数据）。
5. 把 `/tmp/articles.js` 注入 `index.html`（替换 `const ARTICLES = [...];` 整段），或直接跑 `./build.sh`。
6. 部署静态文件（`index.html`、`og.png`、`writing/*.html`）到 Cloudflare Pages。

生成器支持：标题、有序/无序列表、表格、引用、代码围栏、行内代码和少量行内 Markdown。文章页通过客户端语言切换实现双语（内容以 JSON 嵌入页面）。

## 写作原则

- 只写有明确来源的内容。不编故事、不编案例、不编数字。
- 干货、论文式：结论先行，定义/论证/证据分节，一句话收束。不用机械排比，不写凑数的 punchline。
- 工作话题脱敏：只讲方法、判断、取舍，不出现内部名称和路径。

## License

代码：MIT。文章：CC BY-NC-ND 4.0（转载请注明出处，非商业用途，禁止演绎）。
