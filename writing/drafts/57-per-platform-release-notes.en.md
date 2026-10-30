# One Release Note Field, Two Platforms: The Top Level Will Mix Them Up

> Column: Lab Log | Collection: AI Infrastructure | Source: Dual-platform client release-notes split review (desensitized) | Status: Drafted, upcoming

The conclusion first: a release note is not an attribute of "this release" but of "this platform, this version." Two platforms shipping independently but sharing one top-level note in the manifest will mix up their notes — not by accident, but because the data model got the granularity wrong. Notes must live on the platform entry, and a missing note must fail the release, not be papered over with a template sentence.

## A New Release, Wearing the Other Platform's Notes

A dual-platform desktop client ships Windows and macOS independently. On one Windows release, no note was supplied for that platform, so the release tool wrote only a template sentence into the top-level note of one manifest. The download page, however, reads a different manifest, whose top-level note still held the previous macOS publisher's text.

What users saw on the download page was this: the new Windows release, beside the macOS notes. The version was right; the notes were wrong. Nobody edited the wrong page, nobody pasted the wrong link — the page simply read out the top-level note, faithfully.

This is not a page bug. The page cannot judge "which platform does this note belong to," because the data contains no such information: the top level has only one slot, and two platforms take turns writing into the same cell.

## Why a Top-Level Field Inevitably Mixes Platforms

Two platforms shipping independently means three things differ each time: ship time, version, and note content. The top-level field, however, is only one: it can represent one platform at a time.

So the mismatch arrives in two forms, and both will happen:

1. **Later writes overwrite earlier ones**: one place is updated, the other is not, and the old note keeps hanging beside the new release.
2. **Two manifests, each writing its own**: the top-level notes of the release manifest and the download manifest are not the same data — one got a template, the other still holds old text, and the one being read happens to be the old one.

Either way, users see the same symptom: a version and a note that belong to two different platforms. If troubleshooting only checks the page and the links, it will never find the root cause, because neither the page nor the links are wrong. The root cause is in the data model: the granularity of note ownership is one level coarser than the granularity of shipping.

## The Fix: Sink Notes into the Platform Entry

The fix is not "remember to bring a note next time" but turning "remember" into "no note, no release":

1. **Notes follow the platform**: in every manifest, the note sits on that platform's own entry, and a historical version's note sits on that version's entry for that platform; the top level keeps only a summary and no longer plays the role of "this release's notes."
2. **A missing note fails outright**: if a release lacks any platform's note, the release process fails directly, with no template sentence as a fallback. The problem with a template sentence is not that it is badly written — it disguises "not written" as "written," making a gap in the manifest look like a completed release.
3. **Switching must verify the other platform is unchanged**: when switching manifests, besides the current platform's change, the other platform's entry must be checked field by field: everything except notes stays identical. Verifying only the current platform cannot catch a mix-up.
4. **Backfilling reuses the published artifact**: when adding notes after the fact, reuse the artifact that was already published — do not rebuild, do not overwrite the first release's backup. Fixing notes should not quietly replace what users are downloading.

The download page was rearranged to match: the top "current version" summary went away, replaced by one card per platform, each showing its own version, size, time, checksum, and a collapsible note for that release; historical versions expand per platform, each with its own notes and download rows. Once the page structure matches the data structure, a mix-up has nowhere to hide.

## Historical Notes: Better Missing Than Invented

Backfilling historical notes follows one more rule: ownership is judged by whether a note names that platform and that version. If it matches, reuse the original text; if it does not, do not write one up, do not guess, do not move another platform's note over.

For a version that never had its own note saved, the backfill states plainly that no separate note was saved for that version. That sentence is not pretty, but it is true; an invented note would look pretty and would turn fabrication into release history. The first rule of release records is telling "written" apart from "never written."

## One Line to Close

The granularity of notes must match the granularity of shipping: as many platforms ship independently, that many note fields are needed; sharing one top-level field makes a mix-up only a matter of time.
