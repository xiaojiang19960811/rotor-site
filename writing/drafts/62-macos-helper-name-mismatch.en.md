# One Space Removed, the App Won't Launch: macOS Helper Names Must Match Exactly

> Column: Experiment Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/desktop client macOS app-name/helper-name mismatch crash (desensitized) ｜ Status: Drafted · Coming soon

Conclusion first: in one macOS desktop client release, removing a single space from a display name made the app completely unlaunchable: double-click, instant exit, no window, no message. The cause was not a broken signature or wrong permissions. The system looked up the helper program by the bundle name, and the helper on disk differed by one space. On macOS, the app name and the helper name must match character for character; one character off means "helper not found," and the build pipeline never exposes this error.

## Symptom: Signature Fine, Dead in 20 Milliseconds

After installing that day's macOS release, double-clicking quit immediately, with no interface and no prompt. Crash reports on the packaging machine grew by one per launch attempt from the release onward, showing a breakpoint trap, with a process lifetime of about 20 milliseconds. Running the executable inside the app bundle directly produced one fatal error: unable to find the helper app.

This symptom misleads easily: code signing passed, permissions looked right, and system security checks did not block anything, yet the app never showed a window. Troubleshooting from signing, permissions, or security policy would all come up empty, because those parts genuinely were fine. The failure sits one layer deeper: at startup the main program must first locate its helper program, and if it cannot, it exits fatally with no chance of recovery.

## Root Cause: Two Names from Two Sources

Inside a macOS app bundle, the names of the main program and its helpers are not arbitrary. The system locates the helper bundle using the app name from the bundle information, while the helper bundle's name comes from the product name in the packaging configuration. In this incident, one commit removed the space from the display name: the bundle information carried the spaceless version, while the helper bundle still used the old product name, space included.

So the system looked for the "spaceless helper" while the disk held the "spaced helper." One space of difference, lookup failed, and the main program exited fatally inside its startup function. Each name was legal and each had a source; the fault was that they came from two different fields. They had agreed only by coincidence, and the moment one change touched just one of them, they diverged.

That is the typical structure of this kind of incident: not a wrong value, but one concept with two sources of truth. As long as two sources exist, a change that touches only one of them is possible; and in renames, rebrands, and localization work, touching only one place is almost certain to happen eventually. Merging the two sources into one is the real fix; reminding people to "remember to change both places next time" bets correctness on human memory.

## Why the Build Didn't Catch It: The Smoke Test Never Took the Real Launch Path

More worth reviewing is the missed detection. The pre-release smoke checks were all green, yet they failed to stop a package that could not open after installation. The smoke test ran the executable inside the bundle as an ordinary runtime, following a script-execution path that never entered the graphical launch flow. Helper lookup only happens on the real graphical launch path, which the smoke test never executed, so its green result had nothing to do with the actual question of whether the app could start.

The Windows side already had a real-launch check at the time; the macOS side had no equivalent, and that was the gap. What matters in a check's coverage is not how many items ran, but whether they passed through the critical path. A check that bypasses the way the tested object actually works is invalid evidence no matter how many times it passes. In hindsight, this smoke test verified "can the executable run a script," not "can the app launch" — similar names, completely different verification targets.

## Fix: Single-Source Naming, Existence Assertions, Real-Launch Acceptance

The fix came in three steps, each addressing one layer of defense.

1. **Restore the verified combination first**: revert the display name and executable name to the combination already verified in the previous release, and pull the faulty release. This stops the bleeding without fixing the structure, but it restores availability first.
2. **Derive the helper name from the same source as the bundle name**: change the packaging configuration to take the display name directly as the product name, so the helper name and the bundle name come from the same field. From then on, a rename touches one place and both stay consistent; the structural possibility of divergence is gone.
3. **Assert helper bundles exist at build time**: add existence assertions for the four helper bundles (main, GPU, plugin, renderer) to the packaging verification, so a name mismatch fails the build outright. This moves discovery from "at launch" to "at build time," reducing the cost of failure from a production incident to a failed build.

The fixed release was accepted on the packaging machine with a genuine system launch: the main process and all helper processes came up, and the crash report count stopped growing. The acceptance bar changed from "the smoke script passed" to "the app actually launched," which is evidence on the same path as the user experience.

## Epilogue: Renaming the Bundle Left One More Bill

There was one more twist afterward: although the fixed release launched, the system still showed the old executable name in some places, and refreshing system services and restarting the Dock did not change it, so the bundle name itself had to change as well. After that change, the display name and helper name still came from the same source and stayed consistent, so the helper lookup no longer failed, and the new release passed verification and shipped.

But renaming the bundle left an outstanding bill: after upgrade, the old bundle remained in the Applications folder, and the release notes had to ask users to remove it manually; the auto-update path under the new bundle name still needs one genuine upgrade acceptance to confirm. This shows that a "rename" is never just a string change: once the bundle name changes, the upgrade path, leftover cleanup, and auto-update all change with it, and each needs real verification rather than an assumption that it is "just a rename."

## One-Line Close

One name with two sources will diverge sooner or later: derive the helper name and the bundle name from the same source, assert helper bundles exist at build time, and accept releases on a real launch path — otherwise a single space can leave a properly signed, properly permissioned app unable to show even a window.
