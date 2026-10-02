# Video Pipeline: v2 to v4

> Column: Build Notes ｜ Collection: Solo Building ｜ Source: Xiaohongshu video pipeline log (~/workspace/xiaohongshu/, memory/2026-10-01.md, memory/2026-10-02.md) ｜ Status: first draft

The daily AI-news videos for Xiaohongshu went through pipeline versions v2 to v4. Every version bump was a user-review rework. Looking back, the traps in video production weren't about how good the visuals were — they were the things in the delivery checklist everyone assumed were there.

## v2: a pipeline that runs

v2 was the first production pipeline that actually ran: 1080×1920 vertical, fifty-odd seconds, one script rendering the finished piece. Daily publishing depended on it: video on odd days, image-text posts on even days, automatic fallback to image-text if video rendering failed. The content side has two iron rules: news only enters a video after dual-source verification; topics are deduplicated — what shipped yesterday is skipped today. Behind a 60-second video are four steps, "verify, dedupe, render, review," not "run a script."

v2 solved "does it exist." It moved, the flow ran, but it had engineer aesthetics: all the information was on screen, pacing and packaging unconsidered.

## v3: packaging fixes from user review

After the v3 sample shipped, a round of packaging fixes followed review notes: a golden 3-second hook, self-synthesized copyright-free BGM, keyword highlights, next-item teasers, follow/comment prompts at the end; plus title cropping, empty first frames, empty tag boxes, and side-button occlusion.

Every one of these is a "you only see it in the finished piece" problem. They don't exist in storyboard descriptions — whether a title gets cropped is only known after rendering; whether buttons cover text is only known after the UI overlays. Template reviews must watch the finished piece, not the proposal.

The v3 sample passed verification, but production didn't switch: it waited for the user's call. A production pipeline doesn't switch because "the new version looks better" — switching is a separate decision.

## Production incident: subtitles and BGM missing

v2 failed in a real production run: after delivery, the user reported "no Chinese subtitles and no BGM." Investigation showed the render script produced visuals only — the final assembly had skipped subtitle burning and BGM mixing entirely. The pipeline never treated those two steps as mandatory.

Rework produced a re-pressed version with subtitles and BGM added. The lesson became a hard requirement: subtitles and audio are part of the delivery checklist, not "add it in post." The user wants Chinese subtitles — confirmed first at every review since.

## v4: new design language, one more rework

The user asked for an award-winning design style, and v4 shipped in that direction: deep black background, electric green, giant outlined numerals, word-by-word rising titles, monospace kickers, hand-drawn-style visualizations, film grain, a bottom progress bar — visuals sharing DNA with the personal site.

Review surfaced two notes: Chinese subtitles were missing again, and it "lacked a certain feeling." The first is a checklist problem, the second an aesthetics problem — neither can be fully specified before the work, only reworked after watching. After revision, the user approved v4 as the official production template, replacing v2 in the daily pipeline.

## Three production disciplines

1. **Checklist first**: subtitles, audio, cover art are mandatory checks, not afterthoughts to "the visuals." One miss is one rework.
2. **Review the finished piece**: title cropping, button occlusion, empty frames — every layout problem exists only in the rendered result. Proposal reviews can't substitute.
3. **Switching production is a separate decision**: a verified new version doesn't mean an immediate production swap. The v3 sample was fine, but daily publishing stayed on v2 until the user explicitly approved v4.

## In short

Iterating a video pipeline means turning "assumed present" into "must be on the checklist." v2 proved it runs, v3 fixed packaging, v4 changed the language — every rework came from a real review. The scariest thing in automated production isn't slowness; it's nobody watching the finished piece.
