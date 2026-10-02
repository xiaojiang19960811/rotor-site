# Calling AI APIs: Beyond "It Works"

> Column: Garden ｜ Collection: AI Infrastructure ｜ Source: wiki/concepts/AI调用可靠性与计费观测 ｜ Status: first draft

An AI call returning 200 doesn't mean the call was healthy. A real call passes through 8 semantic stages — any observability that only tracks "did it work, total latency, total cost" goes blind the moment something breaks.

## Eight semantic stages

1. Request receive and validation
2. User/global concurrency or task queue wait
3. Model routing, account selection, account slot wait, credential refresh
4. Upstream connection and response-header wait
5. First semantic output wait
6. Continued generation, stream reading, or async task polling
7. Completion, failure, cancellation, or client early disconnect
8. Usage parsing, pricing, cost computation, persistence, aggregation, display

A real postmortem proved why stages matter: the final successful attempt's TTFT looked great, but it hid the earlier queueing, failed attempts, and failover — the user's total wait was far longer. A stage without independent records is a stage that never happened.

## Connection alive ≠ semantic progress

An open HTTP connection, a healthy SSE heartbeat, a received `response.created` — none of it means the user got real content. "First valid output" must be defined per protocol as a genuine semantic event: a text segment, a reasoning block, a tool call. Role-only empty packets, empty content, usage events are transport-level heartbeats.

This distinction has real consequences: a first-round request with no semantic output yet can fail over within budget; but replaying the initial request in a stateful later round that only saw leading events can break session semantics or double-bill upstream compute. Stream idle timeout, response-header timeout, first-semantic-output budget, and full generation duration are four different constraints — not substitutes.

## Retries have costs worth recording separately

Every upstream attempt can occupy concurrency and incur compute and cost. Keeping only the final successful attempt underestimates both true cost and failure rate. Auto-retry must distinguish four cases: idempotent reads, re-creatable tasks, non-repeatable external writes, and possibly-billed generation requests — each needs a different retry policy.

A client disconnecting early doesn't mean the upstream stopped either: whether cancellation propagated, whether upstream kept computing, and who bears the cost all need independent observation.

## Billing is an evidence chain, not a formula

Billing must be verified layer by layer: raw usage from the provider → parser keeps raw categories and normalizes → pricing service picks price by model, channel, group, time → billing service splits buckets (text in/out, cache read/write, images, video duration) → usage records keep quantity, unit price, multiplier, currency → aggregation matches admin and user views → production records reconciled against real requests.

Real incidents prove "the formula is right" isn't enough: one cache-write double-billing came from six links (token classification, parsing, pricing, billing, logging, aggregation) not being covered end to end — fixing the formula or the UI alone couldn't close it. One image-output zero-billing came from conflating "empty inherits default price" with "explicit 0 means free" — different semantics. Once, video billing was misclassified as image by the frontend — the display layer must never re-guess a billing mode the backend already stated explicitly.

## Async tasks: creation success is just the start

For media generation, "created" only means the task was submitted, not that media exists or is downloadable. `queued`, `in_progress`, `completed` should be normalized at the adapter boundary without losing raw states and task IDs. Playable in a browser doesn't mean readable by the server proxy; HTTP 200 never substitutes for verifying media bytes and content type.

## In short

Observing AI API calls is one sentence: record by semantic stage, bill by evidence chain. Every queue, retry, and failure hidden behind "eventual success" will reappear in the bill or the complaint.
