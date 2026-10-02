# When AI Remembers Too Much

> Column: Lab Log ｜ Collection: Agents & Digital Humans ｜ Source: wiki/bugs/digital-human agent interaction memory mis-recall (desensitized) ｜ Status: first draft

A digital-human Agent's memory system once produced a counterintuitive incident: the model assigned 0.99 confidence to all 14 memory candidates, auto-confirmed 11 of them — and human review found all 11 were mis-recalls. Original precision: 0%. Sky-high confidence, zero correctness. Confidence alone can never justify auto-confirmation.

## What happened

A controlled replay ran 5 real, already-replied user letters through the model: all 5 memory-extraction tasks succeeded, producing 14 candidates; the auto-organizer confirmed 11 of them (78.6%).

Human spot-checking gave a blunt verdict: all 11 were one-off task requests, templates, model replies, or "not yet confirmed" process information — none belonged in long-term memory. Not one was a stable preference, factual experience, or reusable relationship fact.

## Typical mis-recalls look like this

- "The user once requested a roundup of recent Shanghai happenings…"
- "In this conversation, the digital human provided a Xiaohongshu copy template."
- "The digital human explicitly stated it had not yet confirmed the latest real-time Shanghai news."
- "Both sides jointly produced one draft and two illustration prompts in this conversation."

See the pattern? Everything describes task process or model output: what was organized, what template was provided, what wasn't confirmed, what draft was produced. They answer "what happened in this conversation," not "who this user is, what they like, or what our relationship is."

## Root cause: process noise, not extraction errors

The root cause deserves its own note: extraction wasn't wrong — the judgment of "what's worth remembering" was. The model faithfully recorded conversation content; the problem is that most conversation content is process noise — one-off task requests, disposable templates, the model's own replies, unconfirmed states. Useful in the moment, polluting as long-term memory.

And 0.99 confidence expresses the model's certainty about "extraction correctness," not "worthiness of long-term memory." Two entirely different questions answered with one number — guaranteed to fail. An auto-confirmation gate looking only at confidence confuses "remembered accurately" with "remembered rightly."

## The fix: gates move from confidence to category

The 11 mis-recalls were soft-revoked with audit records kept. The auto-organizer's bar became twofold: the memory category must be "completed shared experience" or "strictly verified knowledge," AND confidence `>= 0.95`. Task artifacts, model claims, unconfirmed states stay as exceptions or are excluded outright.

Supporting mechanisms went in alongside: 7-day cross-window topic merging, re-review of historical auto-memories, observability interfaces, and human labeling. Two older research auto-memories were soft-revoked under the new rules too.

## What's still open

The 5 replay samples were mostly task-type letters — they don't represent casual chat, explicit personal facts, or ongoing relationship interactions. The wiki lists the follow-up labeling evaluation: build at least 30 multi-type samples, measuring extraction recall, formal-memory precision, exception-queue share, and confidence calibration; if precision misses 95%, tighten categories — never lower the bar.

Whether precision reaches 95% under the tightened bar still needs multi-type sample validation. And whether task requests deserve short-term session memory or no memory at all remains undecided. Tuning a memory system has no finish line — only "good enough under current evidence."

## In short

A memory system's quality gate doesn't block "extracted wrong" — it blocks "not worth remembering." Confidence answers "how sure," category answers "does it deserve memory." Auto-confirmation must check both gates.
