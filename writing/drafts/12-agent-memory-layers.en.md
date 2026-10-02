# Layered Memory for Agents

> Column: Garden ｜ Collection: Agents & Digital Humans ｜ Source: wiki/concepts/Agent记忆分层与自生长 ｜ Status: first draft

An agent's long-term state can't be a stew. "What happened," "what's factually true," "what's in progress," and "how things changed" are four different things — manage them together and you'll eventually mistake small talk for personality and stale knowledge for today's fact. Our digital human agent splits memory into six layers, each with its own content and its own way of entering runtime context.

## What each layer records

| Layer | Records | How it enters runtime context |
|---|---|---|
| Core | Stable self-story, identity, confirmed core facts | High-priority formal context; core persona can't be auto-rewritten |
| Events | Interactions, experiences, completed events | Retrieved or summarized by topic; not the same as persona |
| Relations | Low-risk, traceable observations about people/relationships | Passes risk and source gates first |
| Knowledge | Content once learned, organized, and kept | Builds familiarity; never posed as lived experience, never overrides newer facts |
| Work | Current workset, task context, long-term archive after completion | Current workset first; archived after done |
| Creative | Finished or forming creative material, versions, results | Creative context only; never auto-promoted to persona facts |

The core idea: memory answers "does she still remember, how did this stay, how familiar is it now"; the knowledge base answers "which source counts now." Knowledge memory holds the knowledge itself, never written as lived experience; interpretation builds on persona and existing memory, recorded separately only when it differs from the source text.

## Formal boundaries: candidates don't auto-promote

Extraction results start as candidates and must pass category, completeness, source, risk, and confidence gates before auto-entering formal memory. The following never go straight into reply context: task artifacts, model claims, unconfirmed states, sensitive identity/relationship judgments, low-confidence content.

Auto-promotion, manual promotion, revocation, recovery, and persona application all keep source, operator, version, and changelog. Candidate, observed, formal, revoked, and blocked states must stay distinguishable — one "remembered" flag can't cover the whole lifecycle.

The most important rule: the core persona is never rewritten by auto-extraction or by the model itself. Persona expansion goes through human review. That's the red line.

## Forgetting fades, not deletes

A memory also has its own evolution history, familiarity, and forgetting — three separate mechanisms:

- **Evolution history**: keeps old wordings, append-only, never silently overwritten. When new facts conflict with old memory, the new fact wins, with a note of the updated understanding.
- **Familiarity**: counts only how often the memory is re-encountered, recalled, or mentioned — no borrowed weights.
- **Forgetting**: fades from daily recall while history remains; not the same as revocation. Core memories never fade naturally.

"Remembering" and "always bringing it up" are different things. Fading lets an agent neither lose its past nor be ruled today by something from three years ago.

## The self-growth pipeline

Memory growth is a pipeline, not magic: interactions produce candidates; workers extract and merge by idempotency key, source, and topic window; gates decide auto-confirmation or exception queue; formal memory enters runtime context while candidates stay out of replies by default; long-term repeated evidence forms observations, which project into constrained tone or topic prompts — but an observation's effect needs independent replay and real-sample validation. "Recorded" never means "behavior already changed."

## In short

Layered memory doesn't solve "storing more" — it solves "not mixing flavors": persona stays persona, events stay events, knowledge stays knowledge. Each layer gets its own promotion gates and forgetting rhythm, so the agent can grow over the long term without mistaking the past for the present.
