# The Endpoint You Probed Is Not the Path Production Takes

> Column: Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/2026-08-03-sub2api-codex-compaction-originator-503 ｜ Status: first draft

**The conclusion first:** a wave of Codex context-compaction 503s turned out not to be OpenAI's problem at all, but a "capability gate" our own multi-model gateway had added — one stricter than the upstream protocol, blocking requests it should have simply forwarded. The detour before that is the more valuable lesson: a probe against an endpoint returned 200, which briefly convinced us "capability is fine" — but the endpoint probed and the path production takes were never the same protocol.

## Timeline: probe passed, outage continued

On August 3, 2026, our self-hosted multi-model gateway started returning 503s in bursts: whenever Codex clients triggered context compaction (remote compaction), the gateway failed the request. Ordinary chat requests were fine; only compaction-triggered requests broke.

The first troubleshooting step was a capability probe. At 22:01 we ran a compaction-capability probe on the upstream account in the backend; it succeeded, and "account supports compaction" was recorded in both database and cache. Yet real compaction requests at 22:05–22:06 still returned 503, and a minimal reproduction at 22:14 still returned 503.

The probe passed; production kept failing. Four minutes apart, two different things.

## Pinpointing: first, find which layer the request died in

The gateway logs held the decisive clue: the failed requests were recorded at the scheduling stage as "no available accounts," while the failure records had empty upstream account ID, upstream model, and upstream error fields. The request **failed before account selection — it never left the gateway**. Ordinary requests from the same account, same group, and same model were returning 200 at the time.

That bounded the fault to the local scheduling layer, not upstream. Investigation stopped staring at upstream status and turned to the strict capability gate our local fork had added on top of the official remote compaction v2 chain: an OpenAI account had to be both Responses-capable and flagged as compaction-supported before it could serve a compaction request. And that flag's source was the old probe that passed at 22:01.

## The real root cause: the probed endpoint was not the production protocol

The old compaction probe called the legacy endpoint `/v1/responses/compact`; real remote compaction v2 travels over a streaming `/v1/responses` with beta headers and a compaction-trigger parameter. Two different upstream protocols. A passing probe only proves the legacy endpoint is alive — it cannot prove the new chain is capable. Promoting the old endpoint's probe result into an admission ticket for the new chain was the gate's original sin in logic.

The fix was correspondingly decisive: the handler no longer injects a local capability precondition for remote compaction v2; requests are forwarded upstream as-is. The same minimal request used before the release went from 503 to 200; the SSE stream carried the compaction task's creation events, and logs confirmed the request had moved from the ingress side to the egress side with an account successfully selected.

One note on release discipline: this was a production gateway, touched after 22:00. Before release we took a PostgreSQL custom-format backup and validated it, kept the pre-release rollback tag and old images, and confirmed blue-green switchover, container health, and zero fatal-log counts one by one — the same minimal request going from 503 to 200 closed the loop. Troubleshooting courage comes from a rollback button that actually works.

## The detour deserves its own paragraph

Before that, the team walked a well-sourced detour: upstream genuinely has a known behavior of bucketed load-shedding keyed on client identity headers (there is a relevant commit on the official main branch), so the first hotfix was an "identity normalization" that converged a known shed-prone identity into another one. After the release, the same compaction 503s recurred at 21:52 and 21:55 — still dying at local account selection. The experiment falsified that direction, and it was formally ruled out, without anyone insisting "maybe it worked." Fixing the known cause first was right, but a fix has to be read off the data; when the data doesn't support it, concede and change direction.

## Closing

Four reusable disciplines from this outage:

1. **The probed endpoint must be isomorphic to the production path.** Probing the old protocol while production travels the new one makes the probe's 200 worthless.
2. **When you proxy, don't invent gates stricter than upstream.** A gateway's job is faithful forwarding; every locally invented admission condition will eventually block a request that should have passed.
3. **Pinpointing starts with "which layer did it die in."** An empty upstream account ID is the cheapest scoping evidence there is.
4. **Own your falsified experiments.** Fixing the known cause and missing is not wasted work — it ruled out an option, and a ruled-out option is progress.

"Probe passed" is only responsible for the path that was probed.
