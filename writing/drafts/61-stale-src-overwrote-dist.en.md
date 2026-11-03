# What Runs in Production Is the Build Artifact, Not the Source: A Silent Rollback of 26 Commits

> Column: Lab Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/identity-platform stale source overwrote build output, routes missing (desensitized) ｜ Status: Drafted · Coming soon

Conclusion first: in one production release, the service started cleanly with no errors at all, yet registered routes fell from 282 to 275, and 7 recently shipped endpoints vanished. The code was not wrong. The build input was: the source used for the build lagged the production artifact by 26 commits, so rebuilding from stale source silently rolled production back to a version more than a month old. What runs in production was never the source. It is the build artifact, and rebuilding from the wrong source is a rollback with no error message.

## Symptom: Started Fine, 7 Routes Short

One afternoon, a release went out for a login-related change: the build succeeded, the restart left clean logs, and there were no errors. Then a route-count check showed something wrong: 282 routes before the restart, 275 after. The 7 missing routes included recently shipped authorization endpoints and a token-refresh endpoint, all capabilities real traffic actually uses.

A clean start here is not good news; it is cover. Missing routes do not crash the process, write no error logs, and trigger no startup self-check alarm. They only come back as 404s when real requests hit those endpoints. If release verification only asks "is the service up," a rollback like this can sit in production unnoticed for a long time. The post-incident impact window was about 24 minutes, and whether any real request hit a missing route during it can no longer be verified, because access logging was off by default.

## Root Cause: The Source on the Server Was Not the Production Code

This service runs a compiled build artifact; the source directory is only a build input. The problem hides in that word "only": a leftover source directory on the server lagged the production artifact by 26 commits. Someone edited that copy directly and rebuilt from it, overwriting the production artifact. The build fully succeeded and the artifact was fully valid; it just corresponded to code 26 commits behind.

The result is a textbook misalignment: build, deploy, and restart each succeeded, and together they produced a rollback. One later check makes the version gap obvious: a build file for an auth module was about 37KB in production and contained the refresh-token keyword, while the stale-source build came out at about 25KB with a keyword count of zero. Laid side by side, the two artifacts show the gap at a glance, but the build pipeline itself never makes that comparison.

More alarming is the act itself: "just edit the source on the server." It looks like the fastest path: edit, rebuild, restart, live in minutes. But it bypasses version control, the only guardrail. Once the server copy drifts from the repository mainline, every later "shortcut" overwrites a known-version artifact with unknown-version code. This time it was 26 commits behind; next time it could carry an uncommitted debugging change, and a successful build plus a clean start will wave it all through.

## Response: Rebuild From the Repository, Replace the Whole Directory

After the missing routes were found, the response came in three steps.

1. **Back up the downgraded artifact first**: package the overwritten build artifact in full before touching anything. The backup preserves a rollback path: if the new build has problems too, at least the state "7 routes short but running" is recoverable.
2. **Rebuild from the repository mainline**: export source from the latest repository commit and recompile, without touching the stale server copy. Build input must come from version control, not from a leftover directory on some machine.
3. **Replace the whole directory, restart, verify**: replace the build artifact as a whole directory, then verify item by item after restart: route count back to 282, missing endpoints back in the registry, startup logs clean. The verification anchor is the route count, a hard metric, not the soft feeling that "the service is up."

The response itself was not complicated: no new technology was introduced, no business bug was fixed, only the build input was swapped back to the correct version. The cost of the incident was not in the fix but in the detection: between the release and the discovery of the missing routes, production sat in a state that looked normal and was functionally short.

## Prevention: Three Rules

This review produced three rules:

1. **Releases only accept repository-exported artifacts**: build input is always exported from a specified commit in version control; rebuilding from leftover server source is prohibited. The wording must be absolute: not "prefer the repository," but "only the repository." Leave an "edit the server directly in an emergency" opening, and it will be used in an emergency.
2. **Judge the production version by artifact fingerprints, not by source**: to confirm which version is running, look at build-artifact characteristics: file size, new-feature keywords, registered route count. A source directory existing on the server does not mean it is the source of the production code; inferring the production version from how "new" the source looks was the direct cause of this incident.
3. **Delete leftover source, or make it unbuildable**: if that lagging source directory stays on the server, someone will treat it as source again. If it cannot be deleted, at least make it unusable for building directly: rename it, move it away, or mark it a read-only placeholder. Any of these beats leaving it as-is and relying on people remembering not to use it.

## One-Line Close

A successful build only proves an artifact was produced, not that it was built from the latest code: releases must trust the repository, not leftover directories, and production must be verified by artifact fingerprints, not by how new the source looks. Otherwise one casual rebuild can quietly push production back into the past.
