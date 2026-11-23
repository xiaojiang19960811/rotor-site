# Four Ways to Make a Rule Stick

> Column: Knowledge Garden | Collection: Agents & Digital Humans | Source: wiki/concepts/desktop agent client standing instructions and skill mechanism (desensitized) | Status: Drafted · Upcoming

Conclusion first: to make a rule apply "every time from now on", there are four mechanisms: standing instruction files, Skills, cross-session memory, and schedules with persistent goals. They are not four spellings of the same mechanism, but four different places to put things: global rules, long flows for one kind of task, facts that span sessions, and work that must happen on schedule each have their own home. Putting one in the wrong place has concrete costs: a long flow stuffed into standing instructions taxes every request with prompt budget; the same content maintained in two places will drift; project-specific conventions written into the global file will pollute other projects' sessions.

## Four mechanisms, four jobs

| Need | Mechanism | Where it lives |
| --- | --- | --- |
| A rule to follow every time | Standing instruction file | Workspace instruction files |
| A long flow, checklist, or script for one kind of task | Skill | A skill file |
| Facts, preferences, and decisions that span sessions | Memory | Memory files split by scope |
| Work that runs on schedule or must continue across rounds | Scheduled reminders, persistent goals | In-session schedule items and goals |

The first dividing line is time: instruction files and Skills cover "every time", memory covers "across sessions", schedules and goals cover "on schedule" and "across rounds". The second line is granularity: instruction files hold rules, Skills hold flows, memory holds facts. The two lines crossed give each mechanism its home.

## Standing instructions: carried every time, but on a budget

Standing instruction files come in two layers: user-global and project-level. Project-level files stack from the project root down to the session working directory, and the more specific file wins; identical duplicates are rendered only once. The global file holds only content shared across projects, while project-specific conventions go in project-level files — that is the first line against pollution.

Standing instructions have three boundaries worth remembering. First, they have a total byte budget: over budget, the broader files are dropped whole first, then the most specific file is truncated. A long flow written in here means paying for it on every request, with no way to select by task. Second, there is no watcher: editing a file does not take effect immediately. Only after a successful first-party file read or write reaches a deeper directory does the next request pick up the new file; changing directory in a shell triggers no discovery. Third, they do not override the user's direct instruction of the moment: on conflict, the current instruction wins, and standing instructions rank below it.

## Skills: loaded on demand, and the description is the trigger

A Skill is deliberately restrained in shape: one skill file at the top level of a skill root, discovered one level deep only, with no nesting. Its header must state a name and a description; an invalid field skips the whole skill. Skill roots are ordered by priority: project-level first, user-global after, with more roots addable by configuration.

There are two ways to invoke one: the model loads it by exact name; the user summons it in the input box with a slash plus the name. There is also a deliberately narrow door: a skill marked model-uninvocable never enters the catalog and the model cannot see it — only the user can summon it by hand. That is the closest thing to a "custom prompt", suited to flows that should be triggered by a person, not volunteered by the model.

Skill directories are watched: adding, renaming, or deleting needs no restart, and editing the body alone loads the file's current content. The most important rule follows from this: a Skill's description needs a clear trigger boundary, or the model will load it for unrelated tasks. The more the description reads like "when to use this", the fewer false triggers.

## Memory and schedules: fixing facts and time in place

Memory is split by scope: the team and each member have their own memory files and topic files. Cross-session facts, preferences, and decisions go here, not into instruction files. Instruction files say "how to do it"; memory says "what is true" — the former holds rules, the latter holds facts.

Schedules and goals are "making things stick" in the time dimension: a schedule item supports intervals, daily, weekly, and cron expressions, and on schedule it drops its prompt back into its session; a persistent goal serves long tasks that continue across rounds, unlike a one-off prompt. Neither solves "follow this every time" — they solve "remember to do it on time" and "don't let a long task drop".

## The rule of thumb: three lines, don't let them stand in for each other

Global rules, acceptance requirements, and prohibitions go in instruction files; step-by-step flows, checklists, and scripts for one kind of task go in Skills; cross-session facts go in memory. The three must not stand in for each other.

Maintain each piece of content in exactly one canonical place: a Skill body repeating a long-term rule lets the rule drift across copies. Project-level files take priority over user-global files, and the user-global file holds only content shared across projects. A Skill description needs a clear trigger boundary, or the model will load it for unrelated tasks. Instruction files do not override the user's direct instruction of the moment; on conflict, the current instruction wins.

Two positive examples show the split in practice: writing "long-term knowledge capture plus the reporting format" into the user-global instruction file means every session after that carries it; turning the whole "organize the knowledge base" flow into a Skill means summoning it by name. The two work as a pair, without copying each other's content. Document output goes through the matching Skill, not through step-by-step description inside the instruction file.

## Two counterexamples

Counterexample one: writing a whole long flow into the standing instruction file. The cost is prompt budget on every request, with no way to select by task. A flow that should load on demand has been promoted into a fixed cost paid every time.

Counterexample two: writing project-specific conventions into the user-global instruction file. The conventions ride the global file into every session and affect other projects. The global file should hold only content shared across projects.

One line to close: before making something stick, ask one question — is this a rule needed every time, a flow for one kind of task, a fact that spans sessions, or work that must happen on schedule? The answer differs, so the home differs; and a wrong home is not a one-time cost, it is a tax paid on every request and every session.
