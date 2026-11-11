# An Optional Feature Must Not Block the Main Path: A Browser Cold-Start Postmortem

> Column: Lab Notes | Collection: Engineering Tools | Source: wiki/concepts/DSH client plugin slots and takeover (desensitized) | Status: Drafted · Coming soon

Conclusion first: the agent browser plugin of a desktop client made one mode-probing network request during startup, got stuck in asynchronous initialization, and the whole client failed to start. One optional feature held the main flow hostage. The fix came in three layers: activate synchronously at startup and move network initialization to the background; give each of the two browser modes its own login state and capability boundary, with no automatic fallback on failure; and stop accepting backend-only checks, running acceptance in a real client shell instead. The lesson of this postmortem is one sentence: when an optional capability fails to initialize, it may only degrade itself, never the main flow.

## One Optional Feature Held Up the Whole Startup

The scene was a single line in a user log: one entry did not activate during client boot. The entry was the browser plugin, stuck on loading.

The code had put the mode-probing network request inside the client's asynchronous initialization function. A controlled-delay test confirmed the old behavior: whenever that request stalled, the full client startup stalled with it. The log alone only recorded "did not activate", which is not enough to establish the network latency at the time, nor the order in which concurrent triggers fired — so "the network was slow" cannot be written as the sole on-site root cause. The root cause has to be stated precisely: the problem was not a slow network, it was that an optional feature's network request sat on the synchronous startup path.

The new version separates "connection ready" from "client activated": the plugin completes activation synchronously, holds its own background initialization and polling, and cancels and waits on unload; failures go to the browser error console, and the tool does not switch backends automatically. A full-page regression returning service-unavailable confirmed the result: the error is observable, and the main interface stays usable.

The principle is simple: on the startup path, synchronous work only registers "I exist"; networking, probing, and waiting for readiness all go to the background. When an optional feature fails to initialize, it degrades itself, not the whole application.

## Two Modes Are Not the Same Thing

This browser plugin offers two complementary modes, each with its own pages, login state, and capability boundary.

Native mode controls the desktop's built-in browser tabs directly. Its login state clears when the desktop process ends: a restart means logging in again. At present it offers no page screenshots, no uploads or downloads, and no control inside iframes, and browser-side interface operations are not guaranteed to be accepted by sites that demand trusted input.

Screencast mode launches an independent browser and forwards its picture to the sidebar. The independent browser keeps its own persistent login state. Under an empty allowlist it permits ordinary web addresses, domains, and IPs by default, including intranet addresses and other services on the same machine; but the current listen address and known loopback aliases remain refused. A non-empty allowlist keeps explicit restrictions — a permission adjustment the user confirmed.

The two modes do not switch automatically on failure. Switching modes releases the old backend, and the screencast backend waits for the browser to exit and for auditing to finish. An operation already dispatched but not yet confirmed stays blocked; cancelling it is not the same as rolling back its web side effects. More importantly, "there is a web page on the sidebar" must not be read as "the page is natively embedded": a picture being there does not mean control is there.

The user's call on this was "native by default, screencast optional, explicit switching, no automatic fallback", accepting that native mode requires logging in again after a restart. Automatic fallback looks considerate, but it takes the decision — which login state, which capability boundary — out of the user's hands. The mode is a state the user needs to know, not an implementation detail.

## The Backend Being Up Does Not Mean the Client Is Up

There was also an acceptance gap behind this cold-start problem reaching a user: the existing startup check launched the host in a backend-only mode, which only proved the backend and remote calls worked; standalone webview tests never went through the full plugin startup graph either. Both layers were green, yet real client startup could still stall.

Packaging now runs a real desktop shell with the bundled runtime as a separate check: it verifies the carrier's main-process code matches the installation archive byte for byte, uses an independent home directory and user data, and checks that more than eighty client entries start, that the interface stays usable under delayed mode requests, and that the selected backend returns success. Evidence for both native and screencast modes goes into the startup acceptance file, and the upload gate refuses a missing result.

This new check has its own boundary: it does not replace acceptance with a personal account, a real business website, or the interface on another platform. It can only prove what it actually ran.

But the direction is right: acceptance has to run on the layer that actually runs. The backend being up only proves the backend is alive; the client has to say for itself that it is alive. Every layer has its own startup graph, and a green light on the layer above cannot testify for the layer below.

## Practice: Three Rules for Optional Capabilities

1. **Only synchronous registration on the startup path**: networking, probing, and waiting for readiness all go to the background. A plugin activates first, then initializes at its own pace; if initialization fails, only it is affected, and the main interface stays usable.
2. **The mode is a state the user needs to know**: the two modes differ in login state, capability boundary, and failure behavior, and failures do not trigger an automatic switch. Switching must be explicit, its cost stated up front, and automatic fallback must not decide for the user.
3. **Acceptance runs on the layer that actually runs**: backend checks prove the backend, client checks prove the client. Startup acceptance goes into a real shell, a real runtime, and a real startup graph, and a missing result blocks the upload outright.

## One-Sentence Close

An optional feature's first responsibility is not how much it can do, but that it never blocks the main path: let the main flow through at startup first, then initialize itself slowly; modes that differ must not pretend to be the same, and a layer acceptance never reached will sooner or later be repaid with one real failure.
