# Wrote the Row, Skipped the Projection: 47 Knowledge Entries Without a Version

> Column: Experiment Log | Collection: Agents & Digital Humans | Source: wiki/bugs/digital-human-agent knowledge entries without versions (desensitized) | Status: Drafted, coming soon

The conclusion first: in a digital human agent's knowledge base admin, a large number of entries showed "no version built", and every detail page returned not found. No data was lost; every research item was intact. What was missing was the projection in another table. When a new research item was written, the write path only wrote the main table; it never created the knowledge asset, version, and evidence in the same transaction. In the dev database, 47 of 156 research items had no version: close to a third.

## The chain behind the 404 detail pages

The list page and the detail page do not use the same key. A list row carries only the research item's ID, not the knowledge asset's ID, while the detail API looks up by asset ID only. With no asset ID at hand, the frontend fell back to the research item ID: the request went out, the API looked it up as an asset ID, found nothing, and returned not found. The item existed, yet its detail page could never open.

Worse, the fallback looked reasonable: both are IDs, substituting one for the other raised no error, and the page simply showed "not found". The gap was hidden inside an ordinary 404, and nobody would guess that a write step had been skipped.

The list page itself looked perfectly fine: every item was there, the counts matched, and only the "click through to read" step was broken. The breakage showed in the detail page, the root cause sat in the write path, and a whole ID mapping lay between them. When something failed, nobody suspected the write first.

## Why it went unnoticed for so long

The system did have a safety net: on service startup, a compatibility migration bulk-created knowledge assets, versions, and evidence for existing items. But it only ran at startup. While the service kept running, new items stayed version-less; each restart patched the historical gap, and a new gap started accumulating from the next new item.

That was the problem: a compatibility migration patches historical data; it is not a write path. It fixes "what was missed in the past", not "what is being written now". Treating a compensation mechanism as the write path means accepting that new data can start out incomplete and be fixed later, while "later" only arrives at the next restart.

## The fix: write everything at once

The fix closed the gap in three places:

1. **New items written in full, in one transaction**: when a new research item is added, the knowledge asset, v1 version, evidence, and auto-publish event are created in the same database transaction; if any step fails, the whole batch rolls back, leaving no half-written record.
2. **Startup migration back to compensation duty**: the startup compatibility migration stays, but only patches historical data and gaps left by interrupted runs; it no longer carries projection work for new writes.
3. **Closed-loop tests for writes**: new write tests cover asset, version, and evidence all being written inside the transaction; missing any one of them fails the test.

After the fix, the dev database was rebuilt and rechecked: 156 research items, 156 knowledge assets, 156 versions, zero items without a version, zero assets without a version.

## The practice: derived data shares a transaction with its source

1. **Derivation belongs in the write path**: whenever "writing A must also create B", B's creation must happen in the same transaction as A. Patching it afterwards, at startup, or in a scheduled job is not a write path.
2. **Compensation only patches history**: migrations, backfills, and compatibility logic exist to close out old data and interrupted runs; state their boundary clearly. Once they start covering for new writes, gaps accumulate quietly. When a new field or status rule is added, the startup migration and the write tests must be updated together.
3. **A missing key ID is an anomaly, not a reason to fall back**: when the list cannot supply the ID the detail page needs, report a data anomaly. Substituting a different ID only hides a write gap as an ordinary 404.

## One line to close

Write the main table without building the projection, and knowledge will end up version-less sooner or later: derived data must be born in the same transaction as its source. Later fixes can only close out history; they cannot serve as the write path.
