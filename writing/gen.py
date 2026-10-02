#!/usr/bin/env python3
"""Writing 二级页面生成器：单一数据源 -> /tmp/articles.js + writing/<slug>.html
用法: python3 gen.py
- 文章元数据在这里维护（标题/描述/合集/栏目/是否发布）
- 正文来自 drafts/<id>-<slug>.md 和 drafts/<id>-<slug>.en.md
- 站点 CSS 直接复用 index.html 的 <style>，视觉自动同步
"""
import re, json, html, os

ROOT = "/home/hatch/workspace/rotor-site"
DRAFTS = f"{ROOT}/writing/drafts"
OUTDIR = f"{ROOT}/writing"
SITE_CSS_ANCHOR = ("<style>", "</style>")

# id, slug, 合集, 栏目, 中标题, 英标题, 中一句话, 英一句话
ARTS = [
 ("01","newsletter-newsroom","infra","build","做资讯简报：机器干活，人把关","Newsletter, Built Like a Newsroom","发现初筛归机器，核验发布归人；六道质量门禁","Machines discover and draft; humans verify and ship. Six quality gates."),
 ("02","persona-from-briefs","agent","build","从 39 份日报，反推一个数字人的人格","Deriving a Persona from 39 Briefs","不从 prompt 空想性格，从 161 条简报行为提炼人格","Don't imagine a persona from prompts — distill it from 161 briefs of behavior."),
 ("03","fork-selective-upgrade","infra","build","Fork 开源项目：选择性升级","Forking Open Source: Selective Upgrades","按主题手工吸收上游，高风险项不得无确认删除","Absorb upstream by topic, by hand. High-risk hunks need explicit sign-off."),
 ("04","proxy-media-api","infra","build","接第三方媒体 API：代理、缓存和排障纪律","Proxying Media APIs: Discipline Over Magic","同源代理流式转发不落盘；没做 A/B 前不定根因","Same-origin proxy streaming, no disk. No root cause without A/B."),
 ("05","monorepo-future-split","agent","build","单仓不拆，但按“未来可拆”组织","Monorepo, Organized for a Future Split","拒绝拆微仓政治正确，也拒绝意大利面单仓","Neither micro-repo dogma nor spaghetti monorepo."),
 ("06","ai-comics-pipeline","infra","build","AI 漫画是连续生产，不是单图生成","AI Comics Are a Production Line","角色场景道具镜头受控；生成成功≠成品","Controlled cast, sets and shots. A successful call is not a finished product."),
 ("07","one-biz-four-clients","biz","build","一个业务四个端，怎么组织代码","One Business, Four Clients: Code Organization","目录第一层按端语义命名；清洗下沉 adapter 层","Name top-level dirs by client semantics; push cleanup into adapters."),
 ("08","selfhost-video-models","infra","build","部署开源视频模型前，先看三条边界","Before Self-Hosting Open Video Models","开放权重≠开放完整链路；许可证有地域排除","Open weights ≠ open pipeline. Licenses have regional exclusions."),
 ("09","done-vs-verified","eng","garden","“已完成”不等于“已验证”","“Done” Is Not “Verified”","六个结论不能互相替代；失败证据也是证据","Six conclusions, none interchangeable. Failure is evidence too."),
 ("10","knowledge-base-rules","eng","garden","给知识库立规矩：什么算数，什么不算","Rules for the Knowledge Base","正式规则三来源；AI 推断一律进候选区","Formal rules have three sources. AI inference stays in candidates."),
 ("11","ai-codes-humans-judge","eng","garden","AI 写代码越快，人越要负责判断","The Faster AI Codes, the More Humans Must Judge","开发人员真正参与的七件事；SDD 不保证 Token 更少","Seven things developers actually do. SDD doesn't promise fewer tokens."),
 ("12","agent-memory-layers","agent","garden","Agent 的记忆怎么做分层","Layered Memory for Agents","六层分别管理；遗忘是淡出不是删除","Six layers, managed separately. Forgetting fades, not deletes."),
 ("13","calling-ai-apis","infra","garden","调 AI 接口，不能只看“通没通”","Calling AI APIs: Beyond “It Works”","8 个语义阶段；传输存活≠语义进展","Eight semantic stages. Connection alive ≠ progress made."),
 ("14","public-not-crawlable","biz","garden","公开能看，不等于能爬","Public ≠ Crawlable","红黄绿三级准入；反爬绕过永久禁止","Red/yellow/green access tiers. Anti-scrape bypass permanently banned."),
 ("15","ui-claims-proof","eng","garden","界面只讲能证明的话","UI Should Only Claim What's Proven","“任务完成≠资产确认”；不虚构统一接口","“Task done ≠ asset confirmed.” Never invent a unified API."),
 ("16","ai-app-security","infra","garden","AI 应用的安全审计：内容过滤只是最后一环","AI App Security: Filtering Is the Last Step","提示词快照是高敏证据；fail-open/fail-closed 取舍","Prompt snapshots are sensitive evidence. Fail-open vs fail-closed tradeoffs."),
 ("17","discover-execute-confirm","agent","garden","AI 做事：发现、执行、确认是三件事","Discover, Execute, Confirm: Three Separate Things","前一阶段完成不默认授权后一阶段","Finishing one phase never authorizes the next."),
 ("18","model-said-success","agent","garden","模型说“成功了”，不等于真成功了","The Model Said “Success” — Prove It","决策与执行拆开；成功结论绑定外部证据","Split deciding from doing. Success claims need external evidence."),
 ("19","h5-base","biz","garden","H5 底座：比脚手架多一层，比业务少一层","H5 Base: Thicker Than a Scaffold","带轻业务骨架的底座；路由 meta 承载语义","A base with a light business skeleton. Route meta carries semantics."),
 ("20","writing-skills","agent","garden","Skill 怎么写才有人用","Writing Skills People Actually Use","一 Skill 一任务；高频复用才沉淀","One skill, one task. Distill only what gets reused."),
 ("21","ai-remembers-too-much","agent","log","AI 记得太多：一次记忆误记复盘","When AI Remembers Too Much","14 条候选 11 条误记，模型却给 0.99 置信度","11 of 14 recalled wrong, model confidence 0.99."),
 ("22","nine-minutes-first-token","infra","log","首字等了 9 分钟：一次网关超时复盘","Nine Minutes for the First Token","95% 耗时在首有效输出前；预算 90s/180s/换号 1 次","95% of time before first semantic output. Budgets: 90s/180s/1 swap."),
 ("23","cache-billing-trap","infra","log","缓存计费的坑：三笔账必须互斥","The Cache Billing Trap","修复前按 2.25x 收费；纵向闭环测试缺失","Billed at 2.25x before the fix. The vertical test loop was missing."),
 ("24","webrtc-white-screen","infra","log","WebRTC 白屏：先别急着上 TURN","WebRTC White Screen: Don't Rush to TURN","根因是 NAT 后公网地址发布，不是必须上 TURN","Root cause: public address behind NAT, not a missing TURN."),
 ("25","team-space-leak","eng","log","团队空间看到了别人的项目：一次越权复盘","When Team Spaces Leaked Projects","空 organizationId 历史数据回退；多租户隔离教训","Empty org-id fallback on legacy data. A multi-tenant lesson."),
 ("26","tinykit-decisions","solo","build","TinyKit：一个工具站的决策链","TinyKit: Anatomy of a Decision Chain","痛点调研→31 工具→API→MCP","Pain research → 31 tools → API → MCP."),
 ("27","video-pipeline-v2-v4","solo","build","AI 视频管线：v2 到 v4 的迭代","Video Pipeline: v2 to v4","三次评审返工；字幕/边距/缓存的生产坑","Three review rounds. Subtitles, margins, cache — production pitfalls."),
 ("28","gumroad-launch","solo","build","Gumroad 上架记：三个数字产品","Gumroad Launch Notes","$9/$29/$39 定价；PayPal 收款；中国卖家坑","$9/$29/$39 pricing, PayPal payout, traps for CN sellers."),
]

