# Proxying Third-Party Media APIs: Discipline Over Magic

> Column: Build Notes ｜ Collection: AI Infrastructure ｜ Source: wiki/decisions/2026-07-15-infinite-canvas-grok-xai-media-chain ｜ Status: first draft

When integrating third-party media APIs (image and video generation), the real pitfalls aren't in "getting it working" but in the media chain: upstream returns temporary URLs, browsers time out on cross-border direct connections, and cache semantics are opaque — nobody tells you when things expire. Our approach compresses to three lines: same-origin proxy with streaming and no disk cache; evidence, not guesses, in troubleshooting.

## The media chain: same-origin proxy, no disk

Upstream video completion returns temporary URLs that browsers on domestic networks routinely fail to download or play directly. The production solution is a same-origin media proxy: the frontend rewrites the upstream domain to a site-local `/media-proxy/...` path, and Nginx in the container reverse-proxies streams to upstream. The video proxy never writes to disk — pure forwarding.

Implementation hit two concrete pitfalls: an IPv6 resolution issue and Nginx variable `proxy_pass` dropping the path. Both belong to the "works in config, breaks on a different network in production" category — verifiable only on the real chain.

## An asymmetric risk: reachable locally, blocked from the server

The image-editing chain exposed an asymmetric risk: temporary URLs returned by upstream image editing open fine in the user's own browser, but the server's outbound requests get a 403 from upstream. The Nginx proxy that works for video can't be copied over to images as the formal solution.

The fallback at the time: when cross-origin fetch fails, read the image dimensions and keep the remote URL so the whole edit doesn't fail. But the cost must be written down: its storage key is empty, it depends on the upstream temporary URL, and long-term availability isn't guaranteed after expiry. A fallback isn't a fix — it's a compromise with an expiration date.

## The handling window: 4 hours is a ceiling, not a promise

Upstream only documents image and video URLs as temporary resources, asking you to download or process promptly, with no fixed deletion timeline published. Measured Range requests returned a `Cache-Control` of about 4 hours — engineering treats this as the maximum safe handling window and persists content as soon as possible, not as a promise that "it will definitely be there within 4 hours." Treating an observed cache lifetime as a retention promise is a common form of self-comfort.

## Protocol details: follow the docs, not your imagination

Upstream media protocols are full of "seems obvious, actually wrong." Reference-video mode must distinguish editing from last-frame extension — different endpoints; one reference video per call, never mixed with reference images. When converting image edits to upstream JSON, the image object uses the `url` field — our earlier implementation sent `image_url`, which upstream doesn't recognize.

Response formats can't be hardcoded either. Never label every return as `data:image/png` — upstream currently returns JPEG, so construct Data URLs from the response MIME or file magic bytes. OAuth media requests and text requests use different hosts and identity headers; don't flatten them into "OAuth always uses one host." Every one of these was checked against official behavior item by item. None of it was guessed.

## Troubleshooting discipline: no root cause before A/B

One "duplicate image" incident is worth writing down. Symptom: upstream occasionally returned duplicate images; suspects included canvas reference corruption and browser caching. The method was hash comparison: prompt and upstream request-body hashes checked out, decoded image hashes matched the client-downloaded file, and the anomalous image's hash matched the original canvas export byte-for-byte — ruling out canvas corruption. Meanwhile the anomalous requests took only 140–354ms total, far off the timing profile of a fresh image generation, more consistent with upstream quickly returning existing material.

The conclusion was deliberately restrained: the confirmed fault boundary is "the content upstream returned was itself duplicated"; why upstream fast-returns old images for non-standard clients is unobservable. The correct fix is to atomically align official media hosts, identity headers, and request fields, then run one billed A/B with a unique prompt. Until that A/B completes, no single field may be written up as "the confirmed sole root cause."

## Retry and billing discipline

Generation requests don't go through generic auto-retry. Following official client behavior: refresh credentials and retry exactly once after the first 401; fail directly on 403. Blind retries burn real money.

Billing likewise: charge by the number of images actually returned — on zero images, never fall back to "but we requested n." The denominator must be what really happened, not a request parameter.

## In short

The engineering discipline for third-party media APIs is one line: separate "looks like it works" from "evidence proves it works." Proxies solve reachability, the cache window solves timeliness, A/B solves root-cause attribution — the three must never substitute for each other.
