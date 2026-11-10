# OpenMausBot：Grok Bot 形态的本地多 Agent 工作台调研

状态：已完成公开资料初查；以仓库 README、官方文档和主分支源码说明为据；未安装、运行或审计。

日期：2026-11-04

## 问题和范围

研究 OpenMausBot 的产品形态、运行架构、委派与交付机制、权限边界，并判断它对 Nuska 的研究与原型有什么参考价值。对象是 [`milind-soni/OpenMausBot`](https://github.com/milind-soni/OpenMausBot) 当前公开主分支；项目自述为 Apache-2.0、local-first 的 Grok Bot 替代方案。本文不评估其实际任务成功率、代码安全性、服务条款，也不把 README 的产品描述当成独立验证结果。

## 材料和方法

查阅项目 [README](https://github.com/milind-soni/OpenMausBot/blob/main/README.md)、[job runtime contract](https://github.com/milind-soni/OpenMausBot/blob/main/docs/runtime-contract.md)、[headless CLI](https://github.com/milind-soni/OpenMausBot/blob/main/docs/headless-cli.md)、[MCP server](https://github.com/milind-soni/OpenMausBot/blob/main/docs/mcp-server.md)、[团队分享说明](https://github.com/milind-soni/OpenMausBot/blob/main/docs/team-sharing.md) 与 [package.json](https://github.com/milind-soni/OpenMausBot/blob/main/package.json)。仓库页面和主分支文件访问于 2026-11-04；主分支会变动，引用链接未固定到 commit。没有克隆或运行仓库。

## 发现与证据

### 产品和执行架构

OpenMausBot 把多个 Agent 做成消息应用里的联系人：每个 bot 有独立 profile、模型、对话线程和连接的应用；README 称 Agent 通过用户本机安装的 Claude、Codex、Grok CLI 运行。应用本身与 harness 分为两个进程：UI 通过 HTTP 发送命令并消费 SSE 事件，harness 管理 provider driver、进程和统一事件流，记录按 thread 写入 NDJSON。项目另提供 Electron 桌面应用、CLI 与 stdio MCP 服务。[README：产品与架构](https://github.com/milind-soni/OpenMausBot/blob/main/README.md#how-it-works) · [package.json](https://github.com/milind-soni/OpenMausBot/blob/main/package.json)

运行环境可选云端 Linux 桌面、隔离 Local VM，或在部分平台经显式启用后控制宿主电脑；应用连接 Composio 应用。README 明确写出平台限制，例如 Ubuntu Wayland 的本机控制处于关闭状态。它也声明 harness 默认绑定 loopback，聊天记录、密钥和事件保存在 `~/.openmausbot`。这些是项目文档对部署和数据位置的描述，并不等于已进行隐私或隔离验证。[README：Why / desktop capability status](https://github.com/milind-soni/OpenMausBot/blob/main/README.md#why) · [README：Privacy](https://github.com/milind-soni/OpenMausBot/blob/main/README.md#privacy)

### 多 Agent 委派与任务状态

项目的 runtime contract 把每项委派建模为 Assignment：包含 root/parent、请求来源、requester、assignee、work/consult/notify 模式、响应方式、状态、结果和运行证据；SQLite 持久化 assignment、追加式事件和 inbox。生命周期覆盖 queued、running、waiting、needs_input、completed、failed、cancelled，并通过父子树表达委派、等待、恢复和级联停止。[Runtime contract：记录与生命周期](https://github.com/milind-soni/OpenMausBot/blob/main/docs/runtime-contract.md#1-the-record)

负责人被委派工作后会等待其子任务结束，再恢复一次整合；子 Agent 的问题可唤醒负责人并传递给人。运行时有去重、深度/预算限制、stall 检测、重启恢复政策，以及对已观察到的外部动作（例如已发送邮件或 git push）避免盲目重复执行的处理。README 的 `run` 默认等负责人及其委派队友完成；支持超时、等待用户输入、严格检查子任务失败、导出工作树与对话记录。[Runtime contract](https://github.com/milind-soni/OpenMausBot/blob/main/docs/runtime-contract.md) · [Headless CLI：run/wait/export](https://github.com/milind-soni/OpenMausBot/blob/main/docs/headless-cli.md#run-and-wait)

这是一个比“群聊里 bot 互相发消息”更显式的任务执行层：委派有可追踪父子关系和生命周期，完成时可返回结果和 harness 观测证据。但 `completed` 是运行时状态，不能直接解释为用户目标已经通过独立质量验收。项目 CLI 与 MCP 文档本身也区分 job state 和 conversation `settled`，允许 failed、stalled、needs-input 等终态；这有助于诚实表达执行状态，仍不构成内容质量评分。[Runtime contract](https://github.com/milind-soni/OpenMausBot/blob/main/docs/runtime-contract.md#2-lifecycle) · [MCP server：wait result](https://github.com/milind-soni/OpenMausBot/blob/main/docs/mcp-server.md#tools)

### 人机控制、工具入口与团队复用

README 描述 permission broker 将命令、文件编辑和问题显示为 Allow/Deny/回答卡片；执行级别包括 Ask、Edits、Auto、Full，并随委派继承/受引擎支持能力限制。具体 Full access 行为较复杂：部分可由 Agent 自行选默认的输入会交回 requester 处理，登录、密钥、付款或用户账户等仍需人处理。外来事件按低信任来源处理。此设计说明项目在运行时记录授权来源并传播权限，而非仅靠 bot prompt 约束。[README：审批卡片](https://github.com/milind-soni/OpenMausBot/blob/main/README.md#features) · [Runtime contract：level 与来源](https://github.com/milind-soni/OpenMausBot/blob/main/docs/runtime-contract.md#3-one-level-rule)

除桌面 UI 外，CLI 可由脚本或 CI 设置团队、派发工作、等待完整任务树并导出结果；MCP 可供其他客户端创建/配置 bot 和 channel、发送工作、等待及中断。MCP 有意不开放批准、权限记忆、凭证、删除或电脑/VM 生命周期管理；修改操作在已打包的桌面版要求配对会话。读取有分页上限，截图像素和授权 grant key 不返回。[Headless CLI](https://github.com/milind-soni/OpenMausBot/blob/main/docs/headless-cli.md) · [MCP server：能力与限制](https://github.com/milind-soni/OpenMausBot/blob/main/docs/mcp-server.md#what-it-can-do)

团队包可携带 bot 指令、skills、playbooks、group chats、routines、Chief of Staff 和 starter notes；敏感字段、聊天历史、密钥、模型和电脑不会随包导出。导入后的 routines 暂停，skills 关闭，连接器关闭且凭证为空。项目另外提供从 Grok Bot 迁移的导入流程。导入策略减少复用团队配置时意外赋权的风险，但导出的自由文本仍需用户确认其内容。[团队分享说明](https://github.com/milind-soni/OpenMausBot/blob/main/docs/team-sharing.md)

### 版本和成熟度边界

README 将项目标为 “Early but real”，称消息、Agent、流式回复、工具、审批、computer use 的端到端循环已可用，同时指出 hosted/mobile connectivity 仍在建设、webhook 依赖本地接收器。支持平台能力也存在差异；例如 Ubuntu 仍为 beta。README 和源码列有多项测试与 eval 命令，但本次没有执行，也未核查其覆盖率或公开基准结果。[README：Status / desktop capability status](https://github.com/milind-soni/OpenMausBot/blob/main/README.md#status) · [package.json：scripts](https://github.com/milind-soni/OpenMausBot/blob/main/package.json)

## 局限和未解问题

- 文档与主分支属于项目自身描述；本报告没有验证 CLI 是否能在目标系统启动、沙箱隔离是否有效、授权 broker 是否覆盖所有工具，也没有检查供应商的 CLI 兼容行为。
- 项目有复杂的委派与恢复规则，但其完整性、死锁/竞态行为、崩溃后副作用处理仍需针对真实环境验证。runtime contract 中关于测试的陈述不是本次独立测试证据。
- 公开资料没有给出同一任务集上的完成率、错误完成率、目标变更成功率、交付质量或人工介入成本。因此不能据架构设计推断它“比 Grok Bot 更可靠”或已满足 Nuska 的交付验收标准。
- 主分支在快速变化；发布包、桌面系统和外接云服务的能力及条款需按实际版本核查。

## 对 Nuska 的意义

| Nuska 研究问题 | 可借鉴处 | 尚未解决之处 |
| --- | --- | --- |
| 跨工具持续执行和恢复 | 将每次委派作为持久 Assignment，集中管理生命周期、事件、等待和中断；崩溃恢复时检查已知外部动作 | 恢复逻辑不保证外部副作用可逆或完整观测，需真实故障注入和去重测试 |
| 多 Agent 责任与共享状态 | requester/assignee、父子任务树、work/consult/notify 的区分，明确谁等待谁、谁需要恢复 | 任务树完成不代表最终目标验收通过；还需独立交付物与证据层 |
| 人工介入与权限 | 权限随调用链记录、按引擎能力裁剪，MCP 控制面不暴露批准/凭证等敏感动作 | Full access 的 requester 自动决策需要明确产品授权和可审计边界，不能只复制技术实现 |
| 宿主集成与实验 | 本地 harness + CLI/MCP + 桌面 UI 提供可比较的多种接入面；导出 job tree/transcripts/files 可供复盘 | 文件导出和执行状态仍不是统一的独立评估协议，需对照具体交付标准 |

**建议：**把 OpenMausBot 列为“多 Agent 个人工作台与宿主集成”参照，优先沿 `Assignment → job tree → wait/resume/interrupt → evidence` 路径做源码核查。若选作实验候选，应使用固定任务集，记录模型/CLI 版本、批准级别、每个子任务责任人、实际产物和外部状态；另行评定目标理解、完整性、错误完成与人工负担。不要把产品已经提供多 Agent 或电脑操作，等同于 Nuska 已验证的自主交付能力。

它与上一份 [Grok Bot 与个人交付型 Agent 研究](2026-10-31-grok-personal-agent-research.md)形成直接对照：OpenMausBot公开了比封闭产品更细的运行时机制和代码结构，适合研究“如何实现”；上一份提出的 Goal、Deliverable、Evidence、Decision 验收维度仍适合评测“实现是否交付正确”。

## 下一步

1. 固定一个 commit，追踪 `server/runtime/`、assignment persistence 和 permission broker 的真实调用路径，核对文档与代码是否一致。
2. 将现成的长任务交付评测任务集适配为 OpenMausBot 的 CLI 流程，至少覆盖委派失败、用户输入等待、进程重启、重复发送和外部副作用恢复。
3. 对照 Nuska 现有多 Bot / Tobs 研究，补充 Assignment 与已有实现的实体、生命周期和观察能力映射。
