# Fresh Install Passes, Upgrade Explodes: The Upgrade Path Is a Second Test Line

> Column: Lab Log | Collection: Engineering | Source: wiki/projects/desktop client 0.2.2 core upgrade and dual-distribution release (desensitized) | Status: Drafted · Upcoming

The conclusion first: before one core-upgrade release, four problems all exploded on the upgrade path, and a fresh install caught none of them. A missing dependency declaration, an unsynced lockfile, a plugin placed in the wrong domain: fresh install all green, upgrading from the old version all red. After the four fixes, acceptance added one hard rule: the activation checklists of fresh install and upgrade must be compared item by item, and the difference must be zero. The lesson of this postmortem is one sentence: fresh install and upgrade are two test lines, and testing only the first means testing only half your users.

## Four Problems, All Upgrade-Only

In the same week, two distributions of the same codebase upgraded the core and repackaged, each fixing a batch of upgrade-only problems before release. The four problems in one distribution are the most representative:

1. **The bot plugin failed to import after upgrade**: the plugin had synced a new batch of autonomous execution capability that called the core's credential, compaction, and tool-execution modules, but never declared them in its own dependencies. On a fresh install, those modules happened to be pulled in through other paths and the import succeeded; on upgrade, the old environment resolved the dependency graph along a different path and the import failed outright.
2. **A compression dependency could not be found**: an ordinary dependency was never declared. The development environment masked the gap through a transitive dependency, but the offline installer had no copy of it, and the upgrade install failed with a package-not-found error.
3. **The lockfile was out of date**: after the missing dependency was added, nobody synced the lockfile, so an install with the frozen-lockfile flag failed with an out-of-date error. The same class of problem would break the continuous-integration environment too.
4. **One plugin's inventory dropped to zero after upgrade**: a plugin that renders model thinking was wrongly placed in the tooling domain, hanging under an integration anchor. The upgrade fixture removed the anchor first, the whole tooling domain stopped loading with it, and the plugin's inventory fell to zero. A fresh install never takes the "remove the anchor first" step, so the problem could not show itself.

Four problems, four different root causes: dependency declarations, lockfile sync, domain semantics. But they share one feature: they only appear on the path "upgrading from the old version." Four fixes later, the release could proceed.

## Why a Fresh Install Cannot Catch Them

A fresh install and an upgrade do not test the same thing.

A fresh install starts from a blank sheet: no old configuration, no old plugin versions, no legacy declarations. Dependencies are computed fresh from the current manifest, state is built fresh from the current structure. Every joint between old and new simply does not exist, so it cannot be tested.

An upgrade starts from an old state that really existed: old plugins still there, old configuration still there, the old dependency graph still there. The new version has far more to do than a fresh install: replace old plugin versions, migrate old configuration, regroup under new rules, handle retired declarations. Every joint is a failure point that does not exist in a fresh install. Missing dependency declarations, an expired lockfile, a misplaced domain: all of these are joint problems, not problems with the new features themselves.

So "fresh install all green" only proves the new version can run on its own. It does not prove existing users can get there. And in reality, the vast majority of users take the upgrade path, not a fresh install. Testing only the fresh install tests the minority path and uses it to vouch for the majority one.

## The Other Distribution: The Same Lesson, a Different Face

The other distribution confirmed the same lesson in the same upgrade round, with the problems wearing a different face.

It moved the same plugin back to the base domain on semantic grounds — the move itself was correct — but that change introduced four test regressions: some assertions still looked the plugin up in its old standalone form, one expectation table was missing two rows for the new home, and one count was off by one, because the upstream entry had never updated the expectation in the first place. The fix changed no structure to make tests pass; every expectation was updated to the new domain contract. The contract is the yardstick and the test is the ruler: when the ruler is wrong, calibrate the ruler, do not alter what is being measured.

The same round exposed two more failures from stale shared libraries: the library files lagged the source by several hours, and a targeted rebuild turned them green with zero changes. One extra lesson came along for free: rebuild before running tests. Running new tests against an old build artifact tests the build, not the code.

Two distributions, two sets of problems, one conclusion: failures on the upgrade path live in a different set from failures in the new features themselves.

## Acceptance: Both Lines Must Be Green, and the Checklists Must Match Exactly

After the four fixes, this distribution's acceptance ran as follows:

- Startup qualification split into two lines: 9 items for fresh install, 15 for upgrade, all passing.
- The activation checklists of fresh install and upgrade were compared item by item: 11 plugins all active, zero difference.
- A real old-version configuration was used as a seed, and the migration path was exercised to add the new plugins and activate them, verifying the upgrade path itself.
- The official packaging command returned success in both scenarios.

The second item is the key. Comparing checklists item by item until the difference is zero pins the post-upgrade state to the fresh-install state: an upgrade is not "roughly usable," it is "identical to a fresh install." Each of the four upgrade-only problems would show up in this comparison: a failed import costs one activation entry, a missing dependency costs one, a misplaced domain costs one. Zero difference is the passing bar for the upgrade path.

## Method: Three Rules for the Upgrade Path

1. **Test fresh install and upgrade separately**: each line gets its own qualification checklist, and the upgrade list is only longer, never shorter. Reporting only the fresh-install result does not count as passing acceptance.
2. **Compare post-upgrade state against fresh install, item by item**: activation checklists, configuration state, plugin counts — the difference must be zero. The comparison is the passing bar for the upgrade path, not extra credit.
3. **Fix the joint, do not route around it**: a missing dependency gets its declaration, an expired lockfile gets synced, a wrong home gets moved back on semantic grounds. Do not add a fallback switch to hide the problem: once the fallback is in, the problem is still there, waiting for the next upgrade to explode again.

## One Sentence to Close

A fresh install tests whether the new version can run on its own; an upgrade tests whether existing users can reach the new version: the two lines have their own sets of failures, and testing only the first leaves the road most users travel to luck; compare the post-upgrade state against a fresh install item by item, and only zero difference means the upgrade truly passed.
