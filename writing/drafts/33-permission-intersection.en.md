# Multi-Space Permissions: Intersection, Not Union

> Column: Knowledge Garden ｜ Collection: Engineering Tools ｜ Source: wiki/concepts/多空间组织上下文与权限交集 ｜ Status: Draft

**The conclusion first:** in a multi-space application, permissions cannot be decided by "who the user is" alone — you must first determine "which space this request belongs to." The check order is fixed in six steps: resolve the space, pin the ownership, compute organization actions, intersect with project roles, snapshot ownership at submit time, and let the server make the final call. Button states in the UI are only UX hints; the real security boundary is server-side gates, ownership snapshots of resources, and cross-space data isolation.

## Step 1: Resolve Which Space the Request Belongs To

The first step of permission computation is not looking up the user's identity — it is resolving the request's scope: does this request belong to the personal space or a team space?

1. The request must declare its space explicitly; legacy values are mapped only by compatibility rules, and illegal values are rejected outright.
2. When the declaration is missing, a fallback may be chosen only by an explicit default rule — never by guessing.
3. Scope, organization, project, and series are four different layers of objects; they cannot be replaced by a single organization ID or a single global role.

Collapsing the four layers into one is the most common starting point of multi-space privilege leaks.

## Step 2: Once Ownership Is Pinned, the Request Body Cannot Rewrite It

1. The personal space has an empty organization ID; a team space is bound to an organization.
2. An organization ID inside the request body must never override the scope that was already resolved.
3. A user who has joined no team can still use the personal space; a platform administrator cannot automatically read team resources by virtue of platform identity.

Ownership is a resolved fact, not a claim made by the client.

## Step 3: Capability Is an Intersection — It Only Shrinks, Never Grows

1. Admins, creators, reviewers, and viewers each get only an explicitly defined set of module actions — not one action more.
2. The owner, editor, reviewer, and viewer roles of a project or series are then intersected with the organization actions: being able to generate at the organization level does not mean being able to edit in the current project.
3. Read-only members may view permitted data, but they cannot bypass the write gate through direct URLs, keyboard shortcuts, GET side effects, cache keys, or async tasks.

The intersection is the design's intent: the organization role answers "what actions are allowed," the project role answers "in which project," and the overlap of the two is the person's real capability for this one request. Acceptance testing must use dual-organization test data: the same person can hold completely different action sets in two organizations, and testing only one is the same as testing none.

## Step 4: Async Tasks Snapshot Ownership at Submit Time, Not at Space Switches

Tasks, generation records, and push deliveries keep a snapshot of the space and organization taken at the moment of submission. If the user switches spaces afterward, already-submitted tasks keep their original ownership, and tasks must never be queried across spaces.

An async task without a snapshot hands the ownership decision to "the moment of the query" — and the space context at that moment may be wrong.

## Step 5: The Real Boundary Lives on the Server, Not in the UI

1. Hiding an entry or graying out a button in the UI is only a hint. Direct API calls, media, tasks, downloads, and exports must pass the same server-side gate.
2. The exact 403 vs. 404 policy for missing resources follows the API contract, but responses, file bytes, and caches must never leak another space's resources.
3. Browser refresh, back/forward navigation, two accounts in one origin session, and old links must all be part of acceptance. Testing only "whether the button is gray" is the same as not testing.

Acceptance follows a fixed order: prepare dual-organization test data first, then verify APIs, pages, caches, downloads, and exports one by one, and finally cover browser refresh and dual-account scenarios. The order matters: if the API gate fails, beautifully tested page buttons mean nothing.

## A Real Lesson

A video-workbench project once had a privilege leak: legacy data had an empty organization ID, and after a compatibility-rule fallback, a team space could see another team's projects. The root cause was exactly the mixing of ownership and resolution into one layer — the old data had no space snapshot, and the compatibility mapping gave it a legitimate identity. The fix follows the same check order above: resolve, pin ownership, intersect, and let the server decide — not a single step can be skipped.

## Closing

Multi-space permissions in three sentences: look at where the request is first, then at who the person is, and finally take the intersection. UI states are made for people to see; server-side gates are made for the people who try to go around them.
