# 多 Agent 评审：DSH Team、DS Bot 与交付问题的共识、分歧与勘误

状态：多视角评审记录 · 2026-10-29。评审对象为 DSH `0.2.1-rc.2`、ds-bot `0.2.3`、Tobs `main`（`1e48294`）以及本目录前序研究稿。**未运行任何系统，未做同任务对照**；所有判断都是源码/文档层面的，除了明确标注的主观体验。

## 问题和范围

围绕三个争议组织一次独立评审，避免单一视角的确认偏差：

1. DSH 的 Agent Team 能不能直接当"多房间持久 Bot 产品"？
2. "一个对话 + 持久 persona + 把子智能体输出投影进主对话"是不是够用？
3. ds-bot 交付差，是结构原因、模型原因，还是证据不足？

评审采用四角色、两轮：先各自独立出稿，再交叉质询；每轮要求给出"最强反方观点"和"什么会改变你的结论"。角色与产出：

| 角色 | 关注点 | 主要贡献 |
| --- | --- | --- |
| 架构 | DSH 原语边界、Team 不变量、产品层复用/自建 | Team 是单 Root 会话协调域；可复用原语在 Agent/Session 平面；Room 不能塞进 Team |
| 反方 | 钢人化"单会话团队"和"ds-bot 只是没调好" | 单会话在窄场景成立；多房间最小解是薄层；ds-bot 的失败可能被用法/模型/样本量混淆 |
| 证据 | 逐条核验，不站队 | 版本分界、文档自述的降级、UI/Lead 等待/任务板的真实边界 |
| 交付 | 因果链、最小改造 | 任务是消息级而非任务级；群聊是交付现场却不在派活树；R1–R3 改造与实验设计 |

## 共识

1. **Team 不等于多房间产品层。** TeamId 就是 Lead 的 SessionId；当前 `0.2.1-rc.2` 中 roster 与 task 在 Lead 日志，peer message 归目标成员会话；Team 无房间、成员图、已读位置、@ 路由、每成员独立工作区。把 room 塞进 Team 会破坏多条不变量，改动范围较大。
2. **单会话团队在窄场景成立。** 单用户、≤3 persona、≤1 活跃项目时，"持久 persona + preset + 每项目一 session + 把子任务摘要/产物路径投影到主对话"够用；需要"一个 Bot 同时在私聊与多个群"时不够。
3. **多房间的最小解不是五个域，而是"房间 = root session + preset + registry + 薄轮次器"。** DSH 按 root 会话已支持独立 cwd/模型/preset/workspace；缺的是把多会话绑定到 Bot 的产品层。完整产品域（PersonaBot/Orchestrator/Assignment/Channel/Memory）只在"多真人 + 多房间 + IM 身份 + 跨会话 persona + 可审计派发"同时成立时才值得。
4. **ds-bot 的交付问题在任务层，不在模型层。** 机制是消息级而非任务级：群轮次在产物出现前结束（15s 让位 / 240s 静默 / 接力计数），群 `@` 派活不进派活树，完成由模型自述，宿主级失败只进 diagnostics。群聊是唯一交付现场，却恰好被排除在 ds-bot 唯一成型的问责结构之外。
5. **第一批改造是"判定与状态"，不是更多路由：** 交付单 + 系统关单门（acceptance check）、交付看门狗 + 兜底执行、任务态结束条件 + 状态投影 + 独立步骤 fan-out；产物落盘、摘要 + 路径。
6. **Tobs 是"身份/多房间"的参照，不是"交付保证"的参照。** 它证明完整产品域可行，并在 ADR-0024 明确拒绝把 Assignment 做成 continuable subagent；但它同样没有自动验收，也没有公开的交付能力评估（另文）。

## 真正的分歧

