# UI Should Only Claim What's Proven

> Column: Garden ｜ Collection: Engineering ｜ Source: wiki/decisions/2026-09-08-va-studio资产库V8状态语义收口 ｜ Status: first draft

When our video workbench's asset library went through its V8 redesign, we set a rule that looks dumb: no unified asset status field. Every page may only display facts the underlying data object can prove. Generation progress, shot review, project phase, and export artifacts are expressed separately — never blended into one pretty "Done."

## Why no unified status

The library manages two kinds of things: composite assets under film projects, and standalone assets (images, video, audio, novels, scripts, prompts, characters, digital humans, scenes, props, storyboards, finished films). Each type's "status" means something different — forcing one library-wide "pending/delivered" invents business facts in UI language.

The settled rule: each object displays only what its type can prove.

## The status boundary table

| Object | May display | Never displays |
|---|---|---|
| Ordinary assets | Stored, source, project ownership, version, read-only derivatives | Processing, pending confirmation, delivered |
| Novels | Draft, usable, needs revision, compliance block, submission check results | Confirmed, delivered |
| Scripts | Draft, generating, usable, failed, version | Confirmed, delivered |
| Shot renders | Queued, rendering, rendered, failed; needs review | "Needs review" belongs to its shot only, never the whole film |
| Task records | Queued, running, done, failed | Task done ≠ asset confirmed |
| Export artifacts | Compositing, film generated, export failed, downloadable | Downloadable ≠ user accepted |
| Audio assets | Ready, copyright pending, project-internal only, commercial-use OK | "Pending" only in copyright context |

Three sentences most likely to be written wrong were nailed down: task done doesn't mean asset confirmed; downloadable doesn't mean user accepted; a project's "completed" means production phase only, never delivered.

## Never invent a unified API

The same rule governed interaction design: page navigation references only real existing frontend routes — no invented unified asset-detail endpoint. Click paths were reviewed across three swimlanes — entry and page jumps, asset details and relations, tasks and export facts — every path traceable to an existing route, with no "coming soon" placeholder links.

The relationship diagram states five record boundaries plainly: asset records are saved content, task records are generation processes, shot records are generation results plus review, project records are production phases, export artifacts are whether the film exists. User acceptance isn't recorded by the system today, so it says "not recorded" instead of inventing a status to fill the gap.

## Full-text verification

After the redesign, a full copy scan found none of the status words — "pending," "delivered," "releasable," "confirmed" — anywhere in the library. The sole exception is audio's "copyright pending," kept strictly inside the copyright field's context.

Quantities and examples in the design mockups are demo data and must be replaced by API responses on implementation — not even demo data may pretend to be real state.

## In short

Honest UI copy is one sentence: say what the data can prove; what it can't prove, leave unsaid rather than inventing a flattering status. The rule is clumsy, but it means every sentence on screen traces back to something in the database.
