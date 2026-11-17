# Build Denied on Permissions, but the Label Sat on the Repo Root

> Column: Lab Log | Collection: Engineering | Source: wiki/bugs/multi-model-gateway repo-root Low integrity label blocking the frontend build (desensitized) | Status: Drafted, coming soon

The conclusion first: a release build failed twice in a row at the same step, with esbuild reporting "access denied" while writing temp files — the error pointed straight at the temp directory. But layer-by-layer checks found the real cause at the repository root: the whole repository carried an explicit Low integrity label, every file inherited it, and the build process therefore ran at low integrity, with the system refusing its writes and deletes of temp files. Raising the label to Medium fixed it in one pass: 1,089 modules in 33 seconds. Where an error is reported is not necessarily where the fault lies; with a permissions failure, ask whose permissions first, then where.

## The error pointed at the temp directory

The release build failed twice at the frontend build's "rendering chunks" stage, with the same error both times: esbuild was denied access while writing a temp file, the error carried back by esbuild's service process. The natural first suspect was the temp directory: its permissions, its free space, its leftover files.

But one detail did not fit: if the problem were the temp directory, why did the workaround verified in the previous release fail too? That release had used a standalone esbuild binary to sidestep an old package-manager hard-link problem; this time the same standalone binary failed identically. The temp directory had not changed, the workaround had not changed — something else had. Two stable failures meant this was not a flake, but a reproducible blocking point.

Only the repository's own frontend build verification was affected; already-released artifacts were untouched, and after the fix the release built cleanly and shipped.

## Layer-by-layer checks found the repo root

The investigation did not start at the place the error named. It checked integrity labels level by level, from the repository's parent directories down.

The parent chain was clean — no labels anywhere. The repository root itself carried an explicit Low mandatory label, with no inheritance marker, able to propagate to child objects. Every file in the repository inherited that Low label, including the frontend directory and the standalone esbuild binary. The build process ran at low integrity, matching the executable's label, and the system refused its writes and deletes of temp files.

The timeline fit as well: the same script with the same binary had built successfully in the previous release, so the Low label must have been set on the repo root afterwards. Who set it was never found out, and no guess is offered — that, too, belongs in the conclusion: unknown means unknown.

Two traps are worth naming here. First, the command to remove deny entries reported "success" without taking effect: it only acts on deny-type access entries and cannot touch a mandatory label entry — a command succeeding does not mean the label was removed. Second, the source of the label remains unidentified; if it recurs, the introducer has to be traced from the access entries' origins, not by suspecting the temp directory a second time.

## The fix: back up first, overwrite second

The fix had two steps, in an order that must not be reversed.

1. **Back up the access control list first**: save a copy of the repo root's access control list before touching the label. A label changed wrongly can be restored; without a backup, the only option is guessing from memory.
2. **Overwrite the label to Medium**: set the repo root's integrity label to Medium, equivalent to the system default, with child objects' inherited labels updating along with it. After the fix, the full frontend build script ran clean — type checks and the build all passed, 1,089 modules in 33 seconds.

Medium is not "loosening permissions" but returning to the system default: a Medium-integrity process faces no extra restriction when operating on objects at the same level. A Low label exists to constrain untrusted code; finding it on a repository root is itself a mislabeling.

## The practice: locate a permissions error by layers

1. **The reported location is not the root-cause location**: the build error named the temp directory; the cause sat on the repo root. Ask whose permissions were denied before asking where the error was reported; fixing the literal wording of the error fixes the symptom.
2. **A stable failure rules out flakes before suspecting the environment**: two identical failures rule out jitter; when a workaround verified in the previous release also fails, the change is not in the workaround but in the environment around it.
3. **Check permissions level by level, not only at the level the error names**: directory, parent directory, repo root, one level at a time. A label can be inherited or set explicitly at one level; checking only the level the error names will never find an explicit label one level up.
4. **A command reporting success does not mean it took effect**: the deny-removal command reported success, but it cannot reach mandatory labels. Every fix command has its own scope; a successful run only proves the command finished, not that the target state changed — re-verify the state after changing it.
5. **Back up before changing a system attribute**: save a copy of the access control list before changing a label. The ability to roll back is not added afterwards; it has to exist before the change is made.

## One line to close

The build was denied on permissions, but the label sat on the repo root: locate a permissions error by layers — where the error is reported is only the symptom; the cause lives on whichever level carries the label.