| 争议 | 立场 A | 立场 B | 合成判断 |
| --- | --- | --- | --- |
| 多房间/持久身份是否"必须"建完整产品域 | 架构：Team 之外那层迟早要长成持久层；把房间塞进 Team 破 I1–I7，改动范围大 | 反方：M1–M4 可能已够；五是过度设计，除非多真人/多房间/IM/跨设备身份同时成立 | 这是**产品范围决策**，不是技术必然。先做小型 spike；触发条件满足再升级到完整域 |
| ds-bot 交付差是不是"结构原因" | 交付：6/7 事件可归到协议/状态/可见性，代码路径可核验；约 3/4 可消除 | 反方：n=1 天、1 个群，没有"单 Bot 短链路"对照，模型、任务设置与用法等因素未排除 | 降级为**"有代码依据的强假设"**；先跑单 Bot vs 群对照，再定权重 |
| "DSH 交付强"怎么算 | 体验：Lead 问责、共享 cwd、任务板、计划/todo | 证据：这些是"机制存在"，不是"交付保证"；等待/完成判定都是软的 | 分开评分：**机制分**高，**保证分**低；ds-bot 要补的正是保证分 |
| 先改哪里 | 反方：先把"接线 + 验收门"接上（M1–M4） | 交付：R1 交付单/系统关单门优先，R2/R3 跟上 | 收敛：**任务对象 + 关单门**先行，房间层可并行做薄 |

## 事实勘误（版本敏感）

以下几条在讨论中容易被说成通用结论，必须按版本和证据层级降级：

1. **"Team 的 mailbox 挂在 Lead 会话日志"**：只对旧版 checkout（agent-team `0.1.0-rc.8`）成立。当前安装的 `0.2.1-rc.2` 中只有 roster 与 task 在 Lead 日志，peer message 归目标成员会话；历史 `team/message/*` 仅可读（`dsh-experimental-agent-team/README.md:104,144,146`）。
2. **"experimental = private/不可用"**：错误。相关四个包都公开发布（`publishConfig.access: public`；见各包 `package.json`），只是标注实验性、无稳定性承诺。
3. **"Agent Team 没有 UI / 默认就有"**：都不准确。UI 确实有（roster、任务板、成员会话），但 bundle 默认关闭、面板只读、无 mailbox 时间线（`dsh-experimental-agent-team-profile/README.md:104`；`dsh-experimental-client-ui-agent-team/README.md:88,92`）；启用后还要刷新页面。
4. **"Lead 必须等"是硬机制**：它只是工具政策文本，没有运行时 gate（`dsh-experimental-tool-agent-team/lib/index.js:29`）；任务板也没有自动 owner release 或完成校验（`dsh-experimental-agent-team/README.md:32,136`）。"机制存在"不等于"交付必然完成"。
5. **"共享 cwd = 交付强"**：同一份 README 把它列为 Known Limitation（无 worktree 隔离、无文件锁；`dsh-experimental-agent-team-profile/README.md:106`）；写范围只是 advisory warning（`dsh-experimental-agent-team/README.md:78,136`）。
6. **"15 秒是回合超时"**：15s 是"已开工后的让位宽限"，另有 240s 静默判 missed；接力上限是 3×成员数后暂停（`ds-bot/src/host/constants.js:38,74`；`groups.js:320,318`）。
7. **"上下文满了就换新会话"**：steward 在任务未停时原地 condense，只在停止点换 fresh Session（`ds-bot/src/host/parts.js:1-16`）；"满了必换"不准确。
8. **"Tobs 拒绝 Agent Team"**：ADR-0024 拒的是"把 Assignment 做成 DSH continuable subagent"（[ADR-0024](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/docs/adr/0024-orchestrator-session-per-personabot.md)）；repo 内没有对官方 Agent Team 产品态度的 ADR，也没有使用/挂载证据。
9. **"12 分钟空转 / 4 派 2 / 重复 schedule / 静默失败 = 已证实事实"**：原文档确有记录，但自述 n=1 天、1 个群、结论为"待验证假设"（`docs/research/2026-10-28-ds-bot-delivery-gap-evidence.md:106-108`）；应说"文档记录"而不是"已独立复核"。
10. **"管理员只能靠别人"**：不成立。admin 工具面与成员相同、可自己干（`ds-bot/src/host/constants.js:64-71`）；真缺口是义务、记录、升级。