# 只有这里列出的 id 才会生成页面（发布门控）
LIVE = {"01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28"}
# 发布日期（首页"最新"排序用）
DATES = {"01": "2026-10-02", "02": "2026-10-02", "03": "2026-10-02", "04": "2026-10-02", "05": "2026-10-02", "06": "2026-10-02", "07": "2026-10-02", "08": "2026-10-02", "09": "2026-10-02", "10": "2026-10-02", "11": "2026-10-02", "12": "2026-10-02", "13": "2026-10-02", "14": "2026-10-02", "15": "2026-10-02", "16": "2026-10-02", "17": "2026-10-02", "18": "2026-10-02", "19": "2026-10-02", "20": "2026-10-02", "21": "2026-10-02", "22": "2026-10-02", "23": "2026-10-02", "24": "2026-10-02", "25": "2026-10-02", "26": "2026-10-02", "27": "2026-10-02", "28": "2026-10-02"}

COLLECTIONS = {
 "infra": ("AI 基础设施", "AI Infrastructure"),
 "agent": ("Agent 与数字人", "Agents & Digital Humans"),
 "biz": ("多端业务", "Multi-platform"),
 "eng": ("工程工具", "Engineering"),
 "solo": ("个人建造", "Solo Builds"),
}
COLUMNS = {
 "build": ("建造复盘", "Build Notes"),
 "garden": ("知识花园", "Garden"),
 "log": ("实验日志", "Lab Log"),
}

