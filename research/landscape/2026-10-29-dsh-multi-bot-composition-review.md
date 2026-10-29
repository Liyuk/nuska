# 审阅：多 Bot 群聊与交付的能力盘点是否站得住

状态：审阅意见 · 2026-10-29。只做源码与文档对照，未运行实验，不评价任何产品路线。

## 问题与范围

要回答的问题：现有三份关于「DSH 多 Bot 群聊与交付」的研究稿，在**层级选择、版本对应和缺口判断**上是否成立；如果不成立，后续设计应该从哪里开始。

审阅对象：

- [多 Bot 群聊与交付：现有能力和缺口](2026-10-29-dsh-multi-bot-composition.md)（主）
- [基于 DeepSeek Harness：构建目标驱动的多 Bot 群聊与交付](2026-10-29-dsh-interactive-goals.md)
- [两个 DeepSeek Bot 实现与长任务交付：初步证据](2026-10-29-two-ds-bot-delivery.md)

范围只到结论与证据链；不重新做产品调研，不评价 DSH 或 ds-bot 的产品方向。不包含：运行实验、Grok Bot 内部机制、模型效果比较。

## 材料和方法

三份被审稿件都声明「没有启动 DSH 或验证组合能工作」，结论来自固定源码快照。因此本报告把它们的判断逐条对照到**实际承载层**的源码与公开文档，标注成立 / 需修正；再横向对照三稿之间是否自相矛盾。

