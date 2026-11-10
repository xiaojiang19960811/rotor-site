# Taking Over a Slot Means Taking Over Its Full Cost

> Column: Knowledge Garden | Collection: Agent | Source: wiki/concepts/DSH client plugin slots and takeover (desensitized) | Status: Drafted · Upcoming

The conclusion first: in a plugin system, taking over a UI slot is not "changing the skin" — it is "taking over a post". When the built-in component is shadowed, it stops rendering, and everything it brought disappears with it: grouping, archiving, renaming, and the entry for creating a new workspace are all gone. If the takeover only draws its own new interface without restoring those old capabilities, the user loses not one component but a whole path of operations. Before taking over, list everything the shadowed component used to provide, then decide what you will rebuild yourself and what you will explicitly give up.

## There Are Three Kinds of Slots; Takeover Only Happens in Single Slots

The client assembles pages from slots, and a plugin can only register into a slot that has already been declared. Registration must wait for the declaration to appear, be removed when the declaration folds away, and re-register when it is declared again; registering directly into an undeclared slot errors at load time.

The three kinds of slots have different semantics:

1. **Single slots**: one position renders one component, ordered by priority, and the one ranked first wins. To shadow a built-in component, use a priority that ranks ahead of its default.
2. **List slots**: multiple components stack in order, each occupying its own space.
3. **Keyed slots**: also stacking, but distinguished by key, suited to a set of independently switchable entries.

Declaring someone else's slot errors the same way, and the props a component receives are derived by the framework; business components never touch the framework context directly. The rules are strict, and rightly so: a slot is the contract between plugin and host, and the clearer the contract, the clearer the boundary of a takeover.

## The Shadowed Capabilities Do Not Come Back on Their Own

One real takeover happened in the sidebar workspace: a digital-human agent replaced the built-in workspace browser with its own workspace view. The moment the built-in component disappeared, so did everything it brought: workspace grouping, archiving, pinning, renaming, and the entry for creating a new workspace all vanished. If the takeover wants an orderly exit, it must list fallback entries such as "other sessions" itself; otherwise, once users leave the takeover view, there is no way back.

A takeover must also respect two boundaries:

1. **Opening a session goes through a service, not through props**: the standard hooks can read the session list and running state, but opening a session must go through the UI service. When the service is missing, the view should degrade to "list only, no jumping" rather than clicking with no response.
2. **The narrow column must be drawn by the takeover**: when the sidebar folds into a narrow column, the shell only tells you "it is narrow now"; what it looks like is the takeover's job. The ability to expand the sidebar is provided by the shell and must not be reimplemented by changing the layout.

There is one test for whether a takeover is good enough: after the takeover, can users do more or less than before? Less means the takeover owes a debt.

## Installation Timing Matters More Than Installation Itself

Two pitfalls the takeover ran into both came down to "when things get installed".

A shared stylesheet must be installed before the views that depend on it are registered and mounted, usually while the plugin activates. Installing it only inside a panel component is too late: the sidebar renders first and gets a row of unstyled bare buttons, because component rendering happens before the panel first mounts. Optional views that only activate after a mode is chosen must also have their styles installed before they register.

A palette shared by multiple components should not be read from persistent storage by each component separately: persistent writes happen inside effects, later than the same render round, so an early read gets the old value. The right approach is a module-level current-theme variable that all components read from.

Both rules say the same thing: the installation order of a plugin is itself part of the feature. Installed late is installed wrong.

## Different Activation Paths Need Different Verification

The client bundle's URL carries a content hash, so after repackaging and installing the client script, refreshing the page loads the new version with no app restart; changes to a host plugin require a full quit and relaunch. When the two activation paths mix, "just refresh" and "must restart" have to be kept apart, or you will keep going in circles over "why didn't it take effect".

Two companion practices are worth adopting:

1. **Toggling a plugin off and on can reload its data**: to make the host re-read a plugin's own data file without restarting the app, turn the plugin off and on again in the plugin page. Reactivation re-runs the plugin's activation logic and re-reads the data. In one real troubleshooting session, this pointed the supervisor session from an empty session back to the older session with history, and the old records came back with it.
2. **Receipts must distinguish "not loaded" from "errored after loading"**: a plugin can write a receipt through its own HTTP route, carrying a build identifier, so the host side can confirm "which version is actually running on the page". That is more reliable than the browser console, and it separates "the code didn't take effect" from "the code errored". The receipt must stay outside the loader: if the loader throws, the page must still be able to write the receipt, or there will be no evidence exactly when it is needed most.

## One File Entry Means Splitting Needs a Build Step

The host serves only one file entry, and the page registers through a module loader; to split source code, a build step is required — the browser cannot be expected to load multiple module files natively. The reference approach keeps source files in directories by concern and bundles them into one self-executing package with a bundler, marking the shared library as external instead of bundling a second copy.

The build order matters too: building must come before packaging and release preparation, and the package allowlist must include the single-file artifact the entry points to plus its runtime resources, while the source directory stays out of the package. Forgetting to build can ship a stale artifact or one missing its entry.

Tests must follow the artifact as well: do not slice the artifact by source-text anchors, which break once modules are split and indentation changes. Load the artifact with an explicit test entry instead, and import source modules directly to verify pure functions.

Taking over a slot means taking over its original responsibilities, installation order, and verification method. A plugin that takes over the rendering but not the responsibility will eventually send the bill to the user.
