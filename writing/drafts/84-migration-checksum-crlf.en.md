# The SQL Never Changed, but the Checksum Did

> Column: Experiment Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/2026-07-13 multi-model gateway migration CRLF checksum mismatch (desensitized) ｜ Status: Drafted · Upcoming

Conclusion first: not a single character of the migration files had changed, yet the migrator refused to start, reporting a checksum mismatch. The problem was not in the SQL, and not in the database. It was in the line endings: a historical build had embedded the same migrations with CRLF, and the database recorded hashes of the CRLF text; the current build uses LF. The SQL matches line by line, but the bytes changed, so the hashes no longer match. A checksum checks bytes, not meaning.

## Symptom: nobody touched the migrations, yet startup failed

At startup, the migrator stopped at the first step: the checksum of a historical migration did not match. Its conclusion was that the migration file had been altered, so it refused to proceed rather than build tables on a tampered migration.

The same error appeared in two environments at once, local and production. That distribution is itself a clue: if only one environment had failed, the record in that one database might be at fault; failing in both points at how the migration files reach both places, not at one database being tampered with.

## A checksum only reads bytes, not meaning

The migrator's check is simple: hash the raw text of the migration file and compare it with the hash recorded in the database. A hash function does not understand SQL; it only sees bytes. CRLF is two bytes, LF is one. The same SQL with different line endings is a different byte string, so the hash must differ.

That is why "nothing changed" and "the checksum changed" can both be true: the first is a semantic judgment, the second a byte-level one. Confusing the two leads to two wrong conclusions: either the database was tampered with, or the migrator is broken. Neither is right. What is wrong is the assumption that the file is still the same file.

The migrator is designed this way for a reason: its job is to notice that a migration file differs from the one that originally ran. It has neither the ability nor the mandate to judge whether the difference is semantic. The moment it starts understanding semantics and waving through differences that "look unchanged," the tamper-evidence lock stops being a lock.

## Three pieces of evidence rule out "someone edited the migration"

Before settling on a root cause, the most serious possibility had to be excluded first: that someone had edited an already-executed migration.

1. **The old artifact reproduces it**: the CRLF text could be extracted from the historical build artifact, and re-hashing it produced exactly the hash stored in the database. The recorded hash was correct; what was wrong was the premise that the current file is identical to the original.
2. **No semantic change in version history**: searching the commit history showed no semantic change to the migration SQL at all. The only change was line endings.
3. **Converting line endings alone yields identical lines**: converting only the line endings of the current file, without touching any SQL, produced line-by-line identical content.

Together, the three leave a single root cause: cross-platform line endings. The historical build, produced in a Windows environment, embedded CRLF verbatim; the current build, from a Git working tree, uses LF. The same migration is different bytes at different stages of the pipeline.

## Fix with restraint: narrow compatibility, not removing the lock

The fix added a narrow LF/CRLF hash compatibility for this batch of historical migrations: each file and each hash listed individually in an allowlist, so the migrator accepts both hashes as legitimate.

The restraint shows in four refusals:

1. **No global re-normalization of all historical migrations**: only the affected batch was touched, not the ones that were fine. Normalizing every historical file at once would rewrite the bytes of every executed migration, a risk surface far larger than the original problem.
2. **No deleting migration records**: the records are the audit trail. Deleting them destroys the evidence of who ran what and when. Fixing a checksum by deleting records trades auditability for a successful startup.
3. **No re-running historical migrations**: re-running would touch business data, for the sole benefit of a clean checksum result, at an uncontrollable cost.
4. **No loosening the check**: the checksum verification was not switched off or relaxed. This very error proves the lock works as designed: the bytes changed, and it raised the alarm. Fixing a line-ending problem by removing the lock trades long-term safety for short-term convenience.

Verification followed the same discipline: after a full backup was checked, startup succeeded and later migrations applied normally; a second production environment passed the same compatibility check.

## An allowlist is not unconditional trust

Before an old hash is admitted, the SQL must be verified to differ only in line endings: compare line by line, confirm nothing differs except the endings, then write the hash into the allowlist and guard it with a regression test.

The order cannot be reversed: verify first, admit second. Otherwise the allowlist stops being a precise registry of known differences and becomes a fast lane for hashes of unknown origin, and the next time someone genuinely edits a migration, the allowlist will wave it through. "Narrow" means two things: only these two hashes, only this batch of files.

## Preventing recurrence: line endings are part of the release artifact

1. **Pin migration files to LF**: write the line ending into the standard, so new migrations use exactly one ending and cut off cross-platform differences at the source.
2. **The build environment must not silently rewrite the line endings of published migrations**: the build only packages; it does not change the bytes of published files. Migration files inside the build artifact must be byte-identical to the ones in the repository.
3. **On a checksum error, check bytes before content**: seeing a checksum mismatch, the first question should be "where did the bytes change," not "who edited my SQL." Compare bytes first, then talk about meaning.

## Closing

When a checksum fails, the failure itself is not the fault; it is the protection working. The real fault is bytes changing where nobody was watching. Fix it narrowly, slowly, and with evidence kept; prevent it by treating line endings as part of the release artifact.
