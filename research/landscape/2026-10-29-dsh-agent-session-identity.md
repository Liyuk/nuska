# DSH 的 Agent 是实体还是会话？——身份、persona 与两种 Bot 实现

状态：源码与文档核验 · 2026-10-29。对象为 DSH `0.2.1-rc.2` 本机安装包、ds-bot `0.2.3`、Tobs `main`（[`1e48294`](https://github.com/BotHarness/DeepSeekBot/tree/1e48294d86c681e308e989a8be967ecac21242b6)）。未启动 DSH，未运行任务；身份结论来自类型声明、README 与源码，不是运行时实验。

## 问题和范围

要回答三个问题：

1. DSH 的 agent 是一个独立的持久实体，还是绑定到 session？
2. 如果是绑定，现有 Bot 实现为什么看起来都是"session 聚合"？同一个 Bot 在私聊和群里的实例为什么能共用 persona？
3. 这对"要做一个持久 Bot 产品"意味着什么？

不包含：群聊轮次与派发细节（见[DS Bot 与 Tobs 的任务执行对照](2026-10-29-dsbot-vs-tobs-execution.md)）、交付质量与评估（见[Tobs 交付能力评估证据](../evaluation/2026-10-29-tobs-delivery-evaluation.md)）、模型效果比较。

## 材料和方法

- DSH 本机安装 `0.2.1-rc.2`：`@deepseek-ai/dsh-agent`、`dsh-session` 的类型声明与 README；Team 相关包 `dsh-experimental-agent-team*` 的 README。
- ds-bot `0.2.3`：npm 安装包内 `src/host/{roster,store,groups,prompt}.js`；引用按公开发行包核对。
- Tobs：ADR-0016、ADR-0035、ADR-0024（链接见下），以及 README 中"每个对话都带 persona 和 core memory"的发布说明。
- 方法：对"身份"问题，检查 id 约束、创建/恢复路径、生命周期能力与持久化位置；对 persona，检查它在哪一层被组装、存储和复用。证据按"类型/接口声明 → README → 实现源码"排列，不把某个产品的实现当成 DSH 的通用保证。

路径约定：`dsh-agent/...` 指安装包 `@deepseek-ai/dsh-agent` 内文件；`ds-bot/...` 指 ds-bot 包内文件。

## 发现与证据

### 1 DSH：Agent 是 Session 的实时执行面，不是独立的持久实体

| 事实 | 证据 |
| --- | --- |
| Agent 的 id 就是 session id；类型声明直接称其为 "Session-backed Agent identity" | `dsh-agent/lib/types/types.d.ts:12-13` |
| Agent 持有的 session 是"durable source of truth"；agent 本身是驱动它的实时对象 | `dsh-agent/lib/types/runtime-types.d.ts:140-143` |
| `ctx.agents.create()` 在**一个身份**下同时建 agent 与会话；`resume()` 先加载持久会话，再在其上重建 agent | `dsh-agent/README.zh.md:32` |
| `AgentHandle` 是创建者持有的拆除 capability，不是身份 | `dsh-agent/README.zh.md:117` |
| 持久的是 append-only 会话日志；历史由日志派生，压缩只隐藏不删除 | `dsh-session/README.zh.md:12` |
| persona 不属于 agent 实体，而属于 system-prompt 段 | `dsh-agent/lib/types/runtime-types.d.ts:20`（"Persona belongs to system-prompt sections"）；ds-bot 的实现见下文 |
| 会话的持久元数据里有 `parentSession`、`origin`、`agentPreset`；这些是 session 级事实，不是 agent 级身份 | `dsh-session/lib/types/types.d.ts:72,82,95` |

因此，准确的说法是：

- **运行时**：Agent 是一个真实对象，有 `status`、`inbox`、agent 作用域 `ctx` 和生命周期；
- **持久化**：没有一个"持久 Agent 实体"；进程退出后 agent 消失，session 还在，`resume()` 创建一个同 id 的新 agent；
- **身份**：对 agent 而言，唯一的持久身份是 `SessionId`。子 agent / teammate 也一样：`parentSession` 指向父会话，Team 里的名字是父会话日志中的 roster 状态，不是独立实体。

一条容易误读的边界：Team 的 roster、任务板确实持久，但它们是**会话日志中的记录**；Team id 就是 Lead 的 SessionId，没有 live Lead 就没有 Team 事务（`dsh-experimental-agent-team/README.md:104`；当前 `0.2.1-rc.2` 中 peer message 归目标成员会话，Lead 日志只保留 roster 与 task，历史 `team/message/*` 仅可读：同文件 `:144`、`:146`）。这层细节只影响"消息存在哪里"，不改变"身份是 SessionId"这一结论。

### 2 ds-bot：Bot 身份锚定在第一个私聊 Session 上

ds-bot 的 `createBot` 先 `createSession`，再把返回的 sessionId 直接当作 Bot id 写进 `state.bots`：

- `ds-bot/src/host/roster.js:153-155`：`const id = await createSession(cleanName, { dir })`，随后 `state.bots[id] = { id, ... }`。
- `ds-bot/src/host/store.js:351-353`：源码注释明确写"A Bot's id is the Session id of its first own-chat segment and never changes; `bot.sessionId` is the current one"。
- 每个群再给这个 Bot 一个 hidden session：`room.sessions[botId]`，首次在该群发言时惰性创建（`ds-bot/src/host/groups.js:198-215`）。
- 群 session 与私聊 session 渲染**同一段** system prompt / tools，因此共享 provider prefix cache（`ds-bot/src/host/store.js:344-348`）。
- persona 存在 roster 的 `bot.instructions` 里，但渲染发生在每个 session 的 prompt 组装时：`bot-identity` section 用 `context.agent.id` 反查 Bot（`ds-bot/src/host/prompt.js:57-81`）。
- profile 修改后，旧 session 的 kickoff 仍有惯性，所以会补一条 notice 让下一轮遵守新 profile（`ds-bot/src/host/roster.js:321-326`）。

这解释了两个现象：

1. **"session 聚合"**：Bot 不是一个独立实体，而是一个 roster 记录 + 一组 session（私聊 1 个 + 每群 1 个 + 上下文分段）。identity 是第一个私聊 session 的 id；执行面分散在多个 session。
2. **"个体 + 群内个体共用 persona"**：不是共享上下文，而是同一个 Bot 记录被渲染进多个 session 的 system prompt；历史、上下文、缓存前缀各不相同，只有 persona 文本相同。

### 3 Tobs：把身份从 Session 中移出来

Tobs 的选择相反：

- [ADR-0016](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/docs/adr/0016-bots-are-first-class-entities.md)：PersonaBot 由 registry 拥有，携带 identity、persona、memory、state、channel bindings；**DSH sessions 和 agents 只是它的 execution**。一个 PersonaBot 可以持有多个 session、多个 workspace。
- [ADR-0035](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/docs/adr/0035-session-ownership-is-explicit.md)：session ownership 显式存在 BotHarness 的数据库里，不能从 cwd、标题或 recent activity 推断。
- [ADR-0024](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/docs/adr/0024-orchestrator-session-per-personabot.md)：每个 PersonaBot 一个 Orchestrator session（控制面），工作项跑在独立 root Assignment session 里。

但 Tobs 的 persona 也不在 DSH Agent 实体里：它属于 PersonaBot 的 soul，注入每个会话的 prompt；每个会话仍然拿到同一份 soul / core memory（README 1.1.0 的发布说明写"every conversation carries the Bot's persona and core memory"）。也就是说：

- **身份**：Tobs 放在 registry，独立于 session；
- **persona**：仍然是"每个 session 渲染同一份配置"，和 ds-bot 的机制同类，只是配置源从 roster 换成了 soul / core memory 文件。

### 4 四个概念的对照

| 概念 | 是什么 | 是否持久 | 身份 |
| --- | --- | --- | --- |
| Session | append-only 事件日志 + header | 是 | `SessionId` |
| Agent | 驱动某个 session 的实时执行面 | 否（进程内） | id 就是该 session id |
| AgentHandle | 创建者持有的生命周期 capability | 否 | 指向 agent，不是身份 |
| Subagent / teammate | `parentSession` 指向父会话的子 session | 是（作为 session） | 子 `SessionId`；名字在父日志/Team roster |
| ds-bot Bot | roster 记录 + session 集合 | 是（`state.json`） | 第一个私聊 session id |
| Tobs PersonaBot | registry 实体 | 是（operational DB） | registry 生成的 bot id |

### 5 这意味着什么

- **DSH 不提供"持久 Agent 身份"这层抽象。** 它提供的是 Session 及其执行面。要一个"跨会话/跨重启的 Bot"，必须在宿主之上自己建 registry，或者像 ds-bot 一样把身份锚定在某个 session id 上。
- **"persona 共享"不是实体属性，而是渲染策略。** 同一段 prompt 注入多个 session，就得到"同一个 Bot 在不同场合"的观感；各 session 的历史与上下文仍然独立。反过来说，改 persona 会影响所有新渲染的 session，旧 session 需要 notice/kickoff 补偿。
- **两种产品取向的代价不同。** session-derived 身份实现便宜、天然复用 DSH 的持久化/压缩/恢复，但身份的生命周期跟着 session（换段、删除、迁移都需要映射）；entity-first 身份更干净，但需要 registry、ownership、迁移与备份，工程量大一个量级。
- **这也解释了为什么"一个对话 + 持久 persona"不是身份层。** persona 是配置文本；身份需要一个在对话之外的所有者。没有 registry 时，那个所有者就是"第一个 session"，而不是"一个 Bot"。

## 局限和未解问题

- 本文没有运行 ds-bot / Tobs；"Bot id 不变"来自源码注释与创建路径，未验证归档、删除、迁移后的行为。
- Tobs 的 registry 与 session 映射来自 ADR 与 README，未逐表核对数据库 schema；ADR 可能随版本变化。
- DSH 安装包无 commit 指纹；身份相关引用使用包内文件与 `0.2.1-rc.2` 版本号，不使用不可复现的本地路径。
- "群 session 与私聊共享 prefix cache"来自 ds-bot 源码注释，未实测缓存命中率。
- 未覆盖多人 Human 场景；Tobs 的 local Human 与 ds-bot 的单用户假设不同。

## 对 Nuska 的意义

- 如果 Nuska 的目标只是"把一次任务交付好"，不需要先造 Bot 实体；任务层（任务对象、验收、恢复）才是主问题。
- 如果目标是"用户长期拥有一支可寻址的 Bot 团队"（多场合、跨设备、独立记忆/配置），则**身份必须放在 session 之外**；Tobs 的 PersonaBot 是现成参照，ds-bot 的 session-derived 身份是实现简单但受限的参照。
- 无论选哪种，persona 都应建模为"共享配置 + 每 session 渲染"，而不是 agent 实体上的可变字段；否则换段/多群会出现版本不一致。

## 下一步

1. 用 ds-bot 实测：Bot 的第一个 session 被归档/删除后，Bot 身份与私聊入口是否仍成立；换段后的 `bot.sessionId` 与 `bot.id` 如何影响 API 与 UI。
2. 用 Tobs 实测：bot id 在 export/import、跨设备迁移、Orchestrator 替换后是否稳定；registry 与 session 的映射如何恢复。
3. 在 Nuska 候选设计里，把"Bot 身份"和"任务身份"分开建模，比较 session-derived 与 registry 两种实现所需的结构和维护复杂度。
