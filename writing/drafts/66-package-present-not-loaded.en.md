# "Package Present" Is Not "Loaded": A Plugin That Silently Vanished After an Upgrade

> Column: Lab Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/preinstalled-sub-plugin-upgrade-missing-mount (desensitized) ｜ Status: Drafted · Upcoming

The conclusion first: after a routine upgrade of a desktop client, the session-summary feature silently disappeared. The package was in the install directory, it was absent from the plugin page, and it was never loaded at runtime. The root cause was not the package but the declaration: the upgrade synced the new package yet kept the old loading declarations, and this sub-component's loading depends on exactly those declarations. The qualification check only verified "is the package there", never "is it running", so a fully green acceptance on the old version proved nothing about this kind of upgrade. Present, loaded, and visible are three different things, and each needs its own check.

## The Package Was There; the Declaration Was Not

After the upgrade, the session-summary package was clearly in the install directory, and the dependency pointed at it, yet the count of loading declarations was zero. The way this sub-component loads decided the outcome: it exists as a sub-component that is not bundled into the main package, and its loading depends on an insert declaration for the target group in the new seed. The upgrade flow copied the package from the new seed and completed the dependency list, but it never created that declaration. Copying packages and completing lists do not grow declarations on their own.

This is the quietest kind of upgrade failure: no error, no crash, no log alert. The feature was simply gone. A silent absence costs more than an error: an error gets fixed the same day, while an absence waits until someone notices it.

## Passing Acceptance Proved Nothing About This Upgrade

The second layer is more worth a postmortem: why didn't acceptance stop it? The original qualification check mainly verified that the package existed; it never required the host runtime state of the newly added entry. Package present, check green, upgrade shipped.

The fixture made things worse. The original upgrade fixture copied the new seed and then simulated the old package, but the seed still contained the new declaration: the fixture carried the very result the migration was supposed to produce. Running old-version fresh installs and upgrades against such a fixture was bound to pass, and passing proved nothing about whether a real old configuration would gain its declaration after upgrading. The value of a test is not that it "passed" but whether it can fail: a test that can never go red is the same as no test.

That also set the direction of the fix: upgrade migration determines ownership from seed dependencies and explicit inserts, completes the missing root-level and group declarations and default configuration, and then preserves the priority of existing overrides; declarations that already exist are not inserted twice, and anchors with identity conflicts or that cannot be migrated safely stop the process instead of being forced through. Packaging checks verify module, enabled, and active state against the public patch identifier; upload checks require a "seed-inserted entries active" receipt for both first launch and upgrade. The rule covers the project's own components explicitly inserted by the distribution seed and does not rely on hard-coding one package name: otherwise the same pit gets stepped in again under a different package name next time.

## Loaded Is Not the Same as Visible in the List

A second phenomenon surfaced after the fix, worth its own note: the session summary could run after being inserted through the distribution configuration and integration group, yet it still did not show up on the plugin management page. This is not the same problem; it is another layer: runtime and list membership must be verified separately.

The plugin page reads the main bundle's own patch file; an insert declaration that lives only in the profile is never listed as a sub-component of the main plugin. The fix is to put the declaration in the management package and keep only configuration items in the profile, reusing the existing sub-component list without changing the core. An isolation test verified that inserting a declaration under the same identifier still produces only one running instance, with the old address and idle configuration preserved.

The lesson here is counterintuitive: a feature that runs is not a feature the user can find. Installed but invisible is no different from not installed. Runtime state, list membership, and user visibility are three separate acceptance lines.

## The Boundary of Acceptance: A Dry Run Is Not Acceptance

One more boundary from this round belongs in the ledger. The old local configuration only went through an in-memory dry run: the declaration went from 0 to 1, old configuration values were kept, repeated runs were idempotent, and the actual configuration was never written. A dry run only proves the migration logic is right; it does not prove the configuration on the user's machine is already right. The configuration and features after the user's real update still need the user's own acceptance. Passing an isolated qualification check cannot stand in for acceptance of personal data.

This is the old conclusion from article 9 in a new setting: "done" is not "verified". Migration regression, full client tests, packaging and release-guard tests, and documentation-sync checks all passing only prove the fix itself was not written badly; the real upgrade on the user's machine remains a separate verification.

## Practice: Verify Three Separate Things When Accepting an Upgrade

1. **Check the package, the declaration, and the runtime state separately**: the package being in the install directory is the first thing; the loading declaration existing is the second; the entry being active after the host starts is the third. Each has its own check, and none substitutes for another.
2. **Qualification checks must verify runtime state, not just package presence**: newly added entries need a host runtime-state requirement. A check that only verifies package presence cannot stop an upgrade where the package is there but never loads.
3. **A fixture must first prove it can fail**: an upgrade fixture must genuinely remove the new declaration, default values, and list items before running the migration. If the fixture still holds the result under verification, the test has lost its power of veto. Before writing a fixture, ask one question: has this test ever gone red?
4. **Verify runtime and list membership separately**: a feature that runs is not necessarily visible in the list. The management page reads a different source; a declaration in the wrong place leaves the feature invisible all the same.
5. **Record dry runs and user acceptance separately**: an in-memory dry run and isolation tests passing go in one column; the configuration and feature acceptance after the user's real upgrade go in another. The former cannot substitute for the latter.

## One Line to Close

After an upgrade, don't just ask "is the package there". Ask three questions: is the declaration there, is it running, can the user find it — only when all three have answers is the upgrade done.