def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s

def md_to_html(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1; continue
        if s.startswith("```"):
            lang = s[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1  # 跳过结束围栏
            code = html.escape("\n".join(buf))
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{code}</code></pre>")
            continue
        if s.startswith("# "):
            i += 1; continue
        if s.startswith("## "):
            out.append(f"<h2>{inline(s[3:])}</h2>"); i += 1; continue
        if s == "---":
            out.append("<hr>"); i += 1; continue
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip()); i += 1
            if "wiki/" in " ".join(buf) or "状态" in " ".join(buf):
                continue
            out.append("<blockquote>" + "<br>".join(inline(b) for b in buf) + "</blockquote>")
            continue
        if s.startswith("- "):
            buf = []
            while i < n and lines[i].strip().startswith("- "):
                buf.append(lines[i].strip()[2:]); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in buf) + "</ul>")
            continue
        if re.match(r"^\d+[.)]\s", s):
            buf = []
            while i < n and re.match(r"^\d+[.)]\s", lines[i].strip()):
                buf.append(re.sub(r"^\d+[.)]\s", "", lines[i].strip())); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(b)}</li>" for b in buf) + "</ol>")
            continue
        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            body = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
            t = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in body[0]) + "</tr></thead><tbody>"
            for r in body[1:]:
                t += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            out.append(t + "</tbody></table>")
            continue
        buf = [s]; i += 1
        while i < n and lines[i].strip() and not lines[i].strip().startswith(("#", ">", "-", "|", "---")) and not re.match(r"^\d+[.)]\s", lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        out.append("<p>" + " ".join(inline(b) for b in buf) + "</p>")
    return "\n".join(out)

def site_css():
    s = open(f"{ROOT}/index.html", encoding="utf-8").read()
    m = re.search(r"<style>(.*?)</style>", s, re.S)
    return m.group(1)

PAGE_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_zh} — rotor</title>
<meta name="description" content="{desc_zh}">
<style>{css}
.art-nav{{display:flex;align-items:center;justify-content:space-between;padding:20px clamp(20px,4vw,48px);border-bottom:1px solid var(--line);position:sticky;top:0;background:rgba(11,11,12,.9);backdrop-filter:blur(8px);z-index:50}}
.art-nav .logo{{font-weight:700;font-size:20px;color:var(--ink);text-decoration:none}}
.art-nav .logo sup{{color:var(--lime);font-size:10px}}
.art-nav .mid{{display:flex;gap:18px;align-items:center}}
.art-nav a.lnk{{color:var(--muted);text-decoration:none;font-size:14px}}
.art-nav a.lnk:hover{{color:var(--lime)}}
.art-wrap{{max-width:760px;margin:0 auto;padding:clamp(40px,6vh,72px) clamp(22px,5vw,40px) 40px}}
.prev-next{{display:flex;justify-content:space-between;gap:16px;margin-top:64px;padding-top:28px;border-top:1px solid var(--line)}}
.prev-next a{{color:var(--muted);text-decoration:none;font-size:15px;max-width:44%}}
.prev-next a:hover{{color:var(--lime)}}
.prev-next a span{{display:block;font-family:var(--font-m);font-size:10px;letter-spacing:.16em;text-transform:uppercase;margin-bottom:8px;color:var(--lime)}}
.prev-next .nx{{text-align:right;margin-left:auto}}
.art-foot{{max-width:760px;margin:0 auto;padding:0 clamp(22px,5vw,40px) 80px;color:var(--muted);font-size:13px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px}}
.soon-banner{{display:inline-block;margin-left:10px;padding:3px 12px;border:1px dashed var(--lime);border-radius:20px;color:var(--lime);font-size:12px;letter-spacing:.08em}}
</style>
</head>
<body>
<nav class="art-nav">
  <a class="logo" href="/">rotor<sup>®</sup></a>
  <div class="mid">
    <a class="lnk" href="/#writing" data-i18n="back">← 写作</a>
    <div class="lang"><button id="btn-zh" class="on">中文</button><button id="btn-en">EN</button></div>
  </div>
