# Rules for the Knowledge Base

The biggest enemy of a knowledge base isn't too little information — it's true and false mixed together. AI organizes fast and fluently, and when it writes inference as fact, it sounds more certain than a human. After 230+ pages, we set one rule: first separate what counts from what doesn't.

## What counts: five sources of formal rules

A rule earns a place in the "formal rules" section only if it comes from one of:

1. Explicit user confirmation
2. Existing behavior in source code, config, or tests
3. The repo's AGENTS.md
4. Formal docs/ in the repo
5. Confirmed API docs or business specs

Anything outside these five goes to candidates first, no matter how reasonable it sounds.

## What doesn't: five kinds of candidates

The following belong only in the candidate/unconfirmed section:

- AI inference
- Guesses from project names, directory structure, or past experience
- Unconfirmed business rules
- Proposals
- Unverified state transitions, permission logic, or rule judgments

## Writing discipline

- Pages must use headings to separate "formal rules" from "candidates/unconfirmed." Never mix them.
- Never write candidate information in the tone of established business rules. "Should be" and "is" are one piece of evidence apart.
- When a candidate is later confirmed, move it to formal rules and add the source. Promotions leave a trail.

## Source material: snapshots, not secondhand retellings

The knowledge base has three layers: immutable source material → AI-maintained wiki pages ← schema constraints. The source layer consists of "external authoritative sources" plus "raw immutable snapshots."

What goes into raw/: standalone material from the user, pages that may change or go offline, meeting notes, screenshots, exported reports, key evidence that can't be reconstructed after the task ends. New files may be added at collection time; after that they're immutable, each paired with a same-named `.source.md` recording source, date, reason, and SHA-256.

What stays out of raw/: whole-repo copies, dependencies, build artifacts, reproducibly rebuildable files, material with sensitive information. Source code, configs, and docs under Git stay in their business repos, tracked by absolute path, commit/tag, verifiable location, and verification date — referenced, not copied.

## One counterintuitive rule

An empty raw/ passes validation. File count is not a quality metric, and manufacturing fake source material is forbidden.

This is deliberate. Once the metric becomes "number of snapshots," people stuff in rebuildable files to hit the number. Empty means there's no volatile material to rescue right now — that's a normal state, not a gap.

## How to write a source

A "source" line in the wiki must not be just a task name. It needs: source type, path or URL, version, location, date. Without these, nobody can re-verify later, and the source is decoration.

## In short

Three sentences: grade your sources, keep formal and candidate separate; snapshot source material, keep the uncertain out of formal; count isn't quality, empty isn't shameful.

With the rules in place, AI can organize freely — because it knows uncertain things have a place to go, instead of being forced into false certainty.
