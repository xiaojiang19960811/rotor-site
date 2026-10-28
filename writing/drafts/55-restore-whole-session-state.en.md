# Restoring a Session Means Restoring Its Whole State

> Column: Knowledge Garden | Collection: Agent | Source: Desktop Agent client main-session archive recovery review | Status: Drafted, upcoming

The conclusion first: when you restore an object, the unit of restoration is its whole state, not just bringing it back to life. Restore the actor but not the state flags, and from the user's perspective nothing was restored. And before deciding whether to restore at all, classify the events first — otherwise the restore logic will manufacture new confusion on its own.

## A main session that was "restored" but invisible

In a desktop Agent client, team mode has a main session: the user's everyday conversation entry point. After an upgrade, the restore logic ran and the Agent member came back, but the user still could not find the main session.

Investigation turned up two reproduced gaps:

1. **After an archived main session was restored, only the Agent came back; the archive flag was never cleared.** The member returned, but the session still sat in the archive, invisible in the normal list.
2. **Greeting recovery mistook system context for user speech.** System-generated events — runtime context, skill catalog, time context — were counted as evidence that the user had spoken. As a result, the "greeting" title the user saw belonged to a different ordinary session, while the original main session's title never changed.

Both gaps point to the same root cause: the restore logic only checked whether "the thing exists," not whether "the state is right."

## The unit of restoration is state, not entity

A session is not just an entity that can chat. It is a bundle of state: its original identity, name, history, and visibility flags. Miss any one of them during restore, and the user sees a broken object.

The restore checklist settled in this review:

1. **Keep the original ID, name, and history**: restoration brings back the original session; it does not create a lookalike.
2. **Visibility flags are state too**: the archive flag must be cleared as part of the restore, or the restore never happened from the user's perspective.
3. **Order matters**: unarchive first, then open. Do it the other way round and the open may land on a session that is still archived — work wasted.

More generally, the acceptance test for any "restore" feature should be a before-and-after state checklist, not "the feature ran." Running only proves the code executed; the checklist proves the state came back.

## Classify events before judging restores

The second gap deserves its own section: before restore logic can answer "has the user spoken?" or "should a greeting be added?", it must first classify the events correctly.

A session's event stream contains more than user speech. It carries large amounts of system-generated events: runtime context, skill catalogs, time context. They sit in the same stream, but they are not user behavior. Counting system events as user speech leads the restore logic to wrong conclusions: it may skip a greeting that should have been added, or attach the greeting to the wrong session title.

The fix follows a simple principle: **greeting checks ignore system context, while still never interrupting a real user conversation twice.** Classification first, judgment second; system events do not count toward "has the user spoken."

There is also a diagnostic discipline here: when investigating this kind of problem, the inspection itself should only read the relevant metadata and event classifications, never rewrite user logs. A diagnostic tool that casually writes data creates a new crime scene while investigating the old one.

## Restore triggers must be narrow, never batched

Once restore works, the next question is: at what moments, and over what scope?

The narrowing chosen here: restore the main session only at two explicit moments — the first initialization of the team runtime, and the user explicitly clicking the main member entry. Ordinary members and ordinary sessions are never batch-unarchived.

Batch restore looks efficient but oversteps: sessions the user deliberately archived are not the system's to dig up. Restoration must not go further than the user's intent. The more explicit the trigger, the more predictable the restore behavior — and predictability is the single most important property of a restore feature.

## Hiding UI is not a blanket ban

The same batch of changes carries a wording discipline worth recording on its own.

After team mode was narrowed, the dedicated session header no longer offers ordinary archive or rename actions, ordinary creation and workspace-selection entries are hidden, opening an ordinary session switches back to the original mode, and mode switching creates no extra sessions. But at the same time, the native mode, system menus, keyboard shortcuts, and APIs carry no backend prohibition.

So the correct statement is "the interface narrows it," not "the system bans it outright." Writing UI hiding as a blanket ban promises, in copy, something the backend never implemented. The moment a user gets through by another route, they will conclude the system lied — when in fact only the copy overreached.

This generalizes: for any claim that "some capability is turned off," first ask what exactly was turned off — the entry point, the permission, or the backend capability. The three are not the same thing, and copy may only promise the layer actually implemented.

## One line to close

When accepting a restore feature, check off the state list item by item: identity, name, history, visibility flag — none may be missing. Classify events before judging; narrow triggers to actions the user explicitly takes; and let copy promise only the layer already implemented.
