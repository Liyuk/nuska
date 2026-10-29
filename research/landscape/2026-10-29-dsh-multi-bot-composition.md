# 用 DeepSeek Harness 组合多 Bot 群聊与交付：现有能力和缺口

状态：源码与公开文档调研、候选方案 · 2026-10-29。核对的 DSH 上游源码版本为 [`f3803c96`](https://github.com/deepseek-ai/deepseek-harness/tree/f3803c96974ad4a94195fb97e5c637e9c2a3afe3)。没有启动 DSH 或验证下述组合在同一个 profile 中能直接工作。DSH 的实验性接口可能变化；是否以它为 Nuska 底座仍未决定。

## 核心结论

用户指出的方向成立：DSH 已有比“单次 Agent 调用”更丰富的原语，包括同会话 goal 续行、计划评审、重复调用提醒、实验性 Agent Team、Ralph 和 workflow。**团队 roster、任务板、领取及依赖不应从零当成未存在的东西设计。** 此前 Nuska 文档强调单会话 goal，漏掉了 DSH 的 Team，这是需要纠正的。

这些原语仍需明确各自边界：Team 是一个以 Lead 会话为核心的实验性团队，并不是现成的长期身份 Bot 产品或多人群聊；其任务完成状态也不自动构成独立的交付验收。要形成接近用户所期待的 Grok Bot 体验，还需要研究群/个人身份、上下文、任务和阶段结果如何组织，并以真实任务验证。

## 已有原语及其适用位置

| DSH 原语 | 已记录的能力 | 不应直接推断 |
| --- | --- | --- |
| [Goal domain](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/goal/goal/README.zh.md)、[goal tools](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/goal/tool-goal/README.zh.md)、[round driver](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/goal/goal-round-driver/README.zh.md) | 同会话保存单个当前目标、修订与状态；符合条件时在 Agent 空闲后准入后续 Goal Round。它是用户所说“回合后继续”的具体机制，但依据的是 idle 等条件，不是每个 `turn/end` 必然续跑 | 不自带跨 Bot 共同目标、重启后自动授权续跑或独立验收；额度耗尽与停止语义需按当前版本验证 |
| [Plan Mode](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/plan/plan-mode/README.zh.md) | 自愿进入计划模式，探索后提交计划供人审核；已记录的状态可在恢复和 fork 后重建 | 不是每个愿望都必须预先人工审核；它是提示引导，不自动阻止工具，应由权限/沙箱等机制处理强约束 |
| [Repeat Tool Reminder](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/guard/repeat-tool-reminder/README.zh.md) | 基础 bundle 默认启用，对同 Agent、同工具、规范化参数完全相同的连续调用，在默认第 3、5、8 次提供提醒 | 只是建议，不会阻止；不检测变形重复、无进展对话或跨 Agent 循环，不能作为完整停滞检测 |
| [Agent Team](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/experimental/agent-team/README.zh.md) + [模型工具](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/experimental/tool-agent-team/README.zh.md) | Lead、具名 teammate、直接 inbox 消息、持久 roster 和共享任务板；任务可有依赖并由成员 claim，更新用 revision 防止覆盖 | 实验性、单进程、共享 cwd；不自动释放任务 owner，消息入 inbox 不等于已经处理、同步持久化或交付 |
| [Agent Team Profile](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/experimental/agent-team-profile/README.zh.md) | 在具备 base 的 profile 上组合 Team、工具和 Web 成员/任务板；默认关闭 | 原生 UI 是团队投影，不等于已完成的长期 Bot 身份、群消息与记忆产品；其组合会禁用部分同名普通 subagent 工具，需实测兼容性 |
| [Ralph](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/experimental/tool-ralph/README.zh.md) | 用户明确要求时，以不可变目标运行前台序列：每轮新子 Agent，利用共享工作区及有界交接报告 | 不是默认长期任务路径；中途动态目标不等同于不可变 objective；worker 的 complete 和证据是报告，未经独立认证 |
| [Workflow](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/workflow/workflow/README.zh.md) | 脚本可调用 `agent()`、`parallel()`、`pipeline()` 等；可对结构化子结果做 schema 校验 | 固定脚本的控制路径可复用、可检查；模型输出和外部数据仍非确定性，schema 合法不等于结果真实；文档说明只支持前台收集，重启不恢复运行进度 |
| Skill | 提供可复用指引和模板，可让 Agent 在适合场景读取 | skill 指引不是强制执行或验收保证；用户认为其长期价值仍需验证 |

## 面向 Grok Bot 式交互的组合

```text
用户 → 群 / Bot 交互层（身份、群消息、结果展示）
                  ↓
          群目标与任务协调层
    目标版本 · 阶段产物 · 交付证据 · 可见阻塞
                  ↓
DSH Team：Lead + teammates + 任务板/领取 + inbox
                  ↓
DSH Agent/工具/会话；按任务选 goal、workflow 或明确要求的 Ralph
```

这是**候选分层**：不推断 Grok Bot 采用相同结构，也不要求先创建新的任务板。优先用 Team 的任务板验证派活与领取；Nuska 只补已经在实验中发现缺口的能力，例如跨群目标版本与验收证据。对可完成的小任务，不强制创建团队或计划。

### 1. 长期 Bot 与群

Team 的具名 teammate 属于其 Team/Lead 会话，提供 roster 和任务状态；文档没有将它定义为跨群、跨会话长期存在的独立 Bot 人格。候选的群聊层需解决：Bot 身份与成员关系、群消息可见范围、把输入投递到正确 Agent、阶段成果及回复关联到目标。每个 Bot 的个人记忆、群任务上下文与经授权共享知识应分开；团队消息或 fork 的旧会话前缀不能自动视为可靠的记忆共享。[Team 文档](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/experimental/agent-team/README.zh.md) · [记忆与上下文研究](../context/2026-10-29-memory-and-shared-context.md)

### 2. 目标、分派与领取

用户给出强目标；Lead 在已有授权范围内开始工作，按需建立工作项、指定或让成员领取。任务项应关联用户目标及修订、预期产物、负责人和检查要求；Team 已有任务依赖、claim 和 CAS，可作为试验起点。Team 消息返回成功只说明目标 inbox 接受，不能据此报告成员已处理；任务 owner 不会因成员中断或进程退出自动释放，应明确可见的人工或协调恢复策略。

目标变更时，记录旧工作项和结果所依据的版本，向相关成员发送补充，并通过事件确认何时被实际处理；过期成果仍可作为历史证据，不自动算新目标完成。Team 消息不额外保证未接收发送意图的重试或显式重发去重；跨进程与可靠消息须另行解决。

### 3. Goal、Team 与 Workflow 如何配合

- **Goal** 可研究作为 Lead 同会话持续推进的基础；单个 goal 不自动成为所有 teammate 的共享权威目标。实际组合需要检查目标修订、Team 成员和 goal driver 同时运行时的生命周期与权限。
- **Team** 更适合具名成员和任务板式协作；等待 Team 变化而不是单纯靠群回复接力数判断停止。
- **Workflow** 适合重复、可脚本化的有界并行流程；普通子 Agent 失败可能以 `null` 返回，脚本必须显式处理。它目前不是持久恢复的后台任务引擎。
- **Ralph** 适合用户明确要求新 Agent 多轮迭代的场景，目标不可变；常规可变目标与中途纠偏优先研究 goal/Team 路径。
- **Plan Mode** 用在用户希望审阅方案或需要明确判断的情况；默认先交阶段成果并继续推进，不把所有请求变成计划审批。

### 4. 交付验证

Schema 可以约束交接字段，skill 可以提供报告模板，workflow 可以固定已设计好的步骤；三者都不能保证事实、引用或最终目标满足。候选独立验收需要对照用户当前目标、真实产物与证据，分别执行机器检查、人工/明确评估和未知项报告；不能让模型把任务板标完成，就直接当作验收完成。DSH goal 文档也明确没有独立评估器。

## 与两种 DSBot 的关系

[Fei2411/DS-Bot 的已核查版本](2026-10-29-two-ds-bot-delivery.md)在 Bot 会话隐藏和阻止 goal，并在群内 Bot 接力达到阈值时暂停后续接力；是否能在其公开插件接口上安全启用 Team/goal，尚未验证，不能假设移除限制即可共存。[BotHarness/DeepSeekBot](2026-10-29-two-ds-bot-delivery.md)已有 Assignment 和报告机制，不应当成空白实现；需要对照其目标保持、续行、交付与验收做相同任务实验。

产品路径有三种待比较选择：直接使用 DSH Team 构建新的群/Bot 外壳；作为外部能力接入现有 Bot 产品；或在现有应用公开扩展点上迭代。先检查双方的权限、生命周期、版本和作者提供的接口，再通过运行验证选型。

## 最小可验证实验

1. 在隔离 profile 中记录安装版本和加载的 bundle，验证 Team、goal、reminder、计划模式及 workflow 的组合是否可启动；不得以包文档推断组合兼容。
2. 使用两个 teammate 完成一个真实研究任务：Lead 建任务、设置依赖，成员领取并产生有来源的阶段结果；记录 Team 事件、inbox 接收、实际工作与产物。
3. 用户中途改变范围，检查修订到达与处理、迟到结果所依据的版本，以及最终产物是否遵循最新目标。
4. 中断一位 owner 并重启 profile：核对任务 owner 未自动释放、发送中消息状态与 goal disarm；不依赖盲目重试。
5. 用独立检查验证引用、产物和必要条件；人工评估内容质量。比较有无 Team 与验收层时的真实交付，不凭 schema 或模型自述算完成。
6. 单独对比 Plan Mode 的显式审批、普通 goal 续行、用户明确要求的 Ralph 以及有界 workflow；不把任何一种当作所有任务的默认路径。

记录真实使用场景、模型和宿主版本、事件、阶段/最终产物与未完成项；该实验尚未执行。
