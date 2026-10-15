# One Client, Two Identities: Isolate at Distribution Time, Not at Runtime

> Column: Garden ｜ Collection: AI Infrastructure ｜ Source: wiki/projects/desktop-client-distribution-isolation (desensitized) ｜ Status: Draft

**Conclusion first:** One desktop client codebase ships as two distributions, one for external users and one for internal users. The isolation must be finished at distribution time: app identity, data directory, update source, and login affiliation each stay separate; at runtime, the code never asks "which version am I?" The fewer runtime branches, the fewer openings for cross-contamination.

## What isolation is: a distribution property, not a runtime state

Whatever is fixed at distribution time stays fixed once installed, regardless of runtime config, login state, or network conditions: app identifier, custom protocol, data directory, branding, update URL, and which service login returns to. These go into the artifact, not into a conditional.

Runtime branching is the opposite: code everywhere asking "which version am I," each branch another chance to miss a check. The more branches, the higher the chance one gets missed; miss once, and the external build may reach internal data, or the internal build may update itself from the external channel.

Shipping multi-site switching inside one client looks convenient, but it pushes the isolation burden onto every single decision: each new feature, each routing change, each new service must ask "which version is this" all over again. A decision written in code drifts with the code; a decision written into the artifact never changes once installed. The goal of isolation is not "judge more accurately," but to make the judgment unnecessary.

## Four faces of isolation

1. **Identity**: Each distribution gets its own app identifier, custom protocol, and branding. The OS treats the two installs as two different apps, never as the same one.
2. **Data**: Each uses its own data directory: no migration between them, no overwriting each other. Internal accounts and configuration will not be carried off or overwritten just because the external build got installed.
3. **Updates**: An unsigned package ships with no update source. A signed build's update URL is restricted to its own domain path, so updates can only pull its own packages. An update source is not "a default is provided": no signature means no updates, no configuration means no update.
4. **Login affiliation**: The login page returns to its own service, and model service affiliation belongs to its own side. The external build, once logged in, can only see external services, and likewise for the internal build. Affiliation is decided at distribution time, not by a post-login check.

## Three disciplines

1. **First launch initializes only once**: The first launch generates the default configuration; later shell updates only replace the shell, never touching user configuration or installed plugins. An update must not become an excuse to reset configuration.
2. **Preparation and packaging are separate steps**: Prepare the shared runtime and plugins first, then package; after packaging, re-verify the artifact with the registration and validation functions, never assuming the copy step was error-free. Packagers have default ignore rules: root-level dependencies in the source tree and extra resource mappings must be handled explicitly; check the actual artifact after packaging, not the config file against your imagination. The packaging step itself has traps: do not auto-load a generated config and pass in the same object at the same time, or resources get merged into duplicates; concurrent copies can report file-in-use errors on some systems. Correct config does not equal a correct artifact; verify the artifact against the real files.
3. **Acceptance is layered**: Resource checks, service smoke tests, and GUI installation are three separate layers of evidence; none substitutes for another. Correct resources and a service that starts do not mean the UI installs and works. What is not yet verified is written as "pending acceptance," never as "done." In this real case, GUI installation acceptance could not be completed because desktop access was denied: it was honestly recorded as pending, not patched into a pass with evidence from the first two layers.

## Four anti-patterns

1. **Runtime branching to decide the version**: Version checks scattered through the code; miss one and the two sides bleed into each other.
2. **Shared data directory**: Two distributions writing to the same directory; migration and overwriting are only a matter of time. The cost is not only overwriting: uninstall, backup, migration — any one of these operations can carry the other distribution's data away with it.
3. **Update source without a domain constraint**: If the update URL can point anywhere, the package can come from anywhere.
4. **"The package builds" means "the client works"**: A successful build is only the first layer of evidence; installation, launch, login, and upgrade each need their own acceptance.

## Closing

Permissions are about intersection; distribution is about isolation: [Article 33, "Multi-Space Permissions: Intersection, Not Union"](/writing/33-permission-intersection) is about runtime permission boundaries; this one is about identity boundaries at distribution time. When the artifacts themselves are clearly separated, there is no need to keep judging at runtime who they are. Isolate at distribution time, and at runtime nothing has to prove who it is.
