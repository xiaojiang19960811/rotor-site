# The Mode Switched Back, but the UI Stayed Behind

> Column: Lab Log | Collection: Agent | Source: Desktop Agent client mode round-trip switching review | Status: Drafted, upcoming

The conclusion first: shared state should be subscribed to, not snapshotted once at first render and kept privately. A snapshot is good enough for a one-way flow; the moment users can switch back and forth, the stale snapshot becomes a source of confusion. The acceptance bar for mode switching should be a round-trip case, not a one-way case.

## Switched Back, but the Button Still Thought It Was in Team Mode

A desktop Agent client has two modes: team mode and list mode. A bottom entry button changes its label and click behavior with the current mode.

After one change, this happened: the user switched from team mode back to list mode, but the bottom button's label did not change, and neither did what its click did — it still behaved as team mode. The settings page held its own separate stale state, which had not caught up either.

The root cause was not in the switching logic but in how the mode was read: the bottom entry read the sidebar mode only on first render, and the value it read was captured by the click closure and never refreshed. The mode changed; the button did not know. Its label and behavior stayed in the world it first saw.

## A Snapshot Is Only Good Enough for a One-Way Flow

Reading once at first render looks reasonable in many cases: the mode is settled when the component mounts, it rarely changes afterwards, and skipping a subscription saves a little complexity. But that reasoning rests on a hidden premise: the flow is one-way, and the state will not change after being read once.

Round-trip switching breaks that premise. The user goes from team to list and back to team, and every switch requires the UI to answer again, "what mode am I in now?" A snapshot can only answer, "what mode did I see the first time?" The two answers diverge after the first switch and drift further apart from there.

More insidious is the second copy of the state: the settings page kept its own mode. When one piece of shared state has two copies in the UI with no sync mechanism between them, drift is only a matter of time. Fix one copy, and the other will surface the same problem in a different form sooner or later.

## The Fix: Let the UI Subscribe to the Mode, Not Keep a Copy Each

The fix converges the mode onto one shared source, and every surface that needs it subscribes to that source instead of copying it at first render:

1. **One shared mode snapshot**: the current value of team mode versus list mode lives in exactly one place.
2. **Subscribe, don't read**: the bottom button and the settings page both subscribe to that snapshot, so when the mode changes, both update together — there is no intermediate state where one updated and the other did not know.
3. **Frontend only, no business state touched**: mode is UI state, so fixing how it is read should not touch sessions or accounts along the way. The smaller the change surface, the easier it is to confirm no new confusion was introduced.

Verification has to change with it: a one-way case (the button is correct in team mode) is no longer enough; round-trip cases are required. This regression covered three consecutive team → list → team round trips, checking the button label and the visibility of the native create entry each time, and confirming that switching created no extra sessions. Three clean round trips mean the subscription is genuinely wired up.

## A Checklist to Take With You

For any state users can walk back and forth across, run through this list:

1. **Is this value subscribed to, or snapshotted?** Anything read once at first render and carried along by a closure is a snapshot.
2. **How many copies of it exist in the UI?** More than one means asking what keeps the copies in sync; no answer means a drift candidate.
3. **Does acceptance include a round-trip case?** Testing only one way tests nothing but the moment the snapshot was still fresh.
4. **Does switching have side effects?** Switching modes on its own should create no extra sessions and change no accounts; fixing UI state should leave business state untouched.

Much UI confusion looks like "the switching logic is wrong" when it is actually "the reading approach is wrong." The switching logic may be entirely correct — it is just operating on a state the UI stopped looking at long ago.

## One Line to Close

Shared state has exactly one source, and every UI surface is its subscriber; for any state users can walk back and forth across, acceptance must run round trips, not one-way trips.
