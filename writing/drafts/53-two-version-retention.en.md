# Keep Two Releases: Keep the Official List Separate from Candidates

> Column: Garden ｜ Collection: AI Infrastructure ｜ Source: wiki/decisions/client release retention, two versions per platform (desensitized) ｜ Status: drafted · coming soon

Conclusion first: for a desktop client, keep only two installer releases per product and per platform: the current official release and the previous official release. Candidate builds live somewhere else, for acceptance only: they do not enter the official download list, the auto-update channel, or the definition of the previous release. Once the retention rule gets fuzzy, old builds pile up, and the list, the fallback, and the update prompt will sooner or later disagree with each other.

## Two releases: which two

The current release is the one just officially released. The previous release is the one that was on that platform's official list before the release. There is exactly one basis for identifying the previous release: the pre-release official list.

It is not inferred from file timestamps, not from candidate numbers, and not from which build "looks more stable." Timestamps mislead: a candidate uploaded later is newer than the official release, yet was never officially released; an older official release is older than the candidate, yet is the only legitimate fallback. Treating timestamps, numbers, or subjective stability as the basis for the previous release leaves you with a fallback option that was never officially released.

Platforms do not copy each other's homework either. If a platform had no update in this round, its retention window does not move: another platform's new release does not replace this platform's previous release. The window is maintained independently per product and per platform, not as one site-wide cut.

## Candidates and official releases are two lists

A candidate build has exactly one job: acceptance. Before acceptance passes, it does not enter the official download list, the auto-update channel, or the determination of the previous release. Only after acceptance passes and the official list is switched does it become the current release; the former current release then slides into the previous slot.

This separation must be written into the process, not kept in someone's head. The old way was to leave candidate builds near the official directory and rely on people remembering "don't ship the wrong one"; with a different person, a deadline, or parallel changes, a candidate gets shipped as official. Two physically separate lists are more reliable than a verbal reminder: candidates have their own directory and direct links, and the official list changes only at the moment of the switch, with evidence kept for the list before and after.

The distinction has a second layer: a candidate passing its in-package startup checks is not the same as passing real installation acceptance. That the package starts and old profiles load is part of acceptance; a real overlay install still has to be walked through in a real environment. Writing the former as "accepted" promotes the candidate to official ahead of time.

## The platform version and the top-level version are two numbers

When several platforms share one list, a second confusion appears: the list's top-level version number versus each platform's real version number.

The correct approach: each platform has its own version field, and clients read it first; the top-level version is only a compatibility floor, the lowest value across platforms, meant to keep old clients from misjudging. When cleanup or the download page decides "which build to keep," it must read the platform version, not the top-level version.

The reason is straightforward: one platform upgrading alone should not make another platform's old clients repeatedly see update prompts. If the top-level version takes the highest value, old clients see "an update is available" and find no build for their platform; if it is taken as each platform's real version, cleanup may delete the wrong build. The two numbers have separate jobs: the platform version states the facts, the top-level version handles compatibility.

## A baseline cleanup is an exception, not routine

When this rule landed, a baseline cleanup was done once: each platform kept only its current official release, and history was cleared. At the next official release, the current-plus-previous window resumes; the baseline cleanup is not to be reapplied as a routine plan.

That sentence must be written down, or the baseline becomes a habit. A baseline cleanup presupposes explicit authorization, item-by-item inventory, and an auditable aftermath; treating it as routine means assuming "history can be discarded at any time." Yet history's value shows precisely when something goes wrong: fallback, traceability, and checking old behavior all depend on it. The routine window is two releases; the baseline is an authorized one-off exception. The two must not impersonate each other.

One more thing must be stated plainly: the previous release does not automatically equal a stable fallback release. It is only "the previous official release," not "a release verified over a long time"; nor does it imply that data formats can be downgraded. Rolling back means switching back to the old installer, not downgrading data and configuration along with it. Calling the previous release "the stable release" adds a guarantee to the rollback decision that does not exist.

## Before deleting: verify, then change the lists, then delete

The order of deletion must not be reversed. First verify the hash and download reachability of the resources to keep, then update the download list, the update list, and the history list, and only then delete according to an exact path-and-hash plan. While executing, also check that the list was not modified concurrently, and that files match the inventory.

Three red lines are non-negotiable:

1. **Do not delete user data**: user configuration, sessions, and databases are outside the scope of cleanup.
2. **Do not delete files of unknown ownership**: if ownership is unclear, leave the file and investigate first; do not clean up by guessing.
3. **Do not call a partial deletion complete**: if part was deleted and part remains, the report says partially complete, with the undeleted list and reasons; keep an audit of the retention run, and a gap in the audit is itself an unfinished item.

"Keep every old build just in case" sounds prudent, but it has three real costs: disk and maintenance cost, the risk of a stale build polluting the list and being shipped by mistake, and the decision cost of not knowing which build is really the previous one when a fallback is needed. The two-release window is not stinginess; it narrows "just in case" to a range that can be executed and checked: if a fallback is truly needed, the previous release is right there; if traceability is needed, the list and audit records are right there; the rest is not solved by hoarding.

## Closing

The retention rule for installers comes down to three sentences: per platform, keep only the current and the previous release; candidate builds never mix into the official list; verify before deleting, and leave an audit after deleting.
