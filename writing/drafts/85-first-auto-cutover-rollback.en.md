# The Build Succeeded. The Cutover Failed.

> Column: Lab Log ｜ Collection: AI Infrastructure ｜ Source: wiki/projects/xxt-ai, automated publishing of the Xingqiao service (desensitized) ｜ Status: Drafted · Upcoming

The conclusion first: the first time the automated publishing pipeline connected to production, the cutover failed — but the service never went down. The second build passed every direct check against the standby slot, yet the public version check failed after the smooth reload, and the pipeline rolled back to the original slot on the spot. The third build cut over, and eleven minutes later all three cross-checks passed. A successful build is not a successful cutover: the cutover is judged by the public version, not by the build status, and rolling back is not a rescue — it is part of the cutover's design.

## What happened: everything passed inside the slot, then the public check failed

Before the automated pipeline touched production, the same image was verified end to end in an isolated environment: the login page, the version-tagged scripts, and the anonymous endpoints, one by one. A probe container joined the test network for acceptance, without exposing any port on the host. Only then were the production pipeline and the main-branch push trigger connected, and the first real automated publish began.

The second build looked normal all the way through: the standby blue slot started, direct acceptance passed, and the gateway reloaded smoothly to shift traffic over. The first thing after the reload was the public version check: reach the service from the public internet and confirm the returned page resources were the new version. The check failed.

Where the failure happened matters: not in the build, not in the standby slot's health check, but in the public verification after the cutover. The build, the startup, and the direct acceptance had all passed; the fourth gate was the one that fell. Had acceptance stopped at the third gate, this publish would have been recorded as a success while users were still reaching the old version — or worse, a half-old, half-new mix.

## The cutover is judged by the public version, not by the build status

The pipeline's title and its final result also disagreed at one point: the status the title showed did not match what actually happened. When that happens, the verdict does not come from the title, but from three sources of evidence: the pipeline's exit code, the production receipt, and the version of the public resources. Only when all three agree does the result count; no single one of them decides alone.

The rule generalizes: a publish is complete only as defined by the evidence closest to the user. The build status describes the inside of the pipeline; container health describes the inside of the slot. Only the public version describes what users actually receive. The closer the evidence is to the user, the closer it is to the truth; the closer it is to the build, the further away.

So the acceptance order should run in reverse: fix the public version's acceptance criteria first, then look back at the build and the slot. Ask "are users getting the new version now?" before asking "did the build succeed?" Reverse the order, and the conclusion can reverse too.

## Rolling back is not a rescue; it is part of the cutover's design

After the second build's cutover failed, the pipeline did not stop and wait for manual handling — it rolled back to the original green slot directly. The production receipt and the system logs agree: the reload that cut traffic over and the reload that cut it back were about 40 milliseconds apart. The old slot had stayed healthy throughout, and handing traffic back interrupted nothing.

That speed was not luck; it follows from the structure of blue-green deployment itself. The old slot was never stopped, so when the new slot failed, pointing traffic back at the old one cost a single gateway reload. The rollback could be that fast precisely because the old slot had never left.

Many teams treat a rollback as the cleanup after a failure: the publish counts only if the cutover succeeds, and rolling back means the publish failed. Look at it the other way round: the rollback is what makes the cutover safe to attempt at all. A cutover without a reliable rollback is a gamble every time — cut over, find a problem, and you are stuck fixing it in place or moving traffic back by hand. Being able to roll back is what lets you cut over; without it, no amount of build verification makes the move safe.

The third build's success proves the point: the same pipeline, the same blue-green structure — the second build cut over, failed, and rolled back; the third cut over and stayed. The failure left no mess behind, and the success needed no rebuilt environment. The rollback turned a failed cutover into a rehearsal that cost nothing.

## After the cut, do not announce yet: wait for convergence, then re-verify

The third build cut over at 16:40, and the gateway briefly returned the old version before the re-check passed. That old version in the first moment after the cut was not a failed cutover; it was convergence lag. The reload had gone out, but the gateway, the caches, and the layers of state had not caught up yet. Judging in the very next second after the cut would misread the result either way — success or failure.

The real completion was confirmed at 16:51, when all the checks passed: the pipeline status was success, the blue slot's image matched the acceptance record, the public page resources matched the main branch, and the old green slot was still healthy. None of the four can be skipped: the pipeline status confirms nothing went wrong on the build side, the image confirms the accepted version is the one running, the public resources confirm users are getting the new version, and the old slot's health confirms the rollback capability is still there.

That order belongs in the publish procedure: cut over, wait for convergence, re-verify, then announce. The moment to announce is not when the reload completes, but when the re-verification passes. Announcing early means telling the world the new version is live while users are still seeing the old one.

## Verification and boundaries

The conclusions of this review come from the same day's three build records: the isolated-environment acceptance, the two cutovers, the one rollback, and the three-way evidence cross-check — all from the original production receipts, system logs, and public checks, not from reconstruction after the fact.

There are two boundaries. First, automated publishing covered only the service side; the frontend and the gateway still publish through a different route, and the coordination between the two publish paths is outside this scope. Second, this first automated publish verified only "cutting over" and "cutting back". The pipeline's long-run stability, failure rate, and how often manual intervention is needed will take more publishes to assess.

One line to close: a successful build only buys the ticket to cut over; the public version is the judge, and being able to roll back is the confidence.
