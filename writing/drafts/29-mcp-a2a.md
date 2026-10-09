# Agent 的两条连线：MCP 接工具，A2A 连 Agent

> 栏目：知识花园 ｜ 合集：Agent 与数字人 ｜ 来源：wiki/concepts/MCP-2026-07-28协议演进、Agent间通信协议A2A ｜ 状态：初稿

Agent 世界有两个开放协议，解决的是两种不同的连接问题：MCP 负责 Agent 和工具/资源之间的连线，A2A 负责 Agent 和 Agent 之间的连线。混淆两者的职责，是引入它们之前最常见的误判。

## 三层：Skill、MCP、A2A 各管什么

- **Skill**：单个 Agent 内部的能力包和执行流程。
- **MCP**：Agent 连接工具、API、数据库、文件、外部资源的协议。
- **A2A**：独立 Agent 系统之间互相发现、沟通、委托和协作的开放协议。

典型链路：

```
用户
  -> 主 Agent
    -> 通过 A2A 委托专业 Agent
      -> 专业 Agent 内部使用 Skill
      -> 专业 Agent 通过 MCP 调工具/数据
```

三层互不替代：MCP 是外部能力连接协议，Skill 是 Agent 内部可复用的工作流；协议升级不会把两者合并成同一种资产。

## A2A：Agent 和 Agent 的握手方式

A2A 最初由 Google 提出，后作为 Linux Foundation 下的开放项目演进。它处理的是对等或委托关系：一个主 Agent 发现并调用专业 Agent，但不需要知道对方的内部工具、记忆或实现细节。

核心机制：

- **Agent Card**：Agent 对外声明能力、接口、认证、安全要求和可用技能
- **Task**：协作以任务为核心，有状态和生命周期
- **Message / Part**：交换上下文、用户指令、文本、文件、结构化数据或媒体片段
- **Artifact**：任务产物，例如报告、文件、数据结果
- **Transport**：支持 HTTP(S)、JSON-RPC、SSE 流式更新、异步 push notification，也支持 gRPC/REST binding

适用场景恰恰说明了它的边界：多个供应商或不同框架的 Agent 需要协作；企业内不同业务域的 Agent 需要互相委托。单个 Agent 内部的工作流，不归 A2A 管。

## MCP 的演进：从会话到无状态

MCP 2026-07-28 相对上一版 2025-11-25 的核心变化，是从"初始化握手 + 会话状态"改为"无状态 + 每请求携带版本与能力"：

| 方面 | 2025-11-25 及更早 | 2026-07-28 |
|---|---|---|
| 初始化 | `initialize` 后发送 `notifications/initialized` | 删除初始化握手；每个请求独立声明版本与能力 |
| 状态 | HTTP 可通过 `Mcp-Session-Id` 维持协议会话 | 删除协议级会话；跨调用状态用服务端生成的显式 handle |
| 版本与能力 | 在初始化阶段协商 | 请求 `_meta` 携带协议版本、客户端能力与身份；结果 `_meta` 建议携带服务端身份 |
| 服务发现 | 依赖初始化结果 | 服务端必须实现 `server/discover`；客户端可预先发现，也可直接请求后处理版本错误 |
| 通知 | HTTP GET/SSE 与资源订阅接口 | 用长连接 POST `subscriptions/listen` 统一订阅变化通知 |
| 服务端反向请求 | 服务端直接发起 Roots、Sampling、Elicitation 等请求 | 改为多轮往返：返回 `input_required`，客户端补充输入后重试原请求 |
| 结果结构 | 普通结果无需统一类型字段 | 所有结果必须有 `resultType`，至少区分 `complete` 与 `input_required` |
| 长任务 | Tasks 位于实验性核心协议 | Tasks 移至可选扩展 `io.modelcontextprotocol/tasks`，以 handle 和轮询为核心 |
| SSE 恢复 | 支持 `Last-Event-ID` 与事件重投 | 删除恢复与重投；断流后客户端以新 request ID 重发 |
| 缓存 | 缓存契约较弱 | 主要 list/read 结果要求 `ttlMs` 与 `cacheScope`，工具列表建议稳定排序 |

保持不变的主线：Host、Client、Server 架构，底层 JSON-RPC 2.0；核心原语仍是 Tools、Resources、Prompts；本地仍用 stdio，远程推荐 Streamable HTTP。

## 迁移的纪律：双时代、别只改版本号

协议演进最值得写进工程手册的是它的兼容策略：

1. **双时代实现**：需要兼容旧生态时，现代请求走逐请求元数据，旧请求仍按 `initialize` 语义处理。仅支持现代协议的客户端不能直接与仅支持旧协议的服务端互通，反之亦然。
2. **先核对 SDK**：使用官方 SDK 的项目先核对 SDK 是否支持新版本；不要只修改版本字符串，因为生命周期、通知流和结果 Schema 都发生了变化。
3. **弃用不等于删除**：Roots、Sampling、Logging 已标记 Deprecated，但仍处于兼容窗口。看到 Deprecated 先查替代方向、再排期迁移。

## 什么情况下不需要 A2A

回到架构判断。个人工作流的结论很直白：优先建设 `AGENTS.md` 和 Skills；只有当需要把多个独立 Agent 服务化、跨系统调用、跨团队/供应商协作时，A2A 才成为优先架构议题。

这是整篇最想说的方法论：协议按连接形态选。Agent 连工具资源，用 MCP；Agent 之间对等委托，用 A2A；Agent 内部的工作流复用，用 Skill。还不到跨系统协作的阶段，硬上 A2A 只是多一层没人调用的抽象。

MCP 接工具，A2A 连 Agent；知道什么时候"不需要"，和知道怎么"用"一样重要。
