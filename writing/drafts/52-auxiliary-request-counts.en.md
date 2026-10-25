# One Message, Two Usage Records: Auxiliary Requests Count Too

> Column: Lab Log | Collection: AI Infrastructure | Source: Desktop agent client, 2026-10-22 title auxiliary-request verification (desensitized) | Status: Drafted, pending publication

Conclusion first: when a greeting in a new session produces two records in the gateway usage list, it does not mean the request was retried, nor does it mean you were double-charged. The second record is a title request the client sent on its own: giving the new session a title. The main reply and the title are two requests with different purposes, and each counts as one. Any request a client sends on the user's behalf must be counted in usage, cost, and reconciliation; a request you cannot see is the easiest to mistake for an anomaly.

## What happened: one greeting, two records

The verification used two new sessions, each sending only one greeting. Both sessions left two records in the gateway usage list: one for the main reply, one for the auto-generated title.

The order is the key detail. In the first session, the main reply finished first and the title finished later; in the second session, it was the other way around. The title and the main reply run concurrently, so their finishing order is not fixed.

Seen only from the gateway usage list, the two records look very much alike: the same time window, the same account, the same model. It is easy to read them as "sent once, recorded twice" or "the request failed and was retried." But in the local session log, the two records correspond to different events: one main-reply event, one title-generation event. Different purposes, separate records — that is normal, not an anomaly.

A title request has another layer of invisibility: the user never clicked it. The interface shows only the greeting and the reply, plus the session title that appears afterwards — it never shows a step saying "generating a title for you." With no visible counterpart in the interface, an extra record on the bill naturally reads as a system error. A request that cannot be seen is the hardest to account for; that is why the existence of auxiliary requests belongs in the product description, not in an answer given only after the user asks about the bill.

## Definitions: three kinds of records, kept apart

Before reconciling, separate three kinds of records. Count them together and they will never add up:

| Record | What it is | How to recognize it |
|---|---|---|
| Main request | The reply to the message the user sent | The one call that directly serves the user |
| Auxiliary request | A request the client sends automatically, in the user's service | An auto-generated title is one example: the user did not send it, the client sent it for the user |
| Retry | The same request sent again after a failure | The same purpose, the same request, sent a second time |

The test is not the count, but whether it is the same request for the same purpose. A title request has a different purpose from the main reply: one answers the user, the other names the session. So the title record is not a retry of the main reply.

Likewise, two usage records do not by themselves prove a double charge. A usage record is one input to billing; whether something was charged twice depends on the billing rules, and the count alone cannot settle it. But the reverse does not hold either: an auxiliary request that went through the gateway and entered usage must appear in the cost ledger.

## Method: reconcile by purpose first

1. **Look at local events, not only the gateway list**: the gateway list tells you "how many," the local session events tell you "what each one was for." Reconciliation starts from purpose, not from count. Anyone who only counts records will treat an auxiliary request as an anomaly.
2. **Do not use order as evidence**: which finishes first, title or main reply, is not fixed, and concurrent requests have no fixed order. Order cannot prove which was the original and which was a retry; inferring cause from order is the most common leap in reconciliation.
3. **State the scope of the conclusion**: this verification covered only two new sessions, and the conclusion is limited to that: a new session's title request produces an independent usage record. It cannot be generalized to "every round of dialogue always adds one record," nor to other clients' title mechanisms. What was not verified does not go into the conclusion.
4. **Put auxiliary requests in the cost ledger**: auto titles, auto summaries, auto suggestions — every request a client sends automatically on the user's behalf should be listed first, before talking about the cost of a single conversation. A cost model that counts only the main reply underestimates by construction; when the bill shows one record more than the model, the user's first suspicion is "overcharged."

## Closing

When the usage list shows one record more than expected, first ask "who is it for, and what is it for" — not "was I overcharged?"