| 层 | 固定版本 | 说明 |
| --- | --- | --- |
| DSH | 本机安装 `0.2.1-rc.2`；被审稿件引用快照 `f3803c96` | 两者不是同一个发布，见第 4 节 |
| ds-bot（群、Bot 身份、工作树、记忆的提供者） | `v0.2.3`，commit [`4a7b550`](https://github.com/Fei2411/DS-Bot/tree/4a7b55069ad300eae8be42a74f31bc170b40ead7) | 上游发行 tag 与本地安装包版本一致；npm 包内无 `gitHead`，commit 以 tag 为准 |

方法上的一个限制先写明：ds-bot 是单一插件，内部 35 个模块通过运行时对象互相调用（[`ds-bot/index.js`](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/index.js)），没有面向第三方的公开扩展接口。下面的结论因此是"读源码得到的实现事实"，不是"官方承诺的合同"。

## 发现与证据

### 1 层级：群、长期身份和工作树都在 ds-bot，不在 DSH

被审稿件的原语表以 DSH 的 goal、plan mode、Team、Ralph、workflow 为主，并把「群/Bot 交互层」写成待建能力。对照源码，这一层的实际承载者是 ds-bot：

| 能力 | 实际位置 | 证据 |
| --- | --- | --- |
| 长期 Bot 身份（名字、角色、instructions、模型、工作目录、权限） | ds-bot roster | [`roster.js`](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/src/host/roster.js) |
| 群回合：成员逐个发言、`@` 交接、`[PASS]`、未回复与停放通知 | ds-bot groups | [`groups.js`](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/src/host/groups.js) |
| Bot 之间的派活树、结果自动上返 | ds-bot handoffs | [`handoffs.js`](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/src/host/handoffs.js) |
| 三 scope 记忆（Bot / 群 / 团队）与每次发言后的记忆复盘 | ds-bot memory | [`ds-bot/README.md`](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/README.md)「Memory」一节 |
| 会话续行：checkpoint（原地压缩）或 handoff（换新段 + 交接 note） | ds-bot steward / parts | [`steward.js`](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/src/host/steward.js)、[`parts.js`](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/src/host/parts.js) |

DSH 侧没有群聊，也没有记忆包；两处都可以用包集合反查确认（见[原语核验](2026-10-29-dsh-primitives-verification.md)）。

**需修正的判断**：主稿把「实验性 Agent Team 的任务板」写成派活与领取的试验起点。Team 是单进程、独立 roster，与 ds-bot 的群和 Bot 不共享状态；用它做起点会绕开现有实现，得到的结论无法回搬到实际系统。工作树应该以 ds-bot 的 works 为起点，Team 只作对照。

### 2 goal 在 Bot 会话里被禁用，不能当作续行主轴

ds-bot 在 Bot 会话中主动关闭 DSH goal：

```
// DS Bot carries no goal across conversation parts, so Bot Sessions do not run DSH goals.
const GOAL_TOOLS = ['create_goal', 'update_goal', 'get_goal']
const GOAL_REFUSAL = 'DS Bot does not run goals. Ask the Bot in a message instead.'
```

（[`tools.js`](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/src/host/tools.js) 顶部注释与常量，同文件另有把已存在的 active goal 主动 block 的逻辑。）

这不是遗漏，是设计取舍：ds-bot 用自己的会话分段 + checkpoint/handoff 承担"跨上下文窗口继续"，一个并行的 goal 驱动会与它抢同一件事。

**自相矛盾**：`interactive-goals` 第 109 行已经记过「原 DSBot 在 Bot 会话中屏蔽 DSH goal」，但同一篇 4.4 仍写「goal driver 可用于单会话续行」，主稿也把 goal 列在原语表第一行。读者按文档去做，会得到一个跑不通的方案。**在 Bot 会话这一层，goal 目前不是可用原语，而是被显式拒绝的原语。**

### 3 验收不是"没有"，而是"有判断、没输出、没记录"

主稿把「独立验收」列为待建。实际实现里已经有一个会逐项对照用户请求的检查器，它每次换段前运行一次：

> `"switch"`: the current piece of work has reached a stopping point. …
> Before you choose "switch", check each part of what the user asked against what the assistant actually did, and look for a question the assistant asked that the user has not answered. **A part that was not done, even when the assistant says it is all done, or a question answered only with thanks or an acknowledgment, means the work is still under way.**

（`steward.js` 的判定提示词。）

它的问题只有一个：输出被丢掉了——只用来决定"换段还是压段"，"有部分没做"这个判断没有变成任何可引用的东西。

同一处，交接 note 的模板里已经有交付状态的结构：

| 小节 | 模板要求的内容 |
| --- | --- |
| `Goals` | 当前目标，以及先后变化 |
| `Progress` | `Done:` 完成项与结果、`In progress:` 进行到哪、`Blocked:` 等什么 |
| `Decisions` | 决定了什么、为什么、否决了什么 |
| `Open threads` | 做过的承诺、等待的答复 |
| `Next step` | 唯一的下一步 |

（`parts.js` 的 `NOTE_SECTIONS`。）

所以缺口的性质是：**判断有了，结构化没有，可见范围也没有**（只在本人换段时产生，群里看不到）。最小实现因此不是新建任务平台，而是把这三样接起来。

### 4 版本对不上，而且"Team 已启用"要分两层说

- 主稿固定 `f3803c96`；该 commit 的发布版本是 `0.2.2-alpha.2`，而本机安装的是 `0.2.1-rc.2`。研究稿写"现有能力"时，指的是一个尚未安装的版本。逐条核验见[原语核验](2026-10-29-dsh-primitives-verification.md)。
- 「Agent Team Profile 默认关闭」只对上游成立：它不在内置模板里。但一个 web profile 完全可以把它列进 `bundles`，那时它在 profile 层是启用的。
- 更要紧的是第二层：**profile 启用不等于 Bot 会话能用**。ds-bot 在 `standard` preset 可用时给每个 Bot 绑定 `agentPreset: 'standard'`（[`roster.js`](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/src/host/roster.js) 的 `botPreset()`，注释说明 Session 会固定使用创建时的 preset），而 Web 的 standard preset 会在 preset 内重新挂一套 legacy subagent 工具；Team 工具是 Agent 作用域注册。所以在 Bot 会话里 Team 是否可达，必须按会话核验工具表，不能按 profile 推断。

### 5 群派活不进工作树，群记录按窗口滚动

两件事叠在一起，决定群场景没有持久交付状态：

1. 工作树只覆盖 Bot 之间**私聊**的请求：`handoffs.js` 的头注释把 work 定义为"一个 Bot 给另一个 Bot 的请求"，并说明结果自动往上冒、重启后继续等。群里的 `@Name` 走 `groups.js` 的另一条路径，不建 work。
2. 群消息只保留最近 60 行，超出即删（`README.md` 的「Data and backups」表里写明 `group-lines/` 的清理规则与群最新 60 行的关系）。

结果是：私聊派活有树、有结果上返，但没有验收字段；群派活**完全没有记录**，唯一痕迹是最近 60 行。任何只改 works 的交付层，只覆盖一半场景。

### 6 被审稿件漏掉的已装原语

[原语核验](2026-10-29-dsh-primitives-verification.md)另有一份完整清单；与交付直接相关的至少包括：事件溯源的 session 日志、持久化布局与崩溃恢复、会话 fork、跨会话只读检索、schedule（Host 级持久提醒）、后台作业（`job_*`）、worktree、`present` 与 `ask_user_question`。以及一条结构性事实：**DSH 没有统一编排器**——`ralph` 架在 workflow 引擎上，workflow / ralph / team / 普通 subagent 都以 subagent 为底座，goal 和 todo 只是同一个 Agent 的会话内状态。这解释了为什么"再接一层任务平台"会加剧机制碰撞。

## 局限和未解问题

- 全部结论来自静态阅读。三份稿件自己声明的"未启动 DSH"这一限制，本报告同样继承。
- Bot 会话里 Team 工具的可见性只做了静态推断（preset 注册范围），需要一次真实会话核对。
- ds-bot 没有公开扩展接口这一点，是读 `index.js` 的模块组织得出的推断，不等于维护者不会加。
- 三稿里的「两个 DSBot」比较未复核；本报告只在层级问题上引用它。
- 版本关系只能确认"两个发布不同"，无法从 npm 包内确认 commit，因此不能断言两者代码差异的具体范围。

## 对 Nuska 的意义

1. **承载层判断要改**：研究多 Bot 交付，对象是 ds-bot，不是 DSH 的实验原语。DSH 影响的是底层会话、工具、权限、事件；群、身份、工作树、记忆都在上层插件里。
2. **缺口判断要改**：目标（结构化、可引用、带版本）和验收（结构化、可见、可复核）是真缺口；任务板和派发机制不是——它们在私聊一侧已经存在。
3. **工程纪律要加一条**：现在同时存在多种"继续"机制（goal 轮次驱动、ds-bot 的段续行、Ralph、workflow、Team）。新增交付层之前，先明确哪一种是权威，否则用户看到的是机制互相停放和互相覆盖。

## 下一步

1. 按[最小实现设计](../synthesis/2026-10-29-delivery-collaboration-design.md)做一次最小闭环实验，先测"未完成项会不会被主动报出来"。
2. 核对 Bot 会话的实际工具表（Team 工具是否存在），补齐第 4 节第二层。
3. 在主稿上做一次口径修订：把"Team 任务板作为起点"改为"ds-bot 工作树作为起点、Team 作对照"，并补一句 goal 在 Bot 会话被禁用。
