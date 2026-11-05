# Committed, Released, Verified: Three Different Things

> Column: Garden ｜ Collection: Engineering ｜ Source: wiki/projects/desktop client dual-search configuration and gateway tool-group release (desensitized) ｜ Status: Drafted · Coming soon

Conclusion first: a feature has three states: **committed**, **released**, and **verified**. Each state has its own evidence, and none can stand in for another. On November 4, 2026, a dual-search configuration change in a desktop client had its source committed and every test suite green in its own lane — but the client was never pushed, never packaged, and the installed build was never updated. To the user, this feature does not exist. A gateway tool-group combination released the same day was genuinely live, but its acceptance only covered the existing account's key, not all groups; real billing was never independently reconciled; the rollback script passed a syntax check but was never rehearsed. Writing the three states separately is the cheapest form of honesty.

## Dual-Search Configuration: Code in the Repo, Nothing on the User's Machine

This change made an account plugin sync two web-search configurations side by side: the old messaging interface and the new search/fetch interface, running in parallel. The source was committed to the internal client repository, but the client was not pushed, not packaged, and the installed build on the machine was not updated in this round. Production on the server side did not change because of this client change. From the code's point of view the feature was done; from the user's point of view it had not happened yet.

The hosting semantics of the change itself are worth a close look. Addresses and credentials are hosted as pairs: only credential references are written, never plaintext keys; takeover happens only when a field is unset, still at the official default, or still equal to the last hosted value; a user's own custom configuration is always preserved. Hosting is not takeover: takeover only happens on the premise that "this value was never hand-written by the user," so the user's choices are never quietly overwritten.

More important is a timing semantic: withdrawal is not real-time interception. After a user changes an address or a credential, a still-hosted field is only withdrawn at the next login or host-restore sync. Between the change and its effect lies one sync. Before writing this kind of feature, you must first write down your own sync timing; if you assume "a change takes effect immediately," the old credential keeps working with nobody knowing. Timing semantics are part of the feature definition, not an implementation detail.

The exit path follows the same discipline: only values still hosted by the plugin are withdrawn, and the applicable inherited default is restored; sync and exit for the two configuration lines each catch their own failures, continue with the other line, and report a combined result — never writing one line's success as overall success. Partial success is partial success; the moment it is written as overall success, the failing line disappears from everyone's view.

## The Green Slot Is Live, Which Does Not Mean All Groups Are Verified

The gateway tool-group combination released the same day was genuinely shipped: the new endpoints route fixedly to the same model platform; standard mode only schedules accounts inside the original group and borrows from no other group; a concurrency slot is taken before forwarding and released on both completion and early failure; quota belongs to the original group, and group and subscription settings are unchanged. Search and fetch were verified with the existing account's key before and after the switch, public health checks passed, and the old slot was then stopped.

But the release record states its acceptance gaps just as explicitly: only the current account's existing key was covered, not all user groups; real database billing amounts were never independently reconciled; no end-to-end browser flow was run; no new scheduling regression tests were added. The rollback script passed a syntax check but was never rehearsed switching back to the old version.

The release actions themselves — switching traffic, health checks, stopping the old slot — prove only one thing: the new version is running. They do not prove that all groups can use it, that the billing is right, or that you can roll back. Rollback capability and "a rollback script exists" are two different things: a rollback that has never been rehearsed differs from one that was never written only in psychological comfort, at the moment something breaks.

## Green in Every Lane Does Not Add Up to Green Overall

The test data for the dual-search configuration makes the same point. The first full-suite summary showed 624 passing and 1 failing; the failure was a pre-existing timeout item that passed on a standalone re-run. But no complete all-green summary was ever re-obtained afterward. The account package, messaging module, isolation checks, packaging, and release verification each passed in their own lane, and the final configuration suite passed 15 of 15. Every piece of evidence is real, but none of them is named "overall pass."

The record states it plainly: do not equate passing lanes with installed-build acceptance or real-user search acceptance. Lane evidence only proves lanes; an overall conclusion needs overall evidence. Installed-build acceptance and real-user search acceptance are two separate evidence chains that do not live inside the test report. Stacking five lane passes together does not produce an "overall pass": the fallacy of evidence assembly is that the act of assembling was itself never verified.

This echoes article 39, "A Green Lint Can't Erase Evidence Gaps," but from a different angle. Article 39 is about the limits of a check itself: structural checks can only prove internal consistency. This one is about how evidence combines: the lanes are genuinely green, but the conclusion "overall green" was never proven by any single run.

## Practice: Write Three States, Keep the Gaps Next to the Conclusion

1. **Write status in three parts**: source state, release state, and verification state, each on its own. The word "supported" is too vague — avoid it when you can. Saying "source committed, not released" costs only a few more words than saying "supported," and removes two whole segments of fact that do not exist.
2. **Write the acceptance gaps in the same place as the conclusion**: for a released feature, the gap list is part of the feature. Only the existing key verified, not all groups, no real billing reconciliation, no rehearsed rollback — write it out and let the reader judge how much to trust. Burying gaps in an appendix assumes the reader will never open the appendix.
3. **For sync features, write the timing before the feature**: withdrawal happens at the next sync, not in real time — timing semantics like this belong in the feature definition. Users will use the feature under their own default assumption about timing; if you do not write it down, "a change takes effect immediately" becomes the default assumption, and the old configuration quietly staying in effect becomes a "ghost."

## One-Line Close

Committed, released, and verified are three things: code landing in the repository is only the first segment; being packaged into the installer and running on the user's machine is the second; passing on a real path, and being able to roll back, is the third. Each segment has its own evidence — write down whichever segment is missing.
