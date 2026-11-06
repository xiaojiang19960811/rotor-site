# Whether a Broken Stream Retries Depends on How the Error Is Worded

> Column: Experiment Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/2026-10-17 upstream stream interruption and client retry policy at a multi-model gateway (desensitized) ｜ Status: Drafted · Upcoming

Conclusion first: whether a streaming conversation retries automatically is not decided by the failure itself, but by how the error is worded. Between the evening of October 16 and the early hours of October 17, 2026, four conversations on the same desktop client ended with "this round failed," reporting "upstream response stream was interrupted." The gateway's 72-hour logs contain only 7 stream read errors in total, and 4 of them line up one-to-one with those four failures. The network was fine, and the account pool had not collapsed. The real fault sat between the two layers: the error wording the gateway produced did not fall inside the client's retry allowlist.

## Four Failures, Three Upstreams, One Wording

The four failures happened at 20:55 and 23:13 on October 16, and at 00:24 and 00:31 on October 17, all from the same desktop client and the same gateway account group. The gateway logs show only 7 stream read errors across roughly 136,000 lines in a 72-hour window, and all 7 happened after partial content had already been written to the client. What the far end did differed each time: one third-party channel reset the connection mid-stream, an official API reset it, and another closed cleanly but without a terminal marker. Three different upstreams, three ways of breaking, and in the user interface they all collapsed into one sentence: "upstream response stream was interrupted."

That collapse into one sentence is the problem. The gateway's error classification only distinguishes two cases: a clean close returns "stream ended before completion," and every other read error returns "stream was interrupted." The client's retry decision is a wording-match list: only wordings containing "stream ended," "network/connection," "other side closed," or "premature close" count as retryable transport errors, and the default policy retries only five error classes — "stream was interrupted" is not among them. So the same kind of failure meets a completely different fate depending on its wording: the clean close gets retried automatically and the user never notices, while the mid-stream resets fail the whole round and the user sees "it always breaks."

## Once Streaming Output Starts, There Is No Transparent Retry

There is a second constraint that cannot be worked around: before reporting the error, the gateway had already written partial content to the client. Half an answer was already on the user's screen. At that point the gateway cannot quietly switch to another upstream account and stitch the second half on — continuations from two upstreams do not join together, so a retry can only mean starting the whole round over. "Transparent retry" only exists before the first token is output; once output has started, the price of retrying is making the user wait for a full answer again.

And the price is not only time. A retry is a new upstream request, billed again under the upstream's rules. If one interruption triggers five retries, the worst case is paying six times for the same question. If a retry policy does not state "how many retries at most, how long between them, and what to tell the user when they run out," it is not a policy — it is just a wish that says "try again on failure."

## The Fix: Add the Missing Error Class to the Allowlist

That night's fix touched no production code and changed only the client configuration: the "upstream error" class was added to the retry allowlist, with backoff — a 1-second initial delay, a 30-second cap, and 20% jitter. The configuration passed syntax validation, and its keys matched the retry policy's definition. But the configuration only takes effect after the client restarts, and no restart happened in this round; the gateway's wording was not changed either. In other words, the root cause is located, the fix is written, and the verification has not happened yet.

The open list was written into the postmortem as well: after the restart, how many times does it actually retry, will failures still come in runs, and how much does each retry cost; whether to repair one long-unusable account in the pool, and whether to lower the priority of the channel that keeps breaking; and whether to reword the gateway's error into transport semantics so the default policy retries it too — rewording would depart from the upstream's original message, and that trade-off is still undecided.

## Practice: Error Classification Is a Cross-Layer Contract

1. **Error classification is a cross-layer contract, not each side writing its own wording**: when upstream and downstream align by string matching, the wording is the interface. When the gateway changes one error sentence, the client's retry behavior changes with it. A wording change deserves an interface-change review: who consumes this sentence, what are the matching rules, and which errors enter or leave the allowlist after the change.
2. **Retry eligibility should follow failure semantics, not wording**: whether something is retryable should be a structured error code or classification field, not a regex over the error text. Text is for humans to read; classification is for machines to decide. Tie the two together, and every edit to a human sentence changes machine behavior.
3. **For streaming output, the dividing line is "already output"**: before the first token, a retry can silently switch accounts; after the first token, it can only start the whole round over. A retry policy must be written separately for the two sides of that line: before it, how to switch; after it, how to tell the user, and whether to restart automatically at all.
4. **Retries must be costed**: every retry is a new billable request. The retry budget — count, interval, total cost cap — belongs in the policy, on the same sheet as "how long the user waits at most." Otherwise one upstream wobble becomes a bill six times the size, and the bill never shows which lines were retries.

## One Line to Close

Whether a broken stream retries does not depend on how badly it broke, but on whether the two layers agree on "what kind of error this is"; error classification is a cross-layer contract, and when the wording changes, retry behavior changes with it — so check the list that consumes the wording before changing it.
