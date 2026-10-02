# Monorepo, Organized for a Future Split

> Column: Build Notes ｜ Collection: Agents & Digital Humans ｜ Source: wiki/decisions/2026-09-13-bot-agent单仓模块化与未来拆仓边界 ｜ Status: first draft

Monorepo or multi-repo — both sides have their dogma: splitting into micro-repos looks architecturally advanced; staying monorepo looks pragmatic. Our digital-human Agent project took a third path: stay monorepo, but organize for a future split — draw the deployment units and shared packages clearly now, decide on repo count later. Whether to split is a future decision; being splittable is a present capability.

## How to divide: deployment units first, shared packages second

Directories are organized by two roles. `apps/` holds units that might deploy independently one day: the user client, the admin console, the API service, the background worker. `packages/` holds shared capabilities: contracts, application orchestration, domain, persistence, integrations, runtime.

This reorganization was a physical move, not new directories for show. Both frontend clients' sources were isolated, shared styles collected into an independent UI package, and the two clients no longer call each other through internal paths. Backend routes were split by resource into a dozen-plus module files — world, letters, tasks, creation, accounts, memory, admin each in its place, the registrar keeping only assembly and auth helpers. Domain retrieval logic was extracted from a legacy monolith file; tests were archived by unit/contract/E2E; scripts layered by migration, backup, evaluation, release, and maintenance. Old compatibility shims and mixed directories were deleted outright — no "clean up later" tails.

## Two hard boundaries

First, the contracts package is the source of truth. Hand-written schemas generate the OpenAPI spec and clients; cross-module events use versioned names; the asset manifest defines version, URI, hash, and content-type in contracts, and the main repo pins the asset repo's commit with a lock file. Contracts first, code second.

Second, dependency direction is locked. Domain code may not depend on the web framework, the frontend framework, queues, caches, or concrete SDKs; domains communicate through application-layer orchestration or typed events. Convention alone isn't enough — an architecture check script blocks application/domain packages from reverse-depending on server, database, and queue implementations. Boundaries are guarded by machines, not by self-discipline.

The database follows the same rule: PostgreSQL is the sole business database for the production API and worker; SQLite remains only in migration, backup, and isolated test tooling. The production boot path no longer loads the SQLite driver. One purpose, one database — no dual-track.

## Honest close: what isn't done is written down

The verification numbers: type checking, lint, 293 tests, build, OpenAPI generation, and the architecture check all pass; the containerized dev environment's four services came back healthy after rebuild. But E2E stands at 32 passed, 4 skipped, 4 failed — the failures cluster around existing mock and test-data wait issues, and we did not claim "this restructure fixed them."

What's unfinished is listed explicitly too: API routes aren't fully split by resource yet, migration SQL isn't physically split by domain yet, the independent asset repo isn't truly published yet. These stay as later phases, not smuggled into this round's conclusions. The most suspicious line in any restructure report is "all complete" — we chose to put the unfinished items in the body text.

## In short

"Organized for a future split" means: structure the monorepo through the lens of deployment units, lock dependency direction with contracts and check scripts, and replace the "restructure complete" declaration with an honest verification report. Whether to split can wait; being splittable must be proven now.