## 推荐路线

**Phase 0 先做对照，不写产品域。** 固定模型 id/思考档位及 DSH、ds-bot 版本，跑 A=单 Bot 直做、B=现值群聊；各 N=5；指标按产物判：verified_completion、user_nudges、dead_turns、dispatch_drift、duplicate_tasks、pauses、wall_clock、recovery_rate。

**Phase 1 薄房间层（若 Phase 0 证明多房间确有收益）。** Bot registry（`agent-presets/<bot>` + 只读 list）；房间 = 独立 root session；薄轮次器（一次一人、admin 先答、unseen 注入、迟到补发、暂停/继续）；已读与投递最小闭环。Team 只在"房间内多专家"时作为可选能力。

**Phase 2 交付层（无论 Phase 1 做不做都要做）。** R1 交付单 + 系统关单门：`{objective, owner, deliverable, acceptance[{check|human}], evidence[], status, deadline}`，check 全过才 done。R2 看门狗 + 兜底：超时无进展 → 系统唤醒 owner → 升级 admin 并要求它自己执行 → 群里留低噪声状态；重启按 session 事件对 open 单结算，不确定副作用不重发。R3 任务态结束条件：轮次终止从"接力计数"改为"open 交付单/未交回回报 == 0"；独立步骤 fan-out；交付单/派发表以只读快照注入（保持缓存前缀稳定）。

**Phase 3（只在触发条件满足时）产品域。** 触发：≥2 个真人、≥3 个配置互不相同的房间、需要 IM 身份、需要跨会话/跨设备 persona、需要可审计的任务派发。此时参照 Tobs 的 ADR-0016/0017/0024/0035/0045，而不是从 Team 改。

## 局限和未解问题

- 评审没有运行系统；"结构原因"是代码/文档推断，不是控制实验结论。
- Tobs 的 ADR 与实现可能随版本变化；DSH `0.2.1-rc.2` 是预发布版本，Team 的语义仍在变。
- 评审只覆盖单用户/本地场景；多人 Human、IM 外部身份、跨设备没有展开。
- "12 分钟空转"等案例来自作者单次会话记录，不能当作普遍失败率。

## 对 Nuska 的意义

- 先把"产品形态"和"交付质量"拆成两个问题；Nuska 当前最该做的是后者，而不是先造一个 Bot 产品域。
- 用 ds-bot 作为"轻量、对话原生"的基线，用 Tobs 作为"控制面、可审计"的参照；两者都不是交付已被证明的答案。
- 评审产生的 Phase 0 与 R1–R3 可以直接进入 Nuska 的实验设计；不需要等 DSH Team 稳定或 Tobs 补齐评测。

## 下一步

1. 把 Phase 0 写成可执行的实验协议（任务、权限、模型、判卷、N、记录格式），先跑 ds-bot 单 Bot vs 群。
2. 在 ds-bot 上验证 R1 的最小形态：派发四要素 + 系统关单门；用一个小任务比较"有无关单门"的虚报完成与返工。
3. 对 Tobs 做同一任务的最小复现，特别观察 Assignment 报告与独立检查结果是否一致。
4. 把"评审中仍未达成一致的问题"保留为开放问题，不用共识措辞掩盖（尤其：是否值得为多房间建产品域）。

## 相关资料

- [DSH 的 Agent 是实体还是会话？](../landscape/2026-10-29-dsh-agent-session-identity.md)
- [DS Bot 与 Tobs 的任务执行对照](../landscape/2026-10-29-dsbot-vs-tobs-execution.md)
- [Tobs 的交付能力评估证据](../evaluation/2026-10-29-tobs-delivery-evaluation.md)
- [交付式协作的最小实现设计](2026-10-29-delivery-collaboration-design.md)
- [DSH 原语核验](../landscape/2026-10-29-dsh-primitives-verification.md)
