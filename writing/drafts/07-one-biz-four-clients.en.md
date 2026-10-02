# One Business, Four Clients: How to Organize the Code

> Column: Build Notes ｜ Collection: Multi-Platform Business ｜ Source: wiki/concepts/chengtai-ol多端模式 ｜ Status: first draft

One business, four clients: an admin console, a customer H5, a dealer H5, and an agent H5. Same business domain, different user roles, clearly different interaction flows. How do you organize the code — by tech stack or by client? Our answer: name the top-level directories by client semantics, never by tech stack.

## Why by client, not by stack

The four clients' users and responsibilities barely overlap: the admin side serves internal roles — operations, management, review, finance — handling configuration, reviews, orders, and accounting; the customer H5 walks buyers through products, verification, ordering, signing, and repayment; the dealer side handles applications, signing, earnings, and withdrawals; the agent side handles marketing performance, earnings, and dealer management.

Splitting by tech stack (say `vue/`, `react/`, `admin/`) answers "what it's written in," not "who it's for." When a developer looks for code, they're thinking "I need to change the dealer withdrawal page," not "I need the H5 written in Vue 3." Directory structure should answer business questions, not technical ones.

## Three engineering rules

1. **The root is a business collection directory**: new client projects go on living inside the same collection directory — no fresh starts elsewhere. Four clients, one business, not four projects.
2. **Directory names carry client semantics**: top level says "admin console" and "customer H5," not "vue3-admin" and "h5-vite." Tech stacks change; client semantics don't.
3. **Template leftovers are clues, not names**: scaffold-generated names must never double as business names. Rename on sight; don't live with them.

There's also a meta-rule: a project-level `AGENTS.md` outranks workspace-wide conventions. A client without project-level rules follows the nearest explicit rule in the same business collection — but inference must never be written up as a formal rule.

## Frontend implementation discipline

The page layer does orchestration, navigation, and state dispatch only; field cleanup, status copy, and API compatibility sink into adapter/mapper layers. No "if the backend returns A show this, if B show that" compatibility spaghetti in pages.

API fields follow the confirmed documentation — never keep multiple guessed field names for the same semantics. Code that says "it might be userName or username, let's handle both" guarantees the field semantics will never actually get confirmed.

Styles use semantic variables: theme, buttons, borders, shadows go through variables, no new hard-coded values. Four clients stay visually consistent not because "everyone conscientiously writes the same," but because there's only one set of variables.

## Don't hard-code what isn't confirmed

Four questions remain open in this model: whether the four clients share one backend service, tenant model, and auth mechanism; the formal relationship model between agents, dealers, and customers; the formal definitions of earnings, fee, withdrawal, order, and repayment state transitions. Until confirmed, code treats each client as independent — no premature unification assumptions. An assumption written into code becomes architecture by default.

## In short

Multi-client code organization is three lines: top-level directories by client semantics, not tech stack; pages orchestrate, cleanup sinks into adapters; unconfirmed relationships stay un-hard-coded. Directories are for humans to read — let people find things first, then let machines run them.
