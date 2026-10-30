# Nuska

**Understand the intent. See it through.**

Nuska 是一个 AI Agent 研究与实践项目，探索如何让 AI 理解人的目标，在变化的上下文和真实工作环境中自主推进复杂任务，并交付可验证的结果。

项目结合前沿研究、真实场景、工程原型和可复现实验，研究长期任务执行、人机协作、多 Agent 协作、上下文与记忆，以及结果评估等问题。

人通常从明确、强烈的目标出发；随着执行中获得新的上下文，可以补充信息和调整方向。系统应围绕当前目标独立推进，交付可用的阶段性成果和最终结果，在确有必要时再请求人的判断。

## 研究问题

- 如何理解用户的目标与约束，并在补充上下文或调整方向时持续更新？
- 如何让 Agent 跨会话、跨工具持续推进复杂任务，发现停滞并从失败中恢复？
- 如何验证阶段性成果和最终交付的完整性、可信度与可用性？
- 如何让用户了解进展、随时调整方向，同时让 Agent 在不需要判断时自主推进？
- 如何协调多个 Agent 分工、共享上下文和记忆，并整合结果？
- 如何在真实工作环境中使用工具、验证操作结果，并判断何时需要用户的判断或授权？

## 项目方向

[项目总规划](docs/project-plan.md) · [研究地图](research/index.md) · [项目结构](docs/project-structure.md) · [架构草案](docs/architecture/system-overview.md) · [实施方案](docs/approaches/README.md) · [社区讨论归档](research/community/ds-bot/README.md)

项目总规划、项目结构和架构草案记录讨论方向；实施方案记录特定场景中的实践机制。

项目将逐步汇集使用观察、历史研究、案例、实验和原型。Grok Bot 是一个体验参照；具体使用哪些模型、工具或 agent harness 尚未决定。

当前处于问题梳理和研究阶段；上述目标是研究方向，不代表项目已经具备这些能力。

## 参与研究

欢迎在 [Discussions](https://github.com/Liyuk/nuska/discussions) 分享想法、体验和问题，通过 [Issues](https://github.com/Liyuk/nuska/issues) 提出研究任务、实验或报告错误；参与方式和证据标准见 [CONTRIBUTING.md](CONTRIBUTING.md)。仓库设置和参考依据见 [GitHub 配置说明](docs/github-setup.md)。

仓库目前尚未声明开源许可证。

## 名称

Nuska 源自美索不达米亚神话。在一则古代文本中，Nuska 领会意图、与委托者商议，并代为执行。这个形象为项目的研究方向提供了灵感。[来源：牛津大学苏美尔文学电子文本语料库](https://etcsl.orinst.ox.ac.uk/edition2/etcslgloss.php?charenc=&lookup=c4051.104&sn=ON)。
