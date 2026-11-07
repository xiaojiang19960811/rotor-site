# Before Backing Up, Confirm Which Database You're Backing Up

> Column: Experiment Log ｜ Collection: AI Infrastructure ｜ Source: wiki/projects/multi-model gateway v0.2.20 upstream upgrade and blue-green release (desensitized) ｜ Status: Drafted · Upcoming

Conclusion first: during one upstream major-version upgrade, the backup script used the container's default environment variable for the database name and produced only a 522 KB empty backup, with no business tables at all; the backup that actually mattered was the 136 MB one taken after explicitly naming the production database. Whether an upgrade can ship is not decided by a green build, but by an acceptance ledger: is the upgrade range clean, are local customizations intact, does the rollback touch the database, and did the backup really capture the production database.

## The First Backup Captured an Empty Database

On November 7, 2026, the multi-model gateway merged upstream v0.2.20: 60 non-merge commits, 389 files, with the only conflict in the version file. Before release, the database was backed up as usual, and the backup script took the default database name from the container. It finished at 522 KB, with every business table empty.

The problem was not the backup command, but the database name. The container's default database is not the production database: production is 2.1 GB, and a single log table holds 548,000 rows. Backing up again with the production database named explicitly produced 136 MB, and it verified cleanly. The 522 KB mistaken backup was kept as a counterexample.

The general form of this trap: the default a backup script relies on comes from the runtime environment, not from the application configuration. Container orchestration and deploy scripts each carry their own defaults, and the production database name is only correct in the application configuration. Once a backup script copies the container's default, the backup command itself succeeds and the file lands on disk; the failure only surfaces on the day a real restore is needed. The acceptance test for a backup should not be "it ran", but "does the backup contain the business tables, and how many rows" — an empty backup must be caught on the spot, not on restore day.

## Whether an Upgrade Ships Is Decided by a Ledger

This upgrade's ledger has four columns, each with numbers.

The first column is a clean range: the actual upgrade interval runs from the upstream HEAD merged last time to this time's upstream HEAD — 60 commits, 389 files, with no extra commits outside the interval. With a dirty interval, nobody can tell which upstream change caused a problem.

The second column is customization preserved: the diff between local customizations and upstream is still 47 files and 1,643 lines, identical before and after the merge, which shows this merge quietly dropped no customization and overwrote none of it as if it were an upstream change.

The third column is rollback cost: upstream added no new database migration this time, and the latest migration number did not move. A release with no new migration rolls back by switching back to the old version, without touching the database schema — the cheapest class of release to roll back. Conversely, an upgrade with new migrations needs its rollback plan written separately; "just switch back" is not enough.

The fourth column is build and test evidence: all 3,092 frontend cases passed, and the backend build and unit tests passed; only three cases that depend on a Unix shell needed a completed toolchain before rerunning — environment dependencies should be written down, because the next upgrade will hit them again.

## After Cutover, Verify Again

Once the new version was in the candidate slot and traffic cut over, verification came in two layers. The first layer is entry points: health checks, the login page, the home page, and the register page all returned 200; the login page referenced the new entry file; static assets were normal; the container was healthy, with no restarts and no 5xx, and no panic in the logs. Soon after cutover, a real streaming request was already allowed through, showing the new version works under real traffic.

The second layer is what was not done, and it belongs in the ledger too: no page-by-page browser verification after an admin login — the new features such as image size tiers, email blocklists, and key permissions were never clicked through — and no real paid forwarding verification was initiated. Unauthenticated smoke tests and automated tests cannot replace real business verification. Writing down "what was not verified" matters as much as writing down "what was verified" — the next time someone asks "was this feature verified before launch", the answer is in the ledger, not in memory.

One small trap is worth noting in passing: the deployment package sent to the server was a raw gzip stream, not a tar archive, and the deploy script restores it with gzip streaming. The package format and the unpack command must match; if the format is wrong, the deploy script fails in the middle of the night, and the investigation costs nothing but time.

## Practice: An Upgrade Is a Ledger, Not a Build

1. **Hard-code the database name in the backup script; don't copy environment defaults**: read the name from the application configuration, or write it into the script; don't use the container orchestrator's default database name. After backing up, check the business tables and row counts — an empty backup must be caught on the spot, not on restore day.
2. **Keep the upgrade interval clean**: confirm the interval's start and end points before merging, and don't let commits outside the interval slip in; when something breaks, the interval is the search scope.
3. **Compute the customization diff twice, before and after the merge**: the file and line counts of local customizations versus upstream must match before and after; if they don't, stop and find the cause before shipping with an open question.
4. **Set rollback cost by migration count**: a release with no new migration rolls back by switching to the old version; one with new migrations gets its rollback plan written separately, stating how the database schema goes back.
5. **Write two columns in the ledger: what was verified, and what was not**: entry-point checks, real traffic, and health status go in one column; the browser verification and real paid verification that were not done go in the other. Not verified does not mean passed — write it down, and cover it next time.

## One-Sentence Close

A backup that finished is not a backup that captured anything, and a green build is not a shippable upgrade; ship by the ledger, not by the green light — range, customization, migrations, backup, verification: cut traffic over only when all five columns are filled.
