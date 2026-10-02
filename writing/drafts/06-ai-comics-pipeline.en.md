# AI Comics Are a Production Line, Not Single-Image Generation

> Column: Build Notes ｜ Collection: AI Infrastructure ｜ Source: wiki/concepts/AI漫画生产与视觉一致性 ｜ Status: first draft

The biggest illusion in AI comics is "write a good prompt and one image pops out." In practice it isn't single-image generation but a continuous production line: character, setting, props, shots, and generation state — five things under control at the same time. Lose any one of them and you get "every panel looks great, but nobody recognizes anyone across panels."

## Before production: turn consistency into checkable constraints

For multi-character, multi-scene work, the first step isn't writing prompts — it's building assets: reusable character traits, outfits, key props, scene anchors. You can't rely on each shot's throwaway prompt — every improvised prompt drifts the character a little further. An empty template doesn't count as a finished production result either; creating the canvas is the starting line, and character sheets, scenes, shots, and generation nodes all still need filling in.

Each batch must also pin four things: model, quality, frame size, and style description. 2D and 3D materials must never mix in one batch — otherwise "consistency" can't even be judged. You can't evaluate a 2D line drawing's contour stability against a 3D render; the yardstick itself would be wrong.

A style requirement like "pure 2D" only means something when expressed as checkable constraints: hand-drawn lines, flat or matte colors, stable contours — with 3D rendering and photorealism explicitly excluded. Adjectives in a prompt are wishes; items on a checklist are constraints. Wishes rely on luck; constraints rely on execution.

## During production: a successful call is not a finished product

This is the easiest trap: a successful generation call only means the task was submitted. You must re-read the canvas state and distinguish success, loading, and error — a node that hasn't finished or hasn't been checked can't be declared a finished product. Between "call succeeded" and "product in hand" lies one state confirmation.

Timeout handling has its own order: re-read the state first, then decide whether to retry. The operation may already have persisted — retrying blindly duplicates nodes or tasks. State is fact; retry is action. The order doesn't reverse, and it belongs in the process, not in the operator's memory.

## Open questions

Three things remain unconfirmed in this method: whether character reference sheets, character bibles, and shot/scene templates need to become an independent versioned asset spec; whether visual consistency needs fixed seeds, image similarity scoring, or human rating sheets; and whether automatic regression evaluation should be introduced. Writing them down isn't weakness — in a production methodology, clearly marking "what's still unsolved" is more useful than pretending the loop is closed.

## In short

The production discipline for AI comics is two lines: before production, pin style and assets as checkable constraints; during production, separate "call succeeded" from "finished product." Single-image generation is a lottery; continuous production is engineering.
