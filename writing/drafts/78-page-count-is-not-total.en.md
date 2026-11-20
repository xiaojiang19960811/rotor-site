# 50 Shown, 106 Real: Page Count Is Not the Total

> Column: Experiment Log | Collection: Engineering Tools | Source: wiki/bugs/2026-09-07 Video Workbench Team Asset Count Pagination Mismatch (desensitized) | Status: Drafted · Coming Soon

The conclusion first: the total shown on a screen and the number of items already loaded are two different numbers. The left sidebar of the Video Workbench's team management page read "Team Asset Library: 50", while the asset page's server-side total was 106. The missing 56 items were not lost, and they were not blocked by permissions — they had simply never been loaded. The asset API returns 50 items per page by default, and the sidebar was counting the length of the locally loaded array, treating "one page's worth" as "all of it".

## The Symptom: One Library, Two Numbers

The left sidebar of the team management page showed 50 for the team asset library and 5 for roles. Open the embedded asset page, and the server-side total for assets was 106. Both numbers described the same team asset library, yet they differed by more than double.

There was a subtler point: the sidebar number also moved with the filters. Switch an asset type or a tag, the current page's item count changes, and the sidebar total changes with it. A total that should be stable had become a number drifting with every interaction. What the user saw was not the size of the asset library, but "however many items this page happened to hold".

This mistake survived so long because 50 looks like a plausible total: it is an integer, it throws no error, and nothing on the screen says "this is only the first page". Meanwhile, the role count of 5 next to it was correct — roles are not paginated, so the local array is the full set — and one correct number vouched for a wrong one. A wrong total is not the scary part; a wrong total that looks right is.

## The Root Cause: Local Array Length Is Not a Total

A paginated API returns one page at a time, and its response carries two pieces of information: this page's data, and the server-side total. The old implementation of the organization page only used the former, taking the loaded array's length as the total. With a default page size of 50, the total was capped at 50 forever.

The mistake was collapsing three different numbers into one:

1. **Total**: how many items exist in the library, from the server-side `total`.
2. **Loaded count**: how many have been fetched onto the current page, from the local array's length.
3. **Filtered count**: how many match the current filter, from the `total` returned with the filter applied.

The three are only equal when there is no pagination, no filtering, and everything is loaded at once — and a real interface satisfies none of those. Use one of them to stand in for another, and the numbers are guaranteed to disagree at some point. 50 versus 106 is only the gap that happened to be noticed this time; next time it could be 50 versus 500.

## The Fix: Totals Come Only from the Server-Side Total

The fix took three steps, built on a single rule: wherever a total is displayed, never read the local array's length.

First, the server-side `total` from each category API was normalized and passed back to the organization page: roles, scenes, props, assets, and finished videos each report their own server-side figure, and the sidebar uses those totals directly instead of counting the local array.

Second, when a filter is applied, an unfiltered asset `total` is read separately. The sidebar total stays stable, always the full library size; filtering only affects the "matching items" count inside the asset list, shown separately so the two never interfere.

Third, the organization page's duplicate statistics request was removed. The same batch of pagination APIs had been called twice — once for the list, once for the statistics. Once the definition was unified, the statistics reused the `total` that came back with the list response, with no separate request.

Verification passed 7 targeted tests, and the build passed. The acceptance criteria were specific: open the team management page and check the sidebar count against the asset page's server-side `total`; switch asset type or tag filters and confirm the sidebar still shows the unfiltered total; refresh the page and confirm it still matches.

## Three Rules for Every Interface That Shows a Total

The pitfall here was not pagination itself, but the fact that "total" had no defined meaning. Pagination is a way of fetching data; a total is a business fact, and the two should not share one variable. Wherever a total appears on a screen, apply three rules:

1. **Totals come from the server, not from local state**: the paginated response's `total` is the only trustworthy source for a total; local array length only says how much has been loaded and must never be used to display a total.
2. **Totals and filters stay separate**: filtering changes the "matching count", not the total. Each needs its own number and its own place on the screen; they must not share one display slot.
3. **Totals must be stable**: the same total should stay unchanged when filters switch, pages turn, or the page refreshes. A number that drifts with interaction is a signal that the definition is wrong — there is no need to wait for a user to report mismatched numbers.

## In Brief

The 56 missing assets were never lost; the interface was counting in the wrong place. A total is not counted — it is asked for: ask the server, not the local array.
