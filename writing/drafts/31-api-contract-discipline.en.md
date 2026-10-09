# Don't Hardcode Unconfirmed API Contracts

> Column: Garden ｜ Collection: Engineering ｜ Source: wiki/concepts/接口契约纪律 ｜ Status: draft

**Bottom line first:** Field names, status values, response shapes, and business semantics are contracts, not details. A contract has exactly three legitimate sources: confirmed API docs, source code, or user sign-off. Logic the frontend hardcodes from guesswork to keep integration moving doesn't disappear when integration ends — it stays in the codebase, collecting rent.

## Definition: What Is a Contract

A contract is every agreement about data between frontend and backend: what fields are called, what types they are, what values a status enum can take, how responses nest, what each value means in business terms. It's not "the backend's business" — every mapping line and every status check in frontend code is a vote on the contract.

Only three sources count, in priority order: confirmed API documentation; when docs are missing or dubious, source code or runtime evidence; for business interpretations, user confirmation. Everything else — verbal agreements, names copied from a screenshot, names seen in another project — is an unconfirmed contract.

The reason this is a discipline is that the frontend is usually the first place a contract gets "written down" as code. During integration the API is still shifting, deadlines press, and hardcoding a guess feels like the only option. But guessed code looks exactly like confirmed code, so nobody can tell them apart — the temporary fix becomes the formal logic, and nobody ever goes back to confirm.

## Rule 1: Field Mapping Defaults to Confirmed API Docs

The first authority for mapping logic is the docs, not a sample response. A sample response may be hand-edited, or may only cover the happy path. "What fields exist" comes from the docs; "what one response looked like" comes from a capture. Don't mix the two.

When docs are missing or clearly stale, don't reach for "convention" as a substitute. "We've always named it this way in past projects" is not confirmation — it isn't one of the three sources. Stale docs should either be pushed to update, or downgraded to an observation explicitly marked as not counting.

## Rule 2: Don't Keep Multiple Field-Name Fallbacks Proactively

This is the easiest trap. When a field name is uncertain, it's tempting to write `res.data.name || res.data.title || res.data.label` and call it "being compatible". But once that line merges, it can never be removed: nobody knows which field actually takes effect in production, and deleting any of them risks an incident. The cost of contract uncertainty gets pushed from "confirm once" to "maintain forever".

Keep fallbacks only for explicitly confirmed scenarios — "we need to support an older version" — with an expiry time or version attached. A compatibility mapping with no confirmed basis saves three minutes today and collects maintenance tax every year after.

## Rule 3: When the Definition Is Missing, Confirm First, Then Write Formal Logic

No definition means ask: ask the API owner for the semantics, read the source for the truth, ask the user to confirm the business meaning. Write the formal logic after confirmation.

If the deadline truly can't wait, temporary logic is allowed — but it must be explicitly marked temporary: TODO, comment, and a task entry, none optional. The most dangerous form of temporary logic isn't "written badly", it's "written identically to formal logic", so no one can tell the difference. Marking is whitespace left for your future self, and a warning for teammates: this logic's contract isn't confirmed yet — check back here before changing backend definitions.

And confirm with the right person. Ask the API owner about field semantics, the requirements owner about business interpretations. Don't treat "it runs" as "it's confirmed". Passing integration only proves the data is right on this one path — it proves nothing about the full status set, error branches, or boundary semantics, which is exactly what docs and user confirmation cover.

## Rule 4: When Docs and Actual Responses Disagree, Write Down Three Things

What the docs define, what the actual response is, and how the current code handles it — when they disagree, record all three in one place.

This is a discipline because the instinct is to pick the convenient one: "well, this is what the real response looks like, let's just code to the response." But the real response may be an accident of one version; hardcoding to it turns an accident into an agreement. Writing the three side by side makes the risk visible: whether to push the API owner to fix the response, fix the docs, or adjust the frontend — each decision gets its evidence. A team that can't see the conflict doesn't make it go away; it just delays the explosion until production.

## Closing

These four rules come from common lessons distilled across several frontend projects — admin consoles, H5 clients, business backends. Different projects, same pit: contracts got hardcoded before they were confirmed, and forgotten after they were hardcoded. Remember one line: **confirm before you hardcode, or the frontend isn't writing business logic — it's paying for the API's variability.**
