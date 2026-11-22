# The Menu Granted Access. The API Still Said 403.

> Column: Lab Notes | Collection: Engineering | Source: wiki/bugs/2026-08-14 multi-model gateway admin RBAC route-mapping gap (desensitized) | Status: Drafted · Upcoming

Conclusion first: new admin routes shipped while the permission map stood still, and the same gap failed in both directions at once — authorized accounts were stopped by 403, while an endpoint with no permission check stood open. The root cause was not the permission design. Route registration and the permission map are two sources of truth, and one changed without the other.

## One gap, two directions

An admin assigned a backend menu role to an ordinary account. The account opened the feature, but some of its sub-endpoints still returned 403, demanding an admin menu permission. The permission was granted, the page loaded, and the API refused.

The gap ran the other way too: the payment admin endpoints carried admin authentication and auditing, but no permission middleware. In other words, the condition for passing a sensitive endpoint was "logged in as an admin," not "this account holds the matching permission." Invisible in the menu is not the same as unreachable through the API.

## Root cause: the map drifted

The permission middleware works by deriving a menu key from the request path, then checking whether the account holds that menu's permission. When a path has no entry in the map, only one way through remains: the account must itself be a built-in admin. An ordinary account, even one bound to a role containing the target menu, is refused.

The drift accumulated like this: new sub-routes kept arriving — some belonged under account management, some under settings, some named differently from the old map entries. The route registry grew; the map did not grow with it. Once the two sources of truth diverge, the system sits half new and half old: new routes either find no permission home, or nobody remembers they need a permission check at all.

## Hiding a menu item is not a permission

The point worth pulling out on its own is the difference between hiding a menu item and enforcing a permission on the API. A feature absent from the menu simply has no entrance in the interface; whether the API checks permission is a separate question. Treating "not visible in the menu" as "not callable" mistakes user experience for a boundary.

The payment endpoints are the counterexample: they had a place in the menu system, authentication and auditing were attached, and only the permission middleware was missing. Each step looked right on its own; together they made a sensitive endpoint with no permission home. The truth about permissions lives in the map, not in the menu.

## Fix and verification

The fix came in three steps: the drifted sub-routes were assigned to existing menu permissions; the payment admin routes got the permission middleware, inheriting the orders permission; audit logs stayed exclusive to built-in admins, with no new assignable menu key. Unknown endpoints keep failing closed, and whether to add a new assignable permission key is a separate decision, never a side effect.

Regression tests covered both directions: an ordinary account with the matching permission can reach the sub-endpoints, an unrelated role gets 403; an account with the orders permission passes the payment RBAC check; unknown paths and audit logs stay closed to custom roles.

One gap remains, and it should be recorded honestly: no restricted account was ever walked through the pages in a real browser. Tests passing is not the same as a person walking through it — two pieces of evidence, and the missing one still needs doing.

## Prevention: make the map follow the routes

Three measures, all aimed at keeping the two sources of truth from diverging again:

1. **When an admin top-level route is added or renamed, add the mapping assertion with it**: if the route table changes, the map's tests change too, and a missing mapping fails the test first.
2. **An independently registered admin route must carry all three**: admin authentication, auditing, and the permission check. None may be missing, and the frontend menu hiding counts for none of them.
3. **A sensitive endpoint that fits no existing menu stays denied by default**: block it first, then decide separately whether a new assignable permission key is warranted.

One line to close: the permission map is a living table that follows the routes, not a configuration written once and forgotten; from the day it stops moving, 403s and over-permission arrive one after the other.
