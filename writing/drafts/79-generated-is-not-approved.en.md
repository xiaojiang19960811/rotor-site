# "Generated" Is Not "Approved"

> Column: Knowledge Garden | Collection: Digital Human Agent | Source: wiki/concepts/AI Content and Generated Asset Approval Boundary (desensitized) | Status: Drafted · Coming Soon

The conclusion first: between generation and publication, content passes through four separate zones: a read-only input zone, an approvable output zone, a formal asset zone, and the side governance domains of memory, tasks, and accounts. Compressing those four zones into a single "content status" is where most approval failures begin: a finished generation is treated as approved, visibility is treated as publishable, and a draft is treated as a formal asset.

## Four Zones, Each Minding Its Own Business

The read-only input zone holds source material: user letters, world letters, exploration records, and private-message outputs. Its job is traceability and context, not production. Read-only means read-only in the literal sense: rendering the page must not quietly attach writes, autosaves, or status advances to it. Viewing a source should never change the source's state.

The approvable output zone holds results awaiting a decision: public drafts, creative versions, and pending publications. Every item here must display its source, topic, version, status, and approval action together. Missing any one of them, the reviewer is reviewing blind: no idea where the content came from, which version it is, or who touched it before.

The formal asset zone holds only things that passed an explicit publication rule. The only way in is by completing the publication or approval rule. Content that has not completed it is not a formal asset, no matter how widely visible it already is on screen.

The side governance domains are everything else: memory, growth, task execution, access control, accounts, organization permissions, and run logs. Each maintains its own state; sharing one backend is no reason to share one content state machine. A memory version is not a content version, and a finished task is not a published piece of content.

## Four Inequalities

The boundary can be written as four inequalities, each matching a real class of failure:

1. **Generated is not approved**: an external generation job producing output only means the creative step finished. Content review, source verification, and publication authorization are three further gates, and none of them is satisfied by "it ran".
2. **Visible is not editable**: being able to see a piece of content does not mean having permission to change it. What is shown must rest on the state, source, and permissions already present in the API and the database, not on what the page happened to draw.
3. **Editable is not approvable**: the person who can edit a draft is not necessarily the person who can release it. Approval actions need server-side permission and an audit record; they cannot be governed by whether a front-end button is shown or hidden.
4. **Approvable is not published**: content that entered the approval queue, or even content someone already approved, is still not a formal asset until the publication rule has actually run to completion.

Taken together, the four inequalities say one thing: a status may only advance by completing its own process; it may not borrow another status's name. Drafts, candidate fields, and AI suggestions cannot be auto-promoted to formal status — a direct consequence of the knowledge base's decision separating formal rules from candidate information.

## The Interface Must Not Vouch for the Rules

This boundary is easiest to break on screen. Asset lists and workbenches may organize density, sources, and versions from real operating data, but they must not fabricate covers, statuses, counts, or media relationships just to fill the frame. Whatever appears on screen, users take as real: a drawn cover is taken for an existing finished piece, and a label reading "published" is taken for a completed process.

Likewise, public content, private-message output, research material, and internal operating drafts have different audiences and retention boundaries, and front-end labels alone cannot separate them. A label is a display device, not an isolation device. Isolation rests on server-side state, permissions, and audit: who can view, edit, generate, review, and export, each step grounded on the server.

The content center must also stay within its own remit: it organizes content consumption and the approval entry point; it does not replace the memory center, the growth observatory, the task queue, account management, or the permission center. One entry point does one job, then hands the result to the next system, instead of pulling every system into one page and pretending a single state machine covers them all.

## Three Rules for Every Content System With Approval

1. **Zones before flow**: separate read-only input, approvable output, formal assets, and side governance domains first, then discuss how each item moves. With unclear zones, a finely drawn flow chart is only wiring laid on a wrong foundation.
2. **Status advances only by rule**: every status change must correspond to an explicit rule and an authorized, audited operation. Front-end rendering, autosave, and page navigation are never reasons for a status to advance.
3. **Display only what is real**: every status, count, cover, and relationship on screen must rest on facts already present in the API and the database. A display slot with no fact behind it is better left empty than filled with placeholder content pretending to be real.

## Closing

In a content system, status is not decoration; it is a record of authorization. Generated, editable, approvable, and published are four different powers carrying four different responsibilities. The day they are collapsed into one word, approval is left with only its form.
