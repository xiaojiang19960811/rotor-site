# Two Protocols for Agents: MCP for Tools, A2A for Agents

> Column: Knowledge Garden | Collection: Agents & Digital Humans | Source: wiki/concepts/MCP-2026-07-28 protocol evolution, Agent-to-Agent A2A protocol | Status: First draft

The agent world has two open protocols, and they solve two different connection problems: MCP connects agents to tools and resources; A2A connects agents to agents. Confusing their responsibilities is the most common mistake before adopting either.

## Three Layers: Skill, MCP, A2A — Each Owns One

- **Skill**: a capability package and execution flow inside a single agent.
- **MCP**: the protocol an agent uses to connect to tools, APIs, databases, files, and external resources.
- **A2A**: the open protocol for discovery, communication, delegation, and collaboration between independent agent systems.

A typical chain:

```
User
  -> Primary agent
    -> Delegates via A2A to a specialist agent
      -> Specialist agent uses Skills internally
      -> Specialist agent calls tools/data via MCP
```

The three layers don't substitute for each other: MCP is the external capability protocol, Skill is a reusable workflow inside an agent; a protocol upgrade never merges the two into one asset class.

## A2A: How Agents Shake Hands with Agents

A2A was originally proposed by Google and later evolved as an open project under the Linux Foundation. It handles peer or delegated relationships: a primary agent discovers and calls a specialist agent without needing to know the other's internal tools, memory, or implementation.

Core mechanisms:

- **Agent Card**: the agent declares its capabilities, interfaces, authentication, security requirements, and available skills
- **Task**: collaboration is organized around tasks with state and lifecycle
- **Message / Part**: exchanging context, user instructions, text, files, structured data, or media fragments
- **Artifact**: task outputs, such as reports, files, or data results
- **Transport**: supports HTTP(S), JSON-RPC, SSE streaming updates, async push notifications, and also gRPC/REST bindings

Its applicable scenarios reveal its boundaries: agents from multiple vendors or different frameworks need to collaborate; agents from different business domains inside an enterprise need to delegate to each other. Workflows inside a single agent are not A2A's business.

## MCP's Evolution: From Sessions to Stateless

The core change in MCP `2026-07-28` versus the previous `2025-11-25` is moving from "initialize handshake + session state" to "stateless + version and capabilities on every request":

| Area | `2025-11-25` and earlier | `2026-07-28` |
|---|---|---|
| Initialization | `initialize`, then `notifications/initialized` | Handshake removed; each request independently declares version and capabilities |
| State | HTTP could hold a protocol session via `Mcp-Session-Id` | Protocol-level sessions removed; cross-call state uses explicit server-generated handles |
| Version & capabilities | Negotiated at initialization | Request `_meta` carries protocol version, client capabilities, and suggested client identity; result `_meta` is advised to carry server identity |
| Discovery | Relied on initialization results | Server must implement `server/discover`; clients can discover up front or just request and handle version errors |
| Notifications | HTTP GET/SSE and resource subscription endpoints | Long-lived POST `subscriptions/listen` unifies change notifications |
| Server-to-client requests | Server directly initiates Roots, Sampling, Elicitation, etc. | Replaced by multi round-trip requests: return `input_required`, client retries the original request after supplying input |
| Result structure | No uniform type field needed | Every result must carry `resultType`, at minimum distinguishing `complete` from `input_required` |
| Long tasks | Tasks lived in the experimental core protocol | Tasks moved to the optional `io.modelcontextprotocol/tasks` extension, handle- and polling-centric |
| SSE recovery | Supported `Last-Event-ID` and event replay | Recovery and replay removed; after a drop, the client resends with a new request ID |
| Caching | Weak cache contract | Main list/read results require `ttlMs` and `cacheScope`; stable ordering of tool lists advised |

What stayed: the Host–Client–Server architecture over JSON-RPC 2.0; Tools, Resources, and Prompts as core primitives; stdio locally, Streamable HTTP recommended for remote.

## Migration Discipline: Dual-Era, Don't Just Bump the Version String

The part of this protocol evolution most worth writing into an engineering handbook is its compatibility strategy:

1. **Dual-era implementation**: when old ecosystems must be supported, modern requests go through per-request metadata while old requests are still handled with `initialize` semantics. A client supporting only the modern protocol cannot talk directly to a server supporting only the old one, and vice versa.
2. **Check the SDK first**: projects using official SDKs must verify SDK support for the new version before anything else; don't just change the version string, because the lifecycle, notification flow, and result schema all changed.
3. **Deprecated does not mean deleted**: Roots, Sampling, and Logging are marked Deprecated but remain inside the compatibility window. When you see Deprecated, look up the replacement direction first and schedule the migration — it's not an immediate removal.

## When You Don't Need A2A

Back to the architecture judgment. The conclusion for personal workflows is blunt: build `AGENTS.md` and Skills first; A2A only becomes a priority when you need to service-ize multiple independent agents, call across systems, or collaborate across teams or vendors.

That's the methodology this piece wants to land: choose protocols by connection shape. Agent to tools/resources: MCP. Peer-to-peer delegation between agents: A2A. Reusable workflows inside an agent: Skill. Before you're at the cross-system collaboration stage, bolting on A2A is just an extra layer of abstraction nobody calls.

MCP connects tools, A2A connects agents — and knowing when "not needed" matters as much as knowing how to "use".
