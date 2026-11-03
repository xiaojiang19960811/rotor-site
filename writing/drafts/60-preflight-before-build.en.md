# A 100-Minute Release, Only 12 Minutes of Building

> Column: Lab Log | Collection: AI Infrastructure | Source: wiki/decisions/dual-platform release speedup decision (desensitized) | Status: Drafted, coming soon

The conclusion first: one dual-platform desktop client release took about 100 minutes, of which the genuinely necessary build and release took only about 12 minutes: 7 minutes to build, 5 minutes to release. The rest was not slow execution, but rework: problems that could have been found before building were instead found inside the build loop, so every fix cost another full rebuild.

## Where the Time Went: Only 12 Minutes Were Necessary

The rework concentrated in four places. First, taking over a leftover site: connection details, on-site confirmation, and the plan were only sorted out at the start; the checkout sat on an old commit, carried uncommitted changes, and its dependencies lagged behind the lockfile, so every release began by cleaning up the previous round's site. Second, a missing package was only found by a failed build: the first build ran for minutes before reporting a missing dependency, while whether dependencies matched the lockfile is something a single read-only command can check. Third, signing material went back and forth: the signing material path did not match, each repair failed once more, and several rounds passed before it recovered. Fourth, the evidence checklist was patched in two rounds: it first missed the delta package, then missed the nightly source, so the same checklist's gaps were filled in two separate passes, burning two full builds for nothing.

Two further accidents also occurred: network jitter caused a runtime download to fail, and returning artifacts accidentally dragged along a whole staging tree. Neither was a problem with the build itself, yet both landed after the build and could only be closed by rebuilding or re-uploading. None of these segments looks large on its own; added together, they stretched a 12-minute job to about 100 minutes.

## Root Cause: Discovery Was Placed Inside the Build Loop

The root cause fits in one sentence: the **discovery** step was placed inside the **build** process.

1. **Read-only checks entered the build loop**: whether dependencies match the lockfile, whether signing material is in place, disk space and leftover output directories, and network reachability can all be checked without building. When the check comes late, its price rises from one command to one rebuild.
2. **The previous round's site was never cleaned up**: checkout state, uncommitted changes, and dependency versions are things that should already be clean when a release starts. Starting with a leftover site means every step can trip over the previous round's pit.
3. **One fix per run**: the evidence checklist's gaps were never checked in full at once, so filling them in two rounds meant paying the build cost twice for the same checklist. Whenever a checklist depends on someone remembering to fill it each time, gaps arriving in batches are inevitable.
4. **One fact, two definitions**: the release evidence check held one list of required files, while the packaging step hand-wrote a second matching rule, and two definitions are bound to drift. The result of drift is not that one side is wrong, but that every release needs manual reconciliation.
5. **Editing a script forced a full rebuild**: the release script was tightly bound to the build artifact, so changing one line of release script required a rebuild. Once iteration costs that much, people tend to run it once and see, instead of completing the checks first.

## Two Rules: Preflight First, One Definition

Against these five points, two rules were set.

The first is to **verify the machine and checkout state completely before starting**, so no known failure enters the build stage. One preflight covers both platforms, checking checkout state and target commit, toolchain, whether dependencies match the lockfile, signing material, release credentials, network reachability, leftover output from this version, and disk space. Platform differences are still covered by each platform's supplementary checks, but the shared part runs as one set, not one preflight per platform. The preflight standard is: any problem that can be found read-only before building must not be left to surface inside the build.

The second is to **maintain the evidence file set in exactly one place**. The release evidence check and the packaging step both derive from the same definition, and the check list no longer hand-writes a second matching rule. When the set changes, every step changes together; when it does not change, no step may add or drop items on its own. This makes gaps structurally impossible, instead of relying on someone remembering to fill them at each release. Differences between the two platforms' file sets are also written into the same definition, with cases locking each platform's set, instead of letting each platform keep its own list.

## Target Flow: About 15 Minutes

Rearranged under these two rules, the target flow is about 15 minutes:

1. **Remote readiness preflight**: one command runs the shared preflight.
2. **Sync the checkout**: sync to the target commit, with a clean worktree.
3. **Verification without building**: tests and checklist editing rehearsed offline, without triggering a build.
4. **One build**: cache hit, one pass.
5. **Return by checklist**: artifacts checked one by one against the checklist and returned.
6. **Upload and acceptance**: upload, checklist switch, and acceptance to close.

The key to this flow is not that any one step got faster, but that every failure's discovery point moved earlier: a failure in the preflight stage means fixing the environment and the checklist, without burning a build; the build stage is left with only genuine build work.

## Three Things Not Yet Done

Honestly, three things are still not in place. First, editing only the release script should no longer trigger a full rebuild: the tight binding between release script and build artifact has not yet been loosened, so the iteration cost of editing scripts is still high. Second, a network failure should fall back automatically to a usable mirror, instead of waiting for human judgment. Third, artifact return should be scripted: fetch files one by one against the checklist, with whole-directory recursive copying prohibited. All three point in the same direction: turn things that rely on someone remembering into things that structurally cannot go wrong.

## One Sentence to Close

A slow release is usually not a slow build, but late discovery: move every read-only check before the build, keep one definition for each fact, and only then does the build deserve to take just 12 minutes.
