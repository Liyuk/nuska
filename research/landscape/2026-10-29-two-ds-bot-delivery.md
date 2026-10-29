# 两个 DeepSeek Bot 实现与长任务交付：初步证据

日期：2026-10-29。范围：静态源码、项目 README 和设计记录；GitHub main 版本再次核对为下述 SHA，未运行两个系统，也未做 Grok Bot 对照实验。本文研究问题来自用户判断，并不声称发现了所有实现或证明运行时成功率。

## 研究问题

用户观察：两个项目的交互与组织方式似乎没有充分解决长任务中的目标漂移、虚报完成和交付型协作，部分限制可能妨碍自主推进。这是待验证的假设。这里的“长任务幻觉”暂指未经证据支持地声称进展、委派或完成，不等同于所有事实性幻觉。

## 版本与材料

- **Fei2411/DS-Bot**：本地 checkout `e0432463bd4f88b36c562ab2fcc40696b96e3359`；本次检查的 `groups.js`、`tools.js` 没有本地修改。查看时远端 `main` 为 `4a7b55069ad300eae8be42a74f31bc170b40ead7`，另行核对了该远端版本的 `groups.js` 与 `tools.js`，下述限额和 goal 屏蔽逻辑仍存在。
- **BotHarness/DeepSeekBot（Tobs）**：GitHub `main`，`acb73c46c09da94d2d924595edc2a67f9e68607b`；读取 README、相关 ADR 和少量源文件；没有完整审计源码。
- 个人历史反馈见本地 `private/sources/github-ds-bot/`，如 [issue #611](https://github.com/Fei2411/DS-Bot/issues/611) 对接力上限及任务结束条件的讨论。

## Fei2411/DS-Bot：有明确的自主推进限制

1. **群接力限额会暂停后续 Bot 间接力。** 本地 `groups.js` 定义默认值为成员数三倍；Bot 互相调用达到阈值后，后续接力被停放，用户发言或按 Continue 后可继续。已有正在执行的工作与群接力不完全相同：源码说明长工具工作可以继续，不应表述为所有任务被终止。[固定版本源码](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/src/host/groups.js)
2. **Bot 会话屏蔽 DSH goal。** 本地 `tools.js` 隐藏 create/get/update goal 工具，并把在 Bot 或群会话启动的活跃 goal 标为 blocked；注释指出 DS Bot 不跨对话分段保留 goal。已有让步记录把这解释为命令和会话边界问题，并提出未来 Bot 自身跨段目标能力作为方向。[源码](https://github.com/Fei2411/DS-Bot/blob/4a7b55069ad300eae8be42a74f31bc170b40ead7/ds-bot/src/host/tools.js) · [设计记录](https://github.com/Fei2411/DS-Bot/blob/e0432463bd4f88b36c562ab2fcc40696b96e3359/docs/plans/2026-10-13-dsh-concessions.md)
3. **含义与限制。** 这两项是明确的执行约束，可能导致依赖 Bot 接力或 DSH goal 的任务需要用户再次干预；静态代码不能证明所有长任务失败，也不能说明限额必然不合理。它控制失控和成本，但与用户期望的低监督持续交付存在待测张力。

## BotHarness/DeepSeekBot：已有专门的委派机制

1. 项目 README 描述 Assignment：Bot 可以把较大任务委派到独立工作并接收报告；也描述后台任务结果可唤醒空闲 Bot。它不只是群聊接力。[固定版本 README](https://github.com/BotHarness/DeepSeekBot/blob/acb73c46c09da94d2d924595edc2a67f9e68607b/README.en.md)
2. [ADR 0017](https://github.com/BotHarness/DeepSeekBot/blob/acb73c46c09da94d2d924595edc2a67f9e68607b/docs/adr/0017-assignments-are-sessions-no-task-entity.md) 将 Assignment 身份映射到 DSH Session，并明确不建立单独 Task 实体；这是设计选择，不自行证明不能跟踪目标或完成质量。
3. [ADR 0045](https://github.com/BotHarness/DeepSeekBot/blob/acb73c46c09da94d2d924595edc2a67f9e68607b/docs/adr/0045-orchestrator-manages-assignments-through-a-durable-directory.md) 描述持久目录、恢复、报告、任务请求，以及默认 3 个并发独立 Assignment 的配额；超过配额的创建或唤醒会失败而非自动进入队列。它将执行活动与语义报告区分，也说明目标受控执行是设计重点。文档存在并不等于所有运行情形均已验证。
4. [ADR 0265](https://github.com/BotHarness/DeepSeekBot/blob/acb73c46c09da94d2d924595edc2a67f9e68607b/docs/adr/0265-orchestrators-delegate-through-assignments.md) 将 orchestrator 的独立委派路径收敛到 Assignment。它可能限制特定委派方式，但该限制是否阻碍目标任务仍需实验；不能把限制并发与禁止长任务画等号。
5. 已抽查的云工作工具是受限制的健康检查能力，不代表所有 Assignment 工作或验收机制。当前抽样不足以断言项目没有独立验收、目标保持或长任务自动续跑机制。

## 推断：真正需要比较的交付闭环

- 目的是否在多轮澄清、改动和上下文分段后仍被保留，谁负责最新目标；
- 承诺派发与真实派发、任务领取、进行中状态是否一致；
- 每次模型声称完成时，是否有独立可检查的产物和适当的验收依据；
- 后续工作在暂停、重启、工具失败、配额上限时会怎样继续或通知用户；
- 模型报告、宿主生命周期状态和验收结果是否可区分；
- 阶段结果、最终质量和用户催促次数如何一起衡量。

这些是 Nuska 的候选研究问题，不表示两个项目一定都缺少相应实现。调度任务次数或创建任务对象本身，也不能保证结果符合用户目的。

## 建议的对照实验

使用一个可由独立检查验证的真实交付任务，含多步骤、一次用户修正、一次可控失败和一次上下文或进程中断；对两种系统、可用时的 Grok Bot 使用一致的目标和权限。记录实际派发与领取、任务暂停原因、是否自动恢复、产物与独立验收、虚报或遗漏、人工催促次数和阶段成果。针对 Fei2411 验证接力阈值；针对 Tobs 分别验证并发上限、Assignment 恢复和报告的证据来源。重复运行并保存版本和轨迹后再报告成功率。

## 后续核验

- 在 Fei2411 最新 main 上实际运行接力上限和 goal 场景，检查用户感知与恢复行为。
- 追踪 Tobs Assignment 创建、终止、恢复和报告的实际实现与测试，包括是否存在独立验收路径。
- 搜索并归档用户在 BotHarness 仓库的 issue/discussion；目前按 GitHub `Liyuk` 搜索 issue 作者与评论者为零，discussion 未完成完整检索。
- 在不暴露个人或组织内容的前提下整理具体案例，保留原始日志和环境。
