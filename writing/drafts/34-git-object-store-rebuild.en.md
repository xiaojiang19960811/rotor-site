# When Git's Object Store Breaks: Don't Repair, Rebuild from Remote

> Column: Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/2026-09-20 git object-store corruption and remote recovery ｜ Status: Draft

**Up front:** One project's local Git repository went "half-dead": `git status` threw a fatal error reading the tree, and `git fsck` reported large numbers of missing objects. Nobody tried to repair the broken objects — missing Git objects cannot be repaired, only replaced. Recovery took three steps: first confirm the working tree was intact, then pull a complete clone from remote, and finally drop its object pack straight into the damaged repository's object store. Five minutes later `git status` was back to normal, and every staged change survived. Remember one line: **Git's real source of truth is the remote, not your local .git; when objects are gone, don't repair — fetch.**

## The Symptom: A Half-Dead Repository

On 2026-09-20, a local working branch of the digital-person agent project threw `fatal: unable to read tree` on `git status` — it couldn't even read the current worktree state. `git fsck --full` showed the index's cache-tree pointing at invalid objects and reported large numbers of missing blobs, trees, and commits. `.git/objects/pack` was empty — this repository was essentially living on a damaged set of loose objects, which worked "just barely" until some operation finally tried to read the missing part.

The corruption was uneven, interestingly: the working branch's HEAD commit also existed on the remote, and the HTTP remote was readable. The worktree still held a batch of staged changes and new untracked files. Those changes were things the recovery was absolutely forbidden to touch — they are the "work product"; the repository is just the "packaging".

## Diagnosis: Separate the Worktree from the Object Store

A Git repository contains two completely different things, and damage must be assessed separately.

One is the worktree: the files in the current directory, including staged but uncommitted changes. This layer was intact in this incident.
The other is the object store: the blobs, trees, and commits under `.git/objects` — Git's "database". This layer was broken.

The diagnosis had exactly one goal: confirm whether the remote had these objects. `git ls-remote` showed the remote was readable and a remote branch pointed at exactly the same commit as local HEAD. That established the recovery's legitimacy: the remote had a complete object graph consistent with local HEAD, so the local object store's gaps were fillable, not unrecoverable.

Scope was also bounded on the side: another old local branch was missing 4 objects, but no remote had that branch, and the alternate remote was unreachable due to an unavailable SSH key. Recovery of that branch was explicitly marked "to be confirmed" — no forced repair, no casual deletion. A branch whose objects cannot be supplied is a branch you don't touch.

## Recovery: Add the Pack, Don't Repair Objects

The actual recovery was three steps, no magic.

Step one: create a temporary clone from the remote, without checking out a worktree. All that was needed was its complete object pack (about 78 MiB).
Step two: copy that pack file directly into the damaged repository's `.git/objects/pack` directory. Git searches packs when reading objects, so everything missing from loose objects got covered. No index rebuild, no reference changes.
Step three: verify. `git status` returned to normal with all worktree changes preserved; `git cat-file -p HEAD^{tree}` readable; `git fsck --full HEAD` reported no missing objects, only normal historical dangling objects.

One red line was strictly enforced throughout: nothing in the worktree was rolled back, overwritten, or cleaned. Any recovery plan whose first step is `git reset --hard` or deleting `.git` and starting over fixes the "packaging" and throws away the "product". Wrong order.

## What Stayed Unrecovered: The Old Branch

A repository-wide `git fsck` still reported 4 missing objects, scoped to that old local branch. The record is deliberately honest: the working branch can continue development, but the whole repository cannot be declared lossless; the damaged old branch is neither checked out nor deleted.

That "partial recovery" style of recording is itself a discipline: the scope of recovery must match the evidence from verification one-to-one — a branch counts as recovered only when its objects are readable. To recover the old branch, the objects must first come from another backup, a dev machine, or a remote that still holds it, before any reference repair is considered. Without evidence, write "to be confirmed" — don't write speculation as conclusion.

## Takeaways

This incident left four reusable rules:

1. **When the object store breaks, protect the worktree first, then replace objects.** The worktree is the product; the repository is the packaging. Step one of any recovery plan is always confirming staged and untracked files are fine.
2. **Don't "repair" missing Git objects — fetch them from the remote.** Missing objects have no repair operation, only a replacement operation: drop in a pack from a remote clone and leave the index alone.
3. **Keep recovery scope one-to-one with verification evidence.** Branches that can be read count as recovered; branches with no way to supply objects are marked "to be confirmed", untouched and undeleted. A whole repository that "looks fine" is not evidence of completed recovery.
4. **Important local branches must have a remote or bundle backup.** A branch that exists only on one machine has no legitimate source of objects once they break. Dangling objects are not a backup; unpushed branches are not a backup.

Git is distributed by design: any complete remote clone is a legitimate source for rebuilding your local object store. When the repository breaks, don't repair the repository — rebuild it from the remote.
