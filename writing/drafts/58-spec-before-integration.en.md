# Spec First, Combination Later: A Finished Plugin Spec Is Not a Finished Integration

> Column: Knowledge Garden | Collection: Engineering Tools | Source: wiki/projects/desktop-client-plugin-spec (desensitized) | Status: Drafted, upcoming

The conclusion first: when a plugin system's spec is written, that does not mean the plugins are integrated, and it certainly does not mean they are shipped. Spec, combination, and implementation are three stages, and one stage being settled does not automatically settle the next. Naming the stages keeps one sentence from blurring three jobs into one: the docs are done, so the product must be done.

## What a spec stage actually settles

The scope confirmed in this spec stage is specific: only the ten plugin packages currently shipped, nine feature packages plus one shared library. The output is three things: a plugin map, a development onboarding guide, and an acceptance checklist, plus bilingual pages with pairing records and navigation entries in the client documentation.

That scope is itself part of the conclusion. The spec stage changed no package's shipping behavior, changed no restriction configuration, and packaged and shipped nothing. It answered one question: what the ten existing packages are, how to onboard them, and what acceptance looks like. Answering that question is not answering the next one: in what combination are these ten packages shipped to users.

So the genuinely pending items after the spec must be listed separately, not assumed resolved:

1. **Main package combination**: which packages ship with the main package, and which do not.
2. **Existing migration**: how already-installed user configurations move to the new combination.
3. **Core protection exceptions**: which core capabilities plugins may not override or bypass.

These three still need stage-by-stage review. A settled spec does not automatically implement them.

## Spec first, freeze the combination second, implement third

This order is worth stating on its own, because it runs against instinct: the easiest order is to write the spec, settle the combination, and change the code all at once. But then every change to the spec pulls the combination and the implementation along with it, and a review cannot tell "is this rule right" apart from "does this combination work" as two separate questions.

Kept apart, each stage has its own acceptance artifact:

1. **Spec stage**: map, onboarding guide, and acceptance checklist complete, with package count and boundaries stated.
2. **Freeze-combination stage**: the main package combination is settled, and the migration plan and protection exceptions pass review.
3. **Implementation stage**: configuration, shipping behavior, packaging, and release change according to the frozen combination.

The previous stage's output is the next stage's input, not its substitute. Skipping the frozen combination and going straight to implementation lets the implementation site decide the combination on the spot; skipping the spec and freezing the combination directly settles what ships before the packages' boundaries are stated. The order itself is a form of error prevention: it lets each decision appear only where it belongs.

## A sample proves only what it can prove

The spec stage's verification evidence must also be read by its boundaries. This time the evidence includes: twenty package-level tests passing for one feature package, one test passing for a new isolated-loader sample, four pairs of official documentation pairing passing, local link and format checks passing for eight documents, a diff check passing in the business repository, and an independent read-only review of the sample with no mandatory items.

That evidence carries weight, but its coverage is explicit: the sample evidence covers only real loading and unloading at the source level. It proves that the isolated loader can load a package and unload it again at the source level. It does not prove isolation of the shipped artifact, installation under a formal profile, or closure of the spec stage as a whole.

Stating the evidence more narrowly is not diminishing it, it is protecting it: only by first stating what the sample did not prove can a later attempt to use it to argue for release isolation be prevented from being misread as an already-verified conclusion. Writing the boundary of the evidence into the record matters as much as the evidence itself. Whether the whole is complete is judged by the final delivery, not by any single test passing.

## Soft lock: keeping the mechanism and removing a binding are two things

There is one more easily confused decision this time: a future removal of the current release's soft-lock binding on individual capabilities, while the soft-lock mechanism itself is kept as an optional restriction capability, with no configuration changed yet.

These two sentences must be read separately. Removing a binding says a specific capability is no longer bound by the soft lock; keeping the mechanism says the restriction tool itself stays in the toolbox for future use. Saying only "the soft lock is removed" makes people think the mechanism is gone too; saying only "the soft lock is kept" makes people think the binding is still in place.

The soft lock's own semantics must also be stated precisely: it signs the user out when a plugin is closed and attempts to restore on sign-in, not a hard refusal before deactivation. In other words, it is not a front-loaded ban, but a post-hoc state handling. Describing it as a hard refusal gives users the wrong expectation of its behavior; stating its semantics precisely is what lets a review judge what it actually restricts and what it does not.

## What does not count as done

Closing with a checklist. The next time someone says "the plugin spec is done," ask these four questions first; if they cannot be answered, it is not done:

1. **Spec**: are the package map, onboarding guide, and acceptance checklist complete.
2. **Combination**: have the main package combination, existing migration, and core protection exceptions passed review.
3. **Implementation**: have shipping behavior and restriction configuration actually changed and shipped.
4. **Evidence**: does each piece of evidence cover the source level, the shipped-artifact level, or the formal-installation level.

The value of the spec stage is precisely that it lets "not yet done" be stated accurately. Being able to say clearly which stage has not started is closer to done than vaguely saying "almost done."

## One-sentence close

Spec first is not delay: it gives combination and implementation each their own review point. Complete docs are only stage one, a frozen combination is stage two, and only a real change to shipping behavior, released, counts as done.
