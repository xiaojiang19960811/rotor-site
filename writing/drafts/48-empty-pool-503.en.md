# "Two Channels" Doesn't Mean Two Are Actually Bound

> Column: Lab Log | Collection: AI Infrastructure | Source: wiki/bugs/2026-10-21 Multi-Model Gateway Empty Group Pool Causing 503 (desensitized) | Status: Drafted · Upcoming

This afternoon, requests for two new models in one group all returned 503, lasting nearly two hours. The user's question was direct: "This model clearly has two channels. Why did it stop at A and never try B?"

The investigation surfaced three facts, each worth writing down:

1. B was never in the group: the "two channels" the user described (upstream accounts A and B) showed only one record, A, in the group's binding table. B had never been added, and the group had no fallback group configured.
2. A had been manually paused four days earlier: the audit log showed an admin marking it unschedulable on October 17, and the scheduler snapshot went empty-pool in sync.
3. So the scheduler never even attempted the "fail over from A to B" path: the candidate set was empty from the start, as `pool=0` and `excluded_account_count: 0` in the log made clear.

## The Diagnostic Bit: pool=0 and "All Excluded" Are Two Different Things

This is the most valuable section of the investigation. Seeing 503, the first instinct is "all accounts got blocked," followed by digging through why each account was excluded. But the log carried two numbers pointing in another direction:

1. `pool=0`: zero accounts entered the candidate set.
2. `excluded_account_count: 0`: zero accounts were individually excluded.

"All excluded" means: there was a batch of candidates, each was checked, each exclusion has a reason. "Empty candidate set" means: nobody ever entered the pool, not even getting the chance to be checked. The two call for completely different investigation moves:

1. All excluded: walk through each exclusion reason (upstream errors, quota, model mapping).
2. Empty candidate set: check who is bound to the group and what the switches say, then look at accounts.

If you assume "all excluded" and go hunting, you will spend a long time inside exclusion reasons while the real problem sits in the binding table: a table that never appears in the error stack.

## Two Switches: One Heals Itself, One Stays Put

The investigation also turned up two "pauses" that look alike but have completely different semantics:

1. **Temporary unschedulable** (`temp_unschedulable_until`): time-window semantics. The query condition is "null or expired," so it recovers automatically on expiry. This time its value sat at October 16, long expired — not the cause.
2. **Schedulable** (`schedulable`): an independent hard switch, changeable only manually through the admin panel, never self-healing on expiry. This one was set to false on October 17 and stayed there through October 21, with no automatic recovery.

There is one more observable difference between them: automatic error isolation also flips the account status to error. Here the account status stayed active throughout, which rules out the automatic isolation path: the pause was made by a human, not by the system.

Lesson: when a system has two different kinds of "stop," distinguish their semantics before concluding. On seeing "unschedulable," first ask: which kind? Will it heal on its own?

## An Empty Pool Ran for Two Hours, and Nobody Was Paged

From 16:00 to 17:57, group scheduling kept returning pool=0, and the failure went unnoticed for nearly two hours until the user reported it. The scheduler log had a single WARN and no alert.

An empty candidate set is one of the most alert-worthy events in a scheduling layer: it is worse than "high error rate," because a high error rate at least means someone is still trying, while an empty pool means "this path has no fallback at all." A persistent pool=0 should page in the first minute, not wait for the user to arrive with 503s.

The remediation is equally clear: if a group line promises "two routes," bind both upstream accounts into the group and configure a fallback group; restoring a manually paused account is a single switch flip. But before any of that, make pool=0 able to speak for itself.

## Closing

Three lines to remember when debugging scheduling:

1. When the user says "two routes," count them in the binding table first — don't look for answers in the retry logic.
2. When the log says pool=0, check whether excluded is 0 first: if it is, investigate the pool's shape; if not, investigate the exclusion reasons.
3. When the system has two kinds of "stop," first confirm which one heals itself and which one sits there waiting for a human.

Between "feeling like there is a fallback" and "actually having one," the difference is often a single act of counting.
