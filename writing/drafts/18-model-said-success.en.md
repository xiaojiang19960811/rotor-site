# The Model Said "Success" — Prove It

> Column: Garden ｜ Collection: Agents & Digital Humans ｜ Source: wiki/concepts/Qwen-CUA与计算机使用智能体 ｜ Status: first draft

In computer-use agents, "the model said it succeeded" is just an output, not a conclusion. Whether the task truly completed must be confirmed by the runtime or a human against verifiable external state. Splitting decision from execution is the architecture's first principle.

## Two things first: the model and the runtime

Qwen-CUA, jointly released by the Qwen team and XLang Lab, is a screenshot-driven computer-use model plus reference implementation. To understand it, separate two components:

- **The model**: understands instructions and screenshots, tracks task progress, and proposes native actions based on the visible UI. Its core constraint is working from screenshots, not hidden application state: no DOM, no accessibility tree, no terminal, no task-specific APIs — just clicks, drags, scrolls, key presses, and inputs in a normalized coordinate space.
- **The Agent runtime**: captures screenshots, manages multimodal history, validates and executes actions, triggers human confirmation, and saves replay evidence.

The boundary means something direct: the model outputting "I'm done" and actually being done are two different things. One is a token sequence; the other needs runtime verification.

## Three reusable engineering principles

The reference architecture distills three principles that hold in any Agent system:

1. **Separate model decisions from action execution**: the runtime validates model output — a model response never becomes an unconstrained system call. The model thinks; the runtime gatekeeps and acts.
2. **Human gates on sensitive actions**: password entry, uploads, downloads, form submissions, cross-origin navigation all need human review. What can be automated and what must be seen by a human split along risk.
3. **Bind success claims to external evidence**: built-in labs verify against explicit UI states deterministically; custom runs are always marked unverified — never let the model's self-report substitute for result verification.

The third deserves unpacking. The correct way to verify "booking succeeded" is to check the order status, not to hear the model say "I saw the confirmation page." Between what the model saw and what actually happened lie rendering, network, popups, and expired login sessions — any link can turn a self-reported success into a false positive.

## Vendor numbers are reference only

Qwen-CUA reports 86.2 on OSWorld-Verified, with larger variants reporting 87.6. These come from the project's README and technical report — self-reported results, never independently reproduced.

They're useful for understanding the project's goals and training methods, but they don't translate into production success rates. Benchmarks run clean; real business has login states, resolution differences, long flows, and dirty states of every kind. Treating a benchmark score as a launch success rate upgrades a "lab conclusion" into a "production conclusion" — the exact evidence-level mismatch from the earlier article on verification.

## Dividing work with traditional automation

Vision agents and Selenium/Playwright scripts aren't replacements for each other:

| Dimension | Vision agents | Traditional scripts |
|---|---|---|
| Input | Screenshots + natural language | DOM, selectors, programmatic assertions |
| Actions | Model decides dynamically from the current screen | Developers pre-write deterministic steps |
| UI changes | Can attempt visual re-targeting and recovery | Usually need selector updates |
| Proof of result | Needs runtime validators, replay, or human review | Explicit assertions and test reports |

Notably, Qwen-CUA's own demo uses Playwright for isolation and browser action execution — deliberately without exposing the DOM to the model. The sane production split: traditional automation handles deterministic execution and verification; vision agents handle UI understanding and recovery that's hard to pre-program. The former guarantees the floor; the latter extends the ceiling.

## One security reminder

Screenshot-driven doesn't mean safe. Page content can still steer the model into wrong actions via prompt injection. Isolated browsers, URL restrictions, and action approvals only reduce risk — they say nothing about each real action's business consequences. Permissions, money, formal releases, and external writes need independent human confirmation and post-hoc checks.

## In short

The model decides from screenshots; the runtime verifies in the real world. Treating "the model said success" as "it really succeeded" is letting the student grade their own exam.
