# Writing Skills People Actually Use

> Column: Garden ｜ Collection: Agents & Digital Humans ｜ Source: wiki/concepts/AI coding assistant skill-building (desensitized) ｜ Status: first draft

A Skill is "an authoring format for reusable task workflows," not a prompt collection. Before writing one, answer a question: does this task deserve to be reused? One-off, low-reuse tasks a user can describe in a sentence need only a prompt — they don't deserve a Skill.

## First, judge whether it qualifies

Tasks worth distilling into Skills share four traits: frequent, reused across people, stable process, needing resources/scripts/templates/verification. The more boxes checked, the more it deserves writing.

Conversely, one-off tasks — or anything the user can describe clearly in one sentence — should stay as prompts. Turning everything into a Skill produces directories nobody triggers. A Skill's directory state, its install state, and "someone actually uses it" are three different facts.

## One Skill, one clear task

That's the first principle. A Skill's `description` is the trigger entry — it must state two things: when to use it, and where it doesn't apply. A Skill with a blurry boundary triggers at random, which is the same as not existing.

Keep `SKILL.md` short: core flow only, detailed specs go in `references/`. If instructions alone complete the task reliably, prefer instruction-only — don't add scripts for the sake of scripts. Only repeated, error-prone steps earn a place in `scripts/`.

Skills shared across people must also separate "core runtime prerequisites" from "optional accelerators." A flow completable through the Agent's file operations shouldn't block just because the machine lacks Python/Node — and it must never install runtimes without confirmation. Sharing assumes a low bar, not "set up the full environment first."

## Recommended structure

```text
skill-name/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
├── scripts/
└── assets/
```

Only `SKILL.md` is required. `agents/openai.yaml` provides the display name, short description, default prompt, and implicit trigger policy shown in the client.

## Boundaries with other surfaces

An AI coding assistant has several places to "put things" — don't mix them up:

- **AGENTS.md**: long-term collaboration rules, project constraints, verification requirements.
- **Skill**: the execution flow, checklists, references, and scripts for one reusable task type.
- **Plugin**: when a Skill needs distribution, composes multiple Skills, or binds MCP/apps/resources — then wrap it.
- **MCP**: connecting external systems, private data, or callable tools.
- **Hook**: mechanical interception, or enforcing rules around tool calls.
- **Automation**: scheduled checks, reminders, monitoring, follow-ups.

When unsure, ask: is this "how to do a class of tasks" (Skill) or "rules for living with a project long-term" (AGENTS.md)? The former is reusable; the latter is resident.

## Test with real tasks after writing

Complex Skills can't rely on review alone. They need forward testing on real tasks: watch whether they trigger stably and complete the flow without extra context. Unstable triggering means the description's boundary is unclear; incompletable flows mean hidden assumptions.

One more note: a recommended prompt is just entry copy that nudges Skill usage — it is not the Skill itself. No matter how good the entry copy, a broken flow is useless.

## In short

A Skill gets used only when three conditions hold: the task deserves reuse, the trigger boundary is clear, and the flow survived real-task verification. Miss one, and it's furniture in a directory.
