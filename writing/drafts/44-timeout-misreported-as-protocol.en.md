# The Error Said "Protocol." It Was a Timeout.

> Column: Engineering Log | Collection: Engineering Tools | Source: wiki/bugs/2026-10-17 desktop client login catalog download timeout misreported | Status: Drafted · Upcoming

An error message is not a statement of root cause. It is a label applied by some layer after classification. When debugging, ask three questions first: which layer assigned this error code, what exactly the timeout covers, and how many distinct failures a catch-all merged into one code. Following the message text usually points the wrong way.

## Symptom: Nothing Wrong With the Input, but the UI Says to Recheck It

A desktop client login: the user signed in successfully, reached the key-selection step, and the UI showed "Request incomplete. Please check your input and retry." Four retries on the same page, all failed.

From the user's perspective the conclusion felt natural: the input must be wrong. But the input was fine. The account, the key status, and the ownership relation were all valid. The real problem was neither the input nor the server. It was in the layer that classified the error.

## Three Layers of Evidence: The Server Was Fine; the Classification Was Wrong

**Layer one: nothing abnormal on the server.** The model catalog endpoint finished in under 0.3 seconds server-side, returned normally, and passed all data validation. The server logs showed no error at all.

**Layer two: the time went into delivery.** The server had long finished sending; delivering the response body to the client took about 15 seconds. A single catalog response is hundreds of kilobytes, and on a link moving tens of kilobytes per second, the download alone exceeds 15 seconds. What was slow was not the service, but the leg that carried the large body to the client.

**Layer three: the classification layer rewrote the timeout as a protocol error.** The client's default request timeout was 15 seconds, and it covered not just the first byte but the entire body read. The read layer used a catch-all that converted any exception during reading, including a timeout abort, into a "protocol" error. The UI then rendered copy from the error code, so a network problem was disguised as a protocol problem, and the user could only retry in place.

The three layers together complete the chain: the slow link inflated download time, the timeout covered the whole read, and the catch-all erased the failure's true type. Each link on its own looks like somebody else's problem.

## Debugging Method: Ask Where the Error Code Was Assigned

When an error message points the wrong way, debug in this order:

1. **Who assigned the error code**: was it thrown at the source, or classified by an intermediate layer? Every reclassification loses some of the original information.
2. **What the timeout covers**: a first-byte timeout and a whole-read timeout are two different budgets. Applying a first-byte budget to a whole read of a large body guarantees false kills on slow links.
3. **How many failures the catch-all merged**: if one error code hides timeout, abort, and parse failure, the copy cannot point the right way. Error-code granularity decides whether the first debugging step goes astray.
4. **Compare against a fast link**: the same request succeeding once on a fast link shows the response structure itself is fine. A fast/slow comparison separates a "structure error" from a "time error."

## Three Layers of Fix; Pick the Cheapest One for the Fire

**Root-cause fix (client):** distinguish abort from parse failure in the read layer, mapping timeout aborts to a timeout-class error instead of a protocol error; or give large catalog requests their own, looser deadline instead of counting the catalog download against the 15-second login budget. This is the correct fix, but it means changing code and shipping a release.

**Server slimming (optional):** have the catalog endpoint return only the fields the client consumes, shrinking hundreds of kilobytes to tens of kilobytes. The cost is a change to the interface's semantics, which its original consumers may not accept.

**Stopgap (reverse proxy):** enable JSON compression at the reverse proxy. No code changes, no release. The body shrank from nearly 800 KB to about 65 KB, so even the slow link finished before the timeout; the decompressed content matched byte for byte, semantics unchanged. This is the layer actually used this time.

The three layers of fix are not ranked by merit, only by cost and urgency. When firefighting, stop the bleeding first, then schedule the root-cause fix. And a stopgap must verify that semantics are unchanged, or it just trades one problem for another.

## In Short

When the error says "protocol," don't go check the protocol first. Check where that "protocol" label was assigned.
