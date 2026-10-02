# Nine Minutes for the First Token

> Column: Lab Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/multi-model gateway first-token timeout retrospective (desensitized) ｜ Status: first draft

The most counterintuitive finding from a gateway timeout retrospective: over 95% of a slow request's time sits before the "first meaningful output." Once the first token arrives, the rest usually finishes fast. So timeout budgets shouldn't be set on total elapsed time — they should be set on first meaningful output. Tuning timeouts against total time tunes the wrong metric.

## The phenomenon: the first token decides everything

Production saw minute-level time-to-first-token (TTFT). Pulled apart, slow samples share one shape: first-token latency eats 95%+ of total time; once it lands, completion follows quickly. Upstream had a sample with 9m19s to first token out of 9m32s total — of nine minutes, nine minutes nineteen seconds waited on a single character.

That shape dictates the budget design: if 95% of time goes to the first token, a "10-minute total timeout" rule barely catches anything. What must be caught is the request that never produces its first token.

## Two traps that mislead

**Trap one: keepalive fixes a different kind of death.** An upstream fix handles HTTP/2 connections with zero frames: PING after 15 silent seconds, recycle after 15 more without ACK. But it can't touch our long tail — connections alive, PING ACKs and SSE keepalive frames flowing, yet no first meaningful output for ages. Blaming "the keepalive fix didn't work" points the wrong way: the connection isn't dead; the semantic output just never came.

**Trap two: a hidden WebSocket pre-downgrade wait.** The retrospective found another layer: after WS failure, the client reconnects several times before falling back to HTTP — a wait invisible to normal HTTP usage stats and unconstrained by the HTTP first-output budget. Reading only HTTP-side logs shows a stretch of "missing" time hiding in the WS downgrade chain.

## The budget rules that shipped

The confirmed rules are live, built on three budgets:

- 90 seconds max per single attempt on one account;
- at most 1 account swap on that timeout;
- 180 seconds total budget from first forward, covering account selection, concurrency-slot waits, token refresh, the swap, and the second attempt.

Once the first real text, reasoning, or tool output appears, budget limits lift — slowness after that is normal generation time, not a first-token problem.

Paired with a critical definition: what counts as "meaningful output." `response.created`/`in_progress`, SSE comment heartbeats, role-only frames, empty content, `usage`, and termination events don't count. Only real text, reasoning, or tool output does — otherwise one heartbeat frame could extend the budget forever and the gate means nothing.

Neutral keepalives may go downstream before timeout, but must never block internal failover — keepalive soothes the client; failover protects the system. Two different jobs.

## Still under observation after launch

The budget rules have shipped to production, but the retrospective isn't closed. The wiki's open items are honest: keep watching TTFT distribution, budget trigger counts, swap success rates, and actual internal failover effects across time windows; whether to grayscale-disable the WS pre-downgrade or bring it under server-side budgets remains undecided.

That matches the evidence view from the verification article: shipping proves "the rule is deployed," not "the problem is solved." Whether budgets truly catch the long tail shows in continuous production data, not in a successful release.

## Split into stages when debugging

The retrospective left practical triage advice: never stare at total time. Split a request into three stages first — before first token, after first token, routing/upstream. If a slow sample carries status frames or heartbeats, don't chase the keepalive direction; if HTTP-side timing doesn't add up, look at the WS pre-downgrade chain.

## In short

First-token latency is the most honest health metric in gateway scenarios: everything before it is waiting, and all of it is risk. Put the budget on first meaningful output, not total time — aim at the right place, once is enough.
