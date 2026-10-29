# Grok Bot 任务机制：证据与 Nuska 研究假设

状态：公开资料研究，查阅于 2026-10-29；尚未独立验证或运行 Grok Bot。第三方分析基于 [Grok Bot 0.70.2 研究快照](https://github.com/oceanz0312/grok-bot-analysis/tree/272439bf4ff4ecc3bdb8190dbdd78fecd00f7b20)；官方在线文档会变化，不一定对应该版本。

## 用户问题

为什么一个明确目标交出去后，系统能持续推进并提供阶段成果？用户以 Grok Bot 的体验为研究参照。重要问题是任务如何派发、领取、更新和交付，以及哪些现象真的能减少用户对过程的管理。

## 资料中可定位的证据

### 官方描述：产品行为和设计目标

- [产品概览](https://docs.x.ai/grok-bot/overview)称 Bot 可并行运行、互相发消息、在群聊中共享上下文并移交任务；关闭客户端不会停止后台回合或例行任务。这是产品描述，不能据此推断长任务可靠性。
- [协作文档](https://docs.x.ai/grok-bot/chat-and-collaboration)描述群里普通消息可由参与者决定谁回复，Bot 可以异步交接、唤醒接收方并稍后回复；用户可发送新消息调整正在进行的工作。文档同时建议为每个阶段指定负责人。这些是产品支持和使用建议，不代表每次委派都被正确完成。
- [设计文章](https://x.ai/news/designing-grok-bot)称群聊提供项目共享上下文，个体 Bot 保有专门记忆；工具和 Skills 在账户层，记忆和 Routines 属于 Bot。官方 [概览](https://docs.x.ai/grok-bot/overview)补充：每个 Bot 的对话和学习上下文通常分开，少量用户信息共享；同一账户的 Bots 共享云电脑上的文件、浏览器会话和登录。**共享运行环境、群上下文和个体记忆是不同边界**，不能推论所有记忆自动互通。
- [协作文档](https://docs.x.ai/grok-bot/chat-and-collaboration)也指出 Bot 间私聊交接不一定出现在群里，群内交接消息为文本；审批、凭据请求等不在群里出现。因此只看群消息可能无法获得完整执行证据。

### 第三方客户端分析：0.70.2

- 第三方资料报告，客户端协议有接收结果和拒绝/重复等不同投递状态，并有 transcript 订阅；它区分接收与完成。该资料以代码或协议为依据，**静态存在不等于已观察到运行**。[Agent 子系统](https://github.com/oceanz0312/grok-bot-analysis/blob/272439bf4ff4ecc3bdb8190dbdd78fecd00f7b20/docs/subsystems/agent.md)
- 同一资料列出任务读取与标记、成员回合、后台执行相关接口；据此提出的服务端调度及工作流实现属于作者推断，不能从客户端接口推定任务确已领取、实际完成或得到验收。[Agent 子系统](https://github.com/oceanz0312/grok-bot-analysis/blob/272439bf4ff4ecc3bdb8190dbdd78fecd00f7b20/docs/subsystems/agent.md)
- 资料分析群成员回合和返回结果，并讨论多 Agent 及记忆；这些设计是后续观察的切入点，不足以证明群体交付可靠。[多 Agent 研究](https://github.com/oceanz0312/grok-bot-analysis/blob/272439bf4ff4ecc3bdb8190dbdd78fecd00f7b20/docs/subsystems/multiagent-memory-security.md)
- 同一研究在静态客户端材料中列出群成员回合请求、去重键与多种回合结果；它对模型何时选择不发言的解释属于推断。该篇明确声明只做静态阅读，不能当作动态运行验证。[群聊与记忆分析](https://github.com/oceanz0312/grok-bot-analysis/blob/272439bf4ff4ecc3bdb8190dbdd78fecd00f7b20/docs/subsystems/multiagent-memory-security.md)
- 阅读时遵守原研究对观察、推断、未知及推荐的区分；客户端无法直接验证未公开的服务端决策或验收机制。[方法与范围](https://github.com/oceanz0312/grok-bot-analysis/blob/272439bf4ff4ecc3bdb8190dbdd78fecd00f7b20/docs/methodology/evidence-levels.md)

## 需要检验的机制

1. **目标与任务**：用户原始目的和之后的修正如何关联？一次接收是否形成持久工作对象，或只是会话内容？
2. **派发与领取**：有无可观察的已派发、已领取、执行中、阻塞与结果状态？谁承担最终交付责任？
3. **持续执行**：成员等待、工具失败、进程重启、上下文切换后，任务如何继续？是否需要用户催促？
4. **阶段结果**：何时给出可使用的中间产物？新信息怎样改变后续路径，是否保留最初目标及用户修订？
5. **最终交付**：产物与检查证据在哪里？完成声明是否经独立检查，哪些判断需要用户？

这些问题是 Nuska 的实验设计，不是对 Grok Bot 内部实现的描述。

## 可重复观察协议

选同一个真实任务：给出明确目标、必要约束和可审阅的产物；执行中给出一条带新信息的目标修正。记录可见消息、任务/产物、阶段结果、实际用户介入、完成及阻塞；在可控环境引入可恢复失败或重启。必要时单独观察不同角色接力，保留版本和不可见环节。对阶段结果与最终产物独立打分，不凭系统自述推断完成。

**尚未知晓**：Grok Bot 0.70.2 及现行版本是否采用独立验收、任务领取契约或可靠续跑；相关细节需要产品行为证据或其他可信来源。
