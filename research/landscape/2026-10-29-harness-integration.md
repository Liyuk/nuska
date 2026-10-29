# Harness 能否承载目标驱动交付：DSH、Pi 与 Hermes

状态：公开文档调研 · 2026-10-29；各项为接入线索而非已跑通的集成或排名。比较采用下列固定源码版本，不预设 Nuska 使用哪一个作为底座。

| 能力 | DeepSeek Harness | Pi coding agent | Hermes Agent |
| --- | --- | --- | --- |
| 可观察扩展点 | 插件和 `session/event`、Agent 生命周期 | TypeScript 扩展可订阅事件、拦截工具调用、注入上下文 | plugin hooks、gateway hooks、shell hooks 等；适用范围不同 |
| 目标与持续推进 | 同会话 goal 状态与可选续行驱动器；恢复后需要重新授权 | `agent_before_settle` 可请求续行；需自行定义目标与终止条件 | 已提供子代理委派和后台结果回送；不能据此推断有跨重启持续任务引擎 |
| 存储与恢复 | 会话事件、goal 状态及显式续行语义 | 扩展可追加持久条目，并依据当前分支重建状态 | 会话与已完成结果可持久化；运行中的子代理在进程重启后不会自动恢复 |
| 用户中途修正 | Agent 提供 followup/steering；送达和实际处理不同 | 支持 steer 和 followUp，交付时机不同 | 子代理可接受 steer；入队不等于已经送达，关闭前未送达的内容会返回 |
| 完成验收 | goal 文档说明没有独立评估器 | 本次未发现已核验的通用独立交付验收合同 | 本次未发现已核验的通用独立交付验收合同 |

“未验证”不是“不存在”。本次没有比较它们的运行成功率，也没有证明任意插件可以跨框架复用。

## 已查看的上游材料

