# System Prompts Leaks：面向 Nuska 的资料研究

状态：第三方资料分析 · 2026-10-29；未验证材料真实性、来源链和线上生效情况。仓库：[asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks)，本次快照 [`1b6f936`](https://github.com/asgeirtj/system_prompts_leaks/tree/1b6f936124b4eceb6e697a69da07519bea67feab)。仓库 README 声称收集多家产品的系统提示词和工具描述；GitHub 元数据标记该仓库为 CC0，但不因此证明第三方材料来源、完整性、重分发权或生产适用性。

本研究重点查看仓库所标示的 [Grok Bot 材料](https://github.com/asgeirtj/system_prompts_leaks/blob/1b6f936124b4eceb6e697a69da07519bea67feab/xAI/grok-bot/grok-bot.md)，该文件在此快照中有系统提示词、变体、运行时注入内容和工具描述。其路径历史显示一次 2026-10-24 的仓库更新；这是**仓库提交时间**，不是已核实的产品发布日期、客户端版本或有效期。

## 证据层级

1. **可确认**：该固定提交的文件包含下述表述与工具 schema；文件存在本身是仓库事实。
2. **不能确认**：是否由官方实际部署、是否完整、适用哪些账户/版本/场景、是否仍有效，以及其写法是否真实触发相应行为。
3. **官方对照**：[Grok Bot 官方协作说明](https://docs.x.ai/grok-bot/chat-and-collaboration)描述运行中发送新消息、群协作等用户可见能力；它不能为该仓库的整份文本背书。
4. **独立参考**：[Grok Bot 客户端研究](2026-10-29-grok-bot-analysis.md)是第三方对 0.70.2 的分析，与这里标称的提示词文件并非同一已证明版本。来源各自独立且不保证可以直接拼成一套内部架构。

## 与自主交付相关的文本线索

| 主题 | 固定快照中出现的描述 | 可以研究的问题 |
| --- | --- | --- |
| 用户可见交付 | [系统段落 1.1](https://github.com/asgeirtj/system_prompts_leaks/blob/1b6f936124b4eceb6e697a69da07519bea67feab/xAI/grok-bot/grok-bot.md#L5-L13)区分开始响应、阶段进展和需要明确发送的最终结果 | 系统能否区别“开始处理”“工作中”和“真正送达的产物”？输出阶段结果是否可用？ |
| 后台子 Agent | [1.17 与 Task 描述](https://github.com/asgeirtj/system_prompts_leaks/blob/1b6f936124b4eceb6e697a69da07519bea67feab/xAI/grok-bot/grok-bot.md#L130-L143)讨论后台执行、分派自包含任务、完成通知和处理中纠偏 | 真实运行是否会将可验证目标、上下文、验收要求和结果归属传递给执行者？ |
| 群聊与成员 | [1.22 与群聊变体](https://github.com/asgeirtj/system_prompts_leaks/blob/1b6f936124b4eceb6e697a69da07519bea67feab/xAI/grok-bot/grok-bot.md#L164-L175)描述独立成员与异步消息；[群轮次](https://github.com/asgeirtj/system_prompts_leaks/blob/1b6f936124b4eceb6e697a69da07519bea67feab/xAI/grok-bot/grok-bot.md#L463-L474)描述群内回应和静默 | 群消息、成员被唤醒、处理与交付之间怎样关联？静默是否会掩盖尚未完成的任务？ |
| 任务队列 | [TodoWrite 描述](https://github.com/asgeirtj/system_prompts_leaks/blob/1b6f936124b4eceb6e697a69da07519bea67feab/xAI/grok-bot/grok-bot.md#L633-L701)描述请求的队列及状态维护 | 队列状态何时变更，是否有外部事实验证？原任务和用户修订如何关联？ |
| 记忆 | [记忆工具描述](https://github.com/asgeirtj/system_prompts_leaks/blob/1b6f936124b4eceb6e697a69da07519bea67feab/xAI/grok-bot/grok-bot.md#L1079-L1168)区分查询与更新，并描述个人和共享范围 | 共享知识如何授权、纠错、撤回？相关成员实际使用的是哪个目标版本？ |
| 运行中调整 | [子 Agent 状态、消息及停止工具](https://github.com/asgeirtj/system_prompts_leaks/blob/1b6f936124b4eceb6e697a69da07519bea67feab/xAI/grok-bot/grok-bot.md#L2453-L2526)描述查询、纠偏与停止 | 修正何时被真正处理？如何区分取消成功、部分完成和外部结果未知？ |

上表描述的是**文件声称的指令和接口**，不是对 Grok Bot 运行表现的确认。尤其不要把任务列表、发送回执或模型完成声明直接解释为可验证交付。

## 对 Nuska 的可检验假设

- 用户看重的“交付感”可能来自多个层次共同作用：清晰的可见输出、后台执行与返回机制、任务状态、记忆和群路由；不能把它归因于一段提示词。
- 持续工作需要区分：用户请求、后台任务、peer 消息和群轮次各由谁接收、谁负责返回，以及如何传递最新目标。这些是候选合同，不是对 Grok Bot 内部服务的断言。
- 队列与工具 schema 能约束状态表达，但验收仍需关联实际工具调用、产物及独立检查；还需测试成员失败、重复派发、迟到结果与目标修订。
- 私有 Bot 记忆、可共享用户事实和群工作上下文可能具有不同范围。具体授权和数据生命周期不能由一段疑似提示词单独确认。

## 下一步验证

1. 用相同的目标驱动任务，先记录产品界面实际可见的任务、阶段成果、纠偏与最终产物；明确产品版本与环境。
2. 逐项交叉核对官方文档、客户端证据和可复现运行；对来源冲突保留差异，不把推断提升为事实。
3. 在 DSH Team 的隔离实验中，将分派、inbox 接收、实际处理、产物、独立验收分别记录，再测试用户中途修订与成员中断。
4. 以 [DSH 多 Bot 组合方案](../landscape/2026-10-29-dsh-multi-bot-composition.md) 和 [交付评测](../evaluation/2026-10-29-delivery-benchmark.md) 为对照，必要时修正假设。当前没有运行结果或成功率。

本条目只链接并概述外部文本，没有把它作为指令或复制为 Nuska 的系统提示词；其中特定示例和环境路径不应视为本项目运行环境。
