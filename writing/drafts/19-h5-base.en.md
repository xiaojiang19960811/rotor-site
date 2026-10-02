# H5 Base: Thicker Than a Scaffold

> Column: Garden ｜ Collection: Multi-Platform Business ｜ Source: business frontend H5 base concept page (wiki, desensitized) ｜ Status: first draft

A scaffold gets you from zero to running; business code gets you from running to launched. An H5 base sits in between: it ships with a light business skeleton so teams can start immediately. No new project rewrites login, tabbars, or request wrappers — the things "every H5 app builds once" are baked in.

## What the extra layer is

This base isn't a bare scaffold. A bare scaffold gives you empty directories and build config; this one adds a layer of conventional H5 business skeleton: four default pages (Login, Home, Task, Mine), a bottom tabbar, a floating back-to-home button, and login-state guards.

The stack is Vue 3, Vite 3, TypeScript, Vue Router 4, Pinia, Vant 3, Axios. Node 16.18.0 and npm 8.x are recommended, switched via nvm. "Ready to use" is concrete: pull it down and the login flow, page switching, and tabbar all work — business logic starts at page five.

## Route meta carries page semantics

The base's most important convention: page semantics converge on route `meta`, never scattered across pages. Page title, caching strategy, login checks, guest pages, tabbar display, and the floating home button are all declared in route meta.

The payoff: onboarding a new page doesn't require reading the whole project. Fill in a few meta fields and the title, auth, and caching behavior are set. Page components only care about how they look; "what role this page plays in the system" is answered uniformly at the routing layer.

## Three "always go through"s, no scattering

Three hard conventions keep the codebase from drifting apart over time:

1. **Login state always goes through the store**: `src/stores/base.ts` owns base login state. Pages never scatter `localStorage` cleanup on their own; state changes pass only through the store.
2. **Requests always go through request.ts**: request instances, duplicate-request cancellation, global loading, error prompts, `401/403` login-expiry handling, and token injection all converge in one file. Business code calls APIs and touches none of this.
3. **API constants always live in list.ts**: only endpoint constants, plus a whitelist of "don't show Toast" endpoints. Which API fails silently and which one prompts — one file tells you.

All three share a shape: take what "every page might reinvent" and funnel it into a single entry point. Scattering is entropy; a base exists to fight entropy.

## How to prove the base works

The base ships a manual verification path — six steps before it counts as usable: open `/#/home` while logged out and expect a redirect to login; log in and land on Home; switch between Home, Task, and Mine with a working tabbar; switching from Task or Mine shows the floating back-to-home button at bottom-right; logging out returns to login and protected pages intercept again; run `npm run build` and confirm `dist` is produced.

The path matters not for its length but because it turns "what the base promises" into an executable checklist. Every derived project runs it on handoff — six steps reveal whether the base got broken.

A base's biggest risk isn't bad design — it's derived projects quietly abandoning the conventions. The wiki records this as an open question: whether each derived project still follows the base conventions needs source-by-source verification.

That's honest. A base's value lies in its constraints, and constraints get bypassed — a rushed project writes requests directly in pages, clears localStorage on its own. At release time, decide how conventions are guarded: by review, by lint, or by "run the six-step verification." A convention with no guardian degrades into an ordinary directory; it's only a matter of time.

## In short

A good base shows off nothing. It does one thing: turns the parts every project rewrites into parts nobody rewrites again. A scaffold gives you a starting point; a base gives you a starting line.
