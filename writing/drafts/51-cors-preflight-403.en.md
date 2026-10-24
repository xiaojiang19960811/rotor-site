# A 403 on Preflight: Check CORS in Three Separate Stages

> Column: Lab Log ｜ Collection: AI Infrastructure ｜ Source: wiki/concepts/AI canvas + multi-model gateway, 2026-10-24 CORS preflight fix record (desensitized) ｜ Status: drafted · coming soon

Conclusion first: when a browser's cross-origin call to an image-generation endpoint failed, the 403 came from the preflight, not from authentication. Before sending the actual request, the browser first sends an OPTIONS preflight asking "is my origin allowed across origins?"; if the preflight is refused, the actual request is never sent, and the key's correctness or the model's state never even gets asked. The root cause was that the current production slot's CORS allowlist was not configured: with an empty allowlist, the application layer refused every preflight outright.

## The Failure: It Happened Before the Request

The AI canvas project's frontend called the multi-model gateway's image-generation endpoint across origins, and the call failed. The first instincts point in two directions: the key must be wrong, or the reverse proxy must be blocking it. But both directions assume "the request already reached the server and was processed" — and when a preflight fails, that premise does not hold at all.

The single decisive piece of evidence: bypassing the reverse proxy and sending OPTIONS straight to the application also returned 403, and the startup log explicitly said the CORS allowlist was empty. The reverse proxy was not on this path, and neither was the key. The problem was the application layer's allowlist configuration itself.

One easily overlooked point: the preflight is sent automatically by the browser; the frontend code never explicitly issues that request. So frontend logs usually show only that the call failed, not which stage failed; you have to find that OPTIONS request in the browser's network panel, or reproduce the preflight directly from the command line, to pin down "which stage". A request you cannot see has to be actively hunted down.

## Definitions: Three Checks, Three Different Questions

One cross-origin call contains three checks, each answering a different question. Mixing them up only lets them cover for each other:

| Check stage | Question it asks | This incident's answer |
|---|---|---|
| Preflight | Is this origin allowed across origins | 403: empty allowlist, origin not on the allowlist |
| Actual request | Are the credentials right, is there permission | Never reached; after the fix, a keyless request returned 401 with correct CORS headers, proving it had entered the auth flow |
| Health check | Is the service alive | Healthy inside and out; the production slot running and healthy |

A healthy health check only proves the service is alive; it proves nothing about CORS allowlisting. A passed preflight only proves the origin is allowed; it proves nothing about authentication. Each piece of evidence answers only its own question and cannot stand in for another. That is the one lesson most worth taking away: **split the stages first, then locate the fault**.

## Three Misjudgments

1. **Treating a preflight 403 as an auth failure**: the preflight carries no business credentials, so its 403 has nothing to do with the key. The real signal for "entered authentication" is a 401 on the actual request: refused for lack of a key, but carrying correct CORS headers, which shows the request had passed the CORS layer and reached the auth layer. A 403 and a 401 look alike; they live on entirely different layers.
2. **Blaming the reverse proxy when a direct connection also fails**: bypassing the reverse proxy and still getting 403 is precisely what rules the reverse proxy out. In troubleshooting, "bypassing a layer changes nothing" is not wasted work; it is the evidence that makes the elimination valid: the bypassed layer is not where the root cause sits.
3. **Assuming a new run directory inherits the old one's allowlist**: a historical allowlist belongs to the old run directory and says nothing about the new run directory's effective state. Configuration travels with the run directory; switching slots does not inherit it automatically. The same applies to blue-green slots: when falling back to the standby slot, its CORS configuration must be verified separately — never assume it shares this change.

## The Fix: Change One Place, Keep a Way Back

The fix touched only the current production slot's configuration: the canvas frontend's origin was added to the allowlist, credentialed requests were allowed, and the slot was restarted. The image, the code, the reverse proxy, and the database were all untouched. The original configuration was backed up first, so rolling back means restoring the backup and restarting the slot — one step, done.

But the verification boundary of this fix must be stated plainly: verification reached "the target origin's preflight returns 204 with a precise allow-origin, an untrusted origin's preflight is still 403, actual requests can enter the auth flow, and health checks are normal." Real image generation is not yet verified: a passed preflight does not mean generation succeeded, just as a healthy health check does not mean CORS is allowed. Each layer only vouches for its own evidence, and an item marked "pending verification" on the checklist must not be crossed off early.

## Release Checklist: Two Additions

This postmortem adds two mandatory checks to the release checklist:

1. **Preflight with the real browser origin**: never verify with the same-origin health endpoint alone. The health endpoint is same-origin reachable and never exercises CORS logic, so checking it cannot expose an allowlist gap.
2. **Check the actual response headers**: the preflight response must carry the precise allow-origin, and actual-request responses must carry correct CORS headers. Status codes alone are not enough; the headers are the evidence that CORS allowlisting is actually in effect.

## Closing

Next time a cross-origin call fails, ask first which stage failed: preflight, auth, or health. Once the stages are separated, an allowlist gap, a key problem, and a service outage stop taking the blame for each other.
