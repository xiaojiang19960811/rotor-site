# 82 Autonomous Research Rounds, 81 With Nothing New

> Column: Experiment Log | Collection: Agents & Digital Humans | Source: wiki/bugs/digital-human-agent autonomous research with no new knowledge and mismatched run state + autonomous research too frequent in dev (desensitized) | Status: Drafted, coming soon

The conclusion first: a digital human agent's autonomous research ran 82 rounds in 24 hours, and 81 of them produced no new knowledge. Only one new research item was added. The system did not stop, and it did not error: each round retrieved, saved an exploration record, and judged there was nothing new, then wrote "nothing new" back as an intention to "keep learning about this topic", so the next round went to search the same topic first. A second problem appeared at the same time: a research job already showed completed in the queue, while its run record still showed running, and only three minutes later was it marked failed by the orphan-run recovery logic. The two traps cover one end each: one lets the loop spin empty, the other lets the state lie. For an autonomous loop to be usable, both ends must be controlled: output needs fatigue and cooldown, and state reconciliation needs its own assertion.

## 82 rounds, 81 with nothing new

The numbers first. The dev environment runs research every 2 to 5 minutes. In 24 hours it ran 82 rounds, 81 of which ended with no new knowledge and only one counted as an update; one new research item was added in the same period, out of 14 in total.

Repetition is not the same as no execution. Every round still retrieved, saved an exploration record, and judged by semantic repetition and content fingerprints whether to promote the result into a new research item or formal knowledge. The current topic stayed on "handwritten journals and everyday detail collection" for a long time, and its sources overlapped heavily with existing exploration, so most rounds were correctly downgraded to exploration records. The judgment itself was not wrong: the lack of new material came mostly from topic repetition and the novelty gate, not from a research pipeline that had fully stopped.

An earlier case shows the frequency problem even better: 133 runs in 10 hours, all on the single topic "secondhand books and old bookstores", 113 completed and 20 failed, mostly because structured output exceeded the length limit and was rejected by validation. The dev environment defaults to a round every 2 to 5 minutes and skips the sleep gate, a cadence too high for the real upstream. Spinning empty costs more than no output: every round consumes upstream quota, and the topic is still the same one.

Little output is partly the novelty gate working as designed; the real problem is in the next section: the system also treated "nothing new" as the basis for its next action.

## The first trap: no-new-result written back as an intention, the system assigning itself work

The closed loop formed like this. When research finalized, it did not distinguish whether the result added anything: as long as there was a personal note, it created or updated an active creation intention carrying the topic key. At the next round's topic selection, the deterministic fallback picked any active intention carrying a topic key and returned a query on that same topic; only when no such intention existed did it rotate through the interest pool.

So a self-reinforcing chain appeared: "handbook search finds nothing new, writes an intention to keep learning about handbooks, the next round searches handbooks first." The only active intention in the store at the time was exactly "keep learning about handwritten journals and everyday detail collection". Even when the latest round had produced a verifiable update, it still did not switch to another interest.

The essence of this trap is an input wired to the wrong output. An intention is an input to action: it decides what the next round researches. A research result is an output of action: it reports what this round found. Writing a "no output" result straight back as an input means the system assigns itself work, and always the same work. A no-new-result outcome may only be recorded as an exploration lead, never used to lock in a creation topic: an exploration lead says "this was checked, nothing new here", a creation intention says "this is worth digging deeper", and the two must not share one table.

## The second trap: the job finished, the run record still running

In the same period, the other end of state was also failing. A research job showed completed in the queue at 05:23:47, while its run record stayed running with no exploration or research item at all; only at 05:26:47 was it marked failed by the worker's orphan-run recovery logic.

The root cause was a state reconciliation gap: no consistency assertion existed between job completion and run-record completion. A worker rebuild or task recovery window can leave a task looking running on the surface, which should not be treated as a normal business result, but at the time nothing intercepted it.

The cost of this trap sits in the display layer. The dashboard showed "retrieved this round but nothing new" and "currently executing" as the same state: both running. Seeing "running" looked normal, when in fact the job had long finished and only the reconciliation was missing. State is shown to people, and a lying state costs more than a failed job: a failure can be fixed, but a misreading keeps someone waiting on a job that already ended, and mistakes repeated exploration for being stuck. Before fixing state reconciliation, the display must be split: retrieved but nothing new, currently executing, and abnormal state are three states, not one shared "running".

## The fix: fatigue for topics, layers for intentions

The fix went two ways, one per trap.

The first way targets output: give topics fatigue. A topic state was added, recording each topic's consecutive no-new-result count, cooldown rounds, latest result, and query. Autonomous research became finite persistence: the first no-new-result round may still retry from a different angle, but after consecutive no-new results the topic cools down; a reliable update resets fatigue to zero, and a retrieval failure does not add to it. Legacy "keep learning" automatic intentions were converted to exploration leads during migration, and the dev store had already generated 7 topic states, with the handbook intention downgraded to an exploration proposal.

The second way targets intentions: intentions auto-generated by research moved to the explore or proposal layer, and autonomous creation only consumes active creation intentions, so research no longer locks in a creation topic directly. Layering means a research output first passes through a "proposal" layer before it can become a "creation task".

One follow-up note: the "only consumes active creation intentions" rule above was the rule at the time of the fix, and it was later relaxed one step, so proposal-layer creation intentions meeting the conditions can enter autonomous draft scheduling. Rules are alive, but the layering did not change: a research result cannot go straight to a creation task; a layer of proposal and judgment must sit in between.

## Rules: three rules for an autonomous loop

1. **A result with no output must not auto-generate an action intention**: a no-new-result outcome is recorded only as an exploration lead; once consecutive no-new results reach a threshold, cool the topic down and force a rotation.
2. **Record fatigue per topic**: consecutive no-new-result counts, cooldown rounds, and latest results all go into the store; a reliable update resets fatigue, and a retrieval failure does not count toward it.
3. **Assert state reconciliation separately**: job completion and run-record completion must agree; the dashboard shows "retrieved but nothing new", "currently executing", and "abnormal state" separately, never sharing one "running".

## One line to close

What an autonomous loop should fear most is not stopping, but never stopping while looking busy: never write a no-new-result back as an intention, and when a job finishes, its run record must finish with it; output and state each keep their own ledger.
