# Only 3 Letters Fixed, Yet the Job Was Marked Complete

> Column: Experiment Log | Collection: Agents & Digital Humans | Source: wiki/bugs/digital-human-agent world-letter voice repair false completion (desensitized) | Status: Drafted, coming soon

The conclusion first: a digital human agent ran a one-off batch job to unify the voice of a set of world letters, and after fixing only 3 letters, the job record was marked complete — with an empty result. Worse, once marked complete, the job would never be enqueued again: the two follow-up tasks, rewriting replies and re-extracting relationship memory, never started. Failures retry; false completions don't. A wrong "complete" costs far more than a failure, because a failure takes the retry path while a false completion takes the "nothing left to do" path.

## Three records, three stories

After the incident, three records each told a different story, and none of them alone could explain the truth:

- In the job record table, this batch repair was complete, with an empty result field.
- In the business state table, the repair was still running, with only 3 letters recorded.
- In the task queue, the job first stalled, then its second processing run "succeeded" in 3 milliseconds, again with an empty return value.

Three milliseconds cannot rewrite one letter, let alone a batch. The second run did no work at all: it merely handed in an empty result, and the queue counted it as success. Whether a job is done cannot be judged by the queue alone: the queue only knows whether delivery succeeded, not whether the work got done. The business state is the authority: how many letters were fixed, how many remain — only it knows.

## How a false completion happens

The chain has four links. Each looks reasonable on its own; together they make one false completion:

1. **The lock was shortened**: renewing the lock changed it from 10 minutes to 2 minutes. A single letter rewrite taking longer than 2 minutes lost the lock.
2. **The redelivery replayed an empty result**: after the lock was lost, the job was redelivered, and the delivery logic saw the business state was still running, so it returned the existing result directly — and that result was empty.
3. **The queue counted the empty result as success**: receiving a return value, the queue did not distinguish "finished the work" from "handed in an empty result", and marked the job complete.
4. **The idempotency key blocked any retry**: with the job already complete, later publishes never enqueued it again. The work after those 3 letters would never get in line.

Note that this was not a publish interruption: an interruption would send the job back to the queue, noting "worker restarted before completion". An interruption takes the retry path, with a record and a sequel; a false completion takes the "complete" path, with no sequel. Both failures look like "the job stopped", but their costs are entirely different: one can resume, the other silently drops the second half.

## The fix: the business state decides what complete means

The fix covered four points, one per link:

1. **Renew the lock for the same duration as the lock itself**: lock renewal went back to 10 minutes, matching the lock duration, so the lock is no longer lost mid-way.
2. **Redelivery replays only completed results**: a state still running is no longer replayed as success.
3. **Empty completions are no longer copied into the job record**: an empty completion appearing in the queue is no longer written to the job record table; instead, the job is re-enqueued.
4. **Re-enqueue is allowed while the business state is incomplete**: when the business state shows the voice repair unfinished, the completed mark can be restarted and the job enqueued again to continue.

All four fixes share one principle: whether the work is done is decided by the business state. The queue's "complete" is only a delivery state, and the job record's "complete" is only a record state; neither can stand in for "the work itself is done".

## Practice: three rules against false completion

1. **Completion must carry evidence**: when marking complete, the result must not be empty; an empty result counts as incomplete, never as complete.
2. **Redelivery asks the state first**: before replaying a result, confirm the business state is actually complete; anything still running is never replayed.
3. **Idempotency keys block duplication, not continuation**: an idempotency key stops repeated execution, not "pick up unfinished work and continue"; while the business state is incomplete, there must be a path to re-enqueue.

## One line to close

Failures retry; false completions don't: before marking "complete", ask the business state whether the work is actually done — the queue's success and the record's completion can never stand in for the work itself being done.
