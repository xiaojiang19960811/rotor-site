# Before Self-Hosting Open Video Models: Three Boundaries

> Column: Build Notes ｜ Collection: AI Infrastructure ｜ Source: wiki/concepts/MiniMax-H3开放权重与部署边界 ｜ Status: first draft

"Open weights" is not "open pipeline." Before self-hosting an open video model, check three boundaries: the license boundary, the weight-size boundary, and the interface-compatibility boundary. Miss any one of them and it surfaces only after you've paid for the GPUs.

## Boundary 1: The license is not Apache/MIT

Take MiniMax-H3: it ships under the MiniMax H3 Community License, not Apache or MIT. Three concrete constraints follow:

1. **Regional exclusions**: the license explicitly excludes the US, EU, UK, and South Korea. When renting GPUs, verify the server's physical region — the cloud brand or account domicile doesn't count.
2. **Revenue threshold**: commercial products or services with over USD 20M annual revenue need prior written authorization.
3. **Attribution**: commercial product UIs must prominently display the model name.

Open doesn't mean unconditional. Reading the license before buying cards is far cheaper than the reverse.

## Boundary 2: Weight size can't be estimated from parameter count alone

H3's Transformer is a 33B dense model, but the BF16 weights are far larger than 33B suggests. The published component list: two DiTs at ~66.3GB each, a Qwen3-VL encoder at ~51.5GB, a video VAE at ~10GB, and an audio VAE at ~0.6GB.

Two consequences: first, budget disk and VRAM from the component list, not the parameter count; second, deploying a single task partition cuts the load substantially — for first validation, download only `FL2VA` (text/first-last-frame to video) instead of loading both DiTs.

Three officially tested tiers for reference: budget validation on 2x RTX 5090 32GB (~384GiB RAM; 768p, 5s, 50 steps in ~560s, ~78s with Turbo LoRA); recommended production starting point on a single node with 4x H100 80GB (peak ~66GB/GPU); large-VRAM production on 4x H200 141GB (~74-84s end-to-end for the same spec).

## Boundary 3: The open part is not the full official pipeline

H3-Base's `FL2VA` and `Ref2VA` checkpoints are open and deployable via SGLang, vLLM-Omni, Diffusers, or ComfyUI. But H3-Context-IR and H3-Regenerate-2K from the official 2K pipeline are not open. Local 768p runs fully private — it just can't be presented as equivalent to the official 2K API output.

Interfaces have their own trap: same path doesn't mean compatible. Our AI canvas project's generic video branch also uses `/v1/videos`, but its requests are multipart (`seconds`, `size`, `preset`, `input_reference[]`); the H3 local service example uses JSON (`task`, `conditions`, `target`). Integration needs a new adapter or explicit parameter mapping plus a real end-to-end run — never assume compatibility from a matching path.

## In short

Self-hosting an open video model costs less in GPUs than in three boundaries: the license decides whether you may use it, the weight size decides what you'll pay, and interface compatibility decides how much code you'll write. Clear all three before ordering cards.
