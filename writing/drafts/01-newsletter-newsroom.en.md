# News Briefings: Machines Do the Work, Humans Hold the Gate

> Column: Build Notes ｜ Collection: Multi-Platform Business ｜ Source: wiki/concepts/AI资讯简报人机协作与质量门禁 ｜ Status: first draft

For AI-generated news briefings, the division of labor isn't decided by "what the machine can do" but by "who is accountable when it's wrong." Discovery, triage, and formatting go to machines; source verification, business judgment, and final publishing stay with humans. Model output is material pending review, not a semi-finished product — nothing goes out until source, date, provenance, and business impact have all passed human review.

## A three-stage pipeline

Briefing production splits into three stages, each with a different owner:

1. **Discovery and collection**: a fixed RSS whitelist covers routine sources; a large model does open discovery. RSS reads only whitelisted feeds, never article bodies; model-discovered candidates must carry precise citations, and the program never fetches cited pages or stores full text.
2. **Triage and assembly**: unified dedup and first-pass filtering produce at most 10 items pending review. Impact analysis follows an "affected business, affected stage, watch today" structure, each item labeled "AI analysis, needs human review."
3. **Human verification and sign-off**: a human keeps, verifies, and approves a snapshot before anything is pushed. Pushing is a separate action: only content whose hash has been approved may go over the network.

"Automatic collection/assembly" and "automatic publishing" are two independent authorization boundaries. A scheduler may generate a pending draft every day, but automatic approval, automatic sending, and automatic retry on failure are all prohibited.

## Six quality gates

1. **Source gate**: citations must resolve to public sources; regulatory, judicial, and legal items go back to the official original for verification.
2. **Date gate**: a matching headline is not a matching date; each candidate's publish date must fall inside the target window.
3. **Content gate**: summaries must not exceed the source; model-generated business impact stays "pending review" and never becomes a handling decision on its own.
4. **Role gate**: only items tied to the role's business scope are included; general industry news doesn't get in on hype.
5. **Volume gate**: fewer than 10 items — or an empty result — is allowed; weak filler must not pad a fixed layout.
6. **Continuity gate**: one clean day only proves the pipeline runs; stability is judged over consecutive days of false positives, misses, dates, and citation quality.

The volume gate is the most counterintuitive: when nothing qualifies, the correct output is to say so explicitly, not to fill 10 slots. A padded briefing damages trust more than an empty one.

## A real acceptance run: 3/10 failed

These gates aren't paper rules — they were earned by real samples. In a two-day acceptance run, hard errors, irrelevant items, and near-duplicates all passed, but substantive rewrite rate on business impact came in at `3/10 = 30%`, over the 20% threshold. Failed.

The problems were specific: a routine reverse repo slipped in two days running on "factual accuracy" alone, with no actionable tie to the role's business; a corporate credit item wore generic funding-channel boilerplate the model had invented. Factually accurate and briefing-worthy are two separate gates.

After root-causing, targeted fixes went in: round one removed the reverse repo and the irrelevant credit item, which exposed false correlations in an aggregated draft; round two added aggregation exclusions, and output converged to 3 directly relevant items. Only after 63 tests, builds, and isolated real runs passed did a human confirm "passed after remediation."

Note the wording: "passed after remediation" is a closure state with historical evidence — the original over-threshold sample, the root cause, the fix, the verification, and the human sign-off are all recorded. It can't be shortened to "the original sample passed," and the 20% threshold wasn't lowered because of it.

## Honesty about failure

The pipeline's failure rules are equally strict: if the model call fails wholesale, no briefing goes out that day — a degraded RSS-only result is never silently packaged as the full product. Say what's missing; that's a quality gate in itself.

## In short

The human-machine split for news briefings is one sentence: machines find and organize public information; humans judge what's worth reading and what may ship. The number of gates doesn't matter — what matters is that every gate has a real sample proving it once caught something.
