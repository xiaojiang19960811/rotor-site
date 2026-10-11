# "Available" Is a Market Status, Not a Pass

> Column: Knowledge Garden ｜ Collection: Agents & Digital Humans ｜ Source: wiki/concepts/AI能力资产治理 ｜ Status: First draft

**The short version:** When a skill or plugin is marked "available" in a capability marketplace, the real information content is exactly one sentence: it passed the catalog's quality gate and can currently be distributed. The user actually wants eight separate questions answered: did the quality pass? Is the source readable? Can I see it? Can I install it? Will it run? Can it touch business data? Is external write allowed? None of these answers can be derived from the two words "available".

## One word, eight objects

AI capability assets include skills, plugins, prompt workflows, MCP connections, automations, and other reusable agent workflows. The point of governing them is not to stuff everything into one repository, but to draw clear boundaries around discovery, verification, publishing, distribution, installation, authorization, operation, upgrades, and retirement. In practice, at least eight objects must be modeled separately:

1. **Implementation asset**: an independent repository, version, entry scripts, and dependencies.
2. **Catalog asset**: stable ID, name, description, status, source, and installation method.
3. **Candidate draft**: ideas, AI-completed fields, and content pending maintenance — must never be written back into formal assets automatically.
4. **Distribution info**: marketplace, enterprise mirror, artifact, or Git installation entry.
5. **Installed copy**: the specific version in the user's environment, which does not update automatically when the catalog status changes.
6. **Runtime configuration**: MCP, OAuth, environment variables, model providers, and local private rules.
7. **Permissions and authorization**: source reads, asset visibility, install acquisition, business data access, and external writes.
8. **Verification evidence**: structure checks, installation, triggering, real tasks, permission reviews, and external-write re-verification.

Why split them? Because the eight are produced by different people, at different times, on different evidence. The classic confusion is treating a catalog entry and the user's installed copy as the same object: the catalog got upgraded, but that does not mean the copy on the user's machine followed. Another confusion is letting AI "graduate" a candidate draft: AI can organize ideas, fill in fields, and generate evaluation cases, but promoting a candidate to "available" must be a maintainer's confirmation.

## "Available" does not mean "usable by you"

Permissions must be judged on at least eight layers: source reads, asset management, catalog visibility, install acquisition, local execution, tool connections, data access, and external writes. Each layer answers a different question, with its own evidence.

Three conclusions that fool people most easily:

- **"Available" only speaks to asset quality and market status.** It says nothing about whether the current user holds permissions for the source repository, installation channels, business systems, or data.
- **A live technical session is not authorization.** A logged-in browser, a working MCP connection, or credentials on the local machine only prove the connection is alive — they do not constitute authorization to read, modify, or publish anything. Discovery, publishing, installation, configuration, data access, and external writes are six different actions; finishing one never authorizes the next.
- **An end-to-end green pipeline does not auto-open write access.** In a real worklog-backfill scenario, with the skill, the browser session, and the task candidates all ready, creating the task and submitting the worklog were still two separate authorizations; on an unclear response, you query the state first instead of retrying directly.

## Verify in layers by risk; conclusions cannot borrow each other

Verification of a capability asset climbs in layers by risk: structure and front matter; unit tests and static security checks; installation in an isolated environment; triggering and comprehensibility in a fresh thread; read-only real tasks under the user's permissions; externally confirmed external writes, with the result re-checked afterward; upgrade, rollback, and uninstall capability.

Each verification must also be bound to: the implementation version, the installed copy, the runtime environment, the user's permissions, the real task, the time, and the uncovered boundaries. This is the same evidence view as [article #9, "\"Done\" Is Not \"Verified\"](/writing/09-done-vs-verified): catalog status, successful installation, one successful real task, and sustained availability — four conclusions that cannot substitute for each other.

AI has a clear boundary in this chain. It may identify repeated tasks and generate candidates, extract descriptions and boundaries from sources it is allowed to read, generate candidate tests and maintenance suggestions, and rank within the formally registered candidate set with explanations. It may not: automatically promote candidates to formal status; use a service account's permissions to obtain runtime business permissions for a user; perform external writes just because the browser, MCP, or credentials are available; or extrapolate one successful install or demo to all users, environments, and versions.

Retirement is also part of governance: source repository moves or permission revocations, dependency failures, catalog descriptions drifting from the implementation, installed copies long un-upgraded — before retirement rules are confirmed, never automatically delete formal assets, user installed copies, or historical evidence.

## The wrap-up

The one core move of capability-asset governance: split a word into a set of facts. "Available" splits into who, at which version, in which environment, with which permissions, what was installed, and what was verified. Each answered separately, each verified separately. From now on, when you see "available", ask: available to whom, where, and down to which layer?
