# One Click on "Online Update" Took Down a Production Service

> Column: Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/2026-08-14-sub2api-online-update-migration-collision-502 ｜ Status: first draft

**The conclusion first:** a late-night production 502 was not caused by Nginx, memory, or an unreachable database. Its root cause was the one-click "online update" button in the admin backend, which swapped the official upstream binary directly into a production container that had been running a local fork. The fork's migration numbers had been locally renumbered, and the upstream binary could not read that numbering: it tried to create a column that already existed, the app died in the startup-migration phase and entered a restart loop, and Nginx — facing an upstream that would never come up — could only return 502 to the public.

The most memorable part of this incident is not the technical detail, but a process discipline: a forked production environment may only upgrade through its own channel — selective absorption of upstream changes, migration-renumbering audits, immutable images, blue-green deployment. Any "convenient entry" that bypasses this channel, even the product's own one-click update button, must be treated as a forbidden zone.

## Timeline: one click on update, service won't come back

On August 14, 2026, at 18:49, the admin interface processed two requests in sequence: "system update" and "system restart". It was the backend's built-in official online-update entry point — seemingly harmless.

After the restart, the application container began restarting with exit code 1, OOMKilled false — it was not killed by the system; the process itself could not start. The database, cache, and Nginx on the same host were all healthy, but nothing was listening on local port 8080. Because the upstream connection was refused, Nginx returned 502 to the public internet.

The first round of evidence pinned the fault inside the application layer: the container was restarting in a loop while all the infrastructure it depended on was healthy. So troubleshooting turned to the container logs: at startup, the new binary first registered one upstream migration, then failed executing the next one — because the column it tried to add already existed in the target table.

But the database clearly held an executed record for an equivalent migration. Why would an "already executed" migration be executed twice?

## Root cause: migration-number collision, semantic mapping lost

The answer hides in the numbering difference between the fork and the upstream. The fork running in production had historically renumbered upstream migrations locally: the same schema structure was numbered 216 and 217 locally, while the upstream equivalents were 188 and 189. The database registered the local numbers 216/217, and the columns already existed.

The one-click update had pulled in the official upstream binary, which only understands the upstream numbering. It registered upstream 188, then executed upstream 189 — but the column 189 wanted to create had already been created by local 217. The upstream binary had no idea that "local 216/217" and "upstream 188/189" were two numberings of the same semantics, so it treated the existing column as a never-executed migration and created it again. The transaction failed, the process exited, and the container entered a restart loop.

Two judgments matter here:

1. **502 is the external symptom, not the root cause.** Nginx returned 502 because the upstream was unreachable; the upstream was unreachable because the app died during startup migration. Following the "502 means look at Nginx" instinct wastes time; asking "which layer did the request die in" hits the mark in one shot.
2. **No migration was written wrong.** Both numbering schemes were correct on their own. The mistake was letting a binary that "doesn't understand local numbering" take over "a database registered with local numbering". The failure happened in the upgrade channel, not in the code.

## Troubleshooting discipline: read-only diagnosis first, then backup and forensics

This was a production incident, and the first rule of troubleshooting is "see clearly before touching anything". The response at the time was purely read-only diagnosis: container state, logs, the database's migration registry, and the actual column existence were inspected — without restoring binaries, writing to the database, or restarting/switching production traffic.

Before confirming the recovery plan, forensics backups were taken: the binary swapped in by the one-click update, the auto-generated backup of the old binary in the container's writable layer, and the pristine binary from the local immutable image were all saved to an isolated recovery directory with SHA-256 hashes computed. The result closed the evidence chain: the backed-up old binary was byte-identical to the image's pristine binary, while the one-click-updated binary differed from both — confirming the binary in the container had indeed been replaced.

This step's value is reversibility. In a production incident, the most dangerous thing is "fixing things without knowing what you've changed". Freezing the scene and keeping hashes means every later action has a defined rollback point.

## Recovery: forced rebuild from the immutable image, zero writes to the database

The recovery did not "fix" the database, nor did it hand-patch the migration registry. Instead, the main service was force-recreated directly from the immutable local image. The whole recovery overwrote nothing — not the database, cache, Nginx configuration, volumes, old images, or release directories. Not a single write went to the database.

After the rebuild the container was healthy, the restart counter reset to zero, and port 8080 was listening again. The local health check and the production domains' HTTPS and HTTP endpoints all returned normal. The observation window showed no new panics, fatal logs, migration failures, checksum mismatches, or duplicate-column errors. A post-recovery database check confirmed: the registrations for upstream 188 and local 216/217 were all intact, and the failed upstream 189 was never registered. Everything stopped exactly at the pre-incident state.

The key to the successful recovery was not technical brilliance, but admitting one thing: when the upgrade channel itself is wrong, the fastest and safest fix is to return to the last known-good state — not to keep patching on top of the broken one.

## Prevention: four forbidden zones

This incident left four formal rules:

1. **In a forked production environment, disable or intercept the backend's official online-update entry.** Upgrades continue through the local channel: selective upstream absorption, migration-renumbering audits, immutable images, blue-green deployment. The one-click update button in a forked environment is not a convenience feature — it is an incident entry point.
2. **Migration numbers are a semantic contract, not just filenames.** Once local renumbering exists, the semantic mapping of "local numbers ↔ upstream numbers" must be maintained, and every binary that touches the database must understand it. Matching filenames is not matching semantics.
3. **For a 502, check the application layer before the edge layer.** When the upstream connection is refused, first inspect the app container's liveness and startup logs to establish "who is refusing and at which step it died", then decide whether to look at Nginx or at code.
4. **Troubleshoot production read-only first, then forensics, then action.** Freeze the scene, compute hashes, confirm the rollback point — and only then execute recovery. Avoid writing to the database during recovery whenever possible.

## Closing

The words "one-click update" are only guaranteed for the official, unmodified environment. A forked environment has its own numbering scheme and its own upgrade channel; keeping the official convenience entry intact in a production backend is leaving an unlocked door inside your defenses. This time it was a migration-number collision; next time it could be something else. The door should be locked shut — not rescued one fire at a time.
