# The Faster AI Codes, the More Humans Must Judge

The faster AI writes code, the less developers can afford to check out. Spec-Driven Development (SDD) doesn't replace Vibe Coding with documents — it gives Vibe Coding a stable, reviewable, verifiable context. First drafts of `spec/design/tasks`, breakdowns, formatting, and continuous write-backs can all go to AI. Developers don't need to become typists; they need to become the ones who judge.

## AI works, humans judge

AI is good at: scanning code to map the current state, drafting specs and designs, splitting tasks, building traceability, implementing code and tests, writing back results. That solves information organizing and execution speed.

Seven things developers actually need to do:

1. **Name the sources of truth**: which entry points, modules, API docs, or tests represent current behavior; prototypes show page goals, not business rules.
2. **Catch assumptions AI quietly added**: do interface fields, status values, permissions, and fallback logic have backing; unbacked items go to unconfirmed, not to invented answers.
3. **Confirm the design fits the existing system**: layering, dependencies, compatibility, performance, security, rollback; complexity matched to risk.
4. **Decide which risks close first**: anything changing data structures, API contracts, or core flows must be confirmed before implementation.
5. **Check tasks are actually executable**: dependency order, independent verifiability, no "comprehensive testing" as a task.
6. **Judge whether evidence is enough**: what builds, unit tests, and mocks each prove; never auto-upgrade low-level evidence to high-level conclusions.
7. **Own the final state**: does implementation match spec, does design still reflect code, is it "implemented" or "verified," where do remaining risks go.

One person can wear multiple hats, but every conclusion must trace to its source.

## Token savings are not guaranteed

Bluntly: SDD does not promise fewer tokens in round one. Writing and reviewing specs is new cost.

```
Traditional total = initial prompt + implementation chat + repeated explanations + rework
SDD total        = specs & review + implementation chat + spec write-backs + minor fixes
```

SDD saves tokens only when reduced re-explanation and rework outweigh the new spec cost. Multi-session, multi-person tasks with heavy interface/state/permission constraints are likelier to save; a five-minute fix or throwaway prototype will likely cost more.

## Measure the whole chain, not coding speed

In the first hour, SDD is usually slower — traditional Vibe Coding is already generating code while SDD is still listing unconfirmed items.

Efficiency should be measured across the full chain:

```
requirement in → rules confirmed → implementation → testing & integration → acceptance → rework → final verification
```

Faster code generation with slower integration, acceptance, and rework is not an improvement. SDD pays off through earlier problem discovery and less rework, not through document formats.

## Three tiers, no one-size-fits-all

- **Direct Vibe**: small copy, local styles, one-off exploration, throwaway prototypes — instantly verifiable, cheap to fail.
- **Lightweight notes**: single-page local features, well-bounded single bugs, some legacy behavior to protect.
- **Full SDD**: cross-module changes, API contract changes, permission/state/persistence, payments/approvals/external writes, multi-person or multi-session work.

Escalate tiers as impact grows. Plan mode answers "how do we do this task"; SDD answers "what do we base it on, which rules are confirmed, what counts as done" — one is a single execution plan, the other is the long-term basis.

## In short

The more AI can write, the more humans must guard judgment: sources of truth, hidden assumptions, design tradeoffs, risk ordering, evidence levels. AI can write the documents; it can't do the judging. Whether SDD saves tokens or improves efficiency isn't measured by coding speed, but by how many detours the full delivery chain avoids.
