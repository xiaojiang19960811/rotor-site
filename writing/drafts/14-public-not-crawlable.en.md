# Public ≠ Crawlable

> Column: Garden ｜ Collection: Multi-platform ｜ Source: wiki/concepts/公开资讯自动化合规准入 ｜ Status: first draft

A page you can open in a browser isn't a page your program may scrape. Conversely, a personal non-commercial self-built collector isn't automatically illegal either. Compliance for automated public-info collection comes down to specifics: what method, what fields, what frequency.

## Red/yellow/green access tiers

Our access model has three tiers:

1. **Green**: official RSS/APIs explicitly provided for the purpose, Web Search within product permissions, materials the user provides directly. Use freely.
2. **Yellow**: publicly accessible list or announcement pages, or RSSHub routes, with no login. Low-frequency metadata collection only when all three hold: `robots.txt` doesn't forbid the path, legal notices don't forbid the use, and the implementation uses no login state or private APIs.
3. **Red**: sources explicitly forbidding generic bots or the automation, and any route needing login, cookies, captchas, paywalls, signatures, rate-limit bypass, proxy rotation, or private APIs. Never connected directly by a self-built collector.

Output keeps only title, publisher, date, original link, and short summaries within the permitted scope — never full article text, images, or comments.

## Permanently banned items

These six are hard boundaries confirmed by the user — not "deferred to later" but acceptance-failure conditions for any future implementation:

1. Full-text scraping of media articles
2. Collection via login state, cookies, personal or shared accounts
3. Bypassing paywalls, captchas, rate limits, signature checks, or anti-automation measures
4. Undisclosed, unauthorized, or reverse-engineered private APIs
5. Browser impersonation, proxy rotation, or ban evasion
6. Personal data collection unrelated to the briefing

## Verified examples

The rules weren't imagined — they were verified site by site: the People's Bank of China's `robots.txt` sets `Disallow: /` for generic bots, and its legal notice restricts unlicensed downloading — direct automated scraping stays out. The securities regulator's legal notice asserts copyright and restricts unlicensed alteration, sale, or rental. The stock exchange allows compliant non-commercial browsing and downloading but restricts for-profit electronic scraping, storage, and redistribution.

Note a common misconception: a missing, empty, or unreachable `robots.txt` only means no machine-readable statement was found — never an automation license.

## Technical boundaries

Server-side fixed source whitelist; models and clients can't pass arbitrary URLs. Stop immediately on `401/403/429`, captchas, or anti-automation pages. Default: one source checked at most every 30–60 minutes, concurrency 1. Normal feeds cap at 2MiB/12s — cancel over-limit reads rather than truncating parses.

One easily missed rule: human discovery and automated collection must be modeled separately. Humans browsing only surface headlines; code reads only the locally compiled list and never visits the human's source pages — the human/machine responsibility boundary belongs in the code itself.

## Quality is an access condition too

Beyond compliance, quality gates have also rejected sources: one free news API showed only 35% relevance in its top 20 with ~50% cross-query duplication; another returned 145 candidates of which only one in six had official publish dates hitting the target. Official-domain restriction can't substitute for date verification, and reachability can't substitute for terms authorization.

## In short

Compliance for automated public-info collection is one sentence: take only what's allowed, only by allowed means — and drop sources you can't take compliantly. Explicitly banned items are out; unclear ones stay off by default until each site is documented and decided.
