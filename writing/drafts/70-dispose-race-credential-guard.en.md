# When Upstream Made Disposal Async, the Credential Guard Silently Broke

> Column: Lab Log ｜ Collection: Engineering Tools ｜ Source: wiki/projects/desktop client 0.2.2 core upgrade and account plugin dispose race (desensitized) ｜ Status: Drafted · Upcoming

Conclusion first: after one core upgrade, a safety guard in the account plugin silently stopped working — while the plugin's own code had not changed by a single line. The upstream plugin framework changed effect disposal from synchronous to an asynchronous chain, so by the time the dispose call returned, disposal had not actually finished, and an in-flight credential write was no longer blocked. The fix did not touch the upstream core; it only added one macrotask yield in the plugin layer: wait for the async disposal chain to finish, check the abort signal again, and the late write is blocked once more. The lesson of this postmortem is a single sentence: a guard often depends not on your code, but on an implicit assumption about upstream behavior; when upstream changes the timing, the guard fails with it.

## What the Guard Was Protecting

The account plugin has one safety rule: once a sign-in flow is cancelled or disposed, a late credential response must not be persisted as a valid grant.

The scenario is easy to picture. A user starts signing in, the credential request is still in flight, and the session gets disposed. The response arrives a step late — and if it still writes the credential into the authorization state, a sign-in the user believed was cancelled quietly takes effect. The user thinks they are not signed in; the system signed them in anyway.

So the plugin puts a gate on the credential commit path: check the lifetime signal before writing, and refuse to persist if the signal has aborted. The gate produces no visible feature; on an ordinary day nobody can feel it. Its entire value lies in the one time it is supposed to block.

## Not a Line Changed, and the Guard Failed First

After the core was upgraded to the new version, the account plugin's recovery tests started failing in a row. The same tests passed 11 out of 11 on the old baseline. The first instinct might be that the tests were outdated — but one fact had to be checked first: the plugin's credential-related source had zero changes. The code had not moved, yet the behavior had; the change could only have come from upstream.

The root cause was an internal refactor in the upstream plugin framework: effect disposal went from synchronous to an asynchronous chain. In the old version, calling dispose took effect immediately — after dispose returned, any in-flight write would be blocked. In the new version, dispose returning only means the disposal chain has started running; the actual cleanup is still queued behind it. So a window opened between dispose and cleanup completing: a credential write landing in that window was no longer blocked, and the late write went straight through.

Characterize the failure before reaching for a fix. The test asserts product safety semantics, not an implementation detail: a cancelled sign-in must not quietly take effect, and that requirement does not change with a framework version. When a test fails, first ask whether the assertion is still right — not how to rewrite the test to accommodate the new behavior. The assertion was right; the behavior was wrong.

## The Fix: Wait for the Disposal Chain Before Writing

The fix left the upstream core alone and adapted only at the plugin layer. The idea is direct: since disposal has become asynchronous, wait for it to finish before writing.

Concretely, on the credential commit path, after the write is issued, one macrotask yield is added, giving the async disposal chain a chance to complete and settle the lifetime signal as aborted; the signal is then checked once more, and if it has aborted, the grant is not persisted. The yield is not a delay — it makes the premise "disposal has completed" true again before running the original check.

Verification ran on two levels: the recovery tests passed 11 out of 11, and the account package's 97 tests all passed. The guard was back, and the fix touched no upstream core, so nothing else the upgrade brought was affected.

## The Same Latent Flaw: Testing Only Explicit Cancellation Misses It

In another distribution built from the same codebase, the sibling account plugin hid the same latent flaw — but the upgrade did not expose it. The difference was not in the code; it was in test coverage.

Its sign-in tests covered only the "user actively cancels" shape: the cancellation sends an explicit abort signal, and the check logic blocks it directly. But no test constructed the disposal concurrency window: a request blocked midway, disposal happening first, the response released afterwards, asserting that both the grant and the credential reference stay undefined. Explicit cancellation travels the signal path; a disposal race travels the timing path — the two cancellation shapes do not test the same guard at all.

The backfill was adapted to that sibling's shape rather than copied mechanically: a new test constructs the "request blocked → dispose → release" window and asserts that both the grant and the credential reference are undefined. The sign-in tests passed 62 out of 62, and the sibling flaw was closed before it ever fired.

The lesson here is not only "write one more test." When code is shared, shared flaws have to be hunted by analogy — you cannot wait for each copy to blow up on its own. On finding one problem, ask where the same code lives elsewhere; that question is far cheaper than the next fire.

## Three Rules for Guards

1. **Characterize first, then fix**: when a test fails, first ask whether it asserts product semantics or implementation detail. If the semantics have not changed, fix the behavior — don't rewrite the test to accommodate the new behavior.
2. **Write implicit assumptions down as tests**: if a guard depends on an upstream timing assumption, write that timing into a test: after dispose, before cleanup completes, an in-flight write must be blocked. An assumption that is never written down fails silently the moment upstream changes.
3. **Cover every shape of cancellation**: explicit cancellation, disposal races, timeout reclamation — testing one is not testing all of them; and shared code's shared flaws are found by analogy, not by luck.

## One Sentence to Close

A guard is most fragile not when its code is wrong, but when the assumption it quietly rests on — "upstream has always behaved this way" — changes without notice: disposal went async, and the late write landed; write the timing assumption into a test, cover every shape of cancellation, and the guard is truly in your own hands.
