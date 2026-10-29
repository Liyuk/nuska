# 多 Agent 调度、通信与交付：从群聊到 Broker

状态：公开资料初步调研，2026-10-29。本文比较具体机制，不是实际运行评测；“尚未验证”不等于该项目没有相关功能。这里的 broker 指协调多个独立 Agent 的消息或任务的组件，并非断言用户所说名称对应某个特定产品。

## 为什么研究这个问题

Nuska 的目标是从用户明确的目的出发，让多个 Agent 自主推进并交付阶段成果与最终成果。一个群聊、多个角色或一个消息 broker 能提供协作结构，但不能单凭其存在断定任务已被领取、执行或验收。需要分别研究：**谁负责决策、消息如何到达、工作是否并行、状态如何恢复，以及结果如何与当前目标对应**。

## 架构比较

| 具体机制 | 谁决定下一步和通信 | 并发与持久化边界 | 对交付的意义 |
| --- | --- | --- | --- |
| [AutoGen SelectorGroupChat](https://github.com/microsoft/autogen/blob/d07c667a3239ea4ab7af62a53b0f4ff205a1f23d/python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_selector_group_chat.py) | 模型或自定义函数选择下一发言者，消息广播共享群上下文 | 文档中的群聊为轮流发言；提供团队状态保存与载入，运行中保存可能不一致 | 发言和终止条件可观察，但发言轮次或终止词并不自动证实实际产物符合目标 |
| [LangChain supervisor / LangGraph](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents) | 主 Agent 把子 Agent 作为工具调用并汇总，默认子 Agent 无状态 | 可在一个回合调用多个子 Agent；[checkpointer 与 store](https://docs.langchain.com/oss/python/langgraph/persistence) 分别保存线程状态与跨线程数据；内存后端重启即丢失 | 主控有利于责任集中和上下文隔离；后台执行、崩溃后的恢复和验收仍需按部署实现验证 |
| [CrewAI hierarchical process](https://docs.crewai.com/v1.15.33/en/learn/hierarchical-process) | manager 按角色分配任务并评估结果 | 可配置 [checkpoint](https://docs.crewai.com/v1.15.33/en/concepts/checkpointing)；默认事件为任务完成，自动写入失败只记录并继续；恢复不保留所有 callable guardrail | 管理者评估是已有机制，是否发现错误完成或符合用户目的仍需实验；不能把一次检查等同独立验收 |
| [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/multi_agent/) | 可让 Agent 作为工具由主管汇总，也可 handoff 转交控制，或由代码编排 | [session](https://openai.github.io/openai-agents-python/sessions/) 保留对话历史；[trace](https://openai.github.io/openai-agents-python/tracing/) 记录调用、工具和交接；运行状态与外部动作恢复仍须具体配置和核查 | 交接控制与调用后返回不同；历史和 trace 不等于交付验收 |
| [WhatsAgent](https://github.com/ivanmak/whatsagent/blob/7b872a80d922f719b9e454ff218d7864f004271b/README.md) | 本地 broker 管理运行中的 coding agent、消息、工作区和看板；可选星形、点对点、群频道 | SQLite 保存工作区状态，终端只保留滚动尾部；仅管理由它启动的会话。其 README 指出 Codex 收到未读提醒后仍需用户手动发送读取提示 | 提供跨运行时消息与任务板参考；状态或消息送达不证明对方已执行或最终交付。该项目明确仍需人监督 |

以上阅读对应的代码仓库 HEAD 记录：AutoGen `d07c667a`；LangGraph `ffc33363`；CrewAI `90266d52`；OpenAI Agents SDK `cd26bbbc`；WhatsAgent `7b872a80`。LangChain、OpenAI 及 AutoGen 官网是会更新的在线文档，访问日期见文首；CrewAI 链接固定文档版本。HEAD 是检索时的版本定位，不表示所有在线文档已逐行核对到该提交。

## 三个不能混为一谈的动作

1. **调度**：决定谁在什么时候承担什么工作。群里的“请 A 处理”可能只是文本；任务需要可核对的接收、执行和结果关联。
2. **通信**：广播、直接消息、共享频道或交接控制。AutoGen 的 selector 是共享上下文下选择发言；WhatsAgent 允许星形或频道策略；LangChain 的 supervisor 子 Agent 则通常向主 Agent 返回结果。它们有不同的上下文与责任边界。
3. **验收**：检查结果与最新目标、质量和约束的关系。框架的终止信号、看板状态或 manager 评价都可以是输入，但需要明确检查什么和如何获取证据。

A2A 的[协议规范](https://a2a-protocol.org/latest/specification/)定义任务、状态、消息、产物、状态更新、查询与取消等互通概念；它是 Agent 之间的协议，而非完整的调度策略或质量证明。其接口可作为未来跨框架接入候选，是否适用、可实现到何种程度仍需具体验证。

## 对 Nuska 的候选设计

可以先用一个负责整体目标的协调者，加多个执行者，但不预设中心化一定最优。协调者的责任是维护当前目标和阶段成果、选择依赖关系、检查派发和执行证据、处理用户新上下文并汇总结果；消息 broker 负责通信与可观测性，宿主负责模型、工具与执行。必要时可以比较点对点方案，但应约束责任归属以防重复执行或讨论漂移。

值得实验的基础记录包括：目标及版本、任务和尝试 ID、发起者与接收者、消息发送和读取、执行事件、产物引用、验收结果、停止原因。状态为未知时保留未知；用户调整目标后，迟到结果需标记所依据的版本并重新判断是否可用。断点记录与实际外部副作用之间可能存在落差，恢复前需核对，避免重复执行。

## 验证问题

- 同一目标下，串行群聊与并行委派是否更快形成可用阶段成果？是否出现重复劳动或上下文冲突？
- 派发后停止接收方、重启 broker 或切断连接：能否区别已发送、已领取、执行中和结果未知？恢复会否重复副作用？
- 目标中途更新时，正在运行的子任务怎样收到变更？旧产物是否被误当新目标的成果？
- 给出看似完成但遗漏关键内容的产物，manager、自动检查和人工复核分别能否发现？
- 比较单 Agent 和多 Agent，记录最终完整度、质量、阶段交付和用户干预次数；多 Agent 本身不是效果改善的证据。

相关研究：[团队执行](../execution/2026-10-29-team-execution.md)、[Harness 接入](2026-10-29-harness-integration.md)、[交付评测](../evaluation/2026-10-29-delivery-benchmark.md)。
