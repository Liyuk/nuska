# 目标驱动的多 Agent 分派与恢复：公开参考

状态：资料调研 · 2026-10-29。关注任务如何从用户的目标到实际领取、执行、阶段交付与验收；以下不是对 Grok Bot 未公开实现的断言。

## 公开研究和实现

- [Magentic-One 论文](https://arxiv.org/abs/2411.04468)描述由 orchestrator 规划、跟踪并在出错时重新规划的多 Agent 系统；[AutoGen 文档](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html)提供其 AgentChat 版本。系统设计及论文实验说明这条路线值得研究，但不能证明同一结构适合任意长期交付，也不等于独立结果验收。
- [AutoGen 群聊基础类](https://github.com/microsoft/autogen/blob/main/python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py)描述群成员通过消息共享上下文。共享消息与工作项被领取、成员完成执行及结果通过验收是不同事实。
- [BotHarness Assignment 设计](https://github.com/BotHarness/DeepSeekBot/blob/acb73c46c09da94d2d924595edc2a67f9e68607b/docs/adr/0045-orchestrator-manages-assignments-through-a-durable-directory.md)描述以宿主会话为身份、用目录和报告呈现工作，并记录交付意图和恢复；这是一种公开设计，不代表其解决所有交付质量问题。
- [Temporal Activity 文档](https://docs.temporal.io/activity-definition)讨论重试条件下的 activity 与幂等实践；持久化调度本身不证明外部副作用只发生一次。Nuska 不因此预设采用 Temporal。
- [OpenHands Agent SDK 实现](https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py)提供持久会话和事件、fork 等机制；这些能力可用于观察和恢复，不直接证明结果已满足用户目标。

## 候选事实模型

把用户目标及版本、工作项、派发、领取、尝试、产物、检查与最终验收分别记录；允许关联群、Bot、宿主会话及工具事件。模型输出“我来处理”只能作为声明：必须另外观察实际派发、接收、执行和产物。领域对象、独立队列或事件投影都只是候选，需根据宿主的真实接口和双写/恢复边界选择。

- **目标调整**：维护用户最初目标和每次有效修订；让活跃工作在可观察的安全节点接收新版本，检查迟到成果是否仍适用。
- **领取与责任**：为每项工作明确负责人、目标和产物；并行执行不意味着全员发言。失败、丢失响应和暂停须可见。
- **恢复与去重**：保存稳定关联标识；对结果未知的外部操作先核查再决定重试，不能只根据一次超时宣称失败或成功。
- **阶段交付**：阶段成果应具有可阅读/使用的产物、依据和目标版本，让人根据新信息改变方向，而不是一遍遍批准过程。
- **完成判断**：状态、模型报告和检查结果分开；对机器可检验条件运行独立检查，对主观质量保留人工判断。

## 待做的最小对照

使用相同的任务和权限，对比单 Agent、现有 Bot 团队和候选任务层；安排一次用户目标修订、一次派发失败及一次重启。检查实际领取、迟到结果、重复动作、阶段产物和独立验收，记录不必要的用户催促。固定模型与宿主版本，多次运行并报告无法判定的情况。没有完成实测之前，不宣称多 Agent 或某个任务状态模型更好。
