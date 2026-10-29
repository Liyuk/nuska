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

- [公开资料核查：覆盖、证据与缺口](2026-10-29-source-audit.md)。

- [群上下文与个体记忆：公开方案与未解问题](context/2026-10-29-memory-and-shared-context.md)。
- [多 Agent 调度、通信与交付：从群聊到 Broker](landscape/2026-10-29-multi-agent-orchestration.md)。
- [TradingAgents：多角色决策图与交付](landscape/2026-10-29-tradingagents.md)。
- [多 Agent 分派与恢复：公开参考](execution/2026-10-29-team-execution.md)。
- [Grok Bot 任务机制：证据与研究假设](landscape/2026-10-29-grok-task-mechanisms.md)。
- [长任务交付评测方案](evaluation/2026-10-29-delivery-benchmark.md)。
- [DSH、Pi 与 Hermes 接入调研](landscape/2026-10-29-harness-integration.md)。

- [Grok Bot 逆向研究资料：阅读入口与适用边界](sources/2026-10-29-grok-bot-analysis.md)。
- [基于 DeepSeek Harness：构建目标驱动的多 Bot 群聊与交付](landscape/2026-10-29-dsh-interactive-goals.md)。
- [两个 DeepSeek Bot 实现与长任务交付：初步证据](landscape/2026-10-29-two-ds-bot-delivery.md)。
- [DS Bot 社区讨论：本人原帖归档](community/ds-bot/README.md)。
- [从意图到交付：问题研究](synthesis/2026-10-29-intent-to-delivery.md)。
- [DS Bot 社区讨论中的研究问题](community/ds-bot/2026-10-29-research-themes.md)。

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
