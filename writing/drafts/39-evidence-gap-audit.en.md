# "A Green Lint Can't Erase Evidence Gaps"

> Column: Knowledge Garden ｜ Collection: Engineering Tools ｜ Source: wiki/bugs/知识库来源与状态待核验 ｜ Status: draft

**Conclusion first:** A knowledge-base audit produced an awkward verdict: strict structural lint passed on every page, yet seven project pages still carried "not yet verified" items. Lint can scan format and annotation completeness, but not semantic evidence gaps. Passing the checks is internal consistency; closing the evidence is external truth. Neither substitutes for the other.

## What Is an "Evidence Gap"

A knowledge base has a peculiar state: the conclusion is written, the basis is not complete. It is less visible than an outright error — the format is correct, the links resolve, the source field is filled — but the evidence backing the conclusion was either never obtained, or obtained and never matched to the right version.

This audit sorted the gaps into three types:

1. **Missing current-state evidence**: a page describes a running state but lacks direct evidence from the current running instance, such as compose/project/container inventories, labels, mounts, and proxy configuration. Runtime information expires; a health check that passed in July does not automatically count as health in October.
2. **Broken version correspondence**: the release report names a version, but the labels on the running side don't match; deployments after a test-branch merge, or the branch origin of a partial release, were never mapped to an actual deployment.
3. **Substituted acceptance**: weak evidence standing in for strong evidence. A health endpoint standing in for real session acceptance; candidate features treated as already shipped. This is the same pattern as [article 38](/writing/38-available-not-a-pass): "available" is the catalog's status, not a statement about your installed copy.

## The Three-Column Gap Ledger

The audit ledger has three columns, one sentence each:

1. **Entry**: which project page the gap is on.
2. **Unverified content**: exactly which evidence is missing, named at inventory level — no hand-waving like "insufficient information".
3. **Minimum check when closing the gap**: which specific points to verify when evidence comes in. "Minimum" is the point: only the correspondences that must hold — release report versus actual labels, branch origin versus real sessions, local environment kept separate from the test environment — never a generic troubleshooting manual.

A gap earns a row in the ledger only if it meets three criteria: it states what is missing, what would close it, and how closure would be verified. What can't be stated that clearly doesn't deserve a row.

One real row, as an example: a multi-model gateway's project page lacked "the correspondence between the actual compose inventory and the project/container names"; the minimum check reads "release report versus actual labels, mounts, and proxy configuration — do not borrow parameters from another project." Note the second half: the easiest mistake when closing evidence is copying confirmed parameters from a sibling project to fill the blank, and the template writes that prohibition into the minimum check.

## Handling Boundary: A Gap Is Not a Fault

The audit page's stated boundary matters more than the ledger itself:

1. These are evidence gaps found by a knowledge-base audit, not reproduced production faults. A gap does not mean the system is broken.
2. Closing evidence does not authorize connecting to servers, running models, or operating accounts: an audit is not an incident investigation. Evidence gets closed "when the corresponding development task obtains it," by updating the main page.
3. The ledger keeps only unclosed items; it does not duplicate logs. Sources are the listed pages plus their full histories; the audit date is marked with "the business environment was not re-verified."

The boundary guards against two kinds of drift: first, reading a "gap" as a "fault" and triggering unnecessary investigation; second, treating the audit as a one-off campaign whose ledger rots after publication. The ledger has one lifecycle rule: close one item, delete one row; it only ever shows unclosed items.

## The Key Sentence: Lint Is Green, the Gaps Remain

One sentence at the end of the audit page deserves verbatim quotation: "A passing structural lint cannot eliminate these gaps."

Lint checks format, links, and whether source annotations are complete — that is the knowledge base's "internal consistency." An evidence gap is semantic: a page claims a service is running, but is there an inventory to prove it; a page says a feature shipped, but do the release report and the actual labels agree. Those correspondences live outside lint's grammar; no machine can scan them. Only people, working through the "minimum check" item by item.

Any statement that substitutes an internal status word — available, passing, complete, shipped — for an external fact — it runs, the versions match, it was truly verified — is the same illusion in different packaging.

## Closing

A knowledge base is honest not in how much it claims to cover, but in whether it dares to list what it does not know and close the items one by one. A green structural lint is a good thing, but never treat it as proof that the evidence is complete: gaps lying on a ledger are the manageable state.
