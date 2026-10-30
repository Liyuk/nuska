# Nuska 研究地图

状态：规划中 · 2026-10-29。这里列的是研究队列，报告和实验尚未完成。

| 研究线 | 核心问题 | 首批产物 |
| --- | --- | --- |
| 体验基线 | 什么让人愿意把事情交给 Agent？ | Grok Bot / DSBot 的真实任务观察与失败记录 |
| 意图 | 如何保持强目标，并根据新信息自主调整？ | 目标、上下文更新、阶段成果与漂移案例 |
| 自主执行 | 如何让任务持续推进、恢复、停止？ | 执行和恢复机制对照、停滞与失败实验 |
| 交付与验收 | 什么证据支持“真的完成”？ | 不同交付物的自动检查和人工验收协议 |
| 宿主与集成 | 哪些能力能在不同 harness 之间复用？ | DSH、Pi、Hermes 等能力与扩展点矩阵 |
| 阶段性交付 | 如何持续交出可用成果并支持调整？ | 阶段成果质量、目标变化与人工介入 |

## 报告基本格式

每份报告标明问题、日期、范围和版本；材料、方法和证据；可复现观察；推断及不确定性；反例；结论的适用范围；下一步。记录失败案例，不把计划中的结果写成实验结果。

## 已整理的起点

### 实施方案

- [Grok bots 编排、Codex CLI 执行、脚本调度与监控](../docs/approaches/orchestrator-codex-executor.md)：一份在用实践方案，组件评审状态和未测量事项见正文。
- [实施方案索引](../docs/approaches/README.md)：后续工具实现方案的入口与格式。

- [公开资料核查：覆盖、证据与缺口](2026-10-29-source-audit.md)。

- [群上下文与个体记忆：公开方案与未解问题](context/2026-10-29-memory-and-shared-context.md)。
- [多 Agent 调度、通信与交付：从群聊到 Broker](landscape/2026-10-29-multi-agent-orchestration.md)。
- [TradingAgents：多角色决策图与交付](landscape/2026-10-29-tradingagents.md)。
- [多 Agent 分派与恢复：公开参考](execution/2026-10-29-team-execution.md)。
- [Grok Bot 任务机制：证据与研究假设](landscape/2026-10-29-grok-task-mechanisms.md)。
- [长任务交付评测方案](evaluation/2026-10-29-delivery-benchmark.md)。
- [DSH、Pi 与 Hermes 接入调研](landscape/2026-10-29-harness-integration.md)。

- [System Prompts Leaks：Grok Bot 提示词与工具线索](sources/2026-10-29-system-prompts-leaks.md)。
- [Grok Bot 逆向研究资料：阅读入口与适用边界](sources/2026-10-29-grok-bot-analysis.md)。
- [DSH 现有能力组合：多 Bot 群聊、任务与交付](landscape/2026-10-29-dsh-multi-bot-composition.md)。
- [基于 DeepSeek Harness：构建目标驱动的多 Bot 群聊与交付](landscape/2026-10-29-dsh-interactive-goals.md)。
- [两个 DeepSeek Bot 实现与长任务交付：初步证据](landscape/2026-10-29-two-ds-bot-delivery.md)。
- [DS Bot 社区讨论：本人原帖归档](community/ds-bot/README.md)。
- [从意图到交付：问题研究](synthesis/2026-10-29-intent-to-delivery.md)。
- [DS Bot 社区讨论中的研究问题](community/ds-bot/2026-10-29-research-themes.md)。

### 2026-10-29 同日一批的后续产物

这三份是上面三篇调研稿的对照与核验，另加一份据此修订的设计方案。前两篇只做源码与公开文档对照，未运行实验。

