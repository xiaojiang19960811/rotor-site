# TinyKit: Anatomy of a Decision Chain

> Column: Build Notes ｜ Collection: Solo Building ｜ Source: TinyKit decision log (~/workspace/goals/tinykit-traffic-monetization/, memory/2026-10-01.md) ｜ Status: first draft

TinyKit is an English micro-tool site built for ad revenue. It wasn't planned in one sitting — it's a decision chain: first prove the pain is real, then build tools; when tool logic gets reused, abstract it into an API; when API logic can be called by AI directly, wrap it as MCP. Each step is the natural extension of the previous one.

## Step one: find the pain before building tools

On 2026-10-01, pain research ran on two tracks: comment sections of 16 high-engagement Xiaohongshu notes, and public sources like V2EX, Zhihu, and Reddit. Of 10 candidate pains, the strongest signals were "AI-flavored writing" (a complete paid segment already exists — users pay to lower AI-detection rates) and "cross-AI context handoff" (fresh, high resonance, zero cost to build).

The decision: ship the de-AI-flavor tool first. Two constraints applied: quality rewriting needs an LLM and pure-frontend rule rewriting has an obvious ceiling, so ship the rules version first with honest labeling, and decide on BYOK (bring-your-own-key) real rewriting only after traffic signals; and one of the main scenarios is "passing plagiarism checks on papers" — an academic-integrity gray zone — so the positioning had to avoid the "paper paraphrasing" framing entirely and serve only self-media copy de-flavoring against platform throttling.

Don't chase hype; chase evidence that someone already pays. Don't touch gray zones, even when they're the strongest demand.

## Step two: the tool site, 27 → 31

The research directly produced 4 new tools: token estimation, structured prompt building, chat-to-markdown, and de-AI-flavor rewriting, taking the total from 27 to 31. A full i18n infrastructure went in at the same time: language switcher, browser-language auto-detect, remembered preference.

The tradeoff here: every new tool serves AI-assistant users, no sprawl. A tool site's deadliest sin is "a little of everything" — each of the 31 tools can name the pain it maps to. If it can't, it doesn't get built.

## Step three: reused tool logic becomes an API

Once tool frontend logic got reused enough times, abstracting it into an API was the natural next step: 24 endpoints, 1,000 requests/day/IP rate limit, an API-key slot reserved for a future paid tier. Deployment took a shortcut: the API runs inside the Pages `_worker.js`, `/api/*` goes to functions, everything else to static assets — one deploy ships both site and API.

Pricing was set before validation: free tier first, paywall only after real usage. Pricing without usage is fantasy.

## Step four: API logic wrapped as MCP

The MCP server rewrote nothing: Node + MCP SDK, stdio transport, directly importing the API's pure functions — 23 tools exposed in one move. When the API later grew to 24 endpoints, MCP followed to 24 tools, smoke tests all green.

It was never published to any registry — publishing needs the user's account authorization, so that line stops at "code ready." Everything doable got done; the rest isn't forced.

## Monetization: two reversals on domain and AdSense

AdSense doesn't accept subdomains, so the `tinykit.rotor1996.top` application path was dead. Decision: register the apex domain `gettinykit.top`, keep the old one as backup. The AdSense application is submitted and pending; no ads display before approval — showing ad slots before approval is gambling with the account.

## In short

This decision chain has one method: each step only solves a problem the previous step already proved. Research proved demand, tools proved the shape, the API proved reuse, MCP proved composability. An unproven next step doesn't get built early.
