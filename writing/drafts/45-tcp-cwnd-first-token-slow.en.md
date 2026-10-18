# A Slow First Token Doesn't Mean a Slow Model

> Column: Engineering Log | Collection: Engineering Tools | Source: wiki/bugs/2026-10-18 Multi-Model Gateway First-Token Slowness After Model Switch | Status: Drafted · Upcoming

A case where the first token went from 4 seconds to 60 seconds after switching models. The root cause was neither model inference nor gateway forwarding — it was a congestion window pressed to 3 MSS by CUBIC inside the container's network namespace. When the first token is slow, first ask where the time went before the first byte arrives; don't reach for a model swap or a routing change.

## The symptom: same context, 10x slower first token after a model switch

The same old session: switching from model A (channel A's route) to model B (channel B's route) with roughly 260k tokens of history in both cases. First token in 4.4 seconds on model A; 47–81 seconds per round on model B — and once the first token arrived, the rest streamed out fast.

The slowdown was triggered by the act of switching models, which naturally looks like a model problem. But note the anomaly: fast output after the first token. Slow inference and slow first token are two different things; when the first token is slow, audit the road before the first byte.

## Four pieces of evidence: the time went to uploading, not inference

**Piece 1: timing alignment.** The gateway logs show comparable context sizes on both sides but first-token times an order of magnitude apart. Within one request, total time minus first-token time was only 1–5 seconds: the model was not slow at producing tokens; all the time went to the period before the first upstream byte arrived.

**Piece 2: size buckets.** First-token time on the same channel scaled almost linearly with context size: under 20k tokens ~4s, 20–60k ~8s, 60–150k ~21s, 150–250k ~42s, 250k and up ~62s. Small requests fast, large requests slow — the "transport" stage was slow, not inference.

**Piece 3: direct-connection comparison.** The same ~1MB request body took 7–14 seconds sent directly to the upstream channel, but 55–65 seconds when forwarded through the gateway. The upstream was not slow; the gateway's outbound leg was.

**Piece 4: packet capture conviction.** Capturing inside the container's network namespace: uploading the 1MB body took ~55 seconds, and the first response byte arrived 4.7 seconds after the upload finished. Connection state showed CUBIC, a window pressed to 3 MSS, ~200ms RTT, ~12% retransmission, measured throughput 64KB/s. Verdict: the "slow first token" was really a slow request-body upload.

## Two layers of root cause: a jittery link, plus the wrong default algorithm on the gateway

**Layer 1: the link was jittery to begin with.** From the overseas server hosting the gateway to this channel's network, ping round-trip was ~150ms with 5–10% packet loss. CUBIC crushes the congestion window to the floor under heavy loss and climbs back slowly; 1MB under such a window takes over 50 seconds to upload.

**Layer 2: the container netns still ran default CUBIC.** Linux's `tcp_congestion_control` takes effect per network namespace: the host had BBR enabled, but the Docker container's namespace still ran CUBIC. More subtle still: after changing the container netns's algorithm to BBR, existing reused long-lived connections kept the old CUBIC; the old connections had to be killed (with no in-flight requests) before new connections picked up the new algorithm. Many people enable it on the host and think they're done — they've changed the light in another room.

Why did the model switch expose it? The old model went through channel A, whose route was fine — 260k tokens still got a 4.4s first token. The new model went through channel B, and the jittery-link-plus-tiny-window combination surfaced. The model switch only changed the road; the road itself wasn't slower than before.

## The fix: enable BBR, kill the stale connections

1. Enable BBR on the host and persist it.
2. Enable BBR separately inside the container's netns (via nsenter into the container's network namespace).
3. Kill the established old connections to that upstream so new connections use the new algorithm (only after confirming no in-flight requests).

Re-verified: the same 1MB request through the gateway went from 55–65s to 10.3s; real large-context traffic went from 40–62s to the 8–20s range, approaching the 7–14s of a direct connection. The congestion window grew from 3 MSS to over 700. Boundaries recorded honestly: BBR's fairness impact on other cross-border traffic was not evaluated; the change was limited to the host and this container's netns.

## Conclusion

When the first token is slow, first subtract first-token time from total time to remove inference, then pin the slow segment with three steps: size buckets, a direct-connection comparison, and a packet capture. And for any network tuning inside containers: check which netns it lives in first.
