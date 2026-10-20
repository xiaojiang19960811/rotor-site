# Two Lines Told Apart by Branch Names Alone Will Mix Sooner or Later

> Column: Build Notes | Collection: AI Infrastructure | Source: wiki/decisions/2026-10-20 multi-model gateway two-line repository split (desensitized) | Status: Drafted · Upcoming

When two long-diverging lines share one repository and are told apart only by branch names and human memory, "looking like one line" is itself a liability: misuse is not a question of whether, but of when. The bar for splitting repositories is a single one: the directory structure itself must show two lines, not branch names plus manually read commit history.

## The Starting Point: A Convenient Single Repo That Became a Liability

It began as convenience: one private fork carrying two lines. One was the multi-model gateway version I maintain myself; the other was the version running in the company's production environment. Locally there was a single main clone plus several worktrees, all sharing one Git object store.

That structure had three consequences, each making "separation" harder over time:

1. **Whether the sources were separate could not be told from the directory structure**: only branch names and manually read commit history could tell them apart. Nothing in the directory itself revealed two independently evolving lines.
2. **Build products and history kept piling up**: the main clone accumulated roughly 110 GB of build products and 16 registered worktrees, 12 of them leftover from half a year earlier. The "cheapness" of a single repo was eventually repaid in disk space and mess.
3. **The version divergence kept widening**: the two lines differed by one minor version, with mutually exclusive branches. Continuing to share one object store would only amplify the risk of misuse.

This is exactly the day reserved in [Article 5, "One Repo Not Split, But Organized for a Future Split"](/writing/05-monorepo-future-split): organizing "for a future split" exists so that the split, when it comes, costs a manageable amount — not so that the repo is never split.

## Alternatives: List Them, Then Reject Them One by One

The conclusion was "split completely and evolve independently": one independent repository, object store, and remote per line, with the old directories cleaned up. Before reaching that conclusion, the alternatives were listed, each with its reason for rejection:

1. **Keep the single repo with multiple worktrees**: the object store stays shared, separation cannot be judged from structure, and build products plus historical worktrees keep accumulating. That just defers the problem.
2. **Split into two repos but rewrite history (strip the other line's commits)**: the other line differed from the common ancestor by hundreds of thousands of lines; rewriting is risky and destroys traceability to upstream. Clean, but at the cost of losing historical credibility.
3. **Split only the remotes, keep sharing the object store locally**: solves nothing at the disk and directory level. Equivalent to no split at all.

The chosen approach was "keep full history, separate object stores": both sides still share the upstream ancestor in history, but refs and object stores are mutually independent; when a cherry-pick is needed later, a remote is added temporarily.

## Count the Cost Before Acting

Writing down the cost before splitting is the most valuable section of this decision record:

1. **Two .git directories, about 10 GB each**: at split time they share disk through hard links, occupying only one copy; but once either side runs gc, each packs independently, so doubled disk usage is only a matter of time.
2. **Database migration tables will diverge over time**: the two lines' nearly-isomorphic state will not stay aligned on its own; schema evolution goes its own way from here.

The cost is not a reason against splitting; it is a bill to keep paying after the split. Written down so it can be reconciled later.

## Execution and Verification: A Split Must Prove Itself Clean

The execution itself was not complex: generate two new repositories from local clones (hard links by default), without the shared-object-store option, so neither side depends on the other's object storage. The verification is what matters:

1. **Re-verify after deleting the old directories**: both repositories pass connectivity checks with zero errors, working trees are clean, and commit history, branches, and tags are all readable. This proves the hard links independently hold the objects, and deleting the old clone took nothing with it.
2. **Production machines are unaffected**: they only receive built binaries and never see repository addresses; subsequent builds are simply produced from the two new directories.
3. **Clean up historical baggage**: the old main clone (with its roughly 110 GB of build products) and a dozen historical worktrees were deleted together, freeing about 110 GB of disk.
4. **Sweep the branch pointers**: more than eighty branch pointers that existed only locally, with no remote counterpart, were deleted along with the old clone and not migrated. Keeping them would carry the "tell them apart by memory" habit into the new repositories.

## The Criterion and the Review Conditions

From now on the bar for a repository split is a single criterion: **does the directory structure itself show two lines**. If yes, the split is clean; if no, it is not done.

But splitting is not a one-time cure. The decision keeps two review conditions; if either triggers, the decision is re-evaluated:

1. If a standing need arises for both lines to share the same commit (for example, one fix that must ship to both sides), re-evaluate whether to keep a cherry-pick channel.
2. If the cost of merging upstream rises noticeably under two repositories, evaluate switching to one-way sync plus a patch queue.

Single repo versus two repos was never a fight over "saving a few gigabytes." It is about who carries the probability of mistakes. Two lines told apart by branch names place that probability on everyone's memory; two lines visible in the directory structure place it on the structure itself. Whatever the structure can carry, don't ask people to memorize.
