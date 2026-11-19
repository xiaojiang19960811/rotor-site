# Set Back to Queued Is Not Re-Enqueued

> Column: Experiment Log | Collection: Agents & Digital Humans | Source: wiki/bugs/Digital Human Agent Worker Recovery Did Not Re-Enqueue Jobs (desensitized) | Status: Drafted · Coming Soon

The conclusion first: recovering a job does not mean setting its status back to "queued" — it means putting it back into a queue that will actually execute it. A digital human Agent's job state lives in two places: the job record in the job record store, and the job itself in the task queue. On Worker restart, recovery only touched the former and left the latter alone: the store said "queued" while the job in the queue had already failed. Worse, the scheduler only reads the store, so it believed a research job was still running and refused to start a new one. A zombie job that nobody executes blocked scheduling permanently.

## Two Places Hold State, Neither Holds the Truth

The job record store is a ledger; the task queue is execution. The ledger says the job is queued, the execution side says it has failed, and nothing in the system can adjudicate which one is right. Recovery logic that only rewrites the ledger assumes the ledger is the truth — but the ledger never was the truth, only a record of execution.

Once the two diverge, the damage runs both ways. With the database showing queued and the queue job failed, the scheduler sees a queued research job and blocks any new autonomous research from starting; there is no job in the queue to execute, and the record in the store never reaches a terminal state. Nothing errors, nothing crashes — the system just quietly stalls: normal from the outside, nothing happening inside.

The trap is deceptive because the recovery itself looks done. The stale jobs were found, their status was set back, and the logs show no errors. Rewriting status is the cheapest recovery to write, and the easiest to fool yourself with: it only moves the cheapest of the two places.

## The First Fix: Three Divergences Reconciled, a Fourth Missed

The first fix changed recovery to take the queue as the source of truth: the recovery function returns stale jobs and checks each one against its real state in the queue. Failed or stuck jobs are retried; jobs missing from the queue are re-added under their original idempotency key; duplicate deliveries and jobs already claimed by another Worker are settled by their idempotency result, never executed twice. Recovery also stopped being a startup-only act: a check every 60 seconds first recovers stale jobs, then reconciles every queued job, so stale states that appear mid-run no longer wait for the next restart.

Verification was thorough: targeted queue tests grew to 9 cases, and the full suite — 54 test files, 232 tests, type checks, and builds on both ends — passed. After cleanup, a new research round entered running and the status endpoint returned healthy. By the evidence available then, the fix was complete.

But it only covered the "not finished" divergences: queue-missing, queue-failed, queue-stuck. One more divergence sat outside those three: the job in the queue had already finished, while the record in the store still said queued. The first fix's reconciliation logic only asked "is the job unfinished" — it never asked "is the job finished but never written back."

## Two Weeks Later, It Came Back: The Finished Side Diverges Too

On September 13, 2026, the same class of problem returned wearing a different face: autonomous exploration had produced nothing new since August 30. Investigation found a research job still marked queued in the job record store, while the corresponding job in the queue had actually completed. The scheduler therefore believed forever that a research job was active, and no new research ever started.

The root cause was identical to the first time, only in the opposite direction: startup and periodic checks handled jobs that were missing, failed, or stuck in the queue, but never reconciled the terminal divergence of "queue completed, store still queued." The blind spot in the recovery logic was not in a code detail but in the enumeration: one divergence was missing from the list.

The second fix closed that side: for jobs completed in the queue, it writes the completed state and result back into the store; and it puts a time limit on the blocking check, so queued or running records untouched for more than 15 minutes no longer block scheduling forever. Twenty-nine targeted tests passed, and once the old zombie jobs were reconciled, autonomous research entered running again.

Only the two fixes together make one complete recovery: the first brings back "the unfinished," the second settles "the finished." Do half, and the other half will come back as a recurrence sooner or later.

## Practice: Reconcile Recovery Against the Execution Side

1. **Let the execution side decide**: before rewriting the store's status, ask where the job actually is in the queue. The store is a record; the queue is the fact. Recovery must act on the fact, not on the record.
2. **Cover every terminal combination**: missing, failed, stuck, completed — each divergence needs its own reconciliation action. Miss one, and it will recur from the other direction, looking like a brand-new problem.
3. **Put a time limit on blocking checks**: any "a job is running, so don't start a new one" rule needs an expiry for stale records. Waiting without a limit is blocking forever; permanent blocking needs no error, only one record that never reaches a terminal state.
4. **Don't recover only at startup**: stale states appear mid-run too, so the periodic check must do the same reconciliation. Recovering only at startup is cleaning only when the door opens — the room gets messy again at any time.
5. **Make state readable by stage**: the admin console should show the research stage alongside the record IDs written at each stage, distinguishing retrieval, organization, projection, and wrap-up. Otherwise, when troubleshooting, you cannot even tell which step a job is stuck at — and recovery has nowhere to start.

Setting a status back is not recovery. Recovery means putting the job back where it can be executed, observed, and brought to an end.
