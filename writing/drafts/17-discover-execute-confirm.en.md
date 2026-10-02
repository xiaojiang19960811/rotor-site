# Discover, Execute, Confirm: Three Separate Things

> Column: Garden ｜ Collection: Agents & Digital Humans ｜ Source: wiki/concepts/可信工时与外部写入确认、wiki/concepts/Agent执行编排与外部副作用边界 ｜ Status: first draft

The easiest trap when building AI workflows is treating "the previous phase finished" as "the next phase is authorized." Discovering evidence doesn't authorize creating a task; creating a task doesn't authorize submitting hours; a model proposing a plan doesn't authorize executing external actions. Discover, execute, and confirm are three separate things, each needing its own authorization — the completion of one is only the input to the next.

## Trusted worklogs: a six-stage evidence chain

A worklog backfill pipeline splits this wide open. Evidence is first discovered from session metadata, code commits, and structured work records, then desensitized, estimated, and routed; only after a human confirms task ownership and hours does an independent authorization allow writing to the external system. The full chain has six stages:

1. **Discover**: enumerate sessions, repos, and records within the authorized scope — never bypass protections to read what shouldn't be read.
2. **Desensitize**: scrub per private rules and verify no sensitive residue in the output.
3. **Estimate**: form candidates from explainable work activity; allow less or more than 8 hours, no rounding to fit.
4. **Route**: match semantically fitting tasks first; low-confidence results and missing fields go to pending — the tool never guesses ownership.
5. **Confirm**: only after a human confirms date, hours, task, and description is this batch granted external-write permission.
6. **Write and re-verify**: dedupe before submitting, then check back the actual records — an idempotent loop.

Two rules matter most. First, creating a task and submitting hours are two independent external state changes, each needing separate confirmation. Second, when a creation result is unclear, query whether it landed before retrying — one blind retry can create a duplicate. Same for submission: dedupe before, verify the actual log ID, accumulated cost, and remaining hours after.

## Agent orchestration: seven distinguishable stages

A digital-human Agent's execution orchestration follows the same idea with finer stages:

1. **Model plan**: parse user intent, propose capability nodes and goals — no direct external action.
2. **DTO normalization**: map Chinese time expressions, platform names, and source windows into structured fields; reject uninterpretable shapes.
3. **Capability path compilation**: only capabilities declared side-effect-free may serve as implicit intermediate nodes — no inventing notification or creation actions.
4. **Capability/authorization/dependency check**: verify the capability registry, user authorization, node inputs/outputs, and dependencies.
5. **Review and bounded repair**: fix structural errors a limited number of times; unknown capabilities never degrade into approximate tasks.
6. **Persistent DAG execution**: run on dependency readiness, resource locks, and pause/resume/cancel — every node result traceable.
7. **Side-effect handlers**: notifications, publishing, and other external calls go through dedicated handlers, advancing only after real results confirm.

The hard boundary: external generation, notification, publishing, writing, or deletion must be explicitly declared in the model plan and pass authorization and state gates. An async external task may not mark the workflow successful before it truly completes or clearly fails — and never fabricate a final URL or delivery result.

## Why the split is mandatory

Two scenarios, one principle. In worklogs, "candidates assembled" and "written to the external system" are separated by human confirmation, because wrong hours pollute external state and cost more to clean than one extra confirmation. In Agents, "the model wants to notify" and "the notification actually sends" are separated by authorization checks, because one model hallucination can become a real external action.

The split admits a truth: every stage's output can be wrong, and the blast radius differs. A wrong read-only discovery stage just yields bad candidates; a wrong external-write stage yields real dirty data or real disturbance. The bigger the impact, the stricter the gate. Equating "done" with "authorized for the next step" endorses the strongest action with the weakest check.

## In short

Discover, execute, confirm — three verbs, three accountabilities: see clearly, do correctly, prove it. The previous phase's completion is forever only the next phase's input; authorization must be granted fresh each time.
