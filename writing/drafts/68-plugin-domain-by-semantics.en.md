# Group by Semantics, Not by Convenience: One Misplaced Plugin Silently Disabled a Whole Domain

> Column: Knowledge Garden | Collection: Engineering | Source: wiki/projects/desktop client five-domain plugin organization (desensitized) | Status: Drafted · Upcoming

The conclusion first: a desktop client reorganized its preinstalled plugins into five domains: Foundation, Tools & Integration, Experience, Team, and Messaging. The reorganization itself was not hard; deciding ownership was. Which domain a component belongs in depends on what it does, not on where it is convenient to hang it. The real lesson came from a thinking-tag display component that was casually hung under the Tools domain: during an upgrade, the anchor was removed, the whole Tools domain failed to load, and the thinking display silently dropped to zero — no error, no crash, the feature simply was not there. Grouping is an organizational device, and it is also a failure boundary: a wrongly drawn domain costs not one position but a whole slice of functionality.

## Five Domains, Divided by Anchor

Two desktop clients did the same thing on the same day: preinstalled plugins organized into five domains, each with one anchor, and sub-components hung beneath their anchor.

| Domain | Anchor | Sub-components |
|---|---|---|
| Foundation | Account | Brand, model menu, updater, thinking-tag display |
| Tools & Integration | Tool management | Tool catalog, enterprise tools, mount shared library |
| Experience | Browser | Image preview, task grid, session review |
| Team | Team assistant | None (standalone package) |
| Messaging | Messaging | None (standalone package) |

The reorganization changed ownership only, not identity: no package renamed, no new package created. Sub-components were marked as not independently bundled, their bundle patches were removed from the package manifests, and the group manifest wrote each ownership in a flat mapping. Anchor packages had their titles changed to the domain name, and runtime ownership is decided by the anchor's group definition.

The advantage of this approach is that it is light: the organizational relationship lives in a single manifest, so changing the manifest changes the organization. But lightness has a cost: a mistake in the manifest is faithfully reproduced at runtime, and a wrong manifest never complains on its own.

## One Misplaced Component, and the Whole Domain Vanished

The ownership of the thinking-tag display component was one such manifest mistake.

It was first placed in the Tools domain, hung under the tool-management anchor. The reasoning felt natural: like tools, it supports model capabilities. But semantically it is not a tool: it displays tags from the model's thinking process and has nothing to do with tool integration. It was put in a convenient position and the wrong semantic home.

The problem surfaced during an upgrade: the upgrade fixture removed the Tools domain's anchor, the whole Tools domain failed to load, and the thinking display's count dropped to zero. The feature did not error; it silently stopped existing.

The first reaction was to add a workaround: a forced-enable flag on the anchor's patch. But a workaround treats the symptom, not the ownership: the anchor was still in the wrong domain, and the next upgrade that removes it differently would fail the same way. The real fix was to move it back on semantic grounds — thinking display has nothing to do with tool integration, so it returned to the Foundation domain — and the workaround was removed with it, leaving nothing behind.

The difference between the two responses is worth recording: a workaround lets a wrong ownership temporarily cause no trouble; moving it back makes the ownership itself right. The first accumulates; the second settles it in one move. When fixing an ownership problem, first ask "what does it actually do", and only then "how do we get it running for now".

## When Ownership Is Unclear, Stop and Ask

Ownership judgment cannot rely on feel alone, so the reorganization established three rules at the same time:

1. **A judgment table**: the operations handbook gained a five-domain judgment table, each domain stating what it takes in and what it does not. A new package checks the table first; if there is no matching entry, it is not assigned.
2. **Ask the user**: when ownership is unclear, stop and ask the user instead of guessing. A correct guess saves one question; a wrong guess costs one silent failure. That trade is not worth it.
3. **Machine checks**: the release check gained a domain-ownership check: a preinstalled plugin with no domain fails outright, and so does one pointing at a nonexistent plugin. Ownership moved from "someone remembers to check" to "the machine blocks the release".

The three rules divide the work: the table gives people a standard, asking the user gives people a way out when uncertain, and the machine check backs the standard up. Miss any one of them, and ownership slowly slides back to "wherever is handy".

## When Tests Go Red, Ask Whether the Expectations Are Wrong

After the component moved back to the Foundation domain, four repository-level tests went red. The easy first reaction is "the move broke something", but checking each one showed all four were problems with the expectations themselves:

- One test still discovered components using the old domain structure; its expectation had to follow the new contract.
- A plugin-count expectation was one short because upstream had failed to update it when adding a component; it had nothing to do with this reorganization.
- One assertion still demanded standalone-package behavior from a package that had become a sub-component.
- The grouped-expectation table was missing two rows for the new ownership.

The fix was to update the expectations to match the five-domain contract, without changing any ownership or manifest structure to pass the tests. Tests are the yardstick of a contract, not the master of the design: when the yardstick is wrong, adjust the yardstick; only change the design when the design is wrong. Confuse the two, and you will move a correct ownership back just to turn tests green.

Two more failures were false ones: a shared library lagged the source by several hours, so the tests ran against a stale library. A targeted rebuild turned them green with zero changes. The lesson goes in the notebook too: rebuild before running tests, or the red may be the build, not the code.

## Practice: Three Rules for Dividing Domains

1. **Judge ownership by semantics**: which domain a component belongs to depends on what it does, not on where it hangs conveniently or what it ships with. Semantics is the only criterion; convenience is not.
2. **When ownership is unclear, stop and ask**: if the table has no answer and the semantics are ambiguous, ask first, do not guess. One question costs far less than one silent failure.
3. **Put ownership into machine checks**: no domain, or a pointer to a nonexistent component, fails the release outright. The manifest is the single source of organizational truth; when it is wrong, block it — do not rely on human eyes.
4. **When tests go red, check the expectations first**: after a change, ask whether the expectations were written against the old structure. Fix wrong expectations; only change the design when the design is wrong.
5. **Workarounds must expire**: if a workaround is needed to ship, it may go in; but it must be followed by a real ownership fix and removed once the fix lands. A workaround left in place is the seed of the next failure.

## One Sentence to Close

Grouping is not tidying up; it is drawing boundaries: judge ownership by semantics, ask when the judgment is unclear, enforce the result with machine checks — the cost of one misplaced component is a whole domain silently vanishing on upgrade.
