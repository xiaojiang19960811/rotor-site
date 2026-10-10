# The Model Only Proposes Plans: Three Gates for Agent Side Effects

> Column: Knowledge Garden ｜ Collection: Agents & Digital Humans ｜ Source: wiki/concepts/Agent执行编排与外部副作用边界 ｜ Status: First draft

**The short version:** When agents fail, it almost always happens between "planning" and "execution". The model proposes a plan, and the system treats it as a license to execute. The boundary that actually works: plan generation, path completion, node execution, and external writes are four distinguishable stages. The model is only allowed the first one; anything with a side effect must pass three gates: explicit declaration, authorization, and recoverable persisted state.

## Four stages, each minding its own business

An agent that can work autonomously needs at least four internal stages:

1. **Model planning**: parse the user's intent and propose candidate capability nodes and goals, without executing any external action directly.
2. **Path completion**: the orchestrator fills in the missing intermediate steps according to capability contracts, and may only fill in side-effect-free intermediate nodes.
3. **Node execution**: run the DAG by dependency readiness, resource locks, and pause/resume/cancel rules, with every node result traceable.
4. **Side-effect writes**: notifications, creation, publishing, and external system calls are handled by dedicated handlers, and later nodes advance only after the real result is confirmed.

Why split the stages? Because the "evidence" differs at each stage: a correct plan does not mean a complete path; a complete path does not mean successful execution; a node showing success does not mean the user actually received the result. Without stage separation, you cannot even locate which link broke when something fails.

## A plan is not a license

The most dangerous misunderstanding: the model writes "send a Feishu notification" in the plan, and the system treats that as permission to send.

Three formal boundaries:

- External actions in a model plan are proposals only. Notifications, creation, publishing, writes, and deletes must be explicitly declared by the model plan, then pass authorization and state gates.
- Capability-path auto-completion may only fill in deterministic, side-effect-free intermediate nodes with input/output contracts. It may not invent notification, creation, or publishing nodes out of thin air.
- Capability registries and authorization checks may not be bypassed with natural-language regexes or hard-coded node names. What the plan says matters less than whether the registry has the capability and the user authorized it.

In other words: the model's authority ends at proposing; execution authority sits with the orchestrator. This is the most basic "distrust" of the model, and the cheapest insurance in the whole agent system.

## Three gates for side effects

Anything that leaves an external trace — sending notifications, creating content, publishing, writing data, deleting data — must pass three gates:

**Gate one: declaration.** Side effects must be explicitly declared in the model plan. No declaration, no execution. Vague intent (like "and create something while you're at it") must be classified into an explicit creation node during intent recognition, not guessed by a later review pass.

**Gate two: authorization.** After declaration, verify each item: does the capability registry have this capability, did the user authorize it, are the node's inputs, outputs, and dependencies correct? Unknown capabilities may not be downgraded into approximate tasks and run anyway; the review pass fixes structural errors a limited number of times, and if it cannot be fixed, it fails. Never run it hard.

**Gate three: recovery.** The easiest gate to overlook. Pause, resume, cancel, retry, and process restarts must be based on persisted execution state to avoid duplicate side effects. An asynchronous external task may not be marked successful before it really completes or explicitly fails, and final URLs or delivery results may not be fabricated.

Gate three has a corollary: for any side effect that cannot be made idempotent, plan the failure story before executing. Retrying three times and sending three notifications is worse than not retrying.

## Real case one: Feishu only delivered the first result

Source: knowledge-base bug record, 2026-08-27, digital-human agent project.

A user asked to look up news on two singers and send it via Feishu. Both research nodes completed, the Feishu delivery status showed sent, but the actual message only contained the first singer's results.

The root cause was on the execution side: the Feishu handler waits for all dependency nodes to complete, but only read the first dependency when assembling the summary and sources. Every node status was completed, the send status was success — every light was green, but the user received incomplete content.

That is the price of "only looking at status": the tests asserted the send status but never asserted the user-visible body and source set. The anti-recurrence rule established after the fix: regression tests for multi-input delivery nodes must assert three levels at once — dependency waiting, the user-visible body, and the source set — not just the send status.

## Real case two: a vague creative intent got dropped

Source: knowledge-base bug record, 2026-09-17, digital-human agent project.

A test message said: "find me some information and send it to me on Feishu — oh, and create something while you're at it." The research and the Feishu notification completed, but the creation step was never generated.

The confirmed cause: the intent-recognition rules did not specify that "create something" counts as a creation directive, so the review pass accepted a plan containing only research and notification. Keyword fallbacks only cover parameters like image output; they cannot replace intent recognition.

The fix was to state it explicitly in the intent-recognition and review rules: "create something" style expressions without a specified medium must keep the creative intent and land on an explicit creation node, plus a regression test.

The two cases map exactly onto gate one and gate three: one dropped intent at the declaration stage, the other checked status without checking results at the confirmation stage.

## Tests must be verified per stage too

Tests for execution orchestration cannot only verify the Planner's output. They must cover separately: capability paths, authorization rejections, dependency failures, resource-lock contention, node recovery, the real state of external handlers, duplicate submissions, and the final user-visible results.

Mocks can verify UI and orchestration shape, but they cannot replace end-to-end verification against real external systems. This complements [No. 9, "Done" Is Not "Verified"](/writing/09-done-vs-verified): that piece explains which verification results support which release conclusions; this piece explains what may execute and when side effects happen.

## In short

The model proposes plans; the orchestrator guards the boundaries. Planning, path completion, execution, side effects — four jobs, four stages; side effects pass three gates: declaration, authorization, recovery. When you meet an agent, the first question to ask is: which gates do its side effects pass through? If no one can answer, put a question mark on its autonomy.
