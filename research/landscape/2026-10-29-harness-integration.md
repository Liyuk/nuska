# Harness 能否承载目标驱动交付：DSH、Pi 与 Hermes

状态：公开文档调研 · 2026-10-29；各项为接入线索而非已跑通的集成或排名。比较采用下列固定源码版本，不预设 Nuska 使用哪一个作为底座。

| 能力 | DeepSeek Harness | Pi coding agent | Hermes Agent |
| --- | --- | --- | --- |
| 可观察扩展点 | 插件和 `session/event`、Agent 生命周期 | TypeScript 扩展可订阅事件、拦截工具调用、注入上下文 | plugin hooks、gateway hooks、shell hooks 等；适用范围不同 |
| 目标与持续推进 | 同会话 goal 状态与可选续行驱动器；恢复后需要重新授权 | 扩展可提供自己的状态与控制；本文未验证内建等价 goal 机制 | 可扩展生命周期；本文未验证内建等价 goal 机制 |
| 存储与恢复 | 会话事件、goal 状态及显式续行语义 | 扩展可向会话追加持久条目；实际恢复策略须验证 | 有多种运行入口；具体任务状态与恢复语义须逐个验证 |
| 用户中途修正 | Agent 提供 followup/steering；送达和实际处理不同 | 可扩展输入与事件；具体行为须实测 | 不同 CLI / gateway / hook 的行为与边界须实测 |
| 完成验收 | goal 文档说明没有独立评估器 | 本次未发现已核验的通用独立交付验收合同 | 本次未发现已核验的通用独立交付验收合同 |

“未验证”不是“不存在”。本次没有比较它们的运行成功率，也没有证明任意插件可以跨框架复用。

## 已查看的上游材料

- DSH 固定版本 `219cc443`：[目标状态](https://github.com/deepseek-ai/deepseek-harness/blob/219cc4434efe27bb38573d98e79b4ddc714dacea/packages/goal/goal/README.zh.md)、[续行驱动](https://github.com/deepseek-ai/deepseek-harness/blob/219cc4434efe27bb38573d98e79b4ddc714dacea/packages/goal/goal-round-driver/README.zh.md)、[Agent 生命周期](https://github.com/deepseek-ai/deepseek-harness/blob/219cc4434efe27bb38573d98e79b4ddc714dacea/docs/agent-lifecycle.zh.md)。
- Pi 固定版本 `aee93326`：[Extensions](https://github.com/badlogic/pi-mono/blob/aee933269ba79b84e7b7454097c1d4c426021d82/packages/coding-agent/docs/extensions.md)：自定义工具、事件、输入与持久条目。
- Hermes 固定版本 `ef75bc70`：[Event Hooks](https://github.com/NousResearch/hermes-agent/blob/ef75bc708867e3884cb40a91363be6dc6fddc034/website/docs/user-guide/features/hooks.md)：不同 hook 的运行范围、生命周期与控制能力。

## 接入方案候选

- **宿主内插件**：接入目标、事件和用户输入，宿主负责模型与工具；需确认生命周期及运行时限制。
- **独立协调服务**：跨宿主追踪目标、阶段成果和证据；需证明如何关联宿主事件及避免重复调度。
- **混合**：用薄插件采集与控制宿主能力，共享服务保存经验证的任务语义；并非当前决定。

Nuska 核心可能需要目标版本、阶段成果、交付证据、工作状态与用户纠偏语义；这些是候选合同，不先假定必须另造 harness 或同步维护两个独立权威状态。

## 下一步验证

从[交付评测方案](../evaluation/2026-10-29-delivery-benchmark.md)选一个任务，先在一个宿主实现真实事件采集和独立验收，再在第二宿主复现。测试目标中途修订、阶段交付、失败、终止和恢复；为不支持的宿主能力明确标注限制。收集证据后再确定插件形式和公共接口。
