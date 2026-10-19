# "Update Available" On, 404 on Download

> Column: Engineering Log ｜ Collection: Engineering Infrastructure ｜ Source: wiki/bugs/2026-10-19 Desktop client update feed undeployed + false green light (desensitized) ｜ Status: Drafted · Coming soon

A release is not done when the deploy script exits cleanly. It is done when a real user can actually fetch the new bits from the public internet. This update-feed outage was masked by three layers: each layer looked "fine" on its own, and together they made the update feature completely dead.

## The symptom: no new version in Settings, ever

A desktop client release went out. Users reported that "Check for updates" in Settings always showed no new version, or just "temporarily unavailable". During troubleshooting the UI briefly showed "a new version is available" — but clicking download only opened the product homepage. No installer could be downloaded.

Every external client was affected: the update prompt was decorative, and the UI exposed no failure reason. Ops and users alike were likely to misread it as "a network issue" and move on.

## Layer one: the production feed directory didn't exist

Investigation found that the production update path pointed at a static directory that had never been deployed. With no matching proxy rule, every request under the update path fell through to the embedded front-end's single-page-app fallback: the version manifest, the installer, even a mistyped path — all returned HTTP 200 with an HTML body.

This is the most insidious kind of failure: **status 200, zero errors**. The client plugin parsed the "manifest", failed to parse HTML as JSON, and silently degraded per design: the UI showed "already up to date" or "temporarily unavailable". The update feature had never been live a single day, while every monitor believed all was well.

## Layer two: a dev mock stood in for the production address

The most confusing moment of troubleshooting: the UI briefly showed "a new version available". It turned out the local development config overrode the update feed URL with a mock service used for integration testing. The mock reported "new version available", but its download URL pointed at a directory instead of a file, and its checksum was all zeros.

The false-green-light chain worked like this: the person debugging saw "new version" on their own machine, concluded the feed was fine, and the real production problem (layer one) stayed buried. Only when re-verified in the real environment did the problem surface. If a dev mock is indistinguishable from production, it is not a tool during troubleshooting — it is a decoy.

## Layer three: config backups inside the live directory

Fixing the production config hit a secondary trap: someone had left a reverse-proxy config backup inside the site-config directory. The server loads every file in that directory, so the backup's stale config conflicted with the live one, producing a pile of "conflicting server name" warnings — and which config actually took effect depended on filename sort order.

A deployment-discipline problem: **backup files must never live in a directory that gets auto-loaded**. The live directory holds only live config; backups go elsewhere. Otherwise you can never say which config is actually running.

## Fix and verification: verify only from the public internet

After fixing all three layers, verification was not done on a local machine. Instead a standing rule: after every release, verify three things from the public internet, all of them, no exceptions.

1. **The manifest is JSON, not HTML**: request the version manifest and check the Content-Type is JSON. A 200 means nothing until you've read the response headers — not the UI copy.
2. **The installer has the right length**: send a HEAD request to confirm the installer exists and its length matches the release record; if resumable downloads are supported, verify a Range request returns 206.
3. **Missing paths return 404**: request a filename that doesn't exist; it must return 404. If it returns 200 with HTML, the SPA fallback swallowed the request again and the directory config never took effect.

Finally, download the full installer from the public internet and recompute the checksum against the manifest. A verification that only ran against a local mock proves nothing.

## The method: three kinds of false green light, each with a countermeasure

Three archetypes emerged from the postmortem:

1. **False success**: status 200, no UI errors — but the content is wrong (HTML served as JSON). Countermeasure: verify response headers and content type, not status codes or UI text.
2. **False environment**: the mock is indistinguishable from production, so troubleshooting sees the mock's "healthy". Countermeasure: mocks must look visibly different from production — use an impossible probe version, tag them as dev. When verifying the chain, first use a probe value to confirm which side you're actually reading.
3. **False config**: warnings ignored, backups mixed into the live directory — the running config isn't the one you think. Countermeasure: the live directory holds only live files; config-check warnings must be cleared to zero before reload.

All three share one trait: **none of them errors**. A troubleshooting process that only handles errors is blind to this class. The release checklist must have a column for "verified from outside", not just "deploy script returned 0".

## Takeaway

An "update available" light being on doesn't mean updates work. A false update prompt is worse than no prompt at all — because it spends the troubleshooter's trust.