</nav>
<article class="art-wrap">
  <div class="reader-top" id="reader-meta"></div>
  <div class="reader-body" id="reader-body"></div>
  <div class="prev-next" id="prev-next"></div>
</article>
<div class="art-foot"><span>© 2026 rotor®</span><span><a href="https://github.com/xiaojiang19960811/rotor-site" target="_blank" rel="noopener" style="color:var(--muted)">GitHub 开源</a></span><span data-i18n="license">CC BY-NC-ND · 转载请注明出处</span></div>
<script>
const LANG0 = localStorage.getItem('rotor-lang') || 'zh';
let LANG = LANG0;
const DATA = {data_json};
const STR = {{
  zh: {{back:"← 写作", license:"CC BY-NC-ND · 转载请注明出处", prev:"← 上一篇", next:"下一篇 →", col:"{col_zh}", column:"{column_zh}", soon:"即将发布 · 敬请期待"}},
  en: {{back:"← Writing", license:"CC BY-NC-ND · attribution required", prev:"← Prev", next:"Next →", col:"{col_en}", column:"{column_en}", soon:"Coming soon"}}
}};
function esc(s){{ const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }}
function render(){{
  const t = STR[LANG], a = DATA;
  document.documentElement.lang = LANG==='zh' ? 'zh-CN' : 'en';
  document.getElementById('btn-zh').classList.toggle('on', LANG==='zh');
  document.getElementById('btn-en').classList.toggle('on', LANG==='en');
  document.querySelectorAll('[data-i18n]').forEach(el=>{{
    const k = el.getAttribute('data-i18n'); if(t[k]!==undefined) el.innerHTML = t[k];
  }});
  document.title = esc(a.t[LANG]) + ' — rotor';
  document.getElementById('reader-meta').innerHTML =
    '<span class="col-tag">'+esc(t.col)+'</span><span class="col-tag">'+esc(t.column)+'</span>';
  document.getElementById('reader-body').innerHTML =
    '<h1>'+esc(a.t[LANG])+'</h1>' + a.body[LANG];
  const pn = document.getElementById('prev-next');
  let h = '';
  if(a.prev) h += '<a href="'+a.prev.url+'"><span>'+t.prev+'</span>'+esc(a.prev.t[LANG])+'</a>';
  if(a.next) h += '<a class="nx" href="'+a.next.url+'"><span>'+t.next+'</span>'+esc(a.next.t[LANG])+'</a>';
  pn.innerHTML = h;
  pn.style.display = h ? 'flex' : 'none';
}}
document.getElementById('btn-zh').onclick = ()=>{{ LANG='zh'; localStorage.setItem('rotor-lang','zh'); render(); }};
document.getElementById('btn-en').onclick = ()=>{{ LANG='en'; localStorage.setItem('rotor-lang','en'); render(); }};
render();
</script>
</body>
</html>
"""

LIST_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Writing — rotor</title>
<meta name="description" content="{desc_zh}">
<style>{css}
.art-nav{{display:flex;align-items:center;justify-content:space-between;padding:20px clamp(20px,4vw,48px);border-bottom:1px solid var(--line);position:sticky;top:0;background:rgba(11,11,12,.9);backdrop-filter:blur(8px);z-index:50}}
.art-nav .logo{{font-weight:700;font-size:20px;color:var(--ink);text-decoration:none}}
.art-nav .logo sup{{color:var(--lime);font-size:10px}}
.art-nav .mid{{display:flex;gap:18px;align-items:center}}
.art-nav a.lnk{{color:var(--muted);text-decoration:none;font-size:14px}}
.art-nav a.lnk:hover{{color:var(--lime)}}
.list-head{{max-width:1200px;margin:0 auto;padding:clamp(48px,7vh,84px) clamp(22px,5vw,40px) 8px}}
.list-head h1{{font-size:clamp(44px,7vw,96px);font-weight:700;letter-spacing:-.03em;line-height:1}}
.list-head h1 .stroke{{color:transparent;-webkit-text-stroke:1.5px var(--lime)}}
.list-head p{{color:var(--muted);max-width:640px;margin:18px 0 30px;font-size:clamp(14px,1.6vw,17px)}}
.filters{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px}}
.f-chip{{font-family:var(--font-m);font-size:11px;letter-spacing:.14em;text-transform:uppercase;border:1px solid var(--line);border-radius:99px;padding:8px 18px;color:var(--muted);background:none;cursor:pointer}}
.f-chip.on{{border-color:var(--lime);color:var(--lime)}}
.list-wrap{{max-width:1200px;margin:0 auto;padding:0 clamp(22px,5vw,40px) 60px}}
.list-foot{{max-width:1200px;margin:0 auto;padding:0 clamp(22px,5vw,40px) 80px;color:var(--muted);font-size:13px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;border-top:1px solid var(--line);padding-top:24px}}
</style>
</head>
<body>
<nav class="art-nav">
  <a class="logo" href="/">rotor<sup>&reg;</sup></a>
  <div class="mid">
    <a class="lnk" href="/" data-i18n="back">&larr; rotor</a>
    <div class="lang"><button id="btn-zh" class="on">中文</button><button id="btn-en">EN</button></div>
  </div>
</nav>
<header class="list-head">
  <h1>Wr<span class="stroke">i</span>ting</h1>
  <p data-i18n="sub">{sub_zh}</p>
  <div class="filters" id="filters"></div>
</header>
<main class="list-wrap"><div id="col-list"></div></main>
<div class="list-foot"><span>&copy; 2026 rotor&reg;</span><span><a href="https://github.com/xiaojiang19960811/rotor-site" target="_blank" rel="noopener" style="color:var(--muted)">GitHub 开源</a></span><span data-i18n="license">CC BY-NC-ND &middot; 转载请注明出处</span></div>
<script>
let LANG = localStorage.getItem('rotor-lang') || 'zh';
const ARTICLES = {articles_json};
const COLS = {cols_json};
const STR = {{
  zh: {{back:"&larr; rotor", sub:"{sub_zh}", license:"CC BY-NC-ND · 转载请注明出处", all:"全部", soon:"即将发布", read:"阅读 &rarr;"}},
  en: {{back:"&larr; rotor", sub:"{sub_en}", license:"CC BY-NC-ND · attribution required", all:"All", soon:"Coming soon", read:"Read &rarr;"}}
}};
let columnFilter = '';
function esc(s){{ const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }}
function render(){{
  const t = STR[LANG];
  document.documentElement.lang = LANG==='zh' ? 'zh-CN' : 'en';
  document.getElementById('btn-zh').classList.toggle('on', LANG==='zh');
  document.getElementById('btn-en').classList.toggle('on', LANG==='en');
  document.querySelectorAll('[data-i18n]').forEach(el=>{{
    const k = el.getAttribute('data-i18n'); if(t[k]!==undefined) el.innerHTML = t[k];
  }});
  const columns = [{{k:'', n:t.all}}, {{k:'build', n: LANG==='zh'?'建造复盘':'Build Notes'}}, {{k:'garden', n: LANG==='zh'?'知识花园':'Garden'}}, {{k:'log', n: LANG==='zh'?'实验日志':'Lab Log'}}];
  document.getElementById('filters').innerHTML = columns.map(c=>
    '<button class="f-chip'+(columnFilter===c.k?' on':'')+'" data-col="'+c.k+'">'+esc(c.n)+'</button>').join('');
  document.querySelectorAll('.f-chip').forEach(b=> b.onclick = ()=>{{ columnFilter = b.dataset.col; render(); }});
  const host = document.getElementById('col-list');
  host.innerHTML = '';
  COLS.forEach(c=>{{
    let arts = ARTICLES.filter(a=>a.col===c.key && (!columnFilter || a.column===columnFilter));
    if(!arts.length) return;
    const block = document.createElement('div');
    block.className = 'col-block';
    block.id = 'col-' + c.key;
    block.innerHTML = '<div class="col-head"><h3>'+esc(c.name[LANG])+
      '<span class="cnt">'+arts.length+'P</span></h3><p>'+esc(c.desc[LANG])+'</p></div>';
    arts.forEach(a=>{{
      const row = document.createElement('div');
      row.className = 'art-row' + (a.live ? '' : ' locked');
      const CN = {{build:"建造复盘",garden:"知识花园",log:"实验日志"}};
      const ENL = {{build:"Build Notes",garden:"Garden",log:"Lab Log"}};
      row.innerHTML =
        '<span class="art-num">'+a.id+'</span>'+
        '<div class="art-main"><div class="art-title">'+esc(a.t[LANG])+'</div>'+
        '<div class="art-desc">'+esc(a.d[LANG])+'</div></div>'+
        '<div class="art-meta"><span class="col-tag">'+esc((LANG==='zh'?CN:ENL)[a.column]||a.column)+'</span>'+
        (a.live && a.url ? '<span class="art-arrow">&rarr;</span>' : '<span class="soon">'+esc(t.soon)+'</span>')+'</div>';
      if(a.live && a.url) row.onclick = ()=>{{ location.href = a.url; }};
      block.appendChild(row);
    }});
    host.appendChild(block);
  }});
  const h = location.hash;
  if(h && h.startsWith('#col-')){{
    const el = document.querySelector(h);
    if(el) setTimeout(()=>el.scrollIntoView({{block:'start'}}), 80);
  }}
}}
document.getElementById('btn-zh').onclick = ()=>{{ LANG='zh'; localStorage.setItem('rotor-lang','zh'); render(); }};
document.getElementById('btn-en').onclick = ()=>{{ LANG='en'; localStorage.setItem('rotor-lang','en'); render(); }};
render();
</script>
</body>
</html>
"""


