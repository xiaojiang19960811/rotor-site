# Forking Open Source: Selective Upgrades

> Column: Build Notes ｜ Collection: AI Infrastructure ｜ Source: wiki/concepts/选择性上游升级 ｜ Status: first draft

You've forked an open-source project and upstream keeps shipping: follow or not? Merging directly lets upstream changes clobber local increments; never following lets the gap grow until even security fixes can't land. Our answer is selective upgrade: never merge upstream directly; hand-absorb upstream changes by topic, risk, and local-increment protection.

## Three iron rules

1. **Never merge upstream directly**: absorb by upstream commit, release notes, and topic — one by one, by hand. An absorbed topic lands as a complete capability chain, never a half cherry-pick — half a feature is more dangerous than none.
2. **Keep local semantics**: local selective-upgrade semantics and fork increments are first-class assets. The version string keeps a local marker (e.g. `0.1.139+` / `PATCH_LEVEL=0.1.139`) and never drops it to align with upstream. `PATCH_LEVEL` isn't version decoration; it declares "this build contains local increments."
3. **Never delete local capability to align**: never remove local capabilities, enums, entry points, config items, translation keys, or tests just to match upstream. Alignment isn't the goal; correctness is.

## High-risk items: no unconfirmed changes

Some things affect production behavior when touched — high-risk items: platform enums, account/group types, permission and state transitions, billing and risk-control rules, public API contracts, persistence fields. None of these may be deleted or narrowed without explicit confirmation. When merging language packs, keys still referenced locally must be kept — never overwrite with the upstream pack wholesale. One dropped translation key is one blank string in production.

What not to absorb must also be written down: Sponsors, README, and Logo updates are skipped unless the user explicitly asks to sync; upstream migration-number reorderings and RBAC-related deletions are skipped unless the deletion and migration plan are confirmed separately. A ledger entry of "evaluated, not absorbed" beats pretending you never saw it.

## What one absorbed release looks like

Take one minor release. Low-risk gateway and payment fixes, gateway compatibility fixes, and billing-rule fixes get absorbed first; a public error-contract fix (like `model_not_found`) gets absorbed because it affects callers' error handling; a subscription support item gets absorbed as an independent upgrade topic with its own verification; a behavioral change like instruction fallback lands together with its default policy config.

Note the wording behind each item: "absorbed," not "merged." The difference in wording is the difference in method: merging takes upstream as-is; absorbing digests only what's needed.

## Lesson from a re-review: split the evidence

A later major-version re-review added an important judgment: selective upgrade isn't just "picking commits" — contract, compile, runtime, release, and rollback evidence must be split apart. Menu viewport, quota management, custom page drag-and-drop, long-connection bridging, usage filters, cache/routing/throttle/identity, model eligibility: verified separately, never replaced by one blanket acceptance.

Candidates that pass still bind to branch, version, environment, and verification scope. After release, blue-green switch, and health checks pass, real provider credentials, production traffic, and high-risk rules stay in post-release observation — shipping a version never automatically proves every upstream capability holds in production. Neither the upstream version number nor one successful build can cover a topic that's still locally unclosed.

## In short

The fork upgrade strategy is three sentences: hand-absorb by topic, never merge directly; local increments and high-risk items don't move without confirmation; verify each class of evidence separately, never use a version number as a quality certificate. Upstream is someone else's progress; production is your own responsibility.
