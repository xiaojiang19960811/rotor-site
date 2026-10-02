# AI App Security: Filtering Is the Last Step

> Column: Garden ｜ Collection: AI Infrastructure ｜ Source: wiki/concepts/AI应用安全与调用审计 ｜ Status: first draft

Many people's idea of AI safety is one content filter after model output. That's the last step, not the whole story. Complete security auditing covers request content, model routing, identity and permissions, responses, billing, and human review — filtering is just the step closest to the user.

## Auditing is an event chain

One call's audit should link these into a correlatable event chain: caller identity, routed account, model, request type, latency stages, token categories, cost. Only then can you tell apart a malformed user request, an upstream failure, a scheduling problem, or a billing problem when something breaks. Watching only the filter result is watching a photo of the finish line.

Prompt auditing itself can include synchronous blocking, async queues, events, metrics, admin review, and filtered deletion — but it must live inside the existing permission domain. Adding an audit page must never implicitly widen RBAC.

## Prompt snapshots are sensitive evidence

Full prompt or response snapshots are highly sensitive audit evidence: restrict who can access them, how long they're kept, and provide a deletion path. Ordinary business logs shouldn't store full text by default. Needing to debug is not a license to retain complete prompts long-term.

## Errors are not hits: the fail-open vs fail-closed tradeoff

The safety review service failing is a completely different state from "content hit a violation" — the two must never be conflated. Our multi-model gateway made this an explicit policy choice:

- **Observe-only mode**: always lets requests through; review-service errors go to error logs and metrics only.
- **Preemptive blocking mode**: configurable error policy. Fail-open keeps passing requests through on errors; fail-closed terminates the request after all review attempts fail, returning 503 with a fixed user message ("review service temporarily unavailable"), explicitly marked as a retryable service error — never labeled a content violation, never counted toward violation totals or auto-bans.

Infrastructure failures are never recorded as user violations. This is written into the protocol boundary: each entry point uses its own error format but keeps a unified error code in the reason field; audit logs record the true disposition (error-blocked as blocked, error-passed as passed), with the `error` field retaining the service fault itself.

## A real dedup lesson

Dedup of error records had a real incident: clients retried about every 14 seconds after receiving 503, while the existing block-dedup TTL was only 10 seconds — so every retry re-invoked the broken review service and wrote duplicate records. The fix was an independent 1-minute error cooldown covering user key, group, endpoint, and protocol — requests during cooldown still get 503 but no longer re-invoke the service; concurrent first failures use atomic registration so exactly one record is written.

Even "log less while broken" got explicit rules: ordinary hits keep their short TTL, never extended; errors must never be written into the hit cache, or admins would keep getting 503s from stale entries after fixing the config.

## Health checks prove nothing about security

A production health check only proves the service is up. Security and billing conclusions still need real requests, permission boundaries, and end-to-end logs. One healthy 200 proves nothing about any audit link in the chain.

## In short

AI app security auditing is one sentence: every critical event from request-in to response-out is traceable and reviewable; sensitive content is stored minimally and briefly; service failures never masquerade as user violations. Content filtering is the last step — not the first, and never the only one.
