# Pip Install Succeeded. Inference Still Broke.

> Section: Experiment Log | Collection: AI Infrastructure | Source: wiki/bugs/2026-10-08-PaddleOCR container dependency compatibility | Status: third draft pending review

A troubleshooting session for installing OCR dependencies in a CPU container ended with five pinned version numbers instead of one. Along the way we learned this: **install success, import success, pip check passing, mock passing, and real inference succeeding are five mutually non-substitutable conclusions.** Wherever you stop in the stack, you leave that layer's false negatives to production.

## The Failure Chain: Three Incompatibilities, Falling Layer by Layer

The starting point was a project that needed to run OCR in a CPU container, targeting PaddleOCR 3.0.3.

- **Layer one: auto-resolved transitive dependencies are incompatible.** Only PaddleOCR was pinned, so the installer auto-fetched PaddleX 3.7.2 — whose PaddlePredictorOption constructor signature no longer matched PaddleOCR's expectations. Explicitly pinning PaddleX 3.0.3 cleared this layer.
- **Layer two: an old dependency dragged the resolver along.** PaddleX 3.0.3 depends on old LangChain's docstore namespace; the installer then auto-fetched LangChain 1.x, and the import failed outright. LangChain had to be pinned to the 0.3 series as well.
- **Layer three: undeclared hidden dependencies.** With the first two fixed, Paddle's import revealed a dependency on setuptools that was never declared in the package metadata. Adding setuptools 75.8.0 and removing the leftover unused LangGraph 1.x packages (remnants of the newer dependency) finally made pip check pass.

The final combination: PaddlePaddle 3.0.0, PaddleOCR 3.0.3, PaddleX 3.0.3, LangChain 0.3 series, setuptools 75.8.0. This combination is valid only for this project at this version — not general advice for all Paddle releases.

## Why Auto-Resolution Keeps Hurting You

Looking back, all three failures shared one root: **we pinned only the packages we cared about and left the resolution of transitive dependencies to the installer.** Every `pip install` resolution is an independent decision — the registry state, the other packages, and the resolver's heuristics at that moment all shape the result. You think you are reproducing an environment; in reality you are rolling the dice again each time.

The generalizable version: **pinning granularity must cover "who gets to decide."** If a package's behavior depends on its dependency's version, then that dependency's version is your configuration, not the installer's — whether or not it appears in your requirements file. Configuration you never wrote down is not configuration.

This also explains why "it installed fine last time" problems are always expensive to debug: the two installs never lived in the same version space. You are comparing two different experiments and expecting identical conclusions. A truly reproducible build recognizes only the pinned version manifest, never the historical event of "it installed successfully once."

## Five Proofs That Do Not Substitute for Each Other

The most valuable takeaway of this postmortem is not the version numbers but the evidence ladder:

| Evidence | Proves | Does not prove |
|---|---|---|
| pip install succeeded | The installer finished with this resolution | The resolution repeats next time; dependencies are compatible |
| import succeeded | The module namespace loads | Constructor signatures, runtime behavior, end-to-end paths |
| pip check passed | Declared dependency ranges are mutually satisfiable | Undeclared hidden dependencies; real inference |
| mock / health endpoint passed | Front-end behavior under simulated conditions | Model loading, real data, the CPU inference path |
| real inference succeeded | This version runs on this environment with these samples | Field accuracy, business correctness, no long-term regression |

The follow-up verification ran two layers of real inference: recognizing negative numbers on synthetic images on CPU (confirming the inference path wasn't hallucinating), then OCR on 66 pages of real scans. The latter only proves the parsing pipeline runs; field accuracy and business correctness are a different claim requiring a different evaluation suite. Even a passing real-inference run does not automatically upgrade to "the recognition is correct."

## The Closure Rules: Preventing Recurrence

This recurrence checklist targets one action only — "upgrading a related dependency":

1. **Verify in an isolated image**, never touching the production image; walk the four steps in order: import, pip check, model loading, real-image inference. Skip one layer and the verification is incomplete.
2. **Real images are not optional**: mocks test interface shapes; model weights, CPU operators, and image localization only live in real inference. Keep negative numbers, key fields, and image-localization checks in the verification — those are the traces of an inference path actually exercised.
3. **Persist the model cache independently**: don't re-download models on every build, and don't let cache pollution contaminate conclusions.
4. **Never upgrade wholesale**: whether a new version can replace the current combination still awaits a full independent verification. The version number went up; the evidence didn't — an evidence-less upgrade is a gamble.

One line to close: **dependency problems never surface at the layer where you stopped; they always hide in the layer you didn't verify.**