- DSH 固定版本 `219cc443`：[目标状态](https://github.com/deepseek-ai/deepseek-harness/blob/219cc4434efe27bb38573d98e79b4ddc714dacea/packages/goal/goal/README.zh.md)、[续行驱动](https://github.com/deepseek-ai/deepseek-harness/blob/219cc4434efe27bb38573d98e79b4ddc714dacea/packages/goal/goal-round-driver/README.zh.md)、[Agent 生命周期](https://github.com/deepseek-ai/deepseek-harness/blob/219cc4434efe27bb38573d98e79b4ddc714dacea/docs/agent-lifecycle.zh.md)。
- Pi 固定版本 `aee93326`：[Extensions](https://github.com/badlogic/pi-mono/blob/aee933269ba79b84e7b7454097c1d4c426021d82/packages/coding-agent/docs/extensions.md)：自定义工具、事件、输入与持久条目。
- Hermes 固定版本 `ef75bc70`：[Event Hooks](https://github.com/NousResearch/hermes-agent/blob/ef75bc708867e3884cb40a91363be6dc6fddc034/website/docs/user-guide/features/hooks.md)：不同 hook 的运行范围、生命周期与控制能力。

## 按实际接入问题展开

### DeepSeek Harness：单会话目标与子代理的边界

在原先固定的 `219cc443` 快照之外，2026-10-29 又查看了上游 `master` 的 [`f3803c96` 目标驱动文档](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/goal/goal-round-driver/README.md)：驱动器在 agent 整体空闲、续行已授权且轮次有剩余时推进；如果加载了 subagent 服务，还会等待正在推进的后代 settle。目标版本修改会通过 revision fence 使旧轮次失效。恢复或 fork 后 active 目标仍需人工授权 resume，临时 provider 或持久化故障不会隐式自动重试。这些描述是该快照的契约，不代表群任务跨进程自动恢复。

**对 Nuska 的意义**：可先研究复用同会话目标、轮次准入以及实验性 Team 的成员与任务板；跨群责任、派发投递保障、阶段产物与独立验收仍须验证或补足；尤其要测试目标修订与正在运行的子任务如何交互，不能假定 revision fence 会自动撤销所有外部副作用。

### Pi：扩展可以控制续行，但需自建目标语义

在 [`aee93326` Extensions 文档](https://github.com/badlogic/pi-mono/blob/aee933269ba79b84e7b7454097c1d4c426021d82/packages/coding-agent/docs/extensions.md)中，`agent_end` 不是最终空闲信号：后面可能还有重试、压缩后重试和排队消息。`agent_before_settle` 是可行动的最后边界，扩展可以追加条目并请求一次续行；无条件续行会反复触发，错误和中止仍是硬退出。`agent_settled` 是最终通知点。`pi.appendEntry()` 持久化扩展数据，但这些条目本身不会进入模型上下文；重建状态应依据当前会话分支，而非所有历史分支。文档还列出通过自定义工具与进程执行启动子代理的示例，这证明可扩展，不等于内建耐久派发。

输入方面，`steer` 在当前 assistant turn 的工具调用完成后送入下一次模型调用，`followUp` 等 Agent 完成工具工作才送入；是否在实际运行中完成目标修订仍需观察产物和事件。由此可做 Pi 插件原型，但目标、停止准则、跨进程恢复以及群级状态都不能从这些 API 自动推导出来。

### Hermes：已有委派与纠偏，重启后的执行仍是难点

[`ef75bc70` 子代理委派文档](https://github.com/NousResearch/hermes-agent/blob/ef75bc708867e3884cb40a91363be6dc6fddc034/website/docs/user-guide/features/delegation.md)描述了后台委派、结果回送、子代理状态和 steer/stop。子代理默认继承父级已启用的工具集合；默认叶子子代理不能写共享长期记忆、发送消息或继续委派，嵌套协调需要启用相应角色和深度设置。steer 成功入队不代表子代理已消费；关闭前未送达的内容会随结果以 pending steer 返回。

同一文档明确区分**完成结果的持久投递**和**执行本身的持久性**：进程重启不恢复正在运行的子代理，其尝试会变成 `unknown`；已完成但尚未送达的结果可以恢复投递。关闭或重置拥有者会中断其子代理。因此恢复流程应检查实际产物和可能已发生的副作用，不能盲目重跑。[记忆文档](https://github.com/NousResearch/hermes-agent/blob/ef75bc708867e3884cb40a91363be6dc6fddc034/website/docs/user-guide/features/memory.md)提供个体记忆线索，但不证明群内共享权限、记忆冲突或多 Bot 目标一致性已解决。

Hermes 的这些能力值得作为比较基线，而非简单归类为只有交互和工具调用；它们是否减少用户催促、提高任务完整度及交付质量，需要相同任务的运行证据。

### 建议验证矩阵

| 场景 | 要观测的事实 | 通过条件示例 |
| --- | --- | --- |
| 阶段交付后继续 | 有可阅读产物，接着出现有效工作，而非仅重复计划 | 至少一个可用阶段产物与后续实际工具事件 |
| 运行时改变范围 | 记录输入入队、交付和实际处理，比较旧任务与结果 | 最终结果遵循最新目标，旧结果标明版本 |
| 多成员派发 | 检查派发 ID、领取、完成与汇总的关系 | 不将仅生成的派发文本当成执行证据 |
| 进程中断与重启 | 区分存储恢复、续跑授权、未知的外部副作用 | 无重复执行，不能证明成功的部分保持未知 |
| 交付验收 | 检查文件、引用和面向目标的质量 | 明确区分自动检查、人工判断和未完成事项 |

## 接入方案候选

- **宿主内插件**：接入目标、事件和用户输入，宿主负责模型与工具；需确认生命周期及运行时限制。
- **独立协调服务**：跨宿主追踪目标、阶段成果和证据；需证明如何关联宿主事件及避免重复调度。
- **混合**：用薄插件采集与控制宿主能力，共享服务保存经验证的任务语义；并非当前决定。

Nuska 核心可能需要目标版本、阶段成果、交付证据、工作状态与用户纠偏语义；这些是候选合同，不先假定必须另造 harness 或同步维护两个独立权威状态。

## 下一步验证

从[交付评测方案](../evaluation/2026-10-29-delivery-benchmark.md)选一个任务，先在一个宿主实现真实事件采集和独立验收，再在第二宿主复现。测试目标中途修订、阶段交付、失败、终止和恢复；为不支持的宿主能力明确标注限制。收集证据后再确定插件形式和公共接口。


补充：[DSH Agent Team、计划、重复提醒、Ralph 与 workflow 的组合及限制](2026-10-29-dsh-multi-bot-composition.md)。
