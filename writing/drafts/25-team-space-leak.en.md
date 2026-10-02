# When Team Spaces Leaked Projects

> Column: Lab Log ｜ Collection: Engineering ｜ Source: wiki/bugs/2026-09-01-va-studio团队短剧项目归属泄露 ｜ Status: first draft

A video workbench once had an authorization flaw: switching to the team space showed personal projects and other platforms' data in the project list; a short-drama project created by a team admin had no team ownership, and after generation the page said "personal projects can't be accessed in team space." Something you created yourself, which you couldn't open — ownership was lost at the moment of creation.

## Two root causes, both in "visible by default"

First, the project and series list endpoints treated an organization admin as entitled to see everything. Admins should see more — but "more" isn't "all." Cross-organization resources had no business in that list.

Second, legacy personal data with empty organization IDs kept an owner fallback for compatibility. Old rows had no org ID, so the code fell back to the owner relationship — and the fallback carried personal projects into the team view. Good intentions toward legacy data became the privilege-escalation entry point.

A third gap sat on the write side: when the drama agent created a project, it never wrote the organization ID from the current request's owner context. Read-side overexposure plus write-side lost ownership squeezed the team space from both ends.

## The fix: exact match, no fallback

Read side: team requests return only projects and series whose organization ID exactly matches the current org; empty-org resources stay in personal space, no fallback. The platform admin's cross-org ability is preserved on a separately verified path.

Write side: agent drafts, final persistence, and auto-created series all inherit the current request's team organization ID; async tasks carry ownership forward via task snapshots. Ownership is written at creation, never patched after.

Permission side: in-project creation capability is intersected with project edit permission — owners and editors can add content, team viewers and reviewers still can't write. The permission drawer restored the implicit project owner, labeled "original owner," so owners no longer vanish from the UI for not being explicitly registered in the member table.

Verification: 13 targeted org-isolation tests passed; 16 additional capability tests and 10 frontend permission/layout tests passed; after a backend restart, a real-browser check confirmed the team admin's add button enabled correctly. The recurrence-proof acceptance criteria are written down too: when a team admin opens the drama page, no empty-org or foreign-org resources may appear in the list; creating a project from one sentence must land back in team space, never bounce on a personal-project gate error.

## Follow-up: 403 returned, page still "loading"

Fixing the main issue surfaced a related bug: when an ordinary member opened another org's project URL directly, the server returned 403, but the project subpage only waited on the `project` object — stuck on "loading storyboard…" forever, with concurrent subpage requests re-triggering 403s.

The fix: the fetch function preserves the status code on non-2xx errors; the layout layer clears project state and navigates back to the org project list on 403/404, and shows "project temporarily unavailable" for other errors. A permission denial needs an explicit UI endpoint, not an infinite spinner.

## Two classic multi-tenant traps

This postmortem left two rules:

1. "Admins see everything" must be translated to "admins see everything in their org" — three words' difference, one privilege escalation.
2. Legacy data with empty org IDs should default to "personal space," not "fall back to visible wherever the owner goes." Every extra fallback layer is another hole in isolation.

## In short

The multi-tenant isolation checklist is short: filter lists by exact org, write ownership at creation time, and give denied access an explicit endpoint. It's short because each line cost at least one real escalation.
