# Before Switching Frameworks, Answer Five Questions

> Column: Garden ｜ Collection: Engineering ｜ Source: wiki/decisions/Execution Runtime Refactor Review ｜ Status: Draft

**Conclusion first:** When a system with a working execution engine wants to switch frameworks, the review should not focus on how strong the new framework is. It should ask whether three old problems get solved, and whether five new questions get answered. A framework swap fixes neither upstream errors, evidence gaps, nor context overflow. If it cannot answer who drives execution, what it can retire, whether replay equals exactly-once, whether framework support equals system fit, and whether it can roll back, do not start the migration.

## Three problems a swap cannot fix

The most common illusion in a refactor review is treating "switch frameworks" as "fix a class of problems." Three classes of problems have nothing to do with framework choice:

1. **Upstream errors**: upstream failures, timeouts, malformed responses. What they need is transport diagnosis: which layer failed, whether retries exceeded authorization, whether failures entered the ledger. A new framework does not produce diagnosis.
2. **Evidence gaps**: incomplete materials, citations that do not match, missing business facts. What they need is material governance and business-gap handling: what is missing, who supplies it, what happens when it cannot be supplied. A new framework does not produce evidence.
3. **Context overflow**: inputs too long, budgets exceeded, selection out of control. What they need is context selection and budget governance: what gets in, what must be dropped, who stops it when it overflows. A new framework does not produce governance.

These three problems survive any framework swap. The first step of a review is to strike them from the migration rationale: do not migrate because of these three problems, and do not expect them to vanish after the migration.

## Question 1: Who drives execution

One task can have only one driver at a time. The new flow fixes a single runtime by record; the old scheduler and the new framework must not drive the same flow together. Old records stay on the old path; do not force them to move.

Dual scheduling is the risk most easily hidden by the slogan "smooth migration": both sides believe they are driving, and the state splits. Which side wrote the ledger, which side sent the request, which side assumed the other would finish — the three accounts stop matching, and during an incident nobody can even answer "who is running this now." Old and new may coexist during migration, but they coexist as separate paths for separate tasks, not as two lives for the same task.

## Question 2: What can the pilot retire

The pilot's acceptance bar is not "the new framework runs." It is "the old duties retired." The pilot must prove it can retire the corresponding old scheduling duties. If it only adds another wrapper — the new framework runs, the old code stays, maintenance responsibility does not shrink at all — then do not expand the migration.

Between "it runs" and "it replaces" lies the entire old duty list: scheduling, recovery, authorization, billing, versioning, report readiness. Each item must be verified against its callers to confirm it truly handed over; "the new framework supports it all" does not close any of them. Migration pays off through the maintenance responsibility it removes, not through the wrapper it adds.

## Question 3: Does replay equal exactly-once

A durable workflow framework's replay mechanism governs execution control, not external side effects. Replay must not be read as "the external side effect happened exactly once": replaying a control flow once may already have sent a request twice or charged a fee twice.

So retries must be configured explicitly, layer by layer: framework, model interface, transport, output correction — each layer writes its own rules. Implicit retries on paid paths start disabled, and any recovery must pass the original authorization and a new call ledger again. Successful results are never redone, unknown fees go to reconciliation, and a restart must not reset the original recovery budget.

## Question 4: Does framework support equal system fit

A framework's documentation saying it supports a capability does not mean this system has passed adaptation. Real streaming progress, reconnect after disconnect, material size, cancellation semantics — each needs dedicated verification. "The framework supports the integration" is not an acceptance conclusion.

A first acceptance round should cover at least eight scenarios: crash before send, crash after send without ledger entry, restart after success, permission revocation, version change, repeated recovery, unknown billing, and limit overflow. Counting must also stay separate: logical tasks, model attempts, real requests, and unknown fees — four ledgers, each kept on its own. Unauthorized new sends must be zero. There is no room to negotiate on that one.

## Question 5: Can it roll back

Rollback is not "switch back to the old engine." It is three things: stop the new flow, keep the audit trail, and never hand unknown in-flight tasks to the old engine for automatic resend. Auto-resending tasks whose state is unknown turns one rollback into a new incident.

A migration that cannot roll back is a release with no rollback plan. Passing the review requires the rollback path itself to pass acceptance.

## Closing

The five questions are really one question: every bit of migration benefit must come with a corresponding, verifiable handover of responsibility. Cross out the old problems it cannot solve, block the new questions it cannot answer, and what remains is a migration worth doing.

[Article 36, "The Model Only Proposes Plans: Three Gates for Agent Side Effects"](/writing/36-agent-side-effect-gates) covers the gates before execution: side effects must be declared, authorized, and recoverable. This article is its prerequisite: even the decision of "which framework, and how to switch" must pass through a gate first. [Article 40, "The Model Finished. Local Said No."](/writing/40-model-done-local-no) covers the guard after execution: log local rejections with their own cause, and do not blame the model. The three together form one chain: decisions pass gates, execution needs authorization, and returned results still get verified once more.
