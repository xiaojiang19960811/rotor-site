# The Model Finished. Local Said No.

> Column: Garden ｜ Collection: Agents & Digital Humans ｜ Source: wiki/concepts/AI调用可靠性与计费观测 ｜ Status: Draft

**Conclusion first:** A full model response is one thing; whether the results may ship is another. A full response, passed business checks, still-valid execution ownership, and reconciled billing are four conclusions that cannot substitute for each other. If any one of them fails, the local layer must have the courage to say no — and must own the reason itself, not blame the model or the gateway.

## Four Conclusions, Each Speaks for Itself

When an agent call finishes, four questions sit in front of you:

1. **Full model response**: stop normal, end frames complete, usage data present — a transport-layer fact.
2. **Business checks passed**: the content follows business rules and did not drift — a business-layer fact.
3. **Execution ownership still valid**: the task's ownership (user, space, authorization lease) did not lapse or change during execution — a permission-layer fact.
4. **Billing reconciled**: usage recorded, pricing source clear — an accounting fact.

The first being true says nothing about the second; the second says nothing about the third. Each layer has its own evidence and its own guard. Treating "the results came back" as a universal pass means letting the transport layer vouch for the permission and billing layers — and it has no authority to do so.

## A Real Case: Complete Response, Ownership Gone

Source: knowledge-base record from 2026-10-11, an offline validation in an agent project.

The scenario: a complete call finished, the model returned full results, business checks passed. But the ownership review before local publishing found the task's execution ownership had changed: the authorization lease's scope no longer matched what it was when execution started. By the rules, the publish ban still stood — this batch could not ship.

Two mistakes are easy here, one more common than the other:

- **Letting it through because the model finished.** The results are already out — blocking them now looks like waste. But ownership is a security boundary, not decoration. Business checks only prove the content is fine; lapsed ownership proves this content is no longer yours to ship. Ship it, and at best billing won't reconcile; at worst you've published across your authorization boundary.
- **Logging the rejection as a model or gateway failure.** Writing "model call failed" or "gateway error" in the logs. That pollutes observability: the model and the gateway did their jobs fine — it was the local authorization layer that said no.

The handling rules established in that record:

- Keep the existing transport diagnostics untouched: stop reasons, end frames, usage data. They prove the model did complete.
- Record the local rejection cause separately (e.g., ownership changed), report it up through the orchestration layer, and do not trigger the interruption-compensation flow.
- A local rejection is a local rejection. Do not attribute it to the model or the gateway.

## Name the Blame Correctly

Why does this deserve its own article? Because "a complete response" is deeply deceptive. A transport layer glowing green relaxes the human; a guard blocking the shipment looks like waste.

But honest attribution is the first requirement of observability: whoever a failure is recorded against determines where the next fix goes. A local authorization rejection recorded as a gateway error sends the next investigation to the gateway, while the real ownership-renewal logic never gets fixed. Naming the blame correctly sounds like a moral issue; it is actually an efficiency issue.

## How to Log a Local Rejection

Logging has its own discipline. A correct local-rejection record carries at least three parts:

1. **Preserve upstream evidence verbatim**: stop reasons, end frames, usage data, untouched. Future readers must see at a glance that the model finished its part.
2. **Local cause in its own field**: which local guard rejected, by which rule, what ownership state was observed. Never mix it into the same field as upstream diagnostics.
3. **State the next action**: retry ownership renewal and ship, discard permanently, and who decides. A log without a next action delegates the decision to the next person debugging.

This style has a side benefit: when the upstream genuinely fails (say, a gateway timeout), the logs read the same way, and nobody has to guess "who actually reported this failure."

## Relation to the Previous Article

Article 36 covered the three gates before execution: the model only proposes plans; anything with side effects passes the gates first. This article is its mirror image: the guard after execution is just as necessary. A plan is a proposal; execution needs authorization; and after the response arrives you still ask once more — "can you still afford to ship this?"

An agent pipeline has guards on both ends. Lose either one, and no amount of strictness on the other can compensate.