- [审阅：多 Bot 群聊与交付的能力盘点是否站得住](landscape/2026-10-29-dsh-multi-bot-composition-review.md)。对上列三篇的层级、版本与缺口判断逐条校正：承载层是 ds-bot 而非 DSH 实验原语；goal 在 Bot 会话被显式禁用；验收已有判断但输出被丢弃；群 `@` 派活不进工作树。
- [DSH 原语核验：文档说法与本机安装的差别](landscape/2026-10-29-dsh-primitives-verification.md)。八个原语逐条对照源码，附文档漏掉的已装能力，以及"profile 启用不等于会话可用"这一层。
- [DS Bot 归档证据清单：需求、失败与缺口](community/ds-bot/2026-10-29-requirements-evidence.md)。22 篇公开帖子逐行整理，按证据等级标注，并写明"只收作者本人原帖、无维护者回复"这一限制。
- [交付式协作的最小实现设计](synthesis/2026-10-29-delivery-collaboration-design.md)。目标对象与版本、工具面的交付记录、复用既有检查器、两处工作记录，以及身份（persona）的六层分层与三条硬约束。

### 2026-10-29 多 Agent 评审与执行对照（追加）

这批包括交叉审阅、实现对照与评测分析；未运行系统，结论以公开源码和文档为限。

- [DSH 的 Agent 是实体还是会话？——身份、persona 与两种 Bot 实现](landscape/2026-10-29-dsh-agent-session-identity.md)。Agent 是 Session 的实时执行面；ds-bot 用第一个私聊 session id 当 Bot 身份，Tobs 把身份放进 registry；persona 两边都是按 session 渲染的共享配置。
- [DS Bot 与 Tobs 的任务执行对照](landscape/2026-10-29-dsbot-vs-tobs-execution.md)。对话驱动 vs 控制面驱动；前台/后台、问责链路、网状 vs 星形、完成与恢复语义的差异。
- [Tobs 的交付能力评估证据](evaluation/2026-10-29-tobs-delivery-evaluation.md)。有真实模型多 Bot E2E 与功能验收，没有面向交付质量、虚报完成与长任务恢复的评估；给出可复用的评测方案。
- [多 Agent 评审：DSH Team、DS Bot 与交付问题](synthesis/2026-10-29-agent-panel-review.md)。四角色两轮评审的共识、分歧与 10 条版本敏感勘误；Phase 0/1/2/3 推荐路线。

## 最先整理的材料

1. 盘点个人博客、工程工作流、harness 研究、DSBot 的已有问题与设计；记录原处与是否可公开。
2. 记录用户实际使用 Grok Bot 的完整任务，核实产品版本和环境。
3. 挑一个同类任务，为候选系统设计可比较的任务输入、验收、观察与验收证据。
4. 检查当前 DSH 与其他候选宿主的官方扩展接口，再选择第一个实验接入点。

个人口述、工作经历与会话原始记录不自动进入公开材料；公开摘要应先核对内容和分享范围。

## 外部参考与研究判断

Graph Memory、DSH Mnemon 和 DSBot 是外部项目，不是 Nuska 作者的项目；研究它们时应标注原作者、来源和版本。作者的初步体验判断是，这些项目的一些能力偏向呈现、包装或局部便利，尚未充分解决长任务的可靠推进、目标保持和可验证交付。这是待检验的观点，不应据此断定项目的全部能力或实际效果。后续需要通过源码、真实场景和对照实验区分：哪些功能改善了体验，哪些改变了任务完成率、完整度或用户负担。

## 个人项目与旧研究的使用方式

Quota Router 和 Skin ChatLab 是作者的局部工具与体验实践，作者认为它们主要解决“糖”的问题；Skills 是个人经验的蒸馏型辅助工具，长期价值待观察。它们可提供案例，不默认等于自主交付能力。

AI Engineering Workflow Lab 和 Claude Code Harness Study 作为早期研究与个人思考的历史快照保留。项目方向和旧时的行业、产品、接口结论不直接作为 Nuska 当前依据；只有在具体研究问题需要时才回溯，相关事实按当前版本重核。
