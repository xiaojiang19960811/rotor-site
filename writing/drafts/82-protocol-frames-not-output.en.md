# Protocol Frames Are Not Output

> Column: Lab Log | Collection: AI Infrastructure | Source: wiki/bugs/2026-08-07 gateway upstream overload transient failover (desensitized) | Status: Drafted · Coming soon

Conclusion first: when upstream says "Our servers are currently overloaded. Please try again later.", that is not an ordinary failure. It is a transient error that should trigger a switch to another account and a retry. The gateway returned it as a plain failure, for three reasons: the transient-error matcher did not recognize that exact wording; the failure-event ordering let the generic rule fire before failover; and empty structural events arriving early in the stream were treated as real output, closing the swap window before the failure arrived. After the fix, the swap decision changed: it no longer asks "have we written any protocol frames", it asks "have we written real semantic output".

## What happened: one error message, the wrong path

A user report showed the upstream sentence "Our servers are currently overloaded. Please try again later." still coming back as a plain failure. Three entries were affected: plain HTTP requests, the Chat and Responses compatibility layer, and failover on failure events in streaming responses. The same wording was already covered in the WebSocket path's mapping, so the gap was not in status-code mapping: it was in the transient check shared by HTTP and streaming. The rules were written per entry, so one missed entry meant one missed path.

## Three layers of root cause

1. The matcher was incomplete: the transient check covered processing, capacity, server overload, and slow-down wordings, but did not explicitly include the sentence "Our servers are currently overloaded". Rules maintained by enumeration miss one every time the vendor phrases it differently.
2. The ordering was wrong: when upstream reports overload with a failure event in a stream, the generic passthrough rule could commit the failure event before the failover rule ran. Correct classification is not enough: with the wrong order, the right branch never gets its turn.
3. Empty structural events took the slot first: upstream sends structural events such as output_item.added and content_part.added early in a stream. They carry no real tokens; they are protocol scaffolding. But the gateway wrote them out as client output. By the time the real overload failure arrived, the response had "already started", and the swap window was closed.

The third layer deserves a closer look: the gateway used "have we written anything to the client" to decide whether a swap was still possible. Protocol frames count as "something", so a few empty shells blocked the way.

## The fix: four changes, one new yardstick

1. Two new matches in the transient check: the full overloaded sentence, and the combination of "please try again later" with "overloaded".
2. Reordered failure handling: overload, capacity, and rate-limit errors enter failover first, and generic passthrough is considered only after.
3. Delayed submission of empty structural events: they count as the first real output only when they carry real payload.
4. The swap decision now reads a new marker: whether real semantic output has started. Protocol scaffolding, SSE keepalives, and empty structural frames do not block a swap; only real output, text deltas, tool arguments, image results, stops it.

The first three are patches. The fourth is a new yardstick: keeping a denylist of "which structural events count as output" only grows longer, so ask the direct question instead: has anything real been written yet.

Two more anti-recurrence measures are worth noting: the long-term strategy is to judge whether real semantic output has started first, rather than keep enumerating protocol structural events; and the WebSocket path keeps its own status-code parsing, so a single wording is not fixed in only one entry: fixing one place is not fixing all of them.

## Verification and boundaries

Regression tests cover three points: the overloaded wording is recognized, failure events take failover first, and a swap still works when overload arrives after empty structural events. The fix shipped in a blue-green release; in the 90-second observation window after release, the overloaded error, the forward-failed marker, and crash-class logs did not reappear.

Two boundaries need stating. First, the first release itself went wrong: a manual build missed the flag that embeds the frontend, and the homepage returned 404 until the same version was released a second time through blue-green. The release that fixed failover had to go through its own failover process. Second, real upstream overload responses still appear after the release: the fix is about recognizing them, not about making upstream stop overloading. Upstream capacity problems will keep happening, but now they enter the transient path instead of returning as plain failures.

One loose end remains: if real output has already been written and overload arrives after it, the stream can only be terminated in place with the failure event; a seamless swap is impossible. That is a hard boundary of the swap mechanism, not something the next patch can fix.

One line to close: to decide whether a swap is still possible, don't count protocol frames written. Ask whether anything real has been written: if not, swap; if yes, accept it.
