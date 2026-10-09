# When the User Says "Data Is Gone": A Cache Scapegoat Postmortem

> Column: Log ｜ Collection: AI Infrastructure ｜ Source: 2026-10-06 work retrospective (static site deploy incident) ｜ Status: First draft

**The short version:** Two updates to a static site project, and the user reported "data is gone" both times. The first time it really was the cache: the JS changed, the version string didn't, and browsers served the old script with the new page. The second time I assumed it was the cache again — and I was wrong. It was a real code defect: the script called an icon helper around line 760, but the helper wasn't defined until around line 990. The runtime threw a ReferenceError mid-file and the rest of the script never executed. Three rules came out of it: bump the asset version on every change; when half the UI works and half doesn't, suspect a mid-script death; and syntax checks can never replace a runtime smoke test.

## Background: Two reports of "data is gone"

On October 6, 2026, a static website hosted on a CDN shipped two feature updates. After each one, the user reported "data is gone" with screenshots. Both times the symptom looked almost identical: the KPI numbers at the top were animating normally, but the tables were blank and the chat button, nav icons, and theme toggle never appeared.

Same symptom, different root causes. The first time it was my own cache discipline failing. The second time, the cache took the blame for something it didn't do.

## First incident: The cache really was guilty

The first update added a stack of features to `app.js`, but the `app.js?v=5.0` version query in the HTML stayed the same. The CDN and the browser cache each did exactly what they were told: new HTML, old script.

The new page's dynamic panels (customer table, opportunity management) called render functions that only existed in the new script. The old script didn't have them, so the panels rendered blank. What the user saw as "data is gone" was really two versions of the code mixed together in one browser.

The fix was procedural: before every deploy, grep every HTML file to confirm all `app.js?v=` and `styles.css?v=` references match the release and are monotonically increasing. And when a user reports something weird, the first step is a hard refresh (Cmd/Ctrl+Shift+R) to rule out the cache before touching any code.

## Second incident: The cache was a scapegoat

The second update added an icon system and a light/dark theme toggle. After deploy, the user reported "data is gone" again — plus "the theme toggle doesn't work either."

My first instinct was "cache again." That judgment was wrong.

The evidence was in the screenshots: the KPI numbers scrolled normally, so part of the script clearly ran. But the tables, chat button, nav icons, and theme toggle were all missing — so the script wasn't failing to load, it was **dying mid-execution**. A cached old version would render a consistently old page, not a half-alive one.

The real root cause: `app.js` is one big IIFE. The chat button at around line 760 calls `ic("message", 22)`, but `ic()` isn't assigned until around line 990. When the runtime reached the call, the function didn't exist yet — a ReferenceError, and every line of top-level IIFE code after that never ran. The KPI numbers survived only because their observer was registered near the top of the file, before the throw.

The detail worth remembering: `node --check` passed the script with flying colors. A syntax check can only find syntax errors — it can't catch a runtime ordering bug like "call before definition." Using it as a release gate is like checking a broken bone with a thermometer.

## Fix and verification

The fix came in three layers:

1. **Code**: moved the whole icon-helper definition block to the top of the IIFE, so every call happens after the definition.
2. **Discipline**: bumped the build number to v5.3 (no missed bump this time) and redeployed.
3. **Verification**: pulled the live `app.js?v=5.3` back from production and re-ran the smoke test to confirm no top-level throw; the user refreshed and confirmed "it's all back," meaning everything that had vanished was restored.

The fourth action filled the missing gate: a Node `vm` sandbox with a minimal DOM stub that executes the script's top-level code and catches runtime throws — now a permanent pre-deploy smoke test. Syntax check and smoke test both have to pass before every release.

## Three rules

1. **Bump the asset version on every change.** Shipping JS/CSS without bumping `?v=` is shipping half-new, half-old pages. Grep every reference before deploy and confirm they're consistent and increasing — one missed bump is one botched release.
2. **When the UI is half-alive, suspect a mid-script death first.** The cache produces a consistently old page; partial, half-missing UI smells like a script that threw and died on some line. Read the user's report literally: "data is gone" didn't mean data was deleted — it meant rendering never finished.
3. **Syntax checks don't replace runtime smoke tests.** `node --check` can't catch definition ordering, variable timing, or environment differences. Before release, run the script's top-level code for real in a minimal DOM stub and catch the throws — that's a gate aimed at actual failures.

## Closing

The cache was blamed twice: once it was the culprit, once it was the scapegoat. The real cost of a scapegoat isn't one misdiagnosis — it's that it makes you stop reading the code.
