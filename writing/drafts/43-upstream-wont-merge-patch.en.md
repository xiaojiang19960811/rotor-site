# When Upstream Won't Take Your Patch, You Maintain It Yourself: The Lifecycle of a Thinking-Tag Parser Patch

> Column: Garden | Collection: Engineering | Source: wiki/projects/open-source desktop client thinking-tag compatibility (desensitized) | Status: Draft

**Conclusion first:** Upstream rejecting your patch is not the end of the patch. It is the start of its lifecycle: from then on, you maintain it. Merging it into your own branch is only the first step. After that you own the porting, the verification, and the expiry, until upstream adopts it or the patch is no longer needed.

## The problem: thinking content leaked into the body text

When a certain model returns through a gateway over Chat Completions, its thinking content comes in two shapes: without tool probing it travels in a dedicated field; with tool probing it arrives mixed into the body text inside `<think>` tags, and may switch into a tool call before the tag ever closes. A client that only parses the dedicated field will display thinking as body text, and will also expose unclosed tags verbatim.

One detail decides how to fix it: whether the tags are produced by the gateway or by something further upstream was not yet determined. An unfinished root-cause analysis does not mean no fix: first fix what the client can fix, write the parsing rules strictly, and do not wait for the attribution verdict.

## The patch boundary: off by default, on by explicit choice

The new parsing rules carry their boundary inside the patch:

1. **Off by default**: it only takes effect on model entries where it is explicitly enabled, and does not affect other models.
2. **Only the opening**: it only converts the exact tag at the start of a text block. Text outside the tag stays as is. Nothing is inferred to be thinking from content or language.
3. **Tolerates incomplete input**: it supports cross-chunk and unclosed segments, preserves tool calls, and keeps streaming, persisted messages, and replay metadata aligned.
4. **Leaves history alone**: it does not rewrite past sessions, touch the agent core, or touch the UI folding component.

The narrower the boundary, the safer the patch: it solves exactly one problem, tag parsing, and does not refactor the surrounding code along the way.

## Independent review: the author's tests passing is not review passing

After the patch was submitted, an independent reviewer reproduced and fixed two defects: interleaved tool blocks were published early while the tag prefix was not yet recognized; and after an empty thinking tag was stripped, the flow still reported success. Both regression classes failed first and passed after the fix, with parser coverage staying at 100%.

The value of review is not the number of defects found. It is reproduction: the reviewer ran the failing cases by hand instead of only reading the code and offering opinions. A review that only reads code cannot see timing and boundary problems.

## After the merge: four checklists for keeping the patch alive

Once the patch is merged into your own branch, the real maintenance begins.

1. **Directed porting**: the installed client is not overwritten with an old build as a whole. Only the adapter file is replaced, keeping the newer build's other adapter behavior. After verification, the default model is restored to its pre-verification value, leaving no test configuration behind.
2. **Real verification**: unit tests passing does not mean the client works. Real-session verification: one 309-character block of independent thinking, one tool call, no tags in the body text; expand, collapse, and expand again after refresh in the UI, confirmed item by item.
3. **Upstream feedback**: the official contribution guide says external patches are not accepted for now, so the route changes to posting in the official discussion forum, then reading the post back to confirm its body and category. At the same time, a public reference branch is ported onto the official baseline: 200-plus directed tests plus 65 parser, loader, and watchdog tests pass, with parser coverage at 100%. The adopt-or-not decision is left to upstream, but nobody waits for upstream.
4. **Expiry management**: the shared source has not yet absorbed the patch, and the trial package does not contain it either. The patch acceptance of one installed build cannot be extrapolated to another package. Every full-package upgrade or reinstall means porting again and verifying again. A patch is never once-and-done. Every time, the question must be asked again: is it still there, and does it still work.

One more honesty rule: a remote with no CI records is not reported as CI-passing. Whatever layer of evidence is missing gets written down as missing.

## Closing

[Article 42, One Client, Two Identities: Isolate at Distribution Time, Not at Runtime](/writing/42-client-distribution-isolation) is about identity boundaries at distribution time. This article is about the lifecycle boundary of a patch. A PR merge only gives the patch its first home. When upstream won't take it, you keep building that home yourself. As [Article 9, Done Is Not Verified](/writing/09-done-vs-verified) puts it: merged does not mean verified, and the work of keeping a patch alive only starts after the merge.