def main():
    arts = []
    for aid, slug, col, column, tcn, ten, dcn, den in ARTS:
        live = aid in LIVE
        entry = {"id": aid, "slug": slug, "col": col, "column": column,
                 "t": {"zh": tcn, "en": ten}, "d": {"zh": dcn, "en": den},
                 "live": live}
        if live:
            entry["url"] = f"/writing/{aid}-{slug}"
            zh_p = f"{DRAFTS}/{aid}-{slug}.md"
            en_p = f"{DRAFTS}/{aid}-{slug}.en.md"
            assert os.path.exists(zh_p), f"missing {zh_p}"
            assert os.path.exists(en_p), f"missing {en_p}"
            entry["body"] = {"zh": md_to_html(zh_p), "en": md_to_html(en_p)}
        arts.append(entry)

    # 上一篇/下一篇：同合集内已发布的相邻文章
    live_by_col = {}
    for a in arts:
        if a["live"]:
            live_by_col.setdefault(a["col"], []).append(a)
    for col, lst in live_by_col.items():
        lst.sort(key=lambda x: x["id"])
        for i, a in enumerate(lst):
            if i > 0:
                p = lst[i-1]
                a["prev"] = {"url": p["url"], "t": p["t"]}
            if i < len(lst) - 1:
                nx = lst[i+1]
                a["next"] = {"url": nx["url"], "t": nx["t"]}

    # 1) articles.js（给首页用，含"即将发布"标记，不含正文；首页"最新"自行按 live 过滤）
    for a in arts:
        if a["live"]:
            a["date"] = DATES.get(a["id"], "")
    slim = [{k: v for k, v in a.items() if k != "body"} for a in arts]
    open("/tmp/articles.js", "w", encoding="utf-8").write(
        "const ARTICLES = " + json.dumps(slim, ensure_ascii=False) + ";")
    print("articles.js:", len(slim), "articles")

    # 2) 文章二级页面（已发布 + 已写稿未发布的都生成）
    css = site_css()
    for a in arts:
        if not a["live"]:
            continue
        col_zh, col_en = COLLECTIONS[a["col"]]
        column_zh, column_en = COLUMNS[a["column"]]
        payload = {"t": a["t"], "body": a["body"]}
        for k in ("prev", "next"):
            if k in a:
                payload[k] = a[k]
        page = PAGE_TMPL.format(
            title_zh=a["t"]["zh"], desc_zh=a["d"]["zh"],
            css=css, data_json=json.dumps(payload, ensure_ascii=False),
            col_zh=col_zh, col_en=col_en, column_zh=column_zh, column_en=column_en)
        assert "</script" not in a["body"]["zh"] and "</script" not in a["body"]["en"]
        fn = f"{OUTDIR}/{a['id']}-{a['slug']}.html"
        open(fn, "w", encoding="utf-8").write(page)
        print("page:", fn, len(page), "bytes")

    # 3) 列表页 /writing/
    cols_json = json.dumps([
        {"key": k, "name": {"zh": v[0], "en": v[1]},
         "desc": {"zh": d[0], "en": d[1]}}
        for k, v, d in [
            ("infra", COLLECTIONS["infra"], ("网关 · 观测 · 计费 · 发布", "Gateway · observability · billing · releases")),
            ("agent", COLLECTIONS["agent"], ("记忆 · 人格 · 执行边界", "Memory · persona · execution boundaries")),
            ("biz", COLLECTIONS["biz"], ("资讯 · H5 · 组织代码", "Newsletters · H5 · code organization")),
            ("eng", COLLECTIONS["eng"], ("验证 · 规范 · 决策记录", "Verification · conventions · ADRs")),
            ("solo", COLLECTIONS["solo"], ("独立项目的复盘", "Indie project retrospectives")),
        ]], ensure_ascii=False)
    list_page = LIST_TMPL.format(
        desc_zh="rotor 的写作存档：建造复盘、知识花园、实验日志。",
        css=css, sub_zh="从知识库里长出来的文章：只写有来源的东西，不编故事。",
        sub_en="Articles grown from the knowledge base: sourced claims only, no fiction.",
        articles_json=json.dumps(slim, ensure_ascii=False),
        cols_json=cols_json)
    open(f"{OUTDIR}/index.html", "w", encoding="utf-8").write(list_page)
    print("list page:", f"{OUTDIR}/index.html", len(list_page), "bytes")

if __name__ == "__main__":
    main()
