# "Done" Is Not "Verified"

> Column: Knowledge Garden ｜ Collection: Engineering Tools ｜ Source: wiki/concepts/AI工程评测与发布证据链 ｜ Status: draft EN

In AI engineering, "code complete," "tests pass," "releasable," "deployed," "production-ready," and "sustained healthy" are six different conclusions. Each must be bound to a target version, environment, identity and permissions, samples, verification method, and uncovered boundaries. Low-level checks, a single success, or a healthy endpoint cannot substitute for real business flows, production observation, or recovery capability evidence.

## Six conclusions, not interchangeable

| Conclusion | Establishes | Does not automatically establish |
|---|---|---|
| Code complete | Implementation landed in the specified tree or commit | It builds, it was tested, it was released |
| Tests pass | Assertions held for the listed checks, environments, and samples | Unlisted real flows, roles, or long-term quality |
| Releasable | Pre-release checks, artifact identity, risk and rollback prep are satisfied | It is deployed or production traffic is healthy |
| Deployed | The specified artifact and config entered the target environment | Traffic was cut over, user flows work |
| Production-ready | Production entry, key dependencies, and this batch's user flows passed at a given point in time | All users, all capabilities, future health |
| Sustained healthy | Errors, latency, cost, resources, and user-visible outcomes stayed in range over an agreed window | It will never degrade or never needs re-verification |

Evidence supports a specific claim, not a vague "done." A passing type check only supports analyzability; a passing mock only supports frontend behavior under simulated conditions; a healthy production endpoint only supports that the service is alive.

## Evidence must be bound to object and scope

For a verification to hold, it must answer at least nine questions:

1. **Object**: Was it source, a commit, an image, a model, a prompt, a config, a migration, or a production instance?
2. **Claim**: Was this about correctness, compatibility, performance, cost, deployment, or recovery?
3. **Environment**: Local, mock, test env, canary, blue-green slot, or production?
4. **Identity and permissions**: Which role? An admin's success is not a regular user's availability.
5. **Inputs and samples**: Sample size, positive/negative cases, external dependencies?
6. **Method and expectation**: What checks ran, what was expected?
7. **Actual results**: Counts, states, failures, degradations, each recorded.
8. **Time and source**: When, and where does the evidence live?
9. **Uncovered boundaries**: Which real flows, roles, or time windows were NOT verified?

Once the commit, model version, prompt, config, or data changes, old evidence keeps only historical value.

## Verification ladder: weak to strong, but not overriding

1. Static and structural checks (lint, types, schemas, secret scanning)
2. Deterministic local tests (unit tests, billing formulas, routing, permission logic)
3. Isolated integration (mocks, clean installs, service composition)
4. Real dependencies and business E2E (real providers, real data, real user flows)
5. Candidate environment (canary / blue-green inactive slot)
6. Post-release verification (real requests, costs, logs after cutover)
7. Cross-time observation (multi-day samples, percentiles, failure rates, quality drift)
8. Recovery verification (rollback, backup restore, idempotent retry)

A higher level does not automatically cover lower-level assertions. One real production request has high fidelity but possibly low coverage and persistence; extensive mock tests have high coverage but low real-dependency fidelity. The two complement each other; neither substitutes for the other.

Low-risk copy doesn't need all eight levels mechanically. Payments, permissions, persistence, model billing, external writes, and production migrations cannot be closed on static or mock evidence alone.

## Special handling for AI evaluation

AI output is non-deterministic. You can't regress on exact-string match, and you can't pass on "looks good":

- Fix what's fixable first: inputs, prompt templates, model versions, parameters, tools, data windows.
- Write the dimensions down: structural validity, factual verifiability, citations with dates, refusal/degradation, latency, cost, extent of human rewriting.
- Keep positive, negative, failed, and degraded samples together. Saving only the best output whitewashes the distribution.
- Single-run success, multi-sample quality, and long-term stability are three separate statements.
- When thresholds exist, record numerator, denominator, and raw samples. A pass after remediation must not rewrite the original failure as a pass.

## Failure is also evidence: a real case

In our newsletter quality-gate practice, automated evaluation passed 3 of 10 samples (`3/10 = 30%`). After remediation, re-verification, and human confirmation, it passed. The `3/10` figure stays in the report, undeleted.

Rationale: failures and unverified items define the current capability boundary. A post-remediation pass is recorded as "original failure + root cause + change + re-verification" — an auditable "pass after fix," not a rewritten history. Deleting the failure record deletes the boundary itself.

## Boundaries for AI participation

AI may organize test lists, generate candidate cases, run authorized checks, summarize results, and point out gaps. It must not:

- Write an unrun, failed, timed-out, or unauthorized check as "passed";
- Derive high-level business or production conclusions from low-level evidence;
- Decide scoring, thresholds, validity periods, or approvers on its own;
- Approve production cutovers or external state changes because automated tests passed;
- Delete failure evidence, or rewrite "pass after fix" as "passed originally."

## In short

"Done" is an adjective; "verified" is a verb. The former describes a state, the latter demands evidence.

Next time someone says "it's done," five questions suffice: in which environment, as which identity, on what samples, when — and what exactly was proven. No answers, no credit.
