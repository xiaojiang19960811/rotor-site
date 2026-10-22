# Before Release, Prove the Old Build Lacks the Feature

> Column: Lab Log | Collection: Engineering Tools | Source: wiki/projects/aiserver-new-sub2api 2026-10-22 Multi-Model Gateway Blue-Green Release (desensitized) | Status: Drafted · Upcoming

Conclusion first: before shipping a new feature, the first job is not preparing the new build — it is proving with evidence that the old build genuinely lacks this feature. "The new build contains the feature" is a positive claim and easy to verify; "the old build does not contain the feature" is a claim of absence, and the easiest to hand-wave away.

The most common release mishaps are not broken new builds, but two ways of treating assumptions as evidence: believing the old build lacks something that some branch had already merged in; or believing the new build has something that the build actually missed. Same root cause in both: nobody ever verified the absence.

## Three Pieces of Evidence, Three Layers

The feature being shipped was a "search/fetch tool API passthrough" for a multi-model gateway: the gateway added two endpoints, billed per successful call with content. Before the release, whether the old build "had" this feature was established with three independent pieces of evidence:

1. **Build timeline**: the production image was built before the target commit. A build produced after that commit cannot possibly contain it.
2. **Product binary**: a string scan of the running old container's binary showed zero occurrences of the new endpoint paths. The feature is absent at the artifact level.
3. **Runtime probing**: real requests to the new endpoints returned 404. The feature is absent at the behavioral level.

The three pieces come from three different layers and cannot substitute for one another: the timeline only proves theoretical impossibility, the binary scan proves the artifact genuinely lacks it, and runtime probing proves it is behaviorally absent. Any single one leaves a gap: the timeline may be right while the artifact was overwritten; the artifact may lack it while requests get hijacked by routing. Proving absence requires all three layers to agree.

## Candidate Slot: Verify Before Switching

The new build does not replace the old one directly. It first starts in a candidate slot: a different port, the same data directory, network, and environment variables. Three checks must pass before traffic switches:

1. Health check returns 200: the service is alive.
2. The new endpoints return 401: the routes exist and authentication is enforced. A 401 here is good news — it proves the request reached the gateway's auth chain instead of being eaten by some middleware halfway.
3. Static assets are reachable: the frontend build is not broken.

The candidate slot paid for itself on the very first start: a missing timezone-data build tag made the candidate container exit on launch, and the problem was caught before any traffic switched. The actual switch took about 4 seconds. Once verified, the candidate container is removed — no keeping two "productions" around.

## Rollback: Ready Before Release

The rollback plan is written before the release, not after. The old image gets a retention tag before the release; this change only touched handlers and routes with no data-structure migration, so rollback only needs switching the tag back, with no data downgrade. The rollback script, the old image, and the switch command are all in place before release day.

## Honest Boundaries: Write Down What Was Not Verified

A release also carries two "not verified" statements, recorded alongside:

1. The candidate container shared the same database for about 6 minutes, with two sets of background tasks running at once, and no data anomaly was observed. That is an observation, not isolation-verification evidence, and it must not be written up as a conclusion.
2. The real per-call billing path had no end-to-end verification — only routes, authentication, and group validation were checked. Billing correctness for the new feature awaits a dedicated verification.

A follow-up probe also found an issue on the second access path: the same feature was registered under both the official path and the root path, and requests to the root path were treated as page routes by the frontend middleware, returning 200 with HTML. Verification had only covered the official path; the gap on the other path is logged as a fix item, with a regression assertion to be added before the next release.

## Closing

A complete release answers at least four questions: the old build truly lacks it (evidence of absence), the candidate truly works (isolated verification), the rollback truly rolls back (a working retreat path), and the unverified is truly listed (a boundary checklist). A release is not "the new build is live" — it is these four answers, all written down.
