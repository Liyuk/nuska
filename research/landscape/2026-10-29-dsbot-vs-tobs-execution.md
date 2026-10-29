# DS Bot 与 Tobs 的任务执行对照：对话驱动 vs 控制面驱动

状态：源码与文档对照 · 2026-10-29。对象为 ds-bot `0.2.3` 与 Tobs `main`（[`1e48294`](https://github.com/BotHarness/DeepSeekBot/tree/1e48294d86c681e308e989a8be967ecac21242b6)）。未运行两者，未做同任务对照；本文比较的是实现机制，不是实测交付率。

## 问题和范围

用户把同一件事交给两个系统后，**任务是怎么被执行的**？差异体现在哪些执行环节，对交付质量有什么影响？

不包含：身份模型（见[DSH 的 Agent 是实体还是会话？](2026-10-29-dsh-agent-session-identity.md)）、Tobs 评测证据（见[Tobs 交付能力评估证据](../evaluation/2026-10-29-tobs-delivery-evaluation.md)）、模型效果与界面设计。

## 材料和方法

- ds-bot：npm `ds-bot@0.2.3` 的 `src/host/{groups,turns,handoffs,store,roster,tools,constants,prompt}.js`；研究稿 `docs/plans/2026-10-16-bot-handoffs.md`、`docs/plans/2026-10-07-group-chat.md`、`docs/plans/2026-10-13-dsh-concessions.md`。
- Tobs：[ADR-0016](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/docs/adr/0016-bots-are-first-class-entities.md)、[ADR-0017](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/docs/adr/0017-assignments-are-sessions-no-task-entity.md)、[ADR-0024](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/docs/adr/0024-orchestrator-session-per-personabot.md)、[ADR-0045](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/docs/adr/0045-orchestrator-manages-assignments-through-a-durable-directory.md)，以及架构文档 `docs/architecture/botharness-architecture.md`。
- 方法：从"用户发出一条请求"开始，逐段对照受理、派发、执行上下文、并发、结果回传、完成判定、恢复与权限；每段先给可核对的实现事实，再给推断。

## 发现与证据

### 1 两条端到端路径

**ds-bot（对话驱动）**

1. 用户发群消息 → 建一轮（round）→ 管理员先答；群内一次只有一个人说话（`ds-bot/src/host/groups.js:455` 的 `runRound`）。
2. 管理员用 `@名字` 或 `message_bot` 叫成员；被叫成员进入自己的 group session（`room.sessions[botId]`，`groups.js:198-215`）。
3. 成员的首个工具调用后 15 秒仍在干活，本轮就继续往下走，不再等它（`constants.js:74`；`groups.js:320`）；静默 4 分钟判 missed（`constants.js:38`；`groups.js:318`）。
4. 成员在后台继续跑，结果迟到回群，由"谁叫的谁接话"再开一轮（`groups.js` 的 late reply 路径）；Bot 间接力到 `3 × 成员数` 就暂停，等用户继续或发言（`groups.js:36-40,469-487`）。
5. 私聊里的 `message_bot` 派活有"派活树"：结果自底向上回传，等待关系存 `state.json`（`ds-bot/src/host/handoffs.js:1-15`）；但**群里的 `@` 和群内 `message_bot` 不进派活树**（`docs/plans/2026-10-16-bot-handoffs.md:89`）。

**Tobs（控制面驱动）**

1. 用户发 DM → Source Event → Bot Inbox → Orchestrator 按批次处理（`docs/architecture/botharness-architecture.md` 的 Orchestrator/Inbox/Channel 段）。
2. Orchestrator 决定直接回答，或调用 `create_assignment`：由 Host-lifetime Assignment Runtime 建一个独立 root DSH Session，并记录 delivery intent、workspace、model、依赖与并发准入（ADR-0045）。
3. Assignment 在自己的 workspace Grant 内执行，可用 native subagent 做更下一层委派；它通过 `report_to_orchestrator` 回报。
4. 报告成为不可变 Source Event + Bot Inbox Admission；Host 另发 lifecycle notice（settled/error/cancelled/interrupted），与模型报告分开 provenance（ADR-0045）。
5. Orchestrator 从当前 Directory 事实或报告答复 Human；Assignment 之间 v1 不直接通信，协调请求经 Orchestrator 转发（ADR-0045）。

### 2 执行环节对照

| 环节 | ds-bot | Tobs |
| --- | --- | --- |
| 任务载体 | 某个 Bot 某个会话里的一个回合；群任务=一轮 | Assignment = 独立 root DSH Session；无 Task 实体，Session id 即身份（ADR-0017/0024） |
| 谁受理 | 群管理员，或私聊里的那个 Bot | Orchestrator session（控制面）；Human 跟 Bot 的 DM/群说话，不直接指挥 Assignment |
| 派发 | `@` / `message_bot`；群 `@` 不进派活树 | `create_assignment` + 五个窄工具（list/inspect/create/send_request/stop）；Directory 持久记录（ADR-0045） |
| 执行上下文 | 群 session：本轮 transcript + 已读位置 + 发言顺序；执行在成员 session 里继续，但群轮次先走 | Assignment：独立连续上下文，自己的 cwd、模型、权限快照 |
| 并发 | 群内一次一人；Bot 接力到 `3 × 成员数` 暂停等用户 | 多 Assignment 并行，默认上限 3（1–32）；超限**结构化失败，不排队**（ADR-0045） |
| 中途调整 | `message_bot` 的 now/queue；群内延迟补发 | 三种语义请求：`context-update`→inject、`next-step`→steer、`next-turn`→followup；普通请求不打断进行中的 step（ADR-0045） |
| 结果回传 | 群消息 + 私聊派活树自底向上回传；群内谁叫的谁接话 | `report_to_orchestrator` 报告事件 + Host lifecycle notice；报告可主动、可合并 attention（ADR-0045） |
| 完成判定 | 模型自述 + 群内接话；无独立 checker | 报告 ≠ 验收；Directory 把 activity 与 latest report 分开；仍由 Human 判断（ADR-0045） |
| 中断恢复 | `inflight.json` 记录进行中的 turn，重启后尽力续跑（`resume.js`）；等待关系存 state.json | 启动把 working 标 `interrupted` 并发 notice；**不自动续跑**，需显式 resume；delivery intent + bounded reconciliation（ADR-0045） |
| 权限/工作区 | 群共享文件夹 + Bot 级权限；goal 在 Bot 会话被屏蔽（`tools.js:17-20`） | per-Assignment workspace Grant（单一 cwd）+ 权限快照；Orchestrator 只读全部 Grant（ADR-0045） |
| 拓扑 | Bot 之间对等：任何 Bot 可 `message_bot` 任何 Bot；群是共享房间 | 星形：Orchestrator 是 PersonaBot 唯一对外声音；Assignment 之间 v1 不直连（ADR-0045） |

### 3 四个关键差异

**① 前台与后台是否分离。** ds-bot 里同一个 Bot 既聊天又干活——"前台即后台"。它忙的时候，群要么等、要么让它让位，接受到迟到的结果。Tobs 里 Orchestrator 只受理与协调，Assignment 在后台跑；前台始终能回话，后台可以同时跑多条线。

**② 问责链路。** ds-bot 的私聊派活有树、会自动回传；群里的 `@` 和群内 `message_bot` 明确不进树（`docs/plans/2026-10-16-bot-handoffs.md:89`）。而群恰恰是交付现场，于是"群派活"成了问责最薄的一条路。Tobs 把 DM/群/IM 的派活都收敛到 Assignment + Directory + Report 一条链路。

**③ 拓扑是网状还是星形。** ds-bot 是 peer-to-peer：Bot 之间直接 `message_bot`，群是共享房间，接力可以多跳。Tobs 是星形：每个 PersonaBot 的 Orchestrator 是唯一对外声音，Assignment 之间不直接通信；想要跨工作项协调，经 Orchestrator 转。前者灵活但容易出现 A→B→A 的绕圈和噪声；后者可审计但多一跳。

**④ 完成与恢复的语义。** ds-bot 的"完成"就是一条消息，恢复是"尽力续跑"；Tobs 的"完成"是一份可审计的报告事件，恢复是"显式、可见、不自动"（重启先标 interrupted）。两者都没有自动验收——Tobs 只是把"执行活动"和"语义报告"分开，最终仍由人判断。

### 4 适用场景

- **ds-bot**：群内串行、成员按需参与；对话自然，适合 1–3 个 Bot 的即时协作、短任务和边聊边改。
- **Tobs**：Assignment 可并行（上限 3），前台不被长任务占住；同时引入 Orchestrator、Assignment、Directory、Channel 和 Grant 等控制面概念。它更适合多任务并行、长期运行和需要审计的场景。

## 局限和未解问题

- 未运行同任务对照；并发与执行时间的实际影响尚未测量。
- Tobs 的机制描述来自 ADR 与架构文档，未逐条核对实现；ADR 可能随版本变化。
- ds-bot 行号按公开发行版本 `v0.2.3` 核对；没有逐行比对所有文件。
- "报告 ≠ 验收"是 Tobs 的设计边界，不代表它的报告质量已被独立验证；Tobs 的评测证据另文讨论。
- 没有覆盖多人 Human、跨设备、IM 渠道差异；这些会改变"谁受理、谁验收"。

## 对 Nuska 的意义

- 如果 Nuska 的目标是"把一个任务交付好"，关键不在"群聊还是私聊"，而在**任务对象、结果回传、完成判定、恢复**这四件事；ds-bot 的群聊只是外衣，Tobs 的 Assignment 才是把这四件事显式化的参照。
- 如果 Nuska 要做"多 Bot 长期协作"，Tobs 的"前台/后台分离 + 星形拓扑 + Assignment 目录"值得借鉴；但也要接受它带来的工程复杂度。
- ds-bot 的可借鉴点是"轻"和"对话原生"：群回合、@ 交接、进度播报、迟到补发，这些在用户体验上比"任务面板"更自然；缺的是把群派活接进问责链路的机制。

## 下一步

1. 选一个可用机器检查的任务，在相同模型/宿主版本下跑 A=单 Bot 直做、B=ds-bot 群、C=Tobs，记录 verified completion、用户催促次数、空转/重复与恢复情况。
2. 针对 ds-bot 验证"群 `@` 派活不进派活树"的实际影响：同一任务分别走私聊 `message_bot` 与群 `@`，比较结果回传与失败可见性。
3. 针对 Tobs 验证 Assignment 的恢复语义：注入进程重启、模型失败、工具审批等待，观察 lifecycle notice、显式 resume 与 Directory 状态是否一致。
