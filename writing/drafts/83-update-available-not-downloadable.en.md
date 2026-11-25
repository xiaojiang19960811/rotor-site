# Update Available Is Not Downloadable

> Column: Experiment Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/2026-10-19 desktop client update feed not deployed and false green light (desensitized) ｜ Status: Drafted · Upcoming

Conclusion first: settings showing "a new version is available" does not mean the new version can actually be downloaded. In one update-prompt failure, three layers — each reasonable on its own — combined to hide the fault: the production environment never deployed the update manifest, the fallback logic returned the missing manifest as a web page; a local mock used for integration testing replaced the production address and propped up the "new version available" display with a fake version number; and a config backup placed in the wrong directory drowned the config check warnings. After the fix, the verification standard changed: no longer "what does the UI show", but three pieces of artifact evidence — whether the manifest is real JSON, whether the installer length matches, and whether a missing file really returns 404.

## Symptom: a new-version prompt with nothing to download

Users reported that settings never showed a new version. During investigation, the row briefly displayed "new version 0.2.2", but clicking "download new version" only opened the gateway homepage — no installer could be downloaded. Real users stayed stuck on "temporarily unable to connect" or "you are on the latest version": no new version in sight, and no error either.

The impact covered all external clients: the update prompt was effectively decorative, and the UI exposed no failure reason, so operations and users alike easily misread it as a network problem.

## Three root causes: each reasonable, together hiding the fault

1. **Production had no update manifest**: the manifest and installer paths all fell through to the single-page-app fallback embedded in the gateway frontend, which returned 200 and a web page for everything. The update-check module failed to parse the page as JSON and silently degraded to "unavailable", as designed. Staying quiet offline is right — but here it also treated "not deployed on the server" as "temporarily unreachable".
2. **A local mock replaced the production address**: the local integration-test config overrode the update address with a local mock service, which returned version 0.2.2, an all-zero checksum, and a download address pointing at a directory. The UI therefore displayed "new version", while the download was bound to fail. This was the false green light: it masked the first layer, and "settings clearly shows a new version" briefly became a point of dispute.
3. **A config backup was placed in the wrong location**: the site config backup file sat inside the config directory, so config loading read the backup in as well. The config check reported 8 conflicting-server-name warnings, and which config actually took effect depended on filename sort order.

No single layer was "wrong code": returning a web page is normal behavior for a single-page app, silent degradation is the update module's intended design, a mock is a standard integration-testing tool, and dropping a backup into the config directory is a casual operation. The fault was not in any one layer but in the three stacked together: each layer absorbed the failure of the one above it, leaving the UI with a single, seemingly normal "new version available".

## Fix: four changes, one new standard

1. Two precise routes on the server: the manifest matches exactly, returned as JSON with no caching; the installer directory matches by prefix, with long caching and resumable downloads preserved.
2. A manifest with real checksums was generated and deployed to the update-feed directory together with the installer.
3. The config backup was moved out of the config directory, and the config was reloaded only after the check came back warning-free.
4. The local update address was switched back to production, and the integration-test mock was stopped.

The first three close the deployment gap; the fourth removes the false green light. But what really changed is the verification standard: from now on, acceptance of the update channel is judged not by "the UI shows a new version", but by three pieces of artifact evidence.

## Verification and boundaries

Five checks were run from the public internet after the release:

1. The manifest request returns 200, JSON content type, and no caching, with the version number of the release in question.
2. A HEAD request on the installer returns 200, a length matching the manifest, and long caching; a ranged request returns 206.
3. A nonexistent filename returns 404: if it returned 200 plus a web page, the single-page fallback would have caught it again.
4. The full installer, about 290 MB, was downloaded from the public internet in about 24 seconds, and the recomputed checksum matched the manifest; the homepage still returned normally, and the backend was unaffected.
5. The local check returned "new version available", and after the mock was temporarily changed to a nonexistent probe version, it still returned the production version — proving the check no longer reads the mock.

Three relapse-prevention rules are worth recording: after a release, the manifest, the installer, and the 404 must be verified from the public internet — verifying only against a local mock is no verification at all; an integration-test mock must use a version number or marker clearly different from production, to avoid a "looks like the update worked" false green light; and config backups always go outside the config directory.

One boundary should be stated clearly: silent degradation is reasonable on its own — offline users should not be bothered with errors. But when troubleshooting, you need evidence that distinguishes "the network is down" from "the manifest is a web page": look at response headers first, not UI copy. UI copy is written for users, not for troubleshooting.

One-line close: the UI showing "a new version is available" is only the last link in the update chain speaking; the manifest, the installer, and the 404 are the proof that the update is actually usable.
